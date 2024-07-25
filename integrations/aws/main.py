import json
import typing

from fastapi import Response, status
import fastapi
from starlette import responses
from pydantic import BaseModel

from port_ocean.core.models import Entity

from utils.resources import (
    is_global_resource,
    resync_custom_kind,
    describe_single_resource,
    fix_unserializable_date_properties,
    resync_cloudcontrol,
)

from utils.aws import (
    describe_accessible_accounts,
    get_sessions,
    update_available_access_credentials,
    validate_request,
)
from port_ocean.context.ocean import ocean
from loguru import logger
from port_ocean.core.ocean_types import ASYNC_GENERATOR_RESYNC_TYPE
from utils.misc import (
    get_matching_kinds_and_blueprints_from_config,
    CustomProperties,
    ResourceKindsWithSpecialHandling,
    is_access_denied_exception,
)


@ocean.on_resync()
async def resync_all(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    if kind in iter(ResourceKindsWithSpecialHandling):
        return
    await update_available_access_credentials()
    is_global = is_global_resource(kind)
    try:
        async for batch in resync_cloudcontrol(kind, is_global):
            yield batch
    except Exception as e:
        if is_access_denied_exception(e):
            async for batch in resync_cloudcontrol(
                kind, is_global=False, stop_on_first_region=True
            ):
                yield batch


@ocean.on_resync(kind=ResourceKindsWithSpecialHandling.ACCOUNT)
async def resync_account(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    await update_available_access_credentials()
    for account in describe_accessible_accounts():
        yield [fix_unserializable_date_properties(account)]


@ocean.on_resync(kind=ResourceKindsWithSpecialHandling.ELASTICACHE_CLUSTER)
async def resync_elasticache(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    await update_available_access_credentials()
    async for session in get_sessions():
        async for batch in resync_custom_kind(
            kind,
            session,
            "elasticache",
            "describe_cache_clusters",
            "CacheClusters",
            "Marker",
        ):
            yield batch


@ocean.on_resync(kind=ResourceKindsWithSpecialHandling.ELBV2_LOAD_BALANCER)
async def resync_elv2_load_balancer(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    await update_available_access_credentials()
    async for session in get_sessions():
        async for batch in resync_custom_kind(
            kind,
            session,
            "elbv2",
            "describe_load_balancers",
            "LoadBalancers",
            "Marker",
        ):
            yield batch


@ocean.on_resync(kind=ResourceKindsWithSpecialHandling.ACM_CERTIFICATE)
async def resync_acm(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    await update_available_access_credentials()
    async for session in get_sessions():
        async for batch in resync_custom_kind(
            kind,
            session,
            "acm",
            "list_certificates",
            "CertificateSummaryList",
            "NextToken",
        ):
            yield batch


@ocean.on_resync(kind=ResourceKindsWithSpecialHandling.AMI_IMAGE)
async def resync_ami(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    await update_available_access_credentials()
    async for session in get_sessions():
        async for batch in resync_custom_kind(
            kind,
            session,
            "ec2",
            "describe_images",
            "Images",
            "NextToken",
            {"Owners": ["self"]},
        ):
            yield batch


@ocean.on_resync(kind=ResourceKindsWithSpecialHandling.CLOUDFORMATION_STACK)
async def resync_cloudformation(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    await update_available_access_credentials()
    async for session in get_sessions():
        async for batch in resync_custom_kind(
            kind,
            session,
            "cloudformation",
            "describe_stacks",
            "Stacks",
            "NextToken",
        ):
            yield batch


@ocean.app.fast_api_app.middleware("aws_cloud_event")
async def cloud_event_validation_middleware_handler(
    request: fastapi.Request,
    call_next: typing.Callable[[fastapi.Request], typing.Awaitable[responses.Response]],
) -> responses.Response:
    if request.url.path.startswith("/integration"):
        if request.method == "OPTIONS":
            logger.info("Detected cloud event validation request")
            headers = {
                "WebHook-Allowed-Rate": "100",
                "WebHook-Allowed-Origin": "*",
            }
            response = fastapi.Response(status_code=200, headers=headers)
            return response

        validation = validate_request(request)
        validation_status = validation[0]
        message = validation[1]
        if validation_status is False:
            return fastapi.Response(
                status_code=status.HTTP_401_UNAUTHORIZED, content=message
            )

    return await call_next(request)


class ResourceUpdate(BaseModel):
    resource_type: str
    identifier: str
    accountId: str
    awsRegion: str


@ocean.router.post("/webhook")
async def webhook(update: ResourceUpdate, response: Response) -> fastapi.Response:
    await update_available_access_credentials()
    try:
        logger.info(f"Received AWS Webhook request body: {update}")
        resource_type = update.resource_type
        identifier = update.identifier
        account_id = update.accountId
        region = update.awsRegion

        with logger.contextualize(
            account_id=account_id, resource_type=resource_type, identifier=identifier
        ):
            matching_resource_configs = get_matching_kinds_and_blueprints_from_config(
                resource_type
            )

            logger.debug(
                "Querying full resource on AWS before registering change in port"
            )

            try:
                resource = await describe_single_resource(
                    resource_type, identifier, account_id, region
                )
            except Exception:
                resource = None

            for kind in matching_resource_configs:
                blueprints = matching_resource_configs[kind]
                if not resource:  # Resource probably deleted
                    for blueprint in blueprints:
                        logger.info(
                            "Resource not found in AWS, un-registering from port"
                        )
                        await ocean.unregister(
                            [
                                Entity(
                                    blueprint=blueprint,
                                    identifier=identifier,
                                )
                            ]
                        )
                else:  # Resource found in AWS, update port
                    logger.info("Resource found in AWS, registering change in port")
                    resource.update(
                        {
                            CustomProperties.KIND: resource_type,
                            CustomProperties.ACCOUNT_ID: account_id,
                            CustomProperties.REGION: region,
                        }
                    )
                    await ocean.register_raw(
                        kind,
                        [fix_unserializable_date_properties(resource)],
                    )

            logger.info("Webhook processed successfully")
            return fastapi.Response(
                status_code=status.HTTP_200_OK, content=json.dumps({"ok": True})
            )
    except Exception as e:
        logger.exception("Failed to process event from aws")
        return fastapi.Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.dumps({"ok": False, "error": str(e)}),
        )

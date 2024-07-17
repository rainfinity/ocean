from loguru import logger

from port_ocean.clients.port.types import UserAgentType
from port_ocean.context.event import event
from port_ocean.core.handlers.entities_state_applier.base import (
    BaseEntitiesStateApplier,
)
from port_ocean.core.handlers.entities_state_applier.port.get_related_entities import (
    get_related_entities,
)
from port_ocean.core.handlers.entities_state_applier.port.order_by_entities_dependencies import (
    order_by_entities_dependencies,
)
from port_ocean.core.models import Entity
from port_ocean.core.ocean_types import EntityDiff
from port_ocean.core.utils import is_same_entity, get_port_diff


class HttpEntitiesStateApplier(BaseEntitiesStateApplier):
    """Applies and manages changes to entities' state using HTTP requests.

    This class extends the BaseEntitiesStateApplier and provides concrete implementations
    for applying changes, deleting entities, upserting entities, and handling entity diffs
    through HTTP requests.
    """

    async def _safe_delete(
        self,
        entities_to_delete: list[Entity],
        entities_to_protect: list[Entity],
        user_agent_type: UserAgentType,
    ) -> None:
        if not entities_to_delete:
            return

        related_entities = await get_related_entities(
            entities_to_protect, self.context.port_client
        )

        allowed_entities_to_delete = []

        for entity_to_delete in entities_to_delete:
            is_part_of_related = any(
                is_same_entity(entity, entity_to_delete) for entity in related_entities
            )
            is_part_of_created = any(
                is_same_entity(entity, entity_to_delete)
                for entity in entities_to_protect
            )
            if is_part_of_related:
                if event.port_app_config.create_missing_related_entities:
                    logger.info(
                        f"Skipping entity {(entity_to_delete.identifier, entity_to_delete.blueprint)} because it is "
                        f"related to created entities and create_missing_related_entities is enabled"
                    )
                else:
                    allowed_entities_to_delete.append(entity_to_delete)
            elif not is_part_of_created:
                allowed_entities_to_delete.append(entity_to_delete)

        await self.delete(allowed_entities_to_delete, user_agent_type)

    async def apply_diff(
        self,
        entities: EntityDiff,
        user_agent_type: UserAgentType,
    ) -> None:
        diff = get_port_diff(entities["before"], entities["after"])
        kept_entities = diff.created + diff.modified

        logger.info(
            f"Updating entity diff (created: {len(diff.created)}, deleted: {len(diff.deleted)}, modified: {len(diff.modified)})"
        )
        await self.upsert(kept_entities, user_agent_type)

        await self._safe_delete(diff.deleted, kept_entities, user_agent_type)

    async def delete_diff(
        self,
        entities: EntityDiff,
        user_agent_type: UserAgentType,
    ) -> None:
        diff = get_port_diff(entities["before"], entities["after"])

        if not diff.deleted:
            return

        kept_entities = diff.created + diff.modified

        logger.info(
            f"Determining entities to delete ({len(diff.deleted)}/{len(kept_entities)})"
        )

        await self._safe_delete(diff.deleted, kept_entities, user_agent_type)

    async def upsert(
        self, entities: list[Entity], user_agent_type: UserAgentType
    ) -> None:
        logger.info(f"Upserting {len(entities)} entities")
        if event.port_app_config.create_missing_related_entities:
            await self.context.port_client.batch_upsert_entities(
                entities,
                event.port_app_config.get_port_request_options(),
                user_agent_type,
                should_raise=False,
            )
        else:
            ordered_created_entities = reversed(
                order_by_entities_dependencies(entities)
            )

            for entity in ordered_created_entities:
                await self.context.port_client.upsert_entity(
                    entity,
                    event.port_app_config.get_port_request_options(),
                    user_agent_type,
                    should_raise=False,
                )

    async def delete(
        self, entities: list[Entity], user_agent_type: UserAgentType
    ) -> None:
        logger.info(f"Deleting {len(entities)} entities")
        if event.port_app_config.delete_dependent_entities:
            await self.context.port_client.batch_delete_entities(
                entities,
                event.port_app_config.get_port_request_options(),
                user_agent_type,
                should_raise=False,
            )
        else:
            ordered_deleted_entities = order_by_entities_dependencies(entities)

            for entity in ordered_deleted_entities:
                await self.context.port_client.delete_entity(
                    entity,
                    event.port_app_config.get_port_request_options(),
                    user_agent_type,
                    should_raise=False,
                )

import asyncio
import typing
from datetime import datetime, timedelta
from typing import List, Tuple, Any, Union, TYPE_CHECKING

import anyio.to_thread
import yaml
from gitlab import Gitlab, GitlabList, GitlabError
from gitlab.base import RESTObject
from gitlab.v4.objects import (
    Project,
    MergeRequest,
    Issue,
    Group,
    ProjectPipeline,
    GroupMergeRequest,
    ProjectPipelineJob,
)
from loguru import logger
from yaml.parser import ParserError

from gitlab_integration.core.entities import generate_entity_from_port_yaml
from gitlab_integration.core.async_fetcher import AsyncFetcher
from gitlab_integration.core.utils import does_pattern_apply
from port_ocean.context.event import event
from port_ocean.core.models import Entity

PROJECTS_CACHE_KEY = "__cache_all_projects"

if TYPE_CHECKING:
    from gitlab_integration.git_integration import (
        GitlabPortAppConfig,
    )


class GitlabService:
    all_events_in_webhook: list[str] = [
        "push_events",
        "merge_requests_events",
        "issues_events",
        "job_events",
        "pipeline_events",
        "releases_events",
        "tag_push_events",
        "subgroup_events",
        "confidential_issues_events",
    ]

    def __init__(
        self,
        gitlab_client: Gitlab,
        app_host: str,
        group_mapping: List[str],
    ):
        self.gitlab_client = gitlab_client
        self.app_host = app_host
        self.group_mapping = group_mapping

    def _does_webhook_exist_for_group(self, group: RESTObject) -> bool:
        for hook in group.hooks.list(iterator=True):
            if hook.url == f"{self.app_host}/integration/hook/{group.get_id()}":
                return True
        return False

    def _create_group_webhook(
        self, group: RESTObject, events: list[str] | None
    ) -> None:
        webhook_events = {
            event: event in (events if events else self.all_events_in_webhook)
            for event in self.all_events_in_webhook
        }

        logger.info(
            f"Creating webhook for {group.get_id()} with events: {[event for event in webhook_events if webhook_events[event]]}"
        )

        resp = group.hooks.create(
            {
                "url": f"{self.app_host}/integration/hook/{group.get_id()}",
                **webhook_events,
            }
        )
        logger.info(
            f"Created webhook for {group.get_id()}, id={resp.id}, url={resp.url}"
        )

    def _get_changed_files_between_commits(
        self, project_id: int, head: str
    ) -> Union[GitlabList, list[dict[str, Any]]]:
        project = self.gitlab_client.projects.get(project_id)
        return project.commits.get(head).diff()

    def _get_file_paths(
        self, project: Project, path: str | List[str], commit_sha: str
    ) -> list[str]:
        if not isinstance(path, list):
            path = [path]
        try:
            files = project.repository_tree(ref=commit_sha, all=True)
        except GitlabError as err:
            if err.response_code != 404:
                raise err

            logger.warning(
                f"Failed to retrieve project tree for commit sha: {commit_sha} as it was not found."
            )
            files = []
        return [
            file["path"]
            for file in files
            if does_pattern_apply(path, file["path"] or "")
        ]

    def _get_entities_from_git(
        self, project: Project, file_name: str, sha: str, ref: str
    ) -> List[Entity]:
        try:
            file_content = project.files.get(file_path=file_name, ref=sha)
            entities = yaml.safe_load(file_content.decode())
            raw_entities = [
                Entity(**entity_data)
                for entity_data in (
                    entities if isinstance(entities, list) else [entities]
                )
            ]
            return [
                generate_entity_from_port_yaml(entity_data, project, ref)
                for entity_data in raw_entities
            ]
        except ParserError as exec:
            logger.error(
                f"Failed to parse gitops entities from gitlab project {project.path_with_namespace},z file {file_name}."
                f"\n {exec}"
            )
        except Exception:
            logger.error(
                f"Failed to get gitops entities from gitlab project {project.path_with_namespace}, file {file_name}"
            )
        return []

    def _get_entities_by_commit(
        self, project: Project, spec: str | List["str"], commit: str, ref: str
    ) -> List[Entity]:
        spec_paths = self._get_file_paths(project, spec, commit)
        return [
            entity
            for path in spec_paths
            for entity in self._get_entities_from_git(project, path, commit, ref)
        ]

    def should_run_for_path(self, path: str) -> bool:
        return any(does_pattern_apply(mapping, path) for mapping in self.group_mapping)

    def should_run_for_group(self, group: Group) -> bool:
        return self.should_run_for_path(group.full_path)

    def should_run_for_project(
        self,
        project: Project,
    ) -> bool:
        return self.should_run_for_path(project.path_with_namespace)

    def should_run_for_merge_request(
        self,
        merge_request: typing.Union[MergeRequest, GroupMergeRequest],
    ) -> bool:
        project_path = merge_request.references.get("full").rstrip(
            merge_request.references.get("short")
        )
        return self.should_run_for_path(project_path)

    def should_run_for_issue(
        self,
        issue: Issue,
    ) -> bool:
        project_path = issue.references.get("full").rstrip(
            issue.references.get("short")
        )
        return self.should_run_for_path(project_path)

    def get_root_groups(self) -> List[Group]:
        groups = self.gitlab_client.groups.list(iterator=True)
        return typing.cast(
            List[Group], [group for group in groups if group.parent_id is None]
        )

    def filter_groups_by_paths(self, groups_full_paths: list[str]) -> List[Group]:
        groups = self.gitlab_client.groups.list(get_all=True)
        return typing.cast(
            List[Group],
            [
                group
                for group in groups
                if group.attributes["full_path"] in groups_full_paths
            ],
        )

    def get_filtered_groups_for_webhooks(
        self,
        groups_hooks_override_list: list[str] | None,
    ) -> List[Group]:
        groups_for_webhooks = []
        if groups_hooks_override_list is not None:
            if groups_hooks_override_list:
                logger.info(
                    "Getting all the specified groups in the mapping for a token to create their webhooks"
                )
                groups_for_webhooks = self.filter_groups_by_paths(
                    groups_hooks_override_list
                )

                groups_paths_not_found = [
                    group_path
                    for group_path in groups_hooks_override_list
                    if group_path
                    not in [
                        group.attributes["full_path"] for group in groups_for_webhooks
                    ]
                ]

                if groups_paths_not_found:
                    logger.warning(
                        "Some groups where not found in gitlab to create webhooks for, "
                        "probably because of groups that are not under the token's scope, or a mismatched "
                        "groups full_path in tokenGroupHooksOverrideMapping with the groups full_path in gitlab. "
                        f"full_paths of groups that where not found: {groups_paths_not_found}"
                    )
        else:
            logger.info("Getting all the root groups to create their webhooks")
            root_groups = self.get_root_groups()
            groups_for_webhooks = [
                group
                for group in root_groups
                if any(
                    does_pattern_apply(
                        mapping.split("/")[0], group.attributes["full_path"]
                    )
                    for mapping in self.group_mapping
                )
            ]

        return groups_for_webhooks

    def create_webhook(self, group: Group, events: list[str] | None) -> str | None:
        logger.info(f"Creating webhook for the group: {group.attributes['full_path']}")

        webhook_id = None
        group_id = group.get_id()

        if group_id is None:
            logger.info(f"Group {group.attributes['full_path']} has no id. skipping...")
        else:
            if self._does_webhook_exist_for_group(group):
                logger.info(f"Webhook already exists for group {group.get_id()}")
            else:
                self._create_group_webhook(group, events)
            webhook_id = str(group_id)

        return webhook_id

    def create_system_hook(self) -> None:
        logger.info("Checking if system hook already exists")
        try:
            for hook in self.gitlab_client.hooks.list(iterator=True):
                if hook.url == f"{self.app_host}/integration/system/hook":
                    logger.info("System hook already exists, no need to create")
                    return
        except Exception:
            logger.error(
                "Failed to check if system hook exists, skipping trying to create, to avoid duplicates"
            )
            return

        logger.info("Creating system hook")
        try:
            resp = self.gitlab_client.hooks.create(
                {
                    "url": f"{self.app_host}/integration/system/hook",
                    "push_events": True,
                    "merge_requests_events": True,
                    "repository_update_events": False,
                }
            )
            logger.info(f"Created system hook with id {resp.get_id()}")
        except Exception:
            logger.error("Failed to create system hook")

    async def get_project(self, project_id: int) -> Project | None:
        """
        Returns project if it should be processed, None otherwise
        If the project is not in the cache, it will be fetched from gitlab and validated against the group mapping
        before being added to the cache
        :param project_id: project id
        :return: Project if it should be processed, None otherwise
        """
        logger.info(f"fetching project {project_id}")
        filtered_projects = event.attributes.setdefault(
            PROJECTS_CACHE_KEY, {}
        ).setdefault(self.gitlab_client.private_token, {})

        if project := filtered_projects.get(project_id):
            return project

        project = await AsyncFetcher.fetch_single(
            self.gitlab_client.projects.get, project_id
        )
        if self.should_run_for_project(project):
            event.attributes[PROJECTS_CACHE_KEY][self.gitlab_client.private_token][
                project_id
            ] = project
            return project
        else:
            return None

    async def get_group(self, group_id: int) -> Group | None:
        logger.info(f"fetching group {group_id}")
        group = await AsyncFetcher.fetch_single(self.gitlab_client.groups.get, group_id)
        if isinstance(group, Group) and self.should_run_for_group(group):
            return group
        else:
            return None

    async def get_all_groups(self) -> typing.AsyncIterator[List[Group]]:
        logger.info("fetching all groups for the token")
        async for groups_batch in AsyncFetcher.fetch_batch(
            fetch_func=self.gitlab_client.groups.list,
            validation_func=self.should_run_for_group,
            pagination="offset",
            order_by="id",
            sort="asc",
        ):
            groups: List[Group] = typing.cast(List[Group], groups_batch)
            logger.info(
                f"Queried {len(groups)} groups {[group.path for group in groups]}"
            )
            yield groups

    async def get_all_projects(self) -> typing.AsyncIterator[List[Project]]:
        logger.info("fetching all projects for the token")
        port_app_config: GitlabPortAppConfig = typing.cast(
            "GitlabPortAppConfig", event.port_app_config
        )

        cached_projects = event.attributes.setdefault(
            PROJECTS_CACHE_KEY, {}
        ).setdefault(self.gitlab_client.private_token, {})

        if cached_projects:
            yield cached_projects.values()
            return

        async for projects_batch in AsyncFetcher.fetch_batch(
            fetch_func=self.gitlab_client.projects.list,
            validation_func=self.should_run_for_project,
            include_subgroups=True,
            owned=port_app_config.filter_owned_projects,
            visibility=port_app_config.project_visibility_filter,
            pagination="offset",
            order_by="id",
            sort="asc",
        ):
            projects: List[Project] = typing.cast(List[Project], projects_batch)
            logger.info(
                f"Queried {len(projects)} projects {[project.path_with_namespace for project in projects]}"
            )
            cached_projects = event.attributes[PROJECTS_CACHE_KEY][
                self.gitlab_client.private_token
            ]
            cached_projects.update({project.id: project for project in projects})
            yield projects

    @classmethod
    async def async_project_language_wrapper(cls, project: Project) -> dict[str, Any]:
        try:
            languages = await anyio.to_thread.run_sync(project.languages)
            return {"__languages": languages}
        except Exception as e:
            logger.warning(
                f"Failed to get languages for project={project.path_with_namespace}. error={e}"
            )
            return {"__languages": {}}

    @classmethod
    async def enrich_project_with_extras(cls, project: Project) -> dict[str, Any]:
        tasks = [
            cls.async_project_language_wrapper(project),
        ]
        tasks_extras = await asyncio.gather(*tasks)
        project_with_extras = project.asdict()
        project_with_extras.update(
            **{
                key: value
                for task_extras in tasks_extras
                for key, value in task_extras.items()
            }
        )
        return project_with_extras

    @staticmethod
    def validate_file_is_directory(
        file: Union[RESTObject, dict[str, Any], Project]
    ) -> bool:
        if isinstance(file, dict):
            return file["type"] == "tree"
        return False

    async def get_all_folders_in_project_path(
        self, project: Project, folder_selector
    ) -> typing.AsyncIterator[List[dict[str, Any]]]:
        branch = folder_selector.branch or project.default_branch
        try:
            async for repository_tree_batch in AsyncFetcher.fetch_batch(
                fetch_func=project.repository_tree,
                validation_func=self.validate_file_is_directory,
                path=folder_selector.path,
                ref=branch,
                pagination="keyset",
                order_by="id",
                sort="asc",
            ):
                repository_tree_files: List[dict[str, Any]] = typing.cast(
                    List[dict[str, Any]], repository_tree_batch
                )
                logger.info(
                    f"Found {len(repository_tree_files)} folders {[folder['path'] for folder in repository_tree_files]}"
                    f" in project {project.path_with_namespace}"
                )
                yield [
                    {
                        "folder": folder,
                        "repo": project.asdict(),
                        "__branch": branch,
                    }
                    for folder in repository_tree_files
                ]
        except Exception as e:
            logger.error(
                f"Failed to get folders in project={project.path_with_namespace} for path={folder_selector.path} and "
                f"branch={branch}. error={e}"
            )
            return

    async def get_all_jobs(
        self, project: Project
    ) -> typing.AsyncIterator[List[ProjectPipelineJob]]:
        def should_run_for_job(_: Union[RESTObject, dict[str, Any], Project]) -> bool:
            return True

        logger.info(f"fetching jobs for project {project.path_with_namespace}")
        async for pipeline_jobs_batch in AsyncFetcher.fetch_batch(
            fetch_func=project.jobs.list,
            validation_func=should_run_for_job,
            pagination="offset",
            order_by="id",
            sort="asc",
        ):
            pipeline_jobs = typing.cast(List[ProjectPipelineJob], pipeline_jobs_batch)

            logger.info(
                f"Queried {len(pipeline_jobs)} jobs {[job.name for job in pipeline_jobs]}"
            )
            yield pipeline_jobs

    async def get_all_pipelines(
        self, project: Project
    ) -> typing.AsyncIterator[List[ProjectPipeline]]:
        from_time = datetime.now() - timedelta(days=14)
        created_after = from_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        def should_run_for_pipeline(
            _: Union[RESTObject, dict[str, Any], Project]
        ) -> bool:
            return True

        logger.info(
            f"Fetching pipelines for project {project.path_with_namespace} created after {created_after}"
        )
        async for pipelines_batch in AsyncFetcher.fetch_batch(
            fetch_func=project.pipelines.list,
            validation_func=should_run_for_pipeline,
            pagination="offset",
            order_by="id",
            sort="asc",
            created_after=created_after,
        ):
            pipelines = typing.cast(List[ProjectPipeline], pipelines_batch)
            logger.info(
                f"Queried {len(pipelines)} pipelines {[pipeline.id for pipeline in pipelines]}"
            )
            yield pipelines

    async def get_opened_merge_requests(
        self, group: Group
    ) -> typing.AsyncIterator[List[MergeRequest]]:
        async for merge_request_batch in AsyncFetcher.fetch_batch(
            fetch_func=group.mergerequests.list,
            validation_func=self.should_run_for_merge_request,
            pagination="offset",
            order_by="created_at",
            sort="desc",
            state="opened",
        ):
            merge_requests: List[MergeRequest] = typing.cast(
                List[MergeRequest], merge_request_batch
            )
            yield merge_requests

    async def get_closed_merge_requests(
        self, group: Group, updated_after: datetime
    ) -> typing.AsyncIterator[List[MergeRequest]]:
        async for merge_request_batch in AsyncFetcher.fetch_batch(
            fetch_func=group.mergerequests.list,
            validation_func=self.should_run_for_merge_request,
            pagination="offset",
            order_by="created_at",
            sort="desc",
            state=["closed", "locked", "merged"],
            updated_after=updated_after.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        ):
            merge_requests: List[MergeRequest] = typing.cast(
                List[MergeRequest], merge_request_batch
            )
            yield merge_requests

    async def get_all_issues(self, group: Group) -> typing.AsyncIterator[List[Issue]]:
        async for issues_batch in AsyncFetcher.fetch_batch(
            fetch_func=group.issues.list,
            validation_func=self.should_run_for_issue,
            pagination="offset",
            order_by="created_at",
            sort="desc",
        ):
            issues: List[Issue] = typing.cast(List[Issue], issues_batch)
            yield issues

    def get_entities_diff(
        self,
        project: Project,
        spec_path: str | List[str],
        before: str,
        after: str,
        ref: str,
    ) -> Tuple[List[Entity], List[Entity]]:
        logger.info(
            f'Getting entities diff for project {project.path_with_namespace}, in path "{spec_path}", before {before},'
            f" after {after}, ref {ref}"
        )
        entities_before = self._get_entities_by_commit(project, spec_path, before, ref)

        logger.info(f"Found {len(entities_before)} entities in the previous state")

        entities_after = self._get_entities_by_commit(project, spec_path, after, ref)

        logger.info(f"Found {len(entities_after)} entities in the current state")

        return entities_before, entities_after

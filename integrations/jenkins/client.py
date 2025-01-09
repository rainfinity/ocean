from enum import StrEnum
from typing import Any, AsyncGenerator, Optional
from urllib.parse import urlparse, urljoin
import httpx

from loguru import logger

from port_ocean.context.event import event
from port_ocean.utils import http_async_client

PAGE_SIZE = 50


class ResourceKey(StrEnum):
    JOBS = "jobs"
    BUILDS = "builds"
    STAGES = "stages"


class JenkinsClient:
    def __init__(
        self, jenkins_base_url: str, jenkins_user: str, jenkins_token: str
    ) -> None:
        self.jenkins_base_url = jenkins_base_url
        self.client = http_async_client
        self.client.auth = httpx.BasicAuth(jenkins_user, jenkins_token)

    async def get_jobs(self) -> AsyncGenerator[list[dict[str, Any]], None]:
        if cache := event.attributes.get(ResourceKey.JOBS):
            logger.info("picking jenkins jobs from cache")
            yield cache
            return

        async for jobs in self.fetch_resources(ResourceKey.JOBS):
            event.attributes.setdefault(ResourceKey.JOBS, []).extend(jobs)
            yield jobs

    async def get_builds(self) -> AsyncGenerator[list[dict[str, Any]], None]:
        if cache := event.attributes.get(ResourceKey.BUILDS):
            logger.info("picking jenkins builds from cache")
            yield cache
            return

        async for _jobs in self.fetch_resources(ResourceKey.BUILDS):
            builds = [build for job in _jobs for build in job.get("builds", [])]
            logger.debug(f"Builds received {builds}")
            event.attributes.setdefault(ResourceKey.BUILDS, []).extend(builds)
            yield builds

    async def _get_build_stages(self, build_url: str) -> list[dict[str, Any]]:
        response = await self.client.get(f"{build_url}/wfapi/describe")
        response.raise_for_status()
        stages = response.json().get("stages", [])
        return stages

    async def _get_job_builds(self, job_url: str) -> AsyncGenerator[Any, None]:
        job_details = await self.get_single_resource(job_url)
        if job_details.get("buildable"):
            yield job_details.get("builds")

        job = {"url": job_url}
        async for _jobs in self.fetch_resources(ResourceKey.BUILDS, job):
            builds = [build for job in _jobs for build in job.get("builds", [])]
            yield builds

    async def get_stages(
        self, job_url: str
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        async for builds in self._get_job_builds(job_url):
            stages: list[dict[str, Any]] = []
            for build in builds:
                build_url = build["url"]
                try:
                    logger.info(f"Getting stages for build {build_url}")
                    build_stages = await self._get_build_stages(build_url)
                    stages.extend(build_stages)
                    yield build_stages
                except Exception as e:
                    logger.error(
                        f"Failed to get stages for build {build_url}: {e.args[0]}"
                    )

    async def fetch_resources(
        self, resource: str, parent_job: Optional[dict[str, Any]] = None
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        page_size = PAGE_SIZE
        page = 0

        child_jobs = []

        while True:
            params = self._build_api_params(resource, page_size, page)
            base_url = self._build_base_url(parent_job)
            logger.info(f"Fetching {resource} from {base_url} with params {params}")

            job_response = await self.client.get(f"{base_url}/api/json", params=params)
            job_response.raise_for_status()
            logger.debug(f"Fetched {job_response.json()}")
            jobs = job_response.json().get("jobs", [])
            logger.info(f"Fetched {len(jobs)} jobs")

            if not jobs:
                break

            enriched_jobs = self.enrich_jobs(jobs, parent_job)

            # immediately return buildable jobs
            yield [job for job in enriched_jobs if job.get("buildable")]

            folder_jobs = [job for job in enriched_jobs if job.get("jobs")]
            child_jobs.extend(folder_jobs)

            page += 1

            if len(jobs) < page_size:
                break

        for job in child_jobs:
            async for fetched_jobs in self.fetch_resources(resource, job):
                yield fetched_jobs

    def _build_api_params(
        self, resource: str, page_size: int, page: int
    ) -> dict[str, Any]:
        start_idx = page_size * page
        end_idx = start_idx + page_size

        jobs_pagination = f"{{{start_idx},{end_idx}}}"
        builds_query = (
            ",builds[id,number,url,result,duration,timestamp,displayName,fullDisplayName,previousBuild[id,url]]{0,100}"
            if resource == "builds"
            else ""
        )
        jobs_query = f"jobs[name,url,displayName,fullName,color,buildable,jobs[name,color,fullName,displayName,url]{builds_query}]"

        return {"tree": jobs_query + jobs_pagination}

    def _build_base_url(self, parent_job: Optional[dict[str, Any]]) -> str:
        job_path = urlparse(parent_job["url"]).path if parent_job else ""
        return f"{self.jenkins_base_url}{job_path}"

    def enrich_jobs(
        self, jobs: list[dict[str, Any]], parent_job: dict[str, Any] | None
    ) -> list[dict[str, Any]]:
        if parent_job:
            return [{**job, "__parentJob": parent_job} for job in jobs]

        return jobs

    async def get_single_resource(self, resource_url: str) -> dict[str, Any]:
        """
        Get either a job or build using the url from the event e.g.

        Job: job/JobName/
        Build: job/JobName/34/
        """
        # Ensure resource_url ends with a slash
        if not resource_url.endswith("/"):
            resource_url += "/"

        # Construct the full URL using urljoin
        fetch_url = urljoin(self.jenkins_base_url, f"{resource_url}api/json")

        response = await self.client.get(fetch_url)
        response.raise_for_status()
        return response.json()

    async def get_users(self) -> AsyncGenerator[list[dict[str, Any]], None]:
        page_size = PAGE_SIZE
        page = 0

        while True:
            start_idx = page_size * page
            end_idx = start_idx + page_size

            params = {"tree": f"users[user[*],*]{{{start_idx},{end_idx}}}"}

            response = await self.client.get(
                f"{self.jenkins_base_url}/people/api/json", params=params
            )
            response.raise_for_status()
            users = response.json()["users"]

            if not users:
                break

            yield users

            page += 1

            if len(users) < page_size:
                break
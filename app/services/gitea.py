from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx

TEHRAN_TZ = ZoneInfo("Asia/Tehran")
UTC_TZ = ZoneInfo("UTC")


@dataclass
class RepoData:
    gitea_id: int
    name: str
    full_name: str
    description: str
    url: str


@dataclass
class CommitData:
    sha: str
    repo_name: str
    repo_full_name: str
    author_name: str
    author_email: str
    timestamp: datetime  # UTC-aware
    title: str
    description: str


class GiteaError(Exception):
    pass


class GiteaAuthError(GiteaError):
    pass


def _tehran_day_bounds(date_str: str) -> tuple[datetime, datetime]:
    d = date.fromisoformat(date_str)
    start = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=TEHRAN_TZ)
    end = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=TEHRAN_TZ)
    return start.astimezone(UTC_TZ), end.astimezone(UTC_TZ)


class GiteaClient:
    def __init__(self, base_url: str, token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "GiteaClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"token {self._token}"},
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client:
            await self._client.aclose()

    async def validate_connection(self) -> str:
        """Verify credentials and return the authenticated username."""
        assert self._client, "Use GiteaClient as an async context manager"
        try:
            r = await self._client.get("/api/v1/user")
        except httpx.ConnectError as exc:
            raise GiteaError(f"Cannot reach Gitea at {self._base_url}") from exc
        if r.status_code == 401:
            raise GiteaAuthError("Invalid Gitea token — check GITEA_TOKEN")
        r.raise_for_status()
        return r.json()["login"]

    async def list_repos(self) -> list[RepoData]:
        """Return all repositories accessible to the configured token."""
        assert self._client
        repos: list[RepoData] = []
        page = 1
        while True:
            r = await self._client.get(
                "/api/v1/repos/search", params={"limit": 50, "page": page}
            )
            r.raise_for_status()
            batch = r.json().get("data", [])
            for item in batch:
                repos.append(
                    RepoData(
                        gitea_id=item["id"],
                        name=item["name"],
                        full_name=item["full_name"],
                        description=item.get("description") or "",
                        url=item["html_url"],
                    )
                )
            if len(batch) < 50:
                break
            page += 1
        return repos

    async def fetch_commits_for_day(
        self, repo_full_name: str, date_str: str
    ) -> list[CommitData]:
        """Fetch all commits in the given Tehran calendar day for one repo."""
        assert self._client
        since, until = _tehran_day_bounds(date_str)
        commits: list[CommitData] = []
        seen: set[str] = set()
        page = 1

        while True:
            r = await self._client.get(
                f"/api/v1/repos/{repo_full_name}/commits",
                params={
                    "since": since.isoformat(),
                    "until": until.isoformat(),
                    "stat": "false",
                    "verification": "false",
                    "files": "false",
                    "limit": 50,
                    "page": page,
                },
            )
            if r.status_code in (404, 409):
                break  # empty/unborn repo or inaccessible
            r.raise_for_status()

            batch = r.json()
            if not batch:
                break

            for item in batch:
                sha: str = item["sha"]
                if sha in seen:
                    continue
                seen.add(sha)

                commit_meta = item["commit"]
                author = commit_meta["author"]
                message: str = commit_meta["message"].strip()
                title, _, body = message.partition("\n")

                ts = datetime.fromisoformat(
                    author["date"].replace("Z", "+00:00")
                )

                commits.append(
                    CommitData(
                        sha=sha,
                        repo_name=repo_full_name.split("/")[-1],
                        repo_full_name=repo_full_name,
                        author_name=author["name"],
                        author_email=author["email"],
                        timestamp=ts,
                        title=title.strip(),
                        description=body.strip(),
                    )
                )

            if len(batch) < 50:
                break
            page += 1

        return commits

    async def fetch_commit_diff(
        self, repo_full_name: str, sha: str, max_lines_per_file: int = 10
    ) -> str:
        """Fetch a truncated unified diff for a commit. Returns empty string on failure."""
        assert self._client
        try:
            # Gitea's REST API (/api/v1/...) has no raw-diff endpoint; the .diff suffix
            # on the web path returns a standard unified diff without authentication issues
            r = await self._client.get(f"/{repo_full_name}/commit/{sha}.diff")
            if r.status_code != 200:
                return ""
            # Keep file headers intact (diff/index/---/+++) and truncate hunk content
            # to max_lines_per_file lines per file section (per ADR-012: ~10 lines is enough
            # for the LLM to understand intent without overloading the context window)
            truncated: list[str] = []
            content_lines = 0
            in_header = True
            for line in r.text.splitlines():
                if line.startswith("diff --git"):
                    in_header = True
                    content_lines = 0
                    truncated.append(line)
                elif in_header and (
                    line.startswith("index ")
                    or line.startswith("--- ")
                    or line.startswith("+++ ")
                ):
                    truncated.append(line)
                elif line.startswith("@@"):
                    in_header = False
                    content_lines = 0
                    truncated.append(line)
                elif not in_header and content_lines < max_lines_per_file:
                    truncated.append(line)
                    content_lines += 1
            return "\n".join(truncated)
        except Exception:
            return ""

from dataclasses import dataclass, field

from app.core.config import settings
from app.models.orm import Commit


@dataclass
class RepositoryData:
    name: str
    full_name: str
    description: str
    organization: str
    commits: list[Commit] = field(default_factory=list)


@dataclass
class OrganizationData:
    name: str
    repositories: list[RepositoryData] = field(default_factory=list)


@dataclass
class ContributorData:
    name: str
    email: str
    commits: list[Commit] = field(default_factory=list)

    @property
    def repositories(self) -> list[str]:
        # dict.fromkeys preserves insertion order while deduplicating
        return list(dict.fromkeys(c.repository.name for c in self.commits))


@dataclass
class AggregatedDay:
    date_str: str
    repositories: list[RepositoryData]
    organizations: list[OrganizationData]
    contributors: list[ContributorData]
    total_commits: int
    non_atomic_commits: int
    atomic_commit_threshold: int


def aggregate_commits(date_str: str, commits: list[Commit]) -> AggregatedDay:
    threshold = settings.atomic_commit_threshold
    non_atomic = 0

    repos: dict[str, RepositoryData] = {}
    contributors: dict[str, ContributorData] = {}

    for commit in commits:
        repo = commit.repository
        if repo.name not in repos:
            org = repo.full_name.split("/")[0] if "/" in repo.full_name else repo.name
            repos[repo.name] = RepositoryData(
                name=repo.name,
                full_name=repo.full_name,
                description=repo.description,
                organization=org,
            )
        repos[repo.name].commits.append(commit)

        # Identity key is name+email: MVP uses raw Git identity, no merging of multiple emails
        key = f"{commit.author_name}:{commit.author_email}"
        if key not in contributors:
            contributors[key] = ContributorData(
                name=commit.author_name,
                email=commit.author_email,
            )
        contributors[key].commits.append(commit)

        # files_changed is nullable: Gitea's commit-list endpoint omits stats unless
        # explicitly requested per-commit, so we skip the check when absent
        if commit.files_changed is not None and commit.files_changed > threshold:
            non_atomic += 1

    # Group repositories by organization (owner prefix of full_name)
    org_map: dict[str, OrganizationData] = {}
    for repo_data in repos.values():
        org_name = repo_data.organization
        if org_name not in org_map:
            org_map[org_name] = OrganizationData(name=org_name)
        org_map[org_name].repositories.append(repo_data)

    return AggregatedDay(
        date_str=date_str,
        repositories=list(repos.values()),
        organizations=list(org_map.values()),
        contributors=list(contributors.values()),
        total_commits=len(commits),
        non_atomic_commits=non_atomic,
        atomic_commit_threshold=threshold,
    )

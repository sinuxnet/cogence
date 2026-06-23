from dataclasses import dataclass, field

from app.core.config import settings
from app.models.orm import Commit


@dataclass
class RepositoryData:
    name: str
    full_name: str
    description: str
    commits: list[Commit] = field(default_factory=list)


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
            repos[repo.name] = RepositoryData(
                name=repo.name,
                full_name=repo.full_name,
                description=repo.description,
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

    return AggregatedDay(
        date_str=date_str,
        repositories=list(repos.values()),
        contributors=list(contributors.values()),
        total_commits=len(commits),
        non_atomic_commits=non_atomic,
        atomic_commit_threshold=threshold,
    )

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import Commit, Repository
from app.services.gitea import CommitData, RepoData

TEHRAN_TZ = ZoneInfo("Asia/Tehran")
UTC_TZ = ZoneInfo("UTC")


def _tehran_day_bounds(date_str: str) -> tuple[datetime, datetime]:
    from datetime import date

    d = date.fromisoformat(date_str)
    start = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=TEHRAN_TZ).astimezone(UTC_TZ)
    end = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=TEHRAN_TZ).astimezone(UTC_TZ)
    return start, end


async def upsert_repository(session: AsyncSession, repo: RepoData) -> Repository:
    result = await session.execute(
        select(Repository).where(Repository.gitea_id == repo.gitea_id)
    )
    orm_repo = result.scalar_one_or_none()

    if orm_repo is None:
        orm_repo = Repository(
            gitea_id=repo.gitea_id,
            name=repo.name,
            full_name=repo.full_name,
            description=repo.description,
            url=repo.url,
        )
        session.add(orm_repo)
        await session.flush()
    else:
        orm_repo.name = repo.name
        orm_repo.full_name = repo.full_name
        orm_repo.description = repo.description
        orm_repo.url = repo.url

    return orm_repo


async def ingest_commit(
    session: AsyncSession, commit: CommitData, repository_id: int
) -> bool:
    """Insert commit if not already present. Returns True if new, False if duplicate."""
    result = await session.execute(select(Commit.id).where(Commit.sha == commit.sha))
    if result.scalar_one_or_none() is not None:
        return False

    session.add(
        Commit(
            repository_id=repository_id,
            sha=commit.sha,
            author_name=commit.author_name,
            author_email=commit.author_email,
            timestamp=commit.timestamp,
            title=commit.title,
            description=commit.description,
        )
    )
    return True


async def query_commits_for_day(session: AsyncSession, date_str: str) -> list[Commit]:
    """Return all stored commits for a Tehran calendar day, ordered by timestamp."""
    since, until = _tehran_day_bounds(date_str)
    result = await session.execute(
        select(Commit)
        .where(Commit.timestamp >= since, Commit.timestamp <= until)
        .order_by(Commit.timestamp)
    )
    return list(result.scalars())

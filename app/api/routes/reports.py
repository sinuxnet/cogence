import json
from datetime import date as dt_date, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_session
from app.models.orm import Report
from app.services.gitea import GiteaClient
from app.services.ingest import ingest_commit, query_commits_for_day, upsert_repository
from app.services.report import build_report
from app.core.config import settings

_TEHRAN_TZ = ZoneInfo("Asia/Tehran")

router = APIRouter(prefix="/api/v1/reports/daily", dependencies=[Depends(require_auth)])


def _parse_date(date: str) -> None:
    try:
        dt_date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD")


@router.post("/{date}/generate")
async def generate_report(
    date: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    _parse_date(date)

    # Idempotency: same date always returns the same stored report without re-generating
    existing = await session.scalar(select(Report).where(Report.report_date == date))
    if existing:
        return json.loads(existing.content)

    async with GiteaClient(settings.gitea_url, settings.gitea_token) as client:
        await client.validate_connection()
        repos = await client.list_repos()
        for repo in repos:
            orm_repo = await upsert_repository(session, repo)
            commits_data = await client.fetch_commits_for_day(repo.full_name, date)
            for cd in commits_data:
                await ingest_commit(session, cd, orm_repo.id)
        # Commit ingest before querying so relationships resolve correctly
        await session.commit()

        all_commits = await query_commits_for_day(session, date)

        # Diffs are fetched while the Gitea client is still open; they are passed to
        # the LLM and never stored (per ADR-012: truncated diff for LLM translation)
        diffs: dict[str, str] = {}
        for commit in all_commits:
            diff = await client.fetch_commit_diff(commit.repository.full_name, commit.sha)
            if diff:
                diffs[commit.sha] = diff

    report_content = await build_report(date, all_commits, diffs, use_ai=True)

    report = Report(
        report_date=date,
        content=json.dumps(report_content, ensure_ascii=False),
        generated_at=datetime.now(tz=_TEHRAN_TZ),
    )
    session.add(report)
    await session.commit()

    return report_content


@router.get("/latest")
async def get_latest_report(session: AsyncSession = Depends(get_session)) -> dict:
    row = await session.scalar(select(Report).order_by(desc(Report.report_date)).limit(1))
    if row is None:
        raise HTTPException(status_code=404, detail="No reports generated yet")
    return json.loads(row.content)


@router.get("/{date}")
async def get_report(date: str, session: AsyncSession = Depends(get_session)) -> dict:
    _parse_date(date)
    row = await session.scalar(select(Report).where(Report.report_date == date))
    if row is None:
        raise HTTPException(status_code=404, detail=f"No report for {date}")
    return json.loads(row.content)

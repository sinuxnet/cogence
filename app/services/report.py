import time
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.models.orm import Commit
from app.services.aggregator import aggregate_commits
from app.services.ai import generate_ai_report

_TEHRAN_TZ = ZoneInfo("Asia/Tehran")


def _template_report(day, duration_ms: int) -> dict:
    if day.total_commits == 0:
        executive_summary = f"No engineering activity was recorded on {day.date_str}."
        repositories: list[dict] = []
        contributors: list[dict] = []
        management_notes = "This may reflect a holiday or non-coding day."
    else:
        executive_summary = (
            f"Engineering activity included {day.total_commits} commit(s) across "
            f"{len(day.repositories)} repository/repositories by "
            f"{len(day.contributors)} contributor(s)."
        )
        repositories = [
            {"name": r.name, "summary": f"Activity recorded in {r.name}."}
            for r in day.repositories
        ]
        contributors = [
            {"name": c.name, "summary": f"Contributed to {', '.join(c.repositories)}."}
            for c in day.contributors
        ]
        management_notes = "Engineering activity recorded for this day."
        if day.non_atomic_commits > 0:
            management_notes += (
                " Some commits touched many files, which may reduce summary precision."
                " Atomic commits help Cogence provide clearer insights."
            )

    return {
        "report_date": day.date_str,
        "report_type": "daily",
        "report_depth": "standard",
        "locale": settings.report_locale,
        "timezone": "Asia/Tehran",
        "executive_summary": executive_summary,
        "repositories": repositories,
        "contributors": contributors,
        "management_notes": management_notes,
        "metadata": {
            "generated_at": datetime.now(tz=_TEHRAN_TZ).isoformat(),
            "delivery": ["api"],
            "total_commits": day.total_commits,
            "total_repositories": len(day.repositories),
            "total_contributors": len(day.contributors),
            "non_atomic_commits": day.non_atomic_commits,
            "atomic_commit_threshold": day.atomic_commit_threshold,
            "generation_duration_ms": duration_ms,
            "llm_model": None,
            "llm_tokens_used": None,
        },
    }


async def _ai_report(day, diffs: dict[str, str]) -> dict:
    result = await generate_ai_report(day, diffs)

    repositories = [
        {"name": r.name, "summary": result.repository_summaries.get(r.name, "")}
        for r in day.repositories
    ]
    contributors = [
        {"name": c.name, "summary": result.contributor_summaries.get(c.name, "")}
        for c in day.contributors
    ]
    management_notes = result.management_notes
    if day.non_atomic_commits > 0:
        management_notes += (
            " Some commits touched many files, which may reduce summary precision."
            " Atomic commits help Cogence provide clearer insights."
        )

    return {
        "report_date": day.date_str,
        "report_type": "daily",
        "report_depth": "standard",
        "locale": settings.report_locale,
        "timezone": "Asia/Tehran",
        "executive_summary": result.executive_summary,
        "repositories": repositories,
        "contributors": contributors,
        "management_notes": management_notes,
        "metadata": {
            "generated_at": datetime.now(tz=_TEHRAN_TZ).isoformat(),
            "delivery": ["api"],
            "total_commits": day.total_commits,
            "total_repositories": len(day.repositories),
            "total_contributors": len(day.contributors),
            "non_atomic_commits": day.non_atomic_commits,
            "atomic_commit_threshold": day.atomic_commit_threshold,
            "generation_duration_ms": result.duration_ms,
            "llm_model": settings.openai_model,
            "llm_tokens_used": result.tokens_used,
        },
    }


async def build_report(
    date_str: str,
    commits: list[Commit],
    diffs: dict[str, str] | None = None,
    use_ai: bool = True,
) -> dict:
    day = aggregate_commits(date_str, commits)
    start = time.monotonic()

    # Skip LLM on empty days — template handles the "no activity" copy correctly
    # and avoids burning tokens on a trivial response
    if not use_ai or day.total_commits == 0:
        duration_ms = int((time.monotonic() - start) * 1000)
        return _template_report(day, duration_ms)

    try:
        return await _ai_report(day, diffs or {})
    except Exception:
        # Graceful degradation: on any LLM failure return a factual template report
        # so the API caller still gets a valid response (per Slice 4 done-criteria AC-7.2)
        duration_ms = int((time.monotonic() - start) * 1000)
        report = _template_report(day, duration_ms)
        report["metadata"]["llm_model"] = settings.openai_model
        report["metadata"]["llm_error"] = "LLM unavailable; template fallback used."
        return report

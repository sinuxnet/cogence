import time
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.core.log_setup import get_logger
from app.models.orm import Commit
from app.services.aggregator import AggregatedDay, aggregate_commits
from app.services.ai import generate_ai_report

log = get_logger("report")

_TEHRAN_TZ = ZoneInfo("Asia/Tehran")


def _build_metadata(day: AggregatedDay, duration_ms: int, llm_model: str | None, llm_tokens: int | None) -> dict:
    return {
        "generated_at": datetime.now(tz=_TEHRAN_TZ).isoformat(),
        "delivery": ["api"],
        "total_updates": day.total_commits,
        "total_organizations": len(day.organizations),
        "total_repositories": len(day.repositories),
        "total_contributors": len(day.contributors),
        "non_atomic_commits": day.non_atomic_commits,
        "atomic_commit_threshold": day.atomic_commit_threshold,
        "generation_duration_ms": duration_ms,
        "llm_model": llm_model,
        "llm_tokens_used": llm_tokens,
    }


def _template_report(day: AggregatedDay, duration_ms: int) -> dict:
    if day.total_commits == 0:
        return {
            "report_date": day.date_str,
            "report_type": "daily",
            "locale": settings.report_locale,
            "timezone": "Asia/Tehran",
            "general": {
                "organizations_count": 0,
                "contributor_count": 0,
                "total_updates": 0,
                "note": f"No engineering activity recorded on {day.date_str}.",
            },
            "projects": [],
            "contributors": [],
            "metadata": _build_metadata(day, duration_ms, None, None),
        }

    projects = [
        {
            "organization": org.name,
            "repositories": [
                {
                    "name": r.name,
                    "update_count": len(r.commits),
                    "summary": f"Activity recorded in {r.name}.",
                }
                for r in org.repositories
            ],
        }
        for org in day.organizations
    ]
    contributors = [
        {"name": c.name, "summary": f"Contributed to {', '.join(c.repositories)}."}
        for c in day.contributors
    ]

    return {
        "report_date": day.date_str,
        "report_type": "daily",
        "locale": settings.report_locale,
        "timezone": "Asia/Tehran",
        "general": {
            "organizations_count": len(day.organizations),
            "contributor_count": len(day.contributors),
            "total_updates": day.total_commits,
        },
        "projects": projects,
        "contributors": contributors,
        "metadata": _build_metadata(day, duration_ms, None, None),
    }


async def _ai_report(day: AggregatedDay, diffs: dict[str, str]) -> dict:
    result = await generate_ai_report(day, diffs)

    projects = [
        {
            "organization": org.name,
            "repositories": [
                {
                    "name": r.name,
                    "update_count": len(r.commits),
                    "summary": result.repository_summaries.get(r.name, ""),
                }
                for r in org.repositories
            ],
        }
        for org in day.organizations
    ]
    contributors = [
        {"name": c.name, "summary": result.contributor_summaries.get(c.name, "")}
        for c in day.contributors
    ]

    return {
        "report_date": day.date_str,
        "report_type": "daily",
        "locale": settings.report_locale,
        "timezone": "Asia/Tehran",
        "general": {
            "organizations_count": len(day.organizations),
            "contributor_count": len(day.contributors),
            "total_updates": day.total_commits,
        },
        "projects": projects,
        "contributors": contributors,
        "metadata": _build_metadata(day, result.duration_ms, settings.openai_model, result.tokens_used),
    }


async def build_report(
    date_str: str,
    commits: list[Commit],
    diffs: dict[str, str] | None = None,
    use_ai: bool = True,
) -> dict:
    day = aggregate_commits(date_str, commits)
    start = time.monotonic()

    log.info(
        "report_generation_started",
        extra={
            "date": date_str,
            "repositories_count": len(day.repositories),
            "commits_count": day.total_commits,
            "use_ai": use_ai,
        },
    )

    # Skip LLM on empty days — template handles the "no activity" copy correctly
    # and avoids burning tokens on a trivial response
    if not use_ai or day.total_commits == 0:
        duration_ms = int((time.monotonic() - start) * 1000)
        report = _template_report(day, duration_ms)
        log.info("report_generation_completed", extra={"date": date_str, "mode": "template", "duration_ms": duration_ms})
        return report

    try:
        report = await _ai_report(day, diffs or {})
        log.info("report_generation_completed", extra={"date": date_str, "mode": "ai", "duration_ms": report["metadata"]["generation_duration_ms"]})
        return report
    except Exception as exc:
        # Graceful degradation: on any LLM failure return a factual template report
        # so the API caller still gets a valid response (per Slice 4 done-criteria AC-7.2)
        duration_ms = int((time.monotonic() - start) * 1000)
        log.error("report_llm_failed", extra={"date": date_str, "error": str(exc)}, exc_info=True)
        report = _template_report(day, duration_ms)
        report["metadata"]["llm_model"] = settings.openai_model
        report["metadata"]["llm_error"] = "LLM unavailable; template fallback used."
        return report

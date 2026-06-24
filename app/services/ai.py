import time
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.log_setup import get_logger
from app.services.aggregator import AggregatedDay

log = get_logger("ai")

_LOCALE_INSTRUCTION = {
    "en": "Respond in English.",
    "fa": "Respond in Persian (Farsi). Use natural Persian business language.",
}

_NEUTRAL_TONE = (
    "Use factual, neutral language only. "
    "Do not use endorsements, evaluations, or opinions. "
    "Do not use phrases like 'significant progress', 'strong collaboration', "
    "'impressive', 'excellent', or 'will improve'. "
    "Do not predict future impact or outcomes. "
    "Describe what was done, not how good it is."
)


@dataclass
class LLMResult:
    repository_summaries: dict[str, str]
    contributor_summaries: dict[str, str]
    tokens_used: int
    duration_ms: int


async def generate_ai_report(day: AggregatedDay, diffs: dict[str, str]) -> LLMResult:
    # Two LLM calls: per-repo factual summaries and per-contributor factual summaries.
    # Executive summary and management notes removed in MVP-v2 (replaced by template stats
    # and factual-only repo/contributor descriptions).
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    locale = _LOCALE_INSTRUCTION.get(settings.report_locale, _LOCALE_INSTRUCTION["en"])
    start = time.monotonic()
    tokens = 0

    # temperature=0.3: low temperature keeps output factual and consistent across re-runs
    # for the same commit data (per ADR-005: AI generates summaries, not facts)

    # Repository summaries — diffs included because vague commit messages need code
    # context for meaningful business translation (ADR-012)
    repo_summaries: dict[str, str] = {}
    for repo_data in day.repositories:
        commit_lines = []
        for c in repo_data.commits:
            line = f"- {c.title}"
            excerpt = diffs.get(c.sha, "")
            if excerpt:
                line += f"\n  Code changes:\n{excerpt}"
            commit_lines.append(line)
        commit_list = "\n".join(commit_lines)

        resp = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.3,
            max_tokens=150,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are converting Git commits into a business-readable description "
                        f"for a non-technical manager. {_NEUTRAL_TONE} {locale}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Write one factual sentence describing what changed in repository: {repo_data.name}\n"
                        f"Organization: {repo_data.organization}\n"
                        f"Description: {repo_data.description or 'N/A'}\n\n"
                        f"Updates:\n{commit_list}\n\n"
                        "Requirements: one sentence, factual only, business language, no jargon, "
                        "no quality judgments, no predictions."
                    ),
                },
            ],
        )
        summary = (resp.choices[0].message.content or "").strip()
        repo_summaries[repo_data.name] = summary
        call_tokens = resp.usage.total_tokens if resp.usage else 0
        tokens += call_tokens
        log.info(
            "llm_repo_summary",
            extra={
                "repo": repo_data.name,
                "model": settings.openai_model,
                "tokens": call_tokens,
            },
        )

    # Contributor summaries
    contrib_summaries: dict[str, str] = {}
    for contrib in day.contributors:
        commit_list = "\n".join(
            f"- [{c.repository.name}] {c.title}" for c in contrib.commits
        )
        resp = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.3,
            max_tokens=100,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are describing an engineer's work for a non-technical manager. "
                        "Do not rank, score, compare, or evaluate contributors. "
                        f"{_NEUTRAL_TONE} {locale}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Write one factual sentence describing the work areas of: {contrib.name}\n"
                        f"Repositories: {', '.join(contrib.repositories)}\n\n"
                        f"Updates:\n{commit_list}\n\n"
                        "Requirements: one sentence, factual work areas only, "
                        "no rankings, no counts, no code jargon, no quality judgments."
                    ),
                },
            ],
        )
        summary = (resp.choices[0].message.content or "").strip()
        contrib_summaries[contrib.name] = summary
        call_tokens = resp.usage.total_tokens if resp.usage else 0
        tokens += call_tokens
        log.info(
            "llm_contributor_summary",
            extra={
                "contributor": contrib.name,
                "model": settings.openai_model,
                "tokens": call_tokens,
            },
        )

    duration_ms = int((time.monotonic() - start) * 1000)
    log.info(
        "llm_report_complete",
        extra={"total_tokens": tokens, "duration_ms": duration_ms},
    )

    return LLMResult(
        repository_summaries=repo_summaries,
        contributor_summaries=contrib_summaries,
        tokens_used=tokens,
        duration_ms=duration_ms,
    )

import time
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.aggregator import AggregatedDay

_LOCALE_INSTRUCTION = {
    "en": "Respond in English.",
    "fa": "Respond in Persian (Farsi). Use natural Persian business language.",
}


@dataclass
class LLMResult:
    executive_summary: str
    repository_summaries: dict[str, str]
    contributor_summaries: dict[str, str]
    management_notes: str
    tokens_used: int
    duration_ms: int


async def generate_ai_report(day: AggregatedDay, diffs: dict[str, str]) -> LLMResult:
    # Four separate LLM calls: each section has different tone constraints and audience
    # (executive vs. per-repo business summary vs. neutral contributor vs. advisory notes).
    # Splitting keeps each prompt focused and avoids conflicting instructions in one call.
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    locale = _LOCALE_INSTRUCTION.get(settings.report_locale, _LOCALE_INSTRUCTION["en"])
    start = time.monotonic()
    tokens = 0

    repo_list = "\n".join(f"- {r.name}: {len(r.commits)} commits" for r in day.repositories)
    commit_titles = "\n".join(
        f"- [{c.repository.name}] {c.title}"
        for r in day.repositories
        for c in r.commits
    )

    # temperature=0.3 throughout: low temperature keeps output factual and consistent
    # across re-runs for the same commit data (per ADR-005: AI generates summaries, not facts)

    # Executive summary
    exec_resp = await client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.3,
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an executive assistant translating engineering activity into business language. "
                    "Your audience is non-technical executives. Use clear, concise business language. "
                    f"Avoid technical jargon. Focus on business value and strategic alignment. {locale}"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate an executive summary for engineering activity on {day.date_str}.\n\n"
                    f"{day.total_commits} commits across {len(day.repositories)} repositories "
                    f"by {len(day.contributors)} contributors.\n\n"
                    f"Repositories:\n{repo_list}\n\n"
                    f"Commit messages:\n{commit_titles}\n\n"
                    "Requirements: 2-4 sentences, business language only, highlight key accomplishments."
                ),
            },
        ],
    )
    executive_summary = (exec_resp.choices[0].message.content or "").strip()
    tokens += exec_resp.usage.total_tokens if exec_resp.usage else 0

    # Repository summaries — diffs are included here because vague commit messages
    # (e.g. "fix", "wip") need code context for meaningful business translation (ADR-012)
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
                        "You are a technical translator converting Git commits into business-readable summaries. "
                        f"Use business language and focus on outcomes, not implementation details. {locale}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a one-sentence project summary for repository: {repo_data.name}\n"
                        f"Description: {repo_data.description or 'N/A'}\n\n"
                        f"Commits:\n{commit_list}\n\n"
                        "Requirements: one sentence, business language, focus on outcomes, no jargon."
                    ),
                },
            ],
        )
        repo_summaries[repo_data.name] = (resp.choices[0].message.content or "").strip()
        tokens += resp.usage.total_tokens if resp.usage else 0

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
                        "You are summarizing an individual's engineering contributions in business terms. "
                        "Do not rank, score, or compare contributors. "
                        f"Use neutral, respectful language. {locale}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a one-sentence contributor summary for: {contrib.name}\n"
                        f"Repositories: {', '.join(contrib.repositories)}\n\n"
                        f"Commits:\n{commit_list}\n\n"
                        "Requirements: one sentence, describe work areas in business terms, "
                        "no rankings, no commit counts, no code jargon."
                    ),
                },
            ],
        )
        contrib_summaries[contrib.name] = (resp.choices[0].message.content or "").strip()
        tokens += resp.usage.total_tokens if resp.usage else 0

    # Management notes
    patterns: list[str] = []
    if day.non_atomic_commits > 0:
        patterns.append(
            f"{day.non_atomic_commits} commit(s) touched more than "
            f"{day.atomic_commit_threshold} files"
        )
    if len(day.repositories) == 1:
        patterns.append("All activity concentrated in one repository")
    pattern_text = (
        "\n".join(f"- {p}" for p in patterns) if patterns else "No unusual patterns observed."
    )
    repo_dist = "\n".join(f"- {r.name}: {len(r.commits)} commits" for r in day.repositories)

    mgmt_resp = await client.chat.completions.create(
        model=settings.openai_model,
        temperature=0.3,
        max_tokens=200,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an engineering advisor providing concise insights to leadership. "
                    "Identify patterns and provide actionable observations. "
                    f"Be constructive, not punitive. {locale}"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate management notes for engineering activity on {day.date_str}.\n\n"
                    f"Overall: {day.total_commits} commits, {len(day.repositories)} repositories, "
                    f"{len(day.contributors)} contributors.\n\n"
                    f"Repository distribution:\n{repo_dist}\n\n"
                    f"Patterns:\n{pattern_text}\n\n"
                    "Requirements: 2-3 sentences, actionable observations, business language."
                ),
            },
        ],
    )
    management_notes = (mgmt_resp.choices[0].message.content or "").strip()
    tokens += mgmt_resp.usage.total_tokens if mgmt_resp.usage else 0

    return LLMResult(
        executive_summary=executive_summary,
        repository_summaries=repo_summaries,
        contributor_summaries=contrib_summaries,
        management_notes=management_notes,
        tokens_used=tokens,
        duration_ms=int((time.monotonic() - start) * 1000),
    )

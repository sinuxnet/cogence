"""CLI: generate a template report (no LLM) for a Tehran calendar day and print JSON."""
import asyncio
import json
import sys
from datetime import date

from app.db.session import AsyncSessionLocal
from app.services.ingest import query_commits_for_day
from app.services.report import build_report


async def main(date_str: str) -> None:
    async with AsyncSessionLocal() as session:
        commits = await query_commits_for_day(session, date_str)
    report = await build_report(date_str, commits, diffs=None, use_ai=False)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    target_date = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    asyncio.run(main(target_date))

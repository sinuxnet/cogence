"""
CLI: collect and persist commits from Gitea for a Tehran calendar day.

Usage:
    python -m app.collector [YYYY-MM-DD]

Defaults to today (Asia/Tehran) when no date is given.
"""

import asyncio
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.gitea import GiteaAuthError, GiteaClient, GiteaError
from app.services.ingest import ingest_commit, upsert_repository

TEHRAN_TZ = ZoneInfo("Asia/Tehran")


async def collect(date_str: str) -> None:
    print(f"Cogence collector — date: {date_str} (Asia/Tehran)")

    async with GiteaClient(settings.gitea_url, settings.gitea_token) as client:
        try:
            username = await client.validate_connection()
        except GiteaAuthError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        except GiteaError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

        print(f"Connected as: {username}")

        repos = await client.list_repos()
        print(f"Repositories discovered: {len(repos)}")

        total_new = 0
        total_dup = 0

        async with AsyncSessionLocal() as session:
            async with session.begin():
                for repo in repos:
                    commits = await client.fetch_commits_for_day(repo.full_name, date_str)
                    if not commits:
                        continue

                    orm_repo = await upsert_repository(session, repo)
                    new, dup = 0, 0

                    for c in commits:
                        inserted = await ingest_commit(session, c, orm_repo.id)
                        if inserted:
                            new += 1
                        else:
                            dup += 1

                    print(f"  {repo.full_name}  {new} new, {dup} duplicate(s)")
                    total_new += new
                    total_dup += dup

        print(f"\nDone — {total_new} new commits stored, {total_dup} duplicate(s) skipped")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = datetime.now(TEHRAN_TZ).strftime("%Y-%m-%d")

    asyncio.run(collect(date_str))

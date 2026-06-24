# ADR-014: RTL-First Persian Locale With Jalali Calendar

## Status

Accepted

## Date

2026-06-24

Rocket.Chat determines text direction for an entire message from the script of its **first line**. If the first line is Latin (English), the whole message renders left-to-right — which makes Persian text with embedded English technical terms nearly unreadable, because words flow in the wrong direction relative to the surrounding script.

Additionally, Iranian managers read dates in the Jalali (Solar Hijri) calendar. Showing `2026-07-04` in a Persian report is correct but culturally mismatched.

## Decision

When `REPORT_LOCALE=fa`:

1. The first line of every delivered message is a Persian date string — e.g. `گزارش روز 4 تیر 1404` — so Rocket.Chat treats the entire message as RTL.
2. The date in that line is in the Jalali calendar, computed via the `jdatetime` Python library. Western (ASCII) numerals are used (`4` not `۴`) to avoid font rendering issues in Rocket.Chat.
3. The Report Footer line is always in English regardless of locale, because it contains only numbers and short fixed labels that render correctly in both directions.
4. Within report body text, technical terms (API, endpoint, OAuth, library names) stay in English. Product-domain terms are written in Persian when a natural equivalent exists; the LLM is given judgment on this boundary rather than a hard-coded glossary.

## Considered Options

- **No RTL fix**: Persian text with English terms renders as garbled mixed-direction text. Unacceptable for the primary audience.
- **Separate `CALENDAR_SYSTEM` env var**: Decouples calendar from locale, but the use case (English + Jalali or Persian + Gregorian) does not exist in practice. Adds configuration surface for no benefit.
- **Persian-Arabic numerals (`۴`)**: Correct by convention but causes inconsistent rendering across Rocket.Chat clients. Western numerals in an RTL context are unambiguous and widely used in Iranian business writing.

## Consequences

- `jdatetime` is added as a production dependency.
- The delivery script gains a locale branch: if `REPORT_LOCALE=fa`, it prepends the Persian date line before the first heading.
- The Report Footer is hardcoded in English and must never be localized, or it will break the RTL trick (the footer is the last line, so direction is already set by the first line — but keeping it English is simpler and consistent with the "stats are universal" intent).

#!/usr/bin/env python3
"""Fetch GitHub contribution activity with resilient parsing and error handling.

GitHub removed the `data-count` attribute from the contribution calendar's
<td> cells at some point. The count now only lives in a linked <tool-tip>
element's text (e.g. "4 contributions on August 24th." / "No contributions
on August 3rd."). This parses both the old rect/data-count markup (kept as
a fallback) and the current td + tool-tip markup.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from pathlib import Path
import json

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "contributions.json"
URL = "https://github.com/users/Kavish-Paraswar/contributions"

COUNT_RE = re.compile(r"(\d+)\s+contributions?", re.IGNORECASE)


class ContributionFetchError(RuntimeError):
    """Raised when contributions could not be fetched."""


def _parse_legacy(soup: BeautifulSoup) -> list[dict]:
    """Old markup: rect/td elements carry data-count directly."""
    cells = soup.select("rect[data-date][data-count], td[data-date][data-count]")
    days = []
    for cell in cells:
        date_value = cell.get("data-date", "")
        if not date_value:
            continue
        days.append(
            {
                "date": date_value,
                "count": int(cell.get("data-count", "0") or 0),
                "level": int(cell.get("data-level", "0") or 0),
            }
        )
    return days


def _parse_tooltip(soup: BeautifulSoup) -> list[dict]:
    """Current markup: td[data-date] + a separate tool-tip[for=<td id>] with the count in its text."""
    tooltip_by_for = {
        tip.get("for"): tip.get_text(strip=True)
        for tip in soup.select("tool-tip[for]")
        if tip.get("for")
    }

    days = []
    for cell in soup.select("td[data-date]"):
        date_value = cell.get("data-date", "")
        if not date_value:
            continue
        tooltip_text = tooltip_by_for.get(cell.get("id", ""), "")
        match = COUNT_RE.search(tooltip_text)
        count = int(match.group(1)) if match else 0
        days.append(
            {
                "date": date_value,
                "count": count,
                "level": int(cell.get("data-level", "0") or 0),
            }
        )
    return days


def parse_contributions(html: str) -> list[dict]:
    """Parse contribution day entries, trying legacy markup first, then the tool-tip based markup."""
    soup = BeautifulSoup(html, "html.parser")

    days = _parse_legacy(soup)
    if not days:
        days = _parse_tooltip(soup)

    unique_days = {item["date"]: item for item in days}
    parsed = sorted(unique_days.values(), key=lambda d: d["date"])
    if not parsed:
        raise ContributionFetchError(
            "GitHub returned no contribution cells. The profile might be private, rate-limited, or markup changed."
        )
    return parsed


def compute_streaks(days: list[dict]) -> tuple[int, int]:
    """Compute current and longest contribution streak."""
    longest = 0
    current_run = 0
    for day in days:
        if day["count"] > 0:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 0

    today = date.today()
    trailing = 0
    for day in reversed(days):
        day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if (today - day_date).days > 1 and trailing == 0:
            break
        if day["count"] > 0:
            trailing += 1
        elif trailing > 0:
            break
    return trailing, longest


def fetch_html() -> str:
    """Fetch contribution markup from GitHub with retries and browser-like headers."""
    session = requests.Session()
    retries = Retry(total=4, connect=4, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    response = session.get(URL, timeout=30, headers=headers)
    if response.status_code in (403, 429):
        limit_remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
        raise ContributionFetchError(
            f"GitHub contributions request was rate-limited (status {response.status_code}, remaining={limit_remaining})."
        )
    response.raise_for_status()
    return response.text


def write_payload(days: list[dict], error: str | None = None) -> None:
    """Write normalized contribution JSON payload."""
    total = sum(day["count"] for day in days)
    max_count = max((day["count"] for day in days), default=0)
    current_streak, longest_streak = compute_streaks(days) if days else (0, 0)
    payload = {
        "username": "Kavish-Paraswar",
        "generated_at": datetime.now(UTC).isoformat(),
        "fetch_succeeded": error is None,
        "error": error,
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "max_count": max_count,
        "days": days,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    """Fetch, parse, compute stats, and save contributions data."""
    try:
        days = parse_contributions(fetch_html())
        write_payload(days)
    except Exception as exc:  # noqa: BLE001
        write_payload([], error=str(exc))


if __name__ == "__main__":
    main()

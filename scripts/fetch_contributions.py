#!/usr/bin/env python3
"""Fetch GitHub contribution activity without GraphQL or authentication."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
import json

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "contributions.json"
URL = "https://github.com/users/Kavish-Paraswar/contributions"


def parse_contributions(html: str) -> list[dict]:
    """Parse contribution day entries from GitHub contributions HTML."""
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("svg.js-calendar-graph-svg rect[data-date]")
    days = []
    for cell in cells:
        days.append(
            {
                "date": cell.get("data-date", ""),
                "count": int(cell.get("data-count", "0")),
                "level": int(cell.get("data-level", "0")),
            }
        )
    return sorted(days, key=lambda d: d["date"])


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
    """Fetch contribution markup from GitHub user endpoint."""
    response = requests.get(URL, timeout=30, headers={"User-Agent": "profile-readme-bot"})
    response.raise_for_status()
    return response.text


def main() -> None:
    """Fetch, parse, compute stats, and save contributions data."""
    days = parse_contributions(fetch_html())
    total = sum(day["count"] for day in days)
    max_count = max((day["count"] for day in days), default=0)
    current_streak, longest_streak = compute_streaks(days)
    payload = {
        "username": "Kavish-Paraswar",
        "generated_at": datetime.now(UTC).isoformat(),
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "max_count": max_count,
        "days": days,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

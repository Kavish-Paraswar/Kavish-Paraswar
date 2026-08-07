#!/usr/bin/env python3
"""Render one-shot animated contribution heatmap SVG from local JSON data.

Renamed output to assets/git-stats.svg to match what README.md actually
references. (The old heatmap.svg was never linked from the README, so
git-stats.svg was showing as a broken image with nothing generating it.)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "assets" / "git-stats.svg"

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def load_data() -> dict:
    """Load cached contribution data."""
    if not DATA_PATH.exists():
        return {"error": f"Missing {DATA_PATH.name}", "days": []}
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON in {DATA_PATH.name}: {exc}", "days": []}


def position(date_str: str, start: datetime) -> tuple[int, int]:
    """Convert date into Sunday-based week/day grid coordinates."""
    day = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = (day.weekday() + 1) % 7
    week = (day - start).days // 7
    return week, weekday


def render_error(message: str) -> str:
    """Render meaningful terminal-style error output when fetch fails."""
    safe = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="220" viewBox="0 0 900 220" role="img" aria-label="Contribution fetch error">
  <rect width="100%" height="100%" fill="#0d1117" rx="14"/>
  <rect x="12" y="12" width="876" height="196" rx="10" fill="#010409" stroke="#30363d"/>
  <text x="24" y="36" font-family="monospace" font-size="14" fill="#8b949e">kavish@github:~$ ./contributions.sh</text>
  <text x="24" y="78" font-family="monospace" font-size="16" fill="#f85149">Failed to fetch contribution data.</text>
  <text x="24" y="106" font-family="monospace" font-size="13" fill="#c9d1d9">{safe}</text>
  <text x="24" y="146" font-family="monospace" font-size="13" fill="#8b949e">Will retry automatically on next scheduled refresh.</text>
</svg>"""


def render(data: dict) -> str:
    """Build SVG markup."""
    error = data.get("error")
    days = data.get("days") or []
    if error and not days:
        return render_error(error)
    if not days:
        return render_error("No public contribution cells were found for this profile yet.")

    first = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    start = first - timedelta(days=(first.weekday() + 1) % 7)

    cells = []
    for item in days:
        week, weekday = position(item["date"], start)
        x = 36 + week * 14
        y = 72 + weekday * 14
        delay = round((week + weekday) * 0.012, 3)
        color = COLORS[min(item["level"], 4)]
        cells.append(
            f"""  <rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{color}" opacity="0">
    <animate attributeName="opacity" begin="{delay}s" dur="0.18s" from="0" to="1" fill="freeze" />
  </rect>"""
        )

    legend = "".join(
        f"<rect x='{694 + i * 24}' y='204' width='14' height='14' rx='3' fill='{color}' />" for i, color in enumerate(COLORS)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="240" viewBox="0 0 900 240" role="img" aria-label="Git contribution statistics">
  <rect width="100%" height="100%" fill="#0d1117" rx="14"/>
  <rect x="12" y="12" width="876" height="216" rx="10" fill="#010409" stroke="#30363d"/>
  <text x="24" y="36" font-family="monospace" font-size="14" fill="#8b949e">$ ./contributions.sh</text>
  <text x="694" y="64" font-family="monospace" font-size="14" fill="#3fb950">total: {data.get('total', 0)}</text>
  <text x="694" y="88" font-family="monospace" font-size="14" fill="#3fb950">current streak: {data.get('current_streak', 0)}</text>
  <text x="694" y="112" font-family="monospace" font-size="14" fill="#3fb950">longest streak: {data.get('longest_streak', 0)}</text>
  <text x="694" y="196" font-family="monospace" font-size="13" fill="#8b949e">Legend</text>
  {legend}
  <text x="812" y="216" font-family="monospace" font-size="12" fill="#8b949e">High</text>
  <text x="648" y="216" font-family="monospace" font-size="12" fill="#8b949e">Low</text>
{''.join(cells)}
</svg>"""


def main() -> None:
    """Read local contribution data and render SVG."""
    OUTPUT_PATH.write_text(render(load_data()), encoding="utf-8")


if __name__ == "__main__":
    main()

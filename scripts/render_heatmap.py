#!/usr/bin/env python3
"""Render clean, properly bounded contribution heatmap SVG with polished stats alignment.

Heatmap grid with month labels, Less/More legend, and stats tiles positioned
under the heatmap grid with generous bottom padding so nothing feels cramped.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "assets" / "git-stats.svg"

# Classic GitHub light theme contribution palette
COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]

CELL = 12
GAP = 3
GRID_LEFT = 40
GRID_TOP = 86
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data() -> dict:
    if not DATA_PATH.exists():
        return {"error": f"Missing {DATA_PATH.name}", "days": []}
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON: {exc}", "days": []}


def traffic_dots(cx_start: int, cy: int) -> str:
    return "".join(
        f'<circle cx="{cx_start + i * 20}" cy="{cy}" r="6" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )


def render_error(message: str) -> str:
    safe = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="200" viewBox="0 0 900 200" role="img" aria-label="Contribution error">
  <rect width="100%" height="100%" fill="#ffffff" rx="16"/>
  <rect x="18" y="18" width="864" height="164" rx="12" fill="#f6f8fa" stroke="#d0d7de"/>
  {traffic_dots(42, 40)}
  <text x="40" y="62" font-family="monospace" font-size="14" fill="#57606a">$ ./contributions.sh</text>
  <text x="40" y="100" font-family="monospace" font-size="14" fill="#cf222e">Error: {safe}</text>
  <text x="40" y="130" font-family="monospace" font-size="13" fill="#57606a">Will retry on next scheduled refresh.</text>
</svg>'''


def render(data: dict) -> str:
    error = data.get("error")
    days = data.get("days") or []
    if error and not days:
        return render_error(error)
    if not days:
        return render_error("No contribution data found.")

    day_map = {d["date"]: d for d in days}
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d")
    start = first - timedelta(days=(first.weekday() + 1) % 7)

    total_days = (last - start).days + 1
    total_weeks = (total_days + 6) // 7

    cells: list[str] = []
    month_labels: list[str] = []
    prev_month = -1

    for week in range(total_weeks):
        for weekday in range(7):
            current = start + timedelta(days=week * 7 + weekday)
            date_str = current.strftime("%Y-%m-%d")
            x = GRID_LEFT + week * (CELL + GAP)
            y = GRID_TOP + weekday * (CELL + GAP)

            item = day_map.get(date_str)
            level = min(item.get("level", 0), 4) if item else 0
            color = COLORS[level]

            delay = round(week * 0.008, 3)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" begin="{delay}s" dur="0.15s" '
                f'from="0" to="1" fill="freeze"/></rect>'
            )

            if current.month != prev_month and weekday == 0:
                month_labels.append(
                    f'<text x="{x}" y="{GRID_TOP - 8}" class="month">'
                    f'{MONTH_NAMES[current.month - 1]}</text>'
                )
                prev_month = current.month

    # Heatmap grid height
    grid_bottom = GRID_TOP + 7 * (CELL + GAP) + 24

    # Legend aligned with grid on left
    legend_y = grid_bottom + 14
    legend_parts = [
        f'<text x="{GRID_LEFT}" y="{legend_y + 10}" class="legend-text">Less</text>'
    ]
    lx = GRID_LEFT + 36
    for i, color in enumerate(COLORS):
        legend_parts.append(
            f'<rect x="{lx + i * 16}" y="{legend_y}" width="{CELL}" '
            f'height="{CELL}" rx="2" fill="{color}"/>'
        )
    legend_parts.append(
        f'<text x="{lx + len(COLORS) * 16 + 6}" y="{legend_y + 10}" class="legend-text">More</text>'
    )

    # Stats Section comfortably placed under heatmap grid
    total = data.get("total", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    year = datetime.now().strftime("%Y")

    stat_box_y = grid_bottom
    stats_markup = [
        # Stat Tile 1: Total
        f'<rect x="420" y="{stat_box_y}" width="130" height="44" rx="6" fill="#ffffff" stroke="#d0d7de"/>',
        f'<text x="485" y="{stat_box_y + 17}" class="stat-lbl" text-anchor="middle">Total ({year})</text>',
        f'<text x="485" y="{stat_box_y + 35}" class="stat-val" text-anchor="middle">{total}</text>',
        # Stat Tile 2: Current Streak
        f'<rect x="562" y="{stat_box_y}" width="130" height="44" rx="6" fill="#ffffff" stroke="#d0d7de"/>',
        f'<text x="627" y="{stat_box_y + 17}" class="stat-lbl" text-anchor="middle">Current Streak</text>',
        f'<text x="627" y="{stat_box_y + 35}" class="stat-val" text-anchor="middle">{current_streak} days</text>',
        # Stat Tile 3: Longest Streak
        f'<rect x="704" y="{stat_box_y}" width="130" height="44" rx="6" fill="#ffffff" stroke="#d0d7de"/>',
        f'<text x="769" y="{stat_box_y + 17}" class="stat-lbl" text-anchor="middle">Longest Streak</text>',
        f'<text x="769" y="{stat_box_y + 35}" class="stat-val" text-anchor="middle">{longest_streak} days</text>',
    ]

    height = stat_box_y + 44 + 32  # Generous bottom padding
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Contribution graph">
  <rect width="100%" height="100%" fill="#ffffff" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#f6f8fa" stroke="#d0d7de"/>
  {traffic_dots(42, 40)}
  <text x="40" y="62" class="prompt">$ ./contributions.sh</text>
  <style>
    .prompt      {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #57606a; }}
    .month       {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #57606a; }}
    .stat-lbl    {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #57606a; }}
    .stat-val    {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #1f883d; font-weight: 700; }}
    .legend-text {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #57606a; }}
  </style>
  {''.join(month_labels)}
  {''.join(cells)}
  {''.join(legend_parts)}
  {''.join(stats_markup)}
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(render(load_data()), encoding="utf-8")


if __name__ == "__main__":
    main()

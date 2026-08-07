#!/usr/bin/env python3
"""Render contribution heatmap SVG styled like GitHub's native graph.

Light-on-dark terminal card with the heatmap grid, streak stats,
current year label, and a legend. Auto-sizes to fit the data.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "assets" / "git-stats.svg"

# GitHub-style green scale
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]
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
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="164" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="40" y="62" font-family="monospace" font-size="14" fill="#7d8590">$ ./contributions.sh</text>
  <text x="40" y="100" font-family="monospace" font-size="14" fill="#f85149">Error: {safe}</text>
  <text x="40" y="130" font-family="monospace" font-size="13" fill="#484f58">Will retry on next scheduled refresh.</text>
</svg>'''


def render(data: dict) -> str:
    error = data.get("error")
    days = data.get("days") or []
    if error and not days:
        return render_error(error)
    if not days:
        return render_error("No contribution data found.")

    # Build lookup
    day_map = {d["date"]: d for d in days}

    first = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d")
    start = first - timedelta(days=(first.weekday() + 1) % 7)  # align to Sunday

    # Compute grid
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
            if item:
                level = min(item.get("level", 0), 4)
                color = COLORS[level]
            else:
                color = COLORS[0]

            delay = round(week * 0.008, 3)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" begin="{delay}s" dur="0.15s" '
                f'from="0" to="1" fill="freeze"/></rect>'
            )

            # Month labels
            if current.month != prev_month and weekday == 0:
                month_labels.append(
                    f'<text x="{x}" y="{GRID_TOP - 8}" class="month">'
                    f'{MONTH_NAMES[current.month - 1]}</text>'
                )
                prev_month = current.month

    # Stats section
    grid_right = GRID_LEFT + total_weeks * (CELL + GAP)
    stats_x = max(grid_right + 30, 680)
    total = data.get("total", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    year = datetime.now().strftime("%Y")

    stats = [
        f'<text x="{stats_x}" y="90" class="stat-label">Total ({year})</text>',
        f'<text x="{stats_x}" y="112" class="stat-value">{total}</text>',
        f'<text x="{stats_x}" y="140" class="stat-label">Current Streak</text>',
        f'<text x="{stats_x}" y="162" class="stat-value">{current_streak} days</text>',
        f'<text x="{stats_x}" y="190" class="stat-label">Longest Streak</text>',
        f'<text x="{stats_x}" y="212" class="stat-value">{longest_streak} days</text>',
    ]

    # Legend
    grid_bottom = GRID_TOP + 7 * (CELL + GAP) + 16
    legend_parts = [
        f'<text x="{GRID_LEFT}" y="{grid_bottom + 2}" class="legend-text">Less</text>'
    ]
    lx = GRID_LEFT + 40
    for i, color in enumerate(COLORS):
        legend_parts.append(
            f'<rect x="{lx + i * 18}" y="{grid_bottom - 10}" width="{CELL}" '
            f'height="{CELL}" rx="2" fill="{color}"/>'
        )
    legend_parts.append(
        f'<text x="{lx + len(COLORS) * 18 + 6}" y="{grid_bottom + 2}" class="legend-text">More</text>'
    )

    height = grid_bottom + 30
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Contribution graph">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="40" y="62" class="prompt">$ ./contributions.sh</text>
  <style>
    .prompt      {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .month       {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #7d8590; }}
    .stat-label  {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #7d8590; }}
    .stat-value  {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #3fb950; font-weight: 700; }}
    .legend-text {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #484f58; }}
  </style>
  {''.join(month_labels)}
  {''.join(cells)}
  {''.join(stats)}
  {''.join(legend_parts)}
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(render(load_data()), encoding="utf-8")


if __name__ == "__main__":
    main()

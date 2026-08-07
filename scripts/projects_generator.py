#!/usr/bin/env python3
"""Generate auto-sizing project cards SVG with proper text wrapping."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "projects.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]
CARD_W = 408
CARD_PAD = 20
TEXT_MAX_W = CARD_W - 2 * CARD_PAD  # 368px available
CHAR_WIDTH = 7.2  # approximate monospace char width at 12px
MAX_CHARS = int(TEXT_MAX_W / CHAR_WIDTH)  # ~51 chars per line


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def traffic_dots(cx_start: int, cy: int) -> str:
    return "".join(
        f'<circle cx="{cx_start + i * 20}" cy="{cy}" r="6" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )


def wrap_text(text: str, max_chars: int) -> list[str]:
    """Word-wrap text into lines of max_chars width."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip() if current else word
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def card(project: dict, x: int, y: int, begin: float) -> tuple[str, int]:
    """Build a single project card. Returns (svg_str, card_height)."""
    parts: list[str] = []
    cy = 32  # local y within the card

    # Title
    parts.append(
        f'<text x="{CARD_PAD}" y="{cy}" class="title">{esc(project["title"])}</text>'
    )
    cy += 8

    # Separator
    cy += 10
    parts.append(
        f'<line x1="{CARD_PAD}" y1="{cy}" x2="{CARD_W - CARD_PAD}" y2="{cy}" '
        f'stroke="#21262d" stroke-width="1"/>'
    )
    cy += 18

    # Description (wrapped)
    desc_lines = wrap_text(project["description"], MAX_CHARS)
    for dl in desc_lines:
        parts.append(f'<text x="{CARD_PAD}" y="{cy}" class="desc">{esc(dl)}</text>')
        cy += 18
    cy += 8

    # Metrics
    for metric in project.get("metrics", []):
        parts.append(
            f'<text x="{CARD_PAD}" y="{cy}" class="metric">▸ {esc(metric)}</text>'
        )
        cy += 18
    cy += 8

    # Stack
    stack_str = " · ".join(project["stack"])
    stack_lines = wrap_text(stack_str, MAX_CHARS)
    for sl in stack_lines:
        parts.append(f'<text x="{CARD_PAD}" y="{cy}" class="stack">{esc(sl)}</text>')
        cy += 16
    cy += 12

    # GitHub button pinned at bottom
    btn_y = cy
    parts.append(
        f'<a href="{project["github"]}">'
        f'<rect x="{CARD_PAD}" y="{btn_y}" width="100" height="28" rx="6" '
        f'fill="#21262d" stroke="#30363d"/>'
        f'<text x="{CARD_PAD + 14}" y="{btn_y + 18}" class="btn">GitHub ↗</text>'
        f'</a>'
    )
    cy = btn_y + 28 + CARD_PAD

    card_h = cy
    svg = (
        f'<g transform="translate({x},{y})" opacity="0">'
        f'<animate attributeName="opacity" begin="{begin:.2f}s" dur="0.2s" '
        f'from="0" to="1" fill="freeze"/>'
        f'<rect width="{CARD_W}" height="{card_h}" rx="10" fill="#0d1117" stroke="#21262d"/>'
        + "".join(parts)
        + "</g>"
    )
    return svg, card_h


def build_svg(projects: list[dict]) -> str:
    GAP_X = 32
    GAP_Y = 20
    START_X = 32
    START_Y = 76

    # Build cards in a 2-column grid, dynamically computing row heights
    cards_svg: list[str] = []
    row_y = START_Y
    t = 0.2

    for i in range(0, len(projects), 2):
        left_proj = projects[i]
        left_svg, left_h = card(left_proj, START_X, row_y, t)
        cards_svg.append(left_svg)
        t += 0.2

        row_h = left_h
        if i + 1 < len(projects):
            right_proj = projects[i + 1]
            right_x = START_X + CARD_W + GAP_X
            right_svg, right_h = card(right_proj, right_x, row_y, t)
            cards_svg.append(right_svg)
            row_h = max(left_h, right_h)
            t += 0.2

        row_y += row_h + GAP_Y

    height = row_y + 20
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Featured projects">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="40" y="62" class="prompt">$ ls featured-projects/</text>
  <style>
    .prompt {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .title  {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; fill: #3fb950; font-weight: 700; }}
    .desc   {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #e6edf3; }}
    .metric {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #8b949e; }}
    .stack  {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; fill: #3fb950; opacity: 0.7; }}
    .btn    {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; fill: #e6edf3; font-weight: 700; }}
  </style>
  {''.join(cards_svg)}
</svg>'''


def main() -> None:
    profile = load_profile()
    OUTPUT_PATH.write_text(build_svg(profile["projects"]), encoding="utf-8")


if __name__ == "__main__":
    main()

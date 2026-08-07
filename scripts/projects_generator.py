#!/usr/bin/env python3
"""Generate dynamic, auto-sizing project cards SVG with polished inner padding and spacing."""

from __future__ import annotations

import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "projects.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]
CARD_WIDTH = 836  # Full width card inside 864px inner container
PAD_LEFT = 32     # Increased inner padding
TEXT_WIDTH = CARD_WIDTH - 2 * PAD_LEFT  # 772px text area


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def traffic_dots(cx_start: int, cy: int) -> str:
    return "".join(
        f'<circle cx="{cx_start + i * 20}" cy="{cy}" r="6" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )


def render_card(project: dict, x: int, y: int, begin: float) -> tuple[str, int]:
    """Render a single full-width card with dynamic height calculation."""
    elements: list[str] = []
    cy = 34  # Relative y inside card

    # Title
    elements.append(
        f'<text x="{PAD_LEFT}" y="{cy}" class="title">{esc(project["title"])}</text>'
    )
    cy += 16

    # Separator
    elements.append(
        f'<line x1="{PAD_LEFT}" y1="{cy}" x2="{CARD_WIDTH - PAD_LEFT}" y2="{cy}" '
        f'stroke="#21262d" stroke-width="1"/>'
    )
    cy += 24

    # Description (wrapped at ~90 chars for 772px width)
    desc_lines = textwrap.wrap(project["description"], width=90)
    for dl in desc_lines:
        elements.append(
            f'<text x="{PAD_LEFT}" y="{cy}" class="desc">{esc(dl)}</text>'
        )
        cy += 22
    cy += 12

    # Key Metrics
    metrics = project.get("metrics", [])
    if metrics:
        elements.append(
            f'<text x="{PAD_LEFT}" y="{cy}" class="section-hdr">Key Metrics:</text>'
        )
        cy += 22
        for m in metrics:
            elements.append(
                f'<text x="{PAD_LEFT + 14}" y="{cy}" class="metric">▸ {esc(m)}</text>'
            )
            cy += 20
        cy += 12

    # Tech Stack
    stack_str = " · ".join(project["stack"])
    stack_lines = textwrap.wrap(f"Tech Stack: {stack_str}", width=95)
    for sl in stack_lines:
        elements.append(
            f'<text x="{PAD_LEFT}" y="{cy}" class="stack">{esc(sl)}</text>'
        )
        cy += 20
    cy += 18

    # GitHub Button pinned at bottom
    btn_y = cy
    elements.append(
        f'<a href="{project["github"]}">'
        f'<rect x="{PAD_LEFT}" y="{btn_y}" width="115" height="32" rx="6" '
        f'fill="#21262d" stroke="#30363d"/>'
        f'<text x="{PAD_LEFT + 20}" y="{btn_y + 21}" class="btn">GitHub ↗</text>'
        f'</a>'
    )
    cy = btn_y + 32 + 28  # Card bottom padding

    card_height = cy

    card_svg = (
        f'<g transform="translate({x},{y})" opacity="0">'
        f'<animate attributeName="opacity" begin="{begin:.2f}s" dur="0.2s" '
        f'from="0" to="1" fill="freeze"/>'
        f'<rect width="{CARD_WIDTH}" height="{card_height}" rx="10" '
        f'fill="#0d1117" stroke="#21262d"/>'
        + "".join(elements)
        + "</g>"
    )
    return card_svg, card_height


def build_svg(projects: list[dict]) -> str:
    CARD_X = 32
    START_Y = 76
    GAP_Y = 28

    cards_markup: list[str] = []
    current_y = START_Y
    t = 0.2

    for project in projects:
        c_svg, c_h = render_card(project, CARD_X, current_y, t)
        cards_markup.append(c_svg)
        current_y += c_h + GAP_Y
        t += 0.25

    height = current_y + 16
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Featured projects">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="40" y="62" class="prompt">$ ls featured-projects/</text>
  <style>
    .prompt      {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .title       {{ font-family: 'JetBrains Mono', monospace; font-size: 20px; fill: #3fb950; font-weight: 700; }}
    .desc        {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #e6edf3; }}
    .section-hdr {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #8b949e; font-weight: 700; }}
    .metric      {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #8b949e; }}
    .stack       {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #3fb950; opacity: 0.85; }}
    .btn         {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #e6edf3; font-weight: 700; }}
  </style>
  {''.join(cards_markup)}
</svg>'''


def main() -> None:
    profile = load_profile()
    OUTPUT_PATH.write_text(build_svg(profile["projects"]), encoding="utf-8")


if __name__ == "__main__":
    main()

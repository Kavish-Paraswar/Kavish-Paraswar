#!/usr/bin/env python3
"""Generate premium tech stack SVG with Base64 icons, text labels, and GitHub green glow."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "tech-stack.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]

_ICON_CACHE: dict[str, str] = {}


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def to_data_uri(url: str) -> str:
    if url in _ICON_CACHE:
        return _ICON_CACHE[url]
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        encoded = base64.b64encode(resp.content).decode("ascii")
        data_uri = f"data:image/svg+xml;base64,{encoded}"
    except requests.RequestException:
        data_uri = ""
    _ICON_CACHE[url] = data_uri
    return data_uri


def traffic_dots(cx_start: int, cy: int) -> str:
    return "".join(
        f'<circle cx="{cx_start + i * 20}" cy="{cy}" r="6" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )


def build_svg(profile: dict) -> str:
    tech_stack = profile["tech_stack"]
    PAD = 40
    ICON_SIZE = 28
    ICON_GAP = 36

    elements: list[str] = []
    y = 80
    t = 0.15

    # Filter for GitHub icon green glow
    glow_filter = '''<defs>
    <filter id="greenGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur"/>
      <feColorMatrix in="blur" type="matrix"
        values="0 0 0 0 0.247  0 0 0 0 0.725  0 0 0 0 0.314  0 0 0 0.6 0" result="glow"/>
      <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>'''

    for cat_name, cat_data in tech_stack.items():
        items = cat_data["items"]
        icons = cat_data.get("icons", [])

        # Category Header
        elements.append(
            f'<text x="{PAD}" y="{y}" class="cat" opacity="0">{esc(cat_name)}'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" '
            f'from="0" to="1" fill="freeze"/></text>'
        )
        t += 0.08
        y += 8

        # Icons row
        ix = PAD
        for icon_url in icons:
            data_uri = to_data_uri(icon_url)
            if data_uri:
                is_github = "github" in icon_url.lower() and "gitlab" not in icon_url.lower()
                filt = ' filter="url(#greenGlow)"' if is_github else ""
                elements.append(
                    f'<image href="{data_uri}" x="{ix}" y="{y}" '
                    f'width="{ICON_SIZE}" height="{ICON_SIZE}"{filt} opacity="0">'
                    f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" '
                    f'from="0" to="1" fill="freeze"/></image>'
                )
                ix += ICON_GAP
        t += 0.06
        y += ICON_SIZE + 10

        # Tech item names below icons
        label_str = "  ·  ".join(items)
        elements.append(
            f'<text x="{PAD}" y="{y}" class="label" opacity="0">{esc(label_str)}'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" '
            f'from="0" to="1" fill="freeze"/></text>'
        )

        t += 0.08
        y += 34

    height = y + 20
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Tech stack">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  {glow_filter}
  <text x="{PAD}" y="62" class="prompt">$ cat tech-stack.yml</text>
  <style>
    .prompt {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .cat    {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #3fb950; font-weight: 700; }}
    .label  {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #e6edf3; }}
  </style>
  {''.join(elements)}
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

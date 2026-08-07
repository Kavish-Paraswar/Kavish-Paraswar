#!/usr/bin/env python3
"""Generate achievements, coding profiles, and currently cards with interactive terminal styling."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
ACHIEVEMENTS_PATH = ROOT / "assets" / "achievements.svg"
CODING_PATH = ROOT / "assets" / "coding.svg"
CURRENTLY_PATH = ROOT / "assets" / "currently.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]
_ICON_CACHE: dict[str, str] = {}


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def to_data_uri(url: str, color_override: str | None = None) -> str:
    if url in _ICON_CACHE:
        return _ICON_CACHE[url]
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        content = resp.text
        if color_override and "fill=" in content:
            content = content.replace('fill="currentColor"', f'fill="{color_override}"')
            content = content.replace('fill="#000000"', f'fill="{color_override}"')
            content = content.replace('fill="#000"', f'fill="{color_override}"')
        elif color_override and "<path" in content and "fill=" not in content:
            content = content.replace('<path', f'<path fill="{color_override}"')
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
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


def build_achievements(profile: dict) -> str:
    """Card-style achievements section from resume."""
    achievements = profile.get("achievements", [])
    PAD = 40
    y = 82
    t = 0.15

    elements: list[str] = []
    for ach in achievements:
        icon = ach["icon"]
        text = esc(ach["text"])

        # Wrap long lines
        if len(text) > 75:
            wrap_at = text.rfind(" ", 0, 75)
            if wrap_at == -1:
                wrap_at = 75
            line1 = text[:wrap_at]
            line2 = text[wrap_at:].lstrip()

            elements.append(
                f'<g opacity="0"><animate attributeName="opacity" begin="{t:.2f}s" '
                f'dur="0.12s" from="0" to="1" fill="freeze"/>'
                f'<rect x="{PAD - 4}" y="{y - 16}" width="830" height="48" rx="8" '
                f'fill="#0d1117" stroke="#21262d"/>'
                f'<text x="{PAD + 8}" y="{y + 2}" class="ach">{icon}  {line1}</text>'
                f'<text x="{PAD + 30}" y="{y + 22}" class="ach">{line2}</text>'
                f'</g>'
            )
            y += 60
        else:
            elements.append(
                f'<g opacity="0"><animate attributeName="opacity" begin="{t:.2f}s" '
                f'dur="0.12s" from="0" to="1" fill="freeze"/>'
                f'<rect x="{PAD - 4}" y="{y - 16}" width="830" height="36" rx="8" '
                f'fill="#0d1117" stroke="#21262d"/>'
                f'<text x="{PAD + 8}" y="{y + 5}" class="ach">{icon}  {text}</text>'
                f'</g>'
            )
            y += 48
        t += 0.1

    height = y + 20
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Achievements">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="{PAD}" y="62" class="prompt">$ cat achievements.log</text>
  <style>
    .prompt {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .ach    {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #e6edf3; }}
  </style>
  {''.join(elements)}
</svg>'''


def build_coding(coding: dict) -> str:
    """Interactive horizontal cards for coding profiles with Base64 logos and hover effects."""
    entries = list(coding.items())
    PAD = 40
    CARD_W = 250
    CARD_H = 135
    GAP = 27
    ICON_SIZE = 44

    cards: list[str] = []
    t = 0.15

    for idx, (name, details) in enumerate(entries):
        cx = PAD + idx * (CARD_W + GAP)
        cy = 76

        url = details.get("url", "#")
        icon_url = details.get("icon", "")
        extra_text = details.get("extra", "")

        # Determine icon color fill if simple-icons
        color_override = "#e6edf3" if "simple-icons" in icon_url else None
        data_uri = to_data_uri(icon_url, color_override=color_override)

        icon_x = cx + (CARD_W - ICON_SIZE) // 2
        center_x = cx + CARD_W // 2

        icon_markup = (
            f'<image href="{data_uri}" x="{icon_x}" y="{cy + 14}" '
            f'width="{ICON_SIZE}" height="{ICON_SIZE}"/>'
            if data_uri
            else ""
        )

        cards.append(
            f'<a href="{esc(url)}" target="_blank" class="card-link">'
            f'<g class="card-group" opacity="0">'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'<rect x="{cx}" y="{cy}" width="{CARD_W}" height="{CARD_H}" rx="10" '
            f'class="card-bg"/>'
            f'{icon_markup}'
            f'<text x="{center_x}" y="{cy + 82}" class="platform" text-anchor="middle">{esc(name)}</text>'
            f'<text x="{center_x}" y="{cy + 106}" class="extra" text-anchor="middle">{esc(extra_text)}</text>'
            f'<text x="{cx + CARD_W - 20}" y="{cy + 24}" class="arrow" text-anchor="middle">↗</text>'
            f'</g>'
            f'</a>'
        )
        t += 0.15

    height = 76 + CARD_H + 28
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Coding profiles">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="{PAD}" y="62" class="prompt">$ cat coding-profiles.log</text>
  <style>
    .prompt    {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .card-bg   {{ fill: #0d1117; stroke: #21262d; stroke-width: 1.5; transition: all 0.2s ease; }}
    .platform  {{ font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #3fb950; font-weight: 700; }}
    .extra     {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #8b949e; }}
    .arrow     {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; transition: fill 0.2s ease; }}
    .card-group:hover .card-bg {{ stroke: #3fb950; fill: #161b22; }}
    .card-group:hover .arrow   {{ fill: #3fb950; }}
  </style>
  {''.join(cards)}
</svg>'''


def build_currently(currently: dict) -> str:
    """Compact terminal key-value card."""
    PAD = 40
    y = 82
    t = 0.15

    elements: list[str] = []
    for key, val in currently.items():
        elements.append(
            f'<g opacity="0"><animate attributeName="opacity" begin="{t:.2f}s" '
            f'dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'<text x="{PAD}" y="{y}" class="key">{esc(key)}</text>'
            f'<text x="{PAD + 160}" y="{y}" class="val">{esc(val)}</text>'
            f'</g>'
        )
        y += 36
        t += 0.12

    height = y + 20
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Currently">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="{PAD}" y="62" class="prompt">$ cat currently.yml</text>
  <style>
    .prompt {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .key    {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #3fb950; font-weight: 700; }}
    .val    {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #e6edf3; }}
  </style>
  {''.join(elements)}
</svg>'''


def main() -> None:
    profile = load_profile()
    ACHIEVEMENTS_PATH.write_text(build_achievements(profile), encoding="utf-8")
    CODING_PATH.write_text(build_coding(profile["coding"]), encoding="utf-8")
    CURRENTLY_PATH.write_text(build_currently(profile["currently"]), encoding="utf-8")


if __name__ == "__main__":
    main()

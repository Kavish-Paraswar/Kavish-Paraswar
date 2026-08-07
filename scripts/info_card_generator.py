#!/usr/bin/env python3
"""Generate achievements, coding profiles, and currently cards."""

from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
ACHIEVEMENTS_PATH = ROOT / "assets" / "achievements.svg"
CODING_PATH = ROOT / "assets" / "coding.svg"
CURRENTLY_PATH = ROOT / "assets" / "currently.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
    """Coding profiles as horizontal cards."""
    entries = list(coding.items())
    PAD = 40
    CARD_W = 260
    CARD_H = 110
    GAP = 24

    cards: list[str] = []
    t = 0.15
    for idx, (name, details) in enumerate(entries):
        cx = PAD + idx * (CARD_W + GAP)
        cy = 76

        tier_color = "#3fb950" if "Knight" in details["tier"] or "Specialist" in details["tier"] else "#e6edf3"

        cards.append(
            f'<g opacity="0"><animate attributeName="opacity" begin="{t:.2f}s" '
            f'dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'<rect x="{cx}" y="{cy}" width="{CARD_W}" height="{CARD_H}" rx="10" '
            f'fill="#0d1117" stroke="#21262d"/>'
            f'<text x="{cx + 20}" y="{cy + 30}" class="platform">{esc(name)}</text>'
            f'<text x="{cx + 20}" y="{cy + 55}" class="tier" fill="{tier_color}">{esc(details["tier"])}</text>'
            f'<text x="{cx + 20}" y="{cy + 76}" class="rating">Max Rating: {details["max_rating"]}</text>'
            f'<text x="{cx + 20}" y="{cy + 94}" class="extra">{esc(details.get("extra", ""))}</text>'
            f'</g>'
        )
        t += 0.15

    total_w = len(entries) * CARD_W + (len(entries) - 1) * GAP + 2 * PAD
    width = max(900, total_w)
    height = 76 + CARD_H + 30
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Coding profiles">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <text x="{PAD}" y="62" class="prompt">$ cat coding-profiles.log</text>
  <style>
    .prompt   {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .platform {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #3fb950; font-weight: 700; }}
    .tier     {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; }}
    .rating   {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #8b949e; }}
    .extra    {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #7d8590; }}
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

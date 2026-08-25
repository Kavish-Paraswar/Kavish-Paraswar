#!/usr/bin/env python3
"""Generate the compact terminal hero banner SVG with embedded Pollito GIF and contact line, without action buttons."""

from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
POLLITO_PATH = ROOT / "assets" / "misc" / "pollito.gif"
OUTPUT_PATH = ROOT / "assets" / "banner.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]
EMAIL_URL = "mailto:kavishp9721@gmail.com"


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def get_pollito_b64() -> str:
    if not POLLITO_PATH.exists():
        return ""
    encoded = base64.b64encode(POLLITO_PATH.read_bytes()).decode("ascii")
    return f"data:image/gif;base64,{encoded}"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anim_line(text: str, x: int, y: int, begin: float, cls: str) -> str:
    safe = esc(text)
    return (
        f'<text x="{x}" y="{y}" class="{cls}" opacity="0">{safe}'
        f'<animate attributeName="opacity" begin="{begin:.2f}s" dur="0.15s" '
        f'from="0" to="1" fill="freeze"/></text>'
    )


def traffic_dots(cx_start: int, cy: int) -> str:
    dots = []
    for i, color in enumerate(DOT_COLORS):
        cx = cx_start + i * 20
        dots.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{color}"/>')
    return "".join(dots)


def cycle_line(items: list[str], x: int, y: int, begin: float, cls: str) -> str:
    visible = 2.8
    transition = 0.45
    slot = visible + transition
    total = slot * len(items)
    parts = ['<g>']
    for i, item in enumerate(items):
        start = i * slot
        fade_in_end = start + transition
        fade_out_start = start + visible
        fade_out_end = start + slot
        parts.append(
            f'<text x="{x}" y="{y}" class="{cls}" opacity="0">{esc(item)}'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="0;{start/total:.6f};{fade_out_start/total:.6f};{fade_out_end/total:.6f}" '
            f'begin="{begin:.2f}s" dur="{total:.2f}s" repeatCount="indefinite"/>'
            f'</text>'
        )
    parts.append('</g>')
    return ''.join(parts)


def build_svg(profile: dict) -> str:
    PAD = 40
    elements: list[str] = []
    y = 80

    elements.append(anim_line("kavish@github:~$", PAD, y, 0.20, "prompt"))
    y += 32

    elements.append(anim_line("./init-profile", PAD, y, 0.40, "cmd"))
    y += 38

    elements.append(anim_line("Loading modules...", PAD, y, 0.65, "muted"))
    y += 26
    elements.append(anim_line("██████████████", PAD, y, 0.90, "bar"))
    y += 38

    name_baseline = y
    elements.append(anim_line("Hey, I'm Kavish Paraswar.", PAD, name_baseline, 1.10, "name"))

    pollito_b64 = get_pollito_b64()
    if pollito_b64:
        gif_x = PAD + 435
        gif_y = name_baseline - 48
        gif_h = 75
        elements.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" begin="1.10s" dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'<image href="{pollito_b64}" x="{gif_x}" y="{gif_y}" height="{gif_h}" preserveAspectRatio="xMidYMid meet" style="border-radius: 6px;"/>'
            f'</g>'
        )

    y += 48

    elements.append(anim_line("I enjoy building", PAD, y, 1.35, "subtitle"))
    y += 32

    cycle_items = ["Backend Systems", "AI-powered Products", "Production Software", "Open Source"]
    elements.append(cycle_line(cycle_items, PAD + 8, y, 1.55, "interest"))
    y += 38

    contact_email = profile.get("contact", "kavishp9721@gmail.com")
    elements.append(anim_line("$ contact --email", PAD, y, 1.95, "contact-cmd"))
    y += 24
    elements.append(
        f'<a href="{EMAIL_URL}" target="_blank">'
        f'<text x="{PAD}" y="{y}" class="contact-email" opacity="0">'
        f'{esc(contact_email)}'
        f'<animate attributeName="opacity" begin="2.05s" dur="0.15s" from="0" to="1" fill="freeze"/>'
        f'</text>'
        f'</a>'
    )
    y += 36

    elements.append(anim_line("Ready_", PAD, y, 2.20, "ready"))

    cursor_x = PAD + 78
    cursor_y = y - 16
    elements.append(
        f'<rect x="{cursor_x}" y="{cursor_y}" width="10" height="20" fill="#3fb950" opacity="0">'
        f'<animate attributeName="opacity" begin="2.20s" dur="0.01s" from="0" to="1" fill="freeze"/>'
        f'<animate attributeName="opacity" begin="2.25s" dur="1s" values="1;0;1" repeatCount="indefinite"/>'
        f'</rect>'
    )

    height = y + 36
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Animated profile boot banner">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <style>
    .prompt        {{ font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #7d8590; }}
    .cmd           {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #e6edf3; }}
    .muted         {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #484f58; }}
    .bar           {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #3fb950; }}
    .name          {{ font-family: 'JetBrains Mono', monospace; font-size: 28px; fill: #e6edf3; font-weight: 700; }}
    .subtitle      {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #8b949e; }}
    .interest      {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #e6edf3; }}
    .contact-cmd   {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #7d8590; }}
    .contact-email {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #3fb950; font-weight: 600; text-decoration: none; }}
    .contact-email:hover {{ text-decoration: underline; }}
    .ready         {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #3fb950; font-weight: 700; }}
  </style>
  {''.join(elements)}
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

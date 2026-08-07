#!/usr/bin/env python3
"""Generate the premium terminal hero banner SVG with embedded Pollito GIF beside name."""

from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
POLLITO_PATH = ROOT / "assets" / "misc" / "pollito.gif"
OUTPUT_PATH = ROOT / "assets" / "banner.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]


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


def build_svg(profile: dict) -> str:
    PAD = 40
    elements: list[str] = []
    y = 80

    # Command prompt
    elements.append(anim_line("kavish@github:~$", PAD, y, 0.20, "prompt"))
    y += 36

    # Executable command
    elements.append(anim_line("./init-profile", PAD, y, 0.45, "cmd"))
    y += 44

    # Loading status
    elements.append(anim_line("Loading modules...", PAD, y, 0.75, "muted"))
    y += 32
    elements.append(anim_line("██████████████", PAD, y, 1.05, "bar"))
    y += 52

    # Greeting & Name
    elements.append(anim_line("Hey,", PAD, y, 1.40, "greeting"))
    y += 40

    # "I'm Kavish Paraswar." + Pollito GIF beside it
    name_baseline = y
    elements.append(anim_line("I'm Kavish Paraswar.", PAD, name_baseline, 1.60, "name"))

    pollito_b64 = get_pollito_b64()
    if pollito_b64:
        # 30px font baseline is at name_baseline. Text height ~30px (baseline - 25px to baseline + 5px).
        # Center of text = name_baseline - 10. For a 75px high GIF, y_pos = name_baseline - 10 - 37.5 = name_baseline - 48.
        gif_x = PAD + 375  # ~20px horizontal spacing after "I'm Kavish Paraswar."
        gif_y = name_baseline - 48
        gif_h = 75
        elements.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" begin="1.60s" dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'<image href="{pollito_b64}" x="{gif_x}" y="{gif_y}" height="{gif_h}" preserveAspectRatio="xMidYMid meet" style="border-radius: 6px;"/>'
            f'</g>'
        )

    y += 52

    # Subtitle
    elements.append(anim_line("I enjoy building", PAD, y, 1.85, "subtitle"))
    y += 36

    # Bullets
    bullets = [
        "Backend Systems",
        "AI-powered Products",
        "Production Software",
        "Open Source",
    ]
    for i, b in enumerate(bullets):
        elements.append(anim_line(f"• {b}", PAD + 8, y, 2.05 + i * 0.15, "interest"))
        y += 32

    y += 18
    elements.append(
        anim_line(
            "Currently focused on creating scalable software that solves real engineering problems.",
            PAD,
            y,
            2.75,
            "focus",
        )
    )
    y += 48

    # Ready line + blinking cursor
    elements.append(anim_line("Ready_", PAD, y, 3.05, "ready"))

    cursor_x = PAD + 78
    cursor_y = y - 16
    elements.append(
        f'<rect x="{cursor_x}" y="{cursor_y}" width="10" height="20" fill="#3fb950" opacity="0">'
        f'<animate attributeName="opacity" begin="3.05s" dur="0.01s" from="0" to="1" fill="freeze"/>'
        f'<animate attributeName="opacity" begin="3.10s" dur="1s" values="1;0;1" repeatCount="indefinite"/>'
        f'</rect>'
    )

    height = y + 40
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Animated profile boot banner">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <style>
    .prompt   {{ font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #7d8590; }}
    .cmd      {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #e6edf3; }}
    .muted    {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #484f58; }}
    .bar      {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #3fb950; }}
    .greeting {{ font-family: 'JetBrains Mono', monospace; font-size: 20px; fill: #8b949e; }}
    .name     {{ font-family: 'JetBrains Mono', monospace; font-size: 30px; fill: #e6edf3; font-weight: 700; }}
    .subtitle {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #8b949e; }}
    .interest {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #e6edf3; }}
    .focus    {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .ready    {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #3fb950; font-weight: 700; }}
  </style>
  {''.join(elements)}
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

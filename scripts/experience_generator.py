#!/usr/bin/env python3
"""Generate premium timeline-style experience card SVG from resume data."""

from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "experience.svg"

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


def build_svg(profile: dict) -> str:
    experiences = profile["experience"]
    PAD_L = 40
    TIMELINE_X = 56
    CONTENT_X = 80

    elements: list[str] = []
    y = 80

    # Command header
    elements.append(
        f'<text x="{PAD_L}" y="{y}" class="prompt">$ cat experience.log</text>'
    )
    y += 44

    t = 0.25
    for idx, exp in enumerate(experiences):
        block_start = y

        # Timeline dot
        elements.append(
            f'<circle cx="{TIMELINE_X}" cy="{y}" r="5" fill="#3fb950" opacity="0">'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'</circle>'
        )

        # Company name
        elements.append(
            f'<text x="{CONTENT_X}" y="{y + 5}" class="company" opacity="0">{esc(exp["company"])}'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'</text>'
        )
        t += 0.12
        y += 28

        # Role + Duration
        elements.append(
            f'<text x="{CONTENT_X}" y="{y}" class="role" opacity="0">{esc(exp["role"])}'
            f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/>'
            f'</text>'
        )
        duration = exp.get("duration", "")
        if duration:
            elements.append(
                f'<text x="860" y="{y}" class="duration" text-anchor="end" opacity="0">{esc(duration)}'
                f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/>'
                f'</text>'
            )
        t += 0.10
        y += 28

        # Highlights
        for bullet in exp.get("highlights", []):
            safe = esc(bullet)
            # Word-wrap long bullets at ~85 chars
            if len(safe) > 85:
                wrap_at = safe.rfind(" ", 0, 85)
                if wrap_at == -1:
                    wrap_at = 85
                line1 = safe[:wrap_at]
                line2 = safe[wrap_at:].lstrip()
                elements.append(
                    f'<text x="{CONTENT_X}" y="{y}" class="bullet" opacity="0">▸ {line1}'
                    f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" from="0" to="1" fill="freeze"/>'
                    f'</text>'
                )
                y += 24
                elements.append(
                    f'<text x="{CONTENT_X + 16}" y="{y}" class="bullet" opacity="0">{line2}'
                    f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" from="0" to="1" fill="freeze"/>'
                    f'</text>'
                )
            else:
                elements.append(
                    f'<text x="{CONTENT_X}" y="{y}" class="bullet" opacity="0">▸ {safe}'
                    f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" from="0" to="1" fill="freeze"/>'
                    f'</text>'
                )
            t += 0.08
            y += 24

        # Technologies
        techs = exp.get("technologies", [])
        if techs:
            y += 4
            tech_str = " · ".join(techs)
            elements.append(
                f'<text x="{CONTENT_X}" y="{y}" class="tech" opacity="0">{esc(tech_str)}'
                f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.12s" from="0" to="1" fill="freeze"/>'
                f'</text>'
            )
            t += 0.10
            y += 12

        # Timeline line segment (connect to next)
        if idx < len(experiences) - 1:
            line_top = block_start + 8
            line_bot = y + 20
            elements.append(
                f'<line x1="{TIMELINE_X}" y1="{line_top}" x2="{TIMELINE_X}" y2="{line_bot}" '
                f'stroke="#21262d" stroke-width="2" opacity="0">'
                f'<animate attributeName="opacity" begin="{t:.2f}s" dur="0.15s" from="0" to="1" fill="freeze"/>'
                f'</line>'
            )
            y += 32
        else:
            y += 12

    height = y + 30
    inner_h = height - 36

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" role="img" aria-label="Experience timeline">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="{inner_h}" rx="12" fill="#010409" stroke="#21262d"/>
  {traffic_dots(42, 40)}
  <style>
    .prompt   {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }}
    .company  {{ font-family: 'JetBrains Mono', monospace; font-size: 22px; fill: #3fb950; font-weight: 700; }}
    .role     {{ font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #e6edf3; }}
    .duration {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #7d8590; }}
    .bullet   {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #8b949e; }}
    .tech     {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #3fb950; opacity: 0.7; }}
  </style>
  {''.join(elements)}
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

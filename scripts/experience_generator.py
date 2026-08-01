#!/usr/bin/env python3
"""Generate animated terminal experience card SVG."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "experience.svg"


def load_profile() -> dict:
    """Load profile metadata."""
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def build_svg(profile: dict) -> str:
    """Create one-shot animated experience layout."""
    sections = []
    y = 80
    step = 0
    for company in profile["experience"]:
        header_begin = 0.25 + step * 0.22
        sections.append(
            f"""
  <g opacity=\"0\">
    <animate attributeName=\"opacity\" begin=\"{header_begin}s\" dur=\"0.25s\" from=\"0\" to=\"1\" fill=\"freeze\" />
    <text x=\"34\" y=\"{y}\" class=\"company\">{company['company']}</text>
    <text x=\"280\" y=\"{y}\" class=\"role\">{company['role']}</text>
  </g>"""
        )
        y += 34
        step += 1
        for bullet in company["highlights"]:
            bullet_begin = 0.25 + step * 0.22
            sections.append(
                f"""
  <g opacity=\"0\" transform=\"translate(0,10)\">
    <animate attributeName=\"opacity\" begin=\"{bullet_begin}s\" dur=\"0.22s\" from=\"0\" to=\"1\" fill=\"freeze\" />
    <animateTransform attributeName=\"transform\" type=\"translate\" begin=\"{bullet_begin}s\" dur=\"0.22s\" from=\"0 10\" to=\"0 0\" fill=\"freeze\" />
    <text x=\"52\" y=\"{y}\" class=\"bullet\">• {bullet}</text>
  </g>"""
            )
            y += 30
            step += 1
        y += 24
    body = "\n".join(sections)
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"430\" viewBox=\"0 0 900 430\" role=\"img\" aria-label=\"Experience card\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\" />
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"406\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\" />
  <text x=\"24\" y=\"36\" font-family=\"monospace\" font-size=\"14\" fill=\"#8b949e\">kavish@github:~$ cat experience.log</text>
  <style>
    .company {{ font-family: 'JetBrains Mono', monospace; font-size: 24px; font-weight: 700; fill: #3fb950; }}
    .role {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; fill: #c9d1d9; }}
    .bullet {{ font-family: 'JetBrains Mono', monospace; font-size: 17px; fill: #8b949e; }}
  </style>
{body}
</svg>"""


def main() -> None:
    """Generate and save experience SVG."""
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

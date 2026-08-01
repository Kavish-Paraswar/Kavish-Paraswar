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


def reveal(text: str, y: int, begin: float, cls: str) -> str:
    """Create one-shot text reveal."""
    return (
        f"<text x=\"34\" y=\"{y}\" class=\"{cls}\" opacity=\"0\">{text}"
        f"<animate attributeName=\"opacity\" begin=\"{begin:.2f}s\" dur=\"0.2s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>"
    )


def build_svg(profile: dict) -> str:
    """Create one-shot animated experience layout."""
    lines = [reveal("$ cat experience.log", 38, 0.0, "cmd")]
    y = 82
    t = 0.25

    for company in profile["experience"]:
        lines.append(reveal(company["company"], y, t, "company"))
        y += 26
        t += 0.18
        lines.append(reveal("──────────────", y, t, "rule"))
        y += 30
        t += 0.16
        lines.append(reveal(company["role"], y, t, "role"))
        y += 34
        t += 0.18

        for bullet in company["highlights"]:
            lines.append(reveal(f"✓ {bullet}", y, t, "bullet"))
            y += 30
            t += 0.16
        y += 20

    height = max(430, y + 24)
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"{height}\" viewBox=\"0 0 900 {height}\" role=\"img\" aria-label=\"Experience card\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\" />
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"{height - 24}\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\" />
  <style>
    .cmd {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #8b949e; }}
    .company {{ font-family: 'JetBrains Mono', monospace; font-size: 27px; font-weight: 700; fill: #3fb950; }}
    .rule {{ font-family: 'JetBrains Mono', monospace; font-size: 20px; fill: #8b949e; }}
    .role {{ font-family: 'JetBrains Mono', monospace; font-size: 20px; fill: #e6edf3; }}
    .bullet {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; fill: #c9d1d9; }}
  </style>
  {''.join(lines)}
</svg>"""


def main() -> None:
    """Generate and save experience SVG."""
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

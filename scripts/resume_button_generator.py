#!/usr/bin/env python3
"""Generate terminal-styled action button SVG for Resume download."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "resume-button.svg"


def build_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="220" height="44" viewBox="0 0 220 44" role="img" aria-label="Download Resume terminal button">
  <rect width="100%" height="100%" fill="#0d1117" rx="8" stroke="#30363d" stroke-width="1.5"/>
  <rect x="2" y="2" width="216" height="40" rx="6" fill="#010409"/>
  <style>
    .prompt { font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #3fb950; font-weight: 700; }
    .label  { font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #e6edf3; font-weight: 700; }
    .arrow  { font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #3fb950; }
  </style>
  <text x="16" y="26" class="prompt">$</text>
  <text x="30" y="26" class="label">./resume.sh</text>
  <text x="184" y="26" class="arrow">↓</text>
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a simple terminal-style closing banner for the README footer."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "footer.svg"


def build_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="120" viewBox="0 0 900 120" role="img" aria-label="Terminal footer">
  <rect width="100%" height="100%" fill="#0d1117" rx="14"/>
  <rect x="12" y="12" width="876" height="96" rx="10" fill="#010409" stroke="#30363d"/>
  <circle cx="34" cy="34" r="5" fill="#f85149"/>
  <circle cx="52" cy="34" r="5" fill="#d29922"/>
  <circle cx="70" cy="34" r="5" fill="#3fb950"/>
  <style>
    .cmd { font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #8b949e; }
    .out { font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #3fb950; }
    .cursor { fill: #3fb950; }
  </style>
  <text x="24" y="70" class="cmd">kavish@github:~$ exit</text>
  <g opacity="0">
    <animate attributeName="opacity" begin="0.4s" dur="0.2s" from="0" to="1" fill="freeze"/>
    <text x="24" y="96" class="out">Thanks for stopping by. See you in the next commit.</text>
  </g>
  <rect x="360" y="84" width="9" height="16" class="cursor">
    <animate attributeName="opacity" values="1;0;1" dur="1s" begin="0.4s" repeatCount="indefinite"/>
  </rect>
</svg>"""


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()

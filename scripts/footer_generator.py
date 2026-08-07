#!/usr/bin/env python3
"""Generate minimal terminal footer SVG."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "footer.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]


def build_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="130" viewBox="0 0 900 130" role="img" aria-label="Terminal footer">
  <rect width="100%" height="100%" fill="#0d1117" rx="16"/>
  <rect x="18" y="18" width="864" height="94" rx="12" fill="#010409" stroke="#21262d"/>
  <circle cx="42" cy="40" r="6" fill="#f85149"/>
  <circle cx="62" cy="40" r="6" fill="#d29922"/>
  <circle cx="82" cy="40" r="6" fill="#3fb950"/>
  <style>
    .cmd  { font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #7d8590; }
    .out  { font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #484f58; }
    .ok   { font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #3fb950; }
  </style>
  <text x="40" y="68" class="cmd">kavish@github:~$ exit</text>
  <g opacity="0">
    <animate attributeName="opacity" begin="0.3s" dur="0.15s" from="0" to="1" fill="freeze"/>
    <text x="40" y="92" class="out">Connection closed.</text>
    <text x="240" y="92" class="ok">See you next time.</text>
  </g>
  <rect x="410" y="80" width="8" height="15" fill="#3fb950" opacity="0">
    <animate attributeName="opacity" begin="0.5s" dur="0.01s" from="0" to="1" fill="freeze"/>
    <animate attributeName="opacity" begin="0.55s" dur="1s" values="1;0;1" repeatCount="indefinite"/>
  </rect>
</svg>'''


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()

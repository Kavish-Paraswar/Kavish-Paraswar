#!/usr/bin/env python3
"""Generate a realistic high-resolution monochrome ASCII portrait SVG."""

from __future__ import annotations

from html import escape
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "profile-processed.png"
OUTPUT_PATH = ROOT / "assets" / "ascii.svg"
ASCII_RAMP = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "


def load_image() -> np.ndarray:
    """Load preprocessed portrait image."""
    image = cv2.imread(str(INPUT_PATH), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Missing preprocessed portrait: {INPUT_PATH}")
    return image


def to_ascii(image: np.ndarray, width: int = 120, height: int = 70) -> list[str]:
    """Convert grayscale portrait into dense ASCII rows."""
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    bucket = 255 / (len(ASCII_RAMP) - 1)
    rows = []
    for row in resized:
        chars = [ASCII_RAMP[min(int(value / bucket), len(ASCII_RAMP) - 1)] for value in row]
        rows.append(escape("".join(chars)).replace(" ", "&#160;"))
    return rows


def build_svg(rows: list[str]) -> str:
    """Render one-shot boot sequence followed by typed ASCII portrait."""
    line_height = 11.2
    top = 236
    delay = 0.028
    start = 3.45

    portrait_lines = []
    for idx, row in enumerate(rows):
        begin = start + idx * delay
        y = top + idx * line_height
        portrait_lines.append(
            f"""  <text x=\"30\" y=\"{y:.1f}\" class=\"ascii\" opacity=\"0\">{row}
    <animate attributeName=\"opacity\" begin=\"{begin:.3f}s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\" />
  </text>"""
        )

    cursor_y_values = ";".join(f"{(top - 9) + i * line_height:.1f}" for i in range(len(rows)))
    key_times = ";".join(f"{i / max(1, len(rows) - 1):.4f}" for i in range(len(rows)))
    typing_time = len(rows) * delay
    hide_cursor_at = start + typing_time + 0.06

    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"1040\" viewBox=\"0 0 900 1040\" role=\"img\" aria-label=\"ASCII portrait terminal output\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\" />
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"1016\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\" />
  <style>
    .boot {{ font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #8b949e; }}
    .done {{ font-family: 'JetBrains Mono', monospace; font-size: 15px; fill: #3fb950; }}
    .ascii {{ font-family: 'JetBrains Mono', monospace; font-size: 9.4px; fill: #e6edf3; letter-spacing: 0.08px; }}
  </style>

  <text x=\"30\" y=\"44\" class=\"boot\" opacity=\"0\">$ ./load-profile<animate attributeName=\"opacity\" begin=\"0s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>
  <text x=\"30\" y=\"76\" class=\"boot\" opacity=\"0\">Loading profile...<animate attributeName=\"opacity\" begin=\"0.30s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>
  <text x=\"30\" y=\"100\" class=\"done\" opacity=\"0\">████████████████████<animate attributeName=\"opacity\" begin=\"0.66s\" dur=\"0.15s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>

  <text x=\"30\" y=\"132\" class=\"boot\" opacity=\"0\">Removing background...<animate attributeName=\"opacity\" begin=\"1.05s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>
  <text x=\"30\" y=\"156\" class=\"done\" opacity=\"0\">████████████████████<animate attributeName=\"opacity\" begin=\"1.42s\" dur=\"0.15s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>

  <text x=\"30\" y=\"188\" class=\"boot\" opacity=\"0\">Generating ASCII...<animate attributeName=\"opacity\" begin=\"1.80s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>
  <text x=\"30\" y=\"212\" class=\"done\" opacity=\"0\">████████████████████<animate attributeName=\"opacity\" begin=\"2.18s\" dur=\"0.15s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>
  <text x=\"30\" y=\"236\" class=\"done\" opacity=\"0\">Done.<animate attributeName=\"opacity\" begin=\"2.52s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>

{''.join(portrait_lines)}

  <rect x=\"30\" y=\"{top - 9:.1f}\" width=\"6\" height=\"9\" fill=\"#3fb950\" opacity=\"1\">
    <animate attributeName=\"y\" begin=\"{start:.3f}s\" dur=\"{typing_time:.3f}s\" values=\"{cursor_y_values}\" keyTimes=\"{key_times}\" fill=\"freeze\" />
    <animate attributeName=\"opacity\" begin=\"{start:.3f}s\" dur=\"0.24s\" values=\"1;0;1\" repeatCount=\"indefinite\" />
    <set attributeName=\"opacity\" to=\"0\" begin=\"{hide_cursor_at:.3f}s\" />
  </rect>
</svg>"""


def main() -> None:
    """Generate and save ASCII SVG output."""
    OUTPUT_PATH.write_text(build_svg(to_ascii(load_image())), encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate animated ASCII portrait SVG from processed photo."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "profile-processed.png"
OUTPUT_PATH = ROOT / "assets" / "ascii.svg"
ASCII_CHARS = "@%#*+=-:. "


def load_image() -> np.ndarray:
    """Load grayscale image, fallback to synthetic image if missing."""
    if INPUT_PATH.exists():
        image = cv2.imread(str(INPUT_PATH), cv2.IMREAD_GRAYSCALE)
        if image is not None:
            return image
    fallback = np.zeros((180, 140), dtype=np.uint8)
    cv2.putText(fallback, "KP", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 2.5, 220, 5, cv2.LINE_AA)
    return fallback


def to_ascii(image: np.ndarray, width: int = 68) -> list[str]:
    """Convert grayscale image into fixed-width ASCII lines."""
    ratio = image.shape[0] / image.shape[1]
    height = max(20, int(width * ratio * 0.55))
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    bucket = 255 / (len(ASCII_CHARS) - 1)
    lines = []
    for row in resized:
        chars = [ASCII_CHARS[min(int(value / bucket), len(ASCII_CHARS) - 1)] for value in row]
        lines.append("".join(chars).replace(" ", "&#160;"))
    return lines


def build_svg(lines: list[str]) -> str:
    """Build one-shot row-by-row ASCII typing animation."""
    line_height = 14
    top = 56
    content = []
    for idx, line in enumerate(lines):
        begin = 0.28 + idx * 0.08
        y = top + idx * line_height
        content.append(
            f"""  <text x=\"24\" y=\"{y}\" class=\"ascii\" opacity=\"0\">{line}
    <animate attributeName=\"opacity\" begin=\"{begin}s\" dur=\"0.02s\" from=\"0\" to=\"1\" fill=\"freeze\" />
  </text>"""
        )

    max_y = top + (len(lines) - 1) * line_height
    cursor_values = ";".join(str(top - 12 + i * line_height) for i in range(len(lines)))
    key_times = ";".join(f"{i/(max(len(lines)-1,1)):.4f}" for i in range(len(lines)))

    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"470\" viewBox=\"0 0 900 470\" role=\"img\" aria-label=\"ASCII portrait\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\"/>
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"446\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\"/>
  <text x=\"24\" y=\"36\" font-family=\"monospace\" font-size=\"14\" fill=\"#8b949e\">kavish@github:~$ ./render-ascii</text>
  <style>
    .ascii {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #c9d1d9; }}
  </style>
{''.join(content)}
  <rect x=\"24\" y=\"{top - 12}\" width=\"8\" height=\"12\" fill=\"#3fb950\">
    <animate attributeName=\"y\" begin=\"0.28s\" dur=\"{max(0.3, len(lines) * 0.08):.2f}s\" values=\"{cursor_values}\" keyTimes=\"{key_times}\" fill=\"freeze\" />
    <animate attributeName=\"opacity\" begin=\"0.28s\" dur=\"0.24s\" values=\"1;0;1\" repeatCount=\"16\" />
    <set attributeName=\"opacity\" to=\"0\" begin=\"{0.32 + len(lines) * 0.08:.2f}s\" />
  </rect>
</svg>"""


def main() -> None:
    """Render and save ASCII SVG portrait."""
    OUTPUT_PATH.write_text(build_svg(to_ascii(load_image())), encoding="utf-8")


if __name__ == "__main__":
    main()

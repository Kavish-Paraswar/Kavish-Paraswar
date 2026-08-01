#!/usr/bin/env python3
"""Generate the animated terminal banner SVG."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "banner.svg"


def load_profile() -> dict:
    """Load profile metadata."""
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def typed_line(text: str, y: int, index: int) -> str:
    """Create one typed line with a one-shot reveal animation."""
    start = 0.35 + index * 1.35
    clip_id = f"lineClip{index}"
    return f"""
  <defs>
    <clipPath id=\"{clip_id}\">
      <rect x=\"40\" y=\"{y - 34}\" width=\"0\" height=\"48\">
        <animate attributeName=\"width\" begin=\"{start}s\" dur=\"1.1s\" from=\"0\" to=\"860\" fill=\"freeze\" />
      </rect>
    </clipPath>
  </defs>
  <text x=\"40\" y=\"{y}\" class=\"typed\" clip-path=\"url(#{clip_id})\">{text}</text>"""


def build_svg(profile: dict) -> str:
    """Render full banner SVG."""
    lines = [profile["name"].upper(), profile["title"], profile["tagline"]]
    typed = "\n".join(typed_line(text, 86 + i * 62, i) for i, text in enumerate(lines))
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"280\" viewBox=\"0 0 900 280\" role=\"img\" aria-label=\"Animated profile banner\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"18\" />
  <rect x=\"18\" y=\"18\" width=\"864\" height=\"244\" rx=\"12\" fill=\"#010409\" stroke=\"#30363d\" />
  <circle cx=\"44\" cy=\"36\" r=\"6\" fill=\"#f85149\"/><circle cx=\"66\" cy=\"36\" r=\"6\" fill=\"#d29922\"/><circle cx=\"88\" cy=\"36\" r=\"6\" fill=\"#3fb950\"/>
  <text x=\"120\" y=\"40\" font-size=\"14\" fill=\"#8b949e\" font-family=\"monospace\">kavish@github:~$ ./init-profile</text>
  <style>
    .typed {{ font-family: 'Fira Code', 'JetBrains Mono', monospace; font-size: 42px; fill: #3fb950; font-weight: 600; }}
  </style>
{typed}
  <rect x=\"40\" y=\"176\" width=\"16\" height=\"34\" fill=\"#3fb950\">
    <animate attributeName=\"x\" begin=\"0.35s\" dur=\"4.2s\" values=\"40;780;780;650\" keyTimes=\"0;0.36;0.7;1\" fill=\"freeze\" />
    <animate attributeName=\"y\" begin=\"0.35s\" dur=\"4.2s\" values=\"52;52;114;176\" keyTimes=\"0;0.36;0.7;1\" fill=\"freeze\" />
    <animate attributeName=\"opacity\" begin=\"0.35s\" dur=\"0.35s\" values=\"1;0;1\" repeatCount=\"12\" />
    <set attributeName=\"opacity\" to=\"0\" begin=\"4.55s\" />
  </rect>
</svg>"""


def main() -> None:
    """Build and save the banner SVG."""
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

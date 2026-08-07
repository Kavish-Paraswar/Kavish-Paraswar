#!/usr/bin/env python3
"""Generate the premium one-shot terminal boot banner SVG."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "banner.svg"

DOT_COLORS = ["#f85149", "#d29922", "#3fb950"]


def load_profile() -> dict:
    """Load profile metadata."""
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def line(text: str, y: int, begin: float, cls: str = "boot") -> str:
    """Build an animated boot line."""
    return (
        f"<text x=\"40\" y=\"{y}\" class=\"{cls}\" opacity=\"0\">{text}"
        f"<animate attributeName=\"opacity\" begin=\"{begin:.2f}s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\"/></text>"
    )


def traffic_dots(y: int, begin: float) -> str:
    """Render the three red/yellow/green terminal window dots as real circles."""
    dots = []
    for i, color in enumerate(DOT_COLORS):
        cx = 46 + i * 18
        dots.append(
            f"<circle cx=\"{cx}\" cy=\"{y}\" r=\"6\" fill=\"{color}\" opacity=\"0\">"
            f"<animate attributeName=\"opacity\" begin=\"{begin:.2f}s\" dur=\"0.01s\" from=\"0\" to=\"1\" fill=\"freeze\"/></circle>"
        )
    return "".join(dots)


def build_svg(profile: dict) -> str:
    """Render full banner SVG."""
    focus = " • ".join(profile.get("focus_areas", []))
    skills = " • ".join(profile.get("top_skills", []))

    lines = [
        line("kavish@github:~$", 80, 0.28),
        line("./init-profile", 112, 0.55, "cmd"),
        line("Loading modules...", 148, 0.9),
        line("████████████████████", 176, 1.25, "ok"),
        line(f"I AM {profile['name'].upper()}", 224, 1.7, "headline"),
        line(f"I work on {focus}", 258, 2.0, "role"),
        line(skills, 292, 2.3, "tag"),
        line("Ready.", 330, 2.6, "ok"),
    ]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="390" viewBox="0 0 900 390" role="img" aria-label="Animated profile boot banner">
  <rect width="100%" height="100%" fill="#0d1117" rx="18" />
  <rect x="18" y="18" width="864" height="354" rx="12" fill="#010409" stroke="#30363d" />
  <style>
    .boot {{ font-family: 'JetBrains Mono', monospace; font-size: 22px; fill: #8b949e; }}
    .cmd {{ font-family: 'JetBrains Mono', monospace; font-size: 24px; fill: #c9d1d9; }}
    .headline {{ font-family: 'JetBrains Mono', monospace; font-size: 32px; fill: #e6edf3; font-weight: 700; }}
    .role {{ font-family: 'JetBrains Mono', monospace; font-size: 23px; fill: #8b949e; }}
    .tag {{ font-family: 'JetBrains Mono', monospace; font-size: 22px; fill: #3fb950; }}
    .ok {{ font-family: 'JetBrains Mono', monospace; font-size: 22px; fill: #3fb950; }}
  </style>
  {traffic_dots(44, 0.0)}
  {''.join(lines)}

  <rect x="40" y="96" width="12" height="20" fill="#3fb950" opacity="1">
    <animate attributeName="x" begin="0.55s" dur="2.5s" values="40;228;40;280;120;520;120" fill="freeze" />
    <animate attributeName="y" begin="0.55s" dur="2.5s" values="96;96;132;132;206;206;350" fill="freeze" />
    <animate attributeName="opacity" begin="0.55s" dur="0.24s" values="1;0;1" repeatCount="indefinite" />
    <set attributeName="opacity" to="0" begin="3.15s" />
  </rect>
</svg>"""


def main() -> None:
    """Build and save the banner SVG."""
    OUTPUT_PATH.write_text(build_svg(load_profile()), encoding="utf-8")


if __name__ == "__main__":
    main()

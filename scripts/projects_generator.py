#!/usr/bin/env python3
"""Generate terminal-styled project cards SVG from profile data."""

from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
OUTPUT_PATH = ROOT / "assets" / "projects.svg"


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def button(x: int, y: int, text: str, href: str, width: int = 122) -> str:
    return (
        f"<a href='{href}'><rect x='{x}' y='{y}' width='{width}' height='30' rx='6' fill='#3fb950'/>"
        f"<text x='{x + 16}' y='{y + 20}' class='btn'>{text}</text></a>"
    )


def card(project: dict, x: int, y: int, begin: float) -> str:
    metrics = " | ".join(project.get("metrics", []))
    stack = " · ".join(project["stack"])
    demo = project.get("demo", "").strip()
    actions = [button(20, 118, "GitHub ↗", project["github"]) ]
    if demo:
        actions.append(button(152, 118, "Live Demo ↗", demo, 140))

    return f"""
  <g transform=\"translate({x},{y})\" opacity=\"0\">
    <animate attributeName=\"opacity\" begin=\"{begin:.2f}s\" dur=\"0.22s\" from=\"0\" to=\"1\" fill=\"freeze\"/>
    <rect width=\"408\" height=\"170\" rx=\"10\" fill=\"#0d1117\" stroke=\"#30363d\"/>
    <text x=\"20\" y=\"34\" class=\"title\">{project['title']}</text>
    <text x=\"20\" y=\"58\" class=\"desc\">{project['description']}</text>
    <text x=\"20\" y=\"82\" class=\"metric\">Key Metrics: {metrics}</text>
    <text x=\"20\" y=\"104\" class=\"stack\">Tech Stack: {stack}</text>
    {''.join(actions)}
  </g>"""


def build_svg(projects: list[dict]) -> str:
    layout = [
        (32, 58, 0.20),
        (460, 58, 0.42),
        (32, 248, 0.64),
        (460, 248, 0.86),
    ]
    groups = [card(project, *layout[idx]) for idx, project in enumerate(projects[:4])]
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"440\" viewBox=\"0 0 900 440\" role=\"img\" aria-label=\"Featured projects\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\"/>
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"416\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\"/>
  <text x=\"24\" y=\"36\" class=\"cmd\">$ ls featured-projects</text>
  <style>
    .cmd {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #8b949e; }}
    .title {{ font-family: 'JetBrains Mono', monospace; font-size: 21px; fill: #3fb950; font-weight: 700; }}
    .desc {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #e6edf3; }}
    .metric {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #c9d1d9; }}
    .stack {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #8b949e; }}
    .btn {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; fill: #0d1117; font-weight: 700; }}
  </style>
  {''.join(groups)}
</svg>"""


def main() -> None:
    profile = load_profile()
    OUTPUT_PATH.write_text(build_svg(profile["projects"]), encoding="utf-8")


if __name__ == "__main__":
    main()

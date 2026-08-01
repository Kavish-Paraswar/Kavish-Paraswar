#!/usr/bin/env python3
"""Generate animated tech stack SVG while preserving all existing icons."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "assets" / "tech-stack.svg"

CATEGORIES = [
    (
        "Cloud",
        ["https://cdn.jsdelivr.net/gh/devicons/devicon/icons/googlecloud/googlecloud-original.svg"],
    ),
    (
        "Frontend",
        [
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-plain.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-plain.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redux/redux-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vite/vite-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bootstrap/bootstrap-original.svg",
        ],
    ),
    (
        "Backend",
        ["https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg"],
    ),
    (
        "Languages",
        [
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg",
        ],
    ),
    (
        "Database",
        [
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/firebase/firebase-plain.svg",
        ],
    ),
    (
        "AI/ML",
        ["https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"],
    ),
    (
        "Tools",
        [
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg",
            "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg",
        ],
    ),
]


def render_category(name: str, icons: list[str], y: int, begin: float) -> str:
    parts = [
        f"<g opacity='0'><animate attributeName='opacity' begin='{begin:.2f}s' dur='0.2s' from='0' to='1' fill='freeze'/>",
        f"<text x='36' y='{y}' class='cat'>{name}</text>",
        f"<text x='36' y='{y + 22}' class='arrow'>↓</text>",
    ]
    x = 84
    for icon in icons:
        parts.append(f"<image href='{icon}' x='{x}' y='{y + 2}' width='34' height='34'/>")
        x += 42
    parts.append("</g>")
    return "".join(parts)


def build_svg() -> str:
    y = 72
    begin = 0.2
    blocks = []
    for name, icons in CATEGORIES:
        blocks.append(render_category(name, icons, y, begin))
        y += 48
        begin += 0.26

    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"430\" viewBox=\"0 0 900 430\" role=\"img\" aria-label=\"Tech stack categories\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\"/>
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"406\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\"/>
  <text x=\"24\" y=\"36\" class=\"cmd\">$ ./tech-stack</text>
  <style>
    .cmd {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; fill: #8b949e; }}
    .cat {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; fill: #3fb950; font-weight: 700; }}
    .arrow {{ font-family: 'JetBrains Mono', monospace; font-size: 18px; fill: #8b949e; }}
  </style>
  {''.join(blocks)}
</svg>"""


def main() -> None:
    OUTPUT_PATH.write_text(build_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()

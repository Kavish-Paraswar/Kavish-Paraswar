#!/usr/bin/env python3
"""Generate animated tech stack SVG with icons embedded as base64 data URIs.

GitHub renders README images (including this SVG) via a plain <img> tag.
Browsers treat an SVG loaded through <img> as a sandboxed image: it is not
allowed to fetch further external resources, so any <image href="https://...">
pointing at an outside URL (jsdelivr, etc.) renders as a broken icon even
though the SVG itself loads fine. The fix is to inline every icon as a
base64 data URI at generation time so the SVG is fully self-contained.
"""

from __future__ import annotations

import base64
from pathlib import Path

import requests

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

_ICON_CACHE: dict[str, str] = {}


def to_data_uri(url: str) -> str:
    """Download an icon once and return it as an inline base64 data URI."""
    if url in _ICON_CACHE:
        return _ICON_CACHE[url]
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        encoded = base64.b64encode(resp.content).decode("ascii")
        data_uri = f"data:image/svg+xml;base64,{encoded}"
    except requests.RequestException:
        data_uri = ""
    _ICON_CACHE[url] = data_uri
    return data_uri


def render_category(name: str, icons: list[str], y: int, begin: float) -> str:
    parts = [
        f"<g opacity='0'><animate attributeName='opacity' begin='{begin:.2f}s' dur='0.2s' from='0' to='1' fill='freeze'/>",
        f"<text x='36' y='{y}' class='cat'>{name}</text>",
        f"<text x='36' y='{y + 22}' class='arrow'>\u2193</text>",
    ]
    x = 84
    for icon in icons:
        data_uri = to_data_uri(icon)
        if data_uri:
            parts.append(f"<image href='{data_uri}' x='{x}' y='{y + 2}' width='34' height='34'/>")
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

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="430" viewBox="0 0 900 430" role="img" aria-label="Tech stack categories">
  <rect width="100%" height="100%" fill="#0d1117" rx="14"/>
  <rect x="12" y="12" width="876" height="406" rx="10" fill="#010409" stroke="#30363d"/>
  <text x="24" y="36" class="cmd">$ ./tech-stack</text>
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

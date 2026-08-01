#!/usr/bin/env python3
"""Generate animated terminal info, coding, and currently SVG cards."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profile.json"
INFO_PATH = ROOT / "assets" / "info-card.svg"
CODING_PATH = ROOT / "assets" / "coding.svg"
CURRENTLY_PATH = ROOT / "assets" / "currently.svg"


def load_profile() -> dict:
    """Load profile content."""
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def row(label: str, value: str, y: int, idx: int) -> str:
    """Create one animated row."""
    begin = 0.28 + idx * 0.22
    return f"""
  <g opacity=\"0\" transform=\"translate(0,12)\">
    <animate attributeName=\"opacity\" begin=\"{begin}s\" dur=\"0.24s\" from=\"0\" to=\"1\" fill=\"freeze\" />
    <animateTransform attributeName=\"transform\" type=\"translate\" begin=\"{begin}s\" dur=\"0.24s\" from=\"0 12\" to=\"0 0\" fill=\"freeze\" />
    <text x=\"28\" y=\"{y}\" class=\"label\">{label}</text>
    <text x=\"186\" y=\"{y}\" class=\"value\">{value}</text>
  </g>"""


def build_info(profile: dict) -> str:
    """Build the whoami info card SVG."""
    rows = [
        ("Name", profile["name"]),
        ("Education", profile["education"][0]),
        ("", profile["education"][1]),
        ("Location", profile["location"]),
        ("Languages", " | ".join(profile["languages"])),
        ("Frontend", " | ".join(profile["frontend"])),
        ("Backend", " | ".join(profile["backend"])),
        ("Database", " | ".join(profile["database"])),
        ("AI", " | ".join(profile["ai"])),
        ("Cloud", " | ".join(profile["cloud"])),
        ("Contact", profile["contact"]),
    ]
    body = "\n".join(row(label, value, 78 + i * 32, i) for i, (label, value) in enumerate(rows))
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"470\" viewBox=\"0 0 900 470\" role=\"img\" aria-label=\"Neofetch style info card\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\" />
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"446\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\" />
  <text x=\"24\" y=\"36\" font-family=\"monospace\" font-size=\"14\" fill=\"#8b949e\">kavish@github:~$ neofetch</text>
  <style>
    .label {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #3fb950; font-weight: 700; }}
    .value {{ font-family: 'JetBrains Mono', monospace; font-size: 16px; fill: #c9d1d9; }}
  </style>
{body}
</svg>"""


def build_terminal_kv(title: str, command: str, entries: dict[str, str], height: int) -> str:
    """Build a compact terminal key-value card."""
    body = "\n".join(row(k, v, 84 + i * 42, i) for i, (k, v) in enumerate(entries.items()))
    return f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"{height}\" viewBox=\"0 0 900 {height}\" role=\"img\" aria-label=\"{title}\">
  <rect width=\"100%\" height=\"100%\" fill=\"#0d1117\" rx=\"14\" />
  <rect x=\"12\" y=\"12\" width=\"876\" height=\"{height - 24}\" rx=\"10\" fill=\"#010409\" stroke=\"#30363d\" />
  <text x=\"24\" y=\"36\" font-family=\"monospace\" font-size=\"14\" fill=\"#8b949e\">kavish@github:~$ {command}</text>
  <style>
    .label {{ font-family: 'JetBrains Mono', monospace; font-size: 22px; fill: #3fb950; font-weight: 700; }}
    .value {{ font-family: 'JetBrains Mono', monospace; font-size: 22px; fill: #c9d1d9; }}
  </style>
{body}
</svg>"""


def main() -> None:
    """Generate all data-driven terminal cards."""
    profile = load_profile()
    INFO_PATH.write_text(build_info(profile), encoding="utf-8")
    CODING_PATH.write_text(
        build_terminal_kv("Coding profiles", "cat coding.json", profile["coding"], 250),
        encoding="utf-8",
    )
    CURRENTLY_PATH.write_text(
        build_terminal_kv("Currently", "cat currently.log", profile["currently"], 290),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

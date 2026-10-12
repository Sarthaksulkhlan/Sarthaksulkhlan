"""Central visual system and evidence-based portfolio content."""
from __future__ import annotations

import re

USERNAME = "Sarthaksulkhlan"
NAME = "Sarthak Sulkhlan"
PROFILE_URL = f"https://github.com/{USERNAME}"
PALETTE = {
    "bg": "#111714", "bg_deep": "#0C110E", "panel": "#18211C",
    "panel_alt": "#202B24", "text": "#E7ECE8", "muted": "#AAB8AF",
    "silver": "#CFD8D2", "mint": "#B8E8CF", "emerald": "#71D3A7",
    "emerald_deep": "#28694E", "border": "#34473D", "grid": "#26362D",
    "light_bg": "#F3F7F3", "light_panel": "#FFFFFF", "light_panel_alt": "#E8F0EA",
    "light_text": "#1B2922", "light_muted": "#52655A", "light_silver": "#50645A",
    "light_mint": "#2F8A66", "light_emerald": "#176C4D", "light_border": "#CED9D1",
    "light_grid": "#DEE7E0", "track_dark": "#2A382F", "track_light": "#E0E9E2",
}
SANS_FONT = "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
MONO_FONT = "SFMono-Regular, Consolas, monospace"
WIDTH = 830
HERO_HEIGHT = 250
DIVIDER_HEIGHT = 34
ACTIVITY_HEIGHT = 220
LANGUAGE_HEIGHT = 250
LANDSCAPE_HEIGHT = 210
GRID_STEP = 28
DARK_MODE_MEDIA = "(prefers-color-scheme: dark)"
LIGHT_MODE_MEDIA = "(prefers-color-scheme: light)"

# Project claims below come from the linked repositories' current README files.
# Runtime homepage links and repository statistics come from GitHub's public API.
PROJECTS = [
    {
        "repo": "epoch-software.evolution", "name": "EPOCH",
        "eyebrow": "SYSTEM EVOLUTION / HACKATHON PROTOTYPE",
        "description": "A governed software-evolution workbench: records code changes, checks system invariants, tracks drift and incidents, and measures alternative futures before a person approves a change. The repository describes a prototype built around one watched sample service.",
        "stack": ["TypeScript", "Hono", "React 19", "SQLite", "MCP"],
        "domain": "change → invariants → review",
    },
    {
        "repo": "Asset-Sentinel", "name": "Asset Sentinel",
        "eyebrow": "ENDPOINT TELEMETRY / FLEET VISIBILITY",
        "description": "A Windows monitoring system that sends heartbeat, hardware, session, and foreground-application signals through a Python agent and Flask API into a Supabase PostgreSQL store and React dashboard. Its README documents an end-to-end deployment and a demo using demonstration data.",
        "stack": ["Python", "Flask", "PostgreSQL", "React", "TypeScript"],
        "domain": "devices → telemetry → operations",
    },
    {
        "repo": "Nexis---Starforge", "name": "MatrixCore",
        "eyebrow": "VOICE SYSTEMS / HACKATHON DEMO",
        "description": "An adaptive voice-agent demo with a browser client, an Express service, and a Python LiveKit agent. The documented voice path connects LiveKit, Gemini, Qdrant retrieval, and Rime speech; local use requires external service credentials.",
        "stack": ["TypeScript", "Express", "Python", "LiveKit", "Gemini"],
        "domain": "voice → reasoning → response",
    },
]

LEARNING = ["Java problem solving", "generative AI systems", "Python"]
CAPABILITIES = [
    {"name": "Application interfaces", "items": ["TypeScript", "React", "Vite"]},
    {"name": "Services and APIs", "items": ["Python", "Flask", "Hono", "Express"]},
    {"name": "Data and persistence", "items": ["SQLite", "PostgreSQL", "Supabase"]},
    {"name": "System integration", "items": ["MCP", "LiveKit", "GitHub Actions"]},
]
EDUCATION = "B.Tech, Computer Science and Engineering (Data Science)"
ACTIVITY_NOTE = (
    "Activity groups only PushEvents returned by GitHub's public user-events endpoint "
    "(up to 100 recent public events). It is a sample, not a contribution history; "
    "an empty bucket does not prove there was no GitHub activity."
)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    """Convert a #RRGGBB value to RGB, rejecting malformed colors."""
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError(f"Expected #RRGGBB color, got {value!r}")
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def card_params(mode: str = "dark") -> dict[str, str]:
    """Return the centralized tokens used by all generated visual instruments."""
    if mode == "dark":
        return {
            "bg": PALETTE["bg"], "bg_deep": PALETTE["bg_deep"],
            "panel": PALETTE["panel"], "panel_alt": PALETTE["panel_alt"],
            "text": PALETTE["text"], "muted": PALETTE["muted"],
            "silver": PALETTE["silver"], "mint": PALETTE["mint"],
            "accent": PALETTE["emerald"], "accent_deep": PALETTE["emerald_deep"],
            "border": PALETTE["border"], "grid": PALETTE["grid"],
            "track": PALETTE["track_dark"],
        }
    if mode == "light":
        return {
            "bg": PALETTE["light_bg"], "bg_deep": PALETTE["light_bg"],
            "panel": PALETTE["light_panel"], "panel_alt": PALETTE["light_panel_alt"],
            "text": PALETTE["light_text"], "muted": PALETTE["light_muted"],
            "silver": PALETTE["light_silver"], "mint": PALETTE["light_mint"],
            "accent": PALETTE["light_emerald"], "accent_deep": PALETTE["light_emerald"],
            "border": PALETTE["light_border"], "grid": PALETTE["light_grid"],
            "track": PALETTE["track_light"],
        }
    raise ValueError("mode must be 'dark' or 'light'")


def contrast_ratio(foreground: str, background: str) -> float:
    """Calculate WCAG relative-luminance contrast ratio."""
    def luminance(color: str) -> float:
        channels = []
        for value in hex_to_rgb(color):
            unit = value / 255
            channels.append(unit / 12.92 if unit <= 0.04045 else ((unit + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    first, second = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def validate_theme() -> None:
    """Fail on malformed tokens or insufficient foreground contrast."""
    for color in PALETTE.values():
        hex_to_rgb(color)
    for mode in ("dark", "light"):
        colors = card_params(mode)
        for token in ("text", "muted", "silver", "accent"):
            if contrast_ratio(colors[token], colors["bg"]) < 4.5:
                raise ValueError(f"{token} does not meet WCAG AA contrast in {mode} mode")
    if not USERNAME or not NAME or WIDTH != 830:
        raise ValueError("Invalid profile identity or supported SVG dimensions")


def picture_markup(asset: str, alt: str) -> str:
    """Use GitHub's theme-aware picture pattern with a static SVG fallback."""
    from html import escape

    if not re.fullmatch(r"[a-z0-9-]+", asset):
        raise ValueError("Asset name must be a lowercase filename stem")
    return (
        "<picture>\n"
        f'  <source media="{DARK_MODE_MEDIA}" srcset="assets/{asset}.svg">\n'
        f'  <source media="{LIGHT_MODE_MEDIA}" srcset="assets/{asset}-light.svg">\n'
        f'  <img src="assets/{asset}.svg" alt="{escape(alt, quote=True)}">\n'
        "</picture>"
    )

"""Central visual system and verified profile copy for generated assets."""
from __future__ import annotations

import re

USERNAME = "Sarthaksulkhlan"
NAME = "Sarthak Sulkhlan"
PROFILE_URL = f"https://github.com/{USERNAME}"
PALETTE = {
    "navy": "#101923", "navy_deep": "#0B121A", "slate": "#283747",
    "blue": "#5A9BD5", "cyan": "#65C7D0", "paper": "#F5F8FA",
    "white": "#FFFFFF", "ink": "#152331", "muted_dark": "#B4C2CE",
    "muted_light": "#526474", "border_dark": "#344553",
    "border_light": "#CFD9E0", "grid_dark": "#283744", "grid_light": "#DEE6EB",
    "cyan_light": "#087E8B", "blue_light": "#246AA5", "steel_blue": "#8095B5",
    "ice_blue": "#7BABC0", "steel": "#718A9A", "mist": "#A1B0BA",
}
SANS_FONT = "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
MONO_FONT = "SFMono-Regular, Consolas, monospace"
WIDTH = 830
HERO_HEIGHT = 245
DIVIDER_HEIGHT = 38
CHART_HEIGHT = 152
GRID_STEP = 30
DARK_MODE_MEDIA = "(prefers-color-scheme: dark)"
LIGHT_MODE_MEDIA = "(prefers-color-scheme: light)"

# Factual project copy is maintained here; live URLs and language metadata are
# read from GitHub. A homepage is linked only when present in the public API.
PROJECTS = [
    {"repo": "epoch-software.evolution", "name": "EPOCH", "description": "A system evolution platform that tracks software changes, invariants, drift, incidents, and measured counterfactual futures.", "maturity": "Implemented system; repository documents a live demo.", "tags": ["TypeScript", "MCP", "Software evolution"]},
    {"repo": "Asset-Sentinel", "name": "Asset Sentinel", "description": "A Windows fleet monitoring platform that turns device sessions, applications, hardware, and heartbeat telemetry into operational visibility.", "maturity": "Repository describes operational monitoring and dashboard features.", "tags": ["Python", "Flask", "React", "Windows"]},
    {"repo": "Nexis---Starforge", "name": "MatrixCore", "description": "An Aura adaptive voice-agent hackathon demo with a browser client and Python LiveKit agent; the repository is titled Nexis / Starforge.", "maturity": "Hackathon demo; local setup requires external service credentials.", "tags": ["TypeScript", "Python", "LiveKit", "Gemini"]},
]
ADDITIONAL_PROJECTS = [
    {"repo": "MediKiosk", "name": "MediKiosk", "description": "The public repository describes a TypeScript project but has no README or detailed project description to verify its purpose.", "maturity": "Early repository; functionality not verified.", "tags": ["TypeScript"]},
]


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    """Convert a #RRGGBB value to an RGB tuple, rejecting malformed colors."""
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError(f"Expected #RRGGBB color, got {value!r}")
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def css_vars() -> str:
    """Return theme tokens as CSS custom properties."""
    return ":root{" + ";".join(f"--{key.replace('_', '-')}:#{value.lstrip('#')}" for key, value in PALETTE.items()) + "}"


def card_params(theme: str = "dark") -> dict[str, str]:
    """Return accessible SVG card colors for dark or light GitHub themes."""
    if theme == "dark":
        return {"bg": PALETTE["navy"], "surface": PALETTE["slate"], "text": PALETTE["white"], "muted": PALETTE["muted_dark"], "border": PALETTE["border_dark"], "grid": PALETTE["grid_dark"], "accent": PALETTE["cyan"], "blue": PALETTE["blue"]}
    if theme == "light":
        return {"bg": PALETTE["paper"], "surface": PALETTE["white"], "text": PALETTE["ink"], "muted": PALETTE["muted_light"], "border": PALETTE["border_light"], "grid": PALETTE["grid_light"], "accent": PALETTE["cyan_light"], "blue": PALETTE["blue_light"]}
    raise ValueError("theme must be 'dark' or 'light'")


def validate_theme() -> None:
    """Fail early if required tokens are missing or malformed."""
    required = {"navy", "navy_deep", "slate", "blue", "cyan", "paper", "white", "ink", "muted_dark", "muted_light", "border_dark", "border_light", "grid_dark", "grid_light", "cyan_light", "blue_light", "steel_blue", "ice_blue", "steel", "mist"}
    missing = required - PALETTE.keys()
    if missing:
        raise ValueError(f"Missing theme colors: {sorted(missing)}")
    for color in PALETTE.values():
        hex_to_rgb(color)
    if not USERNAME or not NAME or WIDTH > 830 or WIDTH < 360:
        raise ValueError("Invalid profile identity or SVG dimensions")
    for mode in ("dark", "light"):
        card = card_params(mode)
        foregrounds = ("text", "muted", "accent", "blue")
        if any(contrast_ratio(card[token], card["bg"]) < 4.5 for token in foregrounds):
            raise ValueError(f"Card text does not meet WCAG AA contrast in {mode} mode")


def contrast_ratio(foreground: str, background: str) -> float:
    """Calculate WCAG relative-luminance contrast ratio for two colors."""
    def luminance(color: str) -> float:
        channels = []
        for value in hex_to_rgb(color):
            unit = value / 255
            channels.append(unit / 12.92 if unit <= 0.04045 else ((unit + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    first, second = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def picture_markup(asset: str, alt: str) -> str:
    """Create GitHub-supported theme selection with a static SVG fallback."""
    from html import escape

    if not re.fullmatch(r"[a-z0-9-]+", asset):
        raise ValueError("Asset name must be a lowercase filename stem")
    safe_alt = escape(alt, quote=True)
    return (
        "<picture>\n"
        f'  <source media="{DARK_MODE_MEDIA}" srcset="assets/{asset}.svg">\n'
        f'  <source media="{LIGHT_MODE_MEDIA}" srcset="assets/{asset}-light.svg">\n'
        f'  <img src="assets/{asset}.svg" alt="{safe_alt}">\n'
        "</picture>"
    )

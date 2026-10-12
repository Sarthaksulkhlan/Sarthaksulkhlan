"""Render static, self-contained SVG assets from theme.py and public data."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from theme import (
    CHART_HEIGHT,
    DIVIDER_HEIGHT,
    GRID_STEP,
    HERO_HEIGHT,
    MONO_FONT,
    NAME,
    PALETTE,
    SANS_FONT,
    WIDTH,
    card_params,
)


def _document(width: int, height: int, title: str, description: str, content: str) -> str:
    """Wrap vector content in valid SVG with a static, accessible fallback."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" '
        f'font-family="{html.escape(SANS_FONT, quote=True)}">'
        f'<title id="title">{html.escape(title)}</title>'
        f'<desc id="desc">{html.escape(description)}</desc>{content}</svg>\n'
    )


def hero(mode: str = "dark") -> str:
    """Render one palette-specific profile banner."""
    c = card_params(mode)
    grid = "".join(
        f'<line x1="{x}" y1="22" x2="{x}" y2="222" stroke="{c["grid"]}" opacity=".55"/>'
        for x in range(480, WIDTH + 1, GRID_STEP)
    )
    grid += "".join(
        f'<line x1="480" y1="{y}" x2="830" y2="{y}" stroke="{c["grid"]}" opacity=".55"/>'
        for y in range(30, 231, GRID_STEP)
    )
    content = f'''<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HERO_HEIGHT-1}" rx="20" fill="{c['bg']}" stroke="{c['border']}"/>
      <g opacity=".65">{grid}</g>
      <circle cx="637" cy="119" r="20" fill="{c['surface']}" opacity=".85"/>
      <path d="M480 182 C555 176 578 99 637 119 S733 201 830 71" fill="none" stroke="{c['blue']}" stroke-width="2" opacity=".85"/>
      <circle cx="637" cy="119" r="6" fill="{c['accent']}"/><circle cx="637" cy="119" r="13" fill="none" stroke="{c['accent']}" opacity=".45"/>
      <text x="42" y="57" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="12" letter-spacing="1.4">SOFTWARE / DATA / AI</text>
      <text x="40" y="116" fill="{c['text']}" font-size="42" font-weight="650">{html.escape(NAME)}</text>
      <text x="42" y="151" fill="{c['muted']}" font-size="17">Building thoughtful software systems</text>
      <text x="42" y="181" fill="{c['muted']}" font-size="14">CSE / Data Science / AI engineering / developer tools</text>
      <text x="42" y="218" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.4">GITHUB.COM/{html.escape(NAME.upper().replace(' ', ''))}</text>'''
    return _document(WIDTH, HERO_HEIGHT, "Sarthak Sulkhlan - software, data, and AI", "A technical portfolio banner with a static systems diagram motif.", content)


def divider(mode: str = "dark") -> str:
    """Render a restrained static section divider."""
    c = card_params(mode)
    content = (
        f'<path d="M0 19H{WIDTH}" stroke="{c["border"]}"/>'
        f'<path d="M0 19H{WIDTH}" stroke="{c["accent"]}" stroke-width="2" stroke-dasharray="2 24"/>'
        f'<circle cx="32" cy="19" r="4" fill="{c["blue"]}"/>'
    )
    return _document(WIDTH, DIVIDER_HEIGHT, "Section divider", "A fine technical line separates profile sections.", content)


def activity(data: dict[str, Any], mode: str = "dark") -> str:
    """Render observed public PushEvents; unavailable input is labelled clearly."""
    c = card_params(mode)
    counts = [0] * 12
    labels = ["11w", "10w", "9w", "8w", "7w", "6w", "5w", "4w", "3w", "2w", "1w", "now"]
    for index, count in enumerate(data.get("activity_weeks", counts)):
        if index < len(counts):
            counts[index] = max(0, int(count))
    maximum = max(counts) or 1
    bars = []
    for i, count in enumerate(counts):
        height = 8 + round(58 * count / maximum) if count else 5
        x = 34 + i * 63
        bars.append(
            f'<rect x="{x}" y="{110-height}" width="26" height="{height}" rx="4" '
            f'fill="{c["blue"] if count else c["border"]}"/>'
            f'<text x="{x+13}" y="128" text-anchor="middle" fill="{c["muted"]}" font-size="9">{labels[i]}</text>'
        )
    summary = f'{sum(counts)} public push events in sampled window' if data.get("events_available", False) else "Public push event data unavailable"
    content = (
        f'<rect width="{WIDTH}" height="{CHART_HEIGHT}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="29" fill="{c["text"]}" font-size="15" font-weight="600">Public repository activity</text>'
        f'<text x="24" y="48" fill="{c["muted"]}" font-size="11">Weekly buckets / public event snapshot / recent 12 weeks</text>'
        f'{"".join(bars)}<text x="{WIDTH-20}" y="143" text-anchor="end" fill="{c["muted"]}" font-size="10">{html.escape(summary)}</text>'
    )
    return _document(WIDTH, CHART_HEIGHT, "Public repository activity", "A twelve week bar chart of observed public push events. Missing data is labelled unavailable.", content)


def languages(data: dict[str, Any], mode: str = "dark") -> str:
    """Render GitHub-reported language byte totals across owned public projects."""
    c = card_params(mode)
    stats = data.get("languages", {})
    ranked_all = sorted(((str(name), int(size)) for name, size in stats.items() if int(size) > 0), key=lambda pair: (-pair[1], pair[0]))
    total = sum(value for _, value in ranked_all)
    ranked = ranked_all[:6] if len(ranked_all) <= 6 else ranked_all[:5] + [("Other", sum(value for _, value in ranked_all[5:]))]
    palette = [PALETTE["blue"], PALETTE["cyan"], PALETTE["steel_blue"], PALETTE["ice_blue"], PALETTE["steel"], PALETTE["mist"]]
    if not ranked:
        graph = f'<text x="24" y="83" fill="{c["muted"]}" font-size="13">Repository language data is not available yet.</text>'
    else:
        x_position = 24
        bar_parts = []
        for index, (name, size) in enumerate(ranked):
            segment = max(1, round(782 * size / total))
            bar_parts.append(f'<rect x="{x_position}" y="57" width="{segment}" height="12" rx="5" fill="{palette[index]}"/>')
            x_position += segment
        legend = []
        for index, (name, size) in enumerate(ranked):
            x = 26 + (index % 3) * 260
            y = 99 + (index // 3) * 25
            legend.append(
                f'<circle cx="{x}" cy="{y-4}" r="4" fill="{palette[index]}"/>'
                f'<text x="{x+12}" y="{y}" fill="{c["text"]}" font-size="12">{html.escape(name)} '
                f'<tspan fill="{c["muted"]}">{size/total:.0%}</tspan></text>'
            )
        graph = "".join(bar_parts + legend)
    content = (
        f'<rect width="{WIDTH}" height="{CHART_HEIGHT}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="29" fill="{c["text"]}" font-size="15" font-weight="600">Languages across public repositories</text>'
        f'<text x="24" y="45" fill="{c["muted"]}" font-size="10">GitHub byte totals snapshot / all languages / profile repository excluded</text>{graph}'
    )
    return _document(WIDTH, CHART_HEIGHT, "Public repository language breakdown", "Language shares weighted by GitHub-reported source bytes across public project repositories.", content)


def write_assets(directory: Path, data: dict[str, Any]) -> None:
    """Write static dark/light SVG pairs; GitHub selects them in README picture tags."""
    directory.mkdir(parents=True, exist_ok=True)
    renderers = {"hero": hero, "divider": divider, "activity": activity, "language-stats": languages}
    for name, renderer in renderers.items():
        for mode, suffix in (("dark", ""), ("light", "-light")):
            content = renderer(mode=mode) if name in {"hero", "divider"} else renderer(data, mode=mode)
            (directory / f"{name}{suffix}.svg").write_text(content, encoding="utf-8", newline="\n")

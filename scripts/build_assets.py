"""Render compact, self-hosted SVG instruments from theme tokens and cached data."""
from __future__ import annotations

import html
import struct
from pathlib import Path
from typing import Any

from theme import (
    ACTIVITY_HEIGHT, DIVIDER_HEIGHT, HERO_HEIGHT, LANGUAGE_HEIGHT, LANDSCAPE_HEIGHT,
    MONO_FONT, NAME, PALETTE, PROJECTS, SANS_FONT, WIDTH, card_params,
)


def _document(width: int, height: int, title: str, description: str, content: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" '
        f'font-family="{html.escape(SANS_FONT, quote=True)}">'
        f'<title id="title">{html.escape(title)}</title>'
        f'<desc id="desc">{html.escape(description)}</desc>{content}</svg>\n'
    )


def hero(mode: str = "dark") -> str:
    """A restrained systems-console banner with a bespoke signal path."""
    c = card_params(mode)
    grid = "".join(
        f'<path d="M{x} 18V232" stroke="{c["grid"]}"/>'
        for x in range(28, WIDTH, 28)
    ) + "".join(
        f'<path d="M18 {y}H812" stroke="{c["grid"]}"/>'
        for y in range(26, HERO_HEIGHT, 28)
    )
    nodes = []
    for index, (x, label, sublabel) in enumerate((
        (548, "CODE", "changes"), (665, "SIGNALS", "invariants"), (782, "REVIEW", "decisions")
    )):
        fill = c["panel_alt"] if index != 1 else c["panel"]
        nodes.append(
            f'<rect x="{x-42}" y="93" width="84" height="66" rx="12" fill="{fill}" stroke="{c["border"]}"/>'
            f'<circle cx="{x}" cy="111" r="4" fill="{c["accent"]}"/>'
            f'<text x="{x}" y="132" text-anchor="middle" fill="{c["text"]}" font-family="{MONO_FONT}" font-size="9" letter-spacing=".8">{label}</text>'
            f'<text x="{x}" y="147" text-anchor="middle" fill="{c["muted"]}" font-size="9">{sublabel}</text>'
        )
    content = f'''<defs>
      <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c['panel']}"/><stop offset="1" stop-color="{c['bg_deep']}"/></linearGradient>
      <linearGradient id="signal" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{c['accent_deep']}"/><stop offset=".52" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['mint']}"/></linearGradient>
    </defs>
    <rect x=".5" y=".5" width="829" height="249" rx="19" fill="url(#surface)" stroke="{c['border']}"/>
    <g opacity=".48">{grid}</g>
    <path d="M20 196H810" stroke="{c['border']}"/>
    <text x="38" y="44" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="11" letter-spacing="2">ENGINEERING / SOFTWARE / DATA</text>
    <text x="36" y="101" fill="{c['text']}" font-size="39" font-weight="650">{html.escape(NAME)}</text>
    <text x="39" y="133" fill="{c['silver']}" font-size="16">Software engineering · data science · AI systems</text>
    <text x="39" y="163" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="11">BUILD → MEASURE → UNDERSTAND → REFINE</text>
    <path d="M590 127H623 M707 127H740" fill="none" stroke="url(#signal)" stroke-width="2"/>
    <path d="M510 70H586L596 60L606 80L616 70H810" fill="none" stroke="{c['mint']}" stroke-width="1.5" opacity=".78"/>
    {''.join(nodes)}
    <text x="39" y="222" fill="{c['muted']}" font-size="11">Practical tools, deliberate systems, evidence-led iteration</text>
    <text x="790" y="222" text-anchor="end" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1">{html.escape(NAME.upper().replace(' ', ''))}</text>'''
    return _document(WIDTH, HERO_HEIGHT, f"{NAME} — engineering portfolio", "A technical portfolio banner with a signal path from code changes through system evidence to human review.", content)


def divider(mode: str = "dark") -> str:
    c = card_params(mode)
    content = (
        f'<path d="M0 17H{WIDTH}" stroke="{c["border"]}"/>'
        f'<path d="M0 17H{WIDTH}" stroke="{c["accent"]}" stroke-width="1.5" stroke-dasharray="2 22" opacity=".72"/>'
        f'<circle cx="44" cy="17" r="3.5" fill="{c["accent"]}"/>'
        f'<circle cx="44" cy="17" r="8" fill="none" stroke="{c["accent"]}" opacity=".25"/>'
    )
    return _document(WIDTH, DIVIDER_HEIGHT, "Systems trace divider", "A fine emerald signal line separates portfolio sections.", content)


def signal_gif() -> bytes:
    """Create a small, looping palette GIF: a signal node travels along a trace."""
    width, height, frame_count = WIDTH, DIVIDER_HEIGHT, 16
    dark = card_params("dark")
    # Transparent canvas works in both GitHub themes; the trace and node remain visible.
    palette = [
        (0, 0, 0),
        tuple(int(dark["border"][i:i + 2], 16) for i in (1, 3, 5)),
        tuple(int(dark["accent_deep"][i:i + 2], 16) for i in (1, 3, 5)),
        tuple(int(dark["mint"][i:i + 2], 16) for i in (1, 3, 5)),
    ]
    output = bytearray(b"GIF89a")
    output.extend(struct.pack("<HHBBB", width, height, 0xF1, 0, 0))
    for color in palette:
        output.extend(bytes(color))
    output.extend(b"\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00")

    def lzw(indices: list[int]) -> bytes:
        packed = bytearray()
        accumulator = bit_count = 0
        def emit(code: int) -> None:
            nonlocal accumulator, bit_count
            accumulator |= code << bit_count
            bit_count += 3
            while bit_count >= 8:
                packed.append(accumulator & 255)
                accumulator >>= 8
                bit_count -= 8
        # Reset before each literal to keep the stream's code width fixed at
        # three bits. The resulting file is still compact and avoids fragile
        # code-width boundary behavior across different GIF decoders.
        for value in indices:
            emit(4)
            emit(value)
        emit(5)
        if bit_count:
            packed.append(accumulator & 255)
        return bytes(packed)

    for frame in range(frame_count):
        marker_x = 14 + round((width - 28) * frame / (frame_count - 1))
        pixels = [0] * (width * height)
        for x in range(width):
            if x % 24 < 3 or x == width - 1:
                pixels[17 * width + x] = 1
            pixels[16 * width + x] = pixels[18 * width + x] = 1
        for radius, color in ((9, 2), (6, 3), (3, 2)):
            for x in range(max(0, marker_x - radius), min(width, marker_x + radius + 1)):
                for y in range(17 - radius, 18 + radius):
                    if 0 <= y < height and (x - marker_x) ** 2 + (y - 17) ** 2 <= radius ** 2:
                        pixels[y * width + x] = color
        output.extend(b"\x21\xf9\x04\x09\x06\x00\x00\x00")
        output.extend(b"\x2c" + struct.pack("<HHHHB", 0, 0, width, height, 0))
        compressed = lzw(pixels)
        output.append(2)
        for offset in range(0, len(compressed), 255):
            chunk = compressed[offset:offset + 255]
            output.append(len(chunk))
            output.extend(chunk)
        output.append(0)
    output.append(0x3B)
    return bytes(output)


def landscape(mode: str = "dark", projects: list[dict[str, Any]] | None = None) -> str:
    """Map three verified project domains to the engineering questions they explore."""
    c = card_params(mode)
    projects = projects or PROJECTS
    cards = []
    for i, project in enumerate(projects[:3]):
        name = project["name"].upper()
        subject = project["domain"]
        label = project["eyebrow"].split(" / ")[0]
        y = 54 + i * 47
        cards.append(
            f'<text x="26" y="{y+5}" fill="{c["accent"]}" font-family="{MONO_FONT}" font-size="9" letter-spacing="1">0{i+1}</text>'
            f'<rect x="58" y="{y-12}" width="235" height="34" rx="8" fill="{c["panel"]}" stroke="{c["border"]}"/>'
            f'<text x="72" y="{y+1}" fill="{c["text"]}" font-size="12" font-weight="600">{name}</text>'
            f'<text x="72" y="{y+15}" fill="{c["muted"]}" font-size="10">{subject}</text>'
            f'<path d="M293 {y+5}H367" stroke="{c["accent"]}" stroke-width="1.4" opacity=".8"/>'
            f'<circle cx="367" cy="{y+5}" r="3" fill="{c["mint"]}"/>'
            f'<text x="390" y="{y+9}" fill="{c["silver"]}" font-family="{MONO_FONT}" font-size="10" letter-spacing=".8">{label}</text>'
        )
    content = (
        f'<rect x=".5" y=".5" width="829" height="{LANDSCAPE_HEIGHT-1}" rx="15" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="27" fill="{c["muted"]}" font-family="{MONO_FONT}" font-size="9" letter-spacing="1.5">PROJECT LANDSCAPE / THREE DIFFERENT SYSTEMS</text>'
        + "".join(cards)
    )
    return _document(WIDTH, LANDSCAPE_HEIGHT, "Selected project landscape", "A map of three documented projects and the software domains they address: software evolution, endpoint telemetry, and voice interaction.", content)


def activity(data: dict[str, Any], mode: str = "dark") -> str:
    """Show repository metadata and public PushEvents returned in the current API sample."""
    c = card_params(mode)
    counts = [0] * 12
    for index, count in enumerate(data.get("activity_weeks", counts)):
        if index < len(counts):
            counts[index] = max(0, int(count))
    maximum = max(counts) or 1
    baseline = 178
    bars = []
    for i, count in enumerate(counts):
        x = 35 + i * 63
        height = max(3, round(42 * count / maximum)) if count else 2
        color = c["accent"] if count else c["border"]
        bars.append(
            f'<rect x="{x}" y="{baseline-height}" width="24" height="{height}" rx="3" fill="{color}"/>'
            f'<text x="{x+12}" y="195" text-anchor="middle" fill="{c["muted"]}" font-family="{MONO_FONT}" font-size="9">{11-i}w</text>'
        )
    repo_available = data.get("repos_available", "public_repo_count" in data)
    repo_count = str(int(data.get("public_repo_count", 0))) if repo_available else "—"
    stars = str(int(data.get("public_repo_stars", 0))) if repo_available else "—"
    pushes = int(data.get("public_push_event_count", sum(counts)))
    availability = data.get("events_available", False)
    push_value = str(pushes) if availability else "—"
    sample_caption = (
        "Observed PushEvents / recent public API sample only"
        if availability else "Public event sample unavailable / cached buckets shown when present"
    )
    content = (
        f'<rect x=".5" y=".5" width="829" height="{ACTIVITY_HEIGHT-1}" rx="15" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="27" fill="{c["accent"]}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.5">REPOSITORY SIGNAL / PUBLIC DATA</text>'
        f'<text x="24" y="43" fill="{c["muted"]}" font-size="9">Owned public repositories · profile repository and forks excluded</text>'
        f'<path d="M276 56V93 M546 56V93" stroke="{c["border"]}"/>'
        f'<text x="26" y="70" fill="{c["silver"]}" font-family="{MONO_FONT}" font-size="10" letter-spacing=".6">REPOSITORIES</text>'
        f'<text x="26" y="90" fill="{c["text"]}" font-size="20" font-weight="650">{repo_count}</text>'
        f'<text x="300" y="70" fill="{c["silver"]}" font-family="{MONO_FONT}" font-size="10" letter-spacing=".3">STARS ACROSS THESE REPOSITORIES</text>'
        f'<text x="300" y="90" fill="{c["text"]}" font-size="20" font-weight="650">{stars}</text>'
        f'<text x="570" y="70" fill="{c["silver"]}" font-family="{MONO_FONT}" font-size="9" letter-spacing=".35">PUSH EVENTS RETURNED</text>'
        f'<text x="570" y="90" fill="{c["text"]}" font-size="20" font-weight="650">{push_value}</text>'
        f'<path d="M24 {baseline}H806" stroke="{c["grid"]}"/>{"".join(bars)}'
        f'<text x="806" y="211" text-anchor="end" fill="{c["muted"]}" font-size="9">{sample_caption}</text>'
    )
    return _document(WIDTH, ACTIVITY_HEIGHT, "GitHub public repository telemetry", "Public original repository count, combined repository stars, and a weekly grouping of PushEvents returned by GitHub's recent public event sample. This is not a complete contribution chart.", content)


def languages(data: dict[str, Any], mode: str = "dark") -> str:
    """Render GitHub language byte totals with values alongside every bar."""
    c = card_params(mode)
    stats = data.get("languages", {})
    ranked = sorted(
        ((str(name), int(size)) for name, size in stats.items() if int(size) > 0),
        key=lambda pair: (-pair[1], pair[0]),
    )
    total = sum(value for _, value in ranked)
    shown = ranked[:5]
    if len(ranked) > 5:
        shown.append(("Other", sum(value for _, value in ranked[5:])))
    chart = []
    accents = [c["accent"], c["mint"], c["silver"], c["accent_deep"], c["muted"], c["text"]]
    if not shown or not data.get("languages_available", bool(ranked)):
        chart.append(f'<text x="26" y="93" fill="{c["muted"]}" font-size="13">Language totals are unavailable in the current cache.</text>')
    else:
        for i, (name, value) in enumerate(shown):
            y = 80 + i * 27
            pct = value / total if total else 0
            bar_width = 510 * pct
            chart.append(
                f'<text x="26" y="{y+4}" fill="{c["text"]}" font-size="12" font-weight="600">{html.escape(name)}</text>'
                f'<rect x="174" y="{y-8}" width="510" height="12" rx="6" fill="{c["track"]}"/>'
                f'<rect x="174" y="{y-8}" width="{bar_width:.2f}" height="12" rx="6" fill="{accents[i % len(accents)]}"/>'
                f'<text x="795" y="{y+4}" text-anchor="end" fill="{c["muted"]}" font-family="{MONO_FONT}" font-size="11">{pct:.1%}</text>'
            )
    content = (
        f'<rect x=".5" y=".5" width="829" height="{LANGUAGE_HEIGHT-1}" rx="15" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="27" fill="{c["accent"]}" font-family="{MONO_FONT}" font-size="11" letter-spacing="1.3">LANGUAGE COMPOSITION / SOURCE BYTES</text>'
        f'<text x="24" y="45" fill="{c["muted"]}" font-size="10">GitHub language API totals · original public repositories · profile and forks excluded</text>'
        + "".join(chart)
    )
    return _document(WIDTH, LANGUAGE_HEIGHT, "Programming language composition", "Relative language shares from GitHub's language byte totals across owned original public repositories, excluding this profile repository and forks.", content)


def write_assets(directory: Path, data: dict[str, Any]) -> None:
    """Write static theme-aware SVG instruments and a restrained animated signal GIF."""
    directory.mkdir(parents=True, exist_ok=True)
    renderers = {
        "hero": lambda mode: hero(mode),
        "divider": lambda mode: divider(mode),
        "project-landscape": lambda mode: landscape(mode, PROJECTS),
        "activity": lambda mode: activity(data, mode),
        "language-stats": lambda mode: languages(data, mode),
    }
    for name, renderer in renderers.items():
        for mode, suffix in (("dark", ""), ("light", "-light")):
            (directory / f"{name}{suffix}.svg").write_text(renderer(mode), encoding="utf-8", newline="\n")
    (directory / "signal.gif").write_bytes(signal_gif())

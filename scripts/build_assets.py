"""Render compact, self-hosted SVG instruments from theme tokens and cached data."""
from __future__ import annotations

import html
import hashlib
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps, PngImagePlugin

from theme import (
    ACTIVITY_HEIGHT, CONTRIBUTION_HEIGHT, DIVIDER_HEIGHT, HERO_HEIGHT, LANGUAGE_HEIGHT,
    MONO_FONT, NAME, PALETTE, PORTRAIT_HEIGHT, SANS_FONT,
    PORTRAIT_SOURCE, PORTRAIT_WIDTH, TYPE_LINES,
    WIDTH, PANEL_RADIUS, card_params, hex_to_rgb,
)


def _document(width: int, height: int, title: str, description: str, content: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" '
        f'font-family="{html.escape(SANS_FONT, quote=True)}">'
        f'<title id="title">{html.escape(title)}</title>'
        f'<desc id="desc">{html.escape(description)}</desc>{content}</svg>\n'
    )


def premium_hero(mode: str = "dark") -> str:
    """Draw the readable static fallback for the complete hero composition."""
    c = card_params(mode)
    grid = "".join(f'<path d="M{x} 16V{HERO_HEIGHT-16}"/>' for x in range(32, WIDTH, 34))
    content = f'''<defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c['panel_alt']}"/><stop offset=".52" stop-color="{c['panel']}"/><stop offset="1" stop-color="{c['bg_deep']}"/></linearGradient></defs>
    <rect x=".5" y=".5" width="829" height="{HERO_HEIGHT-1}" rx="{PANEL_RADIUS}" fill="url(#panel)" stroke="{c['border']}"/><g fill="none" stroke="{c['grid']}" opacity=".38">{grid}</g>
    <path d="M30 28h11 M30 28v11 M800 28h-11 M800 28v11" stroke="{c['accent']}" opacity=".72" fill="none"/>
    <text x="48" y="48" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.6">COMPUTER SCIENCE / DATA SCIENCE / SOFTWARE</text>
    <rect x="677" y="29" width="119" height="27" rx="13.5" fill="{c['panel_alt']}" stroke="{c['border']}"/><circle cx="694" cy="42.5" r="3" fill="{c['mint']}"/><text x="704" y="45.5" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="8" letter-spacing=".8">AVAILABLE</text>
    <text x="47" y="108" fill="{c['text']}" font-size="48" font-weight="800">{html.escape(NAME)}</text>
    <text x="50" y="140" fill="{c['silver']}" font-family="{MONO_FONT}" font-size="11" letter-spacing="1.5">SOFTWARE ENGINEERING / DATA SCIENCE / APPLIED AI</text>
    <path d="M49 160H782" stroke="{c['border']}"/><path d="M49 160H248" stroke="{c['accent']}" stroke-width="1.5"/><circle cx="248" cy="160" r="3" fill="{c['mint']}"/>
    <text x="50" y="207" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="14" font-weight="700">&gt; {html.escape(TYPE_LINES[0])}<tspan opacity=".8">_</tspan></text>
    <text x="782" y="239" text-anchor="end" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="8" letter-spacing="1">ENGINEERING PROFILE</text>'''
    return _document(WIDTH, HERO_HEIGHT, f"{NAME} — software, data, and applied AI", "A bold professional engineering profile hero with a descriptor, separator, and current focus.", content)


def divider(mode: str = "dark") -> str:
    c = card_params(mode)
    content = (
        f'<path d="M0 19H{WIDTH}" stroke="{c["border"]}"/>'
        f'<path d="M0 19H{WIDTH}" stroke="{c["accent"]}" stroke-width="1.5" stroke-dasharray="2 22" opacity=".72"/>'
        f'<circle cx="44" cy="19" r="3.5" fill="{c["accent"]}"/>'
        f'<circle cx="44" cy="19" r="8" fill="none" stroke="{c["accent"]}" opacity=".25"/>'
    )
    return _document(WIDTH, DIVIDER_HEIGHT, "Systems trace divider", "A fine emerald signal line separates portfolio sections; an animated GIF is used in GitHub with this static fallback.", content)


def _font(size: int) -> ImageFont.ImageFont:
    # Pillow's built-in font is pinned through requirements.txt, so GIF bytes
    # stay identical on Windows and the Ubuntu GitHub Actions runner.
    return ImageFont.load_default(size=size)


def _gif(frames: list[Image.Image], durations: list[int]) -> bytes:
    """Encode small, palette-limited, looped GIFs for GitHub's image renderer."""
    import io
    palette = frames[0].quantize(colors=32, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    output = io.BytesIO()
    indexed[0].save(output, format="GIF", save_all=True, append_images=indexed[1:], duration=durations, loop=0, optimize=True, disposal=1)
    return output.getvalue()


def portrait(directory: Path) -> bool:
    """Cache a restrained duotone portrait derived only from the supplied photo."""
    source = directory / PORTRAIT_SOURCE.rsplit("/", 1)[-1]
    output = directory / "profile-portrait.png"
    key = hashlib.sha256(source.read_bytes() + PALETTE["emerald"].encode() + PALETTE["bg_deep"].encode()).hexdigest() if source.is_file() else None
    if output.is_file() and key is not None:
        try:
            with Image.open(output) as cached:
                if cached.size == (PORTRAIT_WIDTH, PORTRAIT_HEIGHT) and cached.info.get("GenerationKey") == key:
                    return True
        except OSError:
            pass
    if not source.is_file():
        if output.is_file():
            try:
                with Image.open(output) as cached:
                    if cached.size == (PORTRAIT_WIDTH, PORTRAIT_HEIGHT):
                        return cached.info.get("PortraitSource") == "true"
            except OSError:
                pass
        placeholder = Image.new("RGB", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), hex_to_rgb(PALETTE["bg_deep"]))
        draw = ImageDraw.Draw(placeholder)
        draw.rectangle((10, 10, PORTRAIT_WIDTH-11, PORTRAIT_HEIGHT-11), outline=hex_to_rgb(PALETTE["emerald_deep"]), width=2)
        draw.text((28, 270), "PHOTO SOURCE REQUIRED", font=_font(22), fill=hex_to_rgb(PALETTE["mint"]))
        metadata = PngImagePlugin.PngInfo(); metadata.add_text("PortraitSource", "placeholder")
        placeholder.save(output, format="PNG", optimize=True, pnginfo=metadata)
        return False
    with Image.open(source) as original:
        image = ImageOps.fit(original.convert("RGB"), (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), method=Image.Resampling.LANCZOS, centering=(0.5, 0.42))
    image = ImageOps.grayscale(image).point(lambda value: int(value * 0.78 + 42))
    dark = hex_to_rgb(PALETTE["bg_deep"]); light = hex_to_rgb(PALETTE["mint"])
    image = ImageOps.colorize(image, black=dark, white=light).quantize(colors=28, method=Image.Quantize.MEDIANCUT).convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, PORTRAIT_WIDTH-11, PORTRAIT_HEIGHT-11), outline=hex_to_rgb(PALETTE["emerald_deep"]), width=2)
    for y in range(16, PORTRAIT_HEIGHT-16, 5):
        draw.line((16, y, PORTRAIT_WIDTH-17, y), fill=hex_to_rgb(PALETTE["bg_deep"]), width=1)
    draw.text((20, PORTRAIT_HEIGHT-25), "SARTHAK / PROFILE", font=_font(10), fill=hex_to_rgb(PALETTE["mint"]))
    metadata = PngImagePlugin.PngInfo(); metadata.add_text("GenerationKey", key); metadata.add_text("PortraitSource", "true")
    image.save(output, format="PNG", optimize=True, pnginfo=metadata)
    return True


def hero_animation(mode: str = "dark") -> bytes:
    """Render a stable, terminal-style typewriter hero and moving separator."""
    c = card_params(mode); frames: list[Image.Image] = []; durations: list[int] = []
    def frame(line: str, highlight_x: int, cursor: bool) -> Image.Image:
        image = Image.new("RGB", (WIDTH, HERO_HEIGHT), hex_to_rgb(c["bg_deep"])); draw = ImageDraw.Draw(image)
        panel = hex_to_rgb(c["panel"])
        draw.rounded_rectangle((0, 0, WIDTH - 1, HERO_HEIGHT - 1), 18, fill=panel, outline=hex_to_rgb(c["border"]))
        for x in range(32, WIDTH, 34): draw.line((x, 16, x, HERO_HEIGHT - 16), fill=hex_to_rgb(c["grid"]))
        draw.text((48, 38), "COMPUTER SCIENCE / DATA SCIENCE / SOFTWARE", font=_font(10), fill=hex_to_rgb(c["accent"]))
        draw.rounded_rectangle((677, 29, 796, 56), 14, fill=hex_to_rgb(c["panel_alt"]), outline=hex_to_rgb(c["border"]))
        draw.ellipse((691, 39, 697, 45), fill=hex_to_rgb(c["mint"]))
        draw.text((704, 39), "AVAILABLE", font=_font(8), fill=hex_to_rgb(c["muted"]))
        name_font = _font(52)
        # A one-pixel offset creates a firm bold weight using the pinned font.
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            draw.text((47 + dx, 66 + dy), NAME, font=name_font, fill=hex_to_rgb(c["text"]))
        draw.text((50, 130), "SOFTWARE ENGINEERING / DATA SCIENCE / APPLIED AI", font=_font(11), fill=hex_to_rgb(c["silver"]))
        draw.line((49, 157, 782, 157), fill=hex_to_rgb(c["border"]))
        draw.line((highlight_x, 157, min(782, highlight_x + 92), 157), fill=hex_to_rgb(c["accent"]), width=2)
        draw.ellipse((min(782, highlight_x + 92) - 3, 154, min(782, highlight_x + 92) + 3, 160), fill=hex_to_rgb(c["mint"]))
        typed = "> " + line + ("_" if cursor else " ")
        draw.text((50, 197), typed, font=_font(14), fill=hex_to_rgb(c["accent"]))
        draw.text((782, 236), "ENGINEERING PROFILE", anchor="ra", font=_font(8), fill=hex_to_rgb(c["muted"]))
        return image
    positions = list(range(50, 692, 72))
    for index, phrase in enumerate(TYPE_LINES):
        steps = sorted({0, len(phrase) // 4, len(phrase) // 2, (3 * len(phrase)) // 4, len(phrase)})
        for step in steps:
            frames.append(frame(phrase[:step], positions[(index * 6 + step) % len(positions)], True)); durations.append(110)
        frames.append(frame(phrase, positions[(index * 6 + 5) % len(positions)], False)); durations.append(1200)
        for step in reversed(steps[:-1]):
            frames.append(frame(phrase[:step], positions[(index * 6 + step + 2) % len(positions)], True)); durations.append(75)
    return _gif(frames, durations)


def _sample_grid(draw: ImageDraw.ImageDraw, data: dict[str, Any], c: dict[str, str], left: int = 56, top: int = 51) -> None:
    """Draw a contribution-style grid whose active cells come only from sampled events."""
    counts = [max(0, int(x)) for x in data.get("activity_weeks", [])[:12]]; counts = (counts + [0] * 12)[:12]
    maximum = max(counts) or 1; cell, gap = 11, 3
    for col in range(52):
        source = counts[col - 40] if col >= 40 else 0
        for row in range(7):
            active = source and row >= 7 - min(7, source)
            fill = c["mint"] if active and source / maximum > .5 else (c["accent"] if active else c["panel_alt"])
            x, y = left + col * (cell + gap), top + row * (cell + gap)
            draw.rounded_rectangle((x, y, x + cell, y + cell), 2, fill=hex_to_rgb(fill), outline=hex_to_rgb(c["grid"]))


def contribution_snake_motion(data: dict[str, Any], mode: str = "dark") -> bytes:
    """Render a decorative snake travelling across an honest sampled-event grid."""
    c = card_params(mode); counts = [max(0, int(x)) for x in data.get("activity_weeks", [])[:12]]; counts = (counts + [0] * 12)[:12]
    frames: list[Image.Image] = []; durations: list[int] = []
    left, top, cell_gap = 56, 51, 14
    for step in range(18):
        image = Image.new("RGB", (WIDTH, 190), hex_to_rgb(c["bg"]))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, WIDTH - 1, 189), 18, fill=hex_to_rgb(c["panel"]), outline=hex_to_rgb(c["border"]))
        draw.text((24, 22), "CONTRIBUTION ART / SNAKE / SAMPLED PUBLIC ACTIVITY", font=_font(10), fill=hex_to_rgb(c["accent"]))
        _sample_grid(draw, data, c, left, top)
        head_col = step * 3 % 52; row = 2 if (step // 6) % 2 == 0 else 4
        for segment in range(7):
            col = head_col - segment
            if col < 0: continue
            x, y = left + col * cell_gap, top + row * cell_gap
            color = c["mint"] if segment == 0 else c["accent"]
            draw.ellipse((x - 2, y - 2, x + 13, y + 13), fill=hex_to_rgb(color))
            if segment == 0:
                draw.ellipse((x + 8, y + 3, x + 10, y + 5), fill=hex_to_rgb(c["bg_deep"]))
        draw.text((24, 168), "Decorative path over a grid based only on the latest sampled public PushEvents; not a full contribution calendar.", font=_font(8), fill=hex_to_rgb(c["muted"]))
        frames.append(image); durations.append(120)
    return _gif(frames, durations)


def contribution_pacman_motion(data: dict[str, Any], mode: str = "dark") -> bytes:
    """Render five small Pac-Man characters on independent, visible grid paths."""
    c = card_params(mode); frames: list[Image.Image] = []; durations: list[int] = []
    left, top, cell_gap = 56, 51, 14
    colors = [c["mint"], c["accent"], c["silver"], c["accent_deep"], "#6FB7C3"]
    rows = [0, 2, 4, 6, 3]
    for step in range(20):
        image = Image.new("RGB", (WIDTH, 190), hex_to_rgb(c["bg"])); draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, WIDTH - 1, 189), 18, fill=hex_to_rgb(c["panel"]), outline=hex_to_rgb(c["border"]))
        draw.text((24, 22), "CONTRIBUTION ART / FIVE PAC-MEN / SAMPLED PUBLIC ACTIVITY", font=_font(10), fill=hex_to_rgb(c["accent"]))
        _sample_grid(draw, data, c, left, top)
        for character, color in enumerate(colors):
            col = (step * 2 + character * 10) % 52; row = rows[character]
            x, y = left + col * cell_gap - 2, top + row * cell_gap - 2
            mouth = 36 if (step + character) % 2 else 20
            draw.pieslice((x, y, x + 16, y + 16), start=mouth, end=360-mouth, fill=hex_to_rgb(color))
            draw.ellipse((x + 10, y + 4, x + 12, y + 6), fill=hex_to_rgb(c["bg_deep"]))
        draw.text((24, 168), "Five decorative characters move independently; cells summarize sampled public PushEvents, not private or full contribution data.", font=_font(8), fill=hex_to_rgb(c["muted"]))
        frames.append(image); durations.append(110)
    return _gif(frames, durations)


def telemetry_motion(data: dict[str, Any], mode: str = "dark") -> bytes:
    """Reveal account signals, language mix, and activity in one fixed dashboard."""
    c = card_params(mode); counts = [max(0, int(x)) for x in data.get("activity_weeks", [])[:12]]; counts = (counts + [0] * 12)[:12]
    maximum = max(counts) or 1; frames: list[Image.Image] = []; durations: list[int] = []
    ranked = sorted(((str(k), int(v)) for k, v in data.get("languages", {}).items() if int(v) > 0), key=lambda item: -item[1])
    total = sum(value for _, value in ranked) or 1
    shown = ranked[:4]
    if len(ranked) > 4: shown.append(("Other", sum(value for _, value in ranked[4:])))
    for progress in range(1, 8):
        image = Image.new("RGB", (WIDTH, ACTIVITY_HEIGHT), hex_to_rgb(c["bg"]))
        draw = ImageDraw.Draw(image); draw.rounded_rectangle((0, 0, WIDTH - 1, ACTIVITY_HEIGHT - 1), 18, fill=hex_to_rgb(c["bg"]), outline=hex_to_rgb(c["border"]))
        draw.rounded_rectangle((18, 18, 400, 166), 14, fill=hex_to_rgb(c["panel"]), outline=hex_to_rgb(c["border"]))
        draw.rounded_rectangle((420, 18, 812, 166), 14, fill=hex_to_rgb(c["panel"]), outline=hex_to_rgb(c["border"]))
        draw.text((38, 39), "GITHUB STATISTICS", font=_font(10), fill=hex_to_rgb(c["accent"]))
        values = [("REPOSITORIES", data.get("public_repo_count", "—")), ("STARS", data.get("public_repo_stars", "—")), ("FOLLOWERS", data.get("followers", "—")), ("SAMPLED EVENTS", data.get("public_push_event_count", "—"))]
        for i, (label, value) in enumerate(values):
            x, y = 38 + (i % 2) * 170, 65 + (i // 2) * 50
            draw.text((x, y), label, font=_font(8), fill=hex_to_rgb(c["muted"]))
            final = int(value) if isinstance(value, int) or str(value).isdigit() else 0
            display = round(final * progress / 7)
            draw.text((x, y + 18), str(display if progress < 7 else value), font=_font(20), fill=hex_to_rgb(c["text"]))
        draw.text((440, 39), "LANGUAGE MIX / SOURCE BYTES", font=_font(10), fill=hex_to_rgb(c["accent"]))
        for i, (name, value) in enumerate(shown):
            y, fraction = 70 + i * 18, value / total
            draw.text((440, y), name, font=_font(9), fill=hex_to_rgb(c["text"]))
            draw.rounded_rectangle((560, y - 1, 752, y + 9), 5, fill=hex_to_rgb(c["track"]))
            width = max(2, round(192 * fraction * progress / 7))
            draw.rounded_rectangle((560, y - 1, 560 + width, y + 9), 5, fill=hex_to_rgb(c["accent"] if i == 0 else c["mint"]))
            draw.text((772, y), f"{fraction:.1%}", font=_font(8), fill=hex_to_rgb(c["silver"]))
        draw.rounded_rectangle((18, 184, 812, 372), 14, fill=hex_to_rgb(c["panel"]), outline=hex_to_rgb(c["border"]))
        draw.text((38, 205), "SAMPLED PUSH EVENTS / TWELVE WEEK BINS", font=_font(10), fill=hex_to_rgb(c["accent"]))
        baseline, left, step = 344, 58, 730 / 12
        for y in (263, baseline): draw.line((left, y, 786, y), fill=hex_to_rgb(c["grid"]))
        for i, count in enumerate(counts):
            height = max(2, round(96 * count / maximum * progress / 7)); x = left + i * step + 12
            draw.rounded_rectangle((x, baseline - height, x + 29, baseline), 4, fill=hex_to_rgb(c["accent"] if count else c["track"]))
        draw.text((38, 359), "Latest public-event response: up to 100 events. This is an activity sample, not a contribution history.", font=_font(8), fill=hex_to_rgb(c["muted"]))
        frames.append(image); durations.append(110 if progress < 7 else 1200)
    return _gif(frames, durations)


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


def telemetry(data: dict[str, Any], mode: str = "dark") -> str:
    """Render account counters and a clearly sampled twelve-week PushEvent graph."""
    c = card_params(mode)
    values = [
        ("ORIGINAL REPOSITORIES", str(data.get("public_repo_count", "—")) if data.get("repos_available", False) else "—"),
        ("REPOSITORY STARS", str(data.get("public_repo_stars", "—")) if data.get("repos_available", False) else "—"),
        ("FOLLOWERS", str(data.get("followers", "—")) if data.get("profile_available", False) else "—"),
        ("SAMPLED PUSH EVENTS", str(data.get("public_push_event_count", "—")) if data.get("events_available", False) else "—"),
    ]
    cards=[]
    for i,(label,value) in enumerate(values):
        x=22+i*199
        cards.append(f'<rect x="{x}" y="62" width="184" height="58" rx="10" fill="{c["panel_alt"]}" stroke="{c["border"]}"/><text x="{x+13}" y="83" fill="{c["muted"]}" font-family="{MONO_FONT}" font-size="8" letter-spacing=".65">{label}</text><text x="{x+13}" y="108" fill="{c["text"]}" font-size="21" font-weight="650">{value}</text>')
    counts=[max(0,int(x)) for x in data.get("activity_weeks",[0]*12)[:12]]
    counts=(counts+[0]*12)[:12]; maximum=max(counts) or 1
    chart=[]; left=60; top=153; baseline=260; chartw=742; chart_h=88; step=chartw/12
    for tick in (0,.5,1):
        y=baseline-round(chart_h*tick)
        chart.append(f'<path d="M{left} {y}H{left+chartw}" stroke="{c["grid"]}"/><text x="48" y="{y+3}" text-anchor="end" fill="{c["muted"]}" font-family="{MONO_FONT}" font-size="8">{round(max(counts)*tick)}</text>')
    for i,count in enumerate(counts):
        week_label = "11+" if i == 0 else str(11-i)
        h=round(chart_h*count/maximum) if count else 2
        x=left+i*step+12
        chart.append(f'<rect x="{x:.1f}" y="{baseline-h}" width="29" height="{h}" rx="4" fill="{c["accent"] if count else c["track"]}"/><text x="{x+14.5:.1f}" y="278" text-anchor="middle" fill="{c["muted"]}" font-family="{MONO_FONT}" font-size="8">{week_label}w</text>')
    available=data.get("events_available",False)
    annotation="Recent public PushEvent sample · 12 weekly buckets · up to 100 events" if available else "Recent public event sample unavailable · cached buckets shown when present"
    content=(f'<rect x=".5" y=".5" width="829" height="{ACTIVITY_HEIGHT-1}" rx="{PANEL_RADIUS}" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="29" fill="{c["accent"]}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.4">GITHUB / PUBLIC ACCOUNT SIGNAL</text>'
        f'<text x="24" y="46" fill="{c["muted"]}" font-size="10">Original public repositories exclude forks and this profile repository</text>'
        + ''.join(cards)+''.join(chart)
        + f'<text x="802" y="291" text-anchor="end" fill="{c["muted"]}" font-size="9">{html.escape(annotation)}</text>')
    return _document(WIDTH,ACTIVITY_HEIGHT,"Public GitHub account telemetry","Cached repository, star, follower and sampled public PushEvent metrics; chart groups the latest public event feed into twelve weekly buckets.",content)


def contribution_art(data: dict[str, Any], mode: str = "dark") -> str:
    """Render a static contribution-style grid from the limited public event sample."""
    c = card_params(mode); counts = [max(0, int(x)) for x in data.get("activity_weeks", [])[:12]]; counts = (counts + [0] * 12)[:12]
    maximum = max(counts) or 1; cells = []; cell, gap, left, top = 12, 3, 86, 58
    for col in range(48):
        source = counts[col - 36] if col >= 36 else 0
        active_rows = min(7, source)
        for row in range(7):
            active = source and row >= 7 - active_rows
            fill = c["mint"] if active and source / maximum > .5 else (c["accent"] if active else c["panel_alt"])
            x, y = left + col * (cell + gap), top + row * (cell + gap)
            cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{fill}" stroke="{c["grid"]}"/>')
    content = (f'<rect x=".5" y=".5" width="829" height="{CONTRIBUTION_HEIGHT-1}" rx="{PANEL_RADIUS}" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="26" fill="{c["accent"]}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.2">CONTRIBUTION ART / PUBLIC EVENT SAMPLE</text>'
        f'<text x="24" y="43" fill="{c["muted"]}" font-size="9">Static fallback: decorative grid, with cells based only on the latest sampled public PushEvents.</text>'
        + ''.join(cells)
        + f'<circle cx="508" cy="114" r="11" fill="{c["accent"]}"/><path d="M508 114l13-7v14z" fill="{c["bg"]}"/><circle cx="512" cy="109" r="1.5" fill="{c["bg_deep"]}"/>'
        + f'<text x="24" y="174" fill="{c["muted"]}" font-size="9">The character is decorative. This is not GitHub’s full daily contribution calendar or a claim about private activity.</text>')
    return _document(WIDTH, CONTRIBUTION_HEIGHT, "Decorative Pac-Man public event grid", "A decorative Pac-Man sits on a contribution-style grid that summarizes only recent sampled public PushEvents, not a full contribution calendar.", content)


def write_assets(directory: Path, data: dict[str, Any]) -> bool:
    """Write static fallbacks and self-hosted animated assets; return portrait validity."""
    directory.mkdir(parents=True, exist_ok=True)
    renderers = {
        "hero": lambda mode: premium_hero(mode),
        "divider": lambda mode: divider(mode),
        "activity": lambda mode: telemetry(data, mode),
        "language-stats": lambda mode: languages(data, mode),
        "contribution-art": lambda mode: contribution_art(data, mode),
    }
    for name, renderer in renderers.items():
        for mode, suffix in (("dark", ""), ("light", "-light")):
            path=directory / f"{name}{suffix}.svg"
            content=renderer(mode)
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                path.write_text(content, encoding="utf-8", newline="\n")
    available = portrait(directory)
    animated = {
        "hero-motion": hero_animation,
        "telemetry-motion": lambda mode: telemetry_motion(data, mode),
        "contribution-snake-motion": lambda mode: contribution_snake_motion(data, mode),
        "contribution-pacman-motion": lambda mode: contribution_pacman_motion(data, mode),
    }
    for name, renderer in animated.items():
        for mode, suffix in (("dark", ""), ("light", "-light")):
            path = directory / f"{name}{suffix}.gif"
            payload = renderer(mode)
            if not path.is_file() or path.read_bytes() != payload:
                path.write_bytes(payload)
    return available

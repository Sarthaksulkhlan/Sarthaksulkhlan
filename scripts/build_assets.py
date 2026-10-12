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
    """Draw a compact, static-first systems hero with a restrained information hierarchy."""
    c = card_params(mode)
    grid = "".join(f'<path d="M{x} 18V{HERO_HEIGHT-18}"/>' for x in range(40, WIDTH, 32))
    content = f'''<defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c['panel']}"/><stop offset="1" stop-color="{c['bg_deep']}"/></linearGradient><linearGradient id="route"><stop stop-color="{c['accent_deep']}"/><stop offset="1" stop-color="{c['mint']}"/></linearGradient></defs>
    <rect x=".5" y=".5" width="829" height="{HERO_HEIGHT-1}" rx="{PANEL_RADIUS}" fill="url(#panel)" stroke="{c['border']}"/><g fill="none" stroke="{c['grid']}" opacity=".26">{grid}</g>
    <path d="M32 28h13 M32 28v13 M798 28h-13 M798 28v13 M32 232h13 M32 232v-13 M798 232h-13 M798 232v-13" stroke="{c['accent']}" opacity=".6" fill="none"/>
    <text x="48" y="53" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.4">COMPUTER SCIENCE / DATA SCIENCE / SOFTWARE</text>
    <rect x="667" y="34" width="126" height="28" rx="14" fill="{c['panel_alt']}" stroke="{c['border']}"/><circle cx="683" cy="48" r="3" fill="{c['accent']}"/><text x="694" y="51" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="8" letter-spacing=".5">PROFILE / PUBLIC DATA</text>
    <text x="47" y="110" fill="{c['text']}" font-size="36" font-weight="650">{html.escape(NAME)}</text><text x="50" y="144" fill="{c['silver']}" font-size="15">Practical software, informed by data and AI.</text><path d="M48 168H512" stroke="{c['border']}"/>
    <text x="50" y="197" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.2">BUILD</text><path d="M95 193H157" stroke="url(#route)"/><circle cx="157" cy="193" r="3" fill="{c['accent']}"/>
    <text x="173" y="197" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.2">OBSERVE</text><path d="M238 193H299" stroke="url(#route)"/><circle cx="299" cy="193" r="3" fill="{c['accent']}"/><text x="315" y="197" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.2">REFINE</text>
    <path d="M548 78V222" stroke="{c['border']}"/><text x="582" y="92" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="9" letter-spacing="1.2">SYSTEMS LOOP</text><path d="M606 116V196" stroke="url(#route)" stroke-width="1.5"/><circle cx="606" cy="118" r="4" fill="{c['accent']}"/><circle cx="606" cy="157" r="4" fill="{c['mint']}"/><circle cx="606" cy="196" r="4" fill="{c['accent']}"/>
    <text x="623" y="122" fill="{c['text']}" font-size="12">working code</text><text x="623" y="161" fill="{c['text']}" font-size="12">observed data</text><text x="623" y="200" fill="{c['text']}" font-size="12">measured change</text><text x="791" y="239" text-anchor="end" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="8" letter-spacing="1">PERSONAL ENGINEERING PROFILE</text>'''
    return _document(WIDTH, HERO_HEIGHT, f"{NAME} — software, data, and applied AI", "A compact build, observe, refine engineering profile.", content)


def divider(mode: str = "dark") -> str:
    c = card_params(mode)
    content = (
        f'<path d="M0 19H{WIDTH}" stroke="{c["border"]}"/>'
        f'<path d="M0 19H{WIDTH}" stroke="{c["accent"]}" stroke-width="1.5" stroke-dasharray="2 22" opacity=".72"/>'
        f'<circle cx="44" cy="19" r="3.5" fill="{c["accent"]}"/>'
        f'<circle cx="44" cy="19" r="8" fill="none" stroke="{c["accent"]}" opacity=".25"/>'
    )
    return _document(WIDTH, DIVIDER_HEIGHT, "Systems trace divider", "A fine emerald signal line separates portfolio sections; an animated GIF is used in GitHub with this static fallback.", content)


def typing(mode: str = "dark") -> str:
    c = card_params(mode)
    lines = "".join(f'<text x="24" y="{35+i*26}" fill="{c["accent"] if i == 0 else c["muted"]}" font-family="{MONO_FONT}" font-size="14">› {html.escape(line)}</text>' for i, line in enumerate(TYPE_LINES[:3]))
    return _document(WIDTH, 100, "Current engineering focus", "Building software, learning data and AI engineering, and studying real project systems.", f'<rect width="830" height="100" rx="{PANEL_RADIUS}" fill="{c["bg"]}" stroke="{c["border"]}"/>{lines}')


def _font(size: int) -> ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


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


def typing_animation(mode: str = "dark") -> bytes:
    """Render one optimized fixed-size loop with type, pause, and erase phases."""
    c = card_params(mode)
    font = _font(18)
    size = (WIDTH, 52)
    frames: list[Image.Image] = []
    durations: list[int] = []
    def frame(line: str, cursor: bool = True) -> Image.Image:
        image = Image.new("RGB", size, hex_to_rgb(c["bg"]))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, WIDTH-1, 51), 10, fill=hex_to_rgb(c["panel"]), outline=hex_to_rgb(c["border"]))
        draw.ellipse((13, 23, 18, 28), fill=hex_to_rgb(c["accent"]))
        prefix = "> " + line
        draw.text((28, 15), prefix, font=font, fill=hex_to_rgb(c["text"]))
        if cursor:
            x = 28 + int(draw.textlength(prefix, font=font)) + 2
            draw.rectangle((x, 17, x+2, 34), fill=hex_to_rgb(c["accent"]))
        return image
    for line in TYPE_LINES:
        for count in range(len(line)+1):
            frames.append(frame(line[:count])); durations.append(58)
        frames.extend([frame(line, False), frame(line, True), frame(line, False)])
        durations.extend([250, 280, 250])
        for count in range(len(line)-1, -1, -1):
            frames.append(frame(line[:count])); durations.append(34)
    # Use one common palette and delta frames so a narrow text change does not
    # rewrite a full-color frame repeatedly in the resulting GIF.
    palette = frames[0].quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    indexed = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image in frames]
    import io
    output = io.BytesIO()
    indexed[0].save(output, format="GIF", save_all=True, append_images=indexed[1:], duration=durations, loop=0, optimize=True, disposal=1)
    return output.getvalue()


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
    """Visualize only genuine weekly counts from the sampled public event feed."""
    c=card_params(mode); counts=[max(0,int(x)) for x in data.get("activity_weeks",[])[:12]]; counts=(counts+[0]*12)[:12]; maximum=max(counts) or 1
    cells=[]
    for i,count in enumerate(counts):
        week_label = "11+" if i == 0 else str(11-i)
        x=22+i*65; strength=count/maximum
        fill=c["accent"] if count and strength>.65 else (c["mint"] if count else c["panel_alt"])
        celltext=c["bg_deep"] if count else c["muted"]
        cells.append(f'<rect x="{x}" y="60" width="54" height="46" rx="8" fill="{fill}" stroke="{c["border"]}"/><text x="{x+27}" y="82" text-anchor="middle" fill="{celltext}" font-size="15" font-weight="650">{count}</text><text x="{x+27}" y="98" text-anchor="middle" fill="{celltext}" font-family="{MONO_FONT}" font-size="7">{week_label}W</text>')
    status="Observed public events" if data.get("events_available",False) else "Public event sample unavailable"
    content=(f'<rect x=".5" y=".5" width="829" height="{CONTRIBUTION_HEIGHT-1}" rx="{PANEL_RADIUS}" fill="{c["bg"]}" stroke="{c["border"]}"/>'
        f'<text x="22" y="28" fill="{c["accent"]}" font-family="{MONO_FONT}" font-size="9" letter-spacing="1.2">WEEKLY EVENT TRACE / {html.escape(status.upper())}</text>'
        + ''.join(cells)+f'<text x="22" y="128" fill="{c["muted"]}" font-size="9">Counts are sampled PushEvents, not a daily contribution calendar; the oldest bin includes events 11+ weeks old.</text>')
    return _document(WIDTH,CONTRIBUTION_HEIGHT,"Sampled public contribution activity","Twelve sampled PushEvent groups from GitHub's recent public event feed; the oldest group includes events 11+ weeks old, and this is not a complete contribution calendar.",content)


def write_assets(directory: Path, data: dict[str, Any]) -> bool:
    """Write static fallbacks and self-hosted animated assets; return portrait validity."""
    directory.mkdir(parents=True, exist_ok=True)
    renderers = {
        "hero": lambda mode: premium_hero(mode),
        "typing": lambda mode: typing(mode),
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
    for mode,suffix in (("dark",""),("light","-light")):
        path=directory / f"typing{suffix}.gif"
        payload=typing_animation(mode)
        if not path.is_file() or path.read_bytes() != payload:
            path.write_bytes(payload)
    return available

"""Render compact, self-hosted SVG instruments from theme tokens and cached data."""
from __future__ import annotations

import html
import math
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps, PngImagePlugin

from theme import (
    ACTIVITY_HEIGHT, DIVIDER_HEIGHT, HERO_HEIGHT, HERO_FRAMES, LANGUAGE_HEIGHT,
    LANDSCAPE_HEIGHT, MOTION_FRAME_MS, MONO_FONT, NAME, PALETTE, PORTRAIT_HEIGHT,
    PORTRAIT_SOURCE, PORTRAIT_WIDTH, PROJECTS, SANS_FONT, SKILLS_HEIGHT, TYPE_LINES,
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


def hero(mode: str = "dark") -> str:
    """Render the static fallback for the portfolio's animated systems hero."""
    c = card_params(mode)
    grid = "".join(f'<path d="M{x} 15V{HERO_HEIGHT-15}"/>' for x in range(36, WIDTH, 30))
    grid += "".join(f'<path d="M18 {y}H812"/>' for y in range(28, HERO_HEIGHT, 30))
    nodes = []
    for x, label, sublabel in ((544, "BUILD", "working code"), (669, "OBSERVE", "real signals"), (786, "REFINE", "better systems")):
        nodes.append(
            f'<rect x="{x-45}" y="116" width="90" height="72" rx="12" fill="{c["panel_alt"]}" stroke="{c["border"]}"/>'
            f'<circle cx="{x}" cy="135" r="4" fill="{c["accent"]}"/>'
            f'<text x="{x}" y="157" text-anchor="middle" fill="{c["text"]}" font-family="{MONO_FONT}" font-size="9" letter-spacing="1">{label}</text>'
            f'<text x="{x}" y="174" text-anchor="middle" fill="{c["muted"]}" font-size="8">{sublabel}</text>'
        )
    content = f'''<defs>
      <linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c['panel']}"/><stop offset="1" stop-color="{c['bg_deep']}"/></linearGradient>
      <linearGradient id="route" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{c['accent_deep']}"/><stop offset=".55" stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['mint']}"/></linearGradient>
      <radialGradient id="glow"><stop stop-color="{c['accent']}" stop-opacity=".19"/><stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/></radialGradient>
    </defs>
    <rect x=".5" y=".5" width="829" height="{HERO_HEIGHT-1}" rx="{PANEL_RADIUS}" fill="url(#surface)" stroke="{c['border']}"/>
    <circle cx="702" cy="126" r="158" fill="url(#glow)"/>
    <g fill="none" stroke="{c['grid']}" opacity=".52">{grid}</g>
    <path d="M32 28h15 M32 28v15 M798 28h-15 M798 28v15 M32 {HERO_HEIGHT-28}h15 M32 {HERO_HEIGHT-28}v-15" stroke="{c['accent']}" opacity=".8" fill="none"/>
    <text x="48" y="58" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1.8">COMPUTER SCIENCE / DATA SCIENCE / SOFTWARE</text>
    <text x="46" y="116" fill="{c['text']}" font-size="38" font-weight="700">{html.escape(NAME)}</text>
    <text x="49" y="151" fill="{c['silver']}" font-size="15">Practical software, informed by data and AI.</text>
    <text x="49" y="180" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="10" letter-spacing="1">LEARN  /  BUILD  /  MEASURE  /  IMPROVE</text>
    <path d="M498 152H499 M589 152H624 M714 152H741" fill="none" stroke="url(#route)" stroke-width="2"/>
    {''.join(nodes)}
    <path d="M48 224H782" stroke="{c['border']}"/>
    <circle cx="48" cy="224" r="3" fill="{c['accent']}"/>
    <text x="60" y="248" fill="{c['muted']}" font-family="{MONO_FONT}" font-size="9">CURRENT THREAD</text>
    <text x="782" y="248" text-anchor="end" fill="{c['accent']}" font-family="{MONO_FONT}" font-size="9" letter-spacing="1">SYSTEMS · DATA · APPLIED AI</text>'''
    return _document(WIDTH, HERO_HEIGHT, f"{NAME} — computer science, data science, and software", "A technical portfolio hero showing a practical engineering loop from building through observation to refinement.", content)


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


def _gif(frames: list[Image.Image], duration: int = MOTION_FRAME_MS) -> bytes:
    import io
    output = io.BytesIO()
    frames[0].save(output, format="GIF", save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2, optimize=True)
    return output.getvalue()


def portrait(directory: Path) -> bool:
    """Render the supplied private source photo as a recognizable duotone halftone portrait."""
    source = directory / "profile-photo-source.jpg"
    output = directory / "profile-portrait.png"
    if not source.is_file():
        if output.is_file():
            try:
                with Image.open(output) as existing:
                    if existing.info.get("PortraitSource") == "true":
                        return True
            except OSError:
                pass
        image = Image.new("RGB", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), hex_to_rgb(PALETTE["bg_deep"]))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((10, 10, PORTRAIT_WIDTH-11, PORTRAIT_HEIGHT-11), 18, outline=hex_to_rgb(PALETTE["border"]), width=2)
        draw.text((36, PORTRAIT_HEIGHT//2-12), "PHOTO SOURCE REQUIRED", font=_font(22), fill=hex_to_rgb(PALETTE["mint"]))
        image.save(output, pnginfo=PngImagePlugin.PngInfo())
        return False
    with Image.open(source) as original:
        image = ImageOps.fit(original.convert("RGB"), (PORTRAIT_WIDTH-36, PORTRAIT_HEIGHT-36), method=Image.Resampling.LANCZOS, centering=(.5, .40))
    mono = ImageOps.grayscale(image)
    mono = ImageEnhance.Contrast(mono).enhance(1.24)
    image = ImageOps.colorize(mono, black=PALETTE["bg_deep"], white=PALETTE["mint"], blackpoint=12, whitepoint=238).convert("RGB")
    # Halftone dots soften gradients while preserving recognizable facial detail.
    small = image.resize((PORTRAIT_WIDTH//3, PORTRAIT_HEIGHT//3), Image.Resampling.LANCZOS).convert("L")
    dots = Image.new("L", image.size, 0)
    dd = ImageDraw.Draw(dots)
    for y in range(small.height):
        for x in range(small.width):
            value = small.getpixel((x, y))
            radius = 1 if value > 92 else 0
            if radius:
                cx, cy = x*3+1, y*3+1
                dd.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=35)
    overlay = Image.new("RGB", image.size, hex_to_rgb(PALETTE["emerald"]))
    image = Image.composite(overlay, image, dots)
    canvas = Image.new("RGB", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), hex_to_rgb(PALETTE["bg_deep"]))
    canvas.paste(image, (18, 18))
    draw = ImageDraw.Draw(canvas)
    for y in range(24, PORTRAIT_HEIGHT-20, 8):
        draw.line((20, y, PORTRAIT_WIDTH-20, y), fill=hex_to_rgb(PALETTE["bg_deep"]), width=1)
    draw.rounded_rectangle((8, 8, PORTRAIT_WIDTH-9, PORTRAIT_HEIGHT-9), 18, outline=hex_to_rgb(PALETTE["emerald_deep"]), width=2)
    draw.text((24, PORTRAIT_HEIGHT-30), "SULKHLAN  /  PROFILE SIGNAL", font=_font(11), fill=hex_to_rgb(PALETTE["mint"]))
    meta = PngImagePlugin.PngInfo(); meta.add_text("PortraitSource", "true")
    canvas.save(output, pnginfo=meta, optimize=True)
    frames = []
    for frame in range(12):
        cel = canvas.copy(); cd = ImageDraw.Draw(cel)
        sweep_y = 28 + round((PORTRAIT_HEIGHT-56) * frame / 11)
        cd.line((20, sweep_y, PORTRAIT_WIDTH-20, sweep_y), fill=hex_to_rgb(PALETTE["emerald"]), width=2)
        frames.append(cel)
    (directory / "profile-portrait.gif").write_bytes(_gif(frames, 110))
    return True


def motion_assets(directory: Path, data: dict[str, Any]) -> None:
    for mode, suffix in (("dark", ""), ("light", "-light")):
        c = card_params(mode)
        # Hero motion draws only a quiet moving signal dot over the same complete design.
        background = Image.new("RGB", (WIDTH, HERO_HEIGHT), hex_to_rgb(c["bg"]))
        d = ImageDraw.Draw(background)
        d.rounded_rectangle((1, 1, WIDTH-2, HERO_HEIGHT-2), PANEL_RADIUS, fill=hex_to_rgb(c["panel"]), outline=hex_to_rgb(c["border"]), width=2)
        d.text((42, 48), "COMPUTER SCIENCE / DATA SCIENCE / SOFTWARE", font=_font(13), fill=hex_to_rgb(c["accent"]))
        d.text((40, 80), NAME, font=_font(42), fill=hex_to_rgb(c["text"]))
        d.text((44, 132), "Practical software, informed by data and AI.", font=_font(17), fill=hex_to_rgb(c["silver"]))
        d.text((44, 165), "LEARN / BUILD / MEASURE / IMPROVE", font=_font(13), fill=hex_to_rgb(c["muted"]))
        for i, label in enumerate(("BUILD", "OBSERVE", "REFINE")):
            x = 540 + i*108
            d.rounded_rectangle((x-43, 115, x+43, 182), 10, fill=hex_to_rgb(c["panel_alt"]), outline=hex_to_rgb(c["border"]))
            d.text((x-20, 139), label, font=_font(12), fill=hex_to_rgb(c["text"]))
        for x in range(34, WIDTH-34, 30): d.line((x, 215, x, 219), fill=hex_to_rgb(c["grid"]))
        d.text((42, 230), "CURRENT THREAD / SYSTEMS · DATA · APPLIED AI", font=_font(12), fill=hex_to_rgb(c["accent"]))
        (directory / f"hero-motion{suffix}.gif").write_bytes(_gif([background.copy() if frame == 0 else _hero_frame(background, frame, c) for frame in range(HERO_FRAMES)]))
        # Typing line has complete first state and rotates through verified focus phrases.
        type_frames = []
        for line in TYPE_LINES:
            for count in range(1, len(line)+1, max(1, len(line)//12)):
                frame = Image.new("RGB", (WIDTH, 48), hex_to_rgb(c["bg"]))
                fd = ImageDraw.Draw(frame); fd.text((14, 14), "> " + line[:count] + ("▌" if count < len(line) else ""), font=_font(17), fill=hex_to_rgb(c["accent"]))
                type_frames.append(frame)
        type_frames.insert(0, Image.new("RGB", (WIDTH,48), hex_to_rgb(c["bg"])))
        td=ImageDraw.Draw(type_frames[0]); td.text((14,14), "> "+TYPE_LINES[0], font=_font(17), fill=hex_to_rgb(c["accent"]))
        (directory / f"typing{suffix}.gif").write_bytes(_gif(type_frames, 180))
        lineframes=[]
        for i in range(18):
            f=Image.new("RGB", (WIDTH,DIVIDER_HEIGHT), hex_to_rgb(c["bg"])); fd=ImageDraw.Draw(f)
            fd.line((0,19,WIDTH,19), fill=hex_to_rgb(c["border"]), width=1)
            fd.line((0,19,WIDTH,19), fill=hex_to_rgb(c["accent"]), width=1)
            x=14+round((WIDTH-28)*i/17); fd.ellipse((x-7,12,x+7,26), fill=hex_to_rgb(c["accent_deep"])); fd.ellipse((x-3,16,x+3,22), fill=hex_to_rgb(c["mint"]))
            lineframes.append(f)
        (directory / f"signal{suffix}.gif").write_bytes(_gif(lineframes, 85))
        # Data bars stay fixed; only a subtle focus marker moves over the cached sample.
        act=Image.new("RGB", (WIDTH,ACTIVITY_HEIGHT), hex_to_rgb(c["bg"])); ad=ImageDraw.Draw(act)
        ad.rounded_rectangle((1,1,WIDTH-2,ACTIVITY_HEIGHT-2),15,fill=hex_to_rgb(c["panel"]),outline=hex_to_rgb(c["border"]))
        ad.text((22,18),"PUBLIC REPOSITORY SIGNAL / CACHED SAMPLE",font=_font(14),fill=hex_to_rgb(c["accent"]))
        counts=list(data.get("activity_weeks",[0]*12))[:12]; maximum=max(counts or [0]) or 1
        for j,count in enumerate(counts):
            x=34+j*63; h=max(2,round(80*count/maximum)); ad.rounded_rectangle((x,165-h,x+25,165),3,fill=hex_to_rgb(c["accent"] if count else c["border"]))
        ad.line((26,166,806,166),fill=hex_to_rgb(c["grid"]))
        af=[]
        for i in range(12):
            fr=act.copy(); x=36+i*66; ImageDraw.Draw(fr).ellipse((x-4,157,x+4,173),fill=hex_to_rgb(c["mint"])); af.append(fr)
        (directory / f"activity-motion{suffix}.gif").write_bytes(_gif(af, 140))


def _hero_frame(image: Image.Image, frame: int, c: dict[str,str]) -> Image.Image:
    result=image.copy(); d=ImageDraw.Draw(result); x=500+round(286*frame/(HERO_FRAMES-1)); d.ellipse((x-8,148,x+8,164),fill=hex_to_rgb(c["accent_deep"])); d.ellipse((x-3,153,x+3,159),fill=hex_to_rgb(c["mint"])); return result


def skills(mode: str="dark") -> str:
    c=card_params(mode); rows=[]
    groups=[("PROGRAMMING", "TypeScript  /  Python  /  Java (learning)"),("AI SYSTEMS", "Gemini  /  MCP  /  LiveKit  /  Qdrant"),("BACKEND + DATA", "Flask  /  Hono  /  Express  /  SQLite  /  PostgreSQL"),("FRONTEND + TOOLS", "React  /  Vite  /  GitHub Actions"),("INTEGRATION", "Windows telemetry  /  REST APIs  /  CI workflows")]
    for i,(label,items) in enumerate(groups):
        y=58+i*49
        rows.append(f'<rect x="18" y="{y-20}" width="794" height="38" rx="8" fill="{c["panel"]}" stroke="{c["border"]}"/><circle cx="36" cy="{y-1}" r="4" fill="{c["accent"]}"/><text x="52" y="{y+3}" fill="{c["accent"]}" font-family="{MONO_FONT}" font-size="9" letter-spacing="1">{label}</text><text x="244" y="{y+3}" fill="{c["text"]}" font-size="12">{html.escape(items)}</text>')
    return _document(WIDTH,SKILLS_HEIGHT,"Hands-on engineering map","Evidence-based technical categories with Java marked as learning.",f'<rect width="830" height="{SKILLS_HEIGHT}" rx="15" fill="{c["bg"]}" stroke="{c["border"]}"/>'+''.join(rows))


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


def write_assets(directory: Path, data: dict[str, Any]) -> bool:
    """Write static fallbacks and self-hosted animated assets; return portrait validity."""
    directory.mkdir(parents=True, exist_ok=True)
    renderers = {
        "hero": lambda mode: hero(mode),
        "typing": lambda mode: typing(mode),
        "divider": lambda mode: divider(mode),
        "project-landscape": lambda mode: landscape(mode, PROJECTS),
        "activity": lambda mode: activity(data, mode),
        "language-stats": lambda mode: languages(data, mode),
        "skills": lambda mode: skills(mode),
    }
    for name, renderer in renderers.items():
        for mode, suffix in (("dark", ""), ("light", "-light")):
            (directory / f"{name}{suffix}.svg").write_text(renderer(mode), encoding="utf-8", newline="\n")
    available = portrait(directory)
    motion_assets(directory, data)
    return available

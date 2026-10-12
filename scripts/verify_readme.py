"""Verify the generated profile's content, assets, and offline behavior."""
from __future__ import annotations

import datetime as dt
import hashlib
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme
import build as builder
from build import END, README_FILE, START


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Verification failed: {message}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_gif(path: Path) -> None:
    with Image.open(path) as image:
        require(image.format == "GIF" and image.size == (theme.WIDTH, 52), f"Unexpected GIF dimensions/format: {path.name}")
        require(image.n_frames >= 40 and image.n_frames <= 240, f"Unexpected frame count: {path.name} ({image.n_frames})")
        require(image.info.get("loop") == 0, f"GIF does not loop: {path.name}")
        require(path.stat().st_size < 65_536, f"GIF exceeds 64 KiB budget: {path.name}")
        for index in (0, image.n_frames // 2, image.n_frames - 1):
            image.seek(index); image.convert("RGB").load()


def check_cache_preservation() -> None:
    original = builder.request_json
    cached = {"followers": 4, "profile_available": True, "repos": [{"name": "cache-item", "html_url": "https://example.invalid"}], "languages": {"Python": 47}, "events_available": True, "activity_weeks": [0]*11+[2], "public_push_event_count": 2, "last_successful_refresh_utc": "2026-01-02T03:04:05Z"}
    try:
        builder.request_json = lambda *a, **k: (_ for _ in ()).throw(OSError("simulated offline"))
        result = builder.fetch_data(cached)
        for key, value in cached.items():
            require(result.get(key) == value, f"API outage changed cached {key}")
    finally:
        builder.request_json = original


def check_markers() -> None:
    old = builder.README_FILE
    try:
        with tempfile.TemporaryDirectory() as folder:
            builder.README_FILE = Path(folder) / "README.md"
            builder.README_FILE.write_text(f"Handwritten intro\n{START}\nold\n{END}\nHandwritten footer\n", encoding="utf-8")
            result = builder.render_readme(builder._read_data(), portrait_available=True)
            require(result.startswith(f"Handwritten intro\n{START}\n") and result.endswith(f"{END}\nHandwritten footer\n"), "Manual README content outside markers changed")
    finally:
        builder.README_FILE = old


def verify() -> None:
    theme.validate_theme()
    readme = README_FILE.read_text(encoding="utf-8")
    require(readme.count(START) == readme.count(END) == 1, "README generated markers are unbalanced")
    mojibake = any(marker in readme for marker in (chr(0x00c3), chr(0x00c2), chr(0x00e2) + chr(0x20ac)))
    require(chr(0xfffd) not in readme and not mojibake, "README contains mojibake")
    require("## About" in readme and 'width="34%"' in readme and 'width="66%"' in readme, "Portrait and profile facts need the two-column layout")
    require("## Experience" in readme and theme.EXPERIENCE["employer"] in readme and theme.EXPERIENCE["duration"] in readme, "Provided experience is missing")
    require(theme.EDUCATION in readme and theme.EDUCATION_DETAIL in readme and all(item in readme for item in theme.COURSEWORK), "Provided education facts are incomplete")
    require(readme.count("type=\"image/gif\"") == 2, "README should contain dark/light sources for the single typing animation")
    require("profile-portrait.gif" not in readme and "assets/profile-photo-source.jpg" not in readme, "Private or obsolete portrait asset is referenced")
    require(not (ROOT / "assets/profile-photo.jpeg").exists(), "Raw source photo must not be published")
    require(theme.PORTRAIT_SOURCE.split("/")[-1] in (ROOT/".gitignore").read_text(encoding="utf-8"), "Source photo is not ignored")
    for project in theme.PROJECTS:
        require(f"{theme.PROFILE_URL}/{project['repo']}" in readme, f"Project link missing: {project['repo']}")
    require("https://ai.studio/" not in readme, "A login-gated demo should not be linked")

    imgs = re.findall(r"<img\b[^>]*>", readme, re.I)
    require(bool(imgs), "README has no images")
    for tag in imgs:
        require(re.search(r'\balt="[^"]+"', tag), f"Image lacks alt text: {tag}")
        src = re.search(r'\bsrc="([^"]+)"', tag).group(1)
        if src.startswith("https://skillicons.dev/icons?"):
            anchor_start = readme.rfind("<a ", 0, readme.find(tag))
            anchor_end = readme.find("</a>", readme.find(tag))
            require(anchor_start >= 0 and anchor_end >= 0, "External technology icon must be linked")
            anchor = readme[anchor_start:anchor_end]
            icon = re.search(r"[?&]i=([^&]+)", src).group(1)
            allowed = {entry[1] for _, group in theme.SKILL_GROUPS for entry in group}
            require(icon in allowed and re.search(r'href="https://', anchor), f"Unapproved or unlinked Skill Icon: {icon}")
        else:
            require(src.startswith("assets/") and (ROOT/src).is_file(), f"Missing local image: {src}")
    external_sources = re.findall(r'<source\b[^>]*srcset="([^"]+)"', readme, re.I)
    for source in external_sources:
        require(source.startswith("assets/") and (ROOT/source).is_file(), f"Missing picture source: {source}")

    gifs = sorted(p.name for p in (ROOT/"assets").glob("*.gif"))
    require(gifs == ["typing-light.gif", "typing.gif"], f"Unexpected GIF assets: {gifs}")
    for name in gifs:
        check_gif(ROOT/"assets"/name)
    for path in (ROOT/"assets").glob("*.svg"):
        root = ET.parse(path).getroot()
        require(root.tag.endswith("svg") and int(root.attrib.get("width", "0")) <= theme.WIDTH, f"Invalid SVG size/root: {path.name}")
        raw = path.read_text(encoding="utf-8")
        require(not re.search(r"<\s*script\b|javascript:|on(?:load|error)\s*=|<\s*(?:animate|set)\b|@import", raw, re.I), f"Unsupported SVG content: {path.name}")
    for stem in ("hero", "typing", "divider", "activity", "language-stats", "contribution-art"):
        for suffix in (".svg", "-light.svg"):
            require((ROOT/"assets"/f"{stem}{suffix}").is_file(), f"Static fallback missing: {stem}{suffix}")
    with Image.open(ROOT/theme.PORTRAIT_PNG) as portrait:
        require(portrait.size == (theme.PORTRAIT_WIDTH, theme.PORTRAIT_HEIGHT), "Portrait dimensions are wrong")
        require(portrait.info.get("PortraitSource") == "true", "Published portrait was not derived from the provided source")

    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", readme):
        target = match.group(1).split()[0]
        if not target.startswith(("https://", "http://", "mailto:", "#")):
            require((ROOT/target).exists(), f"README link target does not exist: {target}")
    headings = {re.sub(r"[^a-z0-9 -]", "", h.lower()).replace(" ", "-") for h in re.findall(r"^#{1,6}\s+(.+)$", readme, re.M)}
    for anchor in re.findall(r"(?<!!)\[[^\]]+\]\(#([^)]+)\)", readme):
        require(anchor in headings, f"Internal anchor has no heading: #{anchor}")
    data=builder._read_data(); stamp=data.get("last_successful_refresh_utc")
    if stamp:
        parsed=dt.datetime.fromisoformat(stamp.replace("Z","+00:00"))
        require(parsed.tzinfo == dt.timezone.utc and builder._refresh_label(data) in readme, "Refresh timestamp is invalid or missing")
    try:
        import yaml
        for name in ("refresh.yml", "verify.yml"):
            yaml.safe_load((ROOT/".github"/"workflows"/name).read_text(encoding="utf-8"))
    except ImportError as exc:
        raise SystemExit("Verification failed: PyYAML is required to validate workflow YAML") from exc
    refresh=(ROOT/".github/workflows/refresh.yml").read_text(encoding="utf-8")
    verify_flow=(ROOT/".github/workflows/verify.yml").read_text(encoding="utf-8")
    require("git diff --cached --quiet" in refresh and "git add README.md assets/*.svg assets/*.gif assets/*.png assets/profile-data.json" in refresh, "Refresh workflow staging/no-op guard is missing")
    require("contents: read" in verify_flow, "Verification workflow must be read-only")

    outputs=[README_FILE, *(ROOT/"assets").glob("*.svg"), *(ROOT/"assets").glob("*.gif"), ROOT/theme.PORTRAIT_PNG]
    before={p:digest(p) for p in outputs}
    old=(builder.ROOT,builder.DATA_FILE,builder.README_FILE)
    try:
        builder.build(offline=True)
        require(before == {p:digest(p) for p in outputs}, "Offline build is not reproducible")
        with tempfile.TemporaryDirectory() as folder:
            temp=Path(folder); builder.ROOT=temp; builder.DATA_FILE=temp/"assets/profile-data.json"; builder.README_FILE=temp/"README.md"
            builder.build(offline=True)
            fallback=(temp/"README.md").read_text(encoding="utf-8")
            require("Portrait placeholder" in fallback, "Missing-photo fallback is not described")
            for svg in (temp/"assets").glob("*.svg"): ET.parse(svg)
            with Image.open(temp/"assets/profile-portrait.png") as image:
                require(image.info.get("PortraitSource") == "placeholder", "Missing photo fallback image was not generated")
            check_gif(temp/"assets/typing.gif")
    finally:
        builder.ROOT,builder.DATA_FILE,builder.README_FILE=old
    check_cache_preservation(); check_markers()
    print("Verified README content and links, photo privacy, icons/alt text, SVGs, single-loop GIF size/frames, workflows, theme contrast, cache preservation, no-photo fallback, marker preservation, and offline reproducibility.")


if __name__ == "__main__":
    verify()

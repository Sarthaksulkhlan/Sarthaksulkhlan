"""Verify generated assets, README references, cached fallbacks, and workflows."""
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


def fail(message: str) -> None:
    raise SystemExit(f"Verification failed: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_gif(path: Path, minimum_frames: int = 2) -> None:
    try:
        with Image.open(path) as image:
            if image.format != "GIF" or image.size[0] > 900 or image.n_frames < minimum_frames:
                fail(f"{path.name} is not a valid multi-frame GIF")
            image.seek(0)
            image.convert("RGB").load()
            image.seek(image.n_frames - 1)
            image.convert("RGB").load()
            if image.info.get("loop") != 0:
                fail(f"{path.name} is not set to loop")
    except (OSError, EOFError) as exc:
        fail(f"Cannot decode {path.name}: {exc}")


def check_yaml() -> None:
    try:
        import yaml
        for name in ("refresh.yml", "verify.yml"):
            yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"))
    except ImportError:
        fail("PyYAML is required for workflow syntax validation in this verification environment")
    except Exception as exc:
        fail(f"Workflow YAML is invalid: {exc}")


def check_cache_preservation() -> None:
    original = builder.request_json
    cached = {"repos": [{"name": "cache-item", "html_url": "https://example.invalid"}], "languages": {"Python": 47}, "events_available": True, "activity_weeks": [0]*11+[2], "public_push_event_count": 2, "last_successful_refresh_utc": "2026-01-02T03:04:05Z"}
    try:
        builder.request_json = lambda *a, **k: (_ for _ in ()).throw(OSError("simulated offline"))
        refreshed = builder.fetch_data(cached)
        for key, value in cached.items():
            if refreshed.get(key) != value:
                fail(f"Simulated API outage changed cached {key}")
    finally:
        builder.request_json = original


def check_manual_content() -> None:
    old = builder.README_FILE
    try:
        with tempfile.TemporaryDirectory() as temp:
            builder.README_FILE = Path(temp) / "README.md"
            builder.README_FILE.write_text(f"Handwritten intro\n{START}\nold\n{END}\nHandwritten footer\n", encoding="utf-8")
            generated = builder.render_readme(builder._read_data(), portrait_available=True)
            if not generated.startswith(f"Handwritten intro\n{START}\n") or not generated.endswith(f"{END}\nHandwritten footer\n"):
                fail("Manual README content outside generated markers was changed")
    finally:
        builder.README_FILE = old


def verify() -> None:
    theme.validate_theme()
    readme = README_FILE.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        fail("README generated markers are unbalanced")
    # Verify every image in HTML and Markdown resolves locally; every image has alt text.
    image_refs = re.findall(r'<(?:img|source)\b[^>]*(?:src|srcset)="([^"]+)"[^>]*>', readme, re.I)
    image_tags = re.findall(r'<img\b[^>]*>', readme, re.I)
    for tag in image_tags:
        if not re.search(r'\balt="[^" ]', tag):
            fail(f"README image lacks descriptive alt text: {tag}")
    for target in image_refs:
        for item in target.split(","):
            path = item.strip().split()[0]
            if not path.startswith("assets/") or not (ROOT / path).is_file():
                fail(f"README image target is missing or external: {path}")
    if "assets/profile-photo.jpeg" in readme or (ROOT / "assets/profile-photo.jpeg").exists():
        fail("Raw source photograph must not be published")
    if "assets/profile-photo-source.jpg" in readme:
        fail("Private source photo path must not be exposed in README")
    if not (ROOT / ".gitignore").read_text(encoding="utf-8").__contains__(theme.PORTRAIT_SOURCE.split("/")[-1]):
        fail("Source portrait is not ignored by Git")
    if "## Who I am" not in readme or "<td width=\"32%\"" not in readme or "<td width=\"68%\"" not in readme:
        fail("Who I am needs the portrait and information two-column layout")
    if "<details>" not in readme or "How this profile is built" not in readme:
        fail("Expandable content and build documentation navigation are required")
    for project in theme.PROJECTS:
        if f"{theme.PROFILE_URL}/{project['repo']}" not in readme:
            fail(f"Missing project repository link: {project['repo']}")
    if not (ROOT / theme.PORTRAIT_PNG).is_file():
        fail("Derived static portrait is missing")
    with Image.open(ROOT / theme.PORTRAIT_PNG) as portrait:
        if portrait.size != (theme.PORTRAIT_WIDTH, theme.PORTRAIT_HEIGHT):
            fail("Portrait dimensions do not match theme settings")
        if portrait.info.get("PortraitSource") == "true" and not (ROOT / theme.PORTRAIT_SOURCE).is_file():
            # The local private source may be omitted after the asset is generated and committed.
            pass
    gifs = ["hero-motion.gif", "hero-motion-light.gif", "typing.gif", "typing-light.gif", "signal.gif", "signal-light.gif", "profile-portrait.gif", "activity-motion.gif", "activity-motion-light.gif"]
    for name in gifs:
        check_gif(ROOT / "assets" / name)
    svg_paths = list((ROOT / "assets").glob("*.svg"))
    for path in svg_paths:
        root = ET.parse(path).getroot()
        if not root.tag.endswith("svg") or int(root.attrib.get("width", "0")) > 830:
            fail(f"Invalid SVG root or width in {path.name}")
        raw = path.read_text(encoding="utf-8")
        if re.search(r"<\s*script\b|javascript:|on(?:load|error)\s*=|<\s*(?:animate|set)\b|@import", raw, re.I):
            fail(f"Unsupported or unsafe SVG content in {path.name}")
    for item in ("hero.svg", "hero-light.svg", "typing.svg", "typing-light.svg", "skills.svg", "skills-light.svg", "activity.svg", "activity-light.svg", "divider.svg", "divider-light.svg"):
        if not (ROOT / "assets" / item).is_file():
            fail(f"Static fallback missing: {item}")
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", readme):
        target = match.group(1).split()[0]
        if not target.startswith(("https://", "http://", "mailto:", "#")) and not (ROOT / target).exists():
            fail(f"README link target does not exist: {target}")
    headings = {re.sub(r"[^a-z0-9 -]", "", h.lower()).replace(" ", "-") for h in re.findall(r"^#{1,6}\s+(.+)$", readme, re.M)}
    for target in re.findall(r"(?<!!)\[[^\]]+\]\(#([^)]+)\)", readme):
        if target not in headings:
            fail(f"Internal anchor has no matching heading: #{target}")
    data = builder._read_data()
    stamp = data.get("last_successful_refresh_utc")
    if stamp:
        parsed = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed.tzinfo != dt.timezone.utc or builder._refresh_label(data) not in readme:
            fail("Successful refresh timestamp is invalid or missing from README")
    check_yaml()
    refresh = (ROOT / ".github/workflows/refresh.yml").read_text(encoding="utf-8")
    verify_flow = (ROOT / ".github/workflows/verify.yml").read_text(encoding="utf-8")
    if "git diff --cached --quiet" not in refresh or "git add README.md assets/*.svg assets/*.gif assets/*.png assets/profile-data.json" not in refresh:
        fail("Refresh workflow must stage all generated outputs and skip empty commits")
    if "contents: read" not in verify_flow:
        fail("Verification workflow should remain read-only")
    before = {path: sha(path) for path in [README_FILE, *svg_paths, *(ROOT / "assets" / x for x in gifs)]}
    old_root, old_data, old_readme = builder.ROOT, builder.DATA_FILE, builder.README_FILE
    try:
        builder.build(offline=True)
        after = {path: sha(path) for path in before}
        if before != after:
            fail("Offline generation is not reproducible")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); builder.ROOT=root; builder.DATA_FILE=root/"assets/profile-data.json"; builder.README_FILE=root/"README.md"
            builder.build(offline=True)
            fallback = (root/"README.md").read_text(encoding="utf-8")
            if "PHOTO SOURCE REQUIRED" not in (root/"assets/profile-portrait.png").read_bytes().decode("latin1") and "PHOTO SOURCE REQUIRED" not in fallback:
                # Raster text is not machine-readable; README must explicitly identify the placeholder source.
                if "Portrait placeholder" not in fallback: fail("Missing-photo fallback is unclear")
            for svg in (root/"assets").glob("*.svg"): ET.parse(svg)
            check_gif(root/"assets/signal.gif")
    finally:
        builder.ROOT, builder.DATA_FILE, builder.README_FILE = old_root, old_data, old_readme
    check_cache_preservation()
    check_manual_content()
    print("Verified GitHub image paths/alt text, two-column layout, anchors, project links, details, theme assets, SVG XML, animated GIF frames/loops, YAML, cache outage behavior, missing-photo fallback, marker preservation, and offline reproducibility.")


if __name__ == "__main__":
    verify()

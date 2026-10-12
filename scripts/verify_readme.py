"""Validate generated profile files, safe SVGs, links, and offline reproducibility."""
from __future__ import annotations

import hashlib
import datetime as dt
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme
import build as builder
from build import END, README_FILE, START, build


def fail(message: str) -> None:
    raise SystemExit(f"Verification failed: {message}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_missing_optional_data() -> None:
    """Build in isolation without a cache and require clear empty-data fallbacks."""
    original = (builder.ROOT, builder.DATA_FILE, builder.README_FILE)
    try:
        with tempfile.TemporaryDirectory(prefix="profile-verify-") as temporary:
            root = Path(temporary)
            builder.ROOT = root
            builder.DATA_FILE = root / "assets" / "profile-data.json"
            builder.README_FILE = root / "README.md"
            builder.build(offline=True)
            activity_svg = (root / "assets" / "activity.svg").read_text(encoding="utf-8")
            language_svg = (root / "assets" / "language-stats.svg").read_text(encoding="utf-8")
            if "Public event sample unavailable" not in activity_svg:
                fail("Missing public activity data lacks an unavailable fallback")
            if "Language totals are unavailable in the current cache" not in language_svg:
                fail("Missing language data lacks an unavailable fallback")
            if "fake" in activity_svg.lower() or "fake" in language_svg.lower():
                fail("Fallback visual contains fabricated sample data")
            for path in (root / "assets").glob("*.svg"):
                ET.parse(path)
    finally:
        builder.ROOT, builder.DATA_FILE, builder.README_FILE = original


def verify_network_failure_preserves_cache() -> None:
    """Simulate unavailable API responses and ensure cached values survive."""
    original_request = builder.request_json
    cache = {
        "repos": [{"name": "cached-project", "html_url": "https://example.invalid/repo"}],
        "languages": {"Python": 42},
        "events_available": True,
        "activity_weeks": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        "public_push_event_count": 3,
        "last_successful_refresh_utc": "2026-01-02T03:04:05Z",
    }
    try:
        builder.request_json = lambda *args, **kwargs: (_ for _ in ()).throw(OSError("simulated offline"))
        refreshed = builder.fetch_data(cache)
        for key, value in cache.items():
            if refreshed.get(key) != value:
                fail(f"API failure replaced cached {key} data")
    finally:
        builder.request_json = original_request


def verify_manual_readme_content_is_preserved() -> None:
    """Ensure regeneration changes only content inside the generated markers."""
    original_readme = builder.README_FILE
    try:
        with tempfile.TemporaryDirectory(prefix="profile-markers-") as temporary:
            builder.README_FILE = Path(temporary) / "README.md"
            builder.README_FILE.write_text(f"Manual intro\n{START}\nold content\n{END}\nManual footer\n", encoding="utf-8")
            result = builder.render_readme(builder._read_data())
            if not result.startswith(f"Manual intro\n{START}\n") or not result.endswith(f"{END}\nManual footer\n"):
                fail("README regeneration changed content outside generated markers")
    finally:
        builder.README_FILE = original_readme


def verify_refresh_workflow_guard() -> None:
    """Require a write scope only for refresh and a nonempty-diff commit guard."""
    refresh = (ROOT / ".github" / "workflows" / "refresh.yml").read_text(encoding="utf-8")
    verify_workflow = (ROOT / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
    if "permissions:\n  contents: write" not in refresh or "git diff --cached --quiet" not in refresh:
        fail("Refresh workflow must have explicit write permission and skip empty commits")
    if "permissions:\n  contents: read" not in verify_workflow:
        fail("Verification workflow should use read-only repository permissions")


def verify() -> None:
    theme.validate_theme()
    readme = README_FILE.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        fail("README must have one balanced generated marker pair")
    cached_data = builder._read_data()
    refresh_stamp = cached_data.get("last_successful_refresh_utc")
    if refresh_stamp:
        try:
            parsed_stamp = dt.datetime.fromisoformat(refresh_stamp.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            fail("last_successful_refresh_utc must be a valid ISO timestamp")
        if parsed_stamp.tzinfo != dt.timezone.utc or builder._refresh_label(cached_data) not in readme:
            fail("Successful refresh timestamp must be UTC and displayed in the README")
    expected = {"hero": 1, "divider": 2, "project-landscape": 1, "activity": 1, "language-stats": 1}
    image_sources = re.findall(r'<source\s+media="([^"]+)"\s+srcset="([^"]+)"\s*/?>', readme)
    image_fallbacks = re.findall(r'<img\s+src="([^"]+)"\s+alt="([^"]*)"\s*/?>', readme)
    if len(image_sources) != sum(expected.values()) * 2 or len(image_fallbacks) != sum(expected.values()):
        fail("README must use a dark/light source pair and fallback image for each asset family")
    for _, target in image_sources:
        if not (ROOT / target).is_file():
            fail(f"README theme image target does not exist: {target}")
    for target, alt in image_fallbacks:
        if not alt.strip():
            fail(f"README image is missing alt text: {target}")
        if not (ROOT / target).is_file():
            fail(f"README fallback image target does not exist: {target}")
    for asset, count in expected.items():
        dark = [item for media, item in image_sources if media == theme.DARK_MODE_MEDIA]
        light = [item for media, item in image_sources if media == theme.LIGHT_MODE_MEDIA]
        if dark.count(f"assets/{asset}.svg") != count or light.count(f"assets/{asset}-light.svg") != count:
            fail(f"README does not select the correct light/dark {asset} variants")
    paths = [ROOT / "assets" / f"{name}{suffix}.svg" for name in expected for suffix in ("", "-light")]
    for path in paths:
        if not path.is_file():
            fail(f"Required generated asset missing: {path.relative_to(ROOT)}")
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            fail(f"Invalid SVG XML in {path.name}: {exc}")
        if not root.tag.endswith("svg"):
            fail(f"{path.name} root is not SVG")
        if int(root.attrib.get("width", "0")) > 830:
            fail(f"{path.name} is wider than 830px")
        raw = path.read_text(encoding="utf-8")
        if re.search(r"<\s*script\b|javascript:|on(?:load|error)\s*=|<\s*(?:animate|set)\b|animation\s*:", raw, re.I):
            fail(f"Unsafe or unsupported animation markup in {path.name}")
        if re.search(r"(?:href\s*=\s*['\"]?(?:https?:)?//|url\(\s*['\"]?(?:https?:)?//|@import\s+)", raw, re.I):
            fail(f"External reference found in {path.name}")
        if "<style" in raw.lower():
            fail(f"{path.name} depends on embedded CSS that GitHub may sanitize")
    for mode in ("dark", "light"):
        for color in theme.card_params(mode).values():
            if not any(color in path.read_text(encoding="utf-8") for path in paths):
                fail(f"Theme color {color} for {mode} mode is not represented in generated assets")
    for project in theme.PROJECTS:
        expected_url = f"{theme.PROFILE_URL}/{project['repo']}"
        if expected_url not in readme:
            fail(f"Selected project link is missing or incorrect: {project['name']}")
    if any(token in readme.lower() for token in ("friday vig", "gold palette", "top engineer")):
        fail("README contains reference-only identity or an unsupported status claim")
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", readme):
        target = match.group(1).split()[0]
        if not target.startswith(("https://", "http://", "mailto:", "#")) and not (ROOT / target).exists():
            fail(f"README link target does not exist: {target}")
    before = {path: digest(path) for path in [README_FILE, *paths]}
    build(offline=True)
    after = {path: digest(path) for path in before}
    if before != after:
        fail("Offline build is not reproducible")
    verify_missing_optional_data()
    verify_network_failure_preserves_cache()
    verify_manual_readme_content_is_preserved()
    verify_refresh_workflow_guard()
    print("Verified theme, README markers/paths/alt text, static SVG safety, theme selection, reproducible build, and missing-data/network fallbacks.")


if __name__ == "__main__":
    verify()

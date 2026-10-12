"""Fetch public GitHub metadata and build the generated profile README/assets."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme
from build_assets import write_assets

DATA_FILE = ROOT / "assets" / "profile-data.json"
README_FILE = ROOT / "README.md"
START = "<!-- PROFILE:GENERATED:START -->"
END = "<!-- PROFILE:GENERATED:END -->"
API = "https://api.github.com"


def request_json(url: str, token: str | None = None) -> Any:
    """Fetch a GitHub public REST resource with bounded timeout and useful errors."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-builder/1.0", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"GitHub returned HTTP {response.status} for {url}")
        return json.loads(response.read().decode("utf-8"))


def _valid_repo_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("Repository response must be a list")
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not isinstance(item.get("html_url"), str):
            raise ValueError("Repository response contains an invalid repository entry")
        if item.get("homepage") is not None and not isinstance(item.get("homepage"), str):
            raise ValueError(f"Invalid homepage metadata for {item['name']}")
        stars = item.get("stargazers_count", 0)
        if not isinstance(stars, int) or isinstance(stars, bool) or stars < 0:
            raise ValueError(f"Invalid star count for {item['name']}")
    return value


def _week_counts(events: Any, now: dt.datetime) -> list[int]:
    counts = [0] * 12
    if not isinstance(events, list):
        return counts
    for event in events:
        if not isinstance(event, dict) or event.get("type") != "PushEvent":
            continue
        try:
            created = dt.datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            age_days = max(0, (now - created).days)
            index = min(11, age_days // 7)
            counts[11 - index] += 1
        except (KeyError, TypeError, ValueError):
            continue
    return counts


def fetch_data(old: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    """Refresh independently validated public datasets, retaining cache on errors."""
    now = dt.datetime.now(dt.timezone.utc)
    result = dict(old)
    result.setdefault("repos", [])
    result.setdefault("languages", {})
    result.setdefault("events_available", False)
    result.setdefault("activity_weeks", [0] * 12)
    result.setdefault("repos_available", "public_repo_count" in old)
    result.setdefault("languages_available", bool(old.get("languages")))
    failures: list[str] = []
    try:
        repos = _valid_repo_list(request_json(f"{API}/users/{theme.USERNAME}/repos?per_page=100&type=owner&sort=updated", token))
        repos = [repo for repo in repos if not repo.get("fork") and repo.get("name") != theme.USERNAME]
        result["repos"] = [{key: repo.get(key) for key in ("name", "html_url", "description", "language", "homepage", "updated_at", "stargazers_count")} for repo in repos]
        result["public_repo_count"] = len(repos)
        result["public_repo_stars"] = sum(repo.get("stargazers_count", 0) for repo in repos)
        result["repos_available"] = True
        lang_totals: dict[str, int] = {}
        language_failures_before = len(failures)
        for repo in repos:
            try:
                languages = request_json(f"{API}/repos/{theme.USERNAME}/{repo['name']}/languages", token)
                if not isinstance(languages, dict):
                    raise ValueError("Language response must be an object")
                for name, amount in languages.items():
                    if not isinstance(name, str) or not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
                        raise ValueError(f"Invalid language total for {repo['name']}")
                    lang_totals[name] = lang_totals.get(name, 0) + amount
            except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
                failures.append(f"languages:{repo['name']}:{exc}")
        if len(failures) == language_failures_before:
            result["languages"] = lang_totals
            result["languages_available"] = bool(lang_totals)
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        failures.append(f"repos:{exc}")
    try:
        events = request_json(f"{API}/users/{theme.USERNAME}/events/public?per_page=100", token)
        if isinstance(events, list):
            pushes = [event for event in events if isinstance(event, dict) and event.get("type") == "PushEvent"]
            result["activity_weeks"] = _week_counts(pushes, now)
            result["public_push_event_count"] = len(pushes)
            result["events_available"] = True
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        failures.append(f"events:{exc}")
    if failures:
        print("GitHub refresh incomplete; retaining cached values where available: " + "; ".join(failures), file=sys.stderr)
    else:
        result["last_successful_refresh_utc"] = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    result["data_note"] = "Original public repositories exclude forks and this profile repository. Languages use GitHub-reported bytes. Activity groups only PushEvents in the latest public user-event sample (up to 100 events), not complete contribution history."
    result.pop("events", None)
    return result


def _read_data() -> dict[str, Any]:
    if not DATA_FILE.exists():
        return {}
    parsed = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Cached profile data must be a JSON object")
    return parsed


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Respect the platform's text newline so Windows checkouts configured with
    # core.autocrlf stay clean after a build, while Unix runners keep LF output.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline=None, dir=path.parent, delete=False) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _refresh_label(data: dict[str, Any]) -> str:
    """Format a verified UTC cache timestamp without guessing on malformed data."""
    value = data.get("last_successful_refresh_utc")
    if not isinstance(value, str):
        return "**Last fully successful data refresh:** not available yet."
    try:
        timestamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "**Last fully successful data refresh:** not available yet."
    if timestamp.tzinfo != dt.timezone.utc:
        return "**Last fully successful data refresh:** not available yet."
    return f"**Last fully successful data refresh:** {timestamp:%Y-%m-%d %H:%M:%S} UTC."


def _project_section(project: dict[str, Any], data: dict[str, Any], index: int) -> list[str]:
    """Render one evidence-based project card using normal GitHub Markdown."""
    remote = next((item for item in data.get("repos", []) if item.get("name") == project["repo"]), {})
    url = remote.get("html_url") or f"{theme.PROFILE_URL}/{project['repo']}"
    stack = " · ".join(f"`{item}`" for item in project["stack"])
    homepage = remote.get("homepage")
    links = [f"[Repository]({url})"]
    demo_url = project.get("demo_url") or homepage
    if demo_url:
        demo = demo_url if str(demo_url).startswith("http") else "https://" + str(demo_url)
        links.insert(0, f"[Project demo]({demo})")
    title = f"### [{project['name']}]({url})"
    if index == 1:
        return [
            title,
            "",
            f"**01 / {project['eyebrow']}**",
            "",
            project["description"],
            "",
            "`change` → `invariants` → `future comparison` → `human decision`",
            "",
            f"**Built with** {stack} · {' · '.join(links)}",
            "",
        ]
    if index == 2:
        return [
            title,
            "",
            f"> **02 / {project['eyebrow']}**",
            ">",
            "> Windows agents → authenticated API → PostgreSQL → fleet dashboard",
            "",
            project["description"],
            "",
            f"**Built with** {stack}",
            "",
            " · ".join(links),
            "",
        ]
    return [
        title,
        "",
        f"**03 / {project['eyebrow']}**",
        "",
        project["description"],
        "",
        "| Voice client | Agent services |",
        "|:--|:--|",
        "| Browser UI → Express API | Python LiveKit → Gemini → Qdrant → Rime |",
        "",
        f"**Built with** {stack} · {' · '.join(links)}",
        "",
    ]


def _language_summary(data: dict[str, Any]) -> str:
    """Provide a readable text equivalent for narrow screens and image fallbacks."""
    ranked = sorted(
        ((str(name), int(size)) for name, size in data.get("languages", {}).items() if int(size) > 0),
        key=lambda item: (-item[1], item[0]),
    )
    total = sum(size for _, size in ranked)
    if not total:
        return "GitHub language totals are unavailable in the current cache."
    visible = ranked[:3]
    remainder = sum(size for _, size in ranked[3:])
    if remainder:
        visible.append(("Other", remainder))
    return " · ".join(f"{name} {size / total:.1%}" for name, size in visible)


def render_readme(data: dict[str, Any], portrait_available: bool | None = None) -> str:
    repository_snapshot = (
        f"**Repository snapshot:** {int(data.get('public_repo_count', 0))} original public repositories · {int(data.get('public_repo_stars', 0))} stars across those repositories."
        if data.get("repos_available", "public_repo_count" in data)
        else "**Repository snapshot:** public repository metrics unavailable; cached visuals are labelled accordingly."
    )
    if portrait_available is None:
        portrait_available = (ROOT / theme.PORTRAIT_SOURCE).is_file() and (ROOT / theme.PORTRAIT_PNG).is_file()
    alt = theme.PHOTO_ALT if portrait_available else "Portrait placeholder; add the supplied image at assets/profile-photo-source.jpg"
    hero = '<picture><source media="(prefers-color-scheme: dark)" type="image/gif" srcset="assets/hero-motion.gif"><source media="(prefers-color-scheme: light)" type="image/gif" srcset="assets/hero-motion-light.gif"><img src="assets/hero.svg" alt="Sarthak Sulkhlan: software and data systems"></picture>'
    typing = '<picture><source media="(prefers-color-scheme: dark)" type="image/gif" srcset="assets/typing.gif"><source media="(prefers-color-scheme: light)" type="image/gif" srcset="assets/typing-light.gif"><img src="assets/typing.svg" alt="Building software, learning data and AI, and tracing system behavior"></picture>'
    divider = '<picture><source media="(prefers-color-scheme: dark)" type="image/gif" srcset="assets/signal.gif"><source media="(prefers-color-scheme: light)" type="image/gif" srcset="assets/signal-light.gif"><img src="assets/divider.svg" alt="Emerald signal trace divider"></picture>'
    portrait = f'<picture><source type="image/gif" srcset="assets/profile-portrait.gif"><img src="assets/profile-portrait.png" alt="{alt}" width="240"></picture>'
    content = [hero, "", typing, "", "**Explore** · [About](#who-i-am) · [Hands-on engineering](#hands-on-engineering) · [Selected work](#selected-work) · [Education](#education--technical-activity) · [Telemetry](#public-telemetry) · [Contact](#contact--navigation) · [How this profile is built](SETUP.md)", "", divider, "", "[GitHub profile](" + theme.PROFILE_URL + ") · [Browse my repositories](" + theme.PROFILE_URL + "?tab=repositories)", "", "## Who I am", "", '<table width="100%"><tbody><tr><td width="32%" valign="top" align="center">', portrait, "", "<sub>COMPUTER SCIENCE / DATA SCIENCE</sub>", "</td><td width=\"68%\" valign=\"top\">", "", "### sarthak@build — profile", "", "| Field | Details |", "|:--|:--|", f"| study | {theme.EDUCATION} |", "| interests | Software engineering · data science · applied AI |", "| project stack | TypeScript · Python · React · Flask · SQL |", "| learning | Java problem solving · generative AI systems |", "| focus | Practical systems whose behavior can be observed and improved |", "", "I’m studying computer science and learning by building useful software. I’m interested in turning ideas into working systems, understanding their behavior through data, and making AI-enabled tools more dependable.", "", "**Current focus:** " + theme.CURRENT_FOCUS, "", "**Projects:** [EPOCH](https://github.com/Sarthaksulkhlan/epoch-software.evolution) · [Asset Sentinel](https://github.com/Sarthaksulkhlan/Asset-Sentinel) · [MatrixCore](https://github.com/Sarthaksulkhlan/Nexis---Starforge)", "", "</td></tr></tbody></table>", "", divider, "", "## Hands-on engineering", "", "Organized by project evidence and current study; not a proficiency ranking.", "", theme.picture_markup("skills", "Evidence-based groups for programming, AI, backend and data, frontend tools, and systems integration"), ""]
    for item in theme.CAPABILITIES: content.extend([f"### {item['name']}", "", " · ".join(item["items"]), "", item["evidence"], ""])
    content.extend(["<details><summary>Learning focus</summary>", "", "Java problem solving and generative AI systems are current learning topics.", "", "</details>", "", "## Selected work", "", "Three documented projects, each approaching a different systems problem. Descriptions and stacks are based on their public repository READMEs.", ""])
    for index, project in enumerate(theme.PROJECTS, start=1): content.extend(_project_section(project, data, index))
    content.extend([theme.picture_markup("project-landscape", "Three selected project areas: software evolution, endpoint telemetry, and voice interaction"), "", divider, "", "## Education & technical activity", "", f"**{theme.EDUCATION}**", "", theme.EDUCATION_DETAIL, "", "**Project activity:** EPOCH is documented as a team prototype built for the IBM Bob 2.0 hackathon. See [the repository](https://github.com/Sarthaksulkhlan/epoch-software.evolution).", "", "## Public telemetry", "", "Public repository metadata and a limited public event sample. No private activity or contribution totals are inferred.", "", _refresh_label(data), "", repository_snapshot, "", f"**Event sample:** {int(data.get('public_push_event_count', 0))} public PushEvents returned." if data.get("events_available", False) else "**Event sample:** public event data unavailable; cached activity remains labelled accordingly.", "", "<details><summary>Expand recent public activity visualization</summary>", "", '<picture><source media="(prefers-color-scheme: dark)" type="image/gif" srcset="assets/activity-motion.gif"><source media="(prefers-color-scheme: light)" type="image/gif" srcset="assets/activity-motion-light.gif"><img src="assets/activity.svg" alt="Cached public activity bars with an animated focus marker"></picture>', "", "</details>", "", theme.picture_markup("activity", "Public repository count, combined stars, and weekly buckets of sampled public PushEvents"), "", theme.ACTIVITY_NOTE, "", theme.picture_markup("language-stats", "Language byte composition across original public repositories, excluding forks and this profile repository"), "", f"**Language mix:** {_language_summary(data)}.", "", "Language shares use GitHub-reported source-byte totals across owned, non-fork public repositories; the profile repository is excluded.", "", "<details><summary>How to read the telemetry</summary>", "", "The activity plot groups PushEvents in GitHub’s latest public user-events response (up to 100 events) into 12 week buckets. It is a sample, not a full contribution history.", "", "</details>", "", "## Contact & navigation", "", f"[GitHub profile]({theme.PROFILE_URL}) · [All public repositories]({theme.PROFILE_URL}?tab=repositories) · [EPOCH](https://github.com/Sarthaksulkhlan/epoch-software.evolution) · [Asset Sentinel](https://github.com/Sarthaksulkhlan/Asset-Sentinel) · [MatrixCore](https://github.com/Sarthaksulkhlan/Nexis---Starforge)", "", "[Back to introduction](#who-i-am) · [How this profile is built](SETUP.md)", "", "<sub>Self-hosted GIFs add subtle motion in GitHub’s rendered README; static SVG or PNG fallbacks retain the information. Telemetry uses public GitHub data and a limited event sample.</sub>"])
    body = "\n".join(content).strip()
    existing = README_FILE.read_text(encoding="utf-8") if README_FILE.exists() else ""
    if START in existing and END in existing:
        prefix, tail = existing.split(START, 1)
        _, suffix = tail.split(END, 1)
        return prefix + START + "\n" + body + "\n" + END + suffix
    if START in existing or END in existing:
        raise ValueError("README generated markers are unbalanced")
    return START + "\n" + body + "\n" + END + "\n"


def build(offline: bool = False, use_token: bool = True) -> None:
    theme.validate_theme()
    data = _read_data()
    if not offline:
        data = fetch_data(data, os.environ.get("GITHUB_TOKEN") if use_token else None)
        _write_atomic(DATA_FILE, json.dumps(data, indent=2, sort_keys=True) + "\n")
    portrait_available = write_assets(ROOT / "assets", data)
    _write_atomic(README_FILE, render_readme(data, portrait_available))
    print("Built profile README and SVG assets.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="build only from cached public data")
    parser.add_argument("--no-token", action="store_true", help="ignore optional GITHUB_TOKEN")
    args = parser.parse_args()
    build(offline=args.offline, use_token=not args.no_token)


if __name__ == "__main__":
    main()

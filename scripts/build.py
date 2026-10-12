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
    result.setdefault("profile_available", "followers" in old)
    result.setdefault("activity_weeks", [0] * 12)
    result.setdefault("repos_available", "public_repo_count" in old)
    result.setdefault("languages_available", bool(old.get("languages")))
    failures: list[str] = []
    try:
        profile = request_json(f"{API}/users/{theme.USERNAME}", token)
        if not isinstance(profile, dict) or not isinstance(profile.get("followers"), int) or isinstance(profile.get("followers"), bool) or profile["followers"] < 0:
            raise ValueError("Invalid public follower metadata")
        result["followers"] = profile["followers"]
        result["profile_available"] = True
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        failures.append(f"profile:{exc}")
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
    """Compose a concise profile with source-grounded content and small motion."""
    if portrait_available is None:
        portrait_available = (ROOT / theme.PORTRAIT_SOURCE).is_file() and (ROOT / theme.PORTRAIT_PNG).is_file()
    alt = theme.PHOTO_ALT if portrait_available else "Portrait placeholder. Add your image at assets/profile-photo-source.jpg."
    hero = theme.picture_markup("hero", "Sarthak Sulkhlan — software, data science, and applied AI")
    typing = (
        '<picture><source media="(prefers-color-scheme: dark)" type="image/gif" srcset="assets/typing.gif">'
        '<source media="(prefers-color-scheme: light)" type="image/gif" srcset="assets/typing-light.gif">'
        '<img src="assets/typing.svg" alt="Building practical software; learning data science and applied AI; turning ideas into working systems"></picture>'
    )
    portrait = f'<img src="assets/profile-portrait.png" width="220" alt="{alt}">'
    content = [
        hero, "", typing, "",
        "**Explore** · [About](#about) · [Hands-on Engineering](#hands-on-engineering) · [Selected Work](#selected-work) · [Experience](#experience) · [Education](#education) · [Telemetry](#telemetry) · [Contribution Art](#contribution-art) · [Contact](#contact) · [How This Profile Is Built](SETUP.md)",
        "", theme.picture_markup("divider", "Thin emerald section divider"), "",
        "## About", "",
        '<table width="100%"><tbody><tr><td width="34%" align="center" valign="top">' + portrait + "</td><td width=\"66%\" valign=\"top\">",
        "<h3><code>sarthak@systems</code> / about</h3>",
        "<table><tbody>"
        f"<tr><th align=\"left\">Study</th><td>{theme.EDUCATION}</td></tr>"
        "<tr><th align=\"left\">Interests</th><td>Software engineering · data science · applied AI</td></tr>"
        "<tr><th align=\"left\">Project work</th><td>Verified software, telemetry, and voice-system projects</td></tr>"
        "<tr><th align=\"left\">Learning</th><td>Java problem solving · Python · generative AI</td></tr>"
        "<tr><th align=\"left\">Focus</th><td>Building practical, reliable software systems</td></tr>"
        "</tbody></table>",
        "<p>I’m a computer science student who learns by building. I enjoy taking an idea through implementation, observing how a system behaves, and using that evidence to improve it.</p>",
        "<p><strong>Selected repositories</strong><br><a href=\"https://github.com/Sarthaksulkhlan/epoch-software.evolution\">EPOCH</a> · <a href=\"https://github.com/Sarthaksulkhlan/Asset-Sentinel\">Asset Sentinel</a> · <a href=\"https://github.com/Sarthaksulkhlan/Nexis---Starforge\">MatrixCore</a></p>",
        "</td></tr></tbody></table>", "", theme.picture_markup("divider", "Thin emerald section divider"), "",
        "## Hands-on Engineering", "",
        "Icons use Skill Icons; each links to an official learning page. If the icon service is unavailable, the linked image’s alt label remains visible.", "",
    ]
    for category, skills in theme.SKILL_GROUPS:
        content.extend([f"### {category}", "", '<p align="center">'])
        for label, icon, url in skills:
            src=f"https://skillicons.dev/icons?i={icon}&theme=dark"
            content.append(f'<a href="{url}" title="{label}"><img src="{src}" width="40" height="40" alt="{label} icon"></a>')
        content.extend(["</p>", ""])
    content.extend([
        "Project libraries documented in MatrixCore include [MCP](https://modelcontextprotocol.io/docs), [LiveKit](https://docs.livekit.io/), and [Qdrant](https://qdrant.tech/documentation/). Java is shown as a learning focus.", "",
        theme.picture_markup("divider", "Thin emerald section divider"), "",
        "## Selected Work", "", "Three verified projects, described from their repositories. Titles link to source; demos are shown only for the two deployed project sites.", "",
    ])
    for index, project in enumerate(theme.PROJECTS, 1):
        remote = next((item for item in data.get("repos", []) if item.get("name") == project["repo"]), {})
        repo_url = remote.get("html_url") or f"{theme.PROFILE_URL}/{project['repo']}"
        homepage = remote.get("homepage") if project["repo"] in ("epoch-software.evolution", "Asset-Sentinel") else None
        links = [f"[Repository]({repo_url})"]
        if homepage:
            demo = str(homepage)
            if not demo.startswith("http"):
                demo = "https://" + demo
            links.insert(0, f"[Live demo]({demo})")
        stack = " · ".join(f"`{item}`" for item in project["stack"])
        content.extend([
            f"### [{project['name']}]({repo_url})", "",
            f"**0{index} / {project['eyebrow']}**", "",
            project["description"], "",
            f"**Technologies:** {stack}", "",
            " · ".join(links), "",
        ])
    content.extend([
        theme.picture_markup("divider", "Thin emerald section divider"), "",
        "## Experience", "",
        f"**{theme.EXPERIENCE['role']}** · {theme.EXPERIENCE['employer']}<br>",
        f"{theme.EXPERIENCE['location']} · {theme.EXPERIENCE['duration']}", "",
        "## Education", "",
        f"**{theme.EDUCATION}** · {theme.EDUCATION_DETAIL}", "",
        "**Coursework:** " + " · ".join(theme.COURSEWORK), "",
        theme.picture_markup("divider", "Thin emerald section divider"), "",
        "## Telemetry", "",
        "Public account statistics and language totals are refreshed daily by GitHub Actions. The event chart is a limited sample from the public events API, not a complete contribution history.", "",
        _refresh_label(data), "",
        theme.picture_markup("activity", "Public repositories, repository stars, followers, sampled public events, and weekly event bars"), "",
        theme.picture_markup("language-stats", "Source-byte language shares across original public repositories"), "",
        "Language mix by GitHub-reported bytes: " + _language_summary(data) + ".", "",
        "## Contribution Art", "",
        "The public event feed does not provide a complete daily contribution calendar, so this profile shows only the weekly groups it can verify.", "",
        "<details><summary>Open the sampled weekly activity trace</summary>", "",
        theme.picture_markup("contribution-art", "Twelve weekly totals of public PushEvents from the recent sampled event feed"), "",
        theme.ACTIVITY_NOTE, "", "</details>", "",
        "<details><summary>How to read these metrics</summary>", "",
        "Repository count and stars are from GitHub’s public repository API and exclude forks and this profile repository. Followers come from the public user endpoint. Language shares use repository language byte totals. PushEvents are grouped into twelve week buckets from the latest public user-events response, which is capped at 100 events.", "", "</details>", "",
        "## Contact", "",
        f"[GitHub profile]({theme.PROFILE_URL}) · [All public repositories]({theme.PROFILE_URL}?tab=repositories) · [How this profile is built](SETUP.md)", "",
        "<sub>One small self-hosted typing GIF is the only looping animation. The portrait, hero, project cards, and telemetry are static SVG/PNG assets. GitHub does not animate SVG; see <a href=\"https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files\">GitHub image support</a>.</sub>",
    ])
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

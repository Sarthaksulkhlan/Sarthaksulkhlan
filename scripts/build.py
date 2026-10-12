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
    failures: list[str] = []
    try:
        repos = _valid_repo_list(request_json(f"{API}/users/{theme.USERNAME}/repos?per_page=100&type=owner&sort=updated", token))
        repos = [repo for repo in repos if not repo.get("fork") and repo.get("name") != theme.USERNAME]
        result["repos"] = [{key: repo.get(key) for key in ("name", "html_url", "description", "language", "homepage", "updated_at")} for repo in repos]
        result["public_repo_count"] = len(repos)
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
    result["data_note"] = "Public repositories and public PushEvent data only; GitHub Events API sampling is limited to recent public events."
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
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _project_lines(project: dict[str, Any], data: dict[str, Any], featured: bool = False) -> list[str]:
    repo_name = project["repo"]
    remote = next((item for item in data.get("repos", []) if item.get("name") == repo_name), {})
    url = remote.get("html_url") or f"{theme.PROFILE_URL}/{repo_name}"
    label = project["name"] + (" | Featured" if featured else "")
    tags = " / ".join(f"`{tag}`" for tag in project["tags"])
    lines = [f"<a href=\"{url}\"><strong>{label}</strong></a><br />", f"{project['description']}<br />", f"{tags}<br />", f"_{project['maturity']}_<br />"]
    homepage = remote.get("homepage")
    if homepage:
        demo = homepage if str(homepage).startswith("http") else "https://" + str(homepage)
        lines.append(f"[Live site]({demo}) | [Repository]({url})")
    else:
        lines.append(f"[Repository]({url})")
    return lines


def _language_summary(data: dict[str, Any]) -> str:
    """Provide a compact text equivalent of the language SVG for narrow screens."""
    values = sorted(((str(name), int(size)) for name, size in data.get("languages", {}).items() if int(size) > 0), key=lambda item: (-item[1], item[0]))
    total = sum(size for _, size in values)
    if not total:
        return "GitHub has not returned repository language totals yet."
    visible = values[:3]
    remainder = sum(size for _, size in values[3:])
    if remainder:
        visible.append(("Other", remainder))
    return " / ".join(f"{name} {size / total:.0%}" for name, size in visible)


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


def render_readme(data: dict[str, Any]) -> str:
    content = [
        theme.picture_markup("hero", "Sarthak Sulkhlan - software, data, and AI engineering"),
        "",
        "## Hello, I'm Sarthak",
        "",
        "My background is B.Tech Computer Science & Engineering (Data Science), and I'm working toward AI engineering and software development. I'm learning Python, Java DSA, generative AI, and software engineering through practical projects.",
        "",
        "### Current focus",
        "",
        "- Python and Java problem solving / generative AI and AI applications / reliable software systems",
        "- Turning project ideas into useful tools, then improving them through implementation and iteration",
        "",
        theme.picture_markup("divider", "Section divider"),
        "",
        "## Selected work",
        "",
    ]
    for index, project in enumerate(theme.PROJECTS):
        content += _project_lines(project, data, featured=index < 2)
        content.append("")
    content += ["[Browse all public repositories](https://github.com/Sarthaksulkhlan?tab=repositories)", "", "### More experiments", ""]
    for project in theme.ADDITIONAL_PROJECTS:
        content += _project_lines(project, data)
        content.append("")
    content += [
        theme.picture_markup("divider", "Section divider"),
        "",
        "## Tools and topics",
        "",
        "**Learning and building** | Python | Java | generative AI | software engineering<br />",
        "**Used in public projects** | TypeScript | React | Flask | Git",
        "",
        "## Activity and languages",
        "",
        "These visuals use public repository language bytes and the limited public event feed. They don't include private contributions or claim a complete contribution history.",
        "",
        _refresh_label(data),
        "",
        theme.picture_markup("activity", "Public GitHub push activity by week; public events only"),
        "",
        theme.picture_markup("language-stats", "Language shares across public project repositories, based on GitHub language byte totals"),
        "",
        f"**Text summary for narrow screens:** {_language_summary(data)}",
        "",
        "## Contact",
        "",
        f"[Find me on GitHub: @{theme.USERNAME}]({theme.PROFILE_URL})",
        "",
        "---",
        "<sub>Generated from public GitHub metadata | Theme and profile copy: <code>scripts/theme.py</code></sub>",
    ]
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
    write_assets(ROOT / "assets", data)
    _write_atomic(README_FILE, render_readme(data))
    print("Built profile README and SVG assets.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="build only from cached public data")
    parser.add_argument("--no-token", action="store_true", help="ignore optional GITHUB_TOKEN")
    args = parser.parse_args()
    build(offline=args.offline, use_token=not args.no_token)


if __name__ == "__main__":
    main()

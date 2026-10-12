# Profile system setup

This repository generates a GitHub profile README and its visual assets from Python configuration and cached public GitHub data. `scripts/theme.py` holds the purple-and-graphite palette, content, experience, education, projects, and linked skill icons. `scripts/build_assets.py` renders static theme-aware SVG instruments, a locally derived portrait PNG, and four compact GIFs: the hero scan stripe, rotating focus display, telemetry reveal, and decorative Pac-Man. `scripts/build.py` refreshes the public data when run online and updates only content inside the README's generated markers.

The optional source portrait belongs at `assets/profile-photo-source.jpg`. It is ignored by Git; only the derived 480x600 `assets/profile-portrait.png` is published. The derived image uses an emerald duotone, restrained scanlines, and a frame. On a fresh checkout without the private source, the builder preserves a valid committed portrait or creates an explicit placeholder. It never creates a synthetic face.

## Windows setup

Install Python 3.10 or newer and Git. From PowerShell in the repository:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
py -3 scripts/build.py
py -3 scripts/verify_readme.py
```

Pillow generates the portrait and GIF; PyYAML validates workflow files. Run `py -3 scripts/build.py --offline` to regenerate from cached data without network access. Use `--no-token` to ignore an optional `GITHUB_TOKEN` environment variable.

## Content and visuals

Edit the portfolio copy and factual configuration in `scripts/theme.py`. README structure is in `scripts/build.py`; hero, focus display, divider, portrait, telemetry, and contribution art are generated in `scripts/build_assets.py`. Each GIF has a static SVG fallback. The stripe moves behind the hero name; the focus display dissolves between three fixed-height status cards rather than deleting and retyping text. The Pac-Man is decorative; its grid summarizes only the most recent public PushEvent sample and is explicitly not a contribution calendar. The profile uses Skill Icons for linked technology marks; each image links to that technology's official documentation. The icon host is external, so the image's alt text remains available if it cannot load.

Project descriptions and stacks are based on the linked public repositories. Live demo links are included only when a verified deployed homepage is available. Keep hand-written README content outside the generated markers. The builder leaves it intact.

```powershell
py -3 scripts/build.py --offline
py -3 scripts/verify_readme.py
```

## GitHub Actions and data

`refresh.yml` runs daily at 03:17 UTC (08:47 India Standard Time) and can also be run manually. It uses the built-in `GITHUB_TOKEN`; no secret is required for these public API endpoints. The cache stores account followers, original public repository count/stars, repository language bytes, and the latest public user-events sample. Repository totals exclude forks and this profile repository. Language mix is based on GitHub-reported source bytes. The activity chart groups only PushEvents returned in the latest public event sample (up to 100 events), so it is not a complete contribution history. Failed refreshes retain the last cached values for that source.

The workflow commits generated changes only when files actually change. To permit those commits, repository Actions workflow permissions must allow read and write access to contents. `verify.yml` runs syntax compilation, theme contrast checks, asset and README validation, workflow YAML checks, outage preservation checks, missing-photo fallback checks, marker preservation, and offline reproducibility checks without requiring network access.

Scheduled runs do not guarantee a personal contribution square. Automation commits are attributed to `github-actions[bot]`; artificial or empty commits are not generated.

## Troubleshooting

- **API rate limit or network failure:** the build logs a warning and keeps cached values where available. Rebuild with `py -3 scripts/build.py --offline`, then retry later.
- **Missing language breakdown:** GitHub may not have processed repository language statistics; the visual reports unavailable data instead of inventing values.
- **No activity bars:** public event sampling is limited and excludes private activity. An unavailable feed is labelled, while an available empty sample is shown as zero.
- **Invalid SVG or README reference:** run `py -3 scripts/verify_readme.py` for the failing asset or link.
- **Action cannot push:** check Actions content permissions and organization policy.
- **PowerShell blocks activation:** invoke `py -3 scripts/build.py` without activating the virtual environment.

No private contribution information is requested or cached. Never store a token in repository files, cached JSON, generated SVG, or README output.

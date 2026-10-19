# Profile system setup

This repository generates a GitHub profile README and its visual assets from Python configuration and cached public GitHub data. `scripts/theme.py` holds the purple-and-graphite palette, content, experience, education, projects, and linked skill icons. `scripts/build_assets.py` renders static theme-aware SVG instruments, a locally derived portrait PNG, and three compact GIFs: the hero separator/focus transition, telemetry reveal, and decorative Pac-Man. `scripts/build.py` refreshes the public data when run online and updates only content inside the README's generated markers.

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

Edit the portfolio copy and factual configuration in `scripts/theme.py`. README structure is in `scripts/build.py`; hero, divider, portrait, telemetry, and contribution art are generated in `scripts/build_assets.py`. Each GIF has a static SVG fallback. The hero holds the bold name, uppercase descriptor, and focus display in one fixed-height panel; a thin highlight moves only along the separator below the descriptor. The focus dissolves between three states rather than deleting and retyping text. The Pac-Man is decorative; its grid summarizes only the most recent public PushEvent sample and is explicitly not a contribution calendar. The profile uses Skill Icons for linked technology marks; each image links to that technology's official documentation. The icon host is external, so the image's alt text remains available if it cannot load.

Project descriptions and stacks are based on the linked public repositories. Live demo links are included only when a verified deployed homepage is available. Keep hand-written README content outside the generated markers. The builder leaves it intact.

```powershell
py -3 scripts/build.py --offline
py -3 scripts/verify_readme.py
```

## GitHub Actions and data

`refresh.yml` runs daily at 03:17 UTC (08:47 India Standard Time) and can also be run manually. It validates the profile application, then records the completed UTC date in `automation/daily-activity.md`. A date already present in that log makes reruns a successful no-op, so the workflow creates at most one automation commit per UTC date. The workflow uses the built-in `GITHUB_TOKEN`; no personal access token or repository secret is required. Its `contents: write` permission is limited to this workflow because it pushes the maintenance commit.

The workflow records a deterministic maintenance event rather than changing profile content solely to create a commit. The commit uses the profile owner's existing repository email (`24cseds104@jssaten.ac.in`), which must remain associated with the GitHub account for attribution. `verify.yml` has read-only permissions and runs type checking and the production build on pushes and pull requests.

Scheduled runs and valid commits do not guarantee a visible personal contribution square: GitHub evaluates commit email association, the repository’s default branch, repository visibility, and account contribution-display settings.

## Troubleshooting

- **API rate limit or network failure:** the build logs a warning and keeps cached values where available. Rebuild with `py -3 scripts/build.py --offline`, then retry later.
- **Missing language breakdown:** GitHub may not have processed repository language statistics; the visual reports unavailable data instead of inventing values.
- **No activity bars:** public event sampling is limited and excludes private activity. An unavailable feed is labelled, while an available empty sample is shown as zero.
- **Invalid SVG or README reference:** run `py -3 scripts/verify_readme.py` for the failing asset or link.
- **Action cannot push:** check Actions content permissions and organization policy.
- **PowerShell blocks activation:** invoke `py -3 scripts/build.py` without activating the virtual environment.

No private contribution information is requested or cached. Never store a token in repository files, cached JSON, generated SVG, or README output.

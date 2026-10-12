# Profile system setup

This repository builds the profile README and self-hosted visuals from one Python configuration. `scripts/theme.py` defines the graphite/emerald palette, typography, dimensions, profile copy, projects, and learning map. `scripts/build_assets.py` generates theme variants, activity graphics, and restrained animated GIFs; every animated composition has a static SVG or PNG fallback. `scripts/build.py` refreshes public GitHub repository, language, and recent-event data when online and updates only content between the README's generated markers. Cached data in `assets/profile-data.json` supports reproducible offline builds.

The source portrait belongs at `assets/profile-photo-source.jpg`. It is ignored by Git and processed locally into published `assets/profile-portrait.png` and `assets/profile-portrait.gif`. The derived 480x600 portrait uses a limited emerald palette, subtle halftone texture, framing, and restrained scanlines. The supplied image was available during generation. If you replace it, use your own clear head-and-shoulders photo; the build never substitutes a generated face. If the source is absent on a fresh checkout, the build creates an explicit PHOTO SOURCE REQUIRED placeholder instead.

The public REST API needs no personal access token. The scheduled workflow passes its built-in `GITHUB_TOKEN`; the same public endpoints work unauthenticated locally. A token is optional and should be stored as a local environment variable or GitHub Actions secret, never written into the repository. No private contribution data is requested, so no elevated scopes or PAT are needed.

## Windows setup

Install standard Python 3.10 or newer and Git. From PowerShell in the repository:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
py -3 scripts/build.py
py -3 scripts/verify_readme.py
```

Install the pinned Pillow image-processing and PyYAML verification dependencies with `py -3 -m pip install -r requirements.txt`. To regenerate assets using the cached snapshot without network access, run `py -3 scripts/build.py --offline`. To refresh public data without using a token in the environment, run `py -3 scripts/build.py --no-token`.

## Theme, projects, and generated copy

Edit the palette, typography, dimensions, name, project descriptions, capability map, and profile copy in `scripts/theme.py`. README layout is in `scripts/build.py`; the hero, skills map, project landscape, telemetry, portrait treatment, and motion frames are generated in `scripts/build_assets.py`. GitHub README images support animated GIFs; inline SVG animation is not relied upon. Self-hosted hero, typing, divider, portrait, and activity GIFs have complete static fallbacks. Motion is subtle, and the activity graphic moves only its focus marker over fixed cached data.

```powershell
py -3 scripts/build.py --offline
py -3 scripts/verify_readme.py
```

To add a project, first confirm its public README, repository metadata, technology, maturity, and live demo. Add the factual description, domain, and verified stack entries to `PROJECTS` in `scripts/theme.py`. The build links a demo only when GitHub's repository metadata supplies a homepage. Keep hand-maintained README content outside the generated markers; the builder leaves it intact.

## GitHub Actions

`refresh.yml` runs daily at 03:17 UTC (08:47 India Standard Time) and can be started with **Actions > Refresh profile > Run workflow**. It uses the built-in `GITHUB_TOKEN`; a fully successful refresh records and displays a genuine ISO UTC timestamp in the cache and README. Failed API calls retain the last successful timestamp and cached values for the failed source. Repository count and combined stars exclude this profile repository and forks. Language shares use GitHub-reported bytes for those original public repositories. The activity plot groups PushEvents from the recent public user-events sample (up to 100 events); it is not a complete contribution record. The workflow never creates an empty commit: it commits generated files only when their staged diff is nonempty. To allow a generated-file commit, open the repository's **Settings > Actions > General > Workflow permissions** and select **Read and write permissions**. No repository secret is required. If organization policy prevents write access for `GITHUB_TOKEN`, the refresh job will fail at push; configure the organization/repository policy before considering a narrowly scoped alternative credential.

`verify.yml` runs syntax compilation, SVG/README checks, theme contrast checks, and an offline reproducibility check for pushes and pull requests. It does not make network calls or claim that external links are currently reachable.

Daily workflow execution is not the same as a daily GitHub contribution. This automation commits only when real generated data changes, and its author is `github-actions[bot]`, so those commits are transparently attributed to automation rather than to your personal account. GitHub attributes a commit to a person only when the commit email is linked to that GitHub account, the commit is in a standalone repository on its default branch (or `gh-pages`), and the person has a qualifying relationship to the repository, such as being a collaborator or opening an issue or pull request there. A scheduled run does not guarantee either a changed file or a contribution square. Empty commits and artificial activity are intentionally not produced.

Disable the daily schedule by removing or commenting out the `schedule` trigger in `.github/workflows/refresh.yml`; `workflow_dispatch` can remain available for manual updates.

## Troubleshooting

- **API rate limit or network failure:** the build logs a concise warning and keeps prior cached values where possible. Run `py -3 scripts/build.py --offline` to regenerate from that cache. Retry the normal build later. Public unauthenticated API limits are lower than authenticated limits.
- **No language breakdown:** GitHub may not yet have processed repository language statistics. The visual says that data is unavailable instead of drawing made-up values.
- **No activity bars:** public event sampling is limited and excludes private activity. A successfully fetched empty public event feed is shown as zero; a failed or never-fetched feed is labelled unavailable.
- **Invalid SVG:** run `py -3 scripts/verify_readme.py`; it reports malformed XML, scripts/external references, missing assets, and width violations. Keep SVG content self-contained and regenerate with the builder.
- **Action cannot push:** verify the repository's Actions workflow permission is set to read/write and that organization policy permits `GITHUB_TOKEN` writes.
- **PowerShell blocks activation:** use `py -3 scripts/build.py` without activating the environment; this project has no third-party dependencies.

## Optional credentials

No credential is required for the public information used here. If a future feature truly needs private contribution information, keep it opt-in, document its minimum permission set, and store its token only in a local environment variable or Actions secret. Never put a token in cached JSON, SVGs, logs, or README output. This implementation does not retrieve private contribution information.

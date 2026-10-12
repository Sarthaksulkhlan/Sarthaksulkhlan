# Profile system setup

This repository builds the profile README and four visual asset families from a single Python configuration. Each family has a static dark SVG and light SVG. `scripts/theme.py` owns the colors, typography, dimensions, theme media rules, profile copy, and featured-project text. `scripts/build.py` optionally retrieves public GitHub repository metadata, language byte totals, and sampled public PushEvents; `scripts/build_assets.py` renders the SVGs; the builder updates only the README content between `PROFILE:GENERATED` markers. The last response is cached in `assets/profile-data.json`, so an offline build can use the last successful data.

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

Only the Python standard library is used; `requirements.txt` intentionally has no third-party packages. To regenerate SVGs using the cached snapshot without network access, run `py -3 scripts/build.py --offline`. To refresh public data without using a token in the environment, run `py -3 scripts/build.py --no-token`.

## Theme, projects, and generated copy

Edit the palette, typography, dimensions, theme media rules, name, project descriptions, tags, or introductory profile copy in `scripts/theme.py`. Generated README layout is in `scripts/build.py`; SVG drawings are in `scripts/build_assets.py`. The README uses GitHub's documented `<picture>` pattern to select separate static light/dark files, with a normal image fallback. SVG animation is intentionally omitted: GitHub documents that SVG animation isn't supported in its renderer. The static design remains complete when animation or SVG CSS is unavailable. Rebuild and verify after a change:

```powershell
py -3 scripts/build.py --offline
py -3 scripts/verify_readme.py
```

To add a project, first confirm its public README, repository metadata, technology, maturity, and live demo. Add the factual description and verified stack tags to `PROJECTS` or `ADDITIONAL_PROJECTS` in `scripts/theme.py`. The build links a live site only when GitHub's repository metadata supplies a homepage. Keep the README's hand-maintained content outside the generated markers; the builder leaves it intact.

## GitHub Actions

`refresh.yml` runs daily at 03:17 UTC (08:47 India Standard Time) and can be started with **Actions > Refresh profile > Run workflow**. It uses the built-in `GITHUB_TOKEN`; a fully successful refresh records and displays an ISO UTC timestamp in the cache and README, so that genuine metadata change can produce a daily commit. Failed API calls keep the last successful timestamp and cached values. The workflow never creates an empty commit. To allow a generated-file commit, open the repository's **Settings > Actions > General > Workflow permissions** and select **Read and write permissions**. No repository secret is required. If organization policy prevents write access for `GITHUB_TOKEN`, the refresh job will fail at push; configure the organization/repository policy before considering a narrowly scoped alternative credential.

`verify.yml` runs syntax compilation, SVG/README checks, and an offline reproducibility check for pushes and pull requests. It does not make network calls or claim that external links are currently reachable.

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

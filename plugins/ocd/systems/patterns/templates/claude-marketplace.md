# Claude Marketplace

Canonical shape for a Claude Code plugin marketplace repository, derived from 18 recently-maintained public repos (6 Anthropic, 12 community) that satisfy filters for marketplace manifest + Python + tests + multi-branch/tagged discipline. Every dimension below cites an adoption count across the sample so a reader can distinguish convention from outlier. Full repo list in *References* at the bottom.

## When to use

- **This pattern** — a repository publishing one or more Claude Code plugins through a `.claude-plugin/marketplace.json` manifest at its root.
- **Adaptation: single-plugin repo** — drop the `plugins/` wrapper; the plugin lives at the repo root. Adoption: 4/18 in the sample place plugin content at repo root with `source: "./"`, the rest use `plugins/<name>/` subdirs.
- **Adaptation: curated third-party aggregator** — plugin dirs hold only metadata; `source` pins external repos by `sha`. Adoption: 2/18 (both Anthropic: `claude-plugins-official`, `claude-plugins-community`). Different discipline (scheduled SHA-bump PRs, `strict: false` entries).
- **Not for MCP-only repos** — standalone MCP servers distribute via npm or PyPI. If a plugin wraps an MCP server, the plugin repo follows this pattern and references the MCP package via `mcpServers` config.

## Canonical shape

```text
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Exactly one manifest. Adoption: 17/18.
├── plugins/
│   └── <plugin>/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin `name` and `version` live here. Adoption: 10/14 with version.
│       ├── skills/ commands/ agents/ hooks/ bin/
│       ├── .mcp.json .lsp.json   # If applicable
│       ├── requirements.txt | pyproject.toml
│       ├── README.md LICENSE
│       └── architecture.md       # Plugin-level design (optional)
├── tests/                        # At repo root. Adoption: 9/10 Python-testing repos.
│   ├── integration/
│   └── plugins/<plugin>/         # Per-plugin nesting. Adoption: 1/10 (everything-claude-code).
├── scripts/
│   ├── test.sh                   # Wrapper around the project's test runner
│   └── release.sh                # Optional — tag-cut automation
├── .github/
│   └── workflows/
│       ├── ci.yml                # Push/PR pytest. Adoption: 9/18.
│       ├── release.yml           # Tag-triggered release. Adoption: 5/18.
│       └── validate.yml          # Manifest linting. Adoption: 1/18 (Anthropic-only).
├── pyproject.toml                # Pytest config lives here. Adoption: 6/10 vs pytest.ini 0/10.
├── README.md
├── CHANGELOG.md
├── LICENSE
├── architecture.md
└── CLAUDE.md                     # Agent procedures (optional)
```

## Dimensional adoption

### Marketplace manifest

| Dimension | Adoption | Notes |
|---|---|---|
| Single `marketplace.json` file | 17/18 | One exception is a nested partner plugin, not a channel split. No repo uses `marketplace.stable.json` or similar. |
| `source` as relative string (`"./"`, `"./<dir>"`) | 14/18 | Self-contained marketplaces. |
| `source` as `url`+`sha` object | 2/18 | Aggregator marketplaces pinning third-party plugins (Anthropic). |
| `source` as `github`/`npm` object | 2/18 | Community outliers. |
| Marketplace `name` matches repo author or domain | 18/18 | Reserved names to avoid: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`. |

### Channel selection (stable vs dev)

| Dimension | Adoption | Notes |
|---|---|---|
| User-facing dev/stable channel declared in marketplace | 0/18 | No repo in the sample implements a channel split at the marketplace level. |
| Channel selected via CLI `@ref` pinning | — | Supported by Claude Code universally; users run `plugin marketplace add <owner>/<repo>@<ref>`. No repo *organizes* around it, but the CLI accepts the form. |
| Second marketplace file (`marketplace.stable.json` or similar) | 0/18 | Not observed. Installing via URL to an alternate JSON file disables auto-update. |

The practical pattern: one marketplace.json. Dev users install with the default branch; stable users install pinned to a release tag or commit SHA.

### Branches and tags

| Dimension | Adoption | Notes |
|---|---|---|
| Default branch is `main` | 16/18 | 2 use `master` (community only). |
| Semver tags (`vX.Y.Z`) | 14/18 | 2 use pre-release suffixes (`-rc`, `-beta`, `-alpha`). 4 have zero tags (3 of those are Anthropic aggregator marketplaces). |
| Tags annotate commits on `main` | 14/15 with tags | `Chachamaru127/claude-code-harness` is the only repo tagging on dedicated `release/*` branches. |
| `release/x.y` long-lived branches | 1/18 | Uncommon. Community norm is tag-on-main. |
| Long-lived `dev` / `develop` branch | 0/18 | One repo (`superpowers-optimized`) has a `dev` branch; no evidence it is exposed as a user channel. |

### Plugin.json version authority

| Dimension | Adoption | Notes |
|---|---|---|
| `version` declared in `plugin.json` only | 10/14 with version | Dominant convention. |
| `version` in marketplace entry only | 3/14 | Outlier — declarations can drift. |
| `version` in both (duplicated) | 1/14 | Observed: drifted in the one case (`eight-eyes`: plugin.json `5.0.0-alpha` vs marketplace entry `4.2.0`). Do not duplicate. |
| `version` absent entirely | 4/18 | All Anthropic aggregator marketplaces. Acceptable only when the marketplace catalogs remote plugins whose `version` lives in their own repos. |

### Tests

| Dimension | Adoption | Notes |
|---|---|---|
| `tests/` at repo root | 9/10 Python-testing | Dominant convention. |
| Per-plugin nested tests `tests/plugins/<name>/` | 1/10 | Observed precedent: `everything-claude-code`. Compatible with 9/10 root-tests norm. |
| Pytest config in `pyproject.toml` | 6/10 Python-testing | Dominant. |
| Dedicated `pytest.ini` | 0/10 Python-testing | Not observed in the sample. |
| `conftest.py` present | 4/10 | Used for shared fixtures and custom command-line options. |

### CI workflows

| Dimension | Adoption | Notes |
|---|---|---|
| At least one workflow in `.github/workflows/` | 16/18 | 2 repos have no CI. |
| `ci.yml` or equivalent (push/PR pytest) | 9/18 | Dominant test-automation shape. |
| `release.yml` triggered by `v*` tag | 5/18 | Standard release-automation shape. |
| Marketplace manifest validation workflow | 1/18 | Anthropic-only (`claude-plugins-official`). Cheap insurance; worth adopting for signal. |
| Scheduled SHA-bump PR workflow | 1/18 | Anthropic-only. Applies only to aggregator marketplaces. |

### Python dependencies

| Dimension | Adoption | Notes |
|---|---|---|
| `pyproject.toml` | 6/10 Python-using | Dominant. |
| `requirements.txt` as primary dep manifest | ≤1/10 | Rare; usually appears as a test fixture rather than the real manifest. |
| SessionStart hook installs into isolated venv | 0/18 | Not observed in the sample. `claude-plugins` (this repo) is novel here; document the mechanism clearly for users. |

### Documentation

| Dimension | Adoption | Notes |
|---|---|---|
| `README.md` at repo root | 18/18 | Universal. |
| `CHANGELOG.md` | 9/18 | Optional; paired with `release.yml` when present. |
| `architecture.md` | 2/18 | Optional; rare at marketplace root. |
| Per-plugin `README.md` | ~12/18 | Standard when plugin is non-trivial. |

## Design decisions with rationale

### One marketplace.json, channel via `@ref`

**Decision.** Ship a single `.claude-plugin/marketplace.json`. Users subscribe to a dev channel by adding the marketplace without a ref; subscribe to a stable channel by adding with `@vX.Y.Z`.

**Evidence.** 17/18 repos have exactly one marketplace.json. 0/18 implement a channel split in the manifest layer. The CLI's `plugin marketplace add <owner>/<repo>@<ref>` gives users channel selection without requiring coordinated marketplace-manifest infrastructure.

**Rejected: second marketplace file (e.g. `marketplace.stable.json`).** Installable only via direct URL to the JSON, which breaks auto-update (URL-based marketplaces do not refresh). 0/18 adoption; no observed precedent.

**Rejected: two separate marketplaces with different `name` fields.** Supported by Claude Code docs for dual-channel setups but introduces plugin.json-name collisions unless each channel also uses different plugin names, which is a substantial maintenance split. 0/18 adoption in the sample.

### Tests at repo root

**Decision.** `tests/` lives at repo root. Per-plugin tests nest under `tests/plugins/<name>/`.

**Evidence.** 9/10 Python-testing repos put tests at repo root. `everything-claude-code` demonstrates the per-plugin nested pattern compatibly. Plugin caches install the entire `plugins/<name>/` tree into `~/.claude/plugins/cache/`; tests at the plugin-dir level would ship with every install. Claude Code has no file-exclusion manifest (no `.claudeignore`), so the only way to keep dev artifacts out of the cache is structurally via repo layout.

### Pytest config in `pyproject.toml`

**Decision.** Pytest configuration goes in `pyproject.toml` under `[tool.pytest.ini_options]`.

**Evidence.** 6/10 Python-testing repos use this form. 0/10 use a dedicated `pytest.ini`. Consolidating reduces the file count and matches community convention.

### Plugin version lives in `plugin.json`

**Decision.** `plugin.json` is the sole location for `version`. Do not duplicate into marketplace entries.

**Evidence.** 10/14 repos with a version set it in `plugin.json` only. The one repo with duplication (`eight-eyes`) had drifted values between the two locations, demonstrating the failure mode documented in Claude Code's plugin-reference (plugin.json wins silently; marketplace entry goes stale).

### Semver tags on main; release branches optional

**Decision.** Main branch tracks `0.0.z` as a dev build counter bumped automatically via pre-commit hook (enables cache invalidation for dev-channel users). Real semver lives on tags; tags annotate commits on `main` directly unless the repo opts into `release/x.y` branches.

**Evidence.** 14/15 tagged repos put tags on `main`. Only `claude-code-harness` uses dedicated release branches — a disciplined choice but not community norm. Either works; the release-branch variant reads as more rigorous for portfolio signal, the tag-on-main variant matches what most users will recognize.

### CI: push/PR pytest + tag-triggered release

**Decision.** `ci.yml` runs pytest on every push and PR. `release.yml` triggers on `v*` tag push and handles release automation. Optionally add `validate.yml` for manifest linting.

**Evidence.** 9/18 have `ci.yml`-shape automation; 5/18 have `release.yml`-shape automation. Manifest validation workflows appear in 1/18 (Anthropic-only) — cheap signal for portfolio-level polish.

## Non-obvious gotchas

- **No `.claudeignore` exists.** Plugin cache carries the entire `plugins/<name>/` directory; dev/prod separation happens only via repo layout discipline (tests at repo root, not inside plugin dirs).
- **`version` duplication (plugin.json + marketplace entry) silently drifts.** Observed in the wild; documented in Claude Code's plugin-reference. Single source of truth: `plugin.json`.
- **Relative-path plugin sources require a git-based marketplace.** Users adding the marketplace via direct URL to `marketplace.json` (not git clone) get relative-path resolution failures. Use explicit `github` + `ref` sources if both install paths need to work.
- **`additionalDirectories` in `permissions`** accepts literal paths, not globs. `..` is portable (resolves against the active project at runtime).
- **Background auto-updates run without git credentials** — private-repo plugins require `GITHUB_TOKEN` / equivalent exported in the user's shell.
- **Marketplace state is per-user, not per-worktree.** `~/.claude/plugins/known_marketplaces.json` is global; switching worktrees does not isolate marketplace config.
- **`--plugin-dir` PATH-shadowing.** `claude --plugin-dir <local-checkout>` loads the plugin module from the checkout (so MCP tools and skill content reflect the dev tree) but does not prepend the checkout's `bin/` to PATH ahead of the marketplace cache's bin directories. Bash-invoked binaries (`<plugin>-run`, anything in `bin/`) resolve to stale marketplace cache versions. Workaround: run `/checkpoint` (commit + push + marketplace update) so the cached install is the version under test, then iterate. `--plugin-dir` alone is not a reliable dev-iteration path when tests shell out to plugin binaries. Full reproduction and root cause documented in `.claude/logs/problem/Marketplace cache PATH shadowing.md`.
- **Pre-commit version bump** — the `0.0.z` auto-bump on main is a commit hook, not a CI step. Skipping hooks (`git commit --no-verify`) silently skips the bump and produces a dev commit Claude Code cannot distinguish from a prior one.

## Checklist for a new marketplace repo

1. Create `.claude-plugin/marketplace.json` with a single plugin entry whose `source` is a relative path (`./plugins/<plugin-a>`).
2. Create the first plugin under `plugins/<plugin-a>/.claude-plugin/plugin.json` with `name` and `version` fields.
3. Initialize `tests/` at repo root with `integration/` and `plugins/<plugin-a>/` subdirs.
4. Put pytest configuration in `pyproject.toml` under `[tool.pytest.ini_options]`.
5. Add `scripts/test.sh` delegating to the test runner.
6. Add `scripts/release.sh` for tag cuts (optional).
7. Add `.github/workflows/ci.yml` running pytest on push/PR.
8. Add `.github/workflows/release.yml` triggered on `v*` tag push (optional).
9. Add `.github/workflows/validate.yml` for manifest linting (optional; portfolio signal).
10. Install pre-commit hook for `0.0.z` auto-bump on `main` (optional; enables dev-channel cache invalidation).
11. Write `README.md`, `CHANGELOG.md`, `LICENSE`, and (optionally) `architecture.md` and `CLAUDE.md`.
12. Tag the first stable release (`v0.1.0`). Users install stable via `/plugin marketplace add <owner>/<repo>@v0.1.0`.
13. Verify by installing from both `main` (default branch) and the tagged ref on a clean machine; confirm the plugin cache contains only intended files.

## References

All observations above are cited to these repositories. Dates reflect recent activity at the time of sampling.

**Anthropic-owned (6):**

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — official curated marketplace; 144 plugins; `url`+`sha` aggregator pattern
- [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) — community catalog; 1,636 plugins; mixed `url`+`sha` and `git-subdir`+`ref`
- [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) — 41 plugins; relative sources
- [anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) — 8 plugins; relative sources
- [anthropics/life-sciences](https://github.com/anthropics/life-sciences) — 17 plugins; relative sources; semver tags on main
- [anthropics/healthcare](https://github.com/anthropics/healthcare) — 7 plugins; relative sources; semver tags on main

**Community (12):**

- [AgentBuildersApp/eight-eyes](https://github.com/AgentBuildersApp/eight-eyes) — single plugin; `v5.0.0-alpha` tag; version drift between plugin.json and marketplace entry
- [BULDEE/ai-craftsman-superpowers](https://github.com/BULDEE/ai-craftsman-superpowers) — 30 semver tags
- [BaseInfinity/sdlc-wizard](https://github.com/BaseInfinity/sdlc-wizard) — 11 tags; extensive CI (8 workflows); 30+ feature branches
- [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) — only sampled repo using `release/*` branches for release cuts
- [CodeAlive-AI/codealive-skills](https://github.com/CodeAlive-AI/codealive-skills) — 10 tags; pytest with coverage in CI
- [CronusL-1141/AI-company](https://github.com/CronusL-1141/AI-company) — 6 tags; `master` default; dedicated `conftest.py`
- [Kanevry/session-orchestrator](https://github.com/Kanevry/session-orchestrator) — pre-release tag suffixes (`-rc`, `-beta`)
- [Vortiago/mcp-outline](https://github.com/Vortiago/mcp-outline) — 18 tags; `release.yml` tag-triggered; `publish-pypi.yml` — demonstrates full release pipeline
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — per-plugin nested tests pattern; reusable workflows
- [IgorGanapolsky/ThumbGate](https://github.com/IgorGanapolsky/ThumbGate) — `npm` source type (outlier)
- [REPOZY/superpowers-optimized](https://github.com/REPOZY/superpowers-optimized) — only repo with a `dev` branch; shell-based tests; no CI
- [HiH-DimaN/idea-to-deploy](https://github.com/HiH-DimaN/idea-to-deploy) — `github` source type (outlier); 20 tags

**Sample gaps disclosed.** GitHub's code-search API caps `path:.claude-plugin filename:marketplace.json` at 2,424 hits with 30 per call, not exhaustively enumerated. The community sample is 12 of ~24 that survived filters out of the first 400 probed out of 1,491 unique plugin-source repos listed in `anthropics/claude-plugins-community`. Distributions in this document are valid for this sample; the global population may differ.

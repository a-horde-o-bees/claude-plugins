# Claude Marketplace

Canonical shape for a Claude Code plugin marketplace repository, derived from 18 recently-maintained public repos (6 Anthropic, 12 community) that satisfy filters for marketplace manifest + Python + tests + multi-branch or tagged discipline. Every decision below cites an adoption count across the sample so a reader can distinguish convention from outlier without inferring. Full repo list in *References*.

## When to use

- **This pattern** — a repository publishing one or more Claude Code plugins through a `.claude-plugin/marketplace.json` manifest at its root.
- **Adaptation: single-plugin repo** — drop the `plugins/` wrapper; the plugin lives at the repo root with `source: "./"`.
- **Adaptation: curated third-party aggregator** — plugin dirs hold only metadata; `source` pins external repos by `sha`. Different discipline (scheduled SHA-bump PRs, `strict: false` entries).
- **Not for MCP-only repos** — standalone MCP servers distribute via npm or PyPI.

## Canonical shape

```text
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Single manifest at this exact path
├── plugins/
│   └── <plugin>/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin name and version live here
│       ├── skills/ commands/ agents/ hooks/ bin/
│       ├── .mcp.json .lsp.json   # If applicable
│       ├── README.md LICENSE
│       └── architecture.md       # Plugin-level design (optional)
├── tests/                        # At repo root
│   ├── integration/
│   └── plugins/<plugin>/         # Per-plugin nesting (optional; precedent exists)
├── scripts/
│   ├── test.sh                   # Wrapper around the project's test runner
│   └── release.sh                # Optional — tag-cut automation
├── .github/
│   └── workflows/
│       ├── ci.yml                # Push/PR pytest
│       ├── release.yml           # Tag-triggered release (optional)
│       └── validate.yml          # Manifest linting (optional)
├── pyproject.toml                # Python deps + pytest config
├── README.md
├── CHANGELOG.md                  # Optional
├── LICENSE
├── architecture.md               # Optional
└── CLAUDE.md                     # Agent procedures (optional)
```

## Decisions

Each subsection describes a design component a repo author chooses among mutually-exclusive implementation paths. The **Docs** column marks paths explicitly recommended by Claude Code documentation (primary signal). The **Adoption** column shows how many of the 18 sample repos use each path (secondary signal).

**Legend.** ★ — path explicitly prescribed or recommended in [plugins-reference](https://code.claude.com/docs/en/plugins-reference) or [plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces). ☆ — docs shown as valid but without endorsement. (blank) — docs silent; adoption is the only available signal.

When the ★ and highest-adoption rows disagree, the conflict is flagged explicitly in the decision's narrative.

**Denominator rule.** Each table's denominator is the applicable subset for that decision, not the full sample. When a decision does not apply to every repo (e.g., version authority doesn't apply to repos without a version; pytest config doesn't apply to repos without Python tests), the narrative names the applicability criterion and how many repos are excluded. Adoption counts are always "adoption where applicable."

**Two samples.** Primary sample = 18 repos (used for all decisions unless noted). Dependency-management sample = 20 repos filtered for plugins with real runtime dep management, used only for the two dep-management decisions because the primary sample was skill-heavy.

### Marketplace manifest layout

Where the marketplace catalog lives. Determines whether Claude Code can find it via the documented default path and whether a single marketplace subscription covers the repo's plugins.

| Implementation path | Docs | Adoption |
|---|---|---|
| Single `.claude-plugin/marketplace.json` at repo root | | 17/18 |
| Multiple `marketplace.json` files at different paths | | 1/18 |

Docs do not prescribe a file count. Community convention is single.

### Plugin source format

How a marketplace entry points at plugin source code. Determines whether plugin code lives in the same repo as the marketplace or is fetched from a pinned external ref.

| Implementation path | Docs | Adoption |
|---|---|---|
| Relative string (`"./<dir>"`) | ☆ | 14/18 |
| `url`+`sha` object | ☆ | 2/18 |
| `github` object | ☆ | 1/18 |
| `npm` object | ☆ | 1/18 |
| `git-subdir` as default source | ☆ | 0/18 (appears only as per-entry pinning in aggregator catalogs) |

Docs show all shapes as valid without endorsing one. The version-authority decision below is coupled — relative sources get `version` in the marketplace entry; other sources get it in `plugin.json`.

### Channel selection mechanism

How users subscribe to dev vs stable channels of the same plugin. Claude Code's CLI supports `plugin marketplace add <owner>/<repo>@<ref>` for ref pinning regardless of how the marketplace itself is organized.

| Implementation path | Docs | Adoption |
|---|---|---|
| Two separate marketplaces with different `name` values, each pinning a different ref/SHA | ★ | 0/18 |
| No channel split declared; users pin via CLI `@ref` | | 18/18 |

**Docs vs adoption conflict.** Anthropic's plugin-marketplaces doc explicitly recommends two marketplaces with different `name` values for stable/latest channels (worked example: `stable-tools` + `latest-tools`). Zero sample repos implement this — community treats `@ref` pinning as the de-facto mechanism. Plugin-name collisions between channels (each `plugin.json` carries the same `name` unless authors ship separate plugin files) explain why community doesn't adopt. For portfolio signal, the docs pattern is the formal choice; for real-world compatibility, most users will expect the `@ref` pattern.

### Version authority

Single source of truth for a plugin's version. Claude Code's plugin-reference documents "plugin manifest always wins silently" when both locations carry the field — duplication drifts.

Applicable to repos that declare a version somewhere. 4 aggregator marketplaces declare no version anywhere and are excluded from the denominator below.

| Implementation path | Docs | Adoption |
|---|---|---|
| `plugin.json` only (for `github`/`url`/`git-subdir`/`npm` sources) | ★ | 10/14 |
| Marketplace entry only (for relative-path sources) | ★ | 3/14 |
| Both (duplicated) | | 1/14 (observed drift: `5.0.0-alpha` vs `4.2.0`) |

Docs split the recommendation by source type: "For relative-path plugins, set the version in the marketplace entry. For all other plugin sources, set it in the plugin manifest." Community majority puts version in `plugin.json` regardless of source shape.

### Default branch

| Implementation path | Docs | Adoption |
|---|---|---|
| `main` | | 16/18 |
| `master` | | 2/18 |

Docs silent. Convention is `main`.

### Tag placement

Where semver tags annotate commits. Docs prescribe semver (`MAJOR.MINOR.PATCH`) for tags but not where to place them.

Applicable to repos that tag releases. 4 aggregator marketplaces are untagged and excluded.

| Implementation path | Docs | Adoption |
|---|---|---|
| Tags on `main` | | 13/14 |
| Tags on `release/*` branches | | 1/14 |

### Release branching

Whether release prep happens on `main` directly or on dedicated long-lived branches. Applicable to repos with a release cadence. 4 aggregator marketplaces have no release cadence and are excluded.

| Implementation path | Docs | Adoption |
|---|---|---|
| Tag on `main` directly; no release branches | | 13/14 |
| Dedicated `release/x.y` long-lived branches | | 1/14 |

Docs silent. Community norm is tag-on-main.

### Version pre-release suffix convention

Docs call out pre-release suffixes explicitly: "Use pre-release versions like `2.0.0-beta.1` for testing." Applicable to repos that tag. 4 untagged repos excluded.

| Implementation path | Docs | Adoption |
|---|---|---|
| Plain semver only (`vX.Y.Z`) | ★ | 12/14 |
| Pre-release suffixes (`-rc`, `-beta`, `-alpha`) | ★ | 2/14 |

Both paths are docs-prescribed: plain semver for releases, pre-release suffixes for testing versions. Use either as appropriate.

### Tests location

Where tests live relative to plugin directories. Determines what ships to the plugin cache — there is no `.claudeignore`, so tests inside `plugins/<name>/` ship to every user who installs. Applicable to repos with Python tests. 8 repos have no Python tests and are excluded.

| Implementation path | Docs | Adoption |
|---|---|---|
| `tests/` at repo root only | | 8/10 |
| `tests/` at repo root with per-plugin subdirs (`tests/plugins/<name>/`) | | 1/10 |
| `tests/` inside plugin directory | | 1/10 |

Docs silent. Community majority is tests at repo root. Inside the plugin directory is an anti-pattern at scale because there is no `.claudeignore` — tests ship to user caches.

### Pytest configuration location

Applicable to repos with Python tests. 8 excluded.

| Implementation path | Docs | Adoption |
|---|---|---|
| `[tool.pytest.ini_options]` in `pyproject.toml` | | 6/10 |
| No explicit config | | 4/10 |

Docs silent. Community convention is `pyproject.toml`. Dedicated `pytest.ini` is a widely-known pytest option but was not observed in any repo in the sample.

### Python dependency manifest format

Applicable to repos with Python deps. 11 repos have no Python deps and are excluded.

| Implementation path | Docs | Adoption |
|---|---|---|
| `pyproject.toml` | | 6/7 |
| `requirements.txt` | | 1/7 |

Docs silent on manifest format. The install mechanism is what docs prescribe (see next decision).

### Dependency install mechanism

How runtime dependencies (Python venvs, Node `node_modules`, Rust/Go binaries) arrive on the user's machine at install or session-start time.

Docs prescribe a complete pattern: SessionStart hook installs into `${CLAUDE_PLUGIN_DATA}` using the docs' `diff -q` idiom so manifest changes trigger reinstall. Exact language from plugins-reference: *"a persistent directory for plugin state that survives updates. Use this for installed dependencies such as `node_modules` or Python virtual environments... The recommended pattern compares the bundled manifest against a copy in the data directory and reinstalls when they differ."* Docs ship a worked example using `diff -q` + trailing `rm` on failure.

**Uses the dependency-management sample (20 repos filtered for real runtime dep management).**

| Implementation path | Docs | Adoption |
|---|---|---|
| SessionStart hook → install into `${CLAUDE_PLUGIN_DATA}` → manifest-diff change detection → retry-next-session on failure | ★ | 17/20 |
| SessionStart hook but installs into `${CLAUDE_PLUGIN_ROOT}` (not `${CLAUDE_PLUGIN_DATA}`) | | 3/20 (usually citing language-specific module-resolution constraints) |
| `npx`/`uvx` ad-hoc runtime fetch as a hybrid within a SessionStart flow | | 1/20 |

### Dependency change detection

How the SessionStart hook decides whether to reinstall deps.

**Uses the dependency-management sample (20 repos).**

| Implementation path | Docs | Adoption |
|---|---|---|
| `diff -q` bundled manifest against cached copy in data dir | ★ | 12/20 |
| Hash (sha256/md5) of manifest | | 4/20 |
| Version file stamp | | 3/20 |
| Existence only (no change detection — miss upgrades) | | 1/20 |

## Features

Independent yes/no features a repo may adopt in any combination. The **Docs** column marks features Claude Code documentation explicitly recommends.

### Universal features

Applicable to every repo in the sample.

| Feature | Docs | Adoption |
|---|---|---|
| Components at plugin root (not inside `.claude-plugin/`) | ★ | 18/18 |
| `README.md` at repo root | | 18/18 |
| At least one CI workflow | | 16/18 |
| Semver tags | ★ | 14/18 |
| Per-plugin `README.md` | | 12/18 |
| `ci.yml` or equivalent push/PR pytest | | 9/18 |
| `CHANGELOG.md` documenting version changes | ★ | 9/18 |
| `architecture.md` at marketplace root | | 2/18 |
| Marketplace manifest validation workflow (runs `claude plugin validate`) | ★ (command recommended; CI workflow around it is inference) | 1/18 |
| `dev`/`develop` long-lived branches | | 1/18 |

### Conditional features

Applicability differs from the full sample. Each row names its applicability criterion and uses a denominator matching the applicable subset.

| Feature | Docs | Applicable to | Adoption where applicable |
|---|---|---|---|
| `release.yml` tag-triggered workflow | | Repos with a release cadence (14 tagged repos) | 5/14 |
| `release/*` long-lived branches | | Repos with a release cadence (14 tagged repos) | 1/14 |
| Pre-release tag suffixes for test versions | ★ | Repos that tag (14 tagged repos) | 2/14 |
| Scheduled SHA-bump PR workflow | | Aggregator marketplaces pinning external plugins by SHA (2 Anthropic aggregators in sample) | 1/2 |
| `bin/` for PATH-accessible plugin executables | ★ | Plugins that ship PATH-accessible binaries (sample count not directly measured; 2/18 observed to have `bin/`) | Where present, location is the docs-prescribed `bin/` |

## Non-obvious gotchas

- **No `.claudeignore` exists.** Plugin cache carries the entire `plugins/<name>/` directory; dev/prod separation happens only via repo layout discipline (tests at repo root, not inside plugin dirs).
- **`version` duplication (plugin.json + marketplace entry) silently drifts.** Claude Code's plugin-reference documents "plugin.json wins silently." One sample repo demonstrates the drift failure in production.
- **Relative-path plugin sources require a git-based marketplace.** Users adding the marketplace via direct URL to `marketplace.json` (not git clone) get resolution failures on relative paths. Use explicit `github` + `ref` sources if both install paths need to work.
- **`additionalDirectories` in `permissions`** accepts literal paths, not globs. `..` is portable because it resolves against the active project at runtime.
- **Background auto-updates run without git credentials** — private-repo plugins require `GITHUB_TOKEN` / equivalent exported in the user's shell.
- **Marketplace state is per-user, not per-worktree.** `~/.claude/plugins/known_marketplaces.json` is global; switching worktrees does not isolate marketplace config.
- **`--plugin-dir` PATH shadowing.** `claude --plugin-dir <local-checkout>` loads the plugin module from the checkout (MCP tools and skill content reflect the dev tree) but does not prepend the checkout's `bin/` to PATH ahead of the marketplace cache's bin directories. Bash-invoked plugin binaries resolve to stale cached versions. Workaround: keep the marketplace install current (commit + marketplace update) so cache and checkout align. `--plugin-dir` alone is not a reliable dev-iteration path when tests shell out to plugin binaries.
- **Pre-commit version bump** — when `main` uses a dev build counter (`0.0.z`) for cache invalidation, the bump usually rides on a pre-commit hook. Skipping hooks (`git commit --no-verify`) silently skips the bump.

## Checklist for a new marketplace repo

1. Create `.claude-plugin/marketplace.json` with a single plugin entry whose `source` is a relative path.
2. Create the first plugin under `plugins/<plugin>/.claude-plugin/plugin.json` with `name` and `version`.
3. Initialize `tests/` at repo root.
4. Put pytest configuration in `pyproject.toml` under `[tool.pytest.ini_options]`.
5. Add `scripts/test.sh` delegating to the test runner.
6. Add `scripts/release.sh` for tag cuts (optional).
7. Add `.github/workflows/ci.yml` running pytest on push/PR.
8. Add `.github/workflows/release.yml` triggered on `v*` tag push (optional).
9. Add `.github/workflows/validate.yml` for manifest linting (optional).
10. Write `README.md`, `CHANGELOG.md`, `LICENSE`, and (optionally) `architecture.md` and `CLAUDE.md`.
11. Tag the first stable release (`v0.1.0`). Users install stable via `/plugin marketplace add <owner>/<repo>@v0.1.0`.
12. Verify by installing from both the default branch and the tagged ref on a clean machine; confirm the plugin cache contains only intended files.

## References

Two samples inform this pattern. Primary sample (18 repos) is used for every decision except the two dependency-management decisions; dependency-management sample (20 repos filtered for real runtime dep management) is used for those two. `CronusL-1141/AI-company` appears in both samples.

### Primary sample (18)

**Anthropic-owned (6):**

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — official curated catalog; `url`+`sha` aggregator pattern
- [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) — community catalog; mixed `url`+`sha` and `git-subdir`+`ref`
- [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) — relative sources; contains the one observed nested partner marketplace
- [anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) — relative sources
- [anthropics/life-sciences](https://github.com/anthropics/life-sciences) — relative sources; semver tags on main
- [anthropics/healthcare](https://github.com/anthropics/healthcare) — relative sources; semver tags on main

**Community (12):**

- [AgentBuildersApp/eight-eyes](https://github.com/AgentBuildersApp/eight-eyes) — single plugin; pre-release tag suffix; drift between plugin.json and marketplace version
- [BULDEE/ai-craftsman-superpowers](https://github.com/BULDEE/ai-craftsman-superpowers) — 30 semver tags; ci.yml
- [BaseInfinity/sdlc-wizard](https://github.com/BaseInfinity/sdlc-wizard) — 11 tags; 8 workflows including `release.yml`
- [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) — only sampled repo using `release/*` branches for release cuts
- [CodeAlive-AI/codealive-skills](https://github.com/CodeAlive-AI/codealive-skills) — 10 tags; pytest with coverage in CI
- [CronusL-1141/AI-company](https://github.com/CronusL-1141/AI-company) — 6 tags; `master` default; dedicated `conftest.py`
- [Kanevry/session-orchestrator](https://github.com/Kanevry/session-orchestrator) — pre-release tag suffixes (`-rc`, `-beta`)
- [Vortiago/mcp-outline](https://github.com/Vortiago/mcp-outline) — 18 tags; `release.yml` tag-triggered; `publish-pypi.yml` for full release pipeline
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — per-plugin nested tests precedent; reusable workflows
- [IgorGanapolsky/ThumbGate](https://github.com/IgorGanapolsky/ThumbGate) — `npm` source type (outlier)
- [REPOZY/superpowers-optimized](https://github.com/REPOZY/superpowers-optimized) — only sampled repo with a `dev` branch
- [HiH-DimaN/idea-to-deploy](https://github.com/HiH-DimaN/idea-to-deploy) — `github` source type (outlier)

### Dependency-management sample (20)

Second research wave filtered for plugins with real runtime dep management (Python venvs, Node `node_modules`, Rust/Go binaries). Used only for the two dep-management decisions.

- [CronusL-1141/AI-company](https://github.com/CronusL-1141/AI-company) — Python venv, `diff -q` (also in primary sample)
- [anthril/official-claude-plugins](https://github.com/anthril/official-claude-plugins) — Python venv, stamp file + `diff -q`
- [Arcanon-hub/arcanon](https://github.com/Arcanon-hub/arcanon) — Node/npm, sentinel `diff -q`; installs into ROOT (cites ESM)
- [ekadetov/llm-wiki](https://github.com/ekadetov/llm-wiki) — Node/npm, version file + `diff -q`
- [marioGusmao/mg-plugins](https://github.com/marioGusmao/mg-plugins) — Node/npm, `diff -q` + Node ABI tracking
- [thecodeartificerX/codetographer](https://github.com/thecodeartificerX/codetographer) — Node/npm, copy-then-install
- [tretuttle/AI-Stuff](https://github.com/tretuttle/AI-Stuff) — Node + Playwright Chromium, sha256 + install marker
- [NoelClay/academic-research-mcp-plugin](https://github.com/NoelClay/academic-research-mcp-plugin) — Python venv + Node, `diff -q` both
- [123jimin-vibe/plugin-prompt-engineer](https://github.com/123jimin-vibe/plugin-prompt-engineer) — Python venv, version file
- [includeHasan/prospect-studio](https://github.com/includeHasan/prospect-studio) — Node/npm, sha256; installs into ROOT (cites ESM)
- [damionrashford/trader-os](https://github.com/damionrashford/trader-os) — Node via bun/npm, `diff -q` (cites docs URL in comment)
- [Chulf58/FORGE](https://github.com/Chulf58/FORGE) — Node, mtime vs lockfile; installs into ROOT
- [smcady/Cairn](https://github.com/smcady/Cairn) — Python venv, `diff -q`
- [JordanCoin/pdf-to-text](https://github.com/JordanCoin/pdf-to-text) — WASM binary download, version file
- [ZhuBit/cowork-semantic-search](https://github.com/ZhuBit/cowork-semantic-search) — Python venv, sha256
- [raphaelchristi/harness-evolver](https://github.com/raphaelchristi/harness-evolver) — Python venv, existence-only (no manifest diff)
- [brunoborges/ghx](https://github.com/brunoborges/ghx) — Go binaries into DATA, existence-only
- [jxw1102/flipper-claude-buddy](https://github.com/jxw1102/flipper-claude-buddy) — Python venv, md5 hash
- [BrandCast-Signage/root](https://github.com/BrandCast-Signage/root) — Node/npm, mixed: third-party into `~/.root-framework`, plugin's own into DATA
- [Lykhoyda/rn-dev-agent](https://github.com/Lykhoyda/rn-dev-agent) — Node/npm into DATA + symlink back to ROOT, version stamp

**Sample gaps disclosed.** GitHub's code-search API caps `path:.claude-plugin filename:marketplace.json` at 2,424 hits with 30 per call, not exhaustively enumerated. The community sample is 12 of ~24 that survived filters out of the first 400 probed of 1,491 unique plugin-source repos listed in `anthropics/claude-plugins-community`. Distributions above are valid for the sample; the global population may differ.

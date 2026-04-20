# Claude Marketplace — Pattern Alignment

Audit of this repository's current state against the [claude-marketplace pattern](.claude/patterns/ocd/claude-marketplace.md). Snapshot evolves as the project refactors toward the pattern's canonical shape. Mirrors the pattern's Decisions and Features sections one-to-one.

For each entry:

- **Chosen path** — which implementation path this repo currently uses.
- **Convention match** — whether that path is the dominant convention in the pattern's sample.
- **Gap** — if the chosen path is an outlier or absent, what closing the gap would require.

## Decisions

### Marketplace manifest layout

- **Chosen path:** Single `.claude-plugin/marketplace.json` at repo root.
- **Convention match:** ✓ Dominant (17/18).
- **Gap:** None.

### Plugin source format

- **Chosen path:** Relative string (`"./plugins/ocd"`).
- **Convention match:** ✓ Dominant (14/18).
- **Gap:** None.

### Channel selection mechanism

- **Chosen path:** No channel split declared in the manifest; README documents that users pin via CLI `@ref`.
- **Convention match:** ✓ Universal (18/18).
- **Gap:** None.

### Version authority

- **Chosen path:** `version` in `plugin.json` only.
- **Convention match:** ✓ Dominant (10/14 with version).
- **Gap:** None.

### Default branch

- **Chosen path:** `main`.
- **Convention match:** ✓ Dominant (16/18).
- **Gap:** None.

### Tag placement

- **Chosen path:** Tags on `main`. `plugin.json` on `main` tracks a monotonic `0.0.z` dev build counter; real semver tags annotate the tip of release branches when cut.
- **Convention match:** Partial (14/15 with tags put tags on `main`). The dev-counter-on-main + semver-on-release-branches split is not reflected in the sample; closest precedent is `Chachamaru127/claude-code-harness`, the only repo with `release/*` branches.
- **Gap:** The dev-counter scheme is a deliberate choice to enable cache invalidation for dev-channel users without touching real semver. Outlier but defensible.

### Release branching

- **Chosen path:** `release/x.y` long-lived branches planned; one branch currently exists under the legacy name `v0.1.0` (shadowing the `v0.1.0` tag — should be renamed to `release/0.1`).
- **Convention match:** Rare (1/14 with tags uses this). Only `claude-code-harness` uses the same discipline.
- **Gap:** Non-standard but matches this repo's versioning policy documented in `CLAUDE.md`. Action item: rename the `v0.1.0` branch to `release/0.1` so the tag-and-branch name collision is resolved. Unambiguous `git` resolution becomes `v0.1.0` → tag only.

### Version pre-release suffix convention

- **Chosen path:** Plain semver (`vX.Y.Z`); no pre-release suffixes in use.
- **Convention match:** ✓ Dominant (12/14 tagged).
- **Gap:** None.

### Tests location

- **Chosen path:** `tests/` at repo root with per-plugin subdirs (`tests/plugins/ocd/`).
- **Convention match:** Rare (1/10). Only observed precedent: `affaan-m/everything-claude-code`.
- **Gap:** Outlier but structurally consistent with the 9/10 "tests at repo root" majority. The per-plugin nesting is the sole way to keep dev artifacts out of user plugin caches at marketplace-scale where multiple plugins live in one repo. Defensible.

### Pytest configuration location

- **Chosen path:** Dedicated `tests/plugins/ocd/pytest.ini` per plugin.
- **Convention match:** ✗ Outlier (0/10 use `pytest.ini`; 6/10 use `pyproject.toml`).
- **Gap:** Action item — consolidate pytest config into `pyproject.toml` either at repo root or at `tests/plugins/ocd/pyproject.toml`. `pythonpath` and `testpaths` both work under `[tool.pytest.ini_options]`.

### Python dependency manifest

- **Chosen path:** `plugins/ocd/requirements.txt` for runtime deps (installed by SessionStart hook into isolated plugin venv).
- **Convention match:** ✗ Outlier (≤1/10 use `requirements.txt` as primary). The SessionStart-venv mechanism is novel (0/18 in sample).
- **Gap:** Dependency manifest format is secondary to the overall approach. The SessionStart-installs-into-isolated-venv mechanism is unprecedented but defensible — it solves a real problem (per-plugin dep isolation) that other repos don't address. Document the mechanism clearly in `README.md`/`CLAUDE.md` so consumers recognize it.

## Features

| Feature | This repo | Pattern adoption |
|---|---|---|
| Semver tags | present (`v0.1.0`) | 14/18 |
| `release/*` long-lived branches | planned (`release/0.1` not yet named; `v0.1.0` branch is the legacy) | 1/18 |
| `dev`/`develop` long-lived branches | absent | 1/18 |
| Pre-release tag suffixes | absent | 2/18 |
| At least one CI workflow | present | 16/18 |
| `ci.yml` or equivalent push/PR pytest | present as `.github/workflows/test.yml` | 9/18 |
| `release.yml` tag-triggered | **absent** | 5/18 |
| Marketplace manifest validation workflow | present as `.github/workflows/validate.yml` | 1/18 |
| Scheduled SHA-bump PR workflow | absent (not applicable — not an aggregator) | 1/18 |
| SessionStart-based plugin venv install | **present (novel)** | 0/18 |
| `README.md` at repo root | present | 18/18 |
| `CHANGELOG.md` | present | 9/18 |
| `architecture.md` at marketplace root | present | 2/18 |
| Per-plugin `README.md` | present | ~12/18 |

## Gap summary (open action items)

1. **Rename the `v0.1.0` branch to `release/0.1`** — resolves the branch-and-tag ambiguity; matches `CLAUDE.md`'s documented release-branch convention.
2. **Consolidate pytest config from `pytest.ini` into `pyproject.toml`** — aligns with 6/10 community convention; reduces file count.
3. **Add a `release.yml` tag-triggered workflow** — standard release-automation shape (5/18); pairs naturally with the existing `scripts/release.sh`.

## Novel-but-defensible choices

- **SessionStart hook installing into per-plugin isolated venv** (`plugins/ocd/hooks/install_deps.sh`). Unprecedented in the sample but solves a real per-plugin dependency-isolation problem. Keep; document mechanism.
- **Dev build counter `0.0.z` on `main` + semver tags on `release/*` branches.** Disciplined version-space split not directly observed in the sample but not in conflict with any convention; enables cache invalidation for dev-channel users without burning semver space.
- **Per-plugin nested tests under `tests/plugins/<name>/`.** Matches `affaan-m/everything-claude-code` precedent; consistent with the 9/10 tests-at-repo-root convention.

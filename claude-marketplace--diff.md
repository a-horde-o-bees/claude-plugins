# Claude Marketplace — Pattern Alignment

Audit of this repository's current state against the [claude-marketplace pattern](.claude/patterns/ocd/claude-marketplace.md). Snapshot evolves as the project refactors toward the pattern's canonical shape. Mirrors the pattern's purpose sections one-to-one.

For each purpose:

- **Chosen path** — what this repo currently does for the purpose.
- **Convention match** — ✓ dominant, ⟁ partial / outlier-but-defensible, ✗ outlier requiring action, — not applicable.
- **Gap** — if present, what closing it would require.

## Marketplace discoverability

**Manifest layout.** Single `.claude-plugin/marketplace.json` at repo root. ✓ Dominant (17/18).

**Marketplace-level metadata.** Top-level `description` (no `metadata` wrapper). ✓ Matches `claude-plugins-official` — 6/21 of the sample, including the highest-signal adopter.

**Per-plugin discoverability.** `category: "development"` on the single plugin entry; no `tags` or `keywords`. ✓ Matches the 5/21 category-only pattern.

- *Optional refinement:* adding `tags` (e.g. `["discipline", "project-navigation"]`) would align with Anthropic's life-sciences/healthcare pattern (5/21 use `category + tags`). Not a gap — current shape is defensible.

**`$schema` reference.** Present (`https://anthropic.com/claude-code/marketplace.schema.json`). ⟁ Rare but high-signal (~6/54 — all Anthropic-aligned or thoughtful community repos).

**Reserved names.** Marketplace name is `a-horde-o-bees`. ✓ No conflict with docs blocklist.

## Plugin source binding

**Source format.** Relative string (`"./plugins/ocd"`). ✓ Dominant (14/18).

**Authority (`strict`).** Default (`strict: true` implicit). ✓ Dominant (16/21 default + 1/21 explicit).

**Version authority.** Version in `plugin.json` only (`0.0.338` on main — dev build counter). ✓ Dominant (10/14 with version).

## Channel distribution

**Mechanism.** No channel split declared; README documents `@ref` pinning. ✓ Universal (18/18).

- The pattern doc flags this as a docs-vs-adoption conflict — docs (★) recommend two separate marketplaces with different `name` values. Community uniformly uses `@ref` pinning. This repo follows community.

## Multi-harness distribution

Not applicable. This plugin targets Claude Code only. — No multi-harness parallel manifests, no cross-ecosystem content mirrors.

## Version control and release cadence

**Scheme (Option E, confirmed).** Plain semver `x.y.z` in `plugin.json`; tags live on main; no release branches. Pre-commit hook auto-bumps `z` on commits that touch the plugin tree (excluding plugin.json-only commits). Release cut = bump `y`, reset `z=0`, commit with only plugin.json staged (hook skips bump), tag `v<x.y.0>` on that commit. Patch release = tag a specific main commit as `v<current-version>`; no edit required because z already increments per commit.

Pre-first-release, main stays at `0.0.z` (current state) until `v0.1.0` is cut after this refactor completes.

**Default branch.** `main`. ✓ Dominant (16/18).

**Tag placement.** Tags on main (once the Option E scheme is active). ✓ Dominant (14/14). Current state: `v0.1.0` tag exists at a historical commit predating this refactor and no longer represents a usable release — needs re-pointing or re-cutting when the first real release lands.

**Release branching.** None under Option E. ✓ Dominant (13/14 tagged repos). The legacy `v0.1.0` branch that exists today serves no purpose under Option E and should be deleted as part of release prep. No action item requires Option E's adoption; cleanup happens when the destructive-remote gate is crossed.

**Pre-release suffixes.** Plain semver only. ✓ Dominant (12/14). One minor outlier under Option E: `z` auto-increments per commit rather than holding at the last-release value. Preserves cache-reload detection for dev-channel users; specifically-justified deviation.

## Plugin-component registration

**Style.** `skills: ["./systems/"]` — explicit default-path array in `plugin.json`. ✓ Matches the second-most-common pattern (~12/54 use explicit path arrays — substantially more common than the earlier "1/21" count suggested). Self-documenting and valid.

**Agent frontmatter.** Does not ship custom agents. — Not applicable.

## Dependency installation

**Install location.** `${CLAUDE_PLUGIN_DATA}/venv` via uv. ✓ Dominant (~12/20) + ★ docs-prescribed.

**Change detection.** `diff -q` on `requirements.txt` against cached copy in `$CLAUDE_PLUGIN_DATA/`; venv-existence fallback triggers reinstall if venv is missing. ✓ Matches docs-prescribed idiom (12/20). **Resolved** this session.

**Retry-next-session invariant.** `rm -f $CLAUDE_PLUGIN_DATA/requirements.txt` on install failure (via bash ERR trap). Next session's `diff -q` sees a missing cached manifest and retries. ✓ Matches docs worked-example pattern. **Resolved** this session.

**Failure signaling.** Plain stderr (`echo ... >&2`) + `exit 1`. ✓ Matches community norm — 1/20 repos emit `systemMessage` JSON; docs worked-example uses silent retry (no JSON output). The earlier "Gap — emit systemMessage JSON" action item was withdrawn after pattern-doc corrections showed it was not docs-prescribed.

**Runtime variant.** Python venv via uv. ✓ Aligns with the ~8/20 Python-venv shape.

**Install timing.** SessionStart install (not bin-wrapper lazy install, not hybrid). ✓ Dominant pattern; appropriate since deps are required for every plugin operation.

**Pointer-file pattern for bin wrappers.** `install_deps.sh` writes `$CLAUDE_PLUGIN_ROOT/.venv-python` when `bin/` exists. ✓ Matches anthril/ppc-manager pattern — the most robust observed option for bridging SessionStart install and bin invocation.

## Bin-wrapped CLI distribution

**Ships `bin/`.** Yes — `plugins/ocd/bin/ocd-run`.

**Runtime resolution.** 6-step fallback chain: `$CLAUDE_PLUGIN_DATA` → `.venv-python` pointer → cache-path derivation → `--plugin-dir` inline-mode derivation → self-contained dev checkout → system `python3`. ⟁ Outlier (14/23 use the simple env-var-with-fallback form). This repo's chain is strictly more robust — handles every observed invocation context including `--plugin-dir` dev mode. Defensible.

**Shebang.** `#!/bin/bash`. ✓ 4/23 — minority but common.

**Venv handling.** Direct `exec "$_venv_python" "$plugin_root/run.py" "$@"`. ✓ Preferred pattern (not `source activate`).

**Platform support.** Nix-only. ✓ 17/23.

**chmod +x.** File is mode 100755 in git (verified).

## User configuration

Does not use `userConfig`. — Not applicable. Plugin's configuration surface is minimal and uses project-local files (rules, conventions) rather than per-user prompted settings.

## Tool-use enforcement

**Hooks.** Ships `auto_approval` (matches `Bash|Edit|Write`) and `convention_gate` (matches `Read|Edit|Write`) as PreToolUse handlers with 10s timeouts.

**Output and failure convention.** Audit pending this session. Expected patterns: stderr summary on block (BULDEE-style, CHANGELOG v3.4.4 precedent), top-level try/catch with fail-open or fail-closed posture (Kanevry-style centralized helpers).

- **Gap — action item 2 (audit + fix if needed):** inspect `auto_approval` and `convention_gate` for JSON-only-to-stdout ("No stderr output") anti-pattern and bare `exit 1` crash path (BULDEE v3.4.4 / Kanevry REQ-01 precedents).

## Session context loading

Not implemented in this repo. — Not applicable.

## Live monitoring and notifications

Not implemented in this repo. — Not applicable.

## Plugin-to-plugin dependencies

Single-plugin marketplace. — Not applicable.

## Project-level tooling layout

**Location.** Project-level operations live at project root under `tools/` and are exposed through `bin/plugins-run`. Specifically: `tools/testing/` (test discovery, runner, venv resolution, detached-worktree wrapper) and `tools/setup/` (git hookspath configuration). ✓ Matches universal convention — 0/54 sampled repos package project-level orchestration inside a plugin.

- **Resolved** (was a prior outlier): the test runner previously lived inside `plugins/ocd/systems/framework/` and was invoked through `ocd-run tests`. That was a layering inversion — project-level orchestration routed through a plugin's binary. Moved out to `tools/testing/` + `bin/plugins-run` during this pass.
- **Resolved** (was a prior outlier): the ocd plugin's `init` used to auto-wire this project's `.githooks/` via `git config core.hookspath`. Moved to `bin/plugins-run setup`, making the hookspath decision explicit per checkout rather than imposed by plugin install.
- `scripts/test.sh` and `scripts/release.sh` remain at project root as thin delegators / release helpers.

## Testing and CI

**Tests location.** `tests/` at repo root with per-plugin subdirs (`tests/plugins/ocd/`). ⟁ Rare (1/10). Only observed precedent: `affaan-m/everything-claude-code`. Per-plugin nesting is the sole way to keep dev artifacts out of user plugin caches when multiple plugins live in one repo. Defensible.

**Pytest configuration location.** `tests/plugins/ocd/pyproject.toml` under `[tool.pytest.ini_options]`. ✓ Matches the 6/10 community convention (pyproject.toml for pytest config). **Resolved** — action item 3 from a prior diff.

**Python dependency manifest format.** `plugins/ocd/requirements.txt`. ✗ Outlier (1/7 in the sample uses `requirements.txt`; 6/7 use `pyproject.toml`).

- **Gap — action item 3:** move runtime dep declarations into `plugins/ocd/pyproject.toml` under `[project.dependencies]` (or equivalent). Update `install_deps.sh` to reference the new manifest path. Update change-detection target. Update the install_deps integration tests' fixture.

**CI workflows.** Absent — workflows were removed in commit `70def06` pending CI/CD research (now complete). ✗ Outlier (15/18 have at least one workflow; 9/18 have ci.yml or equivalent push/PR pytest).

- **Gap — action item 4:** reintroduce CI workflow. Minimum shape (from pattern-doc research): `push: [branches: [main]]` + `pull_request`, single-runtime (ubuntu-latest, Python 3.11 or equivalent), direct `bash scripts/test.sh` invocation. Matrix unnecessary for a Python-only single-plugin repo; can add later if multi-OS support becomes a priority.

## Release automation

**`release.yml`.** Absent (removed in `70def06`). ✗ 5/14 tagged repos have one.

- **Gap — action item 5:** add `.github/workflows/release.yml` triggered on `v*` tag push. Per pattern research, this repo's shape should include deep tag-sanity gates (verify tag format, verify tag is on a `release/*` branch, verify tag matches `plugin.json` version) since this repo's versioning policy enforces release-branch-only tagging. Requires `workflow` scope on the GitHub PAT.

**Release script.** `scripts/release.sh` exists. ✓ Pairs with `release.yml` when that lands.

## Marketplace validation

**Validation workflow.** Absent (`validate.yml` was part of the `70def06` removal). ✗ ~8/54 have a dedicated validator script; ~41/54 have none.

- **Gap — action item 6:** reintroduce `validate.yml` using schema-based validation (Python+json or bun + plain TypeScript), not `claude plugin validate` CLI invocation. Per pattern research, 0/54 sampled repos wire the CLI into CI; Anthropic's own `claude-plugins-official` uses bun + plain TypeScript (~65-line manual shape checker, no zod library).

## Documentation

**README.md at repo root.** Present. ✓ 18/18.

**CHANGELOG.md.** Present. ✓ 9/18.

**architecture.md at repo root.** Present. ✓ 2/18 (rare but high-signal).

**CLAUDE.md.** Present. ✓ ~22/54 — now common for active plugins (earlier "rare" framing was stale).

**Per-plugin `README.md`.** Present (`plugins/ocd/README.md`). ✓ 12/18.

**Community health files.** Absent. ⟁ Rare in sample but signals "serious project."

- *Optional refinement:* add `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`. Not a gap — signal, not requirement.

## Action-item summary

Ordered by estimated effort / impact. Numbering reflects the current list after earlier action items were resolved or dropped.

**Resolved:**

- **`install_deps.sh`** has `diff -q` change detection + `rm` retry invariant via bash ERR trap. Integration tests cover first-run, unchanged-manifest, changed-manifest, missing-venv, failure-rm, and idempotency cases.
- **`pytest.ini` → `pyproject.toml`** consolidation.
- **`tools/` + `bin/plugins-run`** extracted from plugin (test runner, venv resolution, sandbox-tests, setup) — closes the project-level-inside-plugin layering inversion.
- **Pattern doc** restructured to purpose-oriented + 17 corrections applied + new "Multi-harness distribution" and "Project-level tooling layout" purpose sections.
- **Versioning scheme** confirmed as Option E (tag-on-main, no release branches, dev counter on z).
- **Per-verb integration test coverage** — every callable surface (scripts, hooks, tools, every system's `__main__.py` CLI dispatch) now has at least one test exercising it. `rules/ocd/testing.md`'s Callable Surface Coverage bar is met. The remaining piece — automating the check as a `/ocd:check` dimension — is tracked in `logs/idea/Callable-surface coverage crawler.md` (build the machinery, not add more tests).

**Dropped:**

- **~~Emit JSON `systemMessage` on install failure.~~** Pattern-doc correction showed this was not docs-prescribed. Current stderr approach is consistent with the docs worked example.
- **~~Rename `v0.1.0` branch → `release/0.1`.~~** Under Option E, release branches don't exist. Legacy branch should be deleted outright (not renamed) when destructive-remote gate is crossed; action item 1 below subsumes this.

**Open:**

1. **Hook output convention audit** — inspect `auto_approval` and `convention_gate` for JSON-only-to-stdout anti-pattern and bare-`exit 1` crash path. Fix if found. Small, self-contained.
2. **`requirements.txt` → `[project.dependencies]` in `pyproject.toml`** — mechanical move, update `install_deps.sh` to reference new path, update change-detection cached-copy target, update install_deps test fixture. Small.
3. **Add `.github/workflows/ci.yml`** — requires `workflow` scope on PAT. Single-runtime, `bash scripts/test.sh`.
4. **Add `.github/workflows/release.yml`** — requires PAT. Shape under Option E: trigger on `push: tags: ['v*']`, verify tag format, verify tag-commit `plugin.json` version matches tag, run tests, `gh release create --generate-notes`.
5. **Add `.github/workflows/validate.yml`** — requires PAT. Schema-based validation (Python+json or bun+plain TS).
6. **Delete legacy `v0.1.0` branch + re-point or delete historical `v0.1.0` tag** — destructive remote op, deferred until actual `v0.1.0` release is cut after refactor+cleanup completes.
7. **Community health files** (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`) — optional polish, deferred.

## Novel-but-defensible choices

Annotated with updated adoption signal from the 54-repo deep research:

- **SessionStart hook installing into per-plugin `${CLAUDE_PLUGIN_DATA}/venv`** — dominant (~12/20 of the dep-management sample) and ★ docs-prescribed. This repo matches the majority.
- **Auto-bump `z` per commit on main (Option E)** — preserves Claude Code's reload detection for dev-channel users tracking main. The auto-bump-z behavior is not directly observed in the sample (most repos hold at last-release version between tags), but the rest of the scheme aligns with convention: tags on main, no release branches, plain semver format. Minor justified deviation.
- **Per-plugin nested tests under `tests/plugins/<name>/`** — matches `affaan-m/everything-claude-code` precedent; consistent with the 9/10 tests-at-repo-root convention.
- **6-step bin-wrapper runtime resolution chain** — more elaborate than the 14/23 simple env-var-with-fallback pattern, but handles the `--plugin-dir` dev-mode case that simpler wrappers break in. Defensible complexity, especially for a development-loop-heavy plugin.
- **Pointer-file pattern (`.venv-python`)** — matches anthril/ppc-manager's pattern (1/23 observed); the most robust observed bridge between SessionStart install and bin invocation for a plugin with non-trivial venv resolution needs.
- **Project-level `bin/plugins-run` + `tools/` layout** — matches the universal community convention (0/54 package project-level orchestration inside a plugin). `bin/plugins-run` is a bash dispatcher resolving the project venv and invoking `tools/` modules; mirrors the ergonomic property of plugin-scoped bins (on PATH, callable by short name) at project scope.

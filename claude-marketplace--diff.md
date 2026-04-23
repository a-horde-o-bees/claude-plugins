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

**Tag placement.** Tags on main under Option E. ✓ Dominant (14/14). No tags currently exist; `v0.1.0` will be the first tagged release on main.

**Release branching.** None under Option E. ✓ Dominant (13/14 tagged repos). The legacy `v0.1.0` branch and historical tag have been removed; no cleanup remains.

**Pre-release suffixes.** Plain semver only. ✓ Dominant (12/14). One minor outlier under Option E: `z` auto-increments per commit rather than holding at the last-release value. Preserves cache-reload detection for dev-channel users; specifically-justified deviation.

## Plugin-component registration

**Style.** `skills: ["./systems/"]` — explicit default-path array in `plugin.json`. ✓ Matches the second-most-common pattern (~12/54 use explicit path arrays — substantially more common than the earlier "1/21" count suggested). Self-documenting and valid.

**Agent frontmatter.** Does not ship custom agents. — Not applicable.

## Description as the discovery surface

**Framing.** 8 skills use action-verb-led prose. Mix of patterns: `/ocd:log` uses explicit "Reach for this when..." trigger-verb framing (strongest docs alignment); `/ocd:git`, `/ocd:check`, `/ocd:setup`, `/ocd:refactor`, `/ocd:sandbox` lead with action verbs ("Manage", "Run", "Execute", "Work on") followed by scope; `/ocd:pdf`, `/ocd:navigator` are shorter action descriptors without explicit when-to-use framing. ⟁ Mixed alignment — most skills match the 9/14 trigger-verb cohort in spirit, `/ocd:log`'s explicit "Reach for this when..." form is the strongest match docs-wise. Sharpening the shorter descriptions toward explicit trigger-verb framing is low-cost polish; not a release blocker.

**Length.** 8 SKILL.md descriptions span ~50-530 characters (well under the 1,536-char docs cap). Falls into the medium-to-long cluster observed across the corpus for description-matched skills.

**Few-shot patterns.** Not used. — Not applicable; skills are user-invocable rather than auto-discovered via agent-matching where `<example>`/`<commentary>` XML blocks pay off.

**Multilingual triggers.** Not applicable — English-only.

## Command and skill frontmatter

**Commands vs skills.** Ships 0 commands under `commands/` and 8 skills under `plugins/ocd/systems/<skill>/SKILL.md`. The BULDEE `name:`-on-commands defect does not apply here since we don't ship slash commands separate from skills.

**SKILL.md `name:` discipline.** 8/8 skills declare `name:` in frontmatter. ✓ Matches the universal SKILL.md 8/8 convention — skills pin identity against directory moves.

**`argument-hint` format.** All skills use the ★ docs-prescribed typed angle-bracket form. Examples: `check` (`"<dormancy | all> [<system-name>] [--plugin <path>]"`), `navigator` (`"[directory-path]"`), `setup` (full verb-and-flag enumeration). ✓ 8/8 typed form; no prose-form drift.

**`allowed-tools` syntax.** YAML-list form with permission-rule scoping where narrow scopes matter — e.g. `Bash(ocd-run:*)` restricts bash to the plugin CLI only. ✓ Matches the YAML-array cohort (2/14 in sample) with permission-rule scoping added as lukasmalkmus/moneymoney demonstrated (scope-limiting as UX).

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

**Output and failure convention.** Both hooks emit `hookSpecificOutput` JSON with the appropriate `permissionDecision` (`allow` for convention_gate, `allow`/`deny` for auto_approval). `auto_approval.__main__` wraps dispatch in a top-level try/except that writes one stderr line and exits 0 on any unhandled exception — fail-open matches the hook's auto-approval role (a crash must never block a tool call; Claude Code's user-prompt fallback takes over). Blocks surface a human-readable reason via `permissionDecisionReason`, which Claude Code relays to the agent. ✓ Matches the Kanevry-style centralized-helper pattern.

## Agent delegation patterns

Does not ship agents. — Not applicable. Skill-to-skill invocation happens via the in-session Skill tool (e.g. `/checkpoint` calling `/ocd:git`); no plugin-shipped agents under `agents/` exist. The pattern doc's three sub-patterns (hook-enforced scope walls, skill composition, non-canonical frontmatter) apply to repos that ship agents — not to this single-skill-surface plugin.

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

**Python dependency manifest format.** `plugins/ocd/pyproject.toml` under `[project.dependencies]`. ✓ Matches the dominant 6/7 convention. **Resolved** — `install_deps.sh` references the new manifest path; change-detection target and install_deps integration fixture updated.

**CI workflows.** `.github/workflows/ci.yml` — `push: [branches: [main]]` + `pull_request`, single-runtime (ubuntu-latest), `uv sync` + plugin-venv bootstrap + `bash scripts/test.sh`. ✓ Matches the 9/18 push/PR pytest shape. **Resolved**.

**Fixture discipline.** Tests run against real backends throughout — real SQLite for navigator, real `git` subprocess via the session-scoped `sandbox_worktree` fixture for integration tests that mutate repo state, real `ocd-run` subprocess for CLI coverage, real plugin venv for install_deps tests. No `unittest.mock` usage. Function-scoped `tmp_path` for filesystem isolation. Opt-in real-agent tests gated by `pytest.mark.agent` + `--run-agent` CLI flag. ✓ Aligns with the ecosystem's real-backends-over-mocks convention (0/5 of sampled Python suites use `unittest.mock`). Opt-in-gate pattern matches SkinnnyJay's env-var gate intent via pytest's native marker mechanism. Worktree-isolation fixture (unique to this project per the sample — no shared convention observed) is documented in `rules/ocd/testing.md` as the canonical primitive.

## Release automation

**`release.yml`.** Present. Triggered on `v*` tag push. Tag-sanity gates: verifies tag matches `vX.Y.Z` format, verifies `plugin.json` version at the tag commit equals the tag's version, runs tests, creates GitHub release with `gh release create --generate-notes`. Option E shape — no release-branch check (tags live on main). ✓ Matches the 5/14 tagged-repo shape. **Resolved**.

**Release script.** `scripts/release.sh` exists. ✓ Pairs with `release.yml`.

## Marketplace validation

**Validation workflow.** `.github/workflows/validate.yml` runs `python3 scripts/validate-manifests.py` on push/PR to main. Schema-based shape check against `.claude-plugin/marketplace.json` and each plugin's `plugin.json` — matches Anthropic's `claude-plugins-official` bun+plain-TS pattern in spirit (no CLI `claude plugin validate` invocation). ✓ Matches the ~8/54 dedicated-validator shape. **Resolved**.

## Documentation

**README.md at repo root.** Present. ✓ 18/18.

**CHANGELOG.md.** Present, Keep-a-Changelog format (dated `## [version] — date` sections with `### Added` sub-headings; v0.1.0 is the first entry). ✓ 9/18 presence; matches the ~17/27 Keep-a-Changelog-explicit cohort among repos that ship a CHANGELOG.

**Release-notes source.** `release.yml` uses `gh release create --generate-notes` — auto-generated from commits/PRs for the tag range. ✓ Matches the ~8/15 release-workflow-repos majority. Trade-off: CHANGELOG narrative and release page notes are decoupled (CHANGELOG reads as curated history; release page reads as commit manifest). Threading CHANGELOG into the release body (Chachamaru's awk-extraction pattern) is available if the decoupling becomes noticeable friction.

**CHANGELOG-as-runtime artifact.** Not applicable — CHANGELOG is for human/author consumption only; no skill fetches it at runtime (unlike BaseInfinity's `/update-wizard` pattern).

**`ARCHITECTURE.md` at repo root.** Present. ✓ 5/5 of the repos that place an architecture doc at repo root use the uppercase form — 100% dominance for this location. Across all 18 sample repos that ship an architecture doc anywhere (root or under `docs/`), uppercase leads ~11/18. Prior audit's "2/18" figure collapsed case into one bucket and undercounted; corrected here. Uppercase aligns with the sibling root-doc convention (`README.md`, `CHANGELOG.md`, `LICENSE`, `SECURITY.md`) — agent-facing all-caps is the dominant signal across the ecosystem.

**CLAUDE.md.** Present. ✓ ~22/54 — now common for active plugins (earlier "rare" framing was stale).

**Per-plugin `README.md`.** Present (`plugins/ocd/README.md`). ✓ 12/18.

**Community health files.** Absent. ⟁ Rare in sample but signals "serious project."

- *Optional refinement:* add `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`. Not a gap — signal, not requirement.

## Action-item summary

All blocking marketplace-convention items are resolved. From a marketplace-alignment standpoint the repository is releasable as `v0.1.0`.

**Resolved:**

- **`install_deps.sh`** has `diff -q` change detection + `rm` retry invariant via bash ERR trap. Integration tests cover first-run, unchanged-manifest, changed-manifest, missing-venv, failure-rm, and idempotency cases.
- **`pytest.ini` → `pyproject.toml`** consolidation.
- **`tools/` + `bin/plugins-run`** extracted from plugin (test runner, venv resolution, sandbox-tests, setup) — closes the project-level-inside-plugin layering inversion.
- **Pattern doc** restructured to purpose-oriented + 17 corrections applied + new "Multi-harness distribution" and "Project-level tooling layout" purpose sections.
- **Versioning scheme** confirmed as Option E (tag-on-main, no release branches, dev counter on z).
- **Per-verb integration test coverage** — every callable surface (scripts, hooks, tools, every system's `__main__.py` CLI dispatch) now has at least one test exercising it. `rules/ocd/testing.md`'s Callable Surface Coverage bar is met. The remaining piece — automating the check as a `/ocd:check` dimension — is tracked in `logs/idea/Callable-surface coverage crawler.md` (build the machinery, not add more tests).
- **Hook output convention** — `auto_approval` and `convention_gate` both emit `hookSpecificOutput` with proper `permissionDecision`; `auto_approval.__main__` wraps dispatch in a fail-open try/except that writes one stderr line and exits 0 on unhandled exceptions. No bare `exit 1` crash path; no JSON-only-to-stdout anti-pattern.
- **`requirements.txt` → `[project.dependencies]` in `pyproject.toml`** — mechanical move complete; `install_deps.sh`, change-detection target, and install_deps test fixture all reference the new path.
- **`.github/workflows/ci.yml`** — push/PR on main, single-runtime, `uv sync` + plugin-venv bootstrap + `bash scripts/test.sh`.
- **`.github/workflows/release.yml`** — triggers on `v*` tag push, verifies tag format + `plugin.json` version alignment, runs tests, creates release with `--generate-notes`.
- **`.github/workflows/validate.yml`** — schema-based manifest validation via `scripts/validate-manifests.py`.
- **Legacy `v0.1.0` branch + historical tag** — both removed from local and remote. The next `v0.1.0` will be the first real release on main.

**Dropped:**

- **~~Emit JSON `systemMessage` on install failure.~~** Pattern-doc correction showed this was not docs-prescribed. Current stderr approach is consistent with the docs worked example.
- **~~Rename `v0.1.0` branch → `release/0.1`.~~** Under Option E, release branches don't exist; legacy branch + tag were deleted outright.

**Open:**

1. **Community health files** (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`) — optional polish, not a release blocker.

## Novel-but-defensible choices

Annotated with updated adoption signal from the 54-repo deep research:

- **SessionStart hook installing into per-plugin `${CLAUDE_PLUGIN_DATA}/venv`** — dominant (~12/20 of the dep-management sample) and ★ docs-prescribed. This repo matches the majority.
- **Auto-bump `z` per commit on main (Option E)** — preserves Claude Code's reload detection for dev-channel users tracking main. The auto-bump-z behavior is not directly observed in the sample (most repos hold at last-release version between tags), but the rest of the scheme aligns with convention: tags on main, no release branches, plain semver format. Minor justified deviation.
- **Per-plugin nested tests under `tests/plugins/<name>/`** — matches `affaan-m/everything-claude-code` precedent; consistent with the 9/10 tests-at-repo-root convention.
- **6-step bin-wrapper runtime resolution chain** — more elaborate than the 14/23 simple env-var-with-fallback pattern, but handles the `--plugin-dir` dev-mode case that simpler wrappers break in. Defensible complexity, especially for a development-loop-heavy plugin.
- **Pointer-file pattern (`.venv-python`)** — matches anthril/ppc-manager's pattern (1/23 observed); the most robust observed bridge between SessionStart install and bin invocation for a plugin with non-trivial venv resolution needs.
- **Project-level `bin/plugins-run` + `tools/` layout** — matches the universal community convention (0/54 package project-level orchestration inside a plugin). `bin/plugins-run` is a bash dispatcher resolving the project venv and invoking `tools/` modules; mirrors the ergonomic property of plugin-scoped bins (on PATH, callable by short name) at project scope.

# Marketplace Standards

Commitments this marketplace repository makes for each purpose a Claude Code plugin marketplace has to address. Each section states the standard this project follows and a one-line rationale. Ecosystem context, observed adoption counts, and alternatives considered live in the consolidated research at [logs/research/claude-marketplace/consolidated.md](logs/research/claude-marketplace/consolidated.md), backed by 54 per-repo samples under `logs/research/claude-marketplace/samples/`.

Graduated from the former `claude-marketplace--diff.md` alignment audit once alignment work stabilized. The methodology that produced this doc is captured in the [alignment-audit pattern](logs/patterns/alignment-audit.md).

## Marketplace discoverability

**Standard.** Single `.claude-plugin/marketplace.json` at repo root. Top-level `description` field (no `metadata` wrapper). Per-plugin `category: "development"` with no `tags` or `keywords`. `$schema` reference present (`https://anthropic.com/claude-code/marketplace.schema.json`). Marketplace name is `a-horde-o-bees` (no conflict with reserved names).

**Why.** Single-manifest layout is the 17/18 dominant shape. Top-level `description` matches `claude-plugins-official` (the highest-signal adopter). `$schema` reference is a high-signal minority (~6/54 — all Anthropic-aligned or thoughtful community repos).

## Plugin source binding

**Standard.** Relative string source (`"./plugins/ocd"`). Default `strict: true` (implicit). Version declared in `plugin.json` only.

**Why.** Relative string is 14/18 dominant. Default strict matches 16/21 + 1/21 explicit. Version in plugin.json is 10/14 dominant for relative-path sources.

## Channel distribution

**Standard.** No channel split declared in marketplace manifest. Users pin channels via `@ref` syntax (e.g. `@v0.1.0` for stable, no pin for dev-tracking-main). README documents both paths.

**Why.** Docs recommend two separate marketplaces with different `name` values, but 18/18 sampled repos use `@ref` pinning instead. Community convention chosen over docs prescription.

## Multi-harness distribution

**Standard.** Not applicable — this marketplace targets Claude Code only. No parallel manifests for Codex, Cursor, OpenCode, or other agent hosts.

**Why.** Single-host focus. Cross-ecosystem distribution is a meaningful axis for some projects (affaan-m and similar) but adds coordination cost without benefit when only one host is targeted.

## Version control and release cadence

**Standard.** Option E — plain `x.y.z` semver in `plugin.json`. Tags live on `main`; no release branches. Pre-commit hook auto-bumps `z` on commits that stage changes to the plugin tree (excluding plugin.json-only commits). Release cut = bump `y`, reset `z = 0`, commit with only `plugin.json` staged (hook skips bump), tag `v<x.y.0>` on that commit. Patch release = tag a specific main commit as `v<current-version>`; no edit required because `z` already increments per commit.

**Why.** Tags-on-main is 14/14 dominant among tagged repos. No release branches matches 13/14. Auto-bump `z` per commit is a specific deviation (most repos hold at last-release version between tags) that preserves Claude Code's reload detection for dev-channel users tracking main. `scripts/release.sh` automates the release-cut sequence.

## Plugin-component registration

**Standard.** Explicit default-path array: `"skills": ["./systems/"]` in `plugin.json`. Does not ship custom agents.

**Why.** Explicit path arrays are ~12/54 — the second-most-common pattern, self-documenting about which directories contain components. No agents is the default since no delegation-to-subagent workflow is needed.

## Description as the discovery surface

**Standard.** Skill descriptions use action-verb-led framing. Prefer explicit "when to use" form (e.g. `/ocd:log`'s "Reach for this when..."). No agent descriptions (no agents shipped). No `<example>`/`<commentary>` few-shot blocks (not needed — skills are user-invocable, not description-matched by the agent matcher). English-only.

**Why.** Trigger-verb framing aligns with ★ docs-prescribed guidance ("Front-load the key use case") and the 9/14 trigger-verb cohort. `/ocd:log`'s explicit form is the strongest docs match; shorter descriptors on `/ocd:pdf` and `/ocd:navigator` are tracked as open polish in `TASKS.md`.

## Command and skill frontmatter

**Standard.** Zero commands under `commands/`. Eight skills under `plugins/ocd/systems/<skill>/SKILL.md`. All skills declare `name:` in frontmatter. All skills use ★ docs-prescribed typed angle-bracket `argument-hint` (e.g. `"<verb>"`, `"<verb | verb>"`, `"[optional-flag]"`). `allowed-tools` uses YAML-list form with permission-rule scoping where narrow scope matters (e.g. `Bash(ocd-run:*)` to restrict bash to the plugin CLI only).

**Why.** SKILL.md `name:` 8/8 convention; typed `argument-hint` is the only form aligned with docs examples. The BULDEE `name:`-on-commands defect doesn't apply since no commands are shipped.

## Dependency installation

**Standard.** SessionStart hook (`hooks/install_deps.sh`) installs Python packages from `plugins/ocd/pyproject.toml` into `${CLAUDE_PLUGIN_DATA}/venv` using `uv`. Change detection via `diff -q` against cached copy in `$CLAUDE_PLUGIN_DATA/`. On install failure, `rm -f $CLAUDE_PLUGIN_DATA/pyproject.toml` via bash ERR trap — next session's diff retries. Writes `$CLAUDE_PLUGIN_ROOT/.venv-python` pointer file when `bin/` exists to bridge to bin-wrapper invocation. Failure signaling via plain stderr + `exit 1`.

**Why.** SessionStart + `${CLAUDE_PLUGIN_DATA}/venv` is ★ docs-prescribed and 12/20 dominant. `diff -q` change detection + rm-on-failure retry matches the docs worked example. Pointer file pattern matches anthril/ppc-manager — the most robust observed option for bridging SessionStart install and bin invocation.

## Bin-wrapped CLI distribution

**Standard.** Ships `plugins/ocd/bin/ocd-run`. Shebang `#!/bin/bash`. File mode 100755 in git. Runtime resolution uses a 6-step fallback chain: `$CLAUDE_PLUGIN_DATA` → `.venv-python` pointer → cache-path derivation → `--plugin-dir` inline-mode derivation → self-contained dev checkout → system `python3`. Direct `exec "$_venv_python" "$plugin_root/run.py" "$@"` — no `source activate`. Nix-only.

**Why.** More elaborate than the 14/23 simple env-var-with-fallback shape, but handles every observed invocation context including `--plugin-dir` dev mode that simpler wrappers break on. Defensible complexity for a development-loop-heavy plugin.

## User configuration

**Standard.** Does not use `userConfig`. Configuration surface uses project-local files (rules, conventions) rather than per-user prompted settings.

**Why.** No per-user secrets, API keys, or preferences needed. When a second plugin requires user configuration, follow the pattern doc's guidance: correct `sensitive: true` application, `${user_config.KEY}` substitution or `CLAUDE_PLUGIN_OPTION_<KEY>` env bridging, per the observed correctness split.

## Tool-use enforcement

**Standard.** Ships two PreToolUse hooks with 10s timeouts:

- `auto_approval` (matches `Bash|Edit|Write`) — hardcoded structural blocks + dynamic settings-based allow/deny. Wraps dispatch in top-level try/except (fail-open) that writes one stderr line and exits 0 on any unhandled exception. Approvals emit `hookSpecificOutput.permissionDecision: allow`. Denials emit `permissionDecision: deny` with `permissionDecisionReason` carrying corrective guidance.
- `convention_gate` (matches `Read|Edit|Write`) — non-blocking. Emits `permissionDecision: allow` with `additionalContext` surfacing applicable conventions from `.claude/conventions/`.

**Why.** Hook output via `hookSpecificOutput` schema matches Kanevry's centralized-helper pattern and avoids the BULDEE JSON-only-to-stdout anti-pattern. Fail-open posture is appropriate for an auto-approval hook: a crash must never block a tool call; Claude Code's default permission prompt takes over instead.

## Session context loading

**Standard.** Not implemented. The plugin does not inject persistent context at session start beyond what `.claude/rules/` auto-loading provides.

**Why.** No knowledge-base or persistent-memory surface needed. Rules auto-loading covers project-level guidance.

## Live monitoring and notifications

**Standard.** Not implemented.

**Why.** No notification surface (webhook-style push, etc.) is part of this plugin's scope.

## Plugin-to-plugin dependencies

**Standard.** Flat-by-convention. Each plugin in this marketplace is independent at runtime. Shared infrastructure (framework code under `systems/framework/`, permissions templates, hooks like `install_deps.sh`) is propagated across plugins via the pre-commit hook, so every plugin carries a self-contained copy. If genuine runtime coupling emerges (plugin B calls plugin A's CLI or MCP server at session start), add a SessionStart guard in the dependent plugin that verifies the sibling's reachability and emits a corrective message on absence. Reach for the native `dependencies` field only when runtime coupling can't be solved by propagation + guard.

**Why.** 0/54 verified adoption of Claude Code v2.1.110+'s native `dependencies` field — the feature is too new to have percolated, and dual-tag namespace overhead (`<plugin>--v{version}` alongside plain `v{version}`) isn't worth the cost without ecosystem traction. Flat-by-convention matches anthropics/knowledge-work-plugins' deliberate stance. Propagation via pre-commit hook is this project's specific mechanism for "self-contained at runtime despite sharing source."

## Project-level tooling layout

**Standard.** Project-level operations tied to this repository's development infrastructure live at project root under `tools/` (specifically `tools/testing/` for test discovery, runner, venv resolution, and detached-worktree wrapping; `tools/setup/` for git hookspath configuration). Exposed through `bin/project-run` — a bash entry point that resolves the project venv and dispatches to `tools/` modules. `scripts/` at project root holds release helpers (`scripts/release.sh`, `scripts/auto_init.py`, `scripts/validate-manifests.py`).

**Why.** 0/54 sampled repos package project-level orchestration inside a plugin — placing dev infrastructure inside `plugins/` is a layering inversion that leaks dev state into end-user plugin caches. `bin/project-run` mirrors the ergonomic property of plugin-scoped bins (on PATH, callable by short name) at project scope.

## Runner binary naming

**Standard.** `<scope>-run` — every runnable scope ships a bash wrapper at `bin/<scope>-run` that resolves the appropriate Python interpreter and dispatches to a module of the same scope. Plugin scope uses the plugin name (`ocd-run`, `blueprint-run`); the project-root scope uses `project-run`. Wrappers live in `bin/` so Claude Code's per-plugin `bin/` PATH-inclusion (and the project-level equivalent) surfaces them as short callable names.

**Why.** One naming rule across scopes keeps the PATH-surface predictable — no reader has to remember whether the project-level runner is `plugins-run`, `repo-run`, or `claude-run`. Short names without scope qualifiers (`run`) would collide across plugins; long names with version qualifiers would break PATH discipline. `<scope>-run` is the narrowest unambiguous form. Agents interacting with permissions (`Bash(project-run:*)`, `Bash(ocd-run:*)`) see a consistent shape, and each scope's permission entry is self-describing.

## Testing and CI

**Standard.** Tests at project root under `tests/` with per-plugin subdirs (`tests/plugins/ocd/`). Per-plugin pytest config in `tests/plugins/<plugin>/pyproject.toml` under `[tool.pytest.ini_options]`. Python dependency manifest at `plugins/ocd/pyproject.toml` under `[project.dependencies]`. CI workflow at `.github/workflows/ci.yml` — triggers on `push: [main]` + `pull_request`, single-runtime (ubuntu-latest), runs `uv sync` + plugin-venv bootstrap + `bin/project-run tests`. Tests use real backends throughout (SQLite in-memory, real `git` subprocess, real `ocd-run` invocation); no `unittest.mock`. Fixture scopes: session for expensive setup (`sandbox_worktree` wraps `systems.sandbox`), function for per-test isolation (`tmp_path`). Real-agent tests gated by `pytest.mark.agent` and selected via `--run-agent` — the flag is a mode switch (without it the deterministic suite runs and agent tests are skipped; with it, only agent-marked tests run). Unknown flags forward verbatim from `bin/project-run tests` to pytest (e.g. `bin/project-run tests --plugin ocd --run-agent`).

**Why.** Per-plugin test nesting under `tests/` is rare (1/10 precedent — affaan-m/everything-claude-code) but the only way to keep dev artifacts out of user plugin caches when multi-plugin. `pyproject.toml` for pytest config matches 6/10 community convention. Real-backend discipline matches 0/5 mock-usage across sampled Python suites. `pytest.mark.agent` gate matches SkinnnyJay's `RUN_CLAUDE_TESTS` env-var gate in intent (2/5 ecosystem adoption of explicit opt-in gates).

## Release automation

**Standard.** `.github/workflows/release.yml` triggered on `push: tags: ['v*']`. Gates: verify tag format matches `^v\d+\.\d+\.\d+$`, verify `plugin.json` version at tag commit equals the tag's version (Option E — no release-branch check). On success: run tests, create GitHub Release via `gh release create --generate-notes`. `scripts/release.sh` automates the operator-side release-cut sequence (bump plugin.json, print next steps).

**Why.** Tag-sanity gates (format + version alignment) match 2/6 tag-triggered repos. `gh release create --generate-notes` is the 3/6 dominant source for release body text.

## Marketplace validation

**Standard.** `.github/workflows/validate.yml` — runs `python3 scripts/validate-manifests.py` on push/PR to main. Schema-based shape check against `.claude-plugin/marketplace.json` and each plugin's `plugin.json`.

**Why.** Schema validation matches Anthropic's `claude-plugins-official` bun+plain-TS pattern in spirit. 0/54 sampled repos wire the `claude plugin validate` CLI into CI — the in-tree schema checker is the community norm.

## Documentation

**Standard.** Three-document model at every system boundary — `README.md` (user-facing), `ARCHITECTURE.md` (developer-facing), `CLAUDE.md` or `SKILL.md` (agent-facing). Project-root: `README.md`, `ARCHITECTURE.md`, `CLAUDE.md`, `CHANGELOG.md`, `LICENSE`, `MARKETPLACE-STANDARDS.md`. Per-plugin: `README.md`, `ARCHITECTURE.md`. Substantive subsystems (governance, navigator) have their own `README.md` + `ARCHITECTURE.md`; thin subsystems consolidate into a single README. Filename case follows the rule in `rules/system-docs.md` — all-caps for entry points at a system boundary, lowercase for content within a structure. `CHANGELOG.md` uses Keep-a-Changelog format (dated `## [version] — date` sections with `### Added` sub-headings). Release notes sourced via `gh release create --generate-notes` (CHANGELOG narrative and release-page notes are decoupled — CHANGELOG reads as curated history, release page reads as commit manifest). No CHANGELOG-as-runtime-consumed pattern. Community health files (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`) deferred — not blocking for a personal project with no external contributors.

**Why.** README 18/18 universal. Keep-a-Changelog matches ~17/27 explicit adopters (the dominant CHANGELOG format). `--generate-notes` matches 8/15 majority source. All-caps at-repo-root `ARCHITECTURE.md` matches 5/5 root-level adoption. CLAUDE.md at ~22/54 is common for active plugins. Community health files absent is ~40/54 minority behavior — rare but defensible for personal projects.

## Novel-but-defensible choices

Consolidated list of deliberate deviations from convention, with justification preserved:

- **Auto-bump `z` per commit on main (Option E).** Preserves Claude Code's reload detection for dev-channel users tracking main. Most repos hold plugin.json at the last-release version between tags; this project increments per commit. Minor deviation with specific justification.
- **Per-plugin nested tests under `tests/plugins/<name>/`.** 1/10 precedent. The only way to keep dev artifacts out of user plugin caches when multi-plugin.
- **6-step bin-wrapper runtime resolution chain.** More elaborate than the 14/23 simple form, but handles `--plugin-dir` dev-mode that simpler wrappers break in.
- **Pointer-file pattern (`.venv-python`).** 1/23 observed (anthril/ppc-manager). The most robust observed bridge between SessionStart install and bin invocation.
- **Project-level `bin/project-run` + `tools/` layout.** 0/54 — novel as a concrete mechanism, but matches the universal convention that project-level orchestration doesn't live inside a plugin.

## Provenance

This doc graduated from the alignment-audit artifact that lived at `claude-marketplace--diff.md` before stabilizing. The audit methodology is captured at [`logs/patterns/alignment-audit.md`](logs/patterns/alignment-audit.md). The ecosystem research this aligns against is at [`logs/research/claude-marketplace/consolidated.md`](logs/research/claude-marketplace/consolidated.md) with 54 per-repo samples under `logs/research/claude-marketplace/samples/`. Outstanding work (items that were open in the audit or surfaced later) is tracked in [`TASKS.md`](TASKS.md) and the idea logs under `logs/idea/`.

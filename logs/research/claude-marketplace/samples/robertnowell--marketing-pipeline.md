# robertnowell/marketing-pipeline

## Identification

- **URL**: https://github.com/robertnowell/marketing-pipeline
- **Stars**: 2
- **Last commit date**: 2026-04-20 (77 commits; repo created 2026-04-11, so ~9 days of history — cycle-driven churn dominates, 50+ commits are automated `cycle: post` bot commits from `.github/workflows/daily.yml`)
- **Default branch**: main
- **License**: MIT (declared in `plugin.json` + `README.md`; no GitHub-detected `license` field in repo metadata because there is no `LICENSE` file at root — only a README "## License" section. Observed gap)
- **Sample origin**: bin-wrapper (single-file `bin/marketing` is the sample trigger; repo also independently satisfies dep-management via SessionStart venv install, so multiple — list: bin-wrapper, dep-management)
- **One-line purpose**: "Automated distribution pipeline for open source developer tools. Onboard a project from its README, launch to MCP Registry + directories, post to Bluesky/Dev.to/Hashnode/Mastodon, track engagement." (from `plugin.json.description`)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, single-plugin marketplace whose plugin `source: "./"` points back at the same repo root — i.e., the marketplace manifest and the plugin manifest coexist in one repository
- **Marketplace-level metadata**: top-level `description` string ("Automated distribution pipeline for open source developer tools") — no `metadata.{description, version, pluginRoot}` wrapper
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `category: "productivity"` only — no `tags`, no `keywords` on the marketplace entry (plugin.json has a `keywords` array: `["marketing", "social-media", "mcp", "developer-tools", "distribution"]` but those live in plugin.json, not the marketplace entry)
- **`$schema`**: present, `https://anthropic.com/claude-code/marketplace.schema.json`
- **Reserved-name collision**: no — "marketing-pipeline-marketplace" and "marketing-pipeline" are custom names
- **Pitfalls observed**: marketplace entry carries only `name`/`description`/`category`/`source` — no `version` field on the entry (version lives solely in `plugin.json`). Users who want to pin via the marketplace are forced to pin at Git level (`@ref`) rather than selecting a version dimension the marketplace surfaces.

## 2. Plugin source binding

- **Source format(s) observed**: `relative` — `"source": "./"` (the single plugin lives at repo root alongside the marketplace manifest)
- **`strict` field**: absent — relies on implicit default (true)
- **`skills` override on marketplace entry**: absent — skills auto-discovered from `skills/` directory via strict-default discovery
- **Version authority**: `plugin.json` only (`version: "0.1.0"`) — marketplace entry has no version; plugin.json is the sole authority
- **Pitfalls observed**: `./` source binding means the marketplace is the plugin — a single-repo self-referential pattern. Fine for solo-plugin repos but not composable: no way to add a second plugin without restructuring.

## 3. Channel distribution

- **Channel mechanism**: no split — single `main` branch, no tags, no stable/latest separation. Users pin via `@<ref>` if desired, but nothing in the repo structure exposes a pinnable channel surface.
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: version declared as `0.1.0` in plugin.json but never bumped in 77 commits; main is under active development with no release discipline. Any user who installs today gets HEAD at install time and has no mechanism to track updates short of re-running `claude plugin install`.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: no tags in the repo (`gh api /tags` returns `[]`)
- **Release branching**: none — development happens directly on main; no `release/*` or `v*` branches
- **Pre-release suffixes**: not applicable (no tags, no releases)
- **Dev-counter scheme**: absent — plugin.json is frozen at `0.0.1`... observed `0.1.0` across every commit I sampled; no per-commit bump
- **Pre-commit version bump**: no (no evidence of a hook bumping plugin.json; version unchanged across 77 commits)
- **Pitfalls observed**: no GitHub release ever cut (`gh api /releases` returns `[]`), no tag ever pushed. This plugin has zero versioning discipline — every install takes HEAD. Conventional commit subjects (e.g., "Fix plugin.json schema: add type/title to userConfig") suggest the author uses commit messages as the changelog surrogate.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — plugin.json declares no `skills`/`commands`/`agents`/`hooks`/`mcpServers` fields at all. Every component is auto-discovered from the canonical directory (`skills/`, `hooks/hooks.json`).
- **Components observed**:
    - skills: yes (7 — cycle, draft, launch, onboard, post, report, setup, status — actually 8: cycle, draft, launch, onboard, post, report, setup, status)
    - commands: no
    - agents: no
    - hooks: yes (`hooks/hooks.json` declares a single SessionStart hook)
    - `.mcp.json`: no
    - `.lsp.json`: no
    - monitors: no
    - bin: yes (`bin/marketing` — single executable; exposed to skills via `Bash(marketing *)` allowed-tools)
    - output-styles: no
- **Agent frontmatter fields used**: not applicable — no agents
- **Agent tools syntax**: not applicable — no agents. (Skills, however, use permission-rule syntax in `allowed-tools`: e.g., `Bash(marketing cycle *)`, `Bash(marketing validate *)`, `Bash(cat *)`, `Read`, `Write`, `WebSearch`, `WebFetch` — mixed permission-specifiers and plain tool names.)
- **Pitfalls observed**: skill frontmatter fields include a non-standard `user-invocable: true` on every skill. The Claude Code plugins reference does not document this field — either author-invented (and ignored by the runtime) or undocumented behavior. If ignored, it is dead metadata; if respected, it's an undocumented dependency.

## 6. Dependency installation

- **Applicable**: yes
- **Dep manifest format**: pyproject.toml (PEP 621 project metadata; dependencies in `[project].dependencies`; `[project.scripts]` exposes a `marketing` console-script entry but the bin wrapper ignores it in favor of `python -m pipeline.cli`)
- **Install location**: `${CLAUDE_PLUGIN_DATA}/venv` — created by the SessionStart hook
- **Install script location**: `hooks-handlers/session-start.sh` (invoked from `hooks/hooks.json` via `bash "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/session-start.sh"`)
- **Change detection**: custom sha256 hash over `pipeline/**/*.py + pyproject.toml + *.md`, stored at `${CLAUDE_PLUGIN_DATA}/.deps-hash`, compared on every SessionStart. If mismatch or venv missing, runs `pip install --force-reinstall "$PLUGIN_ROOT"`. Note the hash intentionally covers source code too, not just `pyproject.toml` — the commit "Fix stale venv: hash pipeline code, not just pyproject.toml" captures the rationale.
- **Retry-next-session invariant**: no `rm` on failure — script is `set -euo pipefail`, so if `pip install` fails the hook exits non-zero. No explicit cleanup of partial venv or hash file. The hash file is only written after successful install (line order), so a failed install leaves the old hash → next session will retry the install on the same hash mismatch, which is a quiet form of retry.
- **Failure signaling**: `set -euo pipefail` halts the hook. Python version check emits a JSON `hookSpecificOutput.additionalContext` with `ERROR:` prefix to stderr and `exit 1`. Pip install failure just dies with pip's stderr. Success emits JSON `hookSpecificOutput.additionalContext` summarizing project/post counts.
- **Runtime variant**: Python pip — `python3 -m venv` then `"$VENV_DIR/bin/pip" install --force-reinstall "$PLUGIN_ROOT"`. No `uv`, no `uvx`. Targets Python 3.12+; enforces at hook start by parsing `python3 --version`.
- **Alternative approaches**: none used — no PEP 723 inline metadata, no pointer files, no `uvx`/`npx` ad-hoc. Just venv + pip + `--force-reinstall`.
- **Version-mismatch handling**: Python 3.12+ enforced via major/minor parse-and-compare at the top of SessionStart. No Python-minor-version tracking in the venv directory name — a user who upgrades system Python from 3.12 to 3.13 keeps the old `venv/` with stale Python binary symlinks until the hash changes.
- **Pitfalls observed**:
    - `--force-reinstall` on every hash change is correct but slow (re-fetches all transitive wheels). No per-package diffing.
    - The hash covers `*.md` files too, so editing README triggers a venv reinstall — over-eager invalidation.
    - Hash uses `find ... | xargs cat | shasum -a 256`, which is not order-deterministic across filesystems if `find`'s output order varies; `sort` is applied after `find` to stabilize.
    - No hash-file lock — concurrent SessionStart invocations (rare, but possible in split-session workflows) could race on the hash file.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — this is the sample origin
- **`bin/` files**:
    - `bin/marketing` — Python CLI wrapper: activates the plugin-managed venv, resolves `--file` args against `$ORIG_CWD` before cd'ing, cd's to `$STATE_DIR`, then `exec python -m pipeline.cli "$@"`
- **Shebang convention**: `#!/usr/bin/env bash`
- **Runtime resolution**: `${CLAUDE_PLUGIN_DATA}` with `$HOME/.claude/plugins/data/marketing-pipeline` fallback. Notably does NOT consult `${CLAUDE_PLUGIN_ROOT}` in the bin wrapper — only PLUGIN_DATA — so if the runtime does not set PLUGIN_DATA, the wrapper guesses a conventional location. `${MARKETING_STATE_DIR}` environment variable also consulted and takes precedence for STATE_DIR (populated by the SessionStart hook writing to `$CLAUDE_ENV_FILE`).
- **Venv handling (Python)**: **`source activate` then `exec python`** — the anti-pattern explicitly flagged in the research prompt. Exact sequence (`bin/marketing` lines 14-25):
    ```bash
    VENV_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/marketing-pipeline}/venv"
    # ...
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    # ...
    exec python -m pipeline.cli "${args[@]}"
    ```
    **Does it actually work?** Yes — `source activate` in a bash script mutates the current process's `$PATH` to prepend `$VENV_DIR/bin`, sets `VIRTUAL_ENV`, and deactivates any prior venv. The subsequent `exec python` resolves `python` via the updated `$PATH`, so the venv's `python` is the one invoked, and `-m pipeline.cli` imports from the venv's `site-packages`. The mechanism is correct.
    **Why it is still an anti-pattern:** it is strictly weaker than `exec "$VENV_DIR/bin/python" -m pipeline.cli "$@"`. The direct-exec form:
    - Skips the sourcing of ~50 lines of `activate` script (performance noise and shellcheck warning surface — note `# shellcheck disable=SC1091` is needed exactly to suppress the warning that `activate` can't be resolved)
    - Does not pollute the execing shell's environment (irrelevant here because `exec` replaces the shell anyway, but philosophically cleaner)
    - Works identically under `sh` and `dash` with minor tweaks; `source` is bash-only
    - Is not dependent on the venv's `activate` script being well-formed (some stripped-down venvs, or uv-managed venvs without `activate`, would break the `source` path)
    The guard `if [ ! -f "$VENV_DIR/bin/activate" ]` right above the source call actually tests for the activate script's presence — revealing that the author is aware the activate script is required, but not that it is unnecessary.
- **Platform support**: nix-only (`#!/usr/bin/env bash`, `source`, POSIX path separators, shellcheck hint). No Windows `.cmd`/`.ps1` counterpart. macOS + Linux implied — `python3 --version` parse works on both.
- **Permissions**: 100755 (executable) — confirmed via `git/trees` blob mode on `bin/marketing`.
- **SessionStart relationship**: hook builds and populates the venv in `${CLAUDE_PLUGIN_DATA}/venv`, then writes `MARKETING_STATE_DIR` to `$CLAUDE_ENV_FILE` so subsequent bin invocations in the same Claude session find the state dir via env var. The bin wrapper itself does no downloading/installing — it fails loudly with a remediation message if the venv is absent:
    ```
    Error: marketing pipeline venv not initialized.
    Start a new Claude Code session to trigger setup, or run:
      bash "$(dirname "$0")/../hooks-handlers/session-start.sh"
    ```
    This is a coupled design — bin depends on SessionStart having run, but the error message gives the user a manual path back in.
- **Pitfalls observed**:
    - `source activate` anti-pattern as documented above — functionally correct, structurally redundant.
    - `--file` argument resolution walks `"$@"` with a `next_is_file=true` flag, which handles `--file path` but NOT `--file=path` (the equals form would be passed through unresolved). Undocumented limitation.
    - `cd "$STATE_DIR"` changes CWD so CWD-relative paths inside the pipeline resolve to the state dir — but this means any user-passed relative path that isn't `--file` (e.g., `--config myproj.yml`) silently resolves against `$STATE_DIR`, not `$PWD`. The `--file`-only resolution is partial coverage of the cd-before-exec surface.
    - `exec python` depends on `$PATH` order post-source; if a conda init (or another venv activate) runs in the user's shell rc between PLUGIN_DATA assignment and source, there could be path shadowing. Direct-exec of the absolute path would bypass this class of issue.

## 8. User configuration

- **`userConfig` present**: yes
- **Field count**: 11 fields (ANTHROPIC_API_KEY, BLUESKY_HANDLE, BLUESKY_APP_PASSWORD, DEVTO_API_KEY, HASHNODE_PAT, HASHNODE_PUBLICATION_ID, MASTODON_ACCESS_TOKEN, MASTODON_INSTANCE_URL, SLACK_WEBHOOK_URL, PINTEREST_ACCESS_TOKEN, PINTEREST_BOARD_ID)
- **`sensitive: true` usage**: correct for actual secrets (API keys, app passwords, access tokens, webhooks, PATs) — ANTHROPIC_API_KEY, BLUESKY_APP_PASSWORD, DEVTO_API_KEY, HASHNODE_PAT, MASTODON_ACCESS_TOKEN, SLACK_WEBHOOK_URL, PINTEREST_ACCESS_TOKEN all `sensitive: true`. Non-secret identifiers (handles, URLs, publication IDs, board IDs) are `sensitive: false`. The distinction is applied cleanly.
- **Schema richness**: typed — every field has `title`, `description`, `type: "string"`, `sensitive`, `required`. No `default`, no enum-narrowing, no pattern/regex validation.
- **Reference in config substitution**: `CLAUDE_PLUGIN_OPTION_<KEY>` env var pattern — the SessionStart hook reads these env vars and writes `export KEY="${CLAUDE_PLUGIN_OPTION_KEY}"` lines into `$CLAUDE_ENV_FILE`, bridging plugin-option names to conventional dotenv-style names (e.g., `CLAUDE_PLUGIN_OPTION_BLUESKY_HANDLE` → `BLUESKY_HANDLE`). No `${user_config.KEY}` substitution in hook/MCP commands (none have this shape).
- **Pitfalls observed**:
    - Bridging credentials via `$CLAUDE_ENV_FILE` is fine but duplicates the value into a file on disk — security depends on file mode of `$CLAUDE_ENV_FILE` (not controlled by this plugin).
    - ANTHROPIC_API_KEY is marked `required: false` with description "Only needed for GitHub Actions cron, not for plugin use" — an unusual inversion where the plugin-supplied credential is for CI, not the plugin itself. Encoded in description prose, not structure; a user reading only the field list would expect it to be needed for the plugin.
    - Pinterest fields (`PINTEREST_ACCESS_TOKEN`, `PINTEREST_BOARD_ID`) are declared in userConfig but NOT bridged in `session-start.sh` — the session-start bridge block only exports Bluesky/Dev.to/Hashnode/Mastodon/Slack credentials plus ANTHROPIC_API_KEY. Pinterest credentials go unexported. Plugin calls to the Pinterest publisher would see empty env vars even with plugin options set. Observed defect: userConfig declares credentials the session-start hook does not bridge. The cron workflow (`launch.yml`) uses GitHub Actions secrets directly so the bug only surfaces for interactive plugin use.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: SessionStart emits stdout JSON `{"hookSpecificOutput":{"additionalContext":"..."}}`; Python-version error emits the same JSON to stderr before `exit 1`. So a mixed convention — stdout for success, stderr for the Python-version-missing failure.
- **Failure posture**: fail-closed on Python version (exit 1, no context); fail-closed on venv install failure (pipefail halts). No fail-open paths.
- **Top-level try/catch wrapping**: not applicable — bash, uses `set -euo pipefail` and defensive `2>/dev/null || true` on individual commands (python3 parse, mkdir cp)
- **Pitfalls observed**: no enforcement of tool-use (no PreToolUse), so skill-level `allowed-tools` permission rules are the only gate on what the agent can call. Consistent with a "trust the skill frontmatter" design; not a gap so much as a chosen scope.

## 10. Session context loading

- **SessionStart used for context**: yes — emits `hookSpecificOutput.additionalContext` that summarizes pipeline state (`"Marketing pipeline ready: X projects, Y posts tracked. Use /onboard to add a project, /status to see current state."`)
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: yes — populated with project/post counts on success, ERROR text on Python version failure
- **SessionStart matcher**: `""` (empty string) — not documented whether this means "all sub-events" or "only startup"; per Claude Code plugins-reference the empty matcher for SessionStart fires on startup/clear/compact alike. Author treats it as every-session.
- **Pitfalls observed**: the context summary recomputes PROJECT_COUNT and POST_COUNT by grepping state files on every session start (`grep -c "^[a-z]" projects.yml`, `grep -c "^- project:" manifest.yml`). Cheap enough, but tightly coupled to the exact file formats — a schema change in those files would produce zero counts silently.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: not applicable — the plugin gets its "monitoring" surface entirely through GitHub Actions cron (`.github/workflows/daily.yml`) rather than Claude Code monitors. This is an interesting pattern — long-running scheduled behavior outsourced to CI infrastructure, with the plugin providing interactive onboarding/drafting/posting only.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none — plugin.json does not declare a `dependencies` key
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin repo with no tags
- **Pitfalls observed**: not applicable

## 13. Testing and CI

- **Test framework**: pytest (`pyproject.toml [tool.pytest.ini_options]` + dev dependency `pytest>=8.0.0`; also `pytest-asyncio>=0.23.0`)
- **Tests location**: `tests/` at repo root (6 test files: test_antislop, test_config, test_lister, test_publishers, test_registry, test_surfaces)
- **Pytest config location**: `[tool.pytest.ini_options]` in pyproject.toml — `testpaths = ["tests"]`, `pythonpath = ["."]`
- **Python dep manifest for tests**: pyproject.toml under `[project.optional-dependencies].dev` (pytest, ruff, pytest-asyncio)
- **CI present**: yes
- **CI file(s)**: `.github/workflows/test.yml`, `.github/workflows/daily.yml`, `.github/workflows/launch.yml`
- **CI triggers**:
    - test.yml — `push: branches: [main]` + `pull_request: branches: [main]`
    - daily.yml — `schedule: cron "0 10,12,14,16,18 * * *"` (five fires per day every day) + `workflow_dispatch` with a `dry_run` boolean input (default true)
    - launch.yml — `workflow_dispatch` only with `project` (required string) + `dry_run` (boolean, default true)
- **CI does**:
    - test.yml — `ruff check pipeline/ tests/` + `pytest tests/ -v`
    - daily.yml — install dep, `marketing cycle` (or `--dry-run`), commit updated state, run `marketing report --no-sync`, upload artifacts
    - launch.yml — install deps, install `mcp-publisher` CLI from GitHub releases, set GitHub topics, publish to MCP Registry via OIDC, optional npm publish, directory listing, draft generation, posting
- **Matrix**: none — all workflows hard-code Python 3.12 and ubuntu-latest
- **Action pinning**: major-tag pinning (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`, `actions/upload-artifact@v4`). No SHA pinning.
- **Caching**: none — no `actions/cache` nor `setup-python` `cache: pip` usage. Every CI run re-installs wheels from scratch.
- **Test runner invocation**: direct `pytest tests/ -v` (no wrapper script, no `uv run`)
- **Pitfalls observed**:
    - `test.yml` runs only on `push` to main and PRs against main, but daily.yml and launch.yml cycle-commit frequently to main ("cycle: post" commits) — 50+ automated commits / week — which triggers test runs on every bot commit, burning CI minutes for no code change. Could gate on path filters (e.g., `paths: ['pipeline/**', 'tests/**', 'pyproject.toml']`).
    - No matrix means Python 3.13 compatibility is untested, even though `requires-python = ">=3.12"` permits it.
    - Launch workflow has `id-token: write` for MCP Registry OIDC publishing — a genuinely sophisticated piece of release automation tucked into what is nominally a marketing tool.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — no workflow matches "release", "tag", "publish", or triggers on `release: [published]` / `push: tags:`
- **Release trigger**: not applicable
- **Automation shape**: not applicable for plugin releases. Launch.yml does do product distribution automation (MCP Registry publish via `mcp-publisher`, npm publish gated on `mcpName` in package.json, directory lister) but the target is customer projects referenced in `projects.yml`, not the plugin itself. No self-release automation.
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable (no CHANGELOG.md)
- **Pitfalls observed**: the author ships an installable Claude Code plugin with zero release engineering — no tags, no releases, no automation. Plugin installs take HEAD. This is the direct consequence of the purpose-6/7 choices: because dep-install is hash-gated on `SessionStart`, the plugin self-heals on every session, so version pinning becomes semantically meaningless. Trade-off: no reproducibility if the user wants to downgrade, but no stale-venv burden either.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: not applicable
- **Hooks.json validation**: not applicable
- **Pitfalls observed**: `$schema` is declared in `marketplace.json` but there is no workflow that validates against it. Validation relies on Claude Code rejecting malformed manifests at install time — fail-late rather than fail-at-commit.

## 16. Documentation

- **`README.md` at repo root**: present (~4.3 KB, ~80 lines — install + use + what-it-does + anti-slop explainer + credentials table + supported surfaces + project-types + dev instructions + license)
- **`README.md` per plugin**: not applicable (single-plugin repo; the root README is the plugin README)
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: absent
- **`CLAUDE.md`**: absent
- **Community health files**: none (no SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, ISSUE_TEMPLATE, or PR_TEMPLATE)
- **LICENSE**: absent as a file (claimed "MIT" in README ## License section and plugin.json `"license": "MIT"`, but no LICENSE file at root — GitHub's license-detection returns `null`)
- **Badges / status indicators**: absent — no CI badge, no pypi badge, no stars badge in README
- **Pitfalls observed**:
    - Missing LICENSE file while claiming MIT is a legal-hygiene gap; "license: null" in the GitHub API means license tooling (e.g., GH API license queries, tldr-legal) will not recognize this repo.
    - No CHANGELOG.md combined with no tags means users have no consolidated view of what changed between their last install and now; the only signal is `git log` on main.
    - Skill-level docs live only in each `SKILL.md` frontmatter + body. For a plugin with 8 skills, a user would benefit from an overview, but the README doesn't enumerate skills by name — it markets by outcome ("talk to Claude"). Reasonable for marketing copy; thin for technical discovery.

## 17. Novel axes

- **Source-activate bin-wrapper pattern (explicitly noted).** Explicit `source "$VENV_DIR/bin/activate"` → `exec python -m module` sequence. Strictly weaker than direct `exec "$VENV_DIR/bin/python" -m module`. Works correctly because `source activate` mutates `$PATH` within the shell before `exec python` resolves. Pattern decision documented here to contrast against cleaner direct-exec patterns the pattern doc may want to recommend.
- **Hash-gated dep install covering source code, not just manifest.** `SessionStart` hashes `pipeline/**/*.py + pyproject.toml + *.md`. Invalidation on source-code edit (not just manifest change) is a deliberate choice, rationalized in commit "Fix stale venv: hash pipeline code, not just pyproject.toml". Most plugins hash only the manifest; this one treats the installed package itself (via `pip install .`) as the unit to hash because the plugin installs itself from source.
- **userConfig bridge to dotenv-style env vars via `$CLAUDE_ENV_FILE`.** SessionStart rewrites `CLAUDE_PLUGIN_OPTION_<KEY>` env vars as `export KEY=...` lines appended to `$CLAUDE_ENV_FILE`. Decouples the plugin's user-config namespace from the conventional env-var names the CLI library and test suite expect. Reusable pattern for plugins whose CLI was designed for standalone `.env` use and needs to keep working inside the plugin harness.
- **Bin wrapper `cd`-before-exec with argument rewriting.** `bin/marketing` resolves `--file` relative paths against `$ORIG_CWD` BEFORE `cd "$STATE_DIR"`. Because the CLI's CWD is forced to the state directory, any relative path passed by the user would otherwise resolve to the wrong base. Partial coverage: handles `--file` only, not other relative-path flags.
- **Claude-Code plugin as interactive front-end, GitHub Actions cron as durable scheduler.** No `monitors.json`, no background plugin execution — long-running behavior (daily cycle, engagement reports) runs in GH Actions on a repo the user must have write access to. Plugin is the "author/debug" surface; CI is the "operate" surface. Interesting hybrid architecture for plugins whose primary value is durable scheduled work.
- **Self-dogfooding marketplace.** Marketplace manifest + plugin manifest coexist in the same repo with `"source": "./"`, so the marketplace IS the plugin. Trivially deployable but not extensible to multi-plugin.
- **Undocumented `user-invocable: true` in every SKILL.md frontmatter.** Not in plugins-reference. Either author-invented or early-access. Pattern-doc candidate for "uncommon frontmatter fields observed in the wild".
- **State-directory separation from plugin root.** State (`content/`, `reports/`, `projects.yml`) lives under `${CLAUDE_PLUGIN_DATA}/state`, seeded from `${CLAUDE_PLUGIN_ROOT}/defaults/*.yml` on first run. Code and state cleanly separated — one is read-only immutable (plugin root), the other is read-write mutable (plugin data). Durable across plugin upgrades because upgrades overwrite plugin root but not plugin data.
- **`--force-reinstall` on every hash mismatch.** Brute-force reinstall instead of diff-based upgrade. Simpler than tracking per-package state; wastes bandwidth + time but guarantees correctness.

## 18. Gaps

- **Whether `user-invocable: true` in SKILL.md is runtime-recognized or dead metadata.** Would need to read Claude Code source or test empirically; plugins-reference doesn't mention it.
- **Whether `CLAUDE_ENV_FILE` write appending (`>> "$CLAUDE_ENV_FILE"`) is idempotent or accumulates on repeated SessionStart.** Script appends, so on every session a fresh set of `export` lines is added. The shell that sources this file will see the later `export` overriding the earlier (bash semantics), so functionally idempotent, but the file grows monotonically. Could be confirmed by examining a live `$CLAUDE_ENV_FILE` across multiple sessions — not available from GitHub API alone.
- **Python minor-version change behavior.** If a user on Python 3.12 upgrades to 3.13, the existing `venv/` has symlinks to 3.12's `python3.12` binary. The hash-gate will only trigger reinstall if the source or pyproject changes, not if system Python changes. Would need runtime observation to confirm behavior; inferred failure mode from code read.
- **Whether Pinterest credential-bridging gap is intentional.** `PINTEREST_ACCESS_TOKEN`/`PINTEREST_BOARD_ID` declared in userConfig but not exported in `session-start.sh` bridge. Could be a bug from Pinterest being added later (commit "Add Pinterest publisher, Kopi content fetcher, content_source field" postdates the session-start.sh), or could be intentional (Pinterest runs only in cron). Reading recent commits on Pinterest files would resolve but was not pursued within budget.
- **Whether `0.1.0` version is semantically meaningful or frozen placeholder.** Never bumped across 77 commits. With no tags and no releases, no downstream consumer could rely on version. Could be "still pre-1.0" semantic or "author forgot to bump"; no commit message clarifies.
- **Exact behavior of `"./"` self-source with the CLI's `plugin marketplace add robertnowell/marketing-pipeline` command.** README says users invoke `claude plugin marketplace add robertnowell/marketing-pipeline && claude plugin install marketing-pipeline@marketing-pipeline-marketplace`. Would the Claude Code CLI recognize `./` as the plugin root relative to the marketplace manifest location, or would it look elsewhere? The plugins-reference describes `source` semantics generally but I didn't verify the exact `./` case for a marketplace co-located with its plugin. Inferred to work from the fact that the repo is installable per README instructions, but not empirically confirmed within budget.
- **Whether `marketing` bin is PATH-surfaced by the plugin harness or only invoked by allowed-tools.** Every SKILL.md declares `Bash(marketing *)` permission rules, implying that `marketing` is on PATH inside the Claude shell. Confirmed by plugins-reference documenting `${CLAUDE_PLUGIN_ROOT}/bin` being prepended to PATH. Verifiable by reading the plugins-reference again; confirmed by context-resource inspection but not re-checked here.

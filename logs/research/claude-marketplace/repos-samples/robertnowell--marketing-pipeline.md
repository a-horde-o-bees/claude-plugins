# Sample

Mirrors of `https://github.com/robertnowell/marketing-pipeline`. Automated distribution pipeline for open source developer tools — onboards a project from its README, launches to MCP Registry + directories, posts to Bluesky/Dev.to/Hashnode/Mastodon, and tracks engagement. MIT-licensed (declared in plugin.json + README, no LICENSE file at root); 2 stars at sample time; current tip is on `main` (commit 2026-04-20, 77 commits in ~9 days, 50+ of which are bot-generated `cycle: post` commits from `.github/workflows/daily.yml`).

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root with one plugin entry pointing back at the same repo via `"source": "./"` — the marketplace IS the plugin. Marketplace name `marketing-pipeline-marketplace` and plugin name `marketing-pipeline` are custom (no reserved-name collision). Top-level `description` string ("Automated distribution pipeline for open source developer tools") with no `metadata.{description, version, pluginRoot}` wrapper. Marketplace entry carries `name`/`description`/`category`/`source` only — no per-entry `version` field, so version pinning is forced to git-ref level.

### `$schema` declaration on marketplace.json

`marketplace.json` declares `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` but no workflow validates against it — validation relies on Claude Code rejecting malformed manifests at install time.

## Plugin source binding

### Relative source pointing to repo root (`./`)

Marketplace entry has `"source": "./"`. Single plugin lives at repo root alongside the marketplace manifest.

### `strict` field default

`strict` field absent on the marketplace entry — relies on implicit-true default. No `skills` override on the entry; skills auto-discovered from `skills/` directory via strict-default discovery.

## Per-plugin discoverability metadata

### Category-only

Marketplace entry carries `category: "productivity"` only — no `tags`, no `keywords` on the marketplace entry. `plugin.json` independently carries `keywords: ["marketing", "social-media", "mcp", "developer-tools", "distribution"]` but those live in plugin.json, not the marketplace entry.

## Channel distribution

### No pinning surface

Single `main` branch, no tags, no stable/latest separation. Version `0.1.0` declared in plugin.json but never bumped across 77 commits; `gh api /tags` returns `[]` and `gh api /releases` returns `[]`. Users pin via `@<ref>` if they want, but nothing in the repo structure exposes a pinnable channel surface — every install takes HEAD.

## Tag and release lifecycle

### No tags at all

Zero tags ever pushed; zero GitHub releases cut. Conventional commit subjects (e.g., "Fix plugin.json schema: add type/title to userConfig") serve as the changelog surrogate. Plugin.json `version: "0.1.0"` is a frozen placeholder across the entire 77-commit history.

## Plugin-component registration

### Default convention discovery

`plugin.json` declares no `skills`/`commands`/`agents`/`hooks`/`mcpServers` fields — every component is auto-discovered from canonical directories.

## Component composition

### Skills (universal)

8 skills under `skills/` (cycle, draft, launch, onboard, post, report, setup, status).

### Hooks

`hooks/hooks.json` declares a single SessionStart hook invoking `bash "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/session-start.sh"`.

### bin

`bin/marketing` — single executable Python CLI wrapper, exposed to skills via `Bash(marketing *)` allowed-tools.

### Component types absent across the corpus

No commands, no agents, no `.mcp.json`, no `.lsp.json`, no monitors, no output-styles.

## Skill authoring conventions

### `allowed-tools` with permission-rule syntax

Skill frontmatter `allowed-tools` mixes permission-specifiers and plain tool names: `Bash(marketing cycle *)`, `Bash(marketing validate *)`, `Bash(cat *)`, `Read`, `Write`, `WebSearch`, `WebFetch`.

### Mixed `allowed-tools` syntax

Same skill files combine permission-rule entries (e.g., `Bash(marketing *)`) with bare tool names (`Read`, `Write`) inside one `allowed-tools` list.

## Bin entry mechanism

### Bash trampoline resolving python3 → python → py

`bin/marketing` is a bash wrapper with shebang `#!/usr/bin/env bash`, mode 100755. Sequence: resolve `${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/marketing-pipeline}/venv` as `VENV_DIR`; if `$VENV_DIR/bin/activate` is missing, error out with a remediation message ("Start a new Claude Code session to trigger setup, or run: bash $(dirname $0)/../hooks-handlers/session-start.sh"); resolve `--file` arguments against `$ORIG_CWD` before changing directories; `cd "$STATE_DIR"` (where `$STATE_DIR` comes from `$MARKETING_STATE_DIR` populated by SessionStart via `$CLAUDE_ENV_FILE`); then `source "$VENV_DIR/bin/activate"` (with `# shellcheck disable=SC1091`); finally `exec python -m pipeline.cli "${args[@]}"`. The `source activate` + `exec python` form is functionally correct (activate mutates `$PATH`, exec python resolves the venv's python, `-m pipeline.cli` imports from venv site-packages) but strictly weaker than `exec "$VENV_DIR/bin/python" -m pipeline.cli "$@"` which would skip ~50 lines of activate sourcing, drop the shellcheck-disable, work under sh/dash, and not depend on activate being well-formed. The `--file` argument resolution walks `"$@"` with a `next_is_file=true` flag, handling `--file path` but NOT `--file=path`. The `cd "$STATE_DIR"` means user-passed relative paths under flags other than `--file` (e.g., `--config myproj.yml`) silently resolve against `$STATE_DIR`, not `$PWD`.

### `${CLAUDE_PLUGIN_DATA}` with HOME fallback

Bin wrapper resolves the venv as `${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/marketing-pipeline}/venv`. Does not consult `${CLAUDE_PLUGIN_ROOT}`; only PLUGIN_DATA and the conventional HOME path.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

`bin/marketing` consults `${CLAUDE_PLUGIN_DATA}` first, falls back to `$HOME/.claude/plugins/data/marketing-pipeline` when unset. `$MARKETING_STATE_DIR` (written to `$CLAUDE_ENV_FILE` by SessionStart) takes precedence over the derived state dir for STATE_DIR resolution.

## Cross-platform discipline

### POSIX-only with no Windows story

`#!/usr/bin/env bash`, `source`, POSIX path separators, shellcheck hint — nix-only by design. No `.cmd` or `.ps1` counterpart. macOS + Linux implied; `python3 --version` parse works on both.

## Dependency installation

### Plugin-data venv with `diff -q` change detection

Dep manifest is `pyproject.toml` (PEP 621; dependencies in `[project].dependencies`). Install location is `${CLAUDE_PLUGIN_DATA}/venv` created by `hooks-handlers/session-start.sh` (invoked from `hooks/hooks.json` via `bash "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/session-start.sh"`). Install command is `python3 -m venv` followed by `"$VENV_DIR/bin/pip" install --force-reinstall "$PLUGIN_ROOT"` — i.e., the plugin treats itself as an installable Python package and reinstalls itself. `--force-reinstall` on every hash mismatch re-fetches all transitive wheels; no per-package diffing. Targets Python 3.12+; enforces at hook start by parsing `python3 --version`. No `uv`, no `uvx`. No Python-minor tracking in venv directory name — system Python upgrade keeps stale interpreter symlinks until the hash changes.

## Install change detection

### Diff-based byte comparison of manifest

Custom sha256 hash over `pipeline/**/*.py + pyproject.toml + *.md` (sorted via `find ... | sort | xargs cat | shasum -a 256`), stored at `${CLAUDE_PLUGIN_DATA}/.deps-hash`, compared on every SessionStart. Mismatch or missing venv triggers `pip install --force-reinstall "$PLUGIN_ROOT"`. The hash deliberately covers source code, not just `pyproject.toml` — rationale captured in commit "Fix stale venv: hash pipeline code, not just pyproject.toml". Side effect: editing README also triggers reinstall (over-eager invalidation). No hash-file lock — concurrent SessionStart could race on the file.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks-handlers/session-start.sh` is the SessionStart hook command in `hooks/hooks.json`. Bin wrapper itself does no installing — fails loudly if venv absent ("Error: marketing pipeline venv not initialized. Start a new Claude Code session to trigger setup, or run: bash $(dirname $0)/../hooks-handlers/session-start.sh").

## Install failure posture

### Implicit retry via late-write cache marker

Script is `set -euo pipefail`. The hash file is only written after successful install, so a failed install leaves the old hash in place and the next session re-enters the install branch on the same hash mismatch. No explicit `rm` cleanup of partial venv. Failure signal: `set -euo pipefail` halts the hook; pip stderr is the user-facing failure surface.

## Hook output contract

### `additionalContext` for context injection

SessionStart emits stdout JSON `{"hookSpecificOutput":{"additionalContext":"..."}}` summarizing pipeline state on success.

### Stderr for human display + stdout JSON for harness

Python-version error emits the same JSON shape to stderr before `exit 1` — mixed convention: stdout for success, stderr for the Python-version-missing failure.

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

Fail-closed on Python version (exit 1, no context); fail-closed on venv install failure (pipefail halts). No fail-open paths. `set -euo pipefail` plus defensive `2>/dev/null || true` on individual commands (python3 parse, mkdir cp).

## Hook handler runtime

### Bash scripts at conventional path

Single bash hook handler at `hooks-handlers/session-start.sh`. Strict mode on (`set -euo pipefail`).

## Session context loading

### `additionalContext` payload at SessionStart

SessionStart emits `hookSpecificOutput.additionalContext` populated with project/post counts on success ("Marketing pipeline ready: X projects, Y posts tracked. Use /onboard to add a project, /status to see current state."), ERROR text on Python version failure. Project/post counts are recomputed by grepping state files on every session start: `grep -c "^[a-z]" projects.yml`, `grep -c "^- project:" manifest.yml`. Cheap but tightly coupled to file format — schema change would silently produce zero counts.

## SessionStart matcher scope

### Empty matcher (all sub-events)

SessionStart matcher is `""` (empty string) — fires on every sub-event (startup/clear/compact). Author treats it as every-session.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. Long-running scheduled behavior runs in `.github/workflows/daily.yml` cron (5×/day) instead of via Claude Code monitors — the plugin is the interactive author/debug surface, GitHub Actions cron is the durable scheduler.

## Long-running scheduled behavior

### Outsourced to GitHub Actions cron

`.github/workflows/daily.yml` runs `schedule: cron "0 10,12,14,16,18 * * *"` (five fires per day) plus `workflow_dispatch` with a `dry_run` boolean (default true). Workflow installs deps, runs `marketing cycle` (or `--dry-run`), commits updated state with a `cycle: post` commit, runs `marketing report --no-sync`, uploads artifacts. This produces the 50+ automated bot commits dominating the commit history.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` does not declare a `dependencies` key — single-plugin repo with no cross-plugin deps.

## Testing

### Pytest with asyncio support

Test framework is pytest (declared dev dependency `pytest>=8.0.0` plus `pytest-asyncio>=0.23.0`). Test runner invocation: direct `pytest tests/ -v`, no wrapper script, no `uv run`.

### Centralized `tests/` placement

`tests/` at repo root with 6 test files: test_antislop, test_config, test_lister, test_publishers, test_registry, test_surfaces. `[tool.pytest.ini_options]` in pyproject.toml declares `testpaths = ["tests"]`, `pythonpath = ["."]`. Test deps in `[project.optional-dependencies].dev` (pytest, ruff, pytest-asyncio).

## CI workflow shape

### Multi-workflow split by trigger and concern

Three workflows: `.github/workflows/test.yml` (push to main + PR to main → `ruff check pipeline/ tests/` + `pytest tests/ -v`), `.github/workflows/daily.yml` (cron 5×/day + workflow_dispatch — install deps, marketing cycle, commit state, marketing report, upload artifacts), `.github/workflows/launch.yml` (workflow_dispatch with `project` required string + `dry_run` boolean — install deps, install `mcp-publisher` from GitHub releases, set GitHub topics, publish to MCP Registry via OIDC with `id-token: write`, optional npm publish, directory listing, draft generation, posting). All three hard-code Python 3.12 and ubuntu-latest — no matrix.

### Action-pinning conventions

Major-tag pinning across all workflows: `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`, `actions/upload-artifact@v4`. No SHA pinning.

### Test workflow with pinned actions, no caching

No `actions/cache`, no `setup-python` with `cache: pip`. Every CI run re-installs wheels from scratch.

## Release automation

### No release automation / manual

No workflow matches release/tag/publish/`release: [published]`/`push: tags:`. No tags, no GitHub releases, no self-release automation. Plugin installs take HEAD because dep-install is hash-gated on SessionStart so the plugin self-heals on every session — version pinning is semantically meaningless. Trade-off: no reproducibility for downgrade, no stale-venv burden. (Launch.yml does product distribution automation — MCP Registry publish via `mcp-publisher`, npm publish gated on `mcpName` in package.json — but the target is customer projects in `projects.yml`, not the plugin itself.)

## Marketplace validation

### No validation

No validation workflow, no validator script, no pre-commit hook, no `claude plugin validate` invocation. `$schema` declared in `marketplace.json` but no workflow checks against it. Validation relies on Claude Code rejecting malformed manifests at install time.

## Documentation surface

### README only

Repo-root `README.md` (~4.3 KB, ~80 lines) covering install, use, what-it-does, anti-slop explainer, credentials table, supported surfaces, project-types, dev instructions, license. Single-plugin repo so the root README is the plugin README.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md`, no `architecture.md`, no `CLAUDE.md`. Combined with no tags, users have no consolidated view of what changed between installs — only `git log` on main.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE`, or `PR_TEMPLATE`.

## License declaration

### License only in README prose

`README.md` carries a `## License` section claiming MIT and `plugin.json` carries `"license": "MIT"`, but no `LICENSE` file at root. GitHub's license-detection returns `null` because there is no `LICENSE` file; license tooling that queries GitHub API will not recognize this repo.

## User configuration and authentication

### Typed `userConfig` schema with rich field types

`userConfig` declares 11 fields (ANTHROPIC_API_KEY, BLUESKY_HANDLE, BLUESKY_APP_PASSWORD, DEVTO_API_KEY, HASHNODE_PAT, HASHNODE_PUBLICATION_ID, MASTODON_ACCESS_TOKEN, MASTODON_INSTANCE_URL, SLACK_WEBHOOK_URL, PINTEREST_ACCESS_TOKEN, PINTEREST_BOARD_ID). Every field has `title`, `description`, `type: "string"`, `sensitive`, `required`. No `default`, no enum-narrowing, no pattern/regex validation.

### `sensitive: true` flag absent on secret fields

Applied cleanly: actual secrets (API keys, app passwords, access tokens, webhooks, PATs) carry `sensitive: true`; non-secret identifiers (handles, URLs, publication IDs, board IDs) carry `sensitive: false`. Worth flagging the inverse case observed here: ANTHROPIC_API_KEY is `required: false` with description "Only needed for GitHub Actions cron, not for plugin use" — a structural inversion where the declared `userConfig` field is for an out-of-band consumer.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

SessionStart hook reads `CLAUDE_PLUGIN_OPTION_<KEY>` env vars supplied by the harness and writes `export KEY="${CLAUDE_PLUGIN_OPTION_KEY}"` lines into `$CLAUDE_ENV_FILE`, bridging plugin-option names to conventional dotenv-style names (e.g., `CLAUDE_PLUGIN_OPTION_BLUESKY_HANDLE` → `BLUESKY_HANDLE`). No `${user_config.KEY}` substitution in hook/MCP commands. Bridge block exports Bluesky/Dev.to/Hashnode/Mastodon/Slack credentials plus ANTHROPIC_API_KEY — but Pinterest fields (`PINTEREST_ACCESS_TOKEN`, `PINTEREST_BOARD_ID`) declared in userConfig are NOT bridged in `session-start.sh`. Plugin calls to the Pinterest publisher would see empty env vars even with plugin options set; the cron workflow (`launch.yml`) uses GitHub Actions secrets directly so the bug surfaces only for interactive plugin use.

## Cross-hook environment plumbing

### `$CLAUDE_ENV_FILE` append for cross-hook env vars

SessionStart appends `export <KEY>=...` lines to `$CLAUDE_ENV_FILE` so the bin wrapper finds `MARKETING_STATE_DIR` and dotenv-style credentials in subsequent shell invocations within the same session. Append is unconditional on every SessionStart — file grows monotonically across sessions if the harness does not truncate, but later `export` overrides earlier so functional idempotency holds.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code is read-only at `${CLAUDE_PLUGIN_ROOT}`. State (`content/`, `reports/`, `projects.yml`) lives under `${CLAUDE_PLUGIN_DATA}/state`, seeded from `${CLAUDE_PLUGIN_ROOT}/defaults/*.yml` on first run. Durable across plugin upgrades because upgrades overwrite plugin root but not plugin data.

## State persistence

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

Venv at `${CLAUDE_PLUGIN_DATA}/venv`. Hash stamp at `${CLAUDE_PLUGIN_DATA}/.deps-hash`. State directory at `${CLAUDE_PLUGIN_DATA}/state`.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse hooks, no PostToolUse hooks, no PermissionRequest/PermissionDenied hooks. Skill-level `allowed-tools` permission rules are the only gate on what the agent can call; the plugin trusts skill frontmatter as its enforcement surface.

## Cross-role tools

### Python (stdlib + pip + uv)

`python3 -m venv` and `pip install --force-reinstall` are the install primitives. No `uv`/`uvx`. Tests via `pytest`.

### Bash

SessionStart hook is bash with `set -euo pipefail`. Bin wrapper is bash.

### `$CLAUDE_ENV_FILE`

Used to bridge SessionStart-resolved variables (state dir, dotenv-style credentials) into subsequent bin wrapper invocations.

### `${CLAUDE_PLUGIN_DATA}`

Venv and state location.

### `hookSpecificOutput.additionalContext`

SessionStart success/failure JSON output channel.

### `plugin.json.version`

Single source of plugin version (`0.1.0`); no marketplace-entry `version` field.

# Sample

Mirrors of `https://github.com/NoelClay/academic-research-mcp-plugin`. Standalone Claude Code plugin (no marketplace manifest) for hallucination-free academic research via Agentic RAG — teaches a subject using only retrieved, cited sources from Semantic Scholar, Unpaywall, and DuckDuckGo, with PDF parsing. Default branch `main`; HEAD created and pushed on a single day (2026-04-11); `package.json` declares MIT (no `LICENSE` file in tree; GitHub `license: null`).

## Marketplace manifest layout

### No marketplace manifest (plugin source repo only)

Repo carries only `.claude-plugin/plugin.json`; no `.claude-plugin/marketplace.json` exists. README install instruction is `claude --plugin-dir /path/to/research-learning-tutor`. The repo-level GitHub name (`academic-research-mcp-plugin`) does not match the plugin `name` (`research-learning-tutor`) — README title is a third variant ("Research Learning Tutor"). A user cloning and installing via `--plugin-dir` gets the plugin-level name.

## Plugin source binding

### Direct git install (no marketplace.json in source repo)

Users install via `claude --plugin-dir /path/to/research-learning-tutor` — no marketplace.json in the repo. Equivalent to a `relative` source if someone else packaged this into a marketplace.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

`plugin.json` carries `keywords: ["research", "learning", "tutor", "academic", "citation", "RAG"]`. No `category`, no `tags`. GitHub repo `topics` array is empty.

### `$schema` absence on per-plugin manifests

`$schema` absent from `plugin.json`.

## Version coordination

### Single source of truth (`plugin.json` only)

`.claude-plugin/plugin.json` `version: "0.1.0"` is the sole user-facing version. `package.json` carries `version: "0.1.0"` for the Node sub-manifest, governing the parser subtree, not plugin identity. Both currently coincide; if one bumps without the other, downstream consumers see a mismatch.

## Channel distribution

### No pinning surface

No tags, no release branches, no marketplace channel. The only pointer is whatever `main` HEAD happens to be at clone time. Consumers track commit SHAs out-of-band.

## Tag and release lifecycle

### No tags at all

Repo has zero tags. Five commits on a single day (2026-04-11). Version `0.1.0` has persisted through every commit. No CHANGELOG, no GitHub Releases.

## Plugin-component registration

### Default convention discovery

`plugin.json` contains only identity/metadata (`name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `userConfig`). No component path fields. MCP servers live in repo-root `.mcp.json`; skills under `skills/`; agents under `agents/`; commands under `commands/`; hooks under `hooks/hooks.json` — all at Claude Code's default locations.

### `.mcp.json` sibling file

`.mcp.json` at repo root carries two MCP server entries: `academic-search` and `web-search`. Servers invoked via explicit `command: "${CLAUDE_PLUGIN_DATA}/venv/bin/python"`.

## Component composition

### Skills (universal)

Single skill at `skills/research-tutor/SKILL.md`. Skill directory contains only `SKILL.md` — no component files (`_*.md`), no prompt fragments.

### Commands

Single `commands/learn.md`. Command frontmatter uses `allowed-tools` with wildcard matchers (`mcp__academic-search__*`, `mcp__web-search__*`).

### Agents

Single `agents/researcher.md`.

### Hooks

`hooks/hooks.json` registers a single SessionStart hook with no `matcher` field — fires on every sub-event including `resume`.

### MCP servers

Two MCP servers declared in `.mcp.json` at repo root.

## Skill authoring conventions

### Standard frontmatter

`SKILL.md` carries standard frontmatter.

### `allowed-tools` with permission-rule syntax

`commands/learn.md` declares `allowed-tools` with wildcard matchers (`mcp__academic-search__*`, `mcp__web-search__*`).

## Agent declaration conventions

### Rich behavior fields (background, isolation, memory)

The `researcher` agent declares `isolation: worktree` directly in YAML frontmatter alongside `model: sonnet` and `maxTurns: 30`. Worktree-isolation semantics presume the invoking session's project is a git repo; for the research/teaching case (where the agent downloads PDFs and writes reports), the worktree's purpose is ambiguous when the consumer is not a git repo.

### `model` + `effort` + `maxTurns` for cost control

`researcher` declares `model: sonnet` and `maxTurns: 30` (hard ceiling on agent turns). An agent hitting the limit would truncate mid-research with no documented recovery.

### Fully-qualified MCP tool names

Agent `tools` lists fully-qualified MCP tool names (`mcp__academic-search__search_papers`, etc.) mixed with built-in tool names (`Read`, `Bash`, `Glob`, `Grep`). Two different conventions for the same kind of access scoping coexist in this plugin — the agent uses fully-qualified names while the sibling `commands/learn.md` uses wildcards in its `allowed-tools`.

## Server runtime (MCP)

### Local venv built by SessionStart hook

`.mcp.json` declares `command: "${CLAUDE_PLUGIN_DATA}/venv/bin/python"` for both servers. The Python venv is built by `hooks/session-start.sh` from `requirements.txt`; the MCP server is launched against it. `.mcp.json` hard-codes `venv/bin/python` (POSIX path) — Windows has no path branch.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory. The PDF parser (`src/parsers/pdf-parser.js`) is invoked directly by full path from `commands/learn.md` — `node ${CLAUDE_PLUGIN_ROOT}/src/parsers/pdf-parser.js <pdf-path> <output-path>`. MCP servers resolve via `.mcp.json`'s explicit `command:` path. `src/parsers/pdf-parser.js` carries `#!/usr/bin/env node` shebang but is invoked via `node <path>`, not directly.

## Dependency installation

### SessionStart-driven dual-runtime install (Python venv + Node modules)

A single SessionStart shell hook (`hooks/session-start.sh`) handles both Python and Node. Python: `python3 -m venv ${CLAUDE_PLUGIN_DATA}/venv` then `pip install -r requirements.txt`. Node: `cd "$PLUGIN_DATA" && cp "$PKG_SRC" . && npm install`. Each manager is guarded by `diff -q` between the source manifest in `${CLAUDE_PLUGIN_ROOT}` and a cached copy in `${CLAUDE_PLUGIN_DATA}`. On `diff` miss, install runs and cache is refreshed; on install failure, the cached copy is `rm -f`'d (`|| rm -f "$REQ_DST"` for Python, `|| rm -f "$PKG_DST"` for Node) so next session's `diff -q` will again miss and retry. `python3 -m venv ... 2>/dev/null || true` makes venv-creation failure invisible — a user without `python3-venv` apt package gets a silent no-op then a "pip not found" downstream. `2>/dev/null` suppression on the install branches keeps stderr quiet to avoid corrupting the same hook's stdout JSON channel that injects context.

### Pip + stdlib venv (no `uv`)

Python deps installed into `${CLAUDE_PLUGIN_DATA}/venv` via stdlib `venv` + pip; uses `requirements.txt` (no `pyproject.toml` for runtime deps).

## Install change detection

### Diff-based byte comparison of manifest

`diff -q` compares `${CLAUDE_PLUGIN_ROOT}/requirements.txt` against `${CLAUDE_PLUGIN_DATA}/requirements.txt` (and analogously for `package.json`). Mismatch triggers install. Pitfall: works only for diffable manifests; misses semantic equivalence and partial-install scenarios. A flaky-network `pip install` that returns 0 but fails to actually land a package leaves a fresh cached manifest, so next session sees "in sync" and skips. The `|| rm -f` only fires on non-zero exit codes; partial-install scenarios aren't detected.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/session-start.sh` runs synchronously on each session start. The same script handles dep install AND emits persona-injection JSON.

## Install failure posture

### Silent fail-through

Both install branches suppress output with `2>/dev/null` and the `|| rm -f` fallback swallows non-zero exit codes. Script always `exit 0`s after emitting the persona-injection JSON. No stderr surfaced to the user; no `continue: false` or exit-2 gating. Missing deps surface later as MCP server import errors.

## User configuration and authentication

### Native `userConfig` with `${user_config.KEY}` substitution

`userConfig` declares 2 fields in `plugin.json`: `semantic_scholar_api_key` (`sensitive: true` — genuine API secret) and `unpaywall_email` (`sensitive: false` — Unpaywall treats the email as a public rate-limit identifier). `.mcp.json`'s `env` block uses `${user_config.KEY}` substitution to translate user config into `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (`CLAUDE_PLUGIN_OPTION_SEMANTIC_SCHOLAR_API_KEY`, `CLAUDE_PLUGIN_OPTION_UNPAYWALL_EMAIL`). The Python server reads them via `os.environ.get(...)`. Round-trip is observable. The `web-search` MCP server receives no `env` block — `userConfig` isn't piped to it (intentional; no API keys needed).

### Schema richness — minimal vs. validated

Each field has only `description` and `sensitive`. No `type`, no `default`, no `enum`, no validation pattern. No `required: true` on `unpaywall_email`; the server raises `ValueError("UNPAYWALL_EMAIL not configured...")` at tool-invocation time rather than at session start. No validation that the email is actually an email string — any non-empty value passes the server's `if not email` check.

## Session context loading

### `additionalContext` payload at SessionStart

`hooks/session-start.sh` emits a heredoc `PERSONA_EOF` containing a JSON object with `hookSpecificOutput.hookEventName: "SessionStart"` and `additionalContext: "..."` carrying the full persona prompt (persona rules, citation rules, paid-resource flow, Korean-language fallback phrase). Dep-install and persona-injection are fused in one script — a change to persona text means the dep-install path is re-reviewed.

### Persona duplication between hook and skill

Persona content is duplicated between `hooks/session-start.sh` (injected into context) and `skills/research-tutor/SKILL.md` (loaded when the skill activates). Both sources describe the cold-researcher persona and citation rules — single-source-of-truth violation.

## SessionStart matcher scope

### Empty matcher (all sub-events)

`hooks.json`'s SessionStart entry has no `matcher` field — fires on `startup`, `clear`, `compact`, `resume`. The persona block re-emits on every sub-event (including `compact`), doubling token cost on long sessions. A `matcher: "startup"` would limit to fresh-session injection.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks. The single SessionStart hook is the only hook. Behavior shaping happens entirely through the persona injected via `additionalContext` plus skill / command instructions.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

`src/parsers/pdf-parser.js` lives in `${CLAUDE_PLUGIN_ROOT}` but `require()`s `pdf-parse` via `path.join(process.env.CLAUDE_PLUGIN_DATA || ".", "node_modules", "pdf-parse")`. Splits code (source-controlled) from deps (not source-controlled) along the `$ROOT` / `$DATA` boundary without relying on standard Node resolution.

## Testing

### No tests

No `tests/` directory, no test files, no `pytest.ini`, no `jest.config.js`, no test script in `package.json` (`scripts` field absent). The most recent commit message references "Fix code review issues" implying manual review happened, but no CI to enforce continued correctness.

## CI workflow shape

### No CI

`.github/` directory does not exist (GitHub API 404). No automated validation of any kind — no manifest schema check, no MCP server smoke test, no linter.

## Marketplace validation

### No validation

Not a marketplace repo and no plugin-manifest validation in CI either.

## Release automation

### No release automation / manual

No `release.yml`, no tags, no GitHub Releases, no CHANGELOG.

## Documentation surface

### README only

Repo ships only `README.md` (~2.3 KB) — what-it-does, persona, install, usage, requirements, architecture, pedagogical foundation, license. No `CHANGELOG.md`, no `architecture.md` at repo root, no `CLAUDE.md`. README has an "Architecture" section with component bullets. `docs/superpowers/specs/2026-04-12-research-learning-tutor-design.md` (12.8 KB) and `docs/superpowers/plans/2026-04-12-research-learning-tutor.md` (37.8 KB) hold design/plan history but are checked in as historical artifacts rather than actively maintained architecture references — generated from a spec-driven workflow ("superpowers" naming). No badges. README's install command uses a directory name (`research-learning-tutor`) that isn't the actual repo name (`academic-research-mcp-plugin`).

## License declaration

### LICENSE declared in manifests, no LICENSE file

`license: "MIT"` declared in `package.json`; README ends with "License / MIT". No `LICENSE` file at repo root. GitHub's license API returns `null`. `plugin.json` carries no `license` field.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE` file, `.github/ISSUE_TEMPLATE/`, or `.github/PULL_REQUEST_TEMPLATE.md`.

## Cross-platform discipline

### POSIX-only with no Windows story

`hooks/session-start.sh` uses `#!/usr/bin/env bash`. `.mcp.json` hard-codes `venv/bin/python` (POSIX path; Windows would be `venv\Scripts\python.exe`). No Windows path branch. README declares "Python 3.10+, Node.js 18+" as the only platform requirement.

## Multi-runtime portability

### Single-runtime — Claude Code only

Plugin manifest lives only under `.claude-plugin/`; no Codex, Cursor, or other runtime directories.

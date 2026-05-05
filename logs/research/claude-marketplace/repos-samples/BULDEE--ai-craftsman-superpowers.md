# Sample

Mirrors of `https://github.com/BULDEE/ai-craftsman-superpowers`. "Senior craftsman methodology for Claude Code" — DDD, Clean Architecture, TDD, rule engine, multi-CI, transforming Claude into a disciplined senior engineer via 21 commands / 11 agents / 14-event hooks.json / a rules engine / an SQLite-backed correction-learning loop / a multi-provider CI adapter. Apache-2.0 licensed, default branch `main`, last commit 2026-04-09 (commit `dfb643a`), 7 stars; sample origin: primary (community).

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root alongside `.claude-plugin/plugin.json` and a `.claude-plugin/ignore` sibling (distribution exclusion list). Source binds via `"./"`. Plugin lives at the marketplace repo root.

### Top-level `metadata` wrapper variants

`metadata.{description}` wrapper (description only — no `version` or `pluginRoot` inside `metadata`). Top-level `name`, `version`, `owner` alongside the `metadata` object. No `metadata.pluginRoot`. No `$schema`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` — plugin root and repo root are the same path. Pairs with the self-referential single-plugin marketplace at repo root.

### `strict` field default

`strict` not set on the entry (implicit-true default). No `skills` override on the marketplace entry.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

All three dimensions populated. Marketplace entry declares `category: "development"` plus `tags: [architecture, quality, php, symfony, react, typescript, ci, rule-engine]` (8 tags). `plugin.json` independently carries an 18-item `keywords` array (ddd, domain-driven-design, clean-architecture, tdd, craftsman, software-engineering, code-quality, symfony, react, typescript, php, testing, refactoring, methodology, quality-metrics, static-analysis, sentry, channels). Tags and keywords overlap heavily but drift: `rule-engine`, `ci` appear only on the marketplace entry; `domain-driven-design`, `clean-architecture`, `methodology`, `static-analysis`, `sentry`, `channels`, `refactoring`, `testing` appear only in `plugin.json` keywords. No `$schema` on either manifest.

## Version coordination

### Multi-site sprawl (5+ locations)

Six independent version carriers, all currently `3.4.4`: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (root-level `version`), `.claude-plugin/marketplace.json` (`plugins[0].version`), `ci/craftsman-ci.sh` `VERSION=` variable, README version badge, and CLAUDE.md "Current version:" string. `tests/ci/test-adapters.sh` mock report versions add a seventh carrier. `scripts/bump-version.sh <new_version>` patches all of them; CLAUDE.md has a "Version Sync Checklist" enumerating the targets. CI's `validate-plugin-manifest` job checks plugin.json version is semver but does not cross-check against marketplace.json. `bump-version.sh` uses BSD `sed -i ''` syntax (works on macOS, fails on GNU Linux sed).

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No split — users pin via git ref. `BULDEE/ai-craftsman-superpowers` resolves to default branch; `@vX.Y.Z` tags available but no stable/latest marketplace pair.

### Application-level channels distinct from distribution channels

Plugin ships `channels.sh` as an internal library (`hooks/lib/channels.sh`, 9.5 KB) and `channel-cache.sh` (2.7 KB) — application-level channel semantics for the plugin's own feature routing (which rules apply to which projects), independent of marketplace distribution channels.

## Tag and release lifecycle

### Tag-on-main, single branch

Tags placed directly on commits merged to `main` (e.g., v3.4.4 is tag of commit `97219e3` on main). 30 tags observed spanning v1.2.1 → v3.4.4. CONTRIBUTING.md instructs branching `feature/*` off main and merging back. Tight cadence: four patches in 36 hours for v3.4.x as reactive fixes (v3.4.1 → v3.4.2 → v3.4.3 → v3.4.4 on 2026-04-05 through 2026-04-06). No pre-release suffixes used; plugin.json CI schema regex (`^\d+\.\d+\.\d+(-[\w.]+)?$`) tolerates them.

## Plugin-component registration

### Default convention discovery

No `skills`, `commands`, `agents`, or `hooks` path arrays in plugin.json. Claude Code auto-discovers from conventional directories (`commands/`, `agents/`, `skills/`, `hooks/hooks.json`). CHANGELOG v3.2.2 explicitly notes: "`skills` and `agents` fields in `plugin.json` used inline objects incompatible with Claude Code v2.1.92 schema. Removed inline definitions; Claude Code now auto-discovers from `commands/` and `agents/` directories."

### Inline `mcpServers` definition in `plugin.json`

`mcpServers` IS inlined in plugin.json (`knowledge-rag` stdio server pointing at `packs/ai-ml/mcp/knowledge-rag/start.mjs`) — mixed inline/discovery within the same manifest.

## Component composition

### Skills (universal)

One hidden session-init skill: `skills/craftsman/session-init/SKILL.md` with `disable-model-invocation: true`.

### Commands

20 `.md` files under `commands/`; symlinks bring pack commands in. CHANGELOG v3.3.2 records an absolute-symlink regression (`commands/knowledge.md` was an absolute symlink, broken on other machines — restored to relative).

### Agents

5 core agents in `agents/` with pack symlinks for 11 total per README.

### Hooks

`hooks/hooks.json` with 14 entries spanning 12 distinct event types, plus 18 `.sh` scripts plus a `hooks/lib/` helper library (rules-engine.sh 17.6 KB, session_state.py 12.5 KB, yaml-parser.py 8 KB, etc.).

### MCP servers

One stdio `knowledge-rag` server inlined in plugin.json (no `.mcp.json`).

### bin

Two thin wrappers: `bin/craftsman-ci` and `bin/craftsman-validate`.

### output-styles, monitors

Two output-style files: `output-styles/craftsman-review.md`, `output-styles/craftsman-terse.md`. No monitors. Plus non-standard `teams/wizard.md` (3.5 KB), `config/default-config.yml`, and an empty `setup/templates/` directory — surfaces not in the plugin reference.

## Skill authoring conventions

### `disable-model-invocation: true` for high-blast-radius skills

`session-init` skill carries `disable-model-invocation: true` — hidden from auto-load.

## Agent declaration conventions

### Rich behavior fields (background, isolation, memory)

Agent frontmatter uses `name`, `description`, `model` (sonnet), `effort` (high), `memory` (project / user), `isolation` (worktree), `maxTurns` (20 / 50), `allowedTools` (array), `skills` (array of `craftsman:<skill>` refs). `team-lead.md` adds non-standard `TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage` to `allowedTools` — references to agent-orchestration tools not documented in the plugin reference. CHANGELOG v3.2.2 notes: "Fixed `tools:` → `allowedTools:` in react-reviewer, symfony-reviewer, security-pentester" — prior releases used the wrong field name. `security-pentester.md` omits the `skills` field.

### Plain tool-name list

`allowedTools` uses plain tool names only (e.g., `Bash`, `Read`, `Glob`, `Grep`, `Write`, `Agent`). No permission-rule syntax in agent frontmatter.

### `skills:` array delegating to skill packages

Agent frontmatter declares `skills: [craftsman:<skill>, ...]` arrays.

## Server runtime (MCP)

### Runtime-fetched server via `npx -y`

`mcpServers.knowledge-rag` runs via `command: "node"` and `args: ["packs/ai-ml/mcp/knowledge-rag/start.mjs"]`. Pack-level `packs/ai-ml/mcp/knowledge-rag/` is a Node module; users must run `npm install` in that subdirectory manually. `.claude-plugin/ignore` excludes `packs/*/mcp/*/node_modules/` from the distributed archive.

## Bin entry mechanism

### Bash thin exec-delegate wrapper

`bin/craftsman-ci` (225 bytes) — `exec bash "$(cd "$(dirname "$0")/.." && pwd)/ci/craftsman-ci.sh" "$@"` (delegates to `ci/craftsman-ci.sh`, the 20 KB multi-provider CI pipeline script). `bin/craftsman-validate` (380 bytes) — builds a JSON tool_input envelope via `jq -n --arg fp "$FILE" '{"tool_input":{"file_path":$fp}}'` and pipes it into `hooks/post-write-check.sh`, letting a user run the same PostToolUse validator from a terminal. Shebang `#!/usr/bin/env bash`. Runtime resolution is script-relative only — `$(cd "$(dirname "$0")/.." && pwd)` resolves the plugin root from the bin script's own path; no `${CLAUDE_PLUGIN_ROOT}` reference. Bash-only, no `.cmd` or `.ps1` companions. CI's `validate-shell-scripts` job's "Check scripts are executable" step checks `hooks/*.sh` and `tests/run-tests.sh` but NOT `bin/*` — executability not CI-enforced for the bin wrappers.

## Dependency installation

### No managed install (user prerequisite)

The plugin itself is pure bash + Python + Markdown with no `requirements.txt`, no `pyproject.toml`, no root `package.json`. No SessionStart dep-install hook. `python3` is invoked via system PATH with graceful degradation (`HAS_PYTHON3=true; command -v python3 >/dev/null 2>&1 || HAS_PYTHON3=false`). Plugin assumes `python3`, `jq`, `bash 3.2+`, and (optionally) `node`, `phpstan`, `eslint`, `deptrac`, `dependency-cruiser`, `shellcheck` are already installed. Graceful degradation is the install story: features light up when their required tool is present. README declares "Claude Code v1.0.33 or later" as host-version floor (documentation only, not enforced in manifest). Pack `packs/ai-ml/mcp/knowledge-rag/` ships a Node MCP server but has no install/bootstrap — user must run `npm install` manually post-clone or the MCP server fails at stdio connect time.

## User configuration and authentication

### Typed `userConfig` schema with rich field types

`userConfig` declares 7 fields: `strictness` (string, default "strict"), `stack` (string, default "fullstack"), `agent_hooks` (boolean, default true), `packs` (string, default ""), `sentry_org` (string), `sentry_project` (string), `sentry_token` (string, `sensitive: true`, description "stored securely in keychain"). Every field declares `type` (string/boolean), most declare `title`, `description`, and `default`.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

`agent-ddd-verifier.sh` gates on `"${CLAUDE_PLUGIN_OPTION_agent_hooks:-true}" == "false"` (early-exit if user disabled agent hooks). No `${user_config.KEY}` tokens in hook commands.

### External config file owned by plugin

`.craft-config.yml` (separate YAML-based project config) carries strictness/stack — userConfig is separate from the project-level config file. `session-start.sh` warns when they mismatch: "detected 'fullstack' but config says 'symfony'. Run /craftsman:setup to update." Two parallel config sources (claudec userConfig and `.craft-config.yml`) overlap and can drift.

## Session context loading

### `systemMessage` payload (broader rendered form)

`hooks/session-start.sh` emits `{systemMessage: "..."}` JSON containing a multi-line profile summary (active stack, strictness, enabled rules, learning trends from prior sessions, healthcheck, command routing table). Renders as `Craftsman active | Stack: fullstack | Strictness: strict | PHP rules: ON | TS rules: ON | Metrics: initialized | PACKS: ai-ml,bash,python,react,symfony | ...` plus correction-learning trends (`Learning: PHP001 fix rate 78%`), healthcheck summary, and a full command `ROUTING` block.

### Per-prompt bias / signal detection

`bias-detector.sh` (UserPromptSubmit) inspects each user prompt for cognitive biases (acceleration, scope creep, over-optimization, missing-design) and emits non-blocking warnings via `{systemMessage: ...}`.

### SessionStart purely for non-context side effects

`session-start.sh` writes a bridge file `~/.claude/craftsman-session-state-path` containing the resolved `CLAUDE_PLUGIN_DATA` path, AND generates `~/.claude/craftsman-set-verified.sh` (a per-session executable wrapper with the plugin's resolved lib path baked in, so skills running in Bash-tool context — where `CLAUDE_PLUGIN_ROOT` is absent — can call `session_state.py set-verified` without path resolution). Both files live outside plugin-managed storage. Caused v3.3.5 test-pollution bug ("Tests calling `session-start.sh` overwrote `~/.claude/craftsman-session-state-path` with temp paths, corrupting the real session's bridge file") — tests need backup/restore guards. Generated wrapper is rebuilt every SessionStart so stale copies from old plugin versions are silently overwritten.

## SessionStart matcher scope

### Empty matcher (all sub-events)

No matcher key on the SessionStart hook entry; fires on `startup|clear|compact`.

## Tool-use enforcement

### Layer-import / architecture rule validation

PreToolUse with matcher `Write|Edit` runs `pre-write-check.sh` (5.3 KB, layer-import validation on PHP/TS/TSX before write, LAYER001-003 and PHP001 rules, `exit 2` to block).

### `if:` permission-rule sub-matcher

PreToolUse entry with matcher `Bash` plus `if: "Bash(git push*)"` runs `pre-push-verify.sh` (2.3 KB, warns when `/craftsman:verify` has not run; v3.4.3 downgraded from blocking to warning). Conditional matcher syntax narrowing the Bash hook to git-push-shaped commands only via the same permission-rule glob syntax as `permissions.allow/deny`. Far more precise than re-parsing inside the hook. Brittle against future Claude Code changes to `if:` parsing.

### Full rule engine with cross-file pattern aggregation

PostToolUse with matcher `Write|Edit` runs `post-write-check.sh` (13.5 KB rules engine with correction-learning, cross-file pattern detection). Consults `session-state.json` after recording a violation; if the same rule has fired in 3+ files this session, appends "PROJECT-WIDE PATTERN: {rule} found in {N} files — consider a project-wide fix or global craftsman-ignore" to the block/warn message. Per-rule inline suppression supported via `craftsman-ignore: <RULE_ID>` or multi-rule `craftsman-ignore: PHP001, TS001, LAYER001` comments inside source files (`line_has_ignore` and `file_has_ignore` helpers); metrics record both "blocked violations" and "ignored violations" — partial suppression is first-class.

### Test-success unlocks subsequent action

PostToolUse with matcher `Bash` and `async: true` runs `post-bash-test-verify.sh` (1.5 KB) on tool-result `exit_code == 0` and matches a regex against `run-tests.sh|phpunit|jest|vitest|pytest|cargo test|go test|npm test|pnpm test|yarn test`; on match flips a session-state `verified=true` flag so the subsequent `git push` PreToolUse hook allows the push without friction. Emergent workflow: "test-then-push unlocks push automatically."

### `PostToolUseFailure` post-hoc diagnostic hook

`PostToolUseFailure` hook with matcher `Write|Edit|Bash` runs `tool-failure-tracker.sh` (async) to record tool failures into metrics. Event was added to CI's `VALID_HOOK_EVENTS` allowlist only in v3.4.1 — plugin sits at the leading edge of event coverage.

### Validate-and-nudge on InstructionsLoaded

`InstructionsLoaded` hook runs `agent-structure-analyzer.sh`.

### Stop-event handlers for session-end aggregation

`SubagentStop` runs `subagent-quality-gate.sh` (async).

### Rule engine reuse across hook + CI lanes

Both `ci/craftsman-ci.sh` (pipeline-mode CI) and `hooks/post-write-check.sh` (real-time-mode hook) source `hooks/lib/pack-loader.sh` and `hooks/lib/rules-engine.sh`. README §5 markets this as "zero drift" — same rules engine invoked at two different lifecycle points. Adapter pattern (`adapter_detect/run/annotate/comment/exit`) provides four CI-provider implementations (GitHub Actions, GitLab CI, Bitbucket Pipelines, Jenkins).

## Hook output contract

### Stderr for human display + stdout JSON for harness

`post-write-check.sh` emits both surfaces. Per CHANGELOG v3.4.4: "When `post-write-check.sh` or `pre-write-check.sh` blocks a write, a human-readable violation summary is now emitted on stderr (displayed in Claude Code UI). Previously only JSON was written to stdout, resulting in an unhelpful 'No stderr output' message." Stderr shows `🚫 BLOCKED by AI Craftsman — N violation(s):` with bulleted `✗` lines and a `Fix these or add: // craftsman-ignore: <RULE_ID>` footer; stdout emits `{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: "BLOCKED: ..."}}` consumed by Claude. Warning-only (non-blocking) exits use `{systemMessage: "WARNINGS: ..."}` on stdout.

## Hook failure posture

### Fail-open envelope via `trap 'exit 0' ERR`

Every hook opens with `set -uo pipefail` (NOT `-e`) and `trap 'echo "WARNING: hook.sh failed at line $LINENO" >&2; exit 0' ERR` — on crash, hooks emit a warning to stderr but exit 0 so writes/pushes are never blocked by hook bugs. CLAUDE.md codifies: "All hook scripts MUST use `exit 0` (pass) or `exit 2` (block). NEVER `exit 1`." SECURITY.md restates this as a hook security guarantee.

## Hook handler runtime

### Bash scripts at conventional path

Hook handlers are `.sh` scripts under `hooks/`, with helper library at `hooks/lib/` (Python 3 helpers `session_state.py`, `metrics-query.py`, `yaml-parser.py` invoked via `python3` on system PATH with graceful degradation).

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field in `plugin.json`.

## Testing

### Bash scripts only

`tests/run-tests.sh` (19 KB) is the single entry point; subdirectories `tests/hooks/`, `tests/ci/`, `tests/core/`, `tests/lib/`, `tests/packs/`, `tests/templates/` each hold their own `.sh` test files. No pytest/unittest/jest. Hierarchical bash-script test suite. `tests/` excluded from distribution via `.claude-plugin/ignore`.

## CI workflow shape

### Single-workflow with multiple jobs in a DAG

`.github/workflows/ci.yml` (18.3 KB, single workflow) on `push: branches: [main, develop]` and `pull_request: branches: [main]`. 9 jobs in a dependency DAG: **secrets-scan** (seed; runs `.github/scripts/secrets-scan.sh` 5.5 KB scanner for OpenAI `sk-*`, AWS `AKIA*`, GitHub `ghp_*`/`github_pat_*`, Anthropic `sk-ant-*`, local filesystem paths, `.env`/`.pem`/`.key`/`id_rsa` filenames, private IPs; full git history scan via `fetch-depth: 0`; all other jobs `needs: [secrets-scan]`); **validate-json** (Python3 `json.load()` round-trip); **validate-hooks-schema** (inline Python3 asserting hook event names in 13-entry `VALID_HOOK_EVENTS` set, hook types in `["command", "agent"]`, agent hooks declare `prompt`, agent `model` in `["haiku", "sonnet", "opus"]`); **validate-plugin-manifest** (inline Python3 required fields + repository string + version regex); **validate-shell-scripts** (bash `-n` syntax + executable-permission + `shellcheck -x` warning-only on an explicit allowlist of 8 scripts); **validate-skills** (traverses `skills/`, validates frontmatter has `name:`/`description:`/`model:` with grep, exception for `session-init`, recurses into namespace directories); **validate-knowledge-base**; **run-tests** (`needs: [validate-json, validate-shell-scripts]`, `./tests/run-tests.sh`); **check-agents**; **summary** (`if: always()`). All jobs ubuntu-latest / Python 3.12; no matrix.

### Action-pinning conventions

Major-version tag pinning (`actions/checkout@v4`, `actions/setup-python@v5`); not SHA-pinned. No caching, no codecov upload.

## Marketplace validation

### Inline Python validators in CI YAML

`validate-plugin-manifest`, `validate-hooks-schema`, `validate-json`, `validate-skills`, `check-agents`, `validate-knowledge-base` jobs in ci.yml together. Validator is inline Python 3.12 heredoc, not a dedicated library. v3.4.1 patch specifically added 4 hook events to VALID_HOOK_EVENTS — validator-as-second-source-of-truth lagging the actual runtime.

### Frontmatter validation by grep

Grep-based for `name:`/`description:`/`model:` in `skills/*/SKILL.md` and `agents/*.md` (not YAML-parsed) — catches missing-fields but misses quoting issues, multi-line descriptions.

### Hardcoded script allowlists in CI

`validate-shell-scripts` and the ShellCheck step list specific scripts by path; adding a new hook requires editing ci.yml too.

### Schema validators that lag the runtime

`VALID_HOOK_EVENTS` set in CI's hooks-schema validator predated the runtime's acceptance of newer events; v3.4.1 patch release was specifically needed to add 4 new events to the allowlist after the runtime accepted them.

### Knowledge-base presence checks with subtle bugs

`validate-knowledge-base` runs `count=$(find ... | wc -l)` but the variable is echoed without comparison to a minimum, so an empty directory with zero files passes the `[ -d "$KNOWLEDGE_DIR/anti-patterns" ]` existence check.

## Release automation

### Tag-driven version-bump script with no GitHub Actions

`scripts/bump-version.sh <new_version>` patches all six version carriers (plugin.json, marketplace.json × 2, ci/craftsman-ci.sh, README badge, CLAUDE.md "Current version" string, tests/ci/test-adapters.sh). The script's tail prints next-step instructions: `git add -A && git commit -m 'chore: bump version to X'; git tag vX; git push origin main && git push origin vX`. No dedicated release workflow, no `workflow_dispatch`, no `release: [published]`. Releases manual via GitHub UI. `bump-version.sh` does not run `git tag` or commit. 30 tags exist with no automation guaranteeing tag == plugin.json version. CHANGELOG.md is Keep-a-Changelog v1.1.0 format, linked explicitly in CHANGELOG header, but no CI consumes it.

## Documentation surface

### Marketing-grade README (40+ KB)

`README.md` at repo root (27.7 KB) — opens with badge row (License, Claude Code compat, Version, Commands count, Agents count, PRs Welcome), tagline "Transform Claude into a disciplined Senior Software Craftsman", ToC links, Requirements, Installation (From GitHub + From Local Path + Verify), API Cost Model section (explicit Haiku-call cost disclosure: ~$0.15-0.30/session), Quick Start with command examples, "Why Craftsman? — 6 Core Differentiators" marketing section, Additional Features, links to examples.

### CLAUDE.md without ARCHITECTURE.md, ADRs as decision capture

No `ARCHITECTURE.md`. `CLAUDE.md` at repo root (5 KB) — Development Rules (exit codes, JSON output, atomic SQLite writes, adapter interface), Testing commands, 6 Key Differentiators, Architecture directory tree, Version Sync Checklist. Architectural content split between CLAUDE.md's "Architecture" section (directory tree only) and 15 ADRs under `docs/adr/` (Nygard-style — Status/Date/Context/Decision/Consequences). Topics: skills-over-prompts, ollama-over-openai, sqlite-over-pgvector, 3p-agent-pattern, knowledge-first-architecture, project-specific-knowledge, commands-over-skills, inline-sqlite-over-bash-expansion, command-hooks-over-agent-hooks, model-tiering, context-fork-strategy, progressive-disclosure, workflow-orchestrator, quick-setup-mode. ADRs are routinely cross-referenced from CHANGELOG entries.

### Keep-a-Changelog with root-cause prose

`CHANGELOG.md` (41 KB) — Keep a Changelog v1.1.0 format, explicit SemVer adherence, dated entries for every version from v1.2.1 forward. Entries routinely reference ADRs (e.g., "See [ADR-0013](docs/adr/0013-workflow-orchestrator.md)").

### Badges and status indicators

Six shields.io badges in README opening row (License, Claude Code compat, Version, Commands count, Agents count, PRs Welcome). No CI status badge despite CI being present.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` file present at repo root (10.5 KB full Apache 2.0 text). Apache-2.0 SPDX identifier declared in manifests.

## Community health files

### LICENSE + CODE_OF_CONDUCT + issue templates

Complete community-health surface: `SECURITY.md` (5.5 KB, security policy with per-hook security table and what-the-plugin-does/doesn't-do bullets — explicit trust surface), `CONTRIBUTING.md` (4.3 KB, bug report template, PR steps, Conventional Commits guidance, command/agent development standards), `CODE_OF_CONDUCT.md` (2.1 KB), `.github/PULL_REQUEST_TEMPLATE.md` and `.github/ISSUE_TEMPLATE/` directory.

## Distribution exclusion and dogfood layout

### `.claude-plugin/ignore` exclusion list

14-line `.claude-plugin/ignore` listing heavy dependencies (`packs/*/mcp/*/node_modules/`, `packs/*/mcp/*/dist/`), dev-only dirs (`tests/`, `scripts/`, `examples/`, `docs/superpowers/`), CI artifacts, and selected docs (`BRUTAL-EVALUATION-PROMPT.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`). The plugin archive served to users is a curated subset of the repo.

## API-cost transparency and cost-gated MCP tools

### Explicit cost-model section in README

README "API Cost Model" section quantifies the agent-hook cost at ~$0.15-0.30 per session with a per-hook breakdown table, and provides an explicit opt-out (`agent_hooks: false` userConfig field).

## Output styles

### Shared markdown templates under `output-styles/`

Two shared markdown files under `output-styles/`: `craftsman-review.md` and `craftsman-terse.md`.

## Novel and cross-cutting concerns

### Graceful-degradation via fallback tool

With no dependency installer at all, the plugin uses Level 1 (regex-only validation) as the baseline; Level 2 (PHPStan, ESLint) and Level 3 (deptrac, dependency-cruiser) features light up only when those tools are installed. README documents the degradation ladder as a design feature.

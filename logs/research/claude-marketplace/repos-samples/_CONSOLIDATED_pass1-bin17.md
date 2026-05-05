# Sample

Pass-1 Phase-1a partial for bin 17. Functional decomposition of robertnowell/marketing-pipeline, skullninja/coco-workflow, and smcady/Cairn, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the marketplace manifest is positioned relative to the plugin(s) it advertises and how a consuming Claude Code marketplace add command discovers the plugin source.

### Self-hosted single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` coexist in a single repository, with the marketplace's plugin entry pointing back at the same root via `"source": "./"` (or `"."`). The marketplace IS the plugin — adding the repo as a marketplace and installing the one plugin it advertises are the only paths users have. Trivially deployable for a single-plugin author and matches the way users typically encounter the work (one repo, one plugin), but is not extensible to a second plugin without restructuring. This collapses the marketplace/plugin split into a single artifact and frees the author from running a separate aggregator marketplace solely to publish one plugin.

## Marketplace-level metadata

Top-level fields on `marketplace.json` that describe the marketplace itself (versus per-plugin entries inside it).

### Minimalist top-level keys only

The marketplace declares only the minimum keys Claude Code needs — typically `name`, `owner`, and the `plugins` array, sometimes a top-level `description` or `version`. There is no `metadata` wrapper, no `metadata.pluginRoot`, no `metadata.description`. A consuming aggregator that expects nested metadata sees nothing under the wrapper key. Appropriate when the author treats the marketplace purely as a vehicle for the one plugin it advertises and does not anticipate a third party indexing its metadata fields.

## Per-plugin discoverability metadata

Searchable/filterable fields on the plugin entry inside the marketplace — what a marketplace consumer would index to make plugins findable.

### Sparse — name/source/description only

Plugin entries carry only the fields required to install (`name`, `source`, sometimes `description` and `version`). No `category`, `tags`, or `keywords` on the marketplace entry. Where keywords exist they live in `plugin.json` and are not surfaced into the marketplace entry. GitHub repo topics may compensate as an external discovery surface but do not flow into the manifest. A category may be present (e.g., `"productivity"`) without accompanying tags. Discoverability is therefore carried by the description prose and any external surface (README, GitHub topics), not by structured manifest metadata.

## Plugin source binding

How the marketplace entry points at the plugin's source directory — the resolution mechanism Claude Code uses to find the plugin's files at install time.

### Relative `./` self-source

`"source": "./"` (or `"."`) — the plugin lives at the same repo root as the marketplace manifest. The `strict` field is omitted, relying on implicit-true. Skills/commands/agents are auto-discovered from canonical directories rather than overridden via a `skills` array on the marketplace entry. Appropriate when the marketplace IS the plugin (see Marketplace manifest layout / Self-hosted single-plugin pattern) and a single-source-of-truth at the repo root is the entire surface. Implies that adding a second plugin to the repo is not naturally accommodated — the relative source assumes one-plugin-per-repo.

## Version authority

Where the canonical version string for the plugin lives, and what mechanism (if any) enforces consistency across copies.

### `plugin.json` only

The plugin's `version` string lives exclusively in `plugin.json`; the marketplace entry carries no `version` field. Users who want to pin a version must do so at the Git ref level (`@<sha>` or `@<tag>`) rather than via a marketplace-surfaced version dimension. Eliminates drift risk by construction (one place, one truth), but pushes pinning out of the marketplace abstraction.

### Duplicated across `plugin.json` and `marketplace.json`

Both `plugin.json` and `marketplace.json` (top-level or per-entry) carry the same version string. The two are kept in sync by hand at release time with no validating workflow. Drift risk is real — a release that bumps one but forgets the other ships inconsistent metadata — and only hand discipline prevents it. Trade-off: marketplace consumers can read the version directly from the manifest entry without dereferencing `plugin.json`, at the cost of a second hand-maintained surface.

## Channel distribution

Whether the repo exposes a stable-versus-development split in its branch/tag/manifest layout that consumers can pin to.

### Single channel — main only

No `stable-*` / `latest-*` branch split, no duplicated manifests. Users install whatever currently lives at HEAD on `main`, with optional `@<ref>` pinning at the Git level. Appropriate for small repos with no separation between stable and dev consumers. Implies that any user who installs takes HEAD at install time and has no in-band mechanism to track updates short of re-running install.

## Release cadence

The pattern of tags and releases over time — frequency, granularity, and the relationship between commits and shipped versions.

### Untagged main (no releases)

No tags exist; no GitHub releases have been cut. The plugin's `version` field is frozen at an initial value (typically `0.1.0`) across many commits. Every install takes HEAD; there is no version-pinning surface. Conventional commit subjects substitute for a changelog. Appropriate while pre-1.0 and exploring the design space, but offers no rollback or reproducibility for downstream consumers.

### Manual semver tags on main

Tags `vX.Y.Z` are pushed directly on main commits — no release branches, no `-rc`/`-beta` suffixes, no dev-counter scheme. Tagging happens at the same minute as the underlying commit lands; releases are hand-cut via the GitHub UI or `gh release create`. Cadence can be rapid (multiple bugfix releases within a single day) when blocking issues are caught post-tag. Trade-off: gives consumers a pinnable surface but provides no objective gate between "tagged" and "shipped" without CI.

## Pre-commit version bump

Whether a hook on this repo bumps the plugin's `version` automatically as commits land.

### Absent

No `.pre-commit-config.yaml`, `.husky/`, or `.github/hooks` configuration that bumps the version on commit. Version is hand-edited at release time. Appropriate when the release model is "tag deliberately, version manually" rather than "every commit gets a unique patch level". Implies long stretches where many commits share a single version string, with the changelog effectively being `git log` between tags.

## Plugin-component registration style

How `plugin.json` connects to the components (skills, commands, agents, hooks, MCP servers) that ship with the plugin — explicit declaration versus directory-convention discovery.

### Default discovery from canonical directories

`plugin.json` declares only top-level fields like `name`, `version`, `description`, `author`. No `commands`, `skills`, `agents`, `hooks`, or `mcpServers` arrays. Claude Code auto-discovers components by directory convention (`skills/`, `commands/`, `agents/`, `hooks/hooks.json`). Appropriate when the plugin has nothing unusual about its layout and prefers convention over configuration. Past tightening of Claude Code's plugin validator has caused authors to remove previously-declared "invalid auto-discovery fields" — i.e., the validator now penalizes redundant declaration of auto-discoverable components. Discovery is therefore the default and the safer path.

### Inline configuration for non-discoverable components

`plugin.json` declares `mcpServers` inline as a configuration object (e.g., `{"cairn": {"command": "bash", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.sh"]}}`) rather than relying on directory discovery. Hooks remain auto-discovered from `hooks/hooks.json`. Appropriate for components like MCP servers that need explicit command/args declaration and have no canonical directory equivalent — discovery cannot describe how to launch a server. Plugin-mode and library-mode (project-local `.mcp.json`) can coexist as two install paths for the same conceptual surface, with no runtime overlap because plugin-mode uses `${CLAUDE_PLUGIN_ROOT}`-relative paths and library-mode uses project-absolute paths.

## Component composition

Which kinds of components the plugin ships — skills, commands, agents, hooks, MCP servers, monitors, bin wrappers, output styles — and how the mix shapes the plugin's product surface.

### Skills + hooks + bin

Multiple skills (each as `skills/<name>/SKILL.md`) plus a SessionStart hook plus a single bin entry point that the skills invoke via `Bash(<binname> *)` permission rules. No commands, no agents. The bin is the orchestrator; skills are the user-invocable surface; the hook handles environment setup. Appropriate when the workflow is dominated by command-line tooling that the agent triggers via `Bash`-permissioned skill invocations.

### Skills + commands + agents + hooks + bin

A multi-component plugin with skills (single-file `SKILL.md`), commands (markdown files for slash invocation), agents (sub-agent definitions with their own model/isolation/color), hooks (pre/post tool use plus session-start/pre-compact), and a thin bin wrapper. Appropriate for spec-driven-development style workflows where each phase has its own command surface, agents handle execution in worktrees, and the bin is a shared utility called from every component context. Skill files are kept single-file (no supporting files) — each skill body is its complete operational reference.

### Hooks + MCP server (no skills/commands/agents/bin)

The plugin's entire product surface is one MCP server with several tools plus two or three hook scripts. No skills, commands, or agents at all. Appropriate when the plugin is purely a context-provider (memory, retrieval, indexing) — Claude reaches its tools via MCP, not via slash commands or skill invocations, and hooks handle background ingestion and per-prompt context injection. Unusual for a marketplace plugin and worth noting: components are not all present in every plugin; the absence of a skills surface is a legitimate design.

## Agent frontmatter fields

Fields used in `agents/*.md` frontmatter to describe sub-agents — model selection, isolation, tool access, presentation.

### Standard fields plus `model`/`color`

`name`, `description`, `model` (selecting between `sonnet`/`opus` per agent role), `color`. The `description` field embeds XML-ish `<example>` blocks inline in YAML strings — readable but assumes the platform doesn't strip or parse them. Agents inherit default tool access; no `tools` field. Appropriate when different agents have different cost/capability budgets (cheap sonnet for execution, expensive opus for review) and agents can use whatever tools the harness allows.

### `isolation: worktree`

A non-standard frontmatter field declaring that the agent should run in an isolated worktree. Assumes Claude Code's worktree isolation feature; if a client doesn't support it, parallel execution silently becomes serial. Appropriate when parallel execution of multiple instances of the same agent is fundamental to the workflow (e.g., spec-driven dev with parallel task execution). Worth cross-referencing against other multi-agent orchestration plugins.

## Skill frontmatter fields

Fields used in `skills/*/SKILL.md` frontmatter beyond the standard set.

### Non-standard `user-invocable: true`

Every `SKILL.md` declares `user-invocable: true`. The Claude Code plugins reference does not document this field — either author-invented (and ignored at runtime) or an undocumented behavior. If ignored, it is dead metadata; if respected, it is an undocumented dependency. Worth flagging as an "uncommon frontmatter fields observed in the wild" data point.

## Dependency-install runtime

The package manager and execution mechanism the plugin's SessionStart bootstrap uses to install Python (or other) dependencies into a plugin-managed venv.

### Classical `python3 -m venv` + `pip install`

`python3 -m venv` creates a venv at `${CLAUDE_PLUGIN_DATA}/venv` (or `.venv`), then `pip install` is run against the plugin source. Some variants pass `--force-reinstall` to guarantee a clean state on every change-detection trigger; others rely on pip's incremental semantics. No `uv`, no `uvx`, no PEP 723 inline metadata. Appropriate when the plugin's authors prefer the standard library's bundled tooling over an extra system-tool dependency on `uv`. Trade-off: brute-force reinstall is correct but slow (re-fetches all transitive wheels on each change); incremental pip is faster but harder to reason about for cache-coherence.

### Zero dependencies (bash + jq only)

The plugin requires only bash (4+) and `jq` (1.6+), both expected to be present on the user's system. No SessionStart-installed venv, no Python packages, no npm packages, no binary downloads. Appropriate for plugins whose business logic fits in shell. Trade-off: avoids the entire dep-install surface and its failure modes, but constrains the tools the author can use. System-tool requirements (bash 4+, jq 1.6+) are stated in README only — there is no runtime probe checking versions before use, so older platforms with bash 3.2 by default produce cryptic failure modes.

## Dependency-install change detection

How the SessionStart bootstrap decides whether to re-run install on each session.

### Hash over source plus manifest

A sha256 hash is computed over the plugin's Python source files, manifest, and (sometimes) markdown — the union representing "anything that would change what `pip install .` produces". The hash is stored in `${CLAUDE_PLUGIN_DATA}/.deps-hash` and compared on every SessionStart. Mismatch triggers `--force-reinstall`. Appropriate when the plugin installs itself from source via `pip install .` — the installed package is not just the manifest, so manifest-only hashing misses source changes. Trade-off: editing README invalidates the hash and forces a venv reinstall (over-eager invalidation); concurrent SessionStart invocations could race on the hash file (no lock). Hash is computed via `find ... | sort | xargs cat | shasum -a 256` to stabilize across filesystems with non-deterministic `find` ordering.

### Three-pronged OR (path drift + manifest diff + venv health)

Three independent checks evaluated with `elif` short-circuit: (a) cached `${CLAUDE_PLUGIN_ROOT}` path file content differs from current value (detects plugin-cache directory move on Claude Code update), (b) `diff -q` against a cached copy of `pyproject.toml` (detects manifest change), (c) `${VENV_DIR}/bin/python` is missing or non-executable (detects broken venv). Any one trigger forces reinstall. Appropriate when plugin-directory relocation is a real failure mode (Claude Code moving the plugin cache between versions). Trade-off: install reason isn't logged because the flag is set without echoing which trigger fired; cached files are written only after pip success, so a failed install leaves stale cache content and the next session naturally retries via the manifest-diff trigger.

## Dependency-install failure recovery

The implicit or explicit retry mechanism when SessionStart bootstrap fails partway through.

### Implicit retry via late-write cache marker

`set -euo pipefail` halts on any failing command. No explicit `rm` of partial state. The change-detection cache (hash file or cached manifest copy) is written only after pip install succeeds, so a failure leaves the old cache content intact — the next session's change-detection check naturally re-fires the install branch. This amounts to retry without explicit cleanup. Appropriate when the install operation is idempotent under reinstall (pip with `--force-reinstall` is). Trade-off: a partially-created venv may persist on disk; if the venv's `python` binary happens to be present, the venv-existence trigger short-circuits past the actual broken state, which is why manifest/hash drift triggers are critical to the recovery story.

## userConfig declaration

How the plugin declares the user-supplied configuration values (credentials, identifiers, URLs) Claude Code prompts for at install time.

### Typed userConfig with `sensitive` discrimination

`plugin.json` declares a `userConfig` block with one entry per field, each typed (`type: "string"`), titled, described, marked `required` true/false, and flagged `sensitive: true` only for actual secrets (API keys, app passwords, access tokens, webhooks, PATs). Non-secret identifiers (handles, URLs, publication IDs, board IDs) are explicitly `sensitive: false`. No `default`, no enum-narrowing, no pattern/regex validation. Appropriate when the plugin needs Claude Code to gather credentials at install time. Trade-off: `sensitive: false` for non-secret-but-identifying values is a defensible distinction; users see those values displayed where secrets would be redacted.

### Deferred to project-local config file

The plugin declares no `userConfig`. Project-level configuration lives in a project-local YAML or `.env` file (e.g., `.coco/config.yaml`, `.env.local`) that the plugin's setup command or runtime hooks consume directly. Each new project needs its own walk-through; configuration cannot be reused across projects without copying the file. Appropriate when configuration is intrinsically project-scoped (per-project rules, per-project secrets) rather than per-user. Trade-off: the Claude Code install flow won't prompt for secrets — discovery is left entirely to documentation; users must hand-configure the file before the plugin works.

## userConfig delivery mechanism

The runtime path by which userConfig values reach the plugin's runtime — where the plugin reads them from once Claude Code has gathered them.

### Bridge `CLAUDE_PLUGIN_OPTION_<KEY>` to dotenv-style env vars via `$CLAUDE_ENV_FILE`

The SessionStart hook reads `CLAUDE_PLUGIN_OPTION_<KEY>` env vars and writes `export KEY="${CLAUDE_PLUGIN_OPTION_KEY}"` lines into `$CLAUDE_ENV_FILE`. This bridges Claude Code's plugin-option namespace to the conventional env-var names that a CLI library originally designed for standalone `.env` use already expects (e.g., `CLAUDE_PLUGIN_OPTION_BLUESKY_HANDLE` → `BLUESKY_HANDLE`). Appropriate when the plugin is a wrapper over a pre-existing CLI that expects standard env-var names, and changing the CLI's naming would constitute a breaking change. Trade-off: duplicates the value into a file on disk (security depends on file mode of `$CLAUDE_ENV_FILE`, not controlled by the plugin); fields declared in `userConfig` but missed in the bridge block silently fail to propagate (observed defect: a credential added to userConfig but not added to the bridge would never reach the plugin's runtime).

## Cross-hook environment plumbing

How SessionStart-provisioned state (venv paths, state directories, derived values) is made available to other hooks and runtime processes that fire later in the session.

### `$CLAUDE_ENV_FILE` append for cross-hook env vars

The bootstrap appends `export VAR=...` lines to `$CLAUDE_ENV_FILE` so that later hooks (Stop, UserPromptSubmit) and the MCP server wrapper can reference the variable without knowing `${CLAUDE_PLUGIN_DATA}` or having to re-derive the venv location. Avoids hard-coding paths in `hooks.json` command strings and decouples venv location from hook definitions. Appropriate as a general pattern when one hook provisions state that others consume. Trade-off: the file is appended to on every SessionStart sub-event (startup, clear, compact, resume) rather than truncated, so multiple `export` lines accumulate across sessions; bash semantics make later exports override earlier so it is functionally idempotent, but the file grows monotonically. If `$CLAUDE_ENV_FILE` is not set by the harness in some Claude Code versions, the env var is silently not persisted and downstream hooks fail with a "not bootstrapped" error message.

## Plugin/state separation

How code (immutable, replaced by upgrades) and runtime data (mutable, must survive upgrades) are organized relative to plugin root and plugin data directories.

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code lives under `${CLAUDE_PLUGIN_ROOT}` — read-only, immutable, overwritten on plugin upgrade. State (content, reports, projects, venvs) lives under `${CLAUDE_PLUGIN_DATA}` — read-write, mutable, durable across upgrades. Default state is seeded from `${CLAUDE_PLUGIN_ROOT}/defaults/*.yml` on first run when the data dir is empty. Appropriate when the plugin manages user data (state files, cached venvs, generated artifacts) that must survive a plugin update. Implies that the bin wrapper and any state-mutating code must locate their state directory via env var rather than path-relative to the plugin root.

## Bin wrapper resolution strategy

How an executable shipped under `bin/` locates the rest of the plugin's code (the venv, the library scripts, the state directory) when invoked from arbitrary working directories and contexts (skills, commands, hooks, user prompts).

### `${CLAUDE_PLUGIN_DATA}` with HOME fallback

The wrapper reads `${CLAUDE_PLUGIN_DATA}` to locate its venv and falls back to `$HOME/.claude/plugins/data/<plugin-name>` if the env var isn't set. Does not consult `${CLAUDE_PLUGIN_ROOT}`. Appropriate when the wrapper needs the venv (in plugin data) but not the plugin source (in plugin root) — running the installed package, not the source. Trade-off: hard-codes a conventional fallback path; if the harness's plugin-data layout changes, the fallback breaks silently.

### Script-relative resolution (no env vars)

The wrapper computes its location via `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` and `exec`s the target script as `"$SCRIPT_DIR/../lib/<target>.sh" "$@"`. No `${CLAUDE_PLUGIN_ROOT}`, no fallback layer, no env-var dependency. Appropriate because `${CLAUDE_PLUGIN_ROOT}` is exported only to hook subprocesses, not to skill/command/Bash-tool invocations — env-var-based wrappers silently break when callers are skill or command markdown rather than hooks. Trade-off: assumes the bin and its target library remain in fixed relative positions in the source tree; refactoring layout requires updating the wrapper. Pairs naturally with a PreToolUse hook that hard-blocks any regression to the env-var-based pattern (`bash "${CLAUDE_PLUGIN_ROOT}/lib/..."`), making wrapper plus enforcement a complete unit. Wrapper itself is ~6 lines with `set -u` only (deliberately omitting `-eo pipefail` so trailing args aren't lost before the terminal `exec`).

### Not applicable (no bin directory)

The plugin ships no `bin/` directory; user-facing invocation is entirely through Claude Code components (slash commands, MCP tools, hook context injection). A library-mode entry point may exist via `pyproject.toml [project.scripts]`, but it is not exposed via the plugin path because the venv lives in plugin data and isn't on PATH. Appropriate when the plugin's surface is purely declarative (MCP tools, slash commands) and there is no need for a user to invoke a binary directly.

## Bin wrapper venv activation pattern

How the bin wrapper enters the plugin-managed Python venv before exec'ing the Python entry point.

### `source activate` then `exec python`

The wrapper `source`s `$VENV_DIR/bin/activate` (with `# shellcheck disable=SC1091` to suppress the unresolvable-path warning), then `exec python -m <module>`. Functionally correct because `source activate` mutates the shell's `$PATH` to prepend the venv's `bin`, sets `VIRTUAL_ENV`, and the subsequent `exec python` resolves to the venv's interpreter. Strictly weaker than the direct-exec form: requires the activate script to be present and well-formed (some stripped-down or `uv`-managed venvs may omit it); is bash-only (`source` not portable to `dash`); sources ~50 lines of activate boilerplate; depends on `$PATH` order surviving any conda or other venv init that runs in the user's shell rc. The guard `if [ ! -f "$VENV_DIR/bin/activate" ]` reveals the author is aware of the activate-script dependency but not that it is unnecessary.

### Direct `exec` of venv Python (no activate)

The wrapper does `exec "$VENV/bin/python" -m <module> "$@"` without sourcing `activate`. Avoids the entire activate-script surface, works under any minimal shell, runs identically against `uv`-managed and stripped venvs that may lack `activate` entirely. Appropriate as the cleaner default for any new wrapper. Pairs naturally with the wrapper resolving the venv via env-var (`${CAIRN_VENV}` etc.) populated in `$CLAUDE_ENV_FILE` by the SessionStart bootstrap, decoupling venv location from wrapper logic.

## Bin wrapper argument handling

How the wrapper transforms arguments between the user's CWD and the plugin's runtime CWD before invoking the underlying entry point.

### `cd`-before-exec with `--file` argument rewriting

The wrapper resolves selected relative-path arguments (e.g., `--file <path>`) against `$ORIG_CWD` before `cd "$STATE_DIR"`, then `exec`s the entry point. Because the entry point is forced to a fixed working directory (state dir), any user-passed relative path that isn't pre-resolved would silently resolve against `$STATE_DIR` instead of the user's PWD. The `--file`-only rewrite is partial coverage of the cd-before-exec surface — other relative-path flags (e.g., `--config`) pass through unresolved. Argument parsing uses a `next_is_file=true` flag walk over `"$@"`, which handles `--file path` form but not `--file=path` (equals-form passes through unresolved). Appropriate when CWD-stability matters for the underlying CLI's path resolution but the wrapper can't predict which user-supplied paths matter; explicit per-flag rewriting is the price of CWD coupling.

### Pass-through (no rewriting)

The wrapper `exec`s the underlying script with `"$@"` unchanged and does not `cd` before executing. The underlying script handles path resolution itself. Appropriate when the underlying script makes no CWD assumptions and works correctly from whatever directory the user invoked it in.

## Tool-use enforcement (PreToolUse)

How the plugin enforces what kinds of tool calls (typically Bash) are acceptable inside its workflows.

### None

No `PreToolUse` hook. Skill-level `allowed-tools` permission rules in frontmatter are the only gate on what the agent can call. Appropriate when the plugin trusts the skill frontmatter as the policy surface and doesn't need cross-cutting Bash-pattern enforcement. Implies that any agent-surface concerns (forbidden command shapes, command rewrites) are not enforced — the design accepts whatever the agent produces.

### Prompt-type Bash-pattern policy engine

A `PreToolUse` hook with matcher `Bash` and type `prompt` whose body is a multi-hundred-word list of blocked Bash patterns and their corrected rewrites. Claude evaluates the prompt against each proposed Bash command and returns a BLOCK or ALLOW verdict. Not just an enforcement gate — the prompt also lists the rewrite for each blocked pattern, turning the hook into an in-context style guide that teaches the agent how to call the plugin's bin correctly without round-tripping to the user. Blocks `cd && compound`, `&&`/`||` chains, `$()` in echo/printf, multiline JSON (jq `--argjson` crashes on newlines), `for` loops, piping tracker output to Python, and any non-bare invocation of the plugin's bin (no env-var paths, no variable assignment, no `source`, no space-separated subcommands). Appropriate when the plugin has strong opinions about how its bin must be invoked and wants to prevent regression to known-broken patterns. Trade-off: prompt-engineering rather than deterministic code, with attendant non-determinism and per-call latency cost; duplicates much of the documentation also kept elsewhere (CLAUDE.md), which must be kept aligned manually.

## Tool-use enforcement (PostToolUse)

How the plugin reacts to completed tool calls — quality gates, side effects, follow-up actions.

### None

No `PostToolUse` hook. The plugin does not react to completed tool calls.

### Command-type quality gate on Write/Edit

A `PostToolUse` hook with matcher `Write|Edit` and type `command` runs a shell script that reads project-local config (e.g., `.coco/config.yaml`) for `lint_command` / `typecheck_command` (with `{file}` substitution) and executes them against the modified file. Optionally auto-fixes on lint failure if config opts in. Silent exit 0 if config is missing or quality commands are unset. Never blocks. Appropriate when the plugin wants to layer language-specific quality checks onto file modifications without forcing them on projects that haven't opted in. Pairs with the prompt-type/command-type distinction: blocking hooks are prompt-type, non-blocking quality hooks are command-type so that a missing config file can't cause "stopped continuation" errors.

## Hook failure posture

Whether each hook fails-closed (block on error) or fails-open (continue on error), and how the design distinguishes which posture each hook should take.

### Mixed by hook role (blocking prompt vs non-blocking command)

Hooks intended to block (PreToolUse/Bash) are `prompt` type — Claude evaluates and returns BLOCK/ALLOW. Hooks intended not to block (PostToolUse, PreCompact, SessionStart) are `command` type and exit 0 unconditionally with `|| true` suppression on every sub-command. Defensive `[ -f "$CONFIG_FILE" ] || exit 0` guards at the top of every non-blocking hook. Appropriate as a learned discipline — earlier `prompt`-type non-blocking hooks caused "stopped continuation" errors when their inputs were missing (e.g., no project config file); command-type with explicit fail-open is the corrective. The principle is that prompt-type treats output as blocking and command-type does not, so blocking hooks stay prompt and non-blocking hooks become command.

### Fail-closed on bootstrap, silent fail-open on runtime hooks

SessionStart bootstrap uses `set -euo pipefail` and halts on any error (Python version check, venv create failure, pip install failure). Runtime hooks (Stop, UserPromptSubmit) wrap their async work in bare `except Exception: sys.exit(0)` blocks — errors during ingest or context injection never surface to the user. Appropriate when the bootstrap must establish strict preconditions (right Python version, working venv) but the runtime hooks are "best-effort" augmentations that should never disrupt the user's session. Trade-off: silent failure means a misconfigured runtime hook is invisible to the user and only discoverable by inspecting plugin internals.

## Hook timeout and async philosophy

How the plugin sizes the latency budget for each hook based on what the hook does and what it blocks.

### Differentiated per-hook timeouts

`UserPromptSubmit` carries an explicit timeout (e.g., 10000 ms) because it blocks the model and must finish fast. `Stop` is `"async": true` with no timeout — fire-and-forget background work like graph ingest. `SessionStart` has no timeout because provisioning (pip install, venv build) can take minutes on first install and must not be killed. Three different postures for three different latency budgets on the same plugin. Appropriate when each hook has a fundamentally different relationship to user-perceived latency: blocking-the-model versus fire-and-forget versus first-time-setup. The 10-second ceiling on prompt-time context injection drives downstream design choices (graph cache to eliminate per-turn rebuild, k-limited search) — the timeout is not just a guardrail but a budget that shapes what the hook can do.

## Session context loading

How the plugin injects project-aware context into the agent's session at startup or on user prompts.

### SessionStart additionalContext via JSON

The SessionStart hook emits stdout JSON `{"hookSpecificOutput":{"additionalContext":"..."}}` summarizing plugin state (e.g., counts of projects/posts tracked, ready-state messages, slash-command hints). Computed by grepping state files cheaply on every session start. Appropriate when the plugin wants to remind the agent of in-flight state at the start of every session. Trade-off: the recompute is tightly coupled to the exact state-file formats — a schema change in those files would silently produce zero counts.

### SessionStart prints plain markdown to stdout

The hook script prints plain markdown text to stdout (which Claude Code surfaces to the agent at session start) rather than using the structured JSON `additionalContext` mechanism. Content is either a first-run nag ("plugin detected but not initialized") or the contents of a session-memory file (populated by `PreCompact`) when present. Appropriate as a simpler mechanism when the plugin doesn't need the JSON envelope's other fields. Trade-off: no validation against the structured-output contract; relies on Claude Code's tolerance for non-JSON SessionStart output.

### UserPromptSubmit additionalContext via JSON

A `UserPromptSubmit` hook queries state (e.g., reasoning graph) for content relevant to the user's prompt and emits a JSON object with `additionalContext` keying the injection. Appropriate when the plugin can produce per-prompt context (memory, retrieval, query expansion) within a tight latency budget. Two output shapes are observed in the wild: a bare top-level `{"additionalContext": ...}` versus the spec-documented `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ...}}` — the first form is potentially legacy or tolerated by the harness; whether the bare shape is silently accepted in current Claude Code releases is uncertain.

### SessionStart matcher absent (fires on every sub-event)

The `SessionStart` entry in `hooks.json` declares no `matcher` field. Per the Claude Code reference, matcher absence (or empty matcher) means the hook fires on all sub-events: startup, clear, compact, resume. Appropriate when the bootstrap is short-circuit-cheap (already-initialized check) so re-firing on every sub-event is harmless. Trade-off: side effects that are non-idempotent (e.g., appending to `$CLAUDE_ENV_FILE`) accumulate across sub-events; idempotency must be designed in or accepted as a known issue.

## Long-running scheduled behavior

How the plugin handles scheduled or recurring work that needs to run independently of an interactive Claude session.

### Outsourced to GitHub Actions cron

No `monitors.json`, no Claude Code-scheduled background work. Long-running scheduled behavior (daily cycles, engagement reports) runs in `.github/workflows/*.yml` on cron triggers. The plugin is the "author/debug" interactive surface; CI is the "operate" durable-scheduler surface. Appropriate when the plugin's user already has a GitHub repo for their work and write access to it; CI minutes are cheap and the discipline of managing scheduled jobs in `.github/workflows` is well-understood. Trade-off: requires a GitHub repo and OIDC or secrets-based credentials in Actions; doesn't help users on private/self-hosted Git platforms.

### Slash-command surface only (no scheduling)

No `monitors.json`, no CI cron. Long-running state surfacing is handled entirely by agent-invoked slash commands (e.g., `/<plugin>:dashboard`, `/<plugin>:status`, `/<plugin>:standup`). Appropriate when the plugin's value is on-demand inspection rather than scheduled execution; sidesteps the entire monitoring surface.

### None (context-provider plugin)

The plugin is a context provider (memory, retrieval) and does not have any scheduled or recurring surface to expose. Appropriate when the plugin's value is purely reactive (per-prompt context injection, per-stop background ingest).

## Plugin-to-plugin dependencies

Whether the plugin declares `dependencies` referring to other plugins it requires.

### None

No `dependencies` key in `plugin.json`. The plugin is self-contained.

## Test framework

The test runner and harness used for the plugin's own tests.

### pytest with asyncio support

`pytest` with `pytest-asyncio` declared in `[project.optional-dependencies].dev` of `pyproject.toml`. `[tool.pytest.ini_options]` configures `testpaths = ["tests"]`, `pythonpath` if needed, optionally `asyncio_mode = "auto"`, and custom markers (e.g., `integration` for tests that hit real LLM APIs). Test runner invoked as direct `pytest tests/ -v` or with marker filters (`-m "not integration"` for unit-only). Appropriate for Python-based plugins with async code paths. Substantial test suites (multi-thousand-line files spanning resolver, mutator, integration) can coexist without CI when integration tests require live API keys and the author runs them locally.

### Hand-rolled bash test harness

A single bash script (e.g., `tests/test-tracker.sh`) implements `assert_eq`, `assert_contains`, `assert_not_null` helpers and runs the plugin's bash logic directly. Test runner invocation is direct `bash tests/test-tracker.sh`. Appropriate when the plugin is bash-only and a Python test framework would force a runtime dependency just for testing. Trade-off: tests typically `source` the underlying library directly rather than invoking the bin wrapper, so wrapper-path bugs (the pattern that broke in a real release) are untested.

## CI presence and shape

Whether GitHub Actions (or equivalent) runs tests/lint on push/PR, and what scope the CI covers.

### Test workflow on push/PR plus scheduled jobs

`.github/workflows/test.yml` runs lint (e.g., `ruff check`) and `pytest tests/ -v` on `push: branches: [main]` and `pull_request: branches: [main]`. Additional workflows handle scheduled work (daily cron) or manual dispatch (release/launch). All workflows hard-code Python 3.12 and ubuntu-latest with no matrix; actions are pinned to major tags (`actions/checkout@v4`, `actions/setup-python@v5`) without SHA pinning; no caching (every run re-installs wheels). Appropriate as the standard "minimum viable CI" shape. Trade-off: scheduled bot commits (daily cycle commits to main) trigger test runs for no code change, burning CI minutes; could gate on path filters. No matrix means newer Python versions are untested even if `requires-python` permits them.

### None

No `.github/workflows/` directory at all. Tests exist (often substantial) but are documented as "run locally". Appropriate when the test suite requires live API keys or has external dependencies the author doesn't want to encode as Actions secrets, but leaves no objective gate between commits and the next user install. Trade-off: regressions in well-tested code paths can land silently; rapid bugfix-release cascades become more likely because there's no automation catching what local runs miss. The absence is sometimes correlated with a pure-bash design where the test harness exists but a CI runner of bash scripts feels redundant.

## Release automation

Whether tag pushes, GitHub releases, or other automation cut releases — versus hand-cut releases without automation.

### None — manual `gh release` or web UI

Releases are hand-cut via `gh release create` or the GitHub web UI. Tag commits land on main; release notes are hand-written into the GitHub release body. No `softprops/action-gh-release`, no `release-please`, no `semantic-release`. No tag-sanity gates verify `plugin.json` version matches the tag, that the tag is on main, or that anything was tested before tag time. Appropriate for small projects where release cadence is low and manual discipline is sustainable. Trade-off: in plugins where `plugin.json` version, marketplace.json version, and tag name all have to align, three fields must be edited in sync by hand; a single-line CI check would eliminate the entire class.

### Not applicable (no releases)

No tags, no releases. The plugin is pre-1.0 or in continuous-deploy-from-main mode where install always takes HEAD. Appropriate while the design is unstable and the author doesn't want to commit to versioned snapshots yet.

## Marketplace validation

Whether a workflow validates manifest structure, frontmatter shape, or hooks.json schema before publish.

### None — externalized to user-side install

No validation workflow. The author discovers manifest-structure problems by failing to install against the validator that ships with Claude Code itself — i.e., validation is externalized to the end-user's `/plugin install` flow. The `$schema` field (when present) is declarative but not validated by any workflow on this repo; install-time rejection by Claude Code is the only enforcement. Past releases have recovered from manifest-structure mismatches that would have been caught pre-publish by a validator (e.g., `plugin.json` at wrong path, `.md` hook files instead of `hooks.json`). Appropriate when the author treats Claude Code's validator as the canonical gate and accepts the cost of an iterative publish-fail-fix loop. Trade-off: the cost of validation falls on users who tried to install a broken release.

## Documentation set

The set of documentation files at the repo root and how they distribute purpose, architecture, and operational content.

### README only

A single `README.md` at repo root — install + use + what-it-does + credentials/config + dev instructions. No `CHANGELOG.md`, no `architecture.md`, no `CLAUDE.md`. Community health files (SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, ISSUE_TEMPLATE) absent. Appropriate when the plugin is small enough that one document holds everything a user needs. Trade-off: technical readers must reverse-engineer the design from source; a multi-skill plugin's README that markets by outcome offers thin technical-discovery surface (skill names not enumerated). LICENSE may be claimed in README and `plugin.json` but absent as a file at root, which causes GitHub's license-detection to return null and breaks license-tooling that consumes the API.

### README + CONTRIBUTING + CLAUDE.md (no architecture.md, no CHANGELOG)

Repo-root `README.md` (with badges, installation, command/skill catalog), `CONTRIBUTING.md` (prerequisites, project structure), and `CLAUDE.md` doubling as project overview plus agent-facing operational reference (key-files index, command reference, bash-usage rules, known gotchas). No dedicated `architecture.md` — architectural content is split between CLAUDE.md "Architecture" and README "How It Works", with a separate long-form `GUIDE.md` for human readers. Appropriate when the author treats CLAUDE.md as the single agent-context document; the layering overlaps with README. Trade-off: same architectural content is described with different framings in two places; readers must know which document to open.

### README + docs/ tree (architecture, configuration, walkthrough, limitations)

Repo-root `README.md` (Quick Start, Claude Code integration, MCP tools table, SDK integration, "How It Works" pipeline diagram) plus a `docs/` directory with `architecture.md`, `configuration.md`, `walkthrough.md`, `limitations.md`, `assets/`. `.gitignore` may explicitly exclude `CLAUDE.md` and `**/CLAUDE.md` — a deliberate stance that agent-context files are not committed. Appropriate when documentation is unusually complete relative to repo size and the author maintains a real dev reference. Trade-off: the explicit exclusion of CLAUDE.md is unusual; most projects either commit it or take no stance.

## Host-project setup

How the plugin handles configuration, scaffolding, or hook installation in the user's host project (versus in the plugin itself).

### None (plugin operates standalone)

The plugin requires no host-project scaffolding. State and config live entirely under `${CLAUDE_PLUGIN_DATA}` or are derived from the user's existing repo without modification. Appropriate when the plugin is self-contained and the host project is a passive subject of the plugin's operations.

### Setup script scaffolds the host project

A `scripts/setup.sh` (often invoked via a `/<plugin>:setup` slash command) creates a project-local config directory (e.g., `.coco/`), populates a default config file, installs git hooks into `.git/hooks/` of the host project, merges plugin permissions into the host's `.claude/settings.json`, and adds plugin artifacts to the host's `.gitignore`. Migration logic (e.g., legacy slug rename) may also be embedded. Most plugins leave host-project setup to the user; this approach takes ownership. Appropriate when the plugin's value depends on host-project artifacts (rules, hooks, permissions) being in place. Trade-off: setup script in-tree and slash-command both invoke the same scaffolding and the duplication is real (the script tail may even acknowledge equivalence); one path is sometimes legacy. Aggressive scaffolding mutates the host project in ways the user must re-discover when they move to a fresh checkout.

## Identity / brand stance

Constraints on technology choices that flow from a deliberate identity ("zero deps", "self-contained", etc.) rather than from technical necessity.

### Zero-runtime-dependency stance

"bash + jq, no daemon, no database, no node_modules" is a load-bearing README badge and pitch. The stance constrains several other axes — no PEP 723 scripts, no npm packages, no binary downloads — in service of a distinctive identity. Appropriate when minimalism is a brand differentiator and the workflow fits in shell. Trade-off: the surface of tools available to the author is constrained; system-tool version requirements (bash 4+, jq 1.6+) become hard prereqs that older platforms (macOS bash 3.2) silently fail against.

### Dual-mode plugin/library

The same source tree installs either as a Claude Code plugin (via marketplace) or as a pip-installable Python library (via `pip install -e ".[dev]"` plus a project-local `init` command). The library-mode entry point declared in `pyproject.toml [project.scripts]` is invisible to plugin-mode users because their venv lives in plugin data and isn't on PATH. Two install paths, one conceptual surface, no runtime overlap because plugin-mode uses `${CLAUDE_PLUGIN_ROOT}`-relative paths and library-mode uses project-absolute paths. Appropriate when the plugin's value is broader than Claude Code (e.g., a memory library usable from any agent harness). Trade-off: two installation flows must be documented and tested separately; some configuration (e.g., MCP server registration) has parallel mechanisms (inline in `plugin.json` for plugin-mode, `.mcp.json.example` template for library-mode).

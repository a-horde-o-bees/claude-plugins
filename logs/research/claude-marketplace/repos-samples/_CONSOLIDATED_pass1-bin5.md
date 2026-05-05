# Sample

Pass-1 Phase-1a partial for bin 5. Functional decomposition of `Emasoft/token-reporter-plugin`, `HiH-DimaN/idea-to-deploy`, `IgorGanapolsky/ThumbGate`, organized by role with implementation paths as sub-sections.

## Marketplace manifest shape

How the repo presents itself to a marketplace aggregator — whether it ships a `marketplace.json`, what flat-vs-nested fields it carries, and whether it uses a `metadata` wrapper.

### Single-plugin marketplace.json at repo root

A `.claude-plugin/marketplace.json` co-located with `plugin.json` in the same repo, containing exactly one entry that points back at the same repo. Top-level fields are flat (`name`, `version`, `owner`, `plugins[]`); a top-level `description` may also be present. Constrains discovery to one entity per repo and removes the need for a separate aggregator. Appropriate when an author ships a single plugin and wants it directly installable without going through a third-party catalog.

### No marketplace.json — plugin source repo only

The repo carries only `.claude-plugin/plugin.json`; the marketplace listing lives in a sibling repo controlled by the same author. The plugin repo is a leaf source, not an aggregator. Constrains the publish pipeline to a cross-repo coordination problem (see release notification under release automation), and means a fork can be installed only after publishing through the sibling marketplace. Appropriate when an author wants a separate aggregator repo to list multiple plugins, or wants to keep marketplace-discovery state out of source repos.

### `$schema` declaration on marketplace.json

A declarative `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` field on the marketplace document. No CI step actively validates against the schema, so the field is editor-assistance only — IDEs offer field completion and inline error squiggles. Outlier in the population sampled. Appropriate when an author wants editor-time validation without committing to wire-up of a real schema-validation gate.

### Custom non-schema fields on marketplace entries

Fields not in any documented marketplace schema, used as de-facto extension points. Observed: an `images: [url]` field carrying a marketing-asset URL on a plugin entry; a `tags: ["community-managed"]` flag distinct from `keywords` and used as a provenance signal rather than a discoverability signal. Permissive consumers ignore these; strict consumers reject them. Constrains the choice of validator — strict schema enforcement breaks. Appropriate as a forward-compatible extension hook when no upstream field exists for the metadata the author wants to expose.

### Redundant metadata sub-object on plugin entries

A nested `metadata: {}` dict on a plugin entry that duplicates sibling fields (`author`, `homepage`, `license`, `keywords`, `category`). Two locations on the same entry carry the same facts; `keywords` and `tags` arrays may also be identical. Constrains validators that want to enforce single-source-of-truth — a drift detector has to either pick a winner or accept divergence. Appears to be a layering accident from generators or from manual edits across two different consumer expectations.

## Plugin source binding

How the marketplace entry resolves to the actual plugin payload — git source, npm package, local path, or other. The choice constrains whether a fork is installable, whether unpublishing breaks installs, and whether a CDN sits between user and source.

### `source: github`

The marketplace entry points at a GitHub repo by `owner/repo`; `/plugin install` clones the repo at HEAD or at a specified ref. Installs survive registry outages but depend on GitHub availability. Forks are first-class — install URL changes, install path same. Appropriate when the plugin author wants direct fork-friendliness and is willing to push releases as git refs rather than registry artifacts.

### `source: npm`

The marketplace entry is `{ "source": "npm", "package": "<name>" }`; `claude plugin install` resolves the package against the public npm registry. Constrains the plugin to be a Node package and pulls in npm's distribution surface (CDN propagation delay, dist-tags, `npm unpublish` risk). A user cannot install a fork or PR until the fork is published to npm under a different name. Appropriate when the plugin is fundamentally a Node CLI with broader reach than just Claude (the same package powers Claude Desktop, Cursor, OpenCode, etc.); the Claude plugin entry is then a thin alias of the npm package.

### Implicit (single-plugin source repo)

No marketplace.json in this repo, so the source format is determined by whatever sibling marketplace lists the plugin (and is opaque from the source repo's perspective). Constrains analysis — a researcher reading only the source repo cannot determine source format without fetching the aggregator.

## Version coordination

Where the canonical version lives and how multiple version-carrying files are kept in lockstep. The functional concern is not "what version are we on" but "how does the system prevent drift between locations that all need the same number."

### Atomic-bump release script

A local-only script (e.g. `scripts/publish.py`) bumps every version-carrying file (`plugin.json`, `pyproject.toml`) in one step, then re-runs the schema validator post-bump to confirm parity. The script is the only sanctioned bump mechanism, gated by a pre-push ancestry check that rejects any push not driven by the script. Constrains the maintainer to use the script (or work around the gate); rejects env-var or marker-file spoofing schemes as forgeable. Appropriate when the maintainer accepts a strong release-discipline gate and wants cross-file parity enforced at write time.

### Cross-manifest sync script with `--check` mode

A script (e.g. `scripts/sync-version.js`) treats one file (typically `package.json`) as the single source of truth and rewrites the others. The same script in `--check` mode runs in pre-commit, CI, and publish workflows to fail builds on drift. Generalizes to ~15 manifests/HTML pages syncing from one source. Constrains every contributor to either run the writer script before commit or accept a CI failure. Appropriate when the version surface is genuinely large (many adapter manifests, READMEs, registry descriptors) and a per-file manual checklist would be impractical.

### Manual checklist with rubric-based audit

No bump automation; release-prep PRs hand-edit each version-carrying file (5+ files: `plugin.json`, marketplace.json, README badge, README.ru badge, per-skill `metadata.version`). A separate machine-checked rubric (e.g. `tests/meta_review.py` gates `M-C5`/`M-C6`) runs in CI and validates that all files agree on a single version. Catches drift but does not prevent it. Constrains the maintainer to per-release attention; the rubric is the safety net rather than the guard rail. Appropriate when the maintainer prefers explicit-edit discipline and treats CI as the late-stage drift detector.

### Separate registry-side version

The marketplace listing in a sibling repo is a third version sync point, kept in lockstep via a webhook-style notifier (see release automation). Constrains the publish flow to a cross-repo coordination dance even after intra-repo bumps are clean.

## Channel distribution

Whether the plugin offers stable/latest channels, how consumers pin a version, and whether the channel mechanism is at the marketplace layer or at the artifact layer.

### Single channel — tag-on-main

No channel split. Every commit on `main` is a release candidate; tags `v1.x.y` land on main commits; consumers either accept `HEAD` or pin via `@v1.x.y` ref on the marketplace entry. Constrains rollback to git-ref pinning by the consumer rather than channel switching by the publisher. Appropriate for solo or small-team plugins where the maintainer doesn't want to maintain a stable branch.

### Dual-asset filename aliasing on GitHub Release

Both a versioned filename (`thumbgate-claude-desktop-v1.14.1.mcpb`) and a channel-aliased filename (`thumbgate-claude-desktop.mcpb`) are uploaded to the same release via `cp`. The channel filename rolls forward with each release; the versioned filename pins. Orthogonal to marketplace channels — operates at the GitHub Release artifact layer. Constrains consumers to choose at download time which lifecycle they want. Appropriate as a lightweight alternative to maintaining parallel `stable-*`/`latest-*` marketplace manifests.

### Disabled-channel skeleton

A release-channel infrastructure that exists in code but is intentionally inert until the maintainer flips a switch — e.g., `release/*` short-lived branches with a fixture-smoke workflow whose job header carries `if: false` plus a missing `ANTHROPIC_API_KEY` secret. The infrastructure is committed for completeness and discoverability but consumers see a single-channel experience. Constrains nothing for current consumers but documents the future shape. Appropriate when the future channel split has a known cost (paid CI runs) the maintainer is not ready to absorb.

## Branching and tagging discipline

Where releases are tagged in git, whether a release-branch buffer exists, and how the plugin handles pre-release suffixes and dev counters.

### Tag-on-main

Tags `v*` land directly on commits on `main`; no release branches. The simplest form. Implies `main` ≈ release; HEAD consumers see the latest version immediately on every release commit. Appropriate for projects with low blast-radius releases or with a strong CI gate on main.

### Short-lived `release/*` branches as gate

PR-shaped release-prep branches (`release/v1.x.y`) exist solely to run an expensive workflow that's disabled on main (e.g., fixture-smoke against the live Claude CLI). The branch is merged back and tagged on main. Not a long-lived channel branch. Appropriate when one specific workflow is too expensive or too flaky to run on every main commit.

### Pre-release support shape (currently unused)

Code support for prerelease tagging (`isPrereleaseVersion()` helper feeding `--prerelease` to `gh release create`) without any actual prerelease tags published. Infrastructure-ready but cold. Appropriate for projects that anticipate prereleases but haven't needed them yet.

### Plugin-name-prefixed tag format

In multi-plugin repos, tags use `{plugin-name}--v{version}` to disambiguate per-plugin lifecycles. Single-plugin repos use plain `vX.Y.Z`. Constrains the parent repo's tag namespace.

## Plugin-component registration

How the plugin tells Claude Code about its skills, hooks, agents, MCP servers, and other components.

### Default discovery via conventional paths

`plugin.json` declares only metadata and (optionally) `userConfig`; component fields like `hooks`, `commands`, `agents` are absent. Claude Code discovers components by scanning known paths — `hooks/hooks.json`, `skills/<name>/SKILL.md`, `agents/*.md`. Constrains the layout: if components don't live at the conventional path, they're invisible. Appropriate when the layout matches the conventions and the manifest can stay minimal.

### Explicit path arrays

`plugin.json` includes `"skills": ["./skills/"]`, `"agents": ["./agents/"]`. Discovery is directory-rooted but explicit. The trailing-slash directory glob form recurses to find every `<name>/SKILL.md`. Constrains the directory layout to be enumerable from the listed roots. Appropriate when the author wants the manifest to make discovery roots explicit (often for tooling that walks the manifest rather than the filesystem).

### Inline mcpServers definition

`plugin.json` carries an `mcpServers` object directly: `{ "thumbgate": { "command": "npx", "args": [...] } }`. No separate `.mcp.json`. Claude Code launches the server with the inline command. Constrains MCP server config to flow through the plugin manifest; a sibling `.mcp.json` is unused. Appropriate when the plugin owns the MCP-server lifecycle and wants no second-source-of-truth for the launch command.

### Out-of-band hook registration

Hooks live in the repo as scripts (`hooks/*.sh`) but `plugin.json` has no `hooks` field. Registration happens via a side script (`scripts/sync-to-active.sh`) that patches the user's `~/.claude/settings.json`, or via a skill (`/adopt`) that writes a project `.claude/settings.json` from a template. The plugin's hook layer is not part of `/plugin install`'s reach. Constrains the user to a manual post-install step to get full hook coverage; the README has to document the gap. Appropriate when hooks are intended for opt-in adoption rather than passive activation, but needs a drift-guard (see governance) since the hook inventory and the registration list can disagree.

## Skill authoring conventions

Frontmatter fields and tool-permission syntax used inside `SKILL.md` files.

### Standard frontmatter

`name`, `description`, `argument-hint`, `allowed-tools`, `license`, plus `metadata.{author, version, category, tags}`. Per-skill versioning (where present) means SKILL.md frontmatter is yet another version-sync site.

### `disable-model-invocation: true` for high-blast-radius skills

A frontmatter flag that prevents auto-routing — the skill won't be auto-invoked via fuzzy embedding match. Users must call by name; routers must explicitly delegate. Applied to `/deploy`, `/migrate`, `/migrate-prod`, `/autopilot`. Constrains how the host model surfaces the skill in completion-style invocation. Appropriate for destructive operations where false-positive auto-routing has real cost.

### `context: fork` invocation hint

A frontmatter field on a router-style skill (`/autopilot`) suggesting subagent-like forked-context invocation. Documentation status unclear — possibly an undocumented Claude Code feature or a methodology-specific extension. Constrains the skill to a mode where it spins up a fresh agent context rather than continuing in the caller's.

### Mixed `allowed-tools` syntax

Same frontmatter line carrying plain tool names (`Read Write Edit`) and permission-rule syntax (`Bash(git:*)`, `Bash(pytest:*)`). The two forms coexist within one declaration. Constrains the parser; an author has to know which form Claude Code accepts in which slot. Appropriate when the skill needs both broad tool access and narrow command-pattern carve-outs.

## Agent authoring conventions

Frontmatter and tool-syntax for agent definitions under `agents/*.md`.

### Standard agent frontmatter

`name`, `description`, `model` (`opus`/`sonnet`), `effort` (`high`), `maxTurns` (integer), `allowed-tools`. No object-form permission rules; tools are space-separated names.

### Read-only agents

All agents in the population declare only read tools (`Read Grep Glob`) — no `Write`/`Edit`. Agents return structured markdown that the caller skill writes. Constrains the caller-callee contract: agents are advisors, the calling skill is the only writer. Appropriate when the author wants a clean read/write split between layers.

## Dependency installation

How runtime deps reach the host machine.

### Ad-hoc per-invocation fetch via `uv run --with`

Python plugins use `uv run --with <pkg> python3 ...` as the hook command. uv's global cache satisfies subsequent invocations (~3s first run, ~3ms cache hit per author measurement). No `SessionStart` hook, no `${CLAUDE_PLUGIN_DATA}` venv. Constrains the plugin to one-shot Python invocations (no long-running state across hook fires); requires `uv` on PATH; the plugin does not own a venv. Appropriate for thin plugins where dep set is small and per-invocation latency is acceptable.

### Ad-hoc per-invocation fetch via `npx --yes --package`

Node plugins use `npx --yes --package <name> <bin> serve` as the MCP-server command. Resolves through the user's npm cache; first launch fetches from the registry. The unpinned form silently rolls forward with whatever `latest` resolves to. A pinned variant (`<name>@<version>`) is available but not surfaced as the default. Constrains the runtime to npm-cache state; auto-upgrade is the default behavior unless the user explicitly pins. Appropriate when the plugin is itself an npm package and wants to share its CLI surface across multiple host integrations.

### Zero runtime deps (stdlib only)

The plugin ships only markdown (skills/agents) plus shell or stdlib-Python hook scripts. No package manager runs at install or runtime. Explicit design choice (e.g., `docs/CI.md` documents "intentionally zero-dependency"). Constrains the plugin to whatever bash + stdlib Python can do; removes supply-chain risk and the SessionStart-install lifecycle entirely. Appropriate when the plugin is fundamentally configuration / methodology rather than executable code with rich dep needs.

### Pre-built npm package as runtime

The plugin is itself an npm package; users install it through npm (transitively via the marketplace's `source: npm` binding), and the plugin manifest's commands invoke `npx <name>` against the installed package. No SessionStart install hook is needed because npm did the work. Constrains the entire plugin to npm's distribution model. Appropriate when the codebase is large (40+ runtime deps including native modules like `better-sqlite3`) and the plugin is one of many consumer surfaces over the same package.

## Bin-wrapped CLI distribution

When the plugin ships an executable visible on the Bash tool's PATH.

### Python `bin/` script with uv injection

`bin/<name>.py` with `#!/usr/bin/env python3` shebang; the script body does `uv run --with <pkg>` internally to inject deps. Plugin-root resolution via `${CLAUDE_PLUGIN_ROOT}` env var with `Path(__file__).resolve().parent.parent` fallback. Cross-platform via `subprocess.run` (chosen over `os.execvp` because the latter raises on Windows). Constrains the bin to use `.py` extension (extensionless or `.sh` flagged by validators as platform-specific); on Windows, `.py` association must be set for PATH invocation. Permissions are 100755. Appropriate when the plugin wants both hook-fire and on-demand-CLI access modes against the same script body.

### Node `bin/` via package.json `bin` field

The plugin's bin is declared via `package.json`'s `"bin": { "<name>": "bin/cli.js" }`, not via the plugin manifest. npm symlinks the binary into the user's `node_modules/.bin/`; on a global install it's on PATH. The plugin manifest is a thin alias and the bin reaches the user via the npm package, not through `/plugin install`'s payload. Constrains discovery — a user who installed only via the Claude marketplace might not have the bin unless the plugin is also globally `npm install`ed. Appropriate when the bin is the primary product and the plugin is one of many integration shims.

### No bin distribution

Plugin has no PATH-visible executable. All invocation flows through skills, hooks, or MCP. Most common when the plugin's value is methodology or contextual injection rather than user-facing tools.

### Version-floor declared only in prose

The minimum Claude Code version supporting a feature (`v2.1.91+` for `bin/`) is declared in a script docstring, a README section header, and README prerequisites — three documentation layers, zero machine-readable fields. `plugin.json` has no `requires.claude-code` / `engines` field. Constrains version-floor enforcement to graceful-degradation discipline (Claude Code silently ignores unknown hook events / fields, so older hosts get partial functionality). Appropriate when no machine-readable mechanism exists upstream and the plugin author prefers prose-documented degradation over a hard precondition check.

## User configuration

How user-tunable parameters surface to Claude Code's `userConfig` system.

### Typed `userConfig` schema in plugin.json

Each entry declares `type` (`number`/`boolean`), `title`, `default`, `description`. Descriptions can be substantive (multi-sentence, with links to upstream documentation explaining the default). The substituted values reach the runtime via env vars Claude Code sets when invoking hooks. Constrains every user-tunable value to be declared up front. Appropriate when the plugin has a small, stable knob set worth surfacing to users.

### Env-var fallback alongside userConfig

For hosts (older Claude Code versions) that don't support `userConfig`, the plugin reads plain env vars (`<PLUGIN>_<KEY>`) as a documented fallback. The runtime checks both the userConfig-populated env var and the plain-env name. Constrains the plugin to maintain two env-var conventions but extends host coverage. Appropriate when backwards-compat with a wider host set matters.

### No `userConfig`

The plugin exposes zero config surface; behavior is fixed. Knobs that exist (e.g., service API keys for a paid tier) are read from process env outside the plugin manifest, requiring users to set them through the host's separate env config. Constrains the user-facing UX — no auto-prompted setup. Appropriate when the plugin is genuinely tuneless or when the maintainer hasn't yet promoted its env-vars to first-class config.

## Tool-use enforcement

Whether and how the plugin gates or annotates tool calls before, during, or after execution.

### PreToolUse advisory injection

A hook on `PreToolUse` matched against `Bash|Edit|Write|NotebookEdit` (or similar) writes `hookSpecificOutput.additionalContext` JSON on stdout to inject context before the tool call. No blocking by default; the agent reads the injected lessons and can choose to comply. Constrains the agent's information environment without restricting its action space. Appropriate when the goal is teaching or reminding rather than blocking.

### PreToolUse blocking gate

The same hook adds a `decision: "block"` output when an env var (e.g., `<PLUGIN>_HOOKS_ENFORCE=1`) is set and a risk threshold is crossed. Default-off, opt-in to enforcement. Constrains the user to an explicit env-var flip before any blocking behavior fires; protects against accidental deadlocks during plugin onboarding. Appropriate when the hook's invariants are real but the maintainer wants advisory mode as the safe default.

### Soft-then-escalating PreToolUse hook

A hook starts in advisory mode, counts ignored reminders, and escalates to blocking after N consecutive ignores (e.g., 3 in `check-tool-skill.sh`). Constrains the agent to a documented escalation curve. Appropriate when the discipline being enforced is genuinely best-effort but persistent ignoring is a defect.

### Hard-blocking PreToolUse on commit-shape invariants

Hooks matched against `Bash` parse the command and block `git commit` when staged content fails a structural check (e.g. SKILL.md edited without referenced `references/` files; >2 files touched without `/review`). Constrains commit shape; users who legitimately need to bypass create a documented escape-hatch file (e.g. `.methodology-self-extend-override`). Appropriate when commit shape is verifiable from staged state and the cost of false-positives is bearable given a documented bypass.

### `PermissionDenied` as event log

The `PermissionDenied` hook event is registered, but the handler treats it as a counter / log source, not an enforcement gate. The hook tallies denials and surfaces the count in a report. Constrains nothing about future tool calls. Appropriate when the goal is observability rather than gating.

### Repo-scope self-restriction

Hooks inspect `cwd` for `.claude-plugin/plugin.json` (or another sentinel) and exit silently when run outside the methodology repo. Prevents the plugin's enforcement from interfering with unrelated projects on the same host. Constrains the hook surface to the repo where it makes sense; means the hook never fires outside that repo unless `/adopt` has written project-level settings. Appropriate for plugins whose enforcement only applies to their own methodology context.

### Documented bypass mechanism

A sentinel file (e.g. `.methodology-self-extend-override`) that, when present in the repo, suppresses hard-enforcement hooks. Documented in the hook README rather than hidden. Constrains the hook's invariant — "block unless escape hatch is explicitly present." Appropriate when there are legitimate cases (extending the methodology, e.g.) where the invariant should not apply.

### No enforcement (observational only)

The plugin uses hook events purely for reporting; no gating. Even events like `PermissionDenied` are inert as gates. Constrains the plugin's operational role to reporter / observer.

## Session context loading

How the plugin injects context into a session — at start, on every prompt, or via skill invocation.

### `SessionStart` context injection

A hook on `SessionStart` (no matcher → fires on startup, clear, compact) reads prior-session state (summaries, lesson stats, prevention rules) and emits `additionalContext`. Loads once per session boundary. Constrains the per-session token budget (one big load); state must persist across sessions in some external store. Appropriate when the context is heavy and per-turn loading would be wasteful.

### `UserPromptSubmit` per-turn context

Hooks on `UserPromptSubmit` fire on every user message, emitting `additionalContext` per turn. Multiple hooks can stack (diagnostic, pre-flight, skill-router). Constrains per-turn cost (token + latency) but avoids stale-context staleness — every prompt sees fresh state. Appropriate when context is small enough per-turn or when freshness is more important than per-turn cost.

### Hook-emits-context output convention

Both styles use `hookSpecificOutput.additionalContext` (JSON on stdout) as the inject mechanism. Hooks are silent (exit 0, no output) when no content matches — keeps normal turns noise-free.

### No session-context ambition

The plugin does not register `SessionStart` or `UserPromptSubmit` hooks; reports or other behaviors fire only on completion-class events (`Stop`, `TaskCompleted`, etc.). Constrains the plugin to post-fact observation. Appropriate when the plugin's job is summarization rather than guidance.

## Live monitoring and notifications

Whether the plugin uses Claude Code's monitor surface for ambient ticking.

### `monitors.json` absent

No samples in this bin use the monitor feature. Either the surface is too new, the plugins predate it, or none have a polling-style use case. Constrains the plugin's ability to do truly background work — without monitors, the plugin has to piggy-back on hook events.

### Statusline as monitor analog

A `statusLine` entry in `.claude/settings.json` invokes a CLI to render a per-session status line. Updated reactively via PostToolUse hook on specific MCP tool calls. Not a monitor per se; the per-session equivalent. Constrains updates to events the host already fires.

## Plugin-to-plugin dependencies

Whether the plugin declares dependencies on other plugins.

### No `dependencies` field used

None of the samples in this bin declare cross-plugin dependencies. All are single-plugin repos with plain `vX.Y.Z` tag formats; the `{plugin-name}--v{version}` multi-plugin tag form is not exercised. Constrains the bin's view of cross-plugin coupling to negative evidence; whether the field is unsupported, unused, or simply unneeded for these plugins is not determinable from the samples alone.

## Test discipline

Whether and how the plugin defines an automated test suite.

### Stdlib-only Python rubric tests

Tests are zero-dependency Python 3.11 stdlib scripts (`tests/meta_review.py`, `tests/verify_snapshot.py`, `tests/verify_triggers.py`), invoked directly via `python3 tests/<script>.py`. No pytest, no test framework. Plus bash fixture-runner scripts for live-CLI tests. Test model is "structural-rubric + golden snapshots," not unit tests. Each rubric check has a stable ID (`M-C1`...`M-C16` Critical, `M-I1`...`M-I9` Important) referenced in CHANGELOG entries — CI-check-as-named-entity. Constrains contributors to write rubric checks in stdlib idioms; rationale: <30s runs, no supply-chain risk in CI itself, runnable locally without setup. Appropriate when the project privileges CI itself being trust-minimized.

### `node --test` chained suite

Hundreds of `tests/<name>.test.js` files under one flat directory; each wired to a `test:<name>` npm script; the root `npm test` chains 70+ entries with `&&`. Sequential, ordering-load-bearing, single failure aborts the chain. Constrains parallelism (none) and ordering discipline (highly so). Plus a separate `prove:*` tier — seven scripts that emit machine-readable `proof/<area>/report.{json,md}` artifacts to GitHub Actions, distinct from the `test:*` tier. Appropriate at scale where the maintainer wants every behavior covered and accepts the long-chain trade-off; the `prove:*` tier supports post-hoc auditing of CI runs.

### No test directory present

The repo references tests in release-script docstrings (`scripts/publish.py` gate 6 expects `tests_dev/`) but no test directory is checked in. Either gitignored locally-only or the gate is dormant. Constrains the project's claimed test discipline to the maintainer's local machine. Appropriate when the maintainer treats tests as private and CI as a public surface.

### Headless `claude -p` snapshot testing

A workflow runs the Claude Code CLI itself in non-interactive `--input-format stream-json --output-format stream-json --no-session-persistence --dangerously-skip-permissions --max-budget-usd <N>` mode against pre-seeded `stream.jsonl` user-turn fixtures, validating output against `expected-snapshot.json`. Per-fixture USD budget cap enforced by the CLI. Cost profiles documented in-tree (~$8–$12 per release). Constrains the testing budget to real money and exposes test results to model-variance. Appropriate when the plugin's core value is the methodology's behavior under a real model — unit tests cannot substitute.

## CI workflows

Continuous-integration coverage outside the test-running concern.

### Minimal cloud CI

A single workflow that does one job — typically a webhook-style notify (e.g., `notify-marketplace.yml` fires `repository_dispatch` to a sibling marketplace repo when `plugin.json` changes). Linting, type-checking, and test execution live in pre-push hooks and release scripts, not in cloud CI. Constrains contributors who fork the repo without adopting the local hook setup — they get no quality gates at all. Appropriate when the maintainer trusts the local pipeline more than cloud CI and wants minimal cloud surface.

### Discipline-checking CI on push and PR

Workflows on `push: main` + `pull_request: main` run a custom rubric (e.g., `meta-review.yml` running `meta_review.py`, `verify_triggers.py`, `verify-sync-to-active.sh`). Targets methodology invariants — version-string parity, skill-count, frontmatter, registration-list drift — rather than the marketplace schema. Constrains the meta-rubric to be the gating contract; external `$schema` validation is not wired in even when declared. Appropriate when the plugin's invariants are richer than the upstream schema.

### Sprawling autonomous workflows

The `.github/workflows/` directory hosts 30+ workflows including cron-driven autonomous loops (`daily-revenue-loop.yml`, `instagram-autopilot.yml`, `gtm-autonomous-loop.yml`, `ralph-loop.yml`, `self-healing-auto-fix.yml`). Orthogonal to plugin distribution but co-resident in the same repo. Constrains the repo's surface area dramatically; mixes plugin-distribution workflows with non-code automation. Appropriate only when the repo intentionally serves both as a plugin source and as an operations hub.

### Action-pinning conventions

Sampled choices: SHA-pinned with version comment (`peter-evans/repository-dispatch@<sha> # v4.0.1`), tag-pinned (`actions/checkout@v4`, `actions/setup-node@v6`). Even within one repo, conventions can be inconsistent (SHA on one action, tag on another). Constrains the security posture — SHA pinning resists hostile-tag substitution; tag pinning trusts the action publisher.

### CI-trigger-as-signal-of-traction

Documented case (CHANGELOG v1.8.0): CI was added specifically because the repo got "3 GitHub stars within 24h of publishing." Adoption signal flipped the cost/benefit on adding CI. Captures the pattern: small projects defer CI until a traction signal appears.

## Release automation

How a release moves from "the maintainer typed a version number" to "users can install it."

### Local-script release pipeline

A maintainer-machine-only Python script (`scripts/publish.py`) orchestrates 15 mandatory gates: tool availability, pre-push hook, clean tree, lint, type-check, py_compile, tests, schema validate, atomic version bump, schema re-validate, CHANGELOG regen via `git-cliff`, release commit, annotated tag, push (gated by ancestry check), `gh release create` with notes from CHANGELOG. Process-ancestry pre-push gate (walks `ps -p <pid> -o args=` rejecting any push not driven by the script) prevents the gate from being bypassed. Constrains the release to the maintainer's working machine; no cloud audit trail; depends on local toolchain (uvx, git-cliff, gh CLI, uv) being correctly installed. Appropriate when the maintainer privileges total local control over cloud reproducibility.

### Path-filtered cloud publish workflow

A workflow on `push: main` with `paths` filter targeting only `package.json`/`package-lock.json`/`server.json`/the workflow file. Tag creation moves *inside* the job, conditional on a decision script's output (`scripts/publish-decision.js`). Multi-trigger: `push: main` + `release: published` + `workflow_dispatch`. Constrains a maintainer to bumping `package.json` deliberately to fire the workflow; non-bump commits don't ship. Appropriate when the publish discipline is "bump = release" and main has high commit cadence on non-shipping changes.

### Manual release via `gh release` UI

No release automation. CHANGELOG.md follows Keep a Changelog format with rich per-release sections (`Added`, `Changed`, `Fixed`, `Ops`, `Context`, `Rationale`, `Lessons learned`, `Deliberately not done`). Releases produced via GitHub UI or `gh release create`. Constrains the maintainer to per-release attention and discipline; CHANGELOG depth carries documentation that automation might otherwise generate. Appropriate when the maintainer values release-note craft over throughput.

### Silent-no-op regression detector

A guard step in publish workflows that fails CI when the version is already on the registry *and* the shipped-files allow-list has commits since the last `v*` tag. Encodes a specific past regression class ("version published, content changed but not shipped"). Constrains every commit to either bump version or not touch shipped files. Appropriate as a defense-in-depth step where a known regression class has burned the maintainer.

### Post-publish runtime smoke

After `npm publish`, a workflow step pulls the freshly-published tarball *back from the registry* (`prove-packaged-runtime.js --package-spec "<name>@<version>" --install-attempts 12 --install-delay-ms 10000`) and smoke-tests it. Retries handle CDN propagation. Closed-loop: "publish verified only when the thing downstream users would pull actually works." Constrains the publish workflow's wall-clock; provides positive evidence of consumer-side install success.

### Cross-repo notify on plugin.json change

Workflow fires `repository_dispatch` (`plugin-updated` event) on a sibling marketplace repo when `.claude-plugin/plugin.json` changes. PAT-gated, one-way. Keeps marketplace state in sync without bidirectional write access. Constrains the relationship to a single secret (PAT) and a custom event-name convention. Appropriate when source and aggregator are decoupled and the maintainer wants a lightweight sync trigger.

## Marketplace validation

What checks run on the marketplace and plugin manifests before a release ships.

### External validator referenced by name

A third-party tool (`cpv-validate` / claude-plugins-validation) referenced in release-script docstrings as the schema validator. Not vendored; fetched per gate; depends on network availability on release day. Constrains release-day reliability to the validator's host being up. Appropriate when the validator is genuinely shared infrastructure across the ecosystem.

### Custom rubric covering methodology invariants

A bespoke `tests/meta_review.py` (or equivalent) checks version parity, frontmatter validity, skill-count, marketplace.json internal consistency, trigger-phrase drift, hook-sync drift. Treats the marketplace schema as a side concern (the `$schema` link is declarative only). Constrains the validator surface to whatever the rubric covers; a strict schema validator would catch different things. Appropriate when methodology invariants are higher-value than schema conformance.

### Cross-manifest version-sync as validation

A drift-detector script (`sync-version.js --check`) is invoked from CI, pre-commit, and publish workflows. It validates that `package.json`, `plugin.json`, `marketplace.json`, `server.json`, README badges, etc. all carry the same version. Constrains every contributor to use the writer-mode of the same script (or to update all manifests by hand and accept the gate).

### Local-only validation, no cloud gate

Manifest validation lives entirely in pre-push hooks and the release script. PR branches run only feature-branch gates (lint + JSON parse). Constrains validation to the maintainer's discipline; contributor PRs ship with weaker checks. Appropriate when the maintainer is the only release author.

## Documentation surface

What docs ship with the plugin and at what granularity.

### Single comprehensive root README

One large `README.md` at repo root (15-25 KB) covering everything — feature description, install, configuration, examples, troubleshooting. Architecture content embedded inline rather than separated. Constrains a reader's ability to navigate to one specific concern. Appropriate for thin plugins where doc volume doesn't justify multi-file split.

### Multi-doc architecture (no separate ARCHITECTURE.md)

Substantial root README plus per-skill SKILL.md plus contributing/changelog/CI docs (`docs/CI.md`, `docs/CONTENT-PLAN.md`). No top-level `ARCHITECTURE.md`. The architectural narrative lives in README sections (e.g., "Call Graph", "Skill Contracts", "How It Works"). Constrains future maintainers to reconstruct the architecture from prose; works while the README author and the maintainer are the same person. Appropriate when README discipline is high and the architecture is methodology-shaped rather than code-shaped.

### Bilingual documentation

Full Russian + English READMEs (`README.md` + `README.ru.md`); per-skill `## Trigger phrases` lists in both languages; `check-skills.sh` regex tables include both-language matches. Constrains every doc-touch to update both READMEs (the version-sync script enforces parity). Appropriate when the user population is genuinely bilingual and each language carries equal trigger weight.

### Documentation sprawl

Many root-level docs covering go-to-market content (`LAUNCH.md`, `LAUNCH_NOW.md`, `LAUNCH_POSTS.md`, `DISTRIBUTION_RUNBOOK.md`, `FIRST_CUSTOMER_BATTLE_PLAN.md`, `gate-program.md`, `primer.md`) alongside developer docs. A new contributor cannot tell from `ls` which doc to read first. Constrains discoverability; works when the project intentionally mixes business and engineering surfaces.

### Promotion drafts in-repo

`docs/promotion/drafts/` carries marketing copy for HN, devto, habr, reddit, twitter. The custom rubric scans these for stale version references — promo content participates in version-drift validation. Constrains every release to update promo too.

### CHANGELOG depth as documentation

CHANGELOG entries carry not just `Added`/`Changed`/`Fixed` but `Ops` (per-release manual checklists), `Context`, `Rationale`, `Lessons learned (meta-review gap)`, `Deliberately not done (deferred)`. The latter two close a feedback loop between CI output and rubric improvements; the deferred section captures negative-space decisions as first-class entries. Constrains release discipline to thoughtful authoring. Appropriate when CHANGELOG is treated as the project's reasoning log rather than a feature manifest.

### Per-plugin README in `.claude-plugin/`

A scoped README (`.claude-plugin/README.md`) inside the plugin manifest directory, distinct from the root README and tailored to the Claude-Desktop install surface. Constrains the maintainer to two README surfaces with overlapping but non-identical content. Appropriate when the plugin is one of several integration shims and the root README is multi-host marketing material.

## Distribution-channel multiplicity

When the same package is published to multiple registries / surfaces simultaneously.

### Multi-adapter single-package shape

One npm package ships internal adapters for multiple host ecosystems (`adapters/{amp,chatgpt,claude,codex,forge,gemini,mcp,opencode}/`), each with its own integration descriptor (`config.toml`, `opencode.json`, `function-declarations.json`, `openapi.yaml`). A parallel `plugins/{amp-skill,claude-codex-bridge,claude-skill,codex-profile,cursor-marketplace,gemini-extension,opencode-profile}/` tree mirrors that at the plugin-format layer. Constrains every release to update every descriptor; the version-sync script makes this tractable. Appropriate when the codebase is genuinely platform-neutral and the author wants one bug-fix to land everywhere.

### Multi-registry publishing

Same release ships to npm, GitHub Releases (`.mcpb` bundle), and the MCP Registry (`server.json`-driven). Each surface has its own publish workflow (`publish-npm.yml`, `publish-claude-plugin.yml`, `mcp-registry-publish.yml`, `publish-codex-plugin.yml`, `publish-tessl.yml`). Constrains the release pipeline to coordinate N parallel workflows; an artifact failure in one needs an explicit re-run rather than blocking the others. Appropriate when each registry serves a distinct discovery population.

## Governance and self-audit

How the plugin checks its own state for invariants beyond standard testing.

### Registration-list drift guard

A script (e.g., `scripts/verify-sync-to-active.sh`) cross-checks every `hooks/*.sh` against a `DESIRED_HOOKS` allowlist in the registration script, with an explicit `EXEMPT` list for opt-in-only hooks. Run in CI as a separate gate. Constrains every new hook to be either registered or explicitly exempted. Added in response to a specific regression where a hook shipped to the repo but never landed in the sync script (users got 12/13 hooks). Appropriate when the registration list and the inventory are maintained separately and the gap is a documented failure mode.

### Derived-artifact drift detector

A validator cross-checks two files where one is meant to be a derived projection of another — e.g., `tests/verify_triggers.py` cross-checks every `## Trigger phrases` list in `skills/*/SKILL.md` against the regex patterns in `hooks/check-skills.sh`. The SKILL.md is source of truth; CI fails on drift. Constrains every trigger-edit to update both sites. Appropriate when one artifact auto-completes from another by hand and the gap is high-value to catch.

### Process-ancestry-verified pre-push gate

`scripts/pre-push` walks the process tree via `ps -p <pid> -o args=` to confirm `scripts/publish.py` is an ancestor process, rejecting pushes to main otherwise. Rationale: env-var/marker-file schemes are "trivially spoofable"; an ancestry check enforces release-discipline without trusting any mutable signal. Constrains all main pushes to flow through the release script. Appropriate when release discipline is non-negotiable and the maintainer accepts the rigidity.

### Self-observability via live API checks

A `test:congruence:live` step in CI calls the live GitHub API to verify the published "About" panel matches the repo's current state. Self-introspection during CI; depends on `GH_PAT` and external network. Constrains CI to occasional flakiness from API outages; provides drift detection between repo and registered metadata.

### Override file as documented bypass

The `.methodology-self-extend-override` sentinel file documents an opt-in suppression of hard enforcement. Mentioned in the plugin's defense-in-depth table. Constrains the hook's invariant to be "block unless this file is present"; surfaces the bypass in user-facing documentation rather than hiding it.

## MCP Registry presence

Whether the plugin registers itself with the upstream MCP Registry as well as Claude Code's marketplace.

### `server.json` as MCP Registry manifest

A separate `server.json` at repo root (distinct from `plugin.json` and `marketplace.json`) carries `$schema` pinned to `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`. Drives `mcp-registry-publish.yml`. The plugin reaches consumers through three discovery surfaces: npm registry, GitHub Release `.mcpb`, and MCP Registry. Constrains every release to update three registries; exposes the plugin to populations that don't search the Claude Code marketplace. Appropriate when the underlying server is genuinely MCP-shaped (not Claude-Code-specific).

### No MCP Registry presence

Most samples don't touch the MCP Registry; the marketplace and a single git/npm source are sufficient.

## Output and reporting conventions

How a hook or skill emits user-facing or system-readable output.

### `systemMessage` for human-readable summaries

Hooks emit `{"systemMessage": "..."}` JSON on stdout for report-style output that Claude Code surfaces inline. Used for completion-event reports (Stop, TaskCompleted, etc.). Constrains output volume to whatever Claude Code's hook-output cap allows (10,000 chars; overflow silently replaced with an opaque stub).

### `additionalContext` for context injection

Hooks emit `{"hookSpecificOutput": {"additionalContext": "..."}}` JSON to inject context the agent reads. Used by PreToolUse advisory injection and by SessionStart/UserPromptSubmit context loading. Distinct from `systemMessage` in that the agent processes the content rather than the user reading it directly.

### `decision: "block"` for gating

PreToolUse hooks emit `{"decision": "block", "reason": "..."}` JSON to refuse a tool call. Used by hard-blocking gates and the env-var-gated optional gates. Stderr carries the human message; stdout carries the contract.

### Inline-truncated + full-HTML dual output

When a report exceeds Claude Code's 10,000-char inline cap, the inline copy is truncated with `⋯ +N more — see HTML report` markers while a full HTML file is always written to a project-relative path (`<project>/reports/<plugin-name>/<timestamp>-<event>-<session>.html`). Convention is per-author across all their plugins, not a Claude Code platform feature. Constrains the plugin to manage its own out-of-band output store. Appropriate when reports legitimately exceed the inline cap and the user wants both a quick scan and a deep-dive.

### Stderr for debug logs

Stderr is reserved for debug-mode logs prefixed with the plugin's name; stdout for the contract. Maintains the JSON-on-stdout discipline regardless of debug verbosity.

## Failure posture

How the plugin handles errors mid-execution.

### Fail-open with try/catch wrapping

Every step wrapped in try/catch; uncaught failures fall through to allow. Rationale: "a bug in the hook never deadlocks the agent" (paraphrased from one author's header). Hooks always exit 0 even when their core function fails — observability degrades, but the agent isn't blocked. Appropriate when the hook is advisory or observational; inappropriate for security boundaries where blocking is the point.

### Fail-open with degraded-mode fallback

When a runtime dep is missing (e.g. `tiktoken`), the plugin falls back to a cruder approximation (chars/4 estimate) and writes a warning to stderr. Hook still exits 0. Constrains the report's accuracy but preserves liveness. Appropriate when graceful degradation is more useful than total absence.

### Postinstall failure suppression

`package.json` `postinstall` and `prepare` scripts wrap their commands with `|| true` (or `>/dev/null 2>&1 || true`). A crashed install-time banner or hooks-installer never fails `npm install`. Constrains user-visible install reliability; means install-time bugs are hidden until the runtime fires. Appropriate as a courtesy to users; trade-off accepted by author.

### Silent-ignore graceful degradation

Older Claude Code versions silently ignore unknown hook event names, missing `userConfig`, etc. Plugins relying on the host's silent-ignore behavior have no machine-readable version floor — the runtime degrades to whatever subset the host supports. Constrains version-floor declaration to documentation only.

## Author identity and provenance drift

How owner / author metadata stays synchronized with reality.

### Owner-rename in flight

A repo migrates from one owner to another (e.g., personal user → organisation). Code commits and homepage URLs update first; `marketplace.json.owner.name`, plugin `author.name`, and similar identity fields lag. GitHub redirect makes both URLs resolve to the same repo, but a consumer reading `owner.name` alone gets the pre-rename identity. No standard validator catches the inconsistency. Constrains long-running plugins to a periodic identity audit; the cost of fixing is low but the surface is wide. Appropriate to flag as an axis specifically because no upstream mechanism prevents it.

### Plugin name vs repo name drift

Repo name (`token-reporter-plugin`) intentionally differs from plugin name (`token-reporter`). README warns users to install as `<plugin>@<marketplace>` to disambiguate. Constrains marketplace aggregators to track both names; users who type the repo name to install get nothing. Appropriate when the maintainer wants the repo namespace and the plugin namespace to be independent (e.g. multiple plugins in a shared repo or vice versa).

### Personal-email owner address

`owner.email` in marketplace.json is a personal Gmail rather than a role/group alias. Constrains the maintainer to handle marketplace-aggregator notifications personally; on owner rename or off-boarding, the email becomes stale.

## Categorization decisions for the merger

- **`disable-model-invocation` and `context: fork` placed under "Skill authoring conventions"** rather than under tool-use-enforcement, on the grounds that the mechanism is frontmatter-shaped rather than runtime-gating. The merger may want to consider whether high-blast-radius opt-out belongs alongside enforcement.
- **"Documented bypass mechanism"** placed under tool-use-enforcement rather than under governance, since the bypass directly modifies what hard-blocking does. Could equally live as a governance pattern.
- **"MCP Registry presence"** treated as its own role rather than folded into channel-distribution or marketplace-manifest-shape. Rationale: it is a distinct registry with its own schema and publish lifecycle, semantically more like a parallel discovery channel than a sub-form of marketplace presence.
- **"Author identity and provenance drift"** is borderline — could be folded into marketplace-manifest-shape or version-coordination. Left as its own role because the drift mechanics (owner rename, name-vs-name, email staleness) are observation-axes the corpus surfaces specifically and they don't quite fit a manifest-shape or version concern.
- **`tests_dev/` referenced but not in tree** — placed under "No test directory present" rather than treated as a separate "private tests" path; the visible artifact is the absence.

## Open questions

- Whether `context: fork` is a documented Claude Code frontmatter field or a methodology-specific extension Claude Code ignores. Affects whether it's a real role-filling choice or an idiomatic projection.
- Whether `images: [url]` on a marketplace plugin entry is consumed by any UI surface. Affects whether it's a real distribution channel or dead metadata.
- Whether the bin-feature version floor (`v2.1.91+`) declared only in prose has any host-side enforcement (e.g., does Claude Code refuse to register a `bin/` directory on older versions, or just silently ignore it). Affects the boundary between "graceful degradation" and "silent failure."
- Whether the disabled-by-default fixture-smoke workflow's two-hand activation gate (`if: false` + missing secret) is itself a pattern other repos exercise, or unique to this corpus. Bin-3/4 may have similar shapes.

## Notable corpus observations

- **All three samples treat version sync as a multi-file problem.** Even the smallest sample (token-reporter-plugin) carries `plugin.json` + `pyproject.toml` as parallel sync sites; idea-to-deploy lists 5+ sync sites; ThumbGate generalizes to ~15 via `sync-version.js`. The role "version coordination" is unavoidable once a plugin has a release script.
- **All three avoid registering hooks via `plugin.json`'s `hooks` field.** token-reporter uses `hooks/hooks.json` (conventional discovery); idea-to-deploy uses out-of-band sync via `scripts/sync-to-active.sh` and a `/adopt` template; ThumbGate's hooks live in dogfood `.claude/settings.json` rather than the plugin tree. None use the manifest's `hooks` declaration. Possibly a generation-gap signal — the field may exist but not be the mainstream choice.
- **Each sample has a distinct CI center of gravity.** token-reporter: pre-push + local release script (cloud is webhook-only). idea-to-deploy: cloud meta-rubric + disabled fixture-smoke. ThumbGate: 30+ workflows including autonomous-ops and post-publish runtime smoke. The roles "test discipline" and "CI workflows" branch deeply across the bin.
- **All three define their own bypass / escape-hatch idiom.** token-reporter: `claude --debug` ancestry detection (no debug, no output). idea-to-deploy: `.methodology-self-extend-override` file. ThumbGate: `THUMBGATE_HOOKS_ENFORCE=1` env-var as the toggle. Suggests a corpus-wide pattern of opt-in enforcement rather than always-on.
- **The "shipping gap" between repo content and `/plugin install` payload** appears in two of the three samples. idea-to-deploy: hooks shipped to the repo but require `scripts/sync-to-active.sh` or `/adopt` to activate. ThumbGate: `.claude/settings.json` is dogfood-only and `.claude-plugin/` doesn't carry hooks. Plugin-managed hook installation appears to be an unsolved problem the authors work around by hand.

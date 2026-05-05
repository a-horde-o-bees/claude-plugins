# Sample

Pass-1 Phase-1a partial for bin 10. Functional decomposition of `affaan-m--everything-claude-code.md`, `anthril--official-claude-plugins.md`, `anthropics--claude-plugins-community.md`, organized by role with implementation paths as sub-sections.

## Marketplace shape

The structural relationship between the marketplace manifest and the plugin payloads it advertises.

### Single-plugin self-hosting

A `.claude-plugin/marketplace.json` at repo root wraps the same repo as a single plugin via `source: "./"`. The marketplace and the plugin are the same artifact; the marketplace exists only to satisfy the install protocol. Appropriate when one large plugin is the entire deliverable and aggregator semantics aren't needed. Constrains versioning to a single track (no per-plugin tag namespaces), and any marketplace metadata becomes plugin-scoped by default.

### Multi-plugin owned-aggregator

A repo-root marketplace lists N plugins under `plugins/<name>/`, each with its own `.claude-plugin/plugin.json` and source tree. Every entry uses a relative source (`./plugins/<name>`); the owner authors all listed plugins. Appropriate when one team ships a coordinated catalog. Constrains release cadence (one repo, one tag stream) and creates per-entry vs per-plugin version-sync surface that needs custom validation.

### Pure external aggregator

The repo holds only `marketplace.json` + LICENSE + README + minimal CI; every plugin is sourced externally via `url` (full clone with `sha` pin) or `git-subdir` (path into an upstream monorepo). The repo authors zero plugin content — it's a denormalized index. Appropriate as a community directory or curated mirror. Constrains the field surface that survives the aggregator boundary (only `name`, `description`, `source`, `homepage`, occasional `category` are preserved); upstream `version`, `author`, `license`, `dependencies`, `tags`, `strict`, `skills` are dropped and resurface only after install.

## Per-plugin discoverability

How the marketplace surfaces a plugin to users browsing or searching the catalog before install.

### Triple-redundant tagging

Every plugin entry carries `category` + `tags` + `keywords`, with `tags` and `keywords` often byte-identical duplicates. The author either doesn't know they serve different purposes or is hedging across tooling that may read one and not the other. Appropriate when uncertain about the consumer's discoverability strategy; produces noise but maximizes match surface.

### Category-only with deep-link homepage

Each entry carries a single `category` enum value plus a `homepage` deep-linking to `/tree/main/plugins/<name>`. No `tags`, no `keywords`. Discoverability rests on category enum + name + description. Appropriate when the catalog is small enough that browsing-by-category beats keyword search, and when the author wants a controlled vocabulary.

### Description-only with sparse opt-in category

Only `description` is universal across entries; `category` appears on a small minority (≈3% in one mirror) with inconsistent capitalization (`development` vs `Developer Tools`). No tags, no keywords. Appropriate when the catalog is too large for any author-supplied taxonomy to stay coherent, but produces an uncontrolled vocabulary even among the opt-in subset.

## Plugin source binding

How a marketplace entry points at the plugin's actual source tree.

### Relative same-repo path

`source` is `"./"` or `"./plugins/<name>"`. The plugin lives in the same repo as the marketplace manifest. Appropriate for self-hosting and owned-aggregator shapes. Constrains the marketplace and plugin to one repo, one tag stream; every plugin moves on the marketplace's release cadence.

### `url` clone with `sha` pin

`source` is an object `{url, sha}` cloning an external repo at a specific commit. SHA pinning is universal in this path — pinning is the contract. Appropriate when aggregating external plugins; produces deterministic consumer state per marketplace snapshot. Constrains the aggregator to a sync workflow that updates SHAs on cadence.

### `git-subdir` into upstream

`source` is `{source: "git-subdir", url, path, ref}` reaching into a path inside an external monorepo. `url` is mixed in practice — bare `owner/repo` slug or full `https://` — and `ref` defaults to `main` (essentially opt-out pinning, in contrast to the universal SHA pinning of the `url` source). Appropriate when the plugin is one slice of a larger upstream repo. Constrains determinism: branch-floated entries move whenever upstream pushes.

## Version authority

Where the canonical version of a plugin lives when multiple manifests could carry it.

### `plugin.json` as sole source of truth

Marketplace entries omit `version`; only `plugin.json` carries it. CI scripts may still parse marketplace entries and warn if a `version` is missing — surfacing intent without enforcing it. Appropriate when the plugin payload owns its identity; the marketplace is a pointer. Constrains marketplace tooling that wants to display versions to traverse to the plugin tree.

### Marketplace-side pin via source ref

In aggregator marketplaces, `source.sha` (for `url`) or `source.ref` (for `git-subdir`) is the version contract. Upstream `plugin.json` versions are not surfaced. Appropriate when the marketplace cannot trust upstream version discipline. Constrains the user: the only pinning surface is the source ref the aggregator sets.

### Cross-ecosystem version sprawl

A release script enumerates many version-bearing files (one observed sample lists 17: `package.json`, `package-lock.json`, multiple `AGENTS.md` locale variants, `agent.yaml`, `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, sibling-ecosystem manifests for Codex/OpenCode/Cursor/Gemini, README locales, architecture docs) that must move atomically. Appropriate when distributing the same plugin across multiple AI-harness ecosystems. Constrains release engineering: adding a new version-bearing manifest requires editing the script; CI tag-verification typically only checks one file, so drift between the others isn't caught.

## Channel distribution

How a marketplace stages dev versus released states for downstream consumers.

### No channel split, tag-on-main

Users pin via git ref against `main`; tagged commits are the "stable" signal, untagged main is dev-quality. No `stable-*`/`latest-*` marketplace twins, no release branches. Appropriate when the audience tolerates riding main; simpler mental model. Constrains: every commit on main is effectively a release candidate for `@main` consumers.

### Sync-PR cadence with no tags

The mirror has zero tags; "release" is implicit in each merged sync PR. Sync branches (`sync/manual-YYYY-MM-DD`, `sync/auto-vendor`) merge into main on a weekly batch cadence. Appropriate for pure aggregators backed by an internal review pipeline. Constrains consumers: the only stable handle is a marketplace-repo commit SHA, which the standard install command doesn't capture by default.

## Version control and release cadence

How the repo manages its own tagging and branching for releases.

### Tag-on-main, no release branches

Tags `vX.Y.Z` cut directly on main, no `release/*` or `v*` legacy branches. Pre-release suffixes absent in observed samples. Appropriate for linear release histories. Constrains rollback: bug fixes ship by cutting a new tag from main, not by maintaining release branches.

### Single lifetime tag with drift

A single `v1.0.0` tag exists at marketplace creation; per-plugin `plugin.json` versions advance (e.g., `1.0.1`, `1.1.0`) without follow-up tags. CHANGELOG.md and README also drift from live state. Appropriate (operationally) when no automation forces tag-version correspondence — but a clear anti-pattern: users pinning the only tag get stale plugins indefinitely.

### Untagged sync-only

Zero tags ever; the entire release surface is the sync-PR merge stream. Appropriate for read-only mirrors of an upstream pipeline. Constrains: no pin handle other than commit SHA.

## Plugin-component registration

How `plugin.json` declares the plugin's components (skills, commands, agents, hooks, MCP).

### Explicit file-path arrays for agents, directory references for skills/commands

`agents` is an enumerated list of `./agents/<name>.md` paths (per-file); `skills` and `commands` use directory references like `["./skills/"]`. The asymmetry tracks an observed validator restriction (`agents: Invalid input` when a directory is passed) that does not apply equally to skills and commands. Appropriate when validator behavior is asymmetric; produces verbose `agents` blocks that grow with the agent count.

### Minimal manifest with default discovery

`plugin.json` carries only `name`, `version`, `description`, `author` and omits all component path declarations. Components are discovered from convention paths (`skills/`, `hooks/hooks.json`, `.mcp.json`). Appropriate when the convention paths are stable and the author trusts default discovery. Constrains: any documentation or test asserting required component fields will fail against the live manifest if not co-evolved.

### Hooks and MCP outside `plugin.json`

`hooks/hooks.json` and `.mcp.json` sit at known paths and are loaded by the install flow without an explicit `plugin.json` reference. Appropriate when the runtime contract is "well-known filename at well-known path." Constrains alternative locations: the path is fixed, not configurable.

## Agent definition format

How agent components declare their identity, model, and permitted tools.

### Frontmatter with model + JSON-array tools

Frontmatter fields `name`, `description`, `tools` (JSON array of plain tool names like `["Read", "Grep", "Glob", "Bash"]`), `model` (e.g., `opus`, `sonnet`). No permission-rule syntax (no `Bash(uv run *)` style). Appropriate for tool-allowlist semantics where any invocation of the named tool is acceptable.

### Frontmatter with space-separated tools and `effort` field

Frontmatter uses space-separated tool names (`tools: Read Grep Bash`), plus a non-standard `effort: max` field, alongside `model`. Appropriate when targeting a specific harness convention; produces ambiguity for parsers that expect YAML-list syntax.

## Skill-to-agent dispatch

How a skill hands execution to a sub-agent.

### Frontmatter `context: fork` + `agent: <name>`

A SKILL.md frontmatter declares `context: fork` and `agent: campaign-auditor` to drop into an isolated sub-agent context. The named agent file lives alongside `skills/` in `agents/<name>.md`. Appropriate when the skill's work warrants a clean context with restricted tools. Constrains skill author: the agent must exist as a sibling component in the plugin.

## Dependency installation

How the plugin provisions runtime dependencies on the user's machine.

### Repo-local Node install via shell wrapper

`install.sh` (POSIX) and `install.ps1` (Windows) at repo root run `npm install --no-audit --no-fund` into a repo-local `node_modules`, then delegate to a Node-based real installer (`scripts/install-apply.js`). Existence-only change detection (`if [ ! -d node_modules ]`); no checksum stamping. Appropriate when the plugin predates the Claude Code plugin spec and needed its own user-facing install entry. Constrains: marketplace-flow installs bypass `install.sh` entirely; the path's completeness via the plugin runtime is uncertain.

### SessionStart-driven Python venv with stamp file

A `SessionStart` hook (`ensure-venv.sh` / `ensure-venv.ps1`, ~180s timeout) creates a Python venv under `${CLAUDE_PLUGIN_DATA}/venv/`, runs `pip install -r requirements.txt`, then on success copies `requirements.txt` to `requirements.stamp`. Next session, `diff -q requirements.txt requirements.stamp` skips re-install when unchanged. On failure, the script emits `{"systemMessage": ...}` JSON with `exit 0` (never block); pip stderr redirects to `install.log`. The stamp-write-after-success structure is the retry invariant: failures leave the stamp absent or stale, so the next session retries the diff path. Appropriate for plugins with Python runtime deps that should converge across sessions without blocking. Constrains: no Python minor-version stamping (a user upgrading Python keeps the old venv); `install.log` doesn't rotate.

### No deps (pure manifest aggregator)

Repo ships only `marketplace.json` + LICENSE + README + a single CI workflow; nothing to install. Appropriate for pure aggregators.

## Bin-wrapped CLI distribution

How a plugin exposes runtime entry points (typically MCP servers) that need a specific interpreter.

### Pointer-file shim invoked via `.mcp.json`

A `bin/python_shim.sh` (POSIX) + `bin/python_shim.ps1` (Windows) reads `${CLAUDE_PLUGIN_DATA}/python_path.txt` (written by the venv-bootstrap SessionStart hook), validates the path is executable, and `exec "$PY" "$@"` to run the requested server script. `.mcp.json` invokes via `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh <server.py>`. Appropriate when the venv interpreter path is OS-dependent and unknown until first session; decouples MCP registration from path encoding. Constrains: if the venv hook has never succeeded, `python_path.txt` is missing and the shim exits 127 with a corrective message; recovery requires the user to install the prerequisite (Python 3.11+) and restart Claude Code. The PowerShell sibling exists but `.mcp.json` only references the `.sh`, leaving Windows users dependent on Git Bash or WSL — Windows support is plumbed in the shim file but not in the registration.

### No bin (hooks-only runtime)

The plugin has no `bin/` directory; all user-facing entry points are slash commands (`commands/`) or skills, plus hook-driven side effects. Appropriate when runtime behavior is fully hook-mediated. Constrains: no direct executable surface for the user to run outside the agent loop.

## User configuration

How a plugin declares values the user must supply (API keys, secrets, preferences).

### Absent (relies on process env vars)

Neither `plugin.json` nor `marketplace.json` declares `userConfig`. Hooks and runtime read `CLAUDE_PLUGIN_*` and other process env vars directly. Appropriate when the audience is technical enough to set env vars from documentation. Constrains discoverability: a user who wants to toggle a feature must know the env var name from prose docs.

### Declared `userConfig` with `${user_config.KEY}` substitution and `CLAUDE_PLUGIN_OPTION_*` projection

`plugin.json` declares a `userConfig` block (8 fields in the observed sample), with `sensitive: true` on credential fields. `.mcp.json` references each value twice per server entry — once via `${user_config.KEY}` substitution into config strings and once as a `CLAUDE_PLUGIN_OPTION_KEY` env var the hook scripts read directly with `$CLAUDE_PLUGIN_OPTION_KEY`. Appropriate for credential-heavy plugins that need both injection forms (placeholder-substitution for config files, env-var for shell scripts). Constrains: if the `userConfig` block isn't actually shipped (observed defect: tests + docs assert it, live manifest omits it), every substitution resolves empty and the runtime starts with empty credentials.

## Tool-use enforcement

How `PreToolUse` / `PostToolUse` hooks gate or react to agent tool calls.

### Centralized inline-bootstrap dispatcher

Every hook command is ~1.5 KB of inline `node -e "..."` boilerplate that re-implements `CLAUDE_PLUGIN_ROOT` resolution across a fallback chain (env var → `~/.claude` direct → six well-known plugin slug paths → versioned cache dirs), then hands off to `plugin-hook-bootstrap.js` which calls `run-with-flags.js {event-id} {handler-script-path} {profile-flags}`. Hook IDs use a structured `{lifecycle}:{scope}:{purpose}` taxonomy (e.g., `pre:edit-write:gateguard-fact-force`). Profile gating (`standard`, `strict`) lets users opt in or out of disciplines. Appropriate for plugins with many hooks and uncertainty about how reliably the host sets `CLAUDE_PLUGIN_ROOT`. Constrains: SessionStart specifically had to be extracted to a standalone file because inline `!` characters trigger bash history expansion and produce a visible CLI error header; the inline pattern is fragile across shell environments.

### Per-hook bash scripts with selective strict mode

Each hook is a small `.sh` script invoked directly from `hooks.json`. `set -euo pipefail` is used on hooks that need fail-fast (e.g., pre-write content validation); other hooks run without strict mode and rely on `exit 0` to fail-open. `{"systemMessage": "..."}` JSON on stdout for non-blocking advice; stderr + `exit 2` for hard blocks. Appropriate when hook count is small and per-hook concerns are simple. Constrains: no centralized fallback for env-var resolution; per-hook copies of common boilerplate accumulate over time.

### Fact-forcing first-edit gate

A `pre:edit-write:gateguard-fact-force` hook blocks the first `Edit`/`Write`/`MultiEdit` per file and demands the agent investigate (importers, schemas, prior context) before allowing. Appropriate for workflow-discipline plugins targeting agent research quality.

## Session context loading

How a plugin injects context at session boundaries.

### SessionStart with welcome banner via `systemMessage`

A `welcome.sh` runs on every SessionStart sub-event (no matcher restriction) and emits `{"systemMessage": ...}` JSON with skill counts, line-count warnings, or other lint-in-banner output. Appropriate for surfacing repo-state diagnostics to the user at session boundaries. Constrains: with no matcher, welcome banners re-emit on every `clear` and `compact`, polluting mid-session context.

### SessionStart for runtime provisioning

SessionStart drives venv ensure + credential check, not user-facing context. Output is `systemMessage` JSON only on failure or status changes. Appropriate when the plugin needs setup work but no banner. Constrains: SessionStart timeout (e.g., 180s for venv) gates session readiness — long first-session installs delay the user.

### SessionStart with structured handler in standalone file

A SessionStart bootstrap (`session-start-bootstrap.js`) was specifically extracted to a standalone file (separate from inline `node -e` patterns used by other hooks) because inline `!` characters in fallback logic triggered bash history expansion in the inline pattern. Appropriate for SessionStart specifically; the extraction-to-file pattern resolves a real shell-environment fragility.

## Notification surface

How the plugin reaches the user outside the agent's text channel.

### Stop-hook driven desktop notification

A `Stop` hook runs `desktop-notify.js` after Stop events to fire macOS desktop notifications. Implemented at the hook layer rather than via a dedicated `monitors.json`. Appropriate when the plugin needs notifications but `monitors.json` isn't yet broadly adopted in the runtime. Constrains: notification delivery is OS-specific to whatever the script targets; multi-OS support requires per-OS handlers.

### `monitors.json` (not used in observed samples)

The dedicated monitor surface is absent in all three samples; even mature plugins implement notification-like behavior via Stop hooks rather than monitors.

## Plugin-to-plugin dependencies

How a plugin declares it requires other plugins.

### Absent

`dependencies` field absent from every entry across all three samples. No `{plugin-name}--v{version}` tag format observed. Appropriate when each plugin is structurally self-contained. Constrains: any cross-plugin contract (skill-chain DAGs in one observed sample) is enforced only by intra-plugin convention, not the runtime.

## Test stack

What test framework runs against the plugin and what it covers.

### Mixed `node:test` + pytest with custom runner

Primary tests use `node:test` via `tests/**/*.test.js`, executed by a custom `tests/run-all.js` that `spawnSync`s each file and aggregates pass/fail in an ASCII box. Python tests (pytest + pytest-asyncio + pytest-cov + pytest-mock) cover a Python sub-package via `pyproject.toml`'s `[project.optional-dependencies] dev`. Appropriate when the plugin spans Node and Python; produces robust coverage but requires the custom runner to coordinate. Constrains: in the observed sample, the custom runner only invokes Node tests — pytest is configured but orphaned from CI.

### Pytest within plugin tree

`plugins/<plugin>/tests/{unit,integration,lint}/` with `conftest.py` doing sys.path shimming. No `pyproject.toml` or `pytest.ini`; the Makefile + conftest are the config. Appropriate when only one plugin in an aggregator has runtime code. Constrains: tests assume invocation via the plugin's own Makefile, not a top-level runner.

### No tests

Pure aggregator marketplaces ship no test code. Appropriate when there's no plugin payload to verify locally; all validation is at the aggregator boundary (manifest parse + version sync) or in the upstream review pipeline.

## CI pipeline

How automated workflows verify the repo on push and pull request.

### Multi-job matrix with parallel test/validate/security/lint

`ci.yml` defines four parallel jobs — `test` (matrix-runs), `validate` (multi-validator chain), `security` (npm audit), `lint` (ESLint + markdownlint). Triggers: `push: [main]` + `pull_request: [main]`. Matrix is OS × Node × package-manager (e.g., `[ubuntu, windows, macos] × [18, 20, 22] × [npm, pnpm, yarn, bun]`, minus exclusions = ~33 lanes). `fail-fast: false`. Appropriate for plugins targeting wide cross-platform support. Constrains: matrix cost — minutes per lane × lane count = significant CI minutes per PR.

### Single-runner JSON validation only

One workflow (`validate-marketplace.yml`) runs on `ubuntu-latest`, Node 20, no matrix, performing only `node -e "JSON.parse(...)"` syntax checks on `marketplace.json` and each `plugin.json`, plus a custom version-sync script. Test suites (where they exist) are not invoked. Appropriate when the plugin payload is content-only (skills/agents) with no runtime to test. Constrains: defects in the payload (manifest fields the docs/tests describe but the live file omits) ship to consumers because no test job catches them.

### Single PR-gatekeeper workflow

The only workflow is `close-external-prs.yml` triggered on `pull_request_target` opened/reopened. Uses `actions/github-script` to check the PR author's collaborator permission; if not `admin`/`write`, posts a canned redirect comment and closes the PR. No manifest validation, no tests. Appropriate for read-only mirrors with explicit anti-contribution posture. Constrains: zero protection against malformed sync-PR merges; a stale `source` entry with a missing directory was observed live.

## Action pinning discipline

How CI workflows pin third-party GitHub Actions.

### SHA-pinned with version comment

Every action pinned by 40-char SHA with a `# vX.Y.Z` trailing comment (e.g., `actions/checkout@de0fac2e... # v6.0.2`). Appropriate when supply-chain risk is taken seriously and the workflow surface is large. Constrains: pin updates require re-fetching the SHA at every version bump; tooling like Dependabot can automate.

### Tag-pinned to major

Major-tag pins (`actions/checkout@v4`, `actions/setup-node@v4`, third-party `@v1`). Appropriate for low-blast-radius workflows or when the supply-chain threat model accepts tag mutation risk. Constrains: a compromised tag could inject code; mitigations rest on the action publisher.

## Release automation

How tagged releases produce artifacts (GitHub Releases, npm packages, marketplace updates).

### Tag-triggered release with multi-gate sanity

`release.yml` triggers on `push: tags: ['v*']`, runs three gates — tag format regex (`^v[0-9]+\.[0-9]+\.[0-9]+$`, no pre-release), tag-equals-package.json-version comparison, and a manifest-sync test (`plugin-manifest.test.js`) — then conditionally `npm publish --access public --provenance`, then creates a GitHub Release via `softprops/action-gh-release` with `body_path: release_body.md` (a heredoc'd template) plus `generate_release_notes: true`. Idempotency: `npm view ${NAME}@${VERSION}` gates the publish step. Appropriate for npm-published plugins with strong release-engineering needs. Constrains: the templated release body adds little over auto-generated notes (anti-pattern signal); cross-manifest version sync is only verified for one of the many version-bearing files.

### Sponsor automation as scheduled workflow

A `sponsors.yml` runs daily (`schedule: "0 6 * * *"`) plus `workflow_dispatch`, calling `JamesIves/github-sponsors-readme-action` six times (one per pledge tier) to sync `SPONSORS.md` and `README.md`. Appropriate for community-funded projects. Constrains: in the observed sample, the action targets `branch: master` while the default branch is `main` — a config drift that would fail on first run.

### No release automation

Releases happen by manually cutting a tag (or never, in pure aggregators); no workflow consumes tags. Appropriate for projects where the team accepts manual cadence. Constrains: nothing enforces tag-version correspondence; observed live drift between sole tag and current `plugin.json` versions.

## Marketplace validation

What runs to ensure the marketplace manifest and plugin payloads are well-formed.

### Multi-validator composition

A `validate` CI job runs many discrete validators in sequence with `continue-on-error: false` — each validator targets one component type or concern: `validate-agents.js`, `validate-hooks.js`, `validate-commands.js`, `validate-skills.js`, `validate-install-manifests.js` (cross-ecosystem manifest sync), `validate-workflow-security.js` (GitHub Actions hygiene — SHA-pinning, minimal permissions), `validate-rules.js`, `catalog.js --text`, `check-unicode-safety.js` (invisible-unicode / zero-width injection block, an AI-agent prompt-injection vector). Appropriate when the plugin surface is large and concerns separate cleanly. Constrains: each validator is its own script to maintain.

### JSON-parse plus version-sync only

`node -e "JSON.parse(...)"` against `marketplace.json` and each `plugin.json`, plus a `check-versions.mjs` script that compares marketplace-entry `version` against `plugin.json` version. Frontmatter validation, hooks.json validation absent. Appropriate when the plugin payload is content with simple structural needs. Constrains: defects in non-validated files (frontmatter formats, hooks shapes) ship.

### No validation

Pure-aggregator workflow does no manifest parsing; relies on an internal review pipeline (private to the marketplace owner) to gate entries before merge. Appropriate when the merge gate is upstream and trusted. Constrains: public-facing repo has no recovery if the upstream gate misses something — observed: a stale `./<plugin-name>` source entry with no matching directory shipped to consumers.

### Reverse-engineered validator notes as primary-source artifact

A `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` document captures undocumented plugin-validator constraints (e.g., `version` is mandatory; `agents`/`commands`/`skills`/`hooks` must be arrays not strings; `agents` MUST be explicit file paths, directory paths reject with `"agents: Invalid input"`) written from observed install failures. Appropriate when the plugin runtime's validator behavior isn't documented elsewhere; the artifact accumulates real-world failure-mode evidence.

## Documentation surface

What docs the repo carries to orient consumers, contributors, and agents.

### Multi-document agent-context layer

Repo root carries 14+ markdown files: `README.md` (multi-locale `docs/<locale>/`), `CHANGELOG.md`, `CLAUDE.md`, `AGENTS.md`, `RULES.md`, `SOUL.md`, `TROUBLESHOOTING.md`, `WORKING-CONTEXT.md`, `EVALUATION.md`, `REPO-ASSESSMENT.md`, `COMMANDS-QUICK-REF.md`, `SPONSORING.md`, `SPONSORS.md`, plus `the-longform-guide.md` / `the-shortform-guide.md` / `the-security-guide.md`. Multi-language READMEs for pt-BR, zh-CN, zh-TW, ja-JP, ko-KR, tr. Appropriate when the audience needs both marketing surface and rich agent-facing context. Constrains: locale README maintenance burden — observed release script bumps version in only two locales, so the others drift.

### Layered repo / plugin / skill READMEs (uneven)

Repo-root `README.md` describes the marketplace; a subset of plugins ship plugin-level `README.md` (4 of 10 in the observed sample), and skills ship per-skill SKILL.md. `architecture.md` exists at the plugin level for one plugin only (the runtime-heavy one); other structurally substantial plugins lack architecture docs. Appropriate as a target structure but unevenly executed. Constrains: nesting-discipline pattern breaks when intermediate layers are skipped.

### Minimal consumer-facing README only

A short `README.md` (~1.4 KB) explains the install commands and submission flow. No `CHANGELOG`, no `architecture.md`, no `CLAUDE.md`, no community health files. Appropriate for read-only mirrors with intentionally-routed contribution paths.

## License granularity

How licensing is expressed across the repo, plugins, and individual content units.

### Single repo-level license

`LICENSE` at repo root applies to everything. Appropriate for most projects.

### Layered: repo-MIT, plugin-MIT, per-skill-Apache-2.0

Plugin code is MIT, but per-skill content is Apache 2.0 under `skills/<name>/LICENSE.txt`. Granular license delineation inside a plugin. Appropriate when content licensing differs from code licensing (Apache for shareable prompt content, MIT for tooling). Constrains: every skill must ship its own LICENSE.txt; mixed licensing requires consumer awareness.

## Locale and content-style enforcement

How a project enforces written-content conventions beyond syntax.

### Australian English mandate with lint check

`CLAUDE.md` and per-plugin tests prescribe Australian English (`colour`, `optimise`, `behaviour`, `organisation`) in narrative text, with a `tests/lint/test_australian_english.py` lint module enforcing the rule. Appropriate when the project has a defined audience locale and wants to keep the voice consistent. Constrains: contributors from other locales must adapt; lint mechanism (word-list grep, regex, AST?) shapes the false-positive rate.

## Distribution channels beyond the marketplace

Whether the same plugin payload is published through other channels.

### Dual-distribution: marketplace + npm

The same source ships as both a Claude Code plugin marketplace entry and an npm package (e.g., `ecc-universal`), with the npm `files:` list including the entire plugin payload. Users can `npm install -g <pkg>` or use the plugin marketplace. Appropriate when the audience overlaps with npm consumers. Constrains: every release must satisfy both packaging contracts (the npm publish gate is an additional release-time check).

### Cross-ecosystem multi-harness distribution

The same plugin payload also ships via parallel manifests for sibling AI harnesses (Codex, OpenCode, Cursor, Gemini), each with its own version-bearing file. The release script lists all of them as version-locked. Appropriate when the plugin is intentionally portable across harnesses. Constrains: cross-ecosystem manifest sync (validated by `validate-install-manifests.js` in one observed sample) becomes a CI concern; sibling-ecosystem changes ripple back into the Claude release.

## Contribution posture

How the repo invites or routes external contributions.

### Open contribution with health files

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` present; PRs welcomed and reviewed. Appropriate for community-driven projects.

### Anti-contribution with auto-close gatekeeper

`pull_request_target` workflow checks the PR author's collaborator permission via GitHub API; if not admin/write, posts a canned redirect comment to a submission portal and closes the PR with `pulls.update({state: 'closed'})`. No `CONTRIBUTING.md` to make the gate discoverable in GitHub's UI; the README carries the routing message. Appropriate for read-only mirrors with submissions accepted via a separate portal. Constrains: first-time visitors may not realize direct PRs are unwelcome until the auto-close fires; the `pull_request_target` trigger runs with repo-scoped secrets so the inline script must avoid checking out PR code (observed: it doesn't, so safe).

## Credential handling

How runtime secrets are stored and accessed.

### Encrypted vault file with passphrase env-var

A vault file on disk holds Fernet-encrypted credentials, with the passphrase supplied via `userConfig` env var (`CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE`); PBKDF2-HMAC-SHA256 with 100000 iterations derives the key. File-locking governs writes; in-memory cache per MCP-server-process. Appropriate for plugins juggling many third-party API tokens (e.g., Google Ads, Meta Ads). Constrains: passphrase loss = vault loss; `userConfig` field must actually ship in `plugin.json` (observed defect: tests assert the field, live manifest omits it, every secret resolves empty).

## Skill chaining

How a plugin guides the user through a sequence of skills.

### Stop-hook tail-grep next-skill suggestion

A `Stop` hook tails the last 200 lines of the transcript, matches the most recent skill invocation, and emits a `systemMessage` recommending the next skill in an intra-plugin DAG. Appropriate when the plugin's skills form an ordered workflow. Constrains: depends on a stable transcript-line format and accurate matching — observed inconsistency where one variant grepped the path string instead of file contents, so it never matched correctly.

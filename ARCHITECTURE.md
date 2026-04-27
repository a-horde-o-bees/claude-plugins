# Marketplace Architecture

Claude Code plugin marketplace packaging one released plugin with shared development infrastructure. Each plugin is an independent system with its own architecture; this document covers how they are packaged, developed, and delivered.

## Layers

```
Claude Code plugin runtime
    ↓ marketplace resolution
Marketplace manifest (.claude-plugin/marketplace.json)
    ↓ plugin source paths
Plugins (plugins/ocd/)
    ↓ own entry points, hooks, skills
Plugin internals (see per-plugin ARCHITECTURE.md)
```

## Plugins

| Plugin | Status | Purpose | Architecture |
|--------|--------|---------|-------------|
| [ocd](plugins/ocd/) | Pre-release (dev channel only) | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation | [ARCHITECTURE.md](plugins/ocd/ARCHITECTURE.md) |

Plugins are independent systems — each has its own manifest, hooks, skills, rules, and tests. Tagged releases live on `main`; no release branches.

Each plugin may register Claude Code hooks (PreToolUse, PostToolUse, SessionStart), MCP servers for persistent tooling (SQLite-backed, launched as subprocesses with per-server data directories under `.claude/<plugin>/`), and skills (discoverable by Claude Code at configured skill paths). The specific hooks, servers, and skills each plugin provides are documented in that plugin's own `ARCHITECTURE.md`.

## Marketplace

The marketplace manifest at `.claude-plugin/marketplace.json` registers the plugin with a source path relative to the repository root. Claude Code resolves this path when users install from the marketplace.

Distribution: users add the GitHub repository as a marketplace source, then install individual plugins. Each plugin installs to `~/.claude/plugins/` with its own lifecycle (init, status, update).

## Three-Document Model

Every system boundary in this project — the repository root, each plugin, each skill that carries agent procedures — maintains a consistent set of documents, each targeting one consumer perspective:

- **`README.md`** — user-facing. What the system does, how to install and use it. At the repository root, the README targets developers and contributors working on the marketplace; at plugin and subsystem boundaries, the README targets the end users of that component.
- **`ARCHITECTURE.md`** — developer-facing. Layers, components, relationships, and key implementation details. A parent `ARCHITECTURE.md` describes each subsystem's role in the overall composition and links to the subsystem's own `ARCHITECTURE.md` for internals, rather than re-explaining what belongs to the subsystem.
- **`CLAUDE.md`** or **`SKILL.md`** — agent-facing. Present only when the system has agent-facing procedures. Opens by directing the agent to read the sibling `ARCHITECTURE.md` before acting. Contains procedures, workflow rules, and tool invocation patterns; structural context is read from `ARCHITECTURE.md` rather than embedded inline.

Readers navigate from general to specific through the nesting chain. A parent document answers "how do these pieces fit together"; each subsystem's documents answer "how does this piece work internally." Neither layer re-explains content that belongs to the other.

## Governance Delivery

The project delivers three kinds of agent guidance, each loaded through a mechanism suited to its scope.

**Rules** live in `.claude/rules/` and load into every session automatically via Claude Code's built-in rule auto-loading. Rules encode project-wide behavioral guidance — the agent follows them regardless of which file it is touching. A rule file contains the guidance the agent should consult at every step.

**Conventions** live in `.claude/conventions/` and load on demand. A PreToolUse hook on Read, Edit, and Write calls the navigator's `governance_match` with the target file path and surfaces matching convention files as additional tool-call context. This keeps session context focused — an agent editing a Python file sees the Python convention, an agent editing a markdown file sees the markdown convention, and neither sees the other. A convention file contains the content standards its target file type must meet.

**Operational documents** — `CLAUDE.md` at system boundaries, `SKILL.md` inside skill packages — load when Claude Code discovers them. They carry the procedures the agent follows when performing work within the system they describe.

Rules govern how the agent behaves. Conventions govern what a file contains. Operational documents govern how operations are performed. Guidance that applies regardless of which file is touched belongs in a rule; guidance that applies only to a specific file type belongs in a convention; step-by-step procedures for a named operation belong in an operational document.

## System Dormancy

An uninitialized system must not influence agent behavior. A system whose infrastructure has not been deployed is dormant: its tools must be absent or non-functional, its rule contributions must not load, its hooks must stay silent, and its skills must route to setup rather than acting on missing state. Dormancy is the complement of Governance Delivery — the same surfaces that carry guidance when a system is ready must go quiet when it is not, so agents are never prescribed toward tools or procedures that cannot work.

Each agent-facing surface a system exposes has its own dormancy mechanism, matched to how that surface reaches the agent:

| Surface | Dormancy mechanism |
|---------|-------------------|
| Hook | Hook short-circuits to empty `additionalContext` when its data corpus is absent; the tool call proceeds without guidance rather than erroring |
| MCP server | Server starts but registers zero tools and emits a one-line instruction naming the setup skill; tool registration is gated on a startup readiness check |
| Skill | `SKILL.md` Route includes an explicit readiness check per dependency; routes to the setup skill on failure before any tool invocation |
| Rule contribution | Rule files that prescribe interaction with a specific system ship with that system's `_init.py`, not at plugin root; absent init means the rule is absent from the deployed corpus |

The discipline is consistent across plugins: a system can only influence agent behavior through surfaces that it has affirmatively deployed. Plugin-wide rules (those governing agent behavior regardless of which system is active) remain in the plugin's central rules folder; system-specific rules (those prescribing use of one system) belong with that system. A plugin adding a new system is responsible for routing each surface it exposes through the matching dormancy mechanism.

## Shared Infrastructure

### Plugin Framework

Each plugin's `systems/framework/` package is identical — a generic framework for environment resolution, plugin metadata, template deployment, output formatting, system and skill discovery, init/status orchestration, test suite discovery and dispatch, and per-plugin venv resolution. Propagated across plugins by a pre-commit hook. Contains no plugin-specific logic; each plugin's skill `_init.py` modules provide their own infrastructure.

### Template-Deployed Model

Templates live per-system in plugin source — project-wide rules in `plugins/<plugin>/systems/rules/templates/`, system-scoped rules in `plugins/<plugin>/systems/<system>/rules/`, conventions in `plugins/<plugin>/systems/conventions/templates/`, log templates in `plugins/<plugin>/systems/log/templates/<type>/`. Templates are the authoritative source. Deployed copies in `.claude/rules/` and `.claude/conventions/` are derived artifacts; they are tracked in git so the rectified state travels with the repo and every consumer (CI, fresh checkouts, new sessions) sees the same corpus. Log-type templates deploy alongside user log entries at project-root `logs/<type>/` — logs are project notes the agent curates, not Claude Code infrastructure, so they live outside the `.claude/` tree entirely. Each system's `_init.py` deploys its own templates; a guard hook blocks direct edits to deployed copies so changes only flow template → deployed. `scripts/auto_init.py` (the auto-init orchestrator) rectifies the full deployed tree at `/checkpoint` — force-runs every system's `init()`, prunes orphans in template-managed categories, backs up existing `.claude/**/*.db` files to `.claude/pre-sync/` and reconciles them against post-init schemas (match → restore data; mismatch → surface a migration flag), then runs `navigator scan` for every plugin that ships one. Governance metadata (`includes`, `excludes`, `governed_by`) lives in each file's YAML frontmatter; the governance library reconciles rules and conventions against disk state on every query, so entries stay current without an explicit registration step.

### Development Scripts

| Script | Purpose |
|--------|---------|
| `scripts/auto_init.py` | Auto-init orchestrator — rectifies deployed state against current templates, called by `/checkpoint` |
| `scripts/release.sh` | Release-cut automation — bumps `y`, resets `z = 0`, tags main, pushes |
| `scripts/validate-manifests.py` | Validate marketplace + plugin manifests; invoked by CI |

These are dev-only — maintainers' tooling, not shipped to plugin consumers.

### Testing

Project-level tests in `tests/`, per-plugin tests isolated by `tests/plugins/<plugin>/pyproject.toml` (`[tool.pytest.ini_options]`) with independent `pythonpath` settings. Each plugin's tests run in isolation matching production import paths. Tests are dev-only — maintainers' infrastructure, not shipped to plugin consumers.

Test orchestration lives at project root under `tools/testing/` and is invoked via `bin/project-run tests`. The runner discovers the project suite plus each `tests/plugins/<name>/` suite, resolves each suite's venv (project `.venv/` for project tests, per-plugin data-dir venvs for plugin tests), dispatches pytest per suite, and compiles a unified report. Unknown flags forward verbatim to pytest, so `bin/project-run tests --plugin ocd --run-agent` flows the agent flag through without a `--` separator. Tests at an arbitrary ref run via `bin/project-run sandbox-tests --ref <ref>`, which creates a detached sibling worktree, invokes the runner inside it, and removes the worktree on return.

### Project-level tooling

Operations tied to this repository's development infrastructure — test orchestration, one-time project setup — live under `tools/` at project root and are exposed through `bin/project-run`. They are deliberately outside every plugin directory so they are not copied into end-user plugin caches and do not impose project-local conventions on downstream consumers of the plugins.

- `tools/testing/` — test discovery, runner, venv resolution, detached-worktree wrapper.
- `tools/setup/` — git hookspath configuration. Installed plugins do not configure the downstream project's git; that decision is explicit per checkout.
- `bin/project-run` — bash entry point that resolves the project venv and dispatches to `tools/` modules.

## File Organization

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         — marketplace manifest registering plugins
├── .claude/
│   ├── rules/                   — deployed rule files (tracked; rectified by scripts/auto_init.py)
│   ├── conventions/             — deployed convention files (tracked; rectified by scripts/auto_init.py)
│   ├── skills/                  — project-local dev skills (checkpoint)
│   ├── hooks/                   — project-level pre-commit guards
│   ├── ocd/                     — ocd plugin project data (navigator db, needs-map db, enabled-systems.json)
│   └── settings.json            — project-level permission patterns
├── bin/
│   └── project-run              — project-level dispatcher into tools/ modules
├── tools/                       — project-level development tooling (testing orchestration, setup)
├── plugins/
│   └── ocd/                     — ocd plugin (own system, see plugins/ocd/ARCHITECTURE.md)
├── scripts/                     — shared development scripts (auto_init, release, manifest validator, test delegator)
├── tests/                       — project-level integration tests (dev-only)
├── logs/                        — project log entries (decisions, friction, problems, ideas)
└── research/                    — external research notes (dev-only)
```

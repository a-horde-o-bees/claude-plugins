# Marketplace Architecture

Claude Code skill source repository with hybrid distribution. Skills are the source-of-truth unit; plugins are thematic packaging bundles for marketplace install. Individual skills are also installable directly via `npx skills` without going through plugin install.

## Distribution model

Two parallel channels deliver the same source skills:

| Channel | Command | Lands at |
|---|---|---|
| **Marketplace plugin install** | `/plugin install <plugin>@a-horde-o-bees` | `~/.claude/plugins/marketplaces/.../plugins/<plugin>/skills/<skill>/` |
| **Individual skill install (npx)** | `npx skills add a-horde-o-bees/claude-plugins --skill <name> -g` | `~/.claude/skills/<name>/` (symlink) |

The marketplace channel preserves bundle install for users who want curated sets per domain. The npx channel covers individual skills and is the path this project uses for its own consumption (per `.claude/installed-skills.json`).

Both materialize from the same skill folders in `plugins/<plugin>/skills/<skill>/`. Plugin manifests in `.claude-plugin/marketplace.json` carve the source tree into packaging units.

## Plugins

Plugin layout completed its domain reorganization into thematic plugins (the canonical set is `.claude-plugin/marketplace.json`); see `logs/decision/plugin-compartmentalization.md` for the rationale. The table below is pre-reorganization and is stale — flagged for a fresh pass.

| Plugin | State | Domain |
|---|---|---|
| `ocd` | Retiring (split per Phase G) | Currently houses `git`, `rebuild`, `rules` skills |
| `skill-authoring` | Active | Authoring discipline — `skill-creator`, `skill-composer` |
| `composed-skills` | Retiring (bucket concept retired) | Composed skills move to their domain plugin; `composition.md` marks origin |
| `ocd-old` | Legacy substrate | Pre-refactor `systems/<sys>/` content; migrates out per Phase E |
| `git` *(planned)* | Phase G target | Version-control skills (`git`) |
| `discipline` *(planned)* | Phase G target | Always-on / discipline skills (`rebuild`, `rules`) |

Each plugin is an independent package: own manifest, hooks, skills, tests. Tagged releases live on `main`; no release branches.

## Three-document model

Every system boundary maintains:

- **`README.md`** — user-facing. What the system does, how to install and use it
- **`ARCHITECTURE.md`** — developer-facing. Layers, components, relationships, key implementation details. Parent docs describe each subsystem's role and link to its own ARCHITECTURE.md for internals
- **`CLAUDE.md`** or **`SKILL.md`** — agent-facing. Present only when the system has agent-facing procedures. Opens by directing the agent to read the sibling ARCHITECTURE.md before acting

Readers navigate from general to specific through the nesting chain. Neither layer re-explains content that belongs to the other.

## Governance delivery

The project delivers three kinds of agent guidance through three mechanisms suited to their scope.

**Rules** live in `<scope>/.claude/rules/dependencies/` (flat) and load into every session automatically. Project opts into specific rules via the `/rules install` verb. Rules encode project-wide behavioral guidance — followed regardless of which file is touched.

**Dependencies** live in `<scope>/.claude/dependencies/<name>.md` and load on demand via the dep-resolution convention. A skill's body lists deps using `[[name]]` wikilinks; the resolver finds the deployed file at session-fire time and auto-deploys from the skill-bundled seed if missing. Same root files support two access patterns:

1. **Skill-declared** — skill's workflow lists deps that auto-load when the skill fires
2. **Situational on-demand** — a planned skill (Phase H) lets the user call a convention into context for any task

**Operational documents** — `CLAUDE.md` at system boundaries, `SKILL.md` inside skill packages — load when Claude Code discovers them. They carry procedures the agent follows when performing work within the system they describe.

Rules govern how the agent behaves. Dependencies govern what a domain or file type requires. Operational documents govern how operations are performed.

## System dormancy

An uninitialized system must not influence agent behavior. A system whose infrastructure has not been deployed is dormant: its tools must be absent or non-functional, its rule contributions must not load, its hooks must stay silent, and its skills must route to setup rather than acting on missing state.

Each agent-facing surface a system exposes has its own dormancy mechanism, matched to how that surface reaches the agent:

| Surface | Dormancy mechanism |
|---|---|
| Hook | Hook short-circuits to empty `additionalContext` when its data corpus is absent; the tool call proceeds without guidance |
| MCP server | Server starts but registers zero tools and emits a one-line instruction naming the setup skill |
| Skill | `SKILL.md` includes a readiness check per dependency; routes to setup on failure before any tool invocation |
| Rule contribution | Rule files that prescribe interaction with a specific system ship with that system's `_init.py`, not at plugin root |

A system can only influence agent behavior through surfaces it has affirmatively deployed.

## Development scripts

| Script | Purpose |
|---|---|
| `scripts/validate-manifests.py` | Validate marketplace + plugin manifests; invoked by CI |

Release cuts are driven by `/git release <version>`. See `plugins/ocd/skills/git/_release.md` for the workflow definition.

## Testing

Project-level tests in `tests/`; per-plugin tests isolated by `tests/plugins/<plugin>/pyproject.toml` with independent `pythonpath` settings. Each plugin's tests run in isolation matching production import paths.

Test orchestration lives at project root under `tools/testing/` and is invoked via `bin/project-run tests`. The runner discovers the project suite plus each `tests/plugins/<name>/` suite, resolves each suite's venv (project `.venv/` for project tests, per-plugin data-dir venvs for plugin tests), dispatches pytest per suite, and compiles a unified report. Unknown flags forward verbatim to pytest.

Tests at an arbitrary ref run via `bin/project-run sandbox-tests --ref <ref>` — creates a detached sibling worktree, invokes the runner inside it, removes the worktree on return.

## Project-level tooling

Operations tied to this repository's development infrastructure — test orchestration, one-time project setup — live under `tools/` and are exposed through `bin/project-run`. They sit outside every plugin directory so they are not copied into end-user plugin caches.

- `tools/testing/` — test discovery, runner, venv resolution, detached-worktree wrapper
- `tools/setup/` — git hookspath configuration
- `bin/project-run` — bash entry point that resolves the project venv and dispatches to `tools/` modules

## File organization

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         — marketplace manifest registering plugins
├── .claude/
│   ├── rules/dependencies/      — deployed always-on rule files (flat)
│   ├── dependencies/            — deployed situational-load dependency files
│   ├── skills/checkpoint/       — project-scoped skills (orchestrators)
│   ├── installed-skills.json    — per-user manifest of npx-installed skills (gitignored)
│   └── settings.json            — project-level permission patterns
├── bin/
│   └── project-run              — project-level dispatcher into tools/ modules
├── tools/                       — project-level development tooling
├── plugins/                     — domain-organized plugin packages
│   ├── ocd/                     — retiring per Phase G
│   ├── ocd-old/                 — legacy substrate (Phase E migrates content out)
│   ├── skill-authoring/         — skill authoring discipline plugin
│   └── composed-skills/         — retiring per Phase G
├── shared/                      — cross-skill canonicals (deps, scripts)
│   ├── _dependencies/           — source canonicals for rule/dep content
│   └── scripts/                 — source canonicals for cross-skill scripts
├── scripts/                     — shared development scripts (manifest validator)
├── tests/                       — project-level integration tests
├── logs/                        — project log entries (decisions, friction, problems, ideas)
└── research/                    — external research notes
```

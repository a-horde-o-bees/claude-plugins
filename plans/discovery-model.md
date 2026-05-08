# Plugin context architecture refactor

The two-mechanism architecture for plugin context delivery: discovery substrate for pure-markdown content (rules, conventions, dependencies) plus shim model for systems with code (skills, workflows, working files). Replaces the broken `includes`/`excludes` path-glob mechanism for content; replaces always-on plugin-skill auto-discovery for systems.

## Goal

Reduce always-on context cost while preserving trigger-strength of guidance. Every plugin contribution is invisible until needed; only relevant content loads, and only the slice the moment requires. Plugin upgrades flow through transparently for system code; reference content updates explicitly via `setup sync`. Plugins coexist without coordination beyond shared mechanical contracts; users extend with their own content using the same contracts.

The motivating data: the `Memory-filling rules auto-load even when irrelevant to project domain` problem log measured ~26.6K tokens of OCD rule overhead in a non-plugin project. Realistic target with both mechanisms: ~67% reduction in always-on cost — substrate trigger router (~1.5K) + skill metadata for installed systems (~2K for 10 systems) + system-bundled rules (~5K) ≈ 8.5K, vs original ~26K. Bigger savings on projects that install fewer systems.

## Output

### Discovery substrate (intent → action routing)

At every install scope:

- `<scope>/.claude/rules/<plugin>/<system>/triggers.md` — per-system routing file. Always-on. Triggers section maps rich-prose trigger phrases to targets (content references for conventions; skill invocations with verb-and-args for systems). For conventions, an indexed purposes section follows the triggers — purpose statements pulled from each opted-in convention's H1 + first paragraph.
- `<scope>/.claude/conventions/<plugin>/<name>.md` — convention bodies. Lazy-loaded when a routing file's purpose entry convinces the agent. Content copied to scope at install; stable scope path; sync rewrites in place on plugin upgrade.
- `<scope>/.claude/dependencies/<name>.md` — single canonical copy of shared content loaded by sources via `requires:` frontmatter. Apt-style: refcounted, content-hashed, conflict-fails.
- `<scope>/.claude/dependencies/_manifest.md` — bookkeeping. Records `{content_hash, used_by}` per dependency. Not auto-loaded.

In plugin source tree:

- `plugins/<plugin>/systems/<system>/triggers.md` — source template (for static handlers) or generator inputs (for dynamic handlers like conventions). Each system's handler decides shape.
- `plugins/<plugin>/dependencies/<name>.md` — bundled dependency content (plugin-level, mirrors deployed flat layout)
- Source files declare `requires:` in YAML frontmatter for any dependency they need

Per-system handler model:

- Most systems' handlers deploy a static `triggers.md` template — triggers table mapping moment prose to skill invocations
- Conventions' handler is dynamic — reads the user's opted-in conventions, extracts purpose statements (H1 + first paragraph) from each, generates the file with both triggers and indexed purposes sections
- Setup install calls each system's handler; setup uninstall is `rm` of the deployed file
- No central merge logic; each system owns its routing file's shape

### Shim model (systems)

At every install scope:

- `<scope>/.claude/skills/<plugin>-<system>/SKILL.md` — thin shim. Frontmatter (description, allowed-tools) copied from cache at install time. Body: a single `Call: !`<plugin>-path <system>`` line.
- The shim invokes Claude Code's user/project skill loading; preprocessing resolves the cache CLAUDE.md path; agent reads the file at the resolved path.

In plugin source tree:

- `plugins/<plugin>/systems/<system>/CLAUDE.md` — the agent-facing operational reference for the system. Loaded on shim invocation. Authoring discipline: dispatches via `<plugin>-run`; embedded `!`...`` blocks must avoid `$` expansions and must succeed (exit 0). See `logs/decision/shim-model.md`.

### Bin layer

In plugin source tree:

- `plugins/<plugin>/bin/<plugin>-run` — existing dispatcher; gains self-update mechanism (manifest diff → run install_deps.sh → exec). See `logs/decision/ocd-run-self-update.md`.
- `plugins/<plugin>/bin/<plugin>-path` — new thin wrapper returning the absolute path to a system's CLAUDE.md in current cache. Used by shim preprocessing.

### Plugin manifest

`plugin.json` declares only `setup` as a plugin-skill. All other systems' SKILL.md files in the source tree are NOT exposed via plugin-skill discovery; they're cached and reachable through `<plugin>-path` after `setup install`.

### State location convention

Plugin-managed state location follows access pattern (see `logs/decision/state-location.md`):

- Bin-mediated state (DBs, indices) → `~/.claude/plugins/data/<plugin>-<author>/projects/<sha-of-project-path>/`
- User-edited artifacts → project tree, outside `.claude/`
- Claude Code-read files → `<scope>/.claude/...`

## Phases

### Phase A — Decisions and plan (this commit)

Captured in:

- `plans/discovery-model.md` (this file)
- `logs/decision/discovery-model.md` — substrate + apt-style dependency versioning
- `logs/decision/shim-model.md` — two-mechanism architecture, shim shape, empirical preprocessing constraints, plugin-skill vs user-skill split
- `logs/decision/ocd-run-self-update.md` — manifest-diff self-update mechanism
- `logs/decision/state-location.md` — bin-mediated vs agent-touched state convention

> The user committed to revisiting these decisions after the refactor lands and the implementation is fully documented — to validate against final shape and slim down. Treat the current text as comprehensive scaffolding, not final form.

### Phase B — Bin layer

> Foundational infrastructure both mechanisms depend on. Lands before any system migration.

1. **Add `<plugin>-path` bin** — `plugins/ocd/bin/ocd-path`. Bash script that walks ancestors from `__file__` for the `.claude-plugin/plugin.json` marker, appends `systems/<system>/CLAUDE.md`, prints to stdout.
2. **Add self-update to `ocd-run`** — manifest-diff before exec; `flock` to serialize concurrent invocations; `install_deps.sh` runs synchronously when drift detected.
3. **Test bin layer from a user-skill** — quick verification that `ocd-path` and `ocd-run` resolve and dispatch correctly under user-skill preprocessing.

### Phase C — Substrate mechanics

> Per-system handler infrastructure for the discovery substrate. Built before migrating rules.

1. **Per-system handler protocol** — each system's facade exposes `install_triggers(scope, args)` (or equivalent), responsible for producing and writing its `triggers.md` to `<scope>/.claude/rules/<plugin>/<system>/triggers.md`. Conventions implements a dynamic handler; other systems will start with static-template handlers when they migrate.
2. **Dependency layer** — apt-style install/uninstall against `<scope>/.claude/dependencies/`. Hash + refcount tracking in `_manifest.md`. Setup install scans system sources for `requires:` declarations and dispatches dependency operations.
3. **Convention content deployment** — copy convention bodies from `plugins/<plugin>/systems/conventions/templates/` (or wherever the source layout lands) to `<scope>/.claude/conventions/<plugin>/<name>.md`.
4. **Tests** — substrate operations are deterministic; cover idempotency, refcount semantics, hash-conflict-fails, per-system handler dispatch, sync as install + diff.

### Phase D — Shim mechanics

> Python facade for the shim model (system delivery). Built before migrating transcripts.

1. **Shim install** — read cached SKILL.md frontmatter, copy `description` + `allowed-tools` into deployed shim at `<scope>/.claude/skills/<plugin>-<system>/SKILL.md`, write the `Call: !`<plugin>-path <system>`` body.
2. **Shim uninstall** — remove the deployed shim file and parent dir if empty.
3. **Shim sync** — refresh frontmatter from cache (description/allowed-tools may have changed); body never changes.
4. **Tests** — install is content-correct; sync detects frontmatter drift; uninstall is clean.

### Phase E — Migrate rules and conventions through substrate (test surface 1)

> First real surface for the substrate. Rules deploy as full content copies (unchanged from today). Conventions migrate to substrate-routed via the discovery layer with the dynamic triggers.md handler.

1. **Move 5 candidate-conventions** from `rules/templates/` to `conventions/templates/`: `markdown`, `principle-not-symptom`, `trigger-specificity`, `tool-positioning`, `agent-first-interfaces`. These fail the cognitive-trigger test (artifact-triggered, not cognitive).
2. **Author per-convention trigger prose** — each convention source declares the cognitive-moment prose its triggers row should carry. Stored alongside source content (frontmatter or co-located markdown).
3. **Implement the conventions handler** — dynamic `install_triggers(scope, args)` that reads opted-in conventions, extracts purposes, generates `<scope>/.claude/rules/<plugin>/conventions/triggers.md` with triggers + indexed purposes sections.
4. **Migrate rules system** — rules continue to deploy as content copies (unchanged); setup install simply layers the substrate machinery on top so the conventions system can use it.
5. **Update `plugin.json`** — drop systems other than `setup` from the skills field. Validate that bin/ still on PATH for user-skill preprocessing.
6. **Verify end-to-end** — fresh install reproduces current behavior; conventions load their bodies via the substrate's purposes-section indirection.

### Phase F — Migrate transcripts system through shim model (test surface 2)

> First real surface for the shim model. Transcripts has Python code, MCP server, working DB — exercises everything the shim model needs to handle.

1. **Migrate transcripts DB to plugin data dir** — `~/.claude/plugins/data/ocd-a-horde-o-bees/projects/<hash>/transcripts.db`. Update Python code to compute the project-keyed path.
2. **Author the transcripts system's CLAUDE.md** — agent-facing operational reference, dispatched via `Call:` from the shim.
3. **Author transcripts' static triggers template** — `plugins/ocd/systems/transcripts/triggers.md` listing the cognitive moments that route to `/ocd-transcripts <verb>` invocations.
4. **Implement transcripts handler** — static `install_triggers` handler that deploys the template to `<scope>/.claude/rules/<plugin>/transcripts/triggers.md`.
5. **Deploy shim and triggers** — `setup install transcripts --scope <scope>` writes both the shim at `<scope>/.claude/skills/ocd-transcripts/SKILL.md` and the triggers file. Setup uninstall removes both.
6. **Verify end-to-end** — `/ocd-transcripts` invocation loads the shim, calls into cache CLAUDE.md, dispatches via `ocd-run transcripts ...`, finds the venv, reaches the relocated DB. Substrate routes intent matching to the verb. Plugin upgrade transparent (next invocation gets new cache content).

### Phase G — Migrate remaining systems

> Each subsequent system is its own focused pass with its own design considerations. Tracked under `system-migrations` in TASKS.md, gated on phases A–F landing.

Pending migrations: log, navigator, pdf, check, git, retrospective, refactor, sandbox, needs_map, setup itself (review post-refactor — does setup stay plugin-skill or also become a shim?).

For each: substrate-deploy any rules/conventions the system contributes; shim-deploy the SKILL.md; migrate working files per state-location convention; document the system's CLAUDE.md.

### Phase H — Post-refactor decision review

> User-committed cleanup pass.

1. Review each `logs/decision/*.md` against final implementation
2. Validate decisions held; remove options-considered branches that are no longer relevant
3. Slim each decision log to essential rationale + final shape

## Open questions

- **Multi-plugin trigger coordination** — under per-system files, two plugins triggering on the same moment have separate rows in their respective files; agent sees both and decides. No merge mechanism. Open question: do we ever want explicit deduplication, and how would we coordinate? Defer until cross-plugin contention surfaces.
- **PFN's authoring-side cognitive trigger** — `requires:` handles parsing-side; authoring side may need a separate cognitive rule. Defer until concrete need surfaces.
- **Setup as shim vs plugin-skill** — currently planned plugin-skill (bootstrap entry point); revisit after Phase F.
- **System-bundled rule lifecycle vs substrate** — system-internal rules (e.g., navigator-usage) deploy as always-on memory at `<scope>/.claude/rules/<plugin>/<system>/`. The triggers.md file lives in that same directory. Question: should the system-internal rule and the triggers file be one file (folded together) or kept as separate files in the same directory? Defer until phase F surfaces concrete cases.

## State

Phase A in flight as of this commit. Decisions captured across four logs; plan revised to reflect expanded scope. Test surfaces selected: rules (substrate) and transcripts (shim model).

PFN already moved (`plugins/ocd/dependencies/process-flow-notation.md`) in earlier work — that change predates the shim model decision but doesn't conflict; PFN is a dependency, not a system.

Transition risk: the deployed `.claude/rules/ocd/process-flow-notation.md` survives but won't redeploy through `setup rules install` until Phase E lands. Avoid re-running rules install until then.

Doc rot scope: `plugins/ocd/README.md` and `plugins/ocd/ARCHITECTURE.md` still describe the old convention-gate hook and `includes`/`excludes` mechanism. Those docs get rewritten holistically when Phase E or F lands, not chip-by-chip.

Next pickup: Phase B (bin layer — `ocd-path` and `ocd-run` self-update).

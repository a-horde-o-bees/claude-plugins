---
log-role: reference
---

# Shim Model

Decisions governing the shim model — how plugin systems with code, workflows, and working files deploy to scope without copying the whole system. Complementary to the discovery substrate (which handles pure-content rules, conventions, and dependencies); each mechanism solves the half of "agent context delivery" that the other doesn't.

## Two-mechanism architecture

### Context

The discovery substrate (see `discovery-model.md`) was designed for trigger-routed context loading of pure-markdown content — rules, conventions, dependencies. Mid-design, the question of system deployment surfaced: systems like `log`, `navigator`, `transcripts`, and `pdf` are more than markdown — they ship Python code, workflows, working files, MCP servers, and a SKILL.md. Treating them as "content" is wrong; they need a different deployment shape.

### Options Considered

**Single-mechanism substrate handles everything** — extend the discovery substrate to deploy systems too, copying full system trees to scope. Rejected: a frozen scope-copy of system code drifts from cache on plugin upgrade, defeats `ocd-run`'s dynamic cache resolution, and forces re-install for every code change.

**Two-mechanism architecture: substrate for content, shim for systems** — substrate handles markdown context (already specified); a parallel shim model handles systems with code. Each mechanism is locally optimal for its concern. Adopted.

### Decision

The plugin architecture has two complementary deployment mechanisms.

**Discovery substrate** — for pure-markdown context (rules, conventions, dependencies):

- Content copied to scope at install
- Stable scope paths in stubs
- Plugin upgrades require explicit `setup sync` to refresh content
- "Stable until sync" is correct semantics for reference content

**Shim model** — for systems (code + workflows + working files + skill entry):

- Thin SKILL.md shim deployed at `<scope>/.claude/skills/<plugin>-<system>/`
- Shim body is `Call: !`<plugin>-path <system>`` — preprocessing resolves to current cache path
- Agent reads cached system CLAUDE.md; relative paths inside resolve against cache
- Plugin upgrades flow through automatically per invocation; no scope-content drift to sync

### Consequences

- **Enables:** correct semantics per content type (stable for reference, dynamic for systems); plugin upgrades transparent for skill-mediated work; no full-system scope copies
- **Constrains:** authors must understand which mechanism a contribution uses; install machinery must implement both
- **Test surfaces:** rules system migrates first through the substrate; transcripts system migrates first through the shim model. Each is the canonical test case for its mechanism

## Shim shape and authoring discipline

### Context

After confirming the shim model, the question is what the deployed shim file looks like and what discipline its body must follow.

### Options Considered

**Inline content via `!`cat <cache-path>`** — preprocess substitutes the cached CLAUDE.md content into the shim body before the agent sees it. Rejected: depends on nested `!`...`` preprocessing for any backtick commands inside the inlined content (untested), and breaks relative-path resolution (cached file's relative paths would resolve against the shim's location, not the cache's).

**Path resolution + `Call:` directive** — shim body resolves the cache path via `!`<plugin>-path <system>``, then `Call:` instructs the agent to Read the resolved path. The agent reads the actual file at the actual cache location, so relative paths inside resolve correctly against the cache. Single preprocessing step (no nesting). Adopted.

### Decision

Shim shape:

```yaml
---
description: <copied from cached SKILL.md frontmatter at install time>
allowed-tools: <copied from cache>
---

# /<plugin>-<system>

Call: !`<plugin>-path <system>`
```

The new `<plugin>-path` bin (e.g., `ocd-path`) is a thin wrapper that returns the absolute path to a system's CLAUDE.md in the current cache. Implementation: walks ancestors from `__file__` for the `.claude-plugin/plugin.json` marker (same logic as `tools.environment.get_plugin_root()`), appends `systems/<system>/CLAUDE.md`. Lives next to `<plugin>-run`.

Authoring discipline for the system's CLAUDE.md (what the agent reads after `Call:`):

- All operations dispatch through `<plugin>-run` invocations — never hardcode cache paths
- Embedded `!`...`` blocks must avoid `$` shell expansions (Claude Code's preprocessing security guard rejects them; see *Empirical constraints* below)
- Embedded `!`...`` blocks must succeed (exit 0) — any non-zero exit halts the entire skill load
- Relative paths within the CLAUDE.md (`Read: workflows/install.md`, `Call: _component.md`) resolve against the cache's CLAUDE.md location, automatically picking up correct cache version

### Consequences

- **Enables:** plugin upgrades transparent to skill invocation; one-line shim body is trivial to install/sync; no nested-preprocessing dependency; relative-path resolution works as authored
- **Constrains:** every plugin must ship a `<plugin>-path` bin; system CLAUDE.md authors must follow the discipline
- **Sync trigger:** shims still need `setup sync` when the cached SKILL.md's `description` or `allowed-tools` change; install rewrites those frontmatter fields. Body itself never changes (it's always one `Call:` line)

## Empirical constraints from preprocessing

### Context

Before locking the shim model, empirical tests via headless `claude -p "/test-plugin-context"` confirmed the relevant Claude Code behaviors and surfaced two constraints not documented anywhere.

### Findings

| Probe | Result | Implication |
|---|---|---|
| `which ocd-run` from user-level skill `!`...`` | resolved to cache path | Plugin `bin/` IS on PATH for user-skill preprocessing |
| `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR` | all unset | Plugin context env vars NOT set in user-skill preprocessing |
| `git rev-parse --show-toplevel` from preprocessing cwd | resolved correctly | Project dir resolution works via fallback (no env var needed) |
| `pwd` during preprocessing | matches the project's cwd | Preprocessing runs in project working directory |
| `!`echo "${VAR:-default}"`` | rejected with "Contains expansion" | Security guard blocks `$` shell expansions in preprocessing |
| `!`<command>`` exits non-zero | entire skill fails to load | Preprocessing failure is fatal to skill rendering |

### Decision

The architecture relies only on documented + tested behaviors:

- `<plugin>-run` and `<plugin>-path` work because plugin `bin/` is on PATH (verified)
- The `bin/` scripts self-locate via the marker walk in `tools.environment.get_plugin_root()`, no env var dependency
- Project dir resolves via `git rev-parse` fallback in `get_project_dir()`, no env var dependency
- `CLAUDE_PLUGIN_DATA` is not used by any runtime code path in the plugin (only by hooks and `.mcp.json` substitution, both of which Claude Code provides the env var for)

Authoring rules derived from constraints:

- No `$` expansions in `!`...`` blocks — use commands without shell variable references
- All `!`...`` commands must succeed — use `<command> || echo FALLBACK` patterns when failure is possible
- Path resolution flows through `<plugin>-run` and `<plugin>-path` (the bins handle everything; shims and CLAUDE.md authors don't reach into env vars or absolute paths)

### Consequences

- **Enables:** confidence that the shim model works in production; concrete authoring rules (not "it should work" speculation)
- **Constrains:** any future shim or CLAUDE.md content must follow the no-expansion / always-succeed discipline; failures here are opaque (the skill silently fails to render)
- **Documentation:** the rules above belong in a system-CLAUDE.md authoring convention that lives at the project's convention layer

## Plugin-skill vs user-skill split

### Context

Claude Code distinguishes plugin-skills (declared in `plugin.json`'s `skills` field, namespaced as `/<plugin>:<skill>`) from user-skills (at `~/.claude/skills/<name>/SKILL.md`, invoked as `/<skill>`). The shim model deploys shims as user/project skills, which means dropping or scoping the plugin-skill declaration.

### Options Considered

**All systems remain plugin-skills** — declare every system in `plugin.json`'s `skills` field. Rejected: every system auto-loads metadata at session start (always-on cost); no per-system enable/disable; "the plugin is the minimum disable unit."

**All systems become user/project shims** — drop `plugin.json` skills entirely; everything opt-in via `setup install <system>`. Rejected: no bootstrap path — the user has to know to run `setup install` before anything works.

**Bootstrap-only as plugin-skill, everything else as shim** — `setup` is the only plugin-declared skill (auto-loads when plugin is enabled); all other systems become deployable shims. Adopted.

### Decision

`plugin.json` declares only `setup` as a plugin-skill. Other systems' SKILL.md files in the source tree are NOT exposed via plugin-skill discovery; they're cached and reachable through `<plugin>-path`.

Install flow:

1. User installs plugin via marketplace
2. `/ocd:setup` is auto-available (plugin-skill)
3. User runs `/ocd:setup install <system> --scope <scope>` for each desired system
4. Setup deploys `<scope>/.claude/skills/<plugin>-<system>/SKILL.md` as a thin shim
5. Setup also deploys the system's `<scope>/.claude/rules/<plugin>/<system>/triggers.md` (per the discovery substrate; see `discovery-model.md`) — registers the cognitive moments that route to this skill

User invokes systems as `/<plugin>-<system>` (e.g., `/ocd-log`, `/ocd-transcripts`) — the namespace separator becomes a hyphen because user-skills don't support `:` namespacing.

### Consequences

- **Enables:** per-system, per-scope enable/disable (user/project skills are file-presence-controlled); minimum always-on context (only setup's metadata is always loaded); user has explicit control over which systems are available where
- **Constrains:** out-of-the-box experience changes — installing the plugin doesn't immediately expose `/ocd:log`; the user must run `setup install log` first. The `ocd:` namespace is lost for system invocations (replaced with `ocd-` prefix)
- **Migration:** every existing plugin skill needs to be re-evaluated as either plugin-bound (rare; only setup-class bootstraps) or shim-deployed (default)

## Substrate routing to shims

### Context

Two pathways surface a deployed shim to the agent's intent matching:

- **Native skill awareness** — Claude Code matches the agent's prompt context against each installed skill's `description` frontmatter; one description per skill.
- **Substrate routing** — the discovery substrate's per-system `triggers.md` files contain rows mapping curated trigger prose to skill invocations with verb-level args (e.g., `Skill: /ocd-log friction`).

### Decision

Both pathways operate; they're complementary. Native skill awareness is the always-on safety net surfacing skills via Claude Code's matching. Substrate routing provides the curated, sharp routing the system author designed for — including verb-and-args precision the single `description` field can't carry.

When `setup install <system>` runs, it deploys both:

- The shim at `<scope>/.claude/skills/<plugin>-<system>/SKILL.md`
- The triggers file at `<scope>/.claude/rules/<plugin>/<system>/triggers.md`

The triggers file's rows pointing at this skill are how the substrate routes intent to this shim. The shim itself doesn't know about substrate routing; it just receives a slash-command invocation and dispatches to the cache CLAUDE.md.

### Consequences

- **Enables:** verb-level routing precision via the substrate; coarse fallback via native skill awareness; system author authoritative over routing prose
- **Constrains:** install/uninstall must coordinate both files (shim + triggers); they're two pieces of a single system's contribution
- **Cross-reference:** see `discovery-model.md` for the substrate shape and trigger-target semantics

# Dependency Resolution

Files declare runtime dependencies via a body `## Dependencies` section listing `[[name]]` references. Agents discover each name's location on the filesystem and load the resolved file if not already in context. The resolved file's own `## Dependencies` section resolves transitively under the same rules.

## What qualifies as a dependency

Dependencies are *runtime* disciplines — rules guiding agent-generated content as the workflow runs (commit messages, CHANGELOG entries, gate phrasing, composed markdown). The rule must be loaded each invocation.

Authoring disciplines — rules shaping the workflow itself (return-spec design, error-message structure, file decomposition, naming) — don't belong as declared deps. They guide the workflow author, not the runtime executor. If a workflow seems to need an authoring rule at runtime, it's under-specified — tighten the return shape, error templates, or output format until the agent has nothing to figure out.

## Dependencies section format

A file declaring runtime deps includes a `## Dependencies` section near the top, using this template:

```
## Dependencies

Read each if not already in context. Discover via `find ~/.claude <project>/.claude -path "*dependencies/<name>.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`. Selection: prefer user-scope; prefer `rules/dependencies/` over plain `dependencies/`. User-scope skills skip project matches. If discovery returns nothing, the dep is not deployed — operate without it (graceful degradation) and surface a one-line note when behavior is affected.

- [[name]]
- [[another-name]]
```

The discovery command + selection clause are templated boilerplate — copy verbatim. Each `[[name]]` bullet declares one dependency.

## Two storage roles, two folder names

Same rule body, two different filesystem locations with distinct roles:

| Folder | Role | Discoverable |
|---|---|---|
| `<scope>/rules/dependencies/<name>.md` | Deployed always-on. Claude Code auto-loads into every session at session start. | Yes |
| `<scope>/dependencies/<name>.md` | Deployed lazy. Loaded by skills via this discovery convention when found. | Yes |
| `<skill>/_dependencies/<name>.md` | Seed canonical. Source content for `/ocd:rules install` to copy from. NOT a runtime fallback. | **No** — excluded by the discovery find filter |
| `shared/_dependencies/<name>.md` | Project-development canonical. Source of truth that pre-commit propagates into each `<skill>/_dependencies/<name>.md`. | **No** — same exclusion |

The `_dependencies/` underscore prefix marks internal-storage role: these files exist to seed scope-level deployments via the rules skill, not to act as a discovery fallback. The find filter excludes any path under `*/_dependencies/*` precisely so plugin caches and marketplace clones don't surface their bundled seeds as discovery candidates.

## Selection rules

Discovery returns all candidate paths from the four valid deployment positions. The agent picks one by applying these rules in order:

1. **User-scope before project-scope.** `~/.claude/...` wins over `<project>/.claude/...`. User-installed disciplines apply consistently across every project the user works in.
2. **Promoted before lazy.** `rules/dependencies/<name>.md` wins over `dependencies/<name>.md` within each scope. Promoted = explicitly elevated to always-on context (auto-loaded by Claude Code); lazy = on-demand only (loaded via this discovery convention when a skill fires).
3. **User-scope skills skip project matches.** A skill installed at `~/.claude/skills/<name>/` behaves identically across projects by never reaching into project-scope deps.

If discovery returns no candidates, the dep is not deployed at any reachable scope. The skill operates without it. Skills that need a particular dep should fail gracefully or surface a one-line note recommending `/ocd:rules install <name> --scope <scope>`.

## Cross-reference notation

Body cross-references to other rules use wikilink notation: `[[name]]`. Every body `[[name]]` reference must also appear as an entry in the file's `## Dependencies` section list — body and section stay aligned.

Don't recapitulate a dep's content inline. Defer with a brief pointer (`"per [[name]]"`, `"following [[name]]"`) and the agent loads the dep itself. Restating dictates what the dep already covers; the dep's body is the canonical source.

## Dedup semantics

The "if not already in context" qualifier is *path-based*. Once a specific path has been read in the current session, subsequent references to the same name resolve to the same path (per the selection rules) and pass the in-context check. Discovery runs once per dep name per session; the result caches in the agent's working context.

Identical content at different paths does NOT dedup automatically — agents treat path identity as authoritative because files at different paths can diverge. Consistent path resolution per the selection rules is what makes dedup work: the convention guarantees one path per name per consumer's scope.

## Transitive resolution

If a resolved file declares its own `## Dependencies`, those resolve recursively under the same selection rules. Cycle-safe — names already-resolved short-circuit. The transitive closure is the full set of files the agent loads to consume the initial reference.

## Rules-skill verbs

The `/ocd:rules` skill is the only writer of deployed rule files:

- `install <name> --scope <user|project> [--force]` — copies from `<rules-skill>/_dependencies/<name>.md` (seed canonical) to `<scope>/rules/dependencies/<name>.md` (always-on). Auto-loads on next session start.
- `uninstall <name> --scope <user|project>` — removes the deployed copy. The seed canonical at `<skill>/_dependencies/` remains; reinstall regenerates the deployed copy.

The lazy path `<scope>/dependencies/<name>.md` is not managed by the skill — move files there manually if you want a rule findable by discovery but not always-on (rare; usually pick promoted-always-on or skip entirely).

Users never move seed canonicals manually. Skills never copy seeds at runtime either — `_dependencies/` is install-source-only.

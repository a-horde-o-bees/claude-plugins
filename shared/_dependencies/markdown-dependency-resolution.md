# Dependency Resolution

Files declare runtime dependencies via a body `## Dependencies` section listing `[[name]]` references. Agents discover each name's location on the filesystem and load the resolved file if not already in context. The resolved file's own `## Dependencies` section resolves transitively under the same rules.

## What qualifies as a dependency

Dependencies are *runtime* disciplines — rules guiding agent-generated content as the workflow runs (commit messages, CHANGELOG entries, gate phrasing, composed markdown). The rule must be loaded each invocation.

Authoring disciplines — rules shaping the workflow itself (return-spec design, error-message structure, file decomposition, naming) — don't belong as declared deps. They guide the workflow author, not the runtime executor. If a workflow seems to need an authoring rule at runtime, it's under-specified — tighten the return shape, error templates, or output format until the agent has nothing to figure out.

## Dependencies section format

A file declaring runtime deps includes a `## Dependencies` section near the top, structured as a PFN block. The list under step 1 is the data the skill author maintains; the procedure under step 2 is templated boilerplate (copy verbatim):

```
## Dependencies

1. {dependencies}:
    - [[name]]
    - [[another-name]]
2. For each {dependency} in {dependencies}:
    1. {found}: bash: `find ~/.claude <project>/.claude -path "*dependencies/{dependency}.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`
    2. If {found} is empty:
        1. {scope}: `<project>` if `<skill-base>` starts with `<project>`, else `~`
        2. bash: `cp <skill-base>/_dependencies/{dependency}.md {scope}/.claude/dependencies/{dependency}.md`
        3. {path}: the cp target
    3. Else: {path}: first of {found} — prefer user-scope; `rules/dependencies/` over plain `dependencies/`; user-scope skills skip project matches
    4. Read {path} if not in context
```

`{dependency}` extracts the name inside the `[[]]` wikilink during iteration — the loop body substitutes the bare name into shell paths. `<skill-base>` is the skill's runtime base directory (Claude Code emits "Base directory for this skill: ..." in the system reminder when a skill fires; substitute that path).

The auto-deploy step (2.2.2) lazily seeds the rule into `<scope>/.claude/dependencies/<name>.md` (NOT `rules/dependencies/`) on first miss — the deployed file is then discoverable on subsequent invocations across this skill and any other skill that declares the same dep. Promotion to always-on (`rules/dependencies/`) is the `/ocd:rules install` skill's role; auto-deploy stops at lazy.

## Two storage roles, two folder names

Same rule body, two different filesystem locations with distinct roles:

| Folder | Role | Find returns? |
|---|---|---|
| `<scope>/rules/dependencies/<name>.md` | Deployed always-on. Claude Code auto-loads into every session at session start. | Yes |
| `<scope>/dependencies/<name>.md` | Deployed lazy. Loaded by skills via this discovery convention when found. | Yes |
| `<skill>/_dependencies/<name>.md` | Seed canonical. Source content the discovery procedure copies into `<scope>/dependencies/<name>.md` on first miss; also the source `/ocd:rules install` reads when promoting to `rules/dependencies/`. | **No** — excluded by the discovery find filter; reached only by the auto-deploy step's explicit `cp` |
| `shared/_dependencies/<name>.md` | Project-development canonical. Pre-commit propagates into each `<skill>/_dependencies/<name>.md`. | **No** — same exclusion |

The `_dependencies/` underscore prefix marks internal-storage role: the discovery find filter excludes any path under `*/_dependencies/*` so plugin caches and marketplace clones don't surface their bundled seeds as direct discovery candidates. Bundled seeds become reachable only through the explicit `cp <skill-base>/_dependencies/{dependency}.md ...` step in the auto-deploy procedure — that's the controlled entry point.

## Selection rules

Discovery returns all candidate paths from the two scope × two layer matrix. The agent picks one by applying these rules in order:

1. **User-scope before project-scope.** `~/.claude/...` wins over `<project>/.claude/...`. User-installed disciplines apply consistently across every project the user works in.
2. **Promoted before lazy.** `rules/dependencies/<name>.md` wins over `dependencies/<name>.md` within each scope. Promoted = explicitly elevated to always-on context (auto-loaded by Claude Code); lazy = on-demand only (loaded via this discovery convention when a skill fires).
3. **User-scope skills skip project matches.** A skill installed at `~/.claude/skills/<name>/` behaves identically across projects by never reaching into project-scope deps.

On empty discovery, the procedure auto-deploys from the skill's bundled seed at `<skill-base>/_dependencies/<name>.md` to `<scope>/.claude/dependencies/<name>.md` (lazy), where `<scope>` is the skill's install scope (project if `<skill-base>` is under `<project>`, else user). After the cp, subsequent discovery finds the deployed copy. If the seed is also missing, the cp fails noisily — that's a skill-authoring failure (the skill declared a dep without bundling its seed), not a runtime case.

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

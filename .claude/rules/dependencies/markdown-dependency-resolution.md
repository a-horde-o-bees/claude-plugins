# Dependency Resolution

Files declare runtime dependencies via a body `## Dependencies` section listing `[[name]]` references. Agents discover each name's location on the filesystem and load the resolved file if not already in context. The resolved file's own `## Dependencies` section resolves transitively under the same rules.

## What qualifies as a dependency

Dependencies are *runtime* disciplines — rules guiding agent-generated content as the workflow runs (commit messages, CHANGELOG entries, gate phrasing, composed markdown). The rule must be loaded each invocation.

Authoring disciplines — rules shaping the workflow itself (return-spec design, error-message structure, file decomposition, naming) — don't belong as declared deps. They guide the workflow author, not the runtime executor. If a workflow seems to need an authoring rule at runtime, it's under-specified — tighten the return shape, error templates, or output format until the agent has nothing to figure out.

## Dependencies section format

A file declaring runtime deps includes a `## Dependencies` section near the top, using this template:

```
## Dependencies

Read each if not already in context. Discover via `find ~/.claude <project>/.claude -path "*dependencies/<name>.md" -type f 2>/dev/null`. Selection: prefer user-scope; prefer `rules/dependencies/` over plain `dependencies/`; skill-bundled is last resort. User-scope skills skip project matches.

- [[name]]
- [[another-name]]
```

The discovery command + selection clause are templated boilerplate — copy verbatim. Each `[[name]]` bullet declares one dependency.

## Selection rules

Discovery returns all candidate paths. The agent picks one by applying these rules in order:

1. **User-scope before project-scope.** `~/.claude/...` wins over `<project>/.claude/...`. User-installed disciplines apply consistently across every project the user works in.
2. **Promoted before lazy.** `rules/dependencies/<name>.md` wins over `dependencies/<name>.md` within each scope. Promoted = explicitly elevated to always-on context; lazy = on-demand only.
3. **Skill-bundled is last resort.** `<skill>/dependencies/<name>.md` reached only when no user or project copy exists. Bundles are distribution-time fallbacks.
4. **User-scope skills skip project matches.** A skill installed at `~/.claude/skills/<name>/` behaves identically across projects by never reaching into project-scope deps.

## Cross-reference notation

Body cross-references to other rules use wikilink notation: `[[name]]`. Every body `[[name]]` reference must also appear as an entry in the file's `## Dependencies` section list — body and section stay aligned.

Don't recapitulate a dep's content inline. Defer with a brief pointer (`"per [[name]]"`, `"following [[name]]"`) and the agent loads the dep itself. Restating dictates what the dep already covers; the dep's body is the canonical source.

## Dedup semantics

The "if not already in context" qualifier is *path-based*. Once a specific path has been read in the current session, subsequent references to the same name resolve to the same path (per the selection rules) and pass the in-context check. Discovery runs once per dep name per session; the result caches in the agent's working context.

Identical content at different paths does NOT dedup automatically — agents treat path identity as authoritative because files at different paths can diverge. Consistent path resolution per the selection rules is what makes dedup work: the convention guarantees one path per name per consumer's scope.

## Transitive resolution

If a resolved file declares its own `## Dependencies`, those resolve recursively under the same selection rules. Cycle-safe — names already-resolved short-circuit. The transitive closure is the full set of files the agent loads to consume the initial reference.

## Rules-skill verbs

The rules skill is the only mover of files between `rules/dependencies/` and `dependencies/`:

- `install <name> [--scope user|project]` — `<scope>/dependencies/<name>.md` → `<scope>/rules/dependencies/<name>.md`. Becomes always-on on next session start.
- `uninstall <name>` — reverses. Other files continue finding it via discovery; just no longer always-on.

Users never move dependency files manually. Skills never move them either — they ship bundled fallbacks for distribution-time discoverability only.

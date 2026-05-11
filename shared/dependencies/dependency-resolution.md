# Dependency Resolution

Skills declare shared rule/reference files (e.g., PFN, file-decomposition) in SKILL.md frontmatter. Every invocation runs the bundled resolver script, which checks each dependency's deployed location, deploys the skill's bundled fallback if nothing is found, and emits a path list for the agent to load.

The resolver runs unconditionally — no gating on "is this dep installed." Correctness comes from idempotence: the check is a cheap stat sequence; the deploy is a one-time copy. Skills self-heal when deployed copies go missing (manual cleanup, between-session rules-skill demotion, partial plugin-update state).

## Resolution order

The order is asymmetric by install scope. User-scope skills only check user scope (so they stay portable across projects); project-scope skills check project first, falling back to user-scope as defaults.

**User-scope skill** (`~/.claude/skills/<name>/`):

1. `~/.claude/rules/dependencies/<name>.md` — promoted
2. `~/.claude/dependencies/<name>.md` — lazy
3. None found — deploy bundled copy to step 2's path

**Project-scope skill** (`<project>/.claude/skills/<name>/`):

1. `<project>/.claude/rules/dependencies/<name>.md` — promoted, project-scope
2. `~/.claude/rules/dependencies/<name>.md` — promoted, user-scope fallback
3. `<project>/.claude/dependencies/<name>.md` — lazy, project-scope
4. `~/.claude/dependencies/<name>.md` — lazy, user-scope fallback
5. None found — deploy bundled copy to step 3's path

The asymmetry preserves user-scope skill portability — a user-installed skill's behavior does not change based on which project it runs in. Project-scope skills can pick up project-specific overrides or fall through to user-scope defaults.

The location distinction (`rules/dependencies/` vs `dependencies/`) is meaningful for the rules-skill's user-facing promotion model — it tells the user whether the dep loads as always-on context on next session start. It does not affect resolver output.

## Resolver output

```
Dependencies for this skill:
- /path/to/dep1.md
- /path/to/dep2.md

Load any listed dependencies not already in context.
```

The "not already in context" qualifier triggers per-file agent evaluation against current input — paths already inlined (always-on rules at session start) get skipped; others get Read in parallel. Same phrasing pattern as the convention_gate hook.

## Rules-skill verbs

The rules skill is the only mover of files between `rules/dependencies/` and `dependencies/`:

- `install <name> [--scope user|project]` — `<scope>/dependencies/<name>.md` → `<scope>/rules/dependencies/<name>.md`. Becomes always-on on next session start.
- `uninstall <name>` — reverses. Skill continues finding it via the resolver; just no longer always-on.

Users never move dependency files manually. Skills never move them either — they only deploy bundled fallbacks when nothing is found at any deployed location.

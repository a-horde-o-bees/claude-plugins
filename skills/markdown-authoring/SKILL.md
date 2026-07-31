---
name: markdown-authoring
description: Use when authoring markdown files, or to lint existing markdown on demand.
---

# markdown-authoring

Open every markdown file with a level-1 heading (`#`) naming the file, then a description of the file written per `/description-authoring`.

## Lint pass

Every invocation ends with a lint pass over the markdown touched — or, invoked purely to lint, over the files, directories, or globs the user names:

```
node ${CLAUDE_SKILL_DIR}/scripts/lint.mjs <file|dir|glob> ...
```

Fix every error; a warn is a judgment call — resolve it or knowingly leave it. `lint-spec.md` is the source of truth for what the script enforces.

## Preference overrides

Two layers, matched to how far preferences diverge:

- **Severity** — a project config retunes individual rules; project-owned, so it survives suite updates.
- **Different rules** — shadow this skill: install your own `markdown-authoring` at a nearer scope (e.g. a project's `.claude/skills/`). Every reference resolves by name through the harness priority chain, so the nearest copy wins everywhere the suite invokes it.

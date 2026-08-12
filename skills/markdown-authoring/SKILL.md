---
name: markdown-authoring
description: Use when authoring markdown files, or to lint existing markdown on demand.
---

# markdown-authoring

Use when authoring markdown files, or to lint existing markdown on demand.

## Structure

- Open every file with a level-1 heading (`#`) naming it, then its summary paragraph: when the file carries `description:` frontmatter, the first paragraph is that description verbatim — one owner for the summary, audited by diffing the two; otherwise write it per description-authoring.
- Only summary-level content sits before the first section heading — the description paragraph, then support that still reads at that level. The test: content is summary-level when it governs the document as a whole (e.g. its input, its output bounds) and would misread as scoped under any one heading; content that fires at a recognizable moment or span belongs in a precise section.
- Give a unit a heading when it is an addressable scope — cited from elsewhere or consulted independently; bind it as a bold-label bullet (`- **Label** — details`) when it is a member of a jointly-consumed set or must sit at summary level.

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

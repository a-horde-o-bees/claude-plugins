---
name: markdown-linter
description: Use when standing up or updating this project's markdown linter — sets up tooling that mechanically enforces the formatting criteria in criteria.md.
---

# Markdown Linter

Stand up project tooling that enforces our markdown formatting mechanically, so authoring skills carry only judgment. The rules to enforce live in `criteria.md`; this skill realizes them as runnable lint configuration.

## Workflow

1. Read `criteria.md` — the complete enforce-list, each criterion tagged built-in or custom.
2. Bind {linter}: reuse the project's existing markdown linter if one is configured; otherwise default to `markdownlint-cli2`.
3. For each criterion in `criteria.md`:
   - If a built-in {linter} rule covers it: enable and configure that rule.
   - Else if it is mechanically checkable (e.g. heading-names-file, single-line paragraphs): author a custom rule.
   - Else (context-dependent, e.g. literal special-character escaping): configure it warn-level and record the limitation.
4. Write the config and any custom-rule files into the project.
5. Wire a run entrypoint — a script target and, if the project runs CI, a CI step.
6. Verify each criterion: confirm it flags a crafted violation and passes a conformant file. A criterion that can't be made to flag isn't enforced — fix the rule or drop it back to step 3.
7. Report coverage to the user: enforced, warn-only, and any criterion no rule can mechanize.

## Keeping criteria current

`criteria.md` is the source of truth. When it changes, rerun this workflow against the diff — add, retune, or remove rules so the linter and the criteria stay matched.

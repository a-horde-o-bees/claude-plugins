---
name: markdown-linter
description: Use when standing up or updating this project's markdown linter — tooling that mechanically enforces the project's markdown formatting rules.
---

# Markdown Linter

Stand up project tooling that enforces our markdown formatting mechanically, so authoring skills carry only judgment. The rules to enforce live in `criteria.md`; this skill realizes them as runnable lint configuration.

## Workflow

1. Read `criteria.md` — the enforce-list, each criterion tagged built-in or custom.
2. {linter}: the project's existing markdown linter if one is configured, else `markdownlint-cli2`.
3. For each {criterion} in `criteria.md`:
    1. If a built-in {linter} rule covers it: enable and configure that rule.
    2. Else if it is mechanically checkable (e.g. heading-names-file, single-line paragraphs): author a custom rule.
    3. Else: configure it warn-level and record the limitation — context-dependent, e.g. literal special-character escaping.
4. Write the config and any custom-rule files into the project.
5. Wire a run entrypoint — a script target, plus a CI step if the project runs CI.
6. For each {criterion} in `criteria.md`:
    1. Confirm its rule flags a crafted violation and passes a conformant file.
    2. If it can't be made to flag: fix the rule, or drop the criterion back to step 3 — an unenforceable criterion isn't enforced.
7. Report coverage to the user: enforced, warn-only, and any criterion no rule can mechanize.

## Keeping criteria current

`criteria.md` is the source of truth. When it changes, rerun this workflow against the diff — add, retune, or remove rules so the linter and the criteria stay matched.

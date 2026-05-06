# Audit skill invocation

Pre-flight check before invoking `/audit-*` skills: ensure the skill reads current content.

These skills read deployed governance files (`.claude/rules/`, `.claude/conventions/`) and cached plugin files (the target skill's `SKILL.md` and components). If template edits have not synced to deployed copies, if the target skill has uncommitted changes, or if the plugin cache is out of date relative to recent work, prompt the user to confirm running `/checkpoint` before proceeding.

Uncommitted unrelated work is fine — only changes that affect what the skill reads matter.

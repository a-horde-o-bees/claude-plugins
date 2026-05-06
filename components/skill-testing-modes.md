# Skill testing modes

Two ways to exercise a skill during development.

## Real invocation

Run via slash command (e.g., `/ocd:status`). Goes through the plugin cache — Claude Code loads everything under `plugins/<plugin>/` at session start: `SKILL.md` and every supporting file (component blocks, prompt fragments, anything in the skill directory). Edits are invisible to real invocations until `/checkpoint` refreshes the cache.

Use for **end-to-end orchestration verification**.

## Ad-hoc

Spawn a general-purpose agent via the Task tool with an explicit prompt that tells it to Read the skill's files by absolute path. Bypasses the cache — the agent reads from disk, so the latest edits propagate immediately.

Use for **iterating on component-file content** (criteria, prompt fragments, shared instruction blocks) without the `/checkpoint` cycle between edits.

## Closing out

Ad-hoc validates instruction content; real invocation validates orchestration. Before closing out skill work, verify via real invocation after a `/checkpoint`.

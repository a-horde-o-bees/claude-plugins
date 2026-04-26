---
name: transcripts
description: Extract simplified user/assistant chat from Claude Code transcripts (~/.claude/projects/<project>/*.jsonl) into companion `<stem>_chat.json` files beside each source. Also exposes the current project's transcripts directory so the session can read its own history.
argument-hint: "<project_list | project_path | chat_export [NAME ...] [--all] | chat_clean [NAME ...] [--all]>"
allowed-tools:
  - Bash(ocd-run:*)
---

# /transcripts

Extract simplified chat from Claude Code session transcripts. Source `.jsonl` files at `~/.claude/projects/<project>/` are dense with harness machinery — tool-use blocks, tool results, thinking, hook payloads. This skill writes a sibling `<stem>_chat.json` next to each source containing only the user prompts and assistant responses.

## Process Model

The skill is a thin wrapper over `ocd-run transcripts`. Four verbs:

| Verb | Effect |
|------|--------|
| `project_list` | Print the encoded folder name of every project under `~/.claude/projects/` |
| `project_path` | Print the absolute path to the current project's transcripts directory |
| `chat_export [NAME ...] [--all]` | Write `<stem>_chat.json` beside each source `.jsonl`. Default target is the current project; `--all` covers every project |
| `chat_clean [NAME ...] [--all]` | Inverse of `chat_export` — remove the companion files. Sources are untouched |

Output envelope per source:

```json
{
  "githash": "<git-compatible blob sha1 of source>",
  "messages": [
    {"type": "user",      "timestamp": "...", "message": "..."},
    {"type": "assistant", "timestamp": "...", "message": "..."}
  ]
}
```

Re-runs are idempotent: if the source's git blob hash matches the existing extract's `githash`, the file is skipped. Active sessions regenerate every run as the source grows; dormant sessions are skipped.

Project names are Claude Code's path-encoding of the project directory (e.g., `-home-dev-projects-foo`). Leading-dash names are accepted as positionals — no `--` separator needed.

## Rules

- Only top-level transcripts — subdirectory transcripts (spawned-agent sessions) are skipped
- Companion files are written in place at `~/.claude/projects/<project>/<stem>_chat.json`; Claude Code owns that directory
- Sources are never modified or removed; `chat_clean` only deletes the `_chat.json` companions

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. {verb} = first token of $ARGUMENTS
3. {verb-args} = remainder of $ARGUMENTS after {verb}

> Each verb maps 1:1 to an `ocd-run transcripts` subcommand. Output is whatever the CLI produces; no post-processing.

4. If {verb} is `project_list`:
    1. bash: `ocd-run transcripts project_list`
5. Else if {verb} is `project_path`:
    1. bash: `ocd-run transcripts project_path`
6. Else if {verb} is `chat_export`:
    1. bash: `ocd-run transcripts chat_export {verb-args}`
7. Else if {verb} is `chat_clean`:
    1. bash: `ocd-run transcripts chat_clean {verb-args}`
8. Else: Exit to user: unrecognized verb {verb} — expected project_list, project_path, chat_export, or chat_clean

### Report

Pass through the CLI's stdout and stderr. `chat_export` and `chat_clean` print a one-line count summary on stderr; `project_list` and `project_path` print to stdout for downstream consumption.

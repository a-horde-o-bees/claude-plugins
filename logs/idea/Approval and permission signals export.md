# Approval and permission signals export

Source `.jsonl` transcripts at `~/.claude/projects/<project>/` carry partial data about tool-approval events keyed by `toolUseID`. The current `chat_export` does not consume any of it — but a sibling `approvals_export` or `sessions_export` could, following the established pattern (`<domain>_export(projects)` library function + `<domain>_export` CLI subcommand, writing `<stem>_<domain>.json` beside the source).

## What IS captured in transcripts

| Signal | Shape | Meaning |
|---|---|---|
| `attachment.type == "hook_success"` | `stdout` is JSON with `hookSpecificOutput.permissionDecision` | PreToolUse hook decision. Observed values: `allow`. Claude Code also supports `deny` and `ask` per the hooks reference. |
| `attachment.type == "hook_blocking_error"` | `blockingError.blockingError` carries the reason text | Hook blocked the tool before it ran |
| `attachment.type == "command_permissions"` | `allowedTools: [...]` lists new patterns | User clicked "Yes, and don't ask again" — a rule was added to the session allowlist |
| `tool_result` content beginning `"The user doesn't want to proceed with this tool use"` | inside a user-type message | User denied the tool at the permission dialog |

## What is NOT captured

- **The permission-prompt text shown to the user.** The rendered dialog is terminal-UI-only and ephemeral — no JSONL event mirrors it. Tool name and input can be reconstructed from the `tool_use` block, but the dialog copy and suggestion list shown alongside it are lost.
- **One-time "Yes" approvals.** When the user approves without adding a rule, the tool simply runs — indistinguishable from an auto-approved or allowlisted call from the transcript alone.
- **`ask` or `deny` decisions from PreToolUse hooks.** Claude Code's hooks reference defines them, but observed samples only emit `allow`; absence here means absence in the data, not absence of the feature.
- **An official schema.** No published reference maps the full set of `type` / `attachment.type` / `system.subtype` values. The gap is acknowledged upstream in [anthropics/claude-code#11891](https://github.com/anthropics/claude-code/issues/11891).

## Implications for gap analysis

Auto-approval gaps can be **partially inferred** from transcripts:

- `command_permissions` and `hook_blocking_error` give direct signal.
- Stronger historical view: cross-reference every `tool_use` against matching `hook_success:allow` attachments and the project's settings allowlist — any `tool_use` that ran with neither is "approved interactively," capturing one-time approvals too.
- Capturing the **actual prompt text** would require a custom `PermissionRequest` hook that writes prompt context (tool, input, suggestions) to a side file at approval time. Transcripts alone are insufficient; this is only useful going forward.

## Next steps if pursued

- New `approvals_export(projects)` library function on `systems.transcripts`, mirroring `chat_export` shape — git blob hash idempotency, sibling `<stem>_approvals.json` output.
- CLI verb `ocd-run transcripts approvals_export [NAME ...] [--all]`.
- Reuse `_project_path`, `_git_blob_hash`, `_existing_githash` from `_transcripts.py` as shared helpers.

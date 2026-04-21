# docs-hooks

**URL**: https://code.claude.com/docs/en/hooks
**Type**: Official Claude Code documentation
**Authority**: Official — authoritative for hook events, handler types, JSON output schema, exit-code semantics, and matcher patterns.

## Scope

Complete reference for hook events, handler invocation, JSON output schema, exit-code behavior, matcher patterns, and hook locations.

## Key prescriptions

### Hook events (full list)

- **Once per session**: `SessionStart`, `SessionEnd`.
- **Once per turn**: `UserPromptSubmit`, `Stop`, `StopFailure`.
- **Per tool call**: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `PermissionDenied`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`.
- **Async/reactive**: `WorktreeCreate`, `WorktreeRemove`, `Notification`, `ConfigChange`, `InstructionsLoaded`, `CwdChanged`, `FileChanged`, `PreCompact`, `PostCompact`, `Elicitation`, `ElicitationResult`, `TeammateIdle`.

### Handler types

- `command` — shell subprocess (most common).
- `http` — POST JSON to URL.
- `prompt` — LLM evaluates `$ARGUMENTS`.
- `agent` — agentic verifier with tools.

### Hook output JSON schema (common fields)

```json
{
  "continue": true,
  "stopReason": "optional message when continue is false",
  "suppressOutput": false,
  "systemMessage": "warning message shown to user"
}
```

- `continue` (bool, default true): false stops Claude entirely.
- `stopReason` (string): shown when continue=false.
- `suppressOutput` (bool): omits stdout from debug log.
- `systemMessage` (string): warning shown to user.

### Event-specific fields

**Top-level `decision: "block"` + `reason`** applies only to: UserPromptSubmit, PostToolUse, PostToolUseFailure, Stop, SubagentStop, ConfigChange, PreCompact. Not SessionStart.

**hookSpecificOutput pattern**:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Context to add to Claude"
  }
}
```

### SessionStart specifics

- **Matcher values**: `startup`, `resume`, `clear`, `compact`.
- **Output**: plain stdout becomes context; JSON with `hookSpecificOutput.additionalContext` is structured equivalent.
- **`CLAUDE_ENV_FILE`** (also CwdChanged, FileChanged): hook writes env var assignments to persist into subsequent tool subprocesses.

### Exit code semantics

- **Exit 0**: JSON stdout parsed for control fields. Non-JSON stdout written to debug log (exception: UserPromptSubmit, SessionStart stdout becomes context).
- **Exit 1**: non-blocking error for most events. Execution continues. Stderr logged. (Exception: `WorktreeCreate` aborts worktree creation on any non-zero.)
- **Exit 2**: blocking error. Effect varies by event:
  - `PreToolUse` blocks the tool.
  - `UserPromptSubmit` blocks the prompt.
  - `Stop` prevents Claude stopping.
  - `PreCompact` blocks compaction.
  - `PostToolUse`, `PostToolUseFailure` — shows stderr (tool already ran).
  - `PermissionDenied` — exit code ignored.
  - Other events — shows stderr to user only.

### PreToolUse output schema

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "reason",
    "updatedInput": {},
    "additionalContext": "..."
  }
}
```

### Common handler fields

```json
{
  "type": "command",
  "if": "Bash(git *)",
  "timeout": 600,
  "statusMessage": "...",
  "once": false,
  "async": false,
  "asyncRewake": false,
  "shell": "bash"
}
```

- `if` — permission rule filter (tool events only). Examples: `Bash(git *)`, `Edit(*.ts)`.
- `timeout` — seconds; defaults 600 command / 30 prompt / 60 agent.
- `once` — runs once per session then removed (skills/agents only).

### Matcher patterns

- `"*"`, `""`, omitted — match all.
- Only letters/digits/underscore/pipe — exact or pipe-separated list (e.g. `Bash`, `Edit|Write`).
- Any other character — treated as JavaScript regex.

### MCP tool naming

- `mcp__<server>__<tool>` — exact match.
- `mcp__memory__.*` — all tools from memory server.
- `mcp__.*__write.*` — write operations from any server.

### Hook locations

- `~/.claude/settings.json` (user, all projects).
- `.claude/settings.json` (project).
- `.claude/settings.local.json` (project, local only).
- Managed policy settings (org-wide).
- Plugin `hooks/hooks.json` (when plugin enabled).
- Skill/agent frontmatter (when component active).

## Use for

- Verifying hook handler output JSON against the schema.
- Resolving exit-code semantics per event type.
- Understanding matcher syntax (exact vs regex) and MCP tool naming.
- Checking SessionStart sub-event matchers (startup/resume/clear/compact).
- `CLAUDE_ENV_FILE` mechanism for persisting env vars across tool subprocesses.
- Hook handler types beyond `command`: http, prompt, agent.

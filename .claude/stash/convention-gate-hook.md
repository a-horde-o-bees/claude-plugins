# Convention Gate Hook

Block Edit/Write tool calls until the agent has read applicable conventions for the target file.

## Goal

Make convention awareness unmissable and dynamic. When an agent edits `foo.py`, it should be confronted with the fact that `python.md` conventions apply — before the edit proceeds.

## Approach Explored

PreToolUse hook on Edit|Write that:
1. Extracts target file path from tool_input
2. Runs conventions CLI to find matching conventions (not rules — those auto-load)
3. If matching conventions exist: block with a message listing them
4. Agent reads conventions, retries, edit proceeds

## What Blocked It

The retry loop problem: after the agent reads conventions and retries the edit, the hook blocks again with the same message. The agent can't signal "I've read the conventions" because:

- **Extra tool fields stripped** — Edit/Write schemas enforce `additionalProperties: false`; extra fields like `conventions_ack` are stripped before the hook receives `tool_input`
- **Shared state files won't work** — spawned agents share the filesystem but have independent contexts; agent A acknowledging conventions doesn't mean agent B has read them
- **Bash wrapper loses Edit UI** — routing convention-gated edits through a Python script works but loses diff UI and file tracking

## Workarounds Considered

- **TTL-based retry** — block first attempt, allow retry within 30 seconds to same file path. Imperfect but simple. Doesn't distinguish between agents.
- **Bash acknowledgment command** — agent runs a separate command to write state, then retries edit. State file problem across agents remains.
- **Non-blocking informational** — hook exits 0 with convention list as stdout. Agent sees it but edit already proceeds — too late to influence the edit content.

## Revisit When

- Claude Code adds extensible tool parameters (extra fields survive to hooks)
- Hook-to-tool communication mechanism emerges (hook can inject context the agent sees before composing the edit)
- Per-agent state isolation becomes possible (each agent gets own state namespace)

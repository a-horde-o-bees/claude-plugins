---
pattern: "*"
depends:
  - .claude/rules/ocd-design-principles.md
---

# Friction Detection

Capture process friction as it occurs without interrupting current work. Friction is signal that a system, tool, or process has a gap — logged for later review and action.

## What Qualifies

- Rule violations the agent couldn't avoid — rule says X but the system forces Y
- Tool gaps — needed a capability that doesn't exist, had to work around
- Unexpected state — file not where expected, schema mismatch, stale data
- Process breakdowns — steps that don't work as written when actually executed
- Repeated manual intervention — user corrected the same thing multiple times
- Any runtime issue where investigating or fixing would derail the current task

## When to Log

During any workflow, the moment friction is encountered. Do not wait until the task is complete — context degrades. Do not investigate or fix the friction inline — log it and continue.

## Where to Log

`.claude/ocd/friction/{system}.md` — where `{system}` is the system the friction is *about*, not the workflow that surfaced it. Friction with navigator discovered during evaluate-governance goes in `navigator.md`, not `evaluate-governance.md`.

Create the file if it doesn't exist. Append to it if it does.

## Format

Each entry is a timestamped bullet with enough context to act on later:

```
- {date} — {what happened}; expected {what was expected}; workaround: {what was done instead, or "none — blocked"}
```

Keep entries concise. The goal is capture, not analysis — analysis happens when the friction log is reviewed.

## Lifecycle

Friction logs are a queue, not an archive. Only unresolved friction remains in the files.

1. **Log** — append entry when friction is encountered
2. **Resolve** — fix the underlying cause (add missing tool, fix broken process, update rule)
3. **Clear** — remove the entry from the friction file after the fix is verified

Do not log friction for issues resolved in the same session. If the problem is identified and fixed immediately, there is nothing to queue.

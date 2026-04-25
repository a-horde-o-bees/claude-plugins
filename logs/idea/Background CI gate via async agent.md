---
tags: ["priority:high"]
---

# Background CI gate via async agent

## Driver

`/checkpoint` blocks ~30–90s on `gh run watch <id> --exit-status` per push. CI must finish, but the agent doesn't need to halt while it does — by the time the gate returns, the user has typically moved on to the next task and would prefer to be notified rather than be stalled.

## Proposed shape

Replace the inline `gh run watch` block with a spawned background agent:

- `/checkpoint` step 7 dispatches to a background subagent: "watch CI runs for SHA X; report pass/fail via PushNotification when done; relax timeout to 5–10 minutes."
- Foreground checkpoint completes immediately after dispatch — reports "CI scheduled, will notify on completion."
- Background agent waits, watches, then either:
    - **Pass** — pushes notification "CI green for X" and exits.
    - **Fail** — pushes notification with workflow name + run URL, optionally creates a friction log entry capturing the failure for triage.
    - **Timeout** — pushes notification "CI still running after N minutes — check `gh run list`."

The agent's only job is wait-and-report. No extra tokens spent on context (no project state needed beyond the SHA).

## Benefits

- Foreground unblocked — user can keep working through the rest of the session immediately
- Longer timeout becomes acceptable — when nothing's blocked on it, we can wait 10+ minutes for slow runs
- Failure notification surfaces asynchronously — user sees the pass/fail when relevant, not when the checkpoint command happened to complete

## Constraints

- Background agents have token cost — need to ensure the watch agent's prompt is minimal (just SHA + watch + notify)
- PushNotification surface needs to exist in this CLI — confirm before designing
- The `/checkpoint` report changes — instead of "CI status: passed" inline, it reports "CI watch dispatched (run ID X)" and the user gets the actual result later

## Open questions

- Should the foreground report wait briefly (~5s) for the runs to be scheduled before dispatching, or fire immediately and let the background agent handle "no runs yet" polling?
- What's the right notification text? Does the user want concise ("CI green") or detailed (workflow names + durations)?
- Does `claude --continue` pick up notifications correctly mid-session, or do they require the user to be active?

## Why now

Most-frequent friction in `/checkpoint`. Resolving it removes the largest single block-time contributor from the workflow. Pairs naturally with the existing **standard system init** refactor — both reduce checkpoint friction without changing the underlying contracts.

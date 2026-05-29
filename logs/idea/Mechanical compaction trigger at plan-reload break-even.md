# Mechanical compaction trigger at plan-reload break-even

Idea — captured 2026-05-21.

## The lever

Every prompt sent to the agent re-reads the full conversation context. That cost is paid *per prompt*, not once per session. So the marginal cost of carrying an unnecessarily large session is multiplied by how many turns remain.

Conversely, compacting and re-loading planning docs on cold pickup pays the reload cost *once*. After that, the lighter session pays a lower per-prompt cost going forward.

Break-even: compact when the cost of loading all planning docs necessary to resume work equals roughly **10% of the current session context** — the per-prompt overhead. Below that ratio, compacting is premature (the reload is cheap, but the session isn't yet expensive enough for the savings to amortize). Above it, every additional turn pays the bloat tax for nothing.

10% is a starting heuristic; the right ratio depends on expected remaining turns. A session about to wrap doesn't benefit from compacting even at 50%; a long-running workstream benefits from compacting at 5%. The ratio should be tunable, not a hard constant.

## What's needed to make this mechanical

Two missing capabilities:

1. **Read current session context size.** Today only the user has direct visibility via `/context`. The agent doesn't see token counts of its own conversation. Need to investigate: does any tool surface (Bash, MCP, harness API) expose the current session's token consumption to the agent at decision time? If not, the trigger has to be human-invoked or based on heuristic proxies (turn count, time, recent tool-call volume).

2. **Quantify reload cost.** "Cost to load planning docs necessary to resume" requires:
   - A known, named set of docs that constitute the resumption surface (typically: `TASKS.md` + the active `plans/<workstream>.md` + 1–2 supporting decision logs).
   - Their summed token cost — readable via filesystem + tokenization estimate.
   - Confidence that loading them is sufficient (the docs must actually carry the resumption state, which depends on the process-progress discipline below).

## Dependency: stricter process-progress tracking

This trigger only works if "where we left off" is reliably captured *in files*, not just in conversation history. Today's pattern is mixed — some workstreams have clean `plans/<name>.md` with checkboxes, others rely on conversation context for current sub-step.

Requirements before the trigger is usable:

- A per-workstream progress stack: which phase is active, which step within the phase, what the immediate next concrete action is.
- Discipline that the agent updates this stack on each meaningful step — not at session end (which never happens cleanly on compaction-driven cutoffs).
- A naming convention so the resumption-surface doc set is mechanically derivable: given a workstream name, return the file set to reload.

Without this, compacting at break-even still produces a cold session that doesn't know what to do next — the reload cost is paid but the resumption fails. The trigger is only as good as the artifacts being reloaded.

## Sequencing

This is downstream of building a stricter process-progress tracking stack. That stack should land first; the break-even trigger builds on top.

Adjacent work: when the transcripts content-extraction (`plans/transcripts.md` Workstream B) ships, agent-side context for *reading* transcripts gets cheaper — which is a different lever (per-read context cost) than the per-prompt session-context cost this idea addresses. Both contribute to overall context discipline but operate on different surfaces.

## Open questions

- Is there a mechanical surface (tool, env var, hook context) that exposes current session token count to the agent? If yes, this idea is implementable now; if no, the trigger stays human-invoked or proxy-driven.
- Is 10% the right break-even ratio? Tunable per workstream length, or fixed default?
- Should the trigger fire automatically (agent compacts itself when the ratio crosses threshold) or as a recommendation surfaced to the user?
- Where does the per-workstream progress stack live? Inside the workstream plan, alongside it, or in a separate file?

## Cross-references

- Process-progress tracking — not yet a captured workstream; this idea names it as a prerequisite.
- `plans/transcripts.md` — adjacent context-cost work (different lever: per-read instead of per-prompt).

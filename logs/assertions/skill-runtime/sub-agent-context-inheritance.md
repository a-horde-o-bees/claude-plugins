---
status: confirmed
last-verified: 2026-05-21
---

# Assertion: Sub-agents have fresh context with a shared skill registry — body re-injects per sub-agent, no inheritance of "already loaded" state

Confirmed across two sibling sub-agents invoking the same skill from independent contexts. Sub-agent A loaded `/sub-target` → log went 0→1. Sub-agent B (separate sub-agent spawned independently from main) saw the log at 1 line, invoked `/sub-target` → log went 1→2. The second sub-agent fully re-loaded the body in its own context — A's "loaded" state did not propagate.

A separate observation surfaced as a side finding: **general-purpose sub-agents do NOT have access to the Agent tool** — they cannot spawn their own nested sub-agents from inside their harness.

## Why it matters

Workflows that delegate to sub-agents need to know whether skills loaded in the parent automatically carry to children. If they don't (confirmed here), each sub-agent burns its own re-injection cost — relevant for token budgeting and for designing workflows that try to "preload" skills.

The shared-registry-but-fresh-context model is the same as a brand new agent: skills are addressable, but no carried state.

## Test design

### Skill

`/sub-target` — minimal helper that appends one timestamped line to `/tmp/sub-target.log` per invocation. Unique marker: `SUB-INHERIT-OCELOT-8842`.

### Run procedure

1. Reset: `rm -f /tmp/sub-target.log`
2. Main agent spawns sub-agent A; A invokes `/sub-target`, attempts to spawn a nested sub-sub-agent via Agent tool, reports observations
3. After A returns, main agent spawns sub-agent B independently; B reads logs, invokes `/sub-target`, reads logs again
4. Verify log file deltas at each step

### Detection method

| Signal | Best case for "fresh context" hypothesis |
|---|---|
| Log line count after A's invocation | 1 |
| Log line count after B's invocation | 2 (body re-injected — no inheritance) |
| B's Skill tool call succeeded? | yes (proves registry shared) |
| A able to spawn nested sub-agent via Agent? | no (separate finding about general-purpose tool surface) |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | Fresh context confirmed; registry shared; no nested sub-agent spawn from general-purpose | After A: log 1 line (`sub-target loaded <ts1>`). A reported Agent-tool unavailable: "There is no Agent/Task sub-agent dispatch tool exposed in this harness." After B: log 2 lines (added `sub-target loaded <ts2>`). B's Skill call succeeded — no Unknown-skill error. `total_tokens` A: 26,672 / 7 tool uses; B: 16,770 / 4 tool uses. |

## Side finding — general-purpose sub-agent tool surface

The general-purpose agent description declares `Tools: *`, but in practice the Agent tool itself is excluded from the sub-agent's tool surface. Nested sub-agent dispatch only works from the main agent context. Workflows that assumed sub-agents could fan out further (parallel sub-research, recursive delegation) need to either dispatch all sub-agents from main or use a different sub-agent type that explicitly includes Agent.

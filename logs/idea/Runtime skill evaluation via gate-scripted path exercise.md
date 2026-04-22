# Runtime skill evaluation via gate-scripted path exercise

## Purpose

Extend `/ocd:audit-runtime (future skill, split from audit-static)`'s runtime phase so agents can traverse past user-interaction gates in the target skill. Today, runtime evaluation halts at the first `AskUserQuestion` — the spawned agent has no user channel, so anything downstream of a gate is never exercised.

## Trigger

Surfaced while planning an A/B comparison of `audit-governance` workflow variants on 2026-04-14. Both variants stall at the `AskUserQuestion` in step 7 ("which level to start at?"), so no actual level-walking behavior — where the variants differ — ever runs under runtime evaluation. Generalizes beyond audit-governance to any skill with mid-flow user interaction.

## Direction

Primary design — pre-answered gate script per exercisable path:

- The executor's path-trace step (today identifies `{args}`) extends to also identify each user gate the path will hit and a canonical answer for that gate. Path spec becomes `{args, gate-script: [{question-cue, answer, rationale}]}`.
- The runtime agent already interprets skill instructions itself (`_runtime-evaluation.md` step 5 — "execute those steps yourself"). Add: when the skill's instructions say `AskUserQuestion`, consult the gate-script for a matching cue and use that answer instead of invoking the tool.
- Cue-matching by question text or by step number — both should be viable; question text is robust to step renumbering, step number is robust to question-text edits. Document which is authoritative.
- Fire-and-forget Spawn semantics preserved. Concurrency stays free.

Escape hatch — unscripted-gate halt:

- When the agent encounters an `AskUserQuestion` its script doesn't cover, it halts with a structured finding (`unscripted gate at step N: question X`) and returns. The executor surfaces this as a coverage gap in the report, and the user can extend the script on the next invocation.
- Prevents silent deadlock and surfaces missing coverage as an ordinary finding rather than a failure mode.

Rejected alternative — stdout-redirect with executor as user-proxy:

- Would require either persistent spawned agents or a streaming protocol between agent and executor. Current Spawn returns once; changing that is an architectural shift, not an extension.
- N concurrent agents all prompting simultaneously would deadlock the executor unless it serializes, which defeats concurrency.
- Keep as a last resort if gate-script authoring proves infeasible for some class of skill.

Authoring concerns:

- Gate-script construction is domain-specific per target skill. Tracing paths today is mostly mechanical; adding gate answers needs understanding of what each gate gates. Reasonable for skills the executor "knows" (audit-governance, commit, push) and less so for arbitrary third-party skills.
- Gate-script could be authored alongside the path trace step or carried in the skill's own metadata (a `routes:` frontmatter-style block?). Latter makes the skill declare its own test scenarios; former keeps all authoring inside audit-runtime. Unresolved.

## Scope

A future audit-runtime skill carries the runtime workflow as its component file. Path-spec schema formalized in that file's Variables section or a shared schema reference. Gate-script tracing lives in audit-runtime's Workflow setup phase.

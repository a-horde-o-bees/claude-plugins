# Description refinement — two-phase loop (creation vs testing)

Reusable workflow shape for refining a skill description so the matcher actually fires on the queries it should and stays silent on the queries it shouldn't.

## The two phases

**Phase 1 — Creation (directed, instructional).** Spawn a fresh-context agent with explicit instructions to:

1. Read the target SKILL.md body
2. Invoke the relevant authoring disciplines via the Skill tool — `/concise-prose`, `/description-authoring`, `/trigger-specificity`, `/agent-first-interfaces`
3. Apply failure-mode framing — "what would have had to go wrong for this skill to be needed?"
4. Output: just the description string (no preamble, no explanation)

The agent's skill use is *demanded* in this phase. The output is whatever the disciplines, applied to this body, produce.

**Phase 2 — Testing (pure discovery).** Take the candidate description, install it in the SKILL.md frontmatter, then run eval queries via `claude -p <query>`:

- One subprocess per query
- **No skill-use instructions in the query** — natural-feeling user phrasing only
- The matcher in each subprocess decides whether to invoke the skill from the description alone
- Detect trigger by parsing stream-json for Skill tool_use events

## Why the decoupling matters

If the test query carried "use the description-authoring skill" or "apply the relevant authoring disciplines," we'd measure **instruction-following**, not **matcher discrimination**. The instruction layer biases the result. The two phases share no orchestration: Phase 1 produces an artifact, Phase 2 measures the artifact, neither knows about the other's mechanics.

## How to apply

- When introducing a new skill: run both phases before considering the description "set."
- When a skill's matcher reliability is suspected (mental simulation says "should trigger" but anecdotal evidence says "doesn't"): re-run Phase 2 with measured queries before adjusting the description.
- When changing a discipline rule's body (e.g., adding new bullets to `description-authoring`): re-run Phase 2 on every skill that depends on the discipline — body changes can affect matcher fit indirectly through the agent's understanding of what "this kind of description" should encode.

## Tooling

- Phase 1: use the Agent tool with a focused prompt. Fresh context isolates the creation from conversation-history bias.
- Phase 2: Anthropic upstream `skill-creator`'s `scripts/run_eval.py` provides the orchestration. Pass `--runs-per-query 1` for dry-tests (1 subprocess call); `--runs-per-query 3` (default) for real measurements.

## Derived from

- The two passes were originally one combined `run_loop` step in the Anthropic skill-creator workflow. Splitting them surfaced that loop-as-shipped wraps the testing in a feedback-driven iteration that's separable from initial creation.
- Anthropic's adversarial trigger-eval (8–10 should-trigger + 8–10 near-miss should-not-trigger queries) is the validation discipline; needs-map's failure-mode framing is the derivation discipline. Each catches what the other misses.

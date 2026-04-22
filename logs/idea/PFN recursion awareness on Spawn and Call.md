# PFN recursion awareness on Spawn and Call

## Purpose

Add a PFN-level rule that a `Spawn:` or `Call:` invocation matching an (target, args) pair already present on the current call chain is a recursion signal — the agent skips the step, records a finding with the detected chain, and continues.

## Trigger

Observed during planning of `/ocd:audit-static --target /ocd:audit-static` on 2026-04-14 (when the skill still bundled runtime evaluation). Runtime agents would invoke the target skill, which itself would spawn audit agents, producing unbounded recursion. The runtime phase has since been split out (see "Runtime skill evaluation via gate-scripted path exercise" idea); the recursion-awareness rule remains independently useful for any spawn pattern.

## Direction

- Detection key is the **full invocation identity** — target (skill path or component file) plus resolved arguments. Identity match within the current call chain = loop; different args with the same target is valid recursion (tree walkers, refiners) and must not fire the check.
- Mechanism lives in `process-flow-notation.md` as a clause on `Spawn:` and `Call:`. Rule should be short; invocation identity is already the natural match key for both constructs.
- Finding format for the skipped step should include the chain (`target X ← target X ← target X`) so the report makes the cycle visible rather than a generic "skipped: recursion."
- Interaction with evaluation skills: for `/ocd:audit-*` targeting themselves, this rule would auto-skip the recursive runtime agent and surface the self-reference as an ordinary finding. That makes self-evaluation safe without a skill-specific guard.

## Scope

PFN rule addition, plus a small update to `_runtime-evaluation.md` replacing its partial "bail on repeated state" phrasing with a reference to the PFN-level mechanism.

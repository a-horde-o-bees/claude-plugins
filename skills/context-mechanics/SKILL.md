---
name: context-mechanics
description: Use when auditing why an instruction failed to fire, fired on the wrong case, or decayed mid-session, or when designing the trigger surface of a rule, skill, hook, or CLAUDE.md block. A construction-time reference on how LLMs attend to, retrieve, and comply with in-context instructions, graded by strength of evidence — not a discipline to load into an authoring pass.
disable-model-invocation: true
---

# context-mechanics

Use when auditing why an instruction failed to fire, fired on the wrong case, or decayed mid-session, or when designing the trigger surface of a rule, skill, hook, or CLAUDE.md block. A construction-time reference on how LLMs attend to, retrieve, and comply with in-context instructions, graded by strength of evidence — not a discipline to load into an authoring pass.

The premise throughout: instructions are neither scoped nor guaranteed — they are retrieved, by soft attention, in competition, with position- and length-dependent reliability, and an artifact that assumes more than that fails silently.

Each entry carries its source, or the mechanics it follows from, and an epistemic grade — **[measured]** (replicated benchmark results), **[mechanistic]** (partial interpretability account), **[behavioral]** (consistent observed regularity, no verified circuit), **[method]** (a way to test, not a claim about the model).

## The mechanics

- **There is no compartment.** No mechanism binds an instruction block to a scope. Every context token is visible to every generation step; an instruction "applies" exactly to the degree the current generation state retrieves it — a continuous weighting, not a rule engine. Apparent compartmentalization is a learned regularity from instruction tuning, so it degrades at the edges rather than failing cleanly. **[mechanistic + behavioral]** ([Anthropic, context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))
- **Attention is a finite budget.** Every token depletes it; as context grows, the model's capacity to hold pairwise relationships stretches thin. The design goal is the smallest set of high-signal tokens, at the right altitude. **[mechanistic]** ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))
- **Position: the U-curve.** Recall is strongest at the start and end of context and weakest in the middle — double-digit accuracy drops mid-context, replicated across model families. Mechanistic account: first-token attention sink (primacy), causal masking + rotary-decay (recency), a starved middle. **[measured; mechanism partial]** ([Liu et al., Lost in the Middle](https://arxiv.org/abs/2307.03172); [mechanistic summary](https://www.tmls.nyc/research/context-rot-mechanistic))
- **Length degrades independently of position ("context rot").** Accuracy declines as input grows even when the relevant content is fixed and favorably placed. A long procedure or session erodes compliance with *all* its instructions, not just the buried ones. **[measured]** ([context-rot overview](https://redis.io/blog/context-rot/); [mechanistic summary](https://www.tmls.nyc/research/context-rot-mechanistic))
- **Recency dominates by training, amplified by architecture.** The most recent direction supersedes earlier ones primarily because dialogue training data works that way, with locality biases reinforcing it. Multi-turn interaction shows large performance drops vs. single-turn (~39% average across tasks), driven by premature-assumption lock-in and gradual drift of the conversational state. **[measured (drop); behavioral (mechanism)]** ([Microsoft, LLMs Get Lost in Multi-Turn Conversation](https://arxiv.org/abs/2505.06120))
- **Conditional binding is feature collision.** A "when X, do Y" instruction fires in proportion to the semantic/lexical overlap between how X was *phrased* and how the live situation *presents*. Soft on both sides: near-matches partially fire; true matches in unfamiliar vocabulary silently don't. A conditional that fails to bind produces no error — the failure mode is silence. **[behavioral]** (applied form: [skills docs](https://code.claude.com/docs/en/skills) — the model decides from the description plus the optional `when_to_use` field, truncated together at 1,536 chars in the listing)
- **Instructions compete.** Simultaneously-active constraints share the same retrieval auction; compliance per constraint decays as constraints accumulate. Adding a rule taxes every other rule. The instruction surface is a budget, not a list. **[measured]** ([context-rot literature](https://www.tmls.nyc/research/context-rot-mechanistic))
- **Salience markers work relatively, not absolutely.** Emphasis (`IMPORTANT`, `MUST`, warning framing) raises retrieval weight because training associated such framing with compliance-critical content — a relative effect with diminishing returns. If everything shouts, nothing does. **[behavioral]** ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); field evidence: the superpowers plugin's escalating enforcement framing, iterated because plain instruction was ignored — [design account](https://blog.fsck.com/2025/10/09/superpowers/))
- **Salience decays; re-injection restores it.** An instruction's influence fades as context accumulates past it — nothing revokes it; it loses the auction. Restating a constraint at the point of use (per-prompt, per-tool, per-phase) beats stating it once at the start. **[behavioral, following from position, length, and recency]**
- **Compliance is measurable, and phrasing is the defect.** Whether an instruction fires on the cases it should — and stays silent on the cases it shouldn't — is testable with should-trigger / should-not-trigger prompt sets and hit rates against a cold model. When wording fails to evoke the behavior, the wording is what to fix; the executor was never given the meaning. **[method]** ([skills docs: description tuning](https://code.claude.com/docs/en/skills))

## The levers, ranked by reliability

For making an instruction fire faithfully when needed:

1. **Mechanical enforcement** — remove the model from the trigger decision: a hook that pattern-matches the situation and injects the instruction (or the full artifact) at that moment; a gate that blocks the action until the condition is met. The condition becomes code; only compliance with *content* remains attentional.
2. **Point-of-use injection** — deliver or restate the instruction adjacent to the decision it governs, rather than relying on a session-start statement surviving the distance.
3. **Position** — put must-hold constraints at the edges of their artifact and of the context; never mid-block, mid-list, or mid-session only.
4. **Vocabulary collision** — write triggers in the surface vocabulary of the situations they must catch: concrete verbs, artifact names, error strings; abstract category names under-bind. One collision is enough to match, so each phrase earns its place by covering a *distinct* case — synonym runs and example-phrasing lists add no matching power while widening accidental binding. Fold needed idiom vocabulary into the trigger's own prose as fluent clauses; a platform-separated trigger field (e.g. Claude Code's `when_to_use`) is the escape hatch for a phrasing that cannot be woven, not the default home.
5. **Salience framing** — emphasis markers, spent sparingly so contrast survives.
6. **Bare statement** — a well-formed instruction, stated once, in competition with everything else. The default, and the weakest.

## Mechanical enforcement in Claude Code

Sentinel-verified behavior of the enforcement surfaces themselves (first-party experiment, 2026-07-28, Claude Code / Fable 5 — harness behavior, so re-verify across Claude Code versions):

- **`PermissionDenied` hooks never fire for deny-rule auto-blocks** — the event covers interactive prompt denials only. A redirect hook placed there sits silent while the rule denies bare. **[measured: sentinel]**
- **`PreToolUse` hooks run *before* permission-rule evaluation.** A PreToolUse `permissionDecision: "deny"` therefore both blocks the call and delivers `permissionDecisionReason` into model context — mechanical enforcement and point-of-use injection in one mechanism, and the only way a deny carries instruction. Keep the bare deny rules behind it: hooks fail open (disabled or broken ⇒ the call proceeds to normal permission flow), rules fail closed. **[measured: sentinel]**
- **Hooks register from settings files present at session start; permission rules apply immediately.** A settings file *created* mid-session contributes its deny rules at once but its hooks only after restart (or `/hooks`); once the file predates session start, subsequent hook edits hot-reload. The asymmetry means a freshly-boxed machine enforces before it redirects. **[measured]**
- **Same-event hook entries from different tools coexist, keyed by matcher** — observed surviving repeated programmatic merges (setdefault-and-append; never replace the array). The failure mode to design against is a writer that replaces. **[behavioral]**

Companion reference: `transcript-file-io.md` — measured I/O findings and correctness traps for code that reads the transcript JSONL directly (hooks, one-shot scans), gathered building a PreToolUse hook. Same epistemic footing as the sentinel findings: first-party measurements over undocumented internals; re-verify across Claude Code versions.

## The audit lens

Questions to hold any rule, description, procedure, or trigger against:

- **Collision**: does the trigger share vocabulary with the live situations it must catch, or only with the author's category for them? Does each example cover a case no other phrase covers, or restate one already present?
- **Position & distance**: where does the critical constraint sit in its artifact — and how far, in tokens, from the moment it must fire? Is anything load-bearing stranded mid-context with no restatement?
- **Budget**: what else is active in the auction when this must fire? Did adding this instruction tax the others; could two rules consolidate into one umbrella with case-bullets?
- **Decay plan**: for long sessions and procedures, what re-grounds this instruction near the point of use — a phase prefix, a hook, a step that restates it?
- **Binding of intermediate state**: does the artifact assume long-range recall — a variable bound far above, a step referenced across a long body? Rebind near consumption.
- **Silent-failure detection**: if this instruction fails to fire, what notices? A consumer, a gate, an eval — or nothing?
- **Escalation to mechanism**: could this trigger be a hook or gate instead of a request to attention?
- **Evidence**: has the trigger been tested cold (should / should-not sets, hit rate), or is compliance assumed?

## Epistemic boundary

The mechanistic claims here are partial accounts, not verified circuitry — interpretability has not produced an "instruction-following circuit." The measured effects (U-curve, length decay, multi-turn drop, constraint-accumulation decay) are benchmark results on specific model families and may shift with newer models; the levers' *ranking* has been stable across them. Verify against current sources before citing numbers forward; treat this file's citations as the re-check list.

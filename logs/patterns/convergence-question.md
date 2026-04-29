# Convergence Question

A scoping methodology: before designing a new abstraction, ask *"what existing pattern in our codebase should this work be matching?"* Recasts open-ended design as closed-ended pattern-extension when an analog exists.

## When to use

The trigger is any moment that frames a task as design rather than reuse — "how should we share this," "what's the cleanest way to model X," "this duplication needs an abstraction." Before answering the design question, ask the convergence question first.

The signal that the convergence question is load-bearing: the codebase has solved structurally similar problems in a different domain. If file-based systems compose `setup.deploy_files` and DB-based systems duplicate orchestration, the asymmetry IS the design hint — extend the existing helper pattern to cover the new domain instead of inventing a parallel one.

## Process

1. **State the duplication or design problem in shape terms.** Not "two systems init their DBs the same way" but "two systems orchestrate compare-then-act over a declared resource." Shape framing exposes structural similarity that a domain-specific framing hides.
2. **Search for an existing pattern with the same shape elsewhere.** Look for helpers, conventions, or system structures the codebase has already converged on. The match doesn't need to be perfect — it needs to be the same call-site shape (declarative inputs, helper-resolved orchestration, predictable result format).
3. **If a match exists: ask "what would extending this pattern look like?"** Mirror call signature. Mirror return shape. The new helper should read like the old helper's sibling, not its cousin.
4. **If no match exists: design proceeds, but the question still earns its place** — confirming the absence prevents accidental parallel invention later when someone notices the precedent that would have applied.

## Worked example

Mid-session during the needs-map migration, the user asked: *"we already converged on helpers for files; we hadn't for DBs?"* That single question collapsed the helper-centralization task. Before the question, the framing was *"how should we share DB-init orchestration?"* (open-ended design). After the question, the framing was *"DB-init orchestration should match the `setup.deploy_files` shape"* (closed-ended pattern extension).

The result: `tools.db.rectify(db_path, schema_builder, rel_path, force)` mirrors `setup.deploy_files(src_dir, dst_dir, pattern, force)` exactly — same call shape, same role split (system declares, helper resolves), same return type (list of `{path, before, after}` entries). The convergence-question framing produced the design without further deliberation.

See `logs/patterns/helper-centralization.md` for the *what* (extract orchestration into a `tools.*` helper); this pattern is the *how to spot it* (recognize structural asymmetry against existing patterns).

## Pitfalls

- **Forced fit.** Matching too aggressively when no real symmetry exists produces an abstraction that limps. The convergence question must allow "no match" as a legitimate answer; if every problem is forced into an existing shape, the answer is too rigid.
- **Shape-blindness when names differ.** Two systems may solve the same shape under different domain names. The shape framing in step 1 is what surfaces the symmetry — without it, "deploy files" and "rebuild DB" read as unrelated when their orchestration shape is identical.

## Anti-patterns

- **Parallel-pattern creation.** Designing a new abstraction shape for what's structurally the same problem. Two abstractions for the same shape now exist; reconciliation cost compounds with every system that picks the wrong one.
- **Asking the question after design lands.** The convergence question cheap if asked before designing; expensive if asked during code review of a parallel abstraction. By then the rework cost is real.

## See also

- `logs/patterns/helper-centralization.md` — the action this pattern's question often points toward
- `plugins/ocd/systems/rules/templates/design-principles.md` *Borrow Before Build* — the umbrella principle this pattern operates under; the principle's case bullet "Before designing a new abstraction or helper: ask what existing pattern in the codebase should this match" is the trigger form of this pattern's question

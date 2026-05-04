---
log-role: reference
---

# Decisions — Breadth-Then-Depth Consolidation

Design decisions and rationale for the breadth-then-depth methodology. Captures the **why** behind each major choice — what problem it solves, what alternatives were considered, what trade-offs are accepted.

For current-state structure, see `ARCHITECTURE.md`. For operational instructions, see `METHODOLOGY.md`.

## Failures corrected from earlier approaches

Two specific failures of earlier consolidation approaches drove the methodology's current shape.

**Functional decomposition vs technical attributes.** Earlier methodologies categorized by language and technology (Python / TypeScript / Docker). That conflates implementation choice with function — the same tool serves different purposes in different projects. Python is one option for the *server runtime* role; Docker fills *distribution channel*, *test stack*, and *deployment artifact* in different samples. Categorization by tool cannot survive technology shifts (every new framework demands a new top-level branch) and obscures the design space (a builder asking "what are my transport options" gets a list of languages instead).

The methodology categorizes by ROLE — what does the part DO. Tools are choices within roles. The role tree stays stable across technology generations.

**Qualitative consolidation vs evidence enumeration.** Earlier methodologies required inline citations after every observation, inflating output 3-5× and treating consolidation as evidence-list reproduction. The consolidated should describe each implementation path qualitatively (one canonical description per path) — not enumerate which samples exemplify it.

Provenance lives in dynamic queries (`references "Sample > <chain>"`). The consolidated stays scannable; the corpus stays queryable; the two never drift out of sync.

## Why merge-time vocabulary normalization

The merger has the hardest task: recognizing when two partials describe the same path under different names ("stdio transport" vs "JSON-RPC over stdin/stdout"). Two designs were considered:

- **Fixed vocabulary at gather time.** All gather agents use a prescribed naming scheme. Easier to merge. Rejected because it constrains discovery — agents biased toward the prescribed shape miss novel categorizations, and the vocabulary itself is what the methodology is supposed to derive
- **Free vocabulary, merge-time normalization.** Each gather agent names choices in its own words; the merger reconciles by (function, choice) pair. Accepted because it preserves the gather phase's ability to surface unexpected categorizations, at the cost of merger judgment effort

The merge-time normalization is more demanding on the merger but produces a corpus-derived tree, not a prescribed tree.

## Why two lenses

The methodology runs convergence (per-bin) and depth (per-role) as separate phases. Why not collapse?

The lenses see different things:

- The per-bin lens prevents agents from comparing all 23 supporting samples for a popular path side-by-side. Description nuance that emerges only when many implementations are stacked is invisible
- The per-role lens prevents agents from seeing each sample's full context (they see only one slice). It cannot derive new categories from sample content; it can only refine what's already there

Collapsing would require an agent to do both — split context budget between full-sample understanding and cross-corpus comparison — neither well. Separation lets each phase use its full budget on one task.

The convergence loop establishes the tree shape; the depth pass refines descriptions. Together they produce a tree that's structurally settled AND qualitatively rich.

## Why quantification is deferred and script-based

Three forces drove the deferred-quantification + script-based design:

- **Determinism by Default.** Counts are deterministic given a stable consolidated and corpus — no judgment required. Per the project's design principles, deterministic operations belong in code, not in agent-interpreted instructions
- **Idempotency.** Re-running on the same inputs must produce identical output. Sentinel-comment-based replace lets the script update tables in place without duplication or stale-state accumulation. Agents have no comparable mechanism
- **Re-runnable as inputs change.** The corpus and tree both evolve through gap-audit re-iterations. Quantification needs to re-run cheaply each cycle. A script does this in seconds; an agent run takes minutes and burns tokens

The deferred timing matters: counting before the qualitative tree converges produces meaningless numbers (the categories shift). The script runs after corrective sweep so chain keys align with the depth-refined tree.

## Why sequential dispatch is the default

Phases that batch work default to sequential dispatch for two reasons:

- **Rate-limit class elimination.** Parallel dispatch can fail when the platform throttles concurrent requests. The methodology hit this during mcp's run: 13 concurrent agents in Phase 05 failed entirely; the retry succeeded only after dropping to batches of 3-4. Sequential eliminates the failure class
- **Trailing-window calibration.** Each subsequent agent sees the prior agent's measurement (work-tok per byte). Subsequent spawns can be sized using the trailing average. Parallel dispatch can only use the calibration spawn's data — every concurrent agent works from the same stale prior estimate

Batch-parallel is opt-in when wall-clock matters more than calibration consistency. Larger concurrency widths increase rate-limit risk non-linearly; 3-4 is the sweet spot when used.

## Why these specific commit boundaries

Commit boundaries are placed at points where artifacts reach a stable state — each marks the end of an artifact's mutation by some phase. Why commit-between-phases (rather than commit-within or commit-only-at-end):

- **Mid-phase commits conflate completed and in-progress work.** A commit between bin 3 and bin 4 of normalize would freeze partial-pass state as a "checkpoint" that doesn't represent any coherent intermediate state
- **End-only commits make selective recovery impossible.** If only the final consolidated is ever committed, a mid-pass failure can only revert to the pre-methodology state — losing all completed bins, including those that succeeded

Committing at phase boundaries gives `git checkout --` a coherent state to revert to, and lets selective recovery preserve completed work within a failed phase.

## Why reset-then-retry over compound-state retry

When a phase fails mid-execution, two recovery strategies are possible:

- **Reset-then-retry.** Roll the working tree back to the last commit; re-dispatch from a clean state. Accepted
- **Compound-state retry.** Re-dispatch on top of partial state; agents discover and complete the unfinished work

Reset-then-retry won because:

- **Partial state is invalid input.** A second normalize pass over partially-rewritten samples treats the partial output as input, compounding errors silently. Detection is impossible after the fact
- **Selective recovery is cheap when most work succeeded.** If 8 of 13 bins succeeded before a rate-limit hit, the 8 are valid output. Reset only the in-progress and not-started bins (selective `git checkout`), re-dispatch from bin 9. Selective recovery is the common case for parallel-prone phases
- **Idempotent retry on top of clean state is safer than retry on top of partial state.** Sequential dispatch reduces failure frequency; reset-then-retry handles the residual cases reliably

Reset-then-retry depends on the commit cadence (above). The two designs are coupled.

## Phase-boundary decisions

**Why `02-sample-population` is separate from `03-gather`.** Sample population is research effort (per-entity); gather is synthesis (across the corpus). Separating them lets the corpus be produced once and consumed by multiple methodology runs (e.g., re-run with a refined methodology without re-doing the research). It also lets the corpus be produced externally (manual research, prior catalogs) without forcing the methodology's discipline on the research phase.

**Why the depth pass has its own phase rather than merging into normalize cycles.** See "Why two lenses" — different lenses, different agent-context budgets.

**Why `08-corrective-sweep` is split from `06-reconcile` (depth's reconciliation).** Depth reconcile integrates findings into the consolidated (description sharpenings, role-level prose, new paths). Sample-level mis-placements visible during depth pass require sample edits — different artifact, different agent capability. Splitting prevents the depth reconciler from juggling tree edits and sample edits in one context. Each phase has one job.

**Why `09-quantify` is its own phase despite being a script.** Even mechanical phases earn visibility in the enumerated sequence. The phase file documents the idempotency contract, re-run triggers, and the sentinel-comment mechanism downstream phases (gap audit) depend on. Without a phase file, future readers might miss that quantification is part of the standard sequence.

**Why gap audit is opt-in.** Corpus mining has diminishing returns. After convergence + depth + corrective + quantify, the corpus has been substantively mined; further refinement trades tokens for marginal gains. Making gap audit opt-in (rather than auto-loop) puts the cost decision with the user, who knows whether the consolidated is sharp enough for their decision.

## Strengths

- **Categorization tracks what samples DO**, not what tools they use — survives technology shifts
- **Qualitative descriptions stay human-scannable** — total document size is bounded by tree shape, not by per-sample evidence count
- **Provenance is always current** — the consolidated never drifts out of sync with the corpus
- **Quantification deferred and deterministic** — adoption counts only appear when the qualitative tree is stable, encoded as a re-runnable script
- **Cross-role linking handles tool-multi-role reality** — Docker exists in the tree wherever it functions, not buried under one role
- **Two-lens design** — convergence settles tree shape; depth pass sharpens descriptions
- **Optional re-iteration via gap audit** — corpus shallowness is detectable post-quantify; refinement is opt-in with a targeted scope rather than corpus-wide re-crawl

## Limitations

- **Pass count is unbounded** — convergence may take many normalize cycles. Suited to research budgets that allow iteration; ill-suited to tight one-shot synthesis
- **Recognition of equivalent buckets is judgment-heavy** — the merger has to recognize "Python with FastMCP" and "FastMCP-based Python server" are the same. Vocabulary normalization depends on agent capability
- **Functional decomposition has subjective edges** — what counts as "one part" vs "two related parts" is sometimes arguable. Normalize cycles correct early-bin mis-splits; some judgment remains
- **Sequential dispatch is N× slower than parallel** — for a 13-bin phase, sequential is ~10× longer wall-clock. Default sequential because rate-limit failure is more expensive than wall-clock; users with platform headroom can opt into batch-parallel deliberately
- **Implementation depth is out of scope** — the methodology produces a decision-support tree, not implementation guidance. When the user picks a path and builds, they research the implementation ad-hoc; gap audit can surface where samples were too shallow even for the decision-support purpose

## When to use

- When the research target is a category of similar projects whose internal structure can be decomposed into functional parts (MCP servers, plugin marketplaces, CLI tools, web apps)
- When the consumer is a builder asking "what are my options for each part" — not a stat-watcher asking "what's most-adopted" (quantification follows)
- When the corpus is large enough that exhaustive evidence enumeration would inflate the synthesis past usefulness

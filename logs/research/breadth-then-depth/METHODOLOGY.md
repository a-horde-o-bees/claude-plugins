---
log-role: reference
---

# Methodology — Breadth-Then-Depth Consolidation

How a research subject's `_CONSOLIDATED_breadth-then-depth.md` is produced. Self-contained reference; companion phase files in this folder document each step's agent instructions.

## Goal

Identify the **functional parts** that come together to form a sample project, enumerate the **implementation paths** each part exhibits across the corpus, and capture qualitative descriptions of each path — what it is, when it's appropriate, what it constrains about other parts. The consolidated tree answers: *what are the parts of a sample project, what does each part do, what are the ways each can be implemented, and how do the parts connect to deliver the project's goals?*

Quantification is deferred to a final pass. The qualitative tree must converge (structure stable, paths well-described) before counting which paths are most-adopted.

The methodology corrects two failures observed in earlier consolidation approaches archived alongside subject-specific consolidateds:

- **Functional decomposition vs technical attributes.** Earlier methodology categorized by language and technology (Python / TypeScript / Docker). That conflates implementation choice with function — the same tool serves different purposes in different projects. Python is one option for the *server runtime* role; Docker fills *distribution channel*, *test stack*, and *deployment artifact* in different samples. The categorization tree must be organized by ROLE, not by tool. Tools are choices within roles
- **Qualitative consolidation vs evidence enumeration.** Earlier methodology required inline citations after every observation, inflating output 3-5× and treating consolidation as evidence-list reproduction. The consolidated should describe each implementation path qualitatively (one canonical description per path) — not enumerate which samples exemplify it. Provenance is dynamic via the `references` verb; inline citations are noise

## Inputs

- A corpus of per-sample files at `logs/research/{subject}/{subtopic}-samples/<entity>.md` — one file per entity in the research target list. Each sample carries observable facts about its entity at the granularity that supports functional decomposition. The methodology's job is to *abstract* those facts into functional parts and implementation paths
- CLI tooling: `sections`, `references`, `diff`, `check`, `quantify` verbs from `ocd-run log research`

The pre-Pass-1 phases (`01-target-selection`, `02-sample-population`) produce the corpus. Methodology consumers can run those phases or accept a corpus produced externally — the phases are documented for reproducibility, not because the rest of the methodology depends on them being agent-driven.

## Tree shape

The consolidated tree has three structural levels:

- **Top level — functional parts.** What does a sample project DO at this layer? Examples: server runtime, transport, authentication, capability surface, configuration delivery, distribution. Discovered from the corpus, not prescribed
- **Sub-level — implementation paths.** For each functional part, what alternatives does the corpus exhibit? Each distinct path a sample takes for that part is a sub-section. Paths are named by their *choice* (e.g., `stdio` not `JSON-RPC over stdin/stdout`), and the same choice across samples is one path, not many
- **Leaf — qualitative description.** Per path: what is this path, how is it configured, what does it constrain about other parts of the system, when is it appropriate. The description refines as more samples demonstrate the path — adding nuance, edge cases, or constraints not visible in the first sample

Cross-role linking: when a single tool fills multiple roles (Docker as distribution channel + test stack + deployment artifact), each role's section names the tool as one of its choices. The tool is not its own top-level branch.

No inline citations. Each branch's supporting samples come from `ocd-run log research references "Sample > <chain>"` — dynamic, always current, never inflates the document.

## Recognizing equivalent implementation buckets

The merger's hardest task: recognize when two partials describe the same implementation path under different names (e.g., one says "stdio transport," another says "JSON-RPC over stdin/stdout"). The dedup keys are:

- **Function** — what role does the path fill? (transport, auth, runtime, etc.)
- **Choice** — what specific implementation alternative is named? (stdio, OAuth 2.1, FastMCP, etc.)

Two chunks under the same (function, path) pair merge into one — even if their wording, sub-classification, or hierarchical placement differ across partials. Vocabulary normalization happens at merge time; the merger maintains a canonical-name map.

## Process

The methodology runs as a numbered sequence of phases. Each phase has a companion instruction file in this folder; the methodology document orchestrates them.

### Pre-consolidation: producing the corpus

**01 — Target selection** (`01-target-selection.md`). Define subject scope, enumerate candidates, stratify, sample to a target count. Output: an entity list. Diversity along the dimensions that matter for functional decomposition outranks comprehensiveness; sampling is stratified, not random.

**02 — Sample population** (`02-sample-population.md`). For each entity, capture observable facts about its components and what purpose each serves. Per-sample structure is loose — the research-objective checklist is *flat*, not nested, so per-sample shape doesn't anchor the consolidated. Capture distinguishing variance (the "would this distinguish?" test); skip implementation depth (covered ad-hoc post-methodology). Defer-mark `↗` anything the researcher can't tell from one entity's vantage point.

### Consolidation: building the tree

**03 — Gather** (`03-gather.md`, Pass 1a). Each agent reads a bin of samples in isolation and identifies functional parts the samples exhibit, the implementation choice each sample makes for each part, and a qualitative description per path. Output: one partial consolidated per bin.

**04 — Merge** (`04-merge.md`, Pass 1b). Single agent reads all partials, recognizes equivalent (function, path) pairs across vocabulary differences, merges descriptions, applies cross-role linking. Output: a unified canonical tree.

### Convergence: aligning samples and consolidated

**05 — Normalize** (`05-normalize.md`, Pass 2a). Each agent reads consolidated + its bin's samples. Rewrites each sample to mirror the consolidated's role tree (level-2 = roles, level-3 = paths), preserving all factual content. Collects proposed refinements (sharpenings, new paths, splits) in a refinement report. Does NOT modify the consolidated directly.

**06 — Reconcile** (`06-reconcile.md`, Pass 2b). Single agent reads all refinement reports, dedupes by cross-bin agreement, applies low-cost refinements liberally and high-cost refinements (new roles, splits) only with strong cross-bin support. Updates the consolidated in place.

Phases 05 + 06 form one normalize cycle. Convergence is detected when a cycle proposes few refinements (mostly sharpenings, no new roles, no bucket splits) and `references "Sample > <chain>"` queries resolve cleanly across the corpus. If still divergent, run another cycle. In practice 2-3 cycles suffice when the Pass 1 tree is well-formed.

> Convergence settles *what categories exist*. It does not settle *how those categories are described* — the per-bin lens prevents agents from comparing all 23 supporting samples for a popular path side-by-side. The depth pass below addresses that.

### Depth: cross-corpus refinement

**07 — Depth pass** (`07-depth.md`). The convergence loop works per-bin: each agent owns 8 whole files. No single agent sees all the supporting samples for any one path together. The depth pass inverts the lens — each agent owns ONE branching role and reads every supporting sample's content for every path under it via `references --show-content`.

What this surfaces that convergence cannot:

- **Description nuance** that emerges only when 20+ implementations of a path are stacked side-by-side
- **Mis-placed samples** — name-matching vs mechanism-matching errors visible only when path exemplars are inspected together
- **Multi-axis role structure** — roles whose paths run along orthogonal axes (e.g., Capability surface = scope × primitives × authoring × gating × auxiliary) the per-bin lens treats as a flat list
- **Cross-role boundary issues** — paths whose evidence sits in two roles (Container artifacts ↔ Distribution channel; Host integration ↔ Claude Code plugin)
- **Role-level prose gaps** — a derived axis like Multi-tenancy (deterministic from Transport × Auth) needs the relationship stated upfront

Per-role agents write refinement reports (`_depth-{role-slug}-refinements.md`); a reconciler integrates ~80% of findings into description text and role-level prose, deferring sample-level mis-placements to the corrective sweep.

The depth pass operates on already-captured sample information; it does NOT fetch new sample data. Implementation depth comes ad-hoc later, when the consolidated has served its decision-support purpose and the user implements their own version of a chosen path.

**08 — Corrective sweep** (`08-corrective-sweep.md`). The depth pass typically surfaces 20-40 sample-level mis-placements the depth reconciler defers (sample edits, not consolidated edits). One focused agent reads the depth refinement reports' "Mis-placed samples" sections and relocates affected sections in their owning samples — preserving content, only changing the parent heading chain. Targeted edit pass; not a full normalize.

After corrective sweep, sample chain keys align with the depth-refined tree.

### Quantification: mechanical adoption tables

**09 — Quantify** (`09-quantify.md`). Mechanical and deterministic — encoded as a script (`ocd-run log research quantify`) rather than agent judgment. The script:

- Walks the consolidated's role tree and identifies every branching point (any heading with 2+ direct heading children)
- For each branching point, counts samples exhibiting each child path via the `count_sections` chain-key index
- Computes coverage as `count / parent_total` (applicability-aware denominator — a 20-sample role doesn't dilute by 84 samples that don't have the role at all)
- Renders an adoption table under each branching point, wrapped in `<!-- adoption-table -->` ... `<!-- /adoption-table -->` sentinels
- Idempotent — re-running with updated sample counts replaces existing tables in place

Default mode prints tables to stdout for inspection; `--write` inserts them into the consolidated. Re-run any time samples or tree shape change — including after every gap-audit re-iteration cycle.

### Optional: re-iteration via gap audit

**10 — Gap audit** (`10-gap-audit.md`). **Opt-in.** Scans the converged, depth-refined, quantified consolidated for shallowness signals — places where understanding is shallow because samples don't carry enough detail. Produces a targeted re-research scope: specific sample × dimension pairs that would benefit from deeper investigation.

Gap audit doesn't fix anything itself. The user reviews the surfaced scope and decides whether to invest another methodology cycle to refine. If yes:

1. Audit's targeted scope routes back through `02-sample-population` (researchers re-investigate named dimensions for named samples)
2. Phases `03` through `08` re-run incrementally on the changed samples
3. Phase `09-quantify` re-runs (idempotent script)
4. Phase `10-gap-audit` re-runs to see if shallowness reduced

Re-iteration is opt-in because corpus mining has diminishing returns — at some point further loops trade tokens for marginal gains.

## Resource budgeting and dispatch

The phases that batch work across samples or roles (`03-gather`, `05-normalize`, `07-depth`) need resource budgeting so each spawn fits within agent context limits.

**Calibration spawn first.** The first spawn in a phase establishes the work-tok per byte ratio empirically. Subsequent spawns are sized using the trailing average. The ratio varies by subject and content density; do not hardcode it across runs.

**Per-spawn budget targets** (rough guidance; verify against the calibration spawn):

| Phase | Content per spawn | Target work-tok |
|-------|---------|------------------|
| 03-gather | ~40-50KB sample content per bin | ~100K |
| 05-normalize | consolidated (current) + ~40-50KB bin samples | ~150-300K |
| 07-depth | role section + per-role evidence pull (variable) | ~150-250K |

**Bin packing rule.** Group work to fill ~80-90% of budget per spawn, leaving headroom for tooling overhead and report generation. Use `references --size` and `sections --size` to budget content cost before pulling.

**Re-calibration trigger.** If trailing measurements diverge from the initial calibration spawn (e.g., bins 1-3 averaged 280K work-tok but bin 4 was assumed at 100K), re-bin the remaining work before continuing rather than continuing on stale estimates.

**Default to sequential dispatch.** For phases that batch work (gather, normalize, depth), default is one spawn at a time. Sequential:

- Eliminates rate-limit risk class entirely (parallel dispatch can fail when the platform throttles concurrent requests)
- Gives each spawn N+1 access to spawn N's measurement — actual context-aware iteration, not just calibration-then-projection
- Produces predictable wall-clock estimates

**Batch-parallel is opt-in.** When wall-clock matters more than calibration consistency and the platform's tolerance is known, batch-parallel (3-4 concurrent) is acceptable. Within a batch, the same trailing-window discipline applies — each batch is a calibration unit, not the whole phase. Larger concurrency widths increase rate-limit risk non-linearly.

The reconciler/merger phases (`04`, `06`, `08`, `09`) are inherently single-agent; this section doesn't apply to them.

## Commit cadence

Failure recovery (next section) relies on git as the checkpoint mechanism. To make selective recovery possible, commit between phases at well-defined boundaries:

- **After `02-sample-population` completes** — corpus is stable; subsequent phases consume it as input
- **After `04-merge` completes** — Pass 1 consolidated is stable; samples haven't yet been touched
- **After each `06-reconcile` cycle (when normalize cycles run iteratively)** — both samples (post-normalize) and consolidated (post-reconcile) are stable for that cycle
- **After `07-depth` reconciliation completes** — depth-refined consolidated is stable; sample mis-placements are about to be corrected
- **After `08-corrective-sweep` completes** — samples are aligned with the depth-refined tree
- **After `09-quantify` completes** — adoption tables are current
- **Before opting into a `10-gap-audit` re-iteration** — establishes the baseline the re-run can revert to if it goes wrong

These boundaries are where artifacts reach a stable state. Committing at each boundary keeps `git checkout --` viable as the reset primitive for the next phase's failure recovery.

For users not using git: snapshot the affected artifacts (`cp -r` before each phase) instead. The methodology depends on a checkpoint-and-revert discipline; git is the project's natural mechanism but not the only option.

## Failure recovery

When a phase agent fails mid-execution (rate limit, crash, timeout), the working tree is left partially modified — some samples or refinement reports may be partial, others untouched. Continuing from partial state pollutes downstream phases because subsequent agents can't tell partial-progress from complete work.

**Reset-then-retry discipline:**

1. **Identify the modified surface.** `git status -s` shows samples and reports the failed phase touched. Compare against expected outputs (one sample-rewrite per bin's samples for normalize; one refinement-report per bin for refinement-producing phases)
2. **Reset incomplete work to the last commit.** For samples: `git checkout -- <paths>` returns them to last-committed state. For partial refinement reports: `rm <_pass{N}-bin{M}-refinements.md>` deletes the stub-or-partial files. For the consolidated mid-edit by a reconciler: `git checkout -- <consolidated-path>`. **This step depends on the commit cadence above** — `git checkout` reverts to whatever was last committed, so phases must commit at their boundaries for this to land in the right place
3. **Re-dispatch with the lesson learned.** If the failure was rate-limit at parallelism N, drop to a smaller batch or sequential. If the failure was budget overrun, re-calibrate before the retry

**Don't retry on top of partial state.** A second pass over partially-rewritten samples treats the partial output as input, compounding errors. Always reset to a clean state before re-dispatching.

**Preserve completed work where possible.** If 8 of 13 bins succeeded before a rate-limit hit on bin 9, the 8 successful bins' samples and reports are valid output. Reset only the in-progress and not-started bins (selective `git checkout -- <specific-paths>`), and re-dispatch from bin 9 onward. Selective recovery is cheaper than full re-run when most work succeeded.

This discipline applied repeatedly during the mcp run. The default sequential dispatch (above) makes it less commonly needed, but failure modes still exist (timeouts, transient infrastructure issues).

## Tooling

| Verb | Purpose |
|------|---------|
| `sections [--subject N] [--count] [--size]` | Chain-key tree across samples; `--count` and `--size` add columns for adoption and byte size |
| `references "<chain>" [--subject N] [--count] [--size] [--show-content]` | List samples containing a section at the chain path. `--show-content` pulls each sample's section body — the depth pass uses this to inspect cross-corpus evidence per role. Replaces inline citations |
| `diff [--subject N] [--consolidated <path>]` | Diff sample heading trees against the running consolidated. Surfaces growth and pruning candidates. Use to scope each pass's work and detect convergence |
| `check <path>` | Verify a markdown file has no sibling-duplicate headings (structural correctness) |
| `quantify [--subject N] [--consolidated <path>] [--write]` | Compute adoption tables for branching points in the consolidated. Default prints to stdout; `--write` inserts in place. Idempotent via sentinel comments |

## Strengths

- **Categorization tracks what samples DO**, not what tools they use — survives technology shifts (a new Python framework is just another implementation path; the function "server runtime" stays stable)
- **Qualitative descriptions stay human-scannable** — readers descend to the depth they need; total document size is bounded by tree shape, not by per-sample evidence count
- **Provenance is always current** — `references` returns the supporting files for any branch at the moment of query; the consolidated never drifts out of sync with the corpus
- **Quantification deferred and deterministic** — adoption counts only appear when the qualitative tree is stable, encoded as a script that re-runs whenever the corpus or tree changes
- **Cross-role linking handles tool-multi-role reality** — Docker exists in the tree wherever it functions, not buried under "Container artifacts" alone
- **Two-lens design** — convergence (per-bin) settles *what categories exist*; depth pass (per-role) sharpens *how categories are described*. Both lenses are needed; one cannot do the other's work
- **Optional re-iteration via gap audit** — corpus shallowness is detectable post-quantify, and refinement is opt-in with a targeted scope rather than a corpus-wide re-crawl

## Limitations

- **Pass count is unbounded** — convergence may take many normalize cycles. Suited to research budgets that allow iteration; ill-suited to tight one-shot synthesis
- **Recognition of equivalent buckets is judgment-heavy** — the merger has to recognize that "Python with FastMCP" and "FastMCP-based Python server" are the same path. Vocabulary normalization is the methodology's hardest task and depends on agent capability
- **Functional decomposition has subjective edges** — what counts as "one part" vs "two related parts" is sometimes arguable. The methodology trusts the corpus to surface natural divisions, but early bins may settle on splits that later bins reveal as wrong; normalize cycles correct
- **Sequential dispatch is N× slower than parallel** — for a 13-bin phase, sequential is ~10× longer wall-clock. The methodology defaults to sequential because rate-limit failure is more expensive than wall-clock; users with platform headroom can opt into batch-parallel deliberately
- **Implementation depth is out of scope** — the methodology produces a decision-support tree, not implementation guidance. When the user picks a path and starts building, they research that path's implementation ad-hoc; gap audit can surface where samples were too shallow even for the decision-support purpose

## When to use

- When the research target is a category of similar projects whose internal structure can be decomposed into functional parts (e.g., MCP servers, plugin marketplaces, CLI tools, web apps)
- When the consumer of the synthesis is a builder asking "what are my options for each part" — not a stat-watcher asking "what's the most-adopted approach" (that comes later, mechanically)
- When the corpus is large enough that exhaustive evidence enumeration would inflate the synthesis past usefulness

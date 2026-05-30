# Assertion

A durable claim about platform behavior, captured with the probe that verifies it. One claim per file; the probe reconstitutes from the file alone, so a future session can re-verify against an evolved platform without re-deriving the methodology.

Distinct from plans (work to be done) and research logs (one-shot investigations). Assertions persist as long as the platform behavior they describe carries load.

## What qualifies

- A claim about Claude Code (or another platform we build on) whose truth must be re-verifiable across platform versions.
- A claim a skill-architecture decision rests on.
- A claim whose probe can be reconstituted from this file alone — no external state, no remembered context.

## What does not qualify

- Behaviors visible in the code we own — read the code.
- One-shot investigations with a single downstream consumer — decision or research log.
- Properties that hold by construction — they need no probe.

## Sections

Required sections appear in every file. Conditional sections appear only when applicable. Order is as listed.

### `## Verdict` (required)

What is provably true now. Opens with the parseable status word in bold: `**Confirmed.**`, `**Refuted.**`, `**Partial.**`, `**Pending.**`, or `**Superseded by <file>.**`. State scope inline (single-level, depth ≥ 2, all depths). Close with the last verifying run's date. No restatement elsewhere in the file.

### `## Canonical artifact` (conditional)

Present when the verdict sanctions a specific verbatim wording or pattern — closing release lines, `## Dependencies` phrasings, frontmatter conventions, command invocations. The artifact appears in a code block, copy-pasteable, with a short note on placement (surrounding markers, position in the host file). Absent when the verdict describes platform behavior without prescribing an authoring pattern.

### `## Why this matters` (required)

What downstream architecture depends on the verdict. One paragraph.

### `## Probe` (required)

The test apparatus: control skill, variants, fixtures. Bodies inline. No external referenced state.

### `## Baseline` (conditional)

What the variant runs are measured *against*. Required when the probe produces quantitative measurements that vary with harness or call count (token costs, latency, log-line counts). Omitted when the verdict is categorical (the field is honored, the file exists).

When the probe's measurement scales with call count, capture two reference points:

- **Single-call baseline** — one invocation of the apparatus with the probe-specific mechanism removed. Records per-invocation harness cost.
- **Multi-call baseline (N=<n>)** — N invocations under the same removal, where N matches the variant run count. Records cumulative harness cost. The delta between (single × N) and multi-call reveals first-call setup tax or other non-linear scaling worth noting.

When the probe's measurement is categorical (binary leak / no-leak, marker injection / absence), capture:

- **Null baseline** — the apparatus with its mechanism removed. Confirms the apparatus produces zero signal on its own.
- **Positive control** — the apparatus with a known-defective variant. Confirms the apparatus produces non-zero signal when it should. Often lives in a sibling assertion that gets referenced rather than re-run.

### `## Procedure` (required)

The orchestrator-side workflow. The orchestrator (a Bash loop, Python script, or the `/reassert` runner) shells each phase out to `claude -p --output-format json --no-session-persistence` and parses the JSON return for `usage` and `result`. Each `claude -p` invocation is a fresh Claude Code session with no carryover from prior phases — context contamination across phases is ruled out by construction.

Numbered steps for the orchestrator: setup, per-phase loop (file ops + `claude -p` dispatch + JSON parsing), aggregation into verification-log rows, cleanup.

#### Runner prompt

Self-contained text the orchestrator passes to each `claude -p` invocation. The runner does NOT read the assertion file; the prompt carries everything it needs.

Default — one shared prompt parameterized by per-phase variables (typically the invocation count N). When phases diverge in what the runner does, each phase subsection under `## Probe` or `## Baseline` carries its own `**Runner prompt:**` block instead.

### `## Detection method` (required)

How to interpret the probe's output. Tabular when several outcomes map to distinct verdicts.

### `## Depends on` (conditional)

Bullet list of prerequisite assertion files in the same directory. Omitted when the assertion is foundational.

### `## Extended by` / `## Superseded by` (conditional)

Pointers to other assertion files, kept distinct:

- **Extended by** — the verdict holds within its stated scope; another file widens scope.
- **Superseded by** — the verdict is wrong; another file replaces it.

Each appears as its own subsection when both apply.

### `## Side effects verified` (conditional)

Pointers to other assertion files confirming the verdict did not break adjacent properties.

### `## Variants deferred` (conditional)

Variants not pursued in this file, with pointers to where they were tested. Prevents re-exploration of rejected branches.

### `## Verification log` (required)

Append-only table of runs: date | conditions | result | tokens / tool uses | notes.

## Lifecycle

- After a test run: append a row to the verification log.
- After a platform update touching the subsystem: re-run; update the verdict if the result flips.
- When the verdict flips: change the bolded status word, rewrite the verdict, append the flipping run. Preserve the prior verdict only when historical context is load-bearing.
- When superseded: set the verdict to `**Superseded by <file>.**`. Leave the body for archaeology unless the assertion never landed.

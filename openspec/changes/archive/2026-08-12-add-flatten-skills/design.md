## Context

The suite's current composition mechanisms are all model-mediated or capped. Empirically established this session: skill `!` bash preprocessing inlines only a ~2KB preview (remainder spilled to a tool-results file; `BASH_MAX_OUTPUT_LENGTH` does not raise it), so runtime inlining cannot carry real dependency bodies (concise-prose alone is ~4.9KB). `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PROJECT_DIR}` are substituted throughout skill markdown (documented), which enables sibling path rewriting. Skill/folder naming constraints are undocumented — kebab-case is convention-by-example only. apply-over-queue's `flatten.py` expands `/name` references by regex and does not execute `!` lines. The suite installs as one unit (sibling folders) both live and in the plugin mirror; `~/.claude/skills/` is source of truth and this repo's `skills/` is generated.

Reference dummies showing the target file shapes: `tmp/skills/concise-prose/SKILL.md` (leaf — no machinery) and `tmp/skills/reauthor/SKILL.md` (materialized region).

## Goals / Non-Goals

**Goals:**

- Dependency text physically present in the SKILL.md the runtime loads; zero model-mediated hops.
- One composition mechanism suite-wide; `/skill-name` expansion retired.
- Freshness mechanically checkable (lint/sync gate), no incremental state to corrupt.
- Reliability precedence: an unreliable disclosure hop is worse than its token savings; token relief comes from mechanization (scripts), not from making the model navigate.

**Non-Goals:**

- Runtime/invocation-time expansion (dead: 2KB cap).
- Partial/incremental region rebuilds, per-unit shas, provenance (`via:`) tracking — full mechanical rebuild every time.
- Cross-suite dependencies (a dep outside the sibling-installed suite).
- Conditional dependency loading — a declared dep is always materialized.

## Decisions

- **Build-time materialization over runtime inlining** — the 2KB preprocessing cap makes runtime inlining unworkable; materialized regions ride the existing live-source → sync → mirror pipeline unchanged.
- **Two-layer file, marker-delimited** — source = everything outside the region plus the marker lines; generated = everything between. Declaration must live on the START line because region content is disposable and holds the transitive closure (units nobody directly declared).
- **JSON declaration on START** — stdlib parsing both ends, exact quoting (names with spaces), extensible object; rejected bespoke `deps:` token list (shlex) and per-unit DEPENDENCY marker lines (generated content masquerading as declaration).
- **Closure over sources, never over artifacts** — extraction strips a dep's own region, so no nesting, no duplication cascade; refresh is a pure function of source layers (idempotent, order-independent); check is recompute-and-byte-compare.
- **Cycle = error**, not skip.
- **Sibling path rewriting via `${CLAUDE_SKILL_DIR}`** — body-wide substitution is documented, so rewriting a dep's `${CLAUDE_SKILL_DIR}` to `${CLAUDE_SKILL_DIR}/../<dep>/` on transplant makes file-bearing skills valid dependencies; rejected the "self-contained deps only" restriction.
- **Colocate in skill-authoring** — the script travels with the discipline that mandates it (pattern set by `lint_skill.py`); rejected a separate /rebuild-skills skill (splits one discipline, spends a listing entry with no independent trigger).
- **Reauthor refocus rides this change** — new description ("invoked when fresh composition is the directive"), "When not to reauthor" dropped, Scope kept, concise-prose as first materialized dependency.

## Risks / Trade-offs

- **Unconditional inlining costs context** — skill-authoring's full discipline set is ~26KB materialized (~6.5k tokens/invocation) vs ~7KB today; /git's markdown corpus is ~91KB against a 4.9KB router. Mitigation: migrate prose procedure into scripts (the fully reliable mechanism), keep citation-grade material (e.g. DECISIONS.md) out of the invocation path, and re-scope which references are true dependencies versus citations.
- **`-->` in dependency bodies** breaks marker integrity — guarded by refresh/lint error; rare in practice.
- **Naming is undocumented upstream** — Claude Code doesn't specify folder-name constraints; JSON quoting absorbs whatever names exist, and the tool imposes none of its own.
- **Materialized copies exist on disk per host** — accepted as build output with a freshness invariant, the same status the mirror's `skills/` already has.
- **Doctrine updates trail the mechanism** — until procedure-authoring, /git, skill-authoring § layout, and file-decomposition are rewritten, the suite's own guidance contradicts the new rules; sequence the migration so lint flips to error only after the purge wave.

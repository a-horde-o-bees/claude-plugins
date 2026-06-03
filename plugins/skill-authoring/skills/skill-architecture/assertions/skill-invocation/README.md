# Skill invocation — calling a skill from within a skill

Consolidated results of the skill-calling investigation. Every figure here is
ground-truth: deduped `tool_use` counts and body-marker injection counts pulled from
captured `claude -p` streams, plus side-effect logs and per-inference `usage` — never
agent self-report. Detailed probes and the full verification log live in
[`repeat-invocation-load-cost.md`](repeat-invocation-load-cost.md).

## The law: dispatch is set by the target, not the verb

A reference resolves by what it points at, regardless of the verb in front of it:

- **`/skill-name` → Skill tool**, which **re-injects the full body on every call**.
  There is no harness cache; N calls cost N bodies. Measured identical for
  `skill: /x`, `apply: /x`, `Apply /x`, and `Call: /x` (3 injections for 3
  executions of a procedural skill).
- **file / section → Read-and-follow**, which is **load-once**: `Call: Section` adds
  zero injections; `Call: \`_file.md\`` reads the file once for N executions.

So "load once, reuse" is not a platform default — the Skill tool always re-injects.
It is engineered by *not calling the tool on repeats*: either route to a file/section,
or override the agent's default with a stated convention (see redefinition, below).

## Complete measured matrix

Procedural target (`/proc-x`, a bash side effect), referenced 3× unless noted:

| Construct | Tool | Body injections | Executions | Load-once? |
|---|---|---|---|---|
| `skill: /x` | Skill | 3 | 3 | ❌ |
| `apply: /x` (prefix) | Skill | 3 | 3 | ❌ (== `skill:`) |
| `Apply /x` (prose) | Skill | 3 | 3 | ❌ (== `skill:`) |
| `Call: /x` (skill target) | Skill | 3 | 3 | ❌ (== `skill:`) |
| `skill: /x (if not already in context)` | Skill | 1 | **1** | ⚠️ action lost |
| `skill: /x — load once if not in context; act every call` | Skill | **1** | 3 | ✅ (variant C) |
| `Call: \`_file.md\`` | Read | **1 read** | 3 | ✅ |
| `Call: Section` (in-document) | none | **0** | 3 | ✅ (cheapest) |

Declarative target (a *rule* applied to the agent's own output, not a tool action),
referenced 3×: `Apply /x` loads **once** and applies the rule to all 3 outputs. The
load-once of a prose `Apply` holds **only** for declarative guidance — when the skill
must *execute* (procedural side effects), "applying" means invoking, so it re-injects.

## Cost: window vs. tokens

Each re-injection is a fresh `cache_creation` ≈ body size — confirmed per-inference,
both within one turn and across interactive turns; the context window grows by a body
per call and is **never deduped**. Prompt caching cheapens only the *re-read* of an
already-sent prefix (`cache_read`), not the injection: identical repeated `claude -p`
calls hold `cache_creation + cache_read` constant while the ratio shifts create→read
after the first. So repeated invocation is cheap in *quota* (cached replay) but real in
*window occupancy*. The git-recursion cost (`/git-commit` re-injected per submodule) is
genuine window cost; caching does not relieve it.

## Redefining `skill:` — feasible, pending a design call

The variant-C semantics can be lifted out of each call site into a **definition**: a
convention stating `skill: /x` means "load once if not in context; act every call"
makes bare `skill: /x` ×3 behave load-once (1 injection, 3 executions). Confirmed both
at parent-body distance and at **PFN-spec distance** — buried as one rule among 25 in a
~2,769-token spec loaded once, bare `skill:` still loaded once (3/3 runs); a same-size
neutral-spec control reverted to 3 injections, isolating the redefinition as the cause.

This opens a design fork, **not yet decided**:

- **A — keep `skill:` = re-inject (current).** Fresh deterministic invocation each call.
  Load-once via `Call:` (file/section) or the opt-in variant-C clause. Small, additive
  PFN edit. Safe for mutations.
- **B — redefine `skill:` = load-once-act-every.** Cheaper by default, but flips the
  global default onto the agent-re-execution path (re-running a body from context),
  which is riskier for mutations like `git-commit` per submodule, and rewrites the
  meaning of every existing `skill:`. Needs a "force-fresh" escape hatch.

## Injection paths (how a body reaches context)

| Path | Trigger | Lands as | Gated by |
|---|---|---|---|
| Slash-expansion | `/x` as sole/leading user content | pasted into the user message | harness — unconditional |
| Agent-inference | `/x` embedded in prose ("run /x") | tool_result after a Skill call | agent judgment |
| Skill-in-skill | `skill: /x` in a body | tool_result after a Skill call | agent judgment |
| Inline prose mention | `Apply /x.` (declarative) | tool_result, ≤1× | agent judgment — lazy load-once |

Slash-expansion is harness-level and only fires for a leading slash command; mid-prose
`/x` is not expanded — the agent infers and calls the Skill tool. `## Dependencies`
bullets are documentary (zero-load); the operative load happens at point-of-use or via
always-on.

## Lineage

Supersedes the measurement intent of quarantined `skill-runtime/skill-caching.md` and
`dep-test-iterations.md`, re-run under ground-truth stream parsing. The git-plugin
*application* of these findings (per-checkpoint cost model, pr-status/doctor dedups,
writing-skill load behavior) is an audit tracked separately, not here.

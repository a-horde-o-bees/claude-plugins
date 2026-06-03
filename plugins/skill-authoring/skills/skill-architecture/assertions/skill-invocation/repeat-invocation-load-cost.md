---
status: confirmed
last-verified: 2026-06-02
---

# Assertion: The Skill tool re-injects the full body on every call; body-once-action-many needs an explicit load/act decoupling

**Confirmed.** Every Skill-tool invocation re-injects the full `SKILL.md` body into
context — whether the calls are embedded as `skill:` steps in a parent skill body or
issued by a top-level natural-language instruction. There is no harness-level cache:
three calls cost three bodies. Consequently, invoking a skill from within a skill
such that its body is **read once but its action is reused as needed** is achievable
only when the invocation **decouples load from action** — instructing the agent to
load the body once (if not already in context) but perform the action on every call.
The agent then loads once and re-performs from context without re-calling the tool.
A bare idempotence cue ("if not already in context") with no act-every-call clause
suppresses the action as well as the load — correct for passive content reuse, wrong
for repeated action. Verified at N=5 for the canonical form. Re-injection holds
across **separate interactive turns**, not just within one — repeated bodies grow the
context window monotonically and are never deduped; prompt caching makes the *repeat
token cost* cheap (`cache_read`) but does nothing for the *window* cost. Last verified
2026-06-02.

## Canonical artifact

For a sub-skill whose **action must repeat** while its **body loads once**:

```
1. skill: /x — load its body only if not already in context; perform its action on every call
```

For repeated action whose logic you control (need not be a separate skill), the
cheaper form is an in-document sub-routine — zero re-injection:

```
1. Call: Perform-Action
2. Call: Perform-Action

## Perform-Action

1. <the action step(s)>
2. Return to caller
```

**Dispatch is set by the target, not the verb.** A `/skill-name` target routes to the
Skill tool — which **re-injects the full body on every call** — under *any* verb:
`skill: /x`, `apply: /x`, `Apply /x`, and even `Call: /x` all measured identically (3
injections for 3 executions of a procedural skill). A **file/section** target routes to
Read-and-follow, which is **load-once**: `Call: Section` adds zero injections,
`Call: \`_component.md\`` reads the file **once** for N executions (corrects an earlier
"re-reads" reading — the extra Read in those runs was result-reporting, not a re-read).
So load-once *procedural* reuse comes only from `Call:` aimed at a file/section, or from
the variant-C decoupling clause on a `skill:` — never from changing the verb in front of
a `/skill`.

## Why this matters

`/git-checkpoint` and the submodule-recursive leaves (`/git-commit`, `/git-push`)
invoke sizable PFN bodies repeatedly within one run. Under the default re-injection
behavior, every repeat invocation pays the full body again. The decoupling clause is
the only way to keep a repeated *cross-skill* action at one body load; the in-document
`Call:` section is the way when the repeated logic can live in the host body. This
assertion is what PFN's `skill:` definition should prescribe for repeated invocation.

## Injection mechanisms

A skill body reaches context by one of three paths, and they are not interchangeable:

| Path | Trigger | Where the body lands | Gated by |
|---|---|---|---|
| **Slash-expansion** | a slash command as the **sole/leading** content of a user turn (`/x` alone) | pasted into the **user message** (with `<command-name>` tags) | harness — unconditional, always full body |
| **Agent-inference** | the command **embedded in prose** ("run /x") | a **tool_result** after the agent calls the Skill tool | agent judgment — agent decides whether to invoke |
| **Skill-in-skill** | `skill: /x` in a skill body | a **tool_result** after the agent calls the Skill tool | agent judgment — same as agent-inference |
| **Inline prose mention** | `Apply /x.` in a step (not a `skill:` step) | a tool_result; **declarative**: ≤1× per skill per turn — **procedural**: every mention | agent judgment + content type — see below |

**The behavior splits on content type — declarative loads once, procedural
re-injects.** Two probes, 2026-06-02:

- **Declarative** (`/apply-target`: a body-only *rule* applied to the agent's own
  drafting). null: 0 loads. single `Apply`: 1 load. triple `Apply`: **1 load**, the
  rule applied to **all three** lines. → **load-once, reuse-many.**
- **Procedural** (`/proc-x`: a body that *executes* a bash side effect per event).
  `Apply /x` ×3 and `apply: /x` ×3 both gave **3 loads / 3 executions — identical to
  `skill: /x`.** → **re-injects every mention.**

So a soft prose reference is load-once **only when "applying" means reusing guidance
from context** (declarative). When `/x` is procedural, "applying" *means executing*,
which the agent does by invoking the Skill tool each time → re-injection. The prefix
form `apply: /x` is not a distinct mechanism: it behaved exactly like `skill: /x`. For
load-once *procedural* reuse the levers are `Call:` (section = 0 injections, file =
read-once) or the variant-C decoupling clause — **not** `Apply`/`apply:`.

The earlier writing-skill run (`Apply /concise-prose, /description-authoring, /honesty`
→ 0 loads) is the *skip* case, not a "never loads": the agent judged those familiar
skills' gist already known (from training + the one-line registry description) and
didn't fetch the body. A skill with non-obvious body content (`/apply-target`) **is**
fetched — once. Net for the git skills: the inline-`Apply` writing references are
**well-formed load-once-on-demand**, not a gap; cost is zero (≤1 load per skill per
turn, even in recursion), and the body is fetched when genuinely needed. (The separate
`## Dependencies` *bullet* remains documentary/zero-load, but the inline `Apply` is the
operative loader, so the bullet is redundant, not load-bearing.)

Confirmed 2026-06-02: a sole `/ctx-probe` turn arrived pre-expanded (full body in the
user message); the same command mid-sentence ("please run /ctx-probe") arrived as plain
text with **no body and no `<command-name>` tag**, and the body appeared only as a
tool_result after the agent's Skill call. **Slash-expansion is a red herring for
skill-in-skill design** — `skill: /x` is the agent-inference path, where agent judgment
is the only lever (which is why the variant-C decoupling clause can work at all).

## Cost vs. context-window — the two are different

Re-injection has two distinct costs, and the cache splits them:

- **Context-window occupancy** grows by one full body per invocation, permanently —
  nothing dedupes. Confirmed across **separate interactive turns** (three sole
  `/ctx-probe` calls): `cache_read` climbed monotonically (~199k → ~212k), never
  dropping; repeated *identical* bodies are not collapsed.
- **Token/quota cost** splits sharply: prompt caching cheapens **re-reading an
  already-sent prefix** (`cache_read`), but does **nothing for the injection itself**.
  Each fresh body injection is `cache_creation` ≈ body-size — including repeated
  injections of the *same* body within one run (measured per-inference: each of three
  in-turn injections produced its own `cache_creation` bump of ~800–1000 tokens; none
  was served from cache). The cache is **prefix-positional, not content-dedup**:
  identical bodies at different positions are each created once. `cache_creation +
  cache_read` holds ~constant for *identical-prefix* content while the ratio shifts
  creation→read after the first occurrence — the "re-created vs replayed" fingerprint.
  The summed `volume` metric (used for the variant matrix above) is deliberately
  cache-invariant, so it counts every re-injection at full weight: right for
  cross-variant comparison, and — now confirmed — not an overstatement of the *repeat
  injection* cost, since each injection genuinely pays `cache_creation`. What caching
  saves is only the prefix re-read, never the duplicate body.

**Scope of cache savings (measured):** `cache_read` relief applies to re-reading a
shared prefix — across interactive turns, across identical independent `claude -p`
calls (no session continuity needed; content/prefix-keyed within the ~5-min TTL), and
across inferences within one turn. It does **not** apply to the repeated *injection* of
a body — within a single run, N injections of the same skill cost N × `cache_creation`.
This is the git-recursion case (`/git-commit --cwd sub1…subN`): each submodule pays a
fresh body. The decoupling clause / `Call:` section is what avoids the N−1 extra
creations.

## Probe

Control child `/inv-child`: appends one `ACTION` line to `/tmp/inv-action.log` per
execution; body carries sentinel `INVCHILD-MARKER-5521-BODY-SENTINEL` so each
re-injection is countable. Parent `/inv-parent`: body swapped per variant. All
variants drive three executions.

| Variant | Parent `## Process` (3 steps) |
|---|---|
| **direct** | top-level NL prompt: "Invoke /inv-child three times via the Skill tool" (no parent) |
| **direct-cond** | top-level NL prompt: "for each of [alpha, beta, gamma], invoke /inv-child once" (no parent) |
| **B** | `skill: /inv-child (if not already in context)` |
| **C** | `skill: /inv-child — load its body only if not already in context; perform its action on every call` |
| **E** | `Call: Perform-Action` (action is an in-document section) |
| **F** | `Call: \`_action.md\`` (action is a component file) |

## Baseline

- **Re-injection baseline (positive control):** `direct` — bare repeat invocation.
  Measures the full per-call body cost the variants are reducing against.
- **Null:** a single invocation (one body, one action) — the floor.

## Procedure

A Python driver shells each phase to `claude -p --output-format stream-json
--no-session-persistence` via [`../runner.py`](../runner.py), each a fresh session
(no cross-phase contamination), with `--add-dir /tmp` for the scratch log. Per run it
parses the captured stream for ground-truth signals — no agent self-report. N-sampled
per variant to expose nondeterminism.

### Runner prompts

- Parent variants (B/C/E/F): "Invoke /inv-parent via the Skill tool and follow its
  steps exactly. Then report the contents of /tmp/inv-action.log."
- `direct`: "Invoke /inv-child three times in sequence via the Skill tool. Then
  report /tmp/inv-action.log."
- `direct-cond`: "I have three items: alpha, beta, gamma. For each, invoke /inv-child
  once via the Skill tool. Then report /tmp/inv-action.log."

## Detection method

| Signal | Source | Reads as |
|---|---|---|
| **body injections** | count of `user` `text` blocks containing the child sentinel | how many times the full body entered context |
| **child Skill calls** | deduped `tool_use` blocks naming Skill+inv-child | how many times the tool fired |
| **Read calls** | `tool_use` count for Read | component-file re-reads (F) |
| **actions** | lines in `/tmp/inv-action.log` | how many times the action actually ran (side effect) |
| **volume** | `usage` cache-invariant token total | cost proxy |

Verdict on `body injections` vs `actions`: load-once-act-many = injections 1, actions 3.

## Supersedes

- Measurement intent of quarantined `../quarantine/skill-runtime/skill-caching.md`
  (H-A re-injection) and `dep-test-iterations.md` — re-run here under ground-truth
  stream parsing instead of agent self-report. Quarantine consulted for direction,
  not trusted for outcomes.

## Verification log

| Date | Variant | N | body injections | actions | volume (median) | Result |
|---|---|---|---|---|---|---|
| 2026-06-02 | direct | 2 | 3, 3 | 3, 3 | 224k | Re-injects every call — no cache outside a parent skill |
| 2026-06-02 | B (idempotence cue only) | 2 | 1, 1 | 1, 1 | 142k | Load once but **action lost** — cue gates the whole call |
| 2026-06-02 | C (decoupled load/act) | 5 | 1×5 | 3×5 | 194k | **Load once + act every call — canonical** |
| 2026-06-02 | E (in-document `Call:` section) | 2 | 0, 0 | 3, 3 | 165k | Zero re-injection; action in host body |
| 2026-06-02 | F (`Call: _component.md`) | 2 | 0, 0 | 3, 3 | 193k | Reads the component **once** for 3 executions (the 2nd Read was result-reporting) — load-once procedural [corrected from an earlier "re-reads" reading] |
| 2026-06-02 | direct-cond (NL per-item) | 3 | 3×3 | 3×3 | 225k | Identical to `direct` — NL-driven repeat calls re-inject too; no "outside a skill" cache |

### Mechanism + cache log (separate signals)

| Date | Test | Result |
|---|---|---|
| 2026-06-02 | Injection path — sole `/ctx-probe` vs mid-prompt "run /ctx-probe" (interactive) | Sole = slash-expansion (full body in user message, `<command-name>` tag). Mid-prompt = no expansion (plain text), body arrives as tool_result via agent's Skill call. `skill:` = the agent-inference path. |
| 2026-06-02 | Interactive separate-turn re-injection — 3 sole `/ctx-probe` turns | Context-window grows per call: `cache_read` ~199k → ~212k monotone, never drops. Identical bodies not deduped. |
| 2026-06-02 | Cache-split — 3 identical `claude -p` calls (skill prompt), back-to-back | `cache_create`+`cache_read` constant across calls 1–2 (49,768 each); ratio shifts create→read 21.4% → 12.4% → 2.1%. Body re-injected into window every call but replayed from cache (cheap) on repeats. Confirms the ratio-shift fingerprint; `volume`'s summed metric hides it. |
| 2026-06-02 | Within-turn injection split — agent calls `/inv-child` 3× in ONE turn; per-inference usage (N=2) | Each of the 3 in-turn body injections is a fresh `cache_creation` bump (~800–1000 tok ≈ body), never `cache_read`. `cache_read` grows monotonically (prefix replay). Caching is prefix-positional, not content-dedup: N injections = N × create. This is the git-recursion cost; no free dedup. |
| 2026-06-02 | Inline `Apply /x` — writing skills (concise-prose/description-authoring/honesty), N=2 | 0 loads — but this is the *skip* case: agent judged the familiar skills' gist known from the registry description, didn't fetch bodies. Not a universal "never loads" (see next row). |
| 2026-06-02 | Inline `Apply /x` — fresh `/apply-target` with body-only token, null/single/triple, N=2 | null: 0 loads / token absent. single: 1 load / token applied. **triple: 1 load / token applied to all 3 lines.** `Apply /x` = lazy load-once-reuse for **declarative** content. |
| 2026-06-02 | Procedural matrix — `/proc-x` (bash side effect), 3 events, 5 constructs, N=2 | `skill:` 3 inj/3 exec; **`Apply /x` 3 inj/3 exec; `apply: /x` 3 inj/3 exec** (both == `skill:`); `Call: _file` 1 read/3 exec; `Call: Section` 0/3. → `Apply`/`apply:` re-inject for procedural; only `Call:` is load-once procedural. `apply:` is not a distinct mechanism from `skill:`. |
| 2026-06-02 | `Call:` pointed at a **skill** — `Call: /proc-x` (prefix) and `Call /proc-x` (prose), N=2 | Both: **3 Skill calls / 3 injections / 0 SKILL.md reads** — identical to `skill:`. Confirms **dispatch is set by the target, not the verb**: a `/skill` target routes to the Skill tool (re-inject) under any verb; only a file/section target routes to Read-and-follow (load-once). |
| 2026-06-02 | Lift variant-C into a **definition** — convention block redefining `skill:` at the parent-body top, then bare `skill: /proc-x` ×3, N=3 | **1 load / 1 injection / 3 executions, all 3 runs** — identical to the inline clause. A stated redefinition of `skill:` overrides the default re-injection (agent re-executes from context). |
| 2026-06-02 | Redefinition at **PFN-spec distance** — `skill:` redefinition buried as rule 13/25 in a ~2,769-tok spec loaded at step 1, then bare `skill: /proc-x` ×3; redef vs same-size neutral control, N=3 | **redef: 1 load / 3 exec (3/3). control: 3 loads / 3 exec (3/3).** Redefinition survives distance and is reliable; the neutral control isolates the redefinition as the cause. Option B (redefine `skill:`) is feasible. Remaining concern is *desirability* — it flips the global default to agent-re-execution, riskier for mutations. |
| 2026-06-03 | Load count is set by the skill's **nature**, not the verb — `skill: /ref-rule` ×3 vs `Apply /ref-rule` ×3, where `/ref-rule` is a *reference* skill (a rule applied to output), N=2 | **Both 1 load.** A reference skill loads once under `skill:` *and* `Apply`; a procedural skill (`/proc-x`) re-injects under both. So the read count tracks reference-vs-procedural + agent judgment, not the verb. Confirms verb-independence and removes any need for a distinct "Apply" construct. |

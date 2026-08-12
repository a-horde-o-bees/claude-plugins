# DECISIONS

Choices behind how apply-over-queue transports its fan-out, resolves an operation file's variables, and keeps the shared prefix cached — each recorded against the alternatives it was taken over.

## The fan-out stays on sequential `claude -p`; baseline context shrinks via CLI flags

**Decision.** Repeated uniform operations run as sequential `claude -p` spawns with automatic prompt caching, minimizing per-spawn baseline with CLI flags rather than migrating to the Agent SDK or the Message Batches API.

**Forces.** The flattened payload already eliminates runtime skill dispatch, so spawns need no skill listing, CLAUDE.md, MCP, or auto-memory — baseline weight is removable without changing transport. Verified against the docs 2026-07-24: neither the CLI nor the SDK exposes `cache_control` breakpoints, so caching is automatic and opaque in both and the SDK offers no additional control over where the cached prefix ends; its genuine advantage, programmatic baseline minimization, is matched by `claude -p`'s baseline flags (`--safe-mode`, `--tools`, `--setting-sources`, and `--bare` — the last requiring API-key auth rather than subscription auth).

**Rejected.**

- *Agent SDK migration*: its baseline-context options duplicate what the CLI flags provide, it adds an operational layer, and it does not return control of the cache boundary — the one axis that would have justified the move.
- *Raw Messages API*: the only transport with explicit `cache_control` placement, but it abandons the harness — tools, permissions, staged-workspace review — that the fan-out's review gate depends on.
- *Message Batches API*: a 50% discount at 100+-target scale with async completion; the suite's queues are an order of magnitude smaller and the review gate is interactive.

## Variable resolution happens at normalize time, in the orchestrator

**Decision.** `${CLAUDE_SKILL_DIR}` in an operation file is resolved to a literal by the orchestrator during normalization — the step that already reads and rewrites the file, and the last point where the binding (the directory the instruction was read from) exists. `flatten.py` backstops mechanically: it substitutes the variable in every skill body it inlines, resolving each unit's folder itself, and refuses to emit a payload where the variable survives. Normalization itself is inlined in SKILL.md rather than living in a separate `Call:` file.

**Forces.** Cold spawns read the payload with no dispatcher, so an unresolved variable expands to an empty string in their shell or invites a guessed path; operation files that hardcode machine-literal paths instead drift and leak into published copies. By flatten time the operation file is a temp copy whose path no longer names its owning skill, so only the orchestrator holds the binding — and it holds it exactly at the normalize step. The normalize sub-routine had one consumer and executed unconditionally on every invocation, so a separate file bought no context saving and cost a parameter-binding indirection.

**Rejected.**

- *A config file of variable values beside the scripts*: stores values that are either derivable at run time (skill dirs — a second drift channel) or owned by another skill's config (per-user state — a second source of truth).
- *A `--operation-skill-dir` flag threading provenance through the driver*: adds a caller obligation to carry a fact the orchestrator already applies earlier and more cheaply as text.
- *Home-anchored literals (`~/...`) in operation files*: portable across users but wrong for non-standard install locations, and the files must apologize for breaking the suite's variable convention.

## Keepalives assume the 5-minute cache TTL

**Decision.** The warmup and keepalive machinery targets the default 5-minute TTL; the 1-hour TTL (`ENABLE_PROMPT_CACHING_1H=1`, 2× write cost) stays unused.

**Forces.** Keepalive pings are near-free prefix reads, while the 1-hour tier doubles the payload's write cost to buy headroom the pings already provide.

**Rejected.**

- *1-hour TTL instead of keepalives*: pays 2× on every payload write to eliminate a mechanism that costs about one prefix read per interval and already survives a missed ping.

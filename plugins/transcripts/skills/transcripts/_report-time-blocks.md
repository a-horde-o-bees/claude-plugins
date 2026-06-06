# Time Blocks Report

Per-day engaged time across topic-coalesced blocks, filtered to a project's billable topics — suitable for client time-charging or per-project rollups. Blocks are **persisted** (`blocks` / `block_exchanges`): coalescing happens once and is reused, so each run only groups exchanges not already in a block.

## Variables

- {format-args} — All args after `time-blocks`. Decompose into:
    - {scope-args} — scope + dates: (`--project X` | `--all-projects` | `--session Y`) `[--from D --to D]`. Passed to `sessions` and `block-list`. Empty scope is rejected by the CLI.
    - {billable} — value of `--billable-topics a,b,c` (the project's billable policy); empty bills nothing.
    - {fill} — value of `--fill` (`off` default | `on`).

## Concepts

A **block** groups exchanges sharing a topic or focus. Membership may **span sessions** — a block is the right grouping whenever its summary holds across the members, regardless of which session each came from. One exchange belongs to at most one block.

Each block carries:

- **Summary description** — the specific unified objective of its exchanges; broader than the per-exchange descriptions, written per /description-authoring.
- **Topic** — a deliberately broader label shared across blocks (many summaries → one topic, e.g. "OAuth writeback", "stale-token re-auth" → `qbo-oauth`). Topics are the unit of billability.

**Billability** is a per-project policy over topics, supplied via `--billable-topics`. The skill stores no billability; the report includes only blocks whose topic is in the billable set. The project owns and passes its list.

**Engaged time** is computed by the CLI (`block-list`), not by hand:

- `combined_s` = `user_s` + `agent_s` per block — the billing basis.
- **`--fill off`** (default): bills only measured compose time — `user_s` counts only when observed (≤ threshold and > 0).
- **`--fill on`**: credits each *unobserved* compose pause (`user_s` NULL or 0) one `avg_user_time_s`, estimating true human engagement.

**Block time** = sum of `combined_s` across the block's resolved members. Members whose session was pruned from `~/.claude/projects/` don't resolve and contribute zero — tolerated, not an error.

## Process

1. Resolve project scope label:
    1. If `--project X` in {format-args}: {project} = X
    2. Else if `--all-projects`: {project} = "all projects"
    3. Else if `--session Y`: {project} = the session's project

2. List existing blocks in scope, to avoid re-coalescing:
    - bash: `cd <THIS-FILE-DIR> && python3 -m scripts block-list {scope-args}`
    - {blocked} = set of `session:exchange` across all returned blocks' `members`

3. List sessions in scope:
    - bash: `cd <THIS-FILE-DIR> && python3 -m scripts sessions {scope-args} --show timeframes`
    - {sessions} = response array, sorted ascending by `first_ts`
    - Assign each {session} a 1-based index in chronological order; exchanges from session N render as `S{N}E{m}`.

4. For each {session} in {sessions}, author any missing descriptions:
    1. Pull exchange detail:
        - bash: `cd <THIS-FILE-DIR> && python3 -m scripts exchanges --session {session} --show messages metrics timeframes`
    2. {descriptions} = empty map
    3. For each {exchange} whose `description` is null:
        1. Read its user + assistant messages (expand any `[[ref:hash]]` only if the body matters: re-run with `--expand-refs all`)
        2. Compose a description per /description-authoring
        3. Set `{descriptions}[{exchange.exchange}] = {description}`
    4. If {descriptions} non-empty: `python3 -m scripts descriptions-set {session} '<json>'`

5. Coalesce **unblocked** exchanges into new blocks (skip any `session:exchange` in {blocked}):
    1. Group exchanges sharing a topic or focus into a block — across sessions where the focus recurs (e.g. an OAuth thread spanning four sessions is one block), and allowing non-contiguous members when a tangent interrupts.
    2. Compose a block summary per /description-authoring.
    3. Assign a topic — reuse an existing topic string verbatim when the focus matches one (consistency beats novelty; check {blocked} blocks' topics and `block-list --topics`), else coin a short kebab phrase.

6. Present proposed blocks for user review:
    1. Render a proposal table — Exchanges, Topic, Summary description, Billable? (topic ∈ {billable-topics})
    2. Ask the user to approve or adjust (Q# format, lettered options)
    3. On adjustment: re-group / re-topic / re-word as directed, then re-present
    4. Once approved, proceed

7. Persist approved blocks:
    - For each new block: `python3 -m scripts block-create --topic {topic} --summary {summary} --exchanges {session}:{e},...`
    - Members use full session ids and may span sessions: `--exchanges <s1>:1-3,<s2>:2`

8. Read back persisted blocks with billable filter + fill, for rendering:
    - bash: `cd <THIS-FILE-DIR> && python3 -m scripts block-list {scope-args} --billable-topics {billable} --fill {off|on}`
    - {billable-blocks} = returned `blocks` (already restricted to billable topics; `combined_s`/`user_s`/`agent_s` already computed under the chosen fill)
    - A block belongs to the **day** of its earliest member's `exchange_start`.

9. Render the two-tier report:
    1. **Top-level, per day (the bill — Combined):**
        - Skip any day with no billable blocks — produce no file for it.
        - Title: `# Time Block Report — {project}`
        - Per day, chronological: `## YYYY-MM-DD`, then a table — `Exchanges`, `Topic`, `Summary Description`, `Time` (Combined).
        - `## Summary`: `Date`, `Billable` (Combined/day), final `**Total**` row.
    2. **`detail/` per day (User/Agent split, honours `--fill`):**
        - Same rows; columns `Exchanges`, `Topic`, `Summary Description`, `User`, `Agent`, `Combined`.
        - Per-day and total roll-ups for each of User / Agent / Combined.
    3. **Span roll-up:** one summary across the full date span — total Combined, and User/Agent in the detail tier.

10. Return to caller.

## Format Conventions

- **Exchange refs** — `S{n}E{m}`; n is the 1-based session index in report scope, m the exchange number. A block spanning sessions lists each session's members: `S1E1-E3, S4E2`.
- **Range form** — Consecutive same-session exchanges collapse to `S2E1-E5`; non-contiguous list comma-separated.
- **Time format** — Sub-hour `Xm` (`7m`); hour-or-more `Xh Ym` (`2h 57m`); zero `0m`.
- **Time rounding** — Ceiling per block (the billable unit), from the block's `combined_s`. Day and span totals sum rounded block minutes — not a re-ceiling of summed seconds.
- **Billable** — A block renders only if its topic ∈ {billable-topics}. The top tier is the client-facing bill; `detail/` is the auditable split.

## Format Example

Top-level `2026-04-30.md`:

```
# Time Block Report — monaco

## 2026-04-30

| Exchanges | Topic | Summary Description | Time |
|---|---|---|---:|
| S2E1-E2 | qbo-oauth | OAuth writeback token refresh | 7m |
| S2E4-E10, S5E3 | inventory-sync | Stock reconcile across the cutover | 58m |

## Summary

| Date | Billable |
|---|---:|
| 2026-04-30 | 1h 5m |
| **Total** | **1h 5m** |
```

`detail/2026-04-30.md` (same blocks, split, `--fill` honoured):

```
| Exchanges | Topic | Summary Description | User | Agent | Combined |
|---|---|---|---:|---:|---:|
| S2E1-E2 | qbo-oauth | OAuth writeback token refresh | 3m | 4m | 7m |
| S2E4-E10, S5E3 | inventory-sync | Stock reconcile across the cutover | 22m | 36m | 58m |
```

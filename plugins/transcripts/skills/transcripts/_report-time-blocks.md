# Time Blocks Report

Per-day time allocation across topic-coalesced exchange groups within the report's target project, with boolean in-scope tagging suitable for client time-charging or per-project rollups.

## Variables

- {format-args} — Filter args passed through to scope queries (`--project X`, `--from D`, `--to D`); empty defaults to current project, all dates

## Concepts

A **block** groups exchanges from a single session that share a topic or focus. Blocks may span non-contiguous exchanges if an unrelated tangent interrupted the focus (e.g., `S2E1, S2E4-E12, S2E15`).

Each block carries a **summary description** — captures the unified objective of the contained exchanges; broader than the per-exchange descriptions that compose it. Written per /description-authoring.

Each block is tagged **in-scope** or **out-of-scope** of the report's target project — boolean classification, not a multi-category taxonomy. Out-of-scope captures sibling-project work, tangents, and meta-explorations that incidentally appeared in the project's session but are not directly related.

**Engaged time** per exchange:

```
engaged_s = COALESCE(user_s, avg_user_time_s) + agent_s
```

`user_s` is the compose pause that produced the exchange — NULL when above the threshold (default 15 min) or unobservable. The `avg_user_time_s` derived stat (from `settings`) is the mean of observable compose pauses; substituting it for NULL `user_s` keeps unmeasurable lead times from collapsing to zero.

**Block time** = sum of `engaged_s` across exchanges in the block. Span math (latest-end minus earliest-start) is *not* used — it would over-count idle gaps within a block.

## Process

1. Resolve project scope label:
    1. If `--project X` in {format-args}: {project} = X
    2. Else if `--all-projects` in {format-args}: {project} = "all projects"
    3. Else: {project} = encoded current project (e.g., `-home-dev-projects-foo`)

2. Pull `avg_user_time_s`:
    - bash: `cd <THIS-FILE-DIR> && python3 -m scripts settings`
    - {avg-user-s} = `derived.avg_user_time_s.value` from response

3. List sessions in scope:
    - bash: `cd <THIS-FILE-DIR> && python3 -m scripts sessions {format-args} --show timeframes`
    - {sessions} = response array, sorted ascending by `first_ts`

4. Assign session indices — for each {session} in {sessions} in chronological order, assign 1-based index; exchanges from session N render as `S{N}E{m}`.
5. For each {session} in {sessions}:
    1. Pull full exchange detail:
        - bash: `cd <THIS-FILE-DIR> && python3 -m scripts exchanges --session {session} --show messages metrics timeframes`
    2. {descriptions} = empty map
    3. For each {exchange} in response:
        1. Read user_msg and assistant messages
        2. Compose a description per /description-authoring
        3. Set `{descriptions}[{exchange.exchange}] = {description}`
    4. Persist descriptions for the session:
        - bash: `cd <THIS-FILE-DIR> && python3 -m scripts descriptions-set {session} '<json of descriptions>'`

6. Consolidate exchanges into blocks:
    1. Within each session, walk exchanges in order
    2. Group exchanges sharing a topic or focus into a single block
    3. A block may include non-contiguous exchanges when an unrelated tangent interrupts
    4. Compose a block summary description per /description-authoring — broader than per-exchange descriptions; captures the unified objective of the contained exchanges
    5. Auto-tag each block as in-scope (`yes`) or out-of-scope (`no`) for {project} from the summary description

7. Present proposed blocks for user review:
    1. Render proposal table for user — Exchanges, Summary description, estimated Time (computed per step 8), In scope?
    2. Ask user to approve or adjust — Q# format with lettered options
    3. If user requests adjustments:
        1. Apply changes (re-group blocks, re-classify, re-word summary descriptions as directed)
        2. Go to step 7. Present
    4. Once approved, proceed

8. Compute time per block (final values used for render):
    1. For each {exchange} in the block:
        1. {engaged-s} = ({exchange.user_s} if not null else {avg-user-s}) + {exchange.agent_s}
    2. {block-seconds} = sum of {engaged-s} across exchanges in the block
    3. {block-minutes} = ceiling({block-seconds} / 60)

9. Render the report:
    1. Title: `# Time Block Report — {project}`
    2. For each day in chronological order:
        1. Day heading: `## YYYY-MM-DD` — date only, no totals
        2. Day table — columns: `Exchanges`, `Summary description`, `Time`, `In scope?`
        3. One row per block belonging to that day (a block belongs to the day of its earliest exchange's `exchange_start`); rows in chronological order, in-scope and out-of-scope interleaved naturally
    3. Summary table:
        - Heading: `## Summary`
        - Columns: `Date`, `In scope`, `Out of scope`
        - One row per day; final `**Total**` row sums day-level totals
        - Day total = sum of rounded block minutes for that day (in-scope and out-of-scope tallied separately)

10. Return to caller

## Format Conventions

- **Exchange refs** — `S{n}E{m}` where n is the 1-based session index (chronological order across the report's scope) and m is the exchange number within that session.
- **Range form** — Consecutive exchanges in the same session collapse to a range: `S2E1-E5`. Non-contiguous exchanges within a single block list comma-separated: `S2E1, S2E4-E12, S2E15`.
- **Time format** — Sub-hour: `Xm` (e.g., `7m`, `35m`). Hour-or-more: `Xh Ym` (e.g., `2h 57m`). Zero-time blocks: `0m`.
- **Time rounding** — Ceiling at the block level (each block is the billable unit). Day totals are sums of rounded block minutes — *not* a re-ceiling of day seconds.
- **In scope? column** — Boolean `yes` / `no`. The question asked: "Is this block directly related to {project}?". Out-of-scope rows may capture sibling-project work, tangents, or meta-explorations.

## Format Example

```
# Time Block Report — example-project

## 2026-04-29

| Exchanges | Summary description | Time | In scope? |
|---|---|---:|---|
| S1E1-E2 | Pre-transfer audit of libs/ packaging vs submodules | 7m | yes |

## 2026-04-30

| Exchanges | Summary description | Time | In scope? |
|---|---|---:|---|
| S2E1-E2 | Repo ownership-transfer procedure documentation | 7m | yes |
| S2E3 | Tangent into a sibling project's debug session | 2m | no |
| S2E4-E10 | KNOWN-ISSUES audit of pipeline + orchestration modules | 58m | yes |

## Summary

| Date | In scope | Out of scope |
|---|---:|---:|
| 2026-04-29 | 7m | — |
| 2026-04-30 | 1h 5m | 2m |
| **Total** | **1h 12m** | 2m |
```

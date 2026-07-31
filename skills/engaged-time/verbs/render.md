# render

Produce a static single-DB timeline HTML — a fixed artifact, no server. The same geometry `serve` draws, written once to a file, plus a companion entity-key `.md`. Use for a shareable snapshot, or to inspect one session without the interactive tree.

## Signature

```
uv run ${CLAUDE_SKILL_DIR}/swimlane_timeline.py [--db ~/.claude/engaged-time/raw.db] \
    [--lines N] [--compact] [--ui-state] [--out ~/.claude/engaged-time/diagrams/swimlane-timeline.html]
```

- `--lines N` — keep only each file's first N lines (0 = all).
- `--compact` — **ordinal** row pitch: uniform rows, elapsed time as log-length heat bars in the left gutter (no idle bands, no hour grid; the labeled prompt/interrupt lines are the time landmarks). Without it, **proportional** pitch: vertical space ∝ real elapsed time, clamped, with idle bands and an hour grid.
- `--ui-state` — include the untimestamped UI-state record types (excluded by default — pure session state, no timeline influence).
- `--out` — HTML path; a sibling `.md` entity key is written alongside.

## Process

1. Ensure the raw DB is current (`verbs/ingest.md`).
2. Choose the pitch: `--compact` for sequence-focused reading (the tree view's mode), default for true-proportion timing.
3. Run it. The HTML lands at `--out`, the companion `.md` beside it (every event class, its description, and which JSONL properties the diagram shows versus hides), and node/edge/column/height counts print.

## Static versus server

The static render keeps **both** pitch modes (`--compact` and proportional) and the per-session hour grid. The interactive `serve` is **ordinal-only** by decision — the tree view's dynamic shared columns need uniform pitch. Both consume the same `swimlane_timeline.py` geometry; neither reinterprets the model.

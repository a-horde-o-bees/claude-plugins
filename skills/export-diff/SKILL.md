---
name: export-diff
description: Use when a change set should be reviewed visually outside the terminal — two versions of a file or directory tree, or an existing unified diff from any tool, rendered to a self-contained side-by-side HTML page set (no git required; e.g. before/after snapshots of docs, skills, or generated trees). Sets itself apart from line-based diff viewers by attributing content that moved, merged into another line, or split apart — even across line breaks — with word-level marks on only the real edits, wrapped prose lines, and a dropdown viewer for large multi-directory diffs.
---

# export-diff

Use when a change set should be reviewed visually outside the terminal — two versions of a file or directory tree, or an existing unified diff from any tool, rendered to a self-contained side-by-side HTML page set (no git required; e.g. before/after snapshots of docs, skills, or generated trees). Sets itself apart from line-based diff viewers by attributing content that moved, merged into another line, or split apart — even across line breaks — with word-level marks on only the real edits, wrapped prose lines, and a dropdown viewer for large multi-directory diffs.

## Run

bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/render_diff.py <--old OLD --new NEW | --diff FILE> --out DIR [--title T] [--split auto|always|never]`

- `--old/--new`: two files or trees, compared with `diff -ruN`. `--diff`: an existing unified diff.
- Output: `DIR/index.html` — open in a browser. A large diff spanning several top-level directories splits into one page per directory behind a dropdown viewer; section pages must stay beside `index.html`.
- Fully self-contained: `uv` supplies the python deps; no network or node tooling.

Report the printed per-section summary (files, ±lines, moved runs, change blocks, rewrite pairs) with the output path. Every page is auto-linted against the box contract (SPEC.md I17); `LINT` lines in the output are defects — investigate, don't ship silently. `scripts/lint_diff.py PAGE.html` re-checks any page standalone.

## Reading the output

- Every changed region is a box: gray outline, faint red fill (removed side) or green fill (added side) — whether edited in place, moved, merged, split, wholly removed, or wholly added.
- Heavy red/green ink inside a box marks the exact removed/added tokens; a wholly removed or added block is fully inked.
- Gutter connectors pair counterpart boxes: straight = changed in place, crossing = moved; no connector = no counterpart.
- Hovering anywhere in a box highlights both sides and the connector; clicking pins one pair (click again to unpin), so an off-screen counterpart can be scrolled to.
- Unchanged spans between hunks render as separators labeled per side with that side's line range ("54-57 unchanged"). When the new-side source files are present and match the diff (rendering from `--old/--new`, or `--diff` run where the diff's paths resolve), the separators expand — per-fold, or all at once via the top Show/Hide button — so the full file is readable in place.
- Right-clicking a box copies a block reference: per present side, an `OLD: path:lines` / `NEW: path:lines` marker line followed by that side's verbatim contents — pasteable into a conversation or grep; the quote stays resolvable after line numbers drift.
- The split viewer carries this legend; for a single page, relay it to the reader.

## Engine and provenance

Custom matching on stock scaffolding — represent it as such:

- GNU `diff` (stock): line-level chunking.
- `scripts/render_diff.py` (this skill): parses the diff and emits its own side-by-side page — one table per file, both sides of a change in the same table row, so alignment holds by construction — plus the box/connector overlay.
- `scripts/engine.py` (this skill's engine): token-stream matching — greedy string tiling (RKR-GST family) for exact anchors that cross line boundaries, anchored gap refinement, bag-of-words Jaccard fallback, then move/merge/split classification and word marks.

The algorithms are established families from the plagiarism-detection and diff literature; the composition — cross-line move/merge/split attribution rendered in a side-by-side HTML view — is what stock viewers (git `--color-moved`, diff2html, difit, GitHub) don't offer. Never present the algorithms themselves as novel.

## Spec

`SPEC.md` (this directory) is the contract: the ordered pipeline, every invariant that must hold on output, thresholds, and known limits. Consult it before debugging or changing matching behavior; a divergence between spec and behavior is a defect — fix whichever is wrong and keep both in sync.

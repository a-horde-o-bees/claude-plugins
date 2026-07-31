# git doctor — default-branch domain

> Advisory component for `/git doctor`. Two related findings on the repo's default branch: `origin/HEAD` unset (branch-resolving verbs fall through to their fallback) and a default that isn't `main` (the modern standard the repo silently contradicts). Non-blocking — convenience and conformance, not a safety gate. Each fix is gated on approval and declinable; the repo keeps whatever it has if you decline. The driver runs both fixes.

## Process

1. `{detail}`: the detector's `default-branch` problem detail — it names which finding fired (unset pointer vs non-`main` default) and, for the latter, the current default `{default}`.
2. Set `origin/HEAD` — when the finding is the unset pointer:
    1. AskUserQuestion — set `refs/remotes/origin/HEAD` now? A local, reversible pointer that makes branch resolution work without a network call; the driver resolves the true default from the forge (fallback `main`).
    2. If approved: bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py origin-head-set` — bind `{origin_head}` and its `{source}` (forge vs fallback) for the report
3. Rename to the `main` standard — when the finding is `{default}` ≠ `main`:
    1. AskUserQuestion — rename `{default}` to `main` across every remote now? This is the modern standard, not a hard requirement — decline to keep `{default}`. The rename is outward-facing: it changes what new clones check out and touches every remote's forge default.
    2. If declined: surface the finding in the report unchanged — the repo keeps `{default}`, no gloss over the contradiction.
    3. If approved: bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py default-branch-rename --old {default}` — the driver runs the canonical order (local rename → publish `main` everywhere → flip each forge default (github via gh, gitlab via glab, local-path remotes directly) → delete `{default}` per remote → repoint HEADs and prune), with progressive output.
    4. If BLOCKED (a remote refused to delete `{default}` — protected there, or an unflippable forge): surface the driver's message verbatim — it names what completed and the manual unprotect → delete → re-protect-`main` path. Protection carry-over is deliberate and manual; never silently drop a default branch's protection.

## Report

Return to caller:

- Default branch: `{default}` — `{renamed to main | kept (rename declined) | rename halted (see driver surface)}`
- `origin/HEAD`: `{set → {origin_head} ({source}) | already set | left unset (verbs fall back)}`
- Remotes updated: `{from the driver's output | — none}`

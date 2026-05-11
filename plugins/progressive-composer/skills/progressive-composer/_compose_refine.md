# Compose refine

Re-enter an existing composition. Script reads composition.md, runs `git ls-remote` per source for non-mutating drift detection, and emits state (spec path, deployed status, per-source drift). This workflow file owns the procedure for what to do with that state. Agent surfaces drift to the user, asks whether to update each drifted source, and drives refinement of the design intent.

## Arguments

`<name> --scope <user|project>`

- `<name>` — composition skill name.
- `--scope` — scope where the composition lives.

## Process

1. Invoke — bash: `uv run -m scripts.compose refine <name> --scope <user|project>`

2. The script emits state only:
    - Spec path
    - Deployed status (`yes` if SKILL.md exists in the skill folder, else `no`)
    - Per-source classification: drifted (with old/new SHA pair), in-sync, or issue (e.g., ls-remote failure)

3. Agent surfaces drift to the user. Suggested opening:
    > "Since last refine, `<source-slug>:<skill>` changed from `<old-short>` to `<new-short>` upstream. Want to incorporate this update into the composition?"

   For sources still in sync, skip mention unless relevant.

4. For each drifted source the user wants to update, agent invokes:

    ```
    uv run -m scripts.compose update-sources <name> --source <source-slug> --scope <scope>
    ```

   This re-sparse-checks the source at current upstream HEAD and advances the pinned `commit` in composition.md. To update all drifted sources at once, omit `--source`.

5. Agent re-reads any updated `<scope>/.claude/skills/<name>/sources/<source-slug>/` to spot content changes worth reflecting in the Goal, Surface, or Sources sections.

6. Agent drives refinement dialogue with the user. Composition.md edits happen **in place** — the file describes current ideal state, not a journal. Targeted prompts:
    - "Now that `<source>` has updated, does its Sources subsection still hold?"
    - "Does the Surface still match the cognitive moments we want this skill to carry?"
    - "Has the Goal shifted?"
    - "Is any source no longer earning its keep?" — if yes, follow with `compose remove-source`

7. Agent edits the live skill (`SKILL.md`, `_<verb>.md`, `scripts/`) directly as the implementation evolves. composition.md tracks **intent**; the skill files are the implementation. Refinement may touch both, in either order.

## Sources missing from cache

If a source's embedded `sources/<slug>/` was purged via `compose purge-sources`, the agent rehydrates by invoking `compose update-sources <name> --source <slug> --scope <scope>` before re-reading the source content. The pinned commit in composition.md ensures rehydration restores the same content the previous session was based on.

## Issues surfaced by the script

The script reports issues for sources where `git ls-remote` failed (network error, repo gone, ref deleted). The agent surfaces these to the user and discusses whether to:

- Replace the source via `compose remove-source <name> <slug> --scope` and `compose add-source <name> <new-url>:<skill>[@<ref>] --scope`
- Drop the source (also call `compose remove-source`) if no replacement exists and the source no longer informs the skill
- Wait and try again later if the failure is transient

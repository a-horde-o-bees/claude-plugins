# Compose refine

> Workflow component for the `refine` verb of compose. Re-enters an existing composition: reads composition.md, runs `git ls-remote` per source for non-mutating drift detection, surfaces drift to the user, drives refinement dialogue.

## Arguments

`<name> --destination <user|project|path>`

- `<name>` — composition skill name.
- `--destination` — scope where the composition lives.

## Process

1. {state}: bash: `uv run --directory <skill-base> -m scripts.compose refine <name> --destination <user|project|path>` — emits:
    - Spec path
    - Deployed status (`yes` if SKILL.md exists in the skill folder, else `no`)
    - Per-source classification: drifted (with old/new SHA pair), in-sync, or issue (e.g., ls-remote failure)

2. {drifted-sources}: subset of {state}'s per-source list where classification is `drifted`

3. For each {source} in {drifted-sources}:
    1. Present: `<source-slug>:<skill>` changed from `<old-short>` to `<new-short>` upstream
    2. {update-this}: AskUserQuestion — incorporate update into the composition? (yes / no)
    3. If {update-this} is yes:
        1. bash: `uv run --directory <skill-base> -m scripts.compose update-sources <name> --source <source-slug> --destination <destination>` — re-sparse-checks at upstream HEAD; advances pinned commit in composition.md
        2. Read updated `<destination-parent>/<name>/sources/<source-slug>/` to spot content changes worth reflecting in Goal / Surface / Sources

4. Drive refinement dialogue. composition.md edits happen **in place** — the file describes current ideal state, not a journal. Targeted prompts:
    - "Now that `<source>` has updated, does its Sources subsection still hold?"
    - "Does the Surface still match the cognitive moments we want this skill to carry?"
    - "Has the Goal shifted?"
    - "Is any source no longer earning its keep?" — if yes, follow with `compose remove-source`

5. Edit the live skill (`SKILL.md`, `_<verb>.md`, `scripts/`) directly as the implementation evolves. composition.md tracks **intent**; the skill files are the implementation. Refinement may touch both, in either order.

## Sources missing from cache

If a source's embedded `sources/<slug>/` was purged via `compose purge-sources`, rehydrate by invoking `compose update-sources <name> --source <slug> --destination <destination>` before re-reading the source content. The pinned commit in composition.md ensures rehydration restores the same content the previous session was based on.

## Issues surfaced by the script

The script reports `issue` classification for sources where `git ls-remote` failed (network error, repo gone, ref deleted). For each issue source:

- Replace the source: `compose remove-source <name> <slug> --destination` + `compose add-source <name> <new-url>:<skill>[@<ref>] --destination`
- Drop the source: `compose remove-source <name> <slug> --destination` (if no replacement exists and the source no longer informs the skill)
- Wait and try again later if the failure is transient

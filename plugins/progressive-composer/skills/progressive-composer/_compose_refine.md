# Compose refine

Re-enter an existing composition. Script reads composition.md, runs `git ls-remote` per source for non-mutating drift detection, and prints status report + orchestration. Agent surfaces drift to the user, asks whether to update each drifted source, then drives the refinement dialogue.

## Arguments

`<name> --scope <user|project>`

- `<name>` — composition skill name.
- `--scope` — scope where the composition lives.

## Process

1. Invoke — bash: `uv run -m scripts.compose refine <name> --scope <user|project>`

2. The script:
    - Reads composition.md frontmatter
    - Runs `git ls-remote <url> <ref>` per source — non-mutating, no local clone state touched
    - Compares each returned SHA to the pinned `commit` field in composition.md
    - Prints status: spec path, type, build_status, last_build; per-source drift lists (drifted vs in-sync vs issues); orchestration guidance

3. Agent surfaces drift to the user. Suggested opening:
    > "Since last refine, `<source-slug>:<skill>` changed from `<old-short>` to `<new-short>` upstream. Want to incorporate this update into the composition?"

   For sources still in sync, simply note them or skip mention.

4. For each drifted source the user wants to update, agent invokes:

    ```
    uv run -m scripts.compose update-sources <name> --source <source-slug> --scope <scope>
    ```

   This re-sparse-checks the source at current upstream HEAD and advances the pinned `commit` in composition.md. To update all drifted sources at once, omit `--source`.

5. Agent re-reads any updated `<scope>/.claude/skills/<name>/sources/<source-slug>/` to spot content changes worth reflecting in the goal or per-source mapping.

6. Agent drives refinement dialogue with the user. Targeted prompts:
    - "Now that `<source>` has updated, does the source mapping still hold?"
    - "Are there parts of the goal you want to revise?"
    - "Anything from upstream's changes you want to incorporate as new design refinements?"

   Agent edits composition.md body via Edit tool — updates `# Goal`, refines `## Source mapping` subsections, and especially appends to `## Design refinements`.

7. Agent appends a dated entry to `## Design refinements`. Format suggestion:

    ```
    ### YYYY-MM-DD — <one-line summary>

    <prose summary of what was discussed and decided this session>

    Sources updated: <slug>, <slug>
    Sources skipped (kept pinned): <slug>
    ```

8. When the user wants to materialize the refined spec, agent invokes:

    ```
    uv run -m scripts.compose build <name> --scope <scope> --force
    ```

   `--force` is required because a deployed SKILL.md already exists from the prior build; the rebuild regenerates it. Note: this overwrites any agent refinements made directly in SKILL.md after the previous build. If significant refinements live in the deployed SKILL.md, the agent should fold them back into composition.md's `# Goal` or `## Source mapping` sections before rebuilding.

## Sources missing from cache

If a source's embedded `sources/<slug>/` was purged via `compose purge-sources`, the agent should rehydrate by invoking `compose update-sources <name> --source <slug> --scope <scope>` before re-reading the source content. The pinned commit in composition.md ensures rehydration restores the same content the previous build was based on.

## Issues surfaced by the script

The script reports `issues:` for sources where `git ls-remote` failed (network error, repo gone, ref deleted). The agent should surface these to the user and discuss whether to:

- Replace the source via `compose remove-source <name> <slug> --scope` and `compose add-source <name> <new-url>:<skill>[@<ref>] --scope`
- Drop the source if no replacement exists
- Wait and try again later if the failure is transient

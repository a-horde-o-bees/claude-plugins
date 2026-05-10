# Compose build

Materialize a finalized composition into a deployable skill folder. Script generates SKILL.md from composition.md drawing on the embedded `sources/<source-slug>/` content; advances pinned commits to current sources/ HEAD; sets `build_status: built`. Agent then refines the deployed SKILL.md via dialogue.

## Arguments

`<name> --scope <user|project> [--force]`

- `<name>` — composition skill name.
- `--scope` — scope where the composition lives.
- `--force` — overwrite an existing deployed SKILL.md (clobbers prior agent refinements).

## Process

1. Invoke — bash: `uv run -m scripts.compose build <name> --scope <user|project>`

2. The script validates:
    - composition.md exists at the resolved path
    - `type` is `composed` (installs don't go through build — they materialize at install time)
    - `description` and `goal_summary` are non-empty (required for the deployed SKILL.md frontmatter and body opener)
    - `sources` list is non-empty (a composition with no exemplars isn't a composition)

3. The script writes:
    - `<scope>/.claude/skills/<name>/SKILL.md` — frontmatter from spec (name, description), body opens with `goal_summary` plus an HTML comment pointing at composition.md and TODO sections for triggers and verbs
    - `<scope>/.claude/skills/<name>/scripts/__init__.py` — empty package marker (created if absent)

4. The script updates composition.md frontmatter: `last_build` (now), `build_status: built`. Pinned source commits are NOT advanced by build itself — they were last set by `compose new`'s `add-source` invocations or by `compose refine`'s `update-sources` calls. Build trusts whatever's pinned.

5. Agent opens the deployed SKILL.md and refines it via dialogue:
    - Reads composition.md to recall the goal articulation and per-source mappings
    - Reads each `sources/<source-slug>/SKILL.md` to draw on the exemplars
    - Authors triggers, verb topography, and procedural workflows that synthesize the design intent
    - Implements scripts in `scripts/` using the embedded sources as references

## Validation gates

Build refuses to proceed when:

- composition.md doesn't exist
- type is `install` (installs don't need build)
- `description` or `goal_summary` is empty in composition.md frontmatter (run `compose refine` to fill them)
- The sources list is empty
- A deployed SKILL.md already exists and `--force` is not set

Each gate prints a corrective message and exits non-zero.

## Output

```
built <name> at <scope>/.claude/skills/<name>
sources used:
  - <url>:<skill>@<ref> @ <commit-short>
  - <url>:<skill>@<ref> @ <commit-short>
status: built

Next steps for the agent:
  1. Open <path>/SKILL.md and refine via dialogue with the user
  2. Add `_<verb>.md` workflow files for each procedure the spec describes
  3. Implement scripts in `scripts/` drawing on `sources/<source-slug>/` exemplars
  4. Run `compose refine <name> --scope <scope>` to detect upstream drift
```

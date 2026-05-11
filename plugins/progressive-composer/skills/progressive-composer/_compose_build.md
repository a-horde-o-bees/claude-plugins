# Compose build

Scaffold a deployable skill folder from composition.md. Script generates the initial SKILL.md frontmatter (from composition.md's `name` + `description`) and a `scripts/` package skeleton. Build is the **initial materialization** — once SKILL.md exists, the agent refines it directly; composition.md tracks intent, not the live code.

## Arguments

`<name> --scope <user|project> [--force]`

- `<name>` — composition skill name.
- `--scope` — scope where the composition lives.
- `--force` — overwrite an existing deployed SKILL.md (clobbers prior agent refinements).

## Process

1. Invoke — bash: `uv run -m scripts.compose build <name> --scope <user|project>`

2. The script validates:
    - composition.md exists at the resolved path
    - `description` is non-empty (required for the deployed SKILL.md frontmatter)
    - `sources` list is non-empty (a composition with no exemplars isn't a composition)
    - SKILL.md does not already exist at the deploy path — unless `--force` is set

3. The script writes:
    - `<scope>/.claude/skills/<name>/SKILL.md` — frontmatter from spec (name, description), body scaffolds a `## Triggers` section the agent fleshes out from composition.md's `## Surface`
    - `<scope>/.claude/skills/<name>/scripts/__init__.py` — empty package marker (created if absent)

4. The script emits state only: skill folder path, SKILL.md path, sources materialized. No procedural guidance.

5. Agent opens the deployed SKILL.md and refines it via dialogue:
    - Reads composition.md to recall the Goal + Surface + per-source rationale
    - Reads each `sources/<source-slug>/SKILL.md` to draw on exemplars
    - Translates each `## Surface > ### <cognitive moment>` from composition.md into a `## Triggers` entry in the deployed SKILL.md
    - For each `Routes to: _<verb>.md` line in Surface, creates the corresponding `_<verb>.md` workflow file under PFN authoring discipline
    - Implements `scripts/` as needed using the embedded sources as references

## Validation gates

Build refuses to proceed when:

- composition.md doesn't exist
- `description` is empty in composition.md frontmatter (set it before building; the SKILL.md frontmatter needs a discoverable description)
- The sources list is empty
- A deployed SKILL.md already exists and `--force` is not set

Each gate prints a corrective message and exits non-zero.

## Output

```
built <name> at <scope>/.claude/skills/<name>
sources used:
  - <url>:<skill>@<ref> @ <commit-short>
  - <url>:<skill>@<ref> @ <commit-short>
```

Nothing else. Procedure for what to do after build lives in this file's *Process* section, not in script output.

## After build: composition.md vs SKILL.md

After the initial materialization, the two files have distinct roles:

- **composition.md** — design intent + source provenance. Edited in place during refinement. Not regenerable from SKILL.md.
- **SKILL.md (+ `_<verb>.md` + `scripts/`)** — the live skill implementation. Refined directly by the agent. Not regenerable from composition.md alone.

`compose build --force` re-scaffolds SKILL.md from composition.md's name + description, **clobbering prior agent refinements**. Use `--force` deliberately — typically only when a major redesign means the prior SKILL.md no longer fits and the agent will refine fresh.

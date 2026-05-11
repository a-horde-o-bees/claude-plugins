# Compose new

Open a new-composition workflow. The script emits resolved state only (target path + scope); this workflow file owns the procedure. The user has not yet chosen a skill name when this verb fires — name + intent are collected through agent-led conversation, then the agent uses Write tool to author the initial composition.md scaffold.

## Arguments

`--scope <user|project>`

- `--scope` — scope where the composition will live (`<scope>/.claude/skills/<name>/`).

## Process

1. Invoke — bash: `uv run -m scripts.compose new --scope <user|project>`

2. The script emits resolved state — scope and the target composition.md path (with `<chosen-name>` as placeholder). No disk writes; no procedural guidance.

3. Agent collects the skill **name** and **high-level intent** through dialogue:
    - "What should this skill enable Claude to do?"
    - "When should this skill fire? (user phrases / contexts)"
    - "What's the expected output format?"
    - "What name should the skill have? (lowercase, hyphenated)"

4. Agent collects the **Surface** — the cognitive moments the skill will carry and where each routes:
    - "What distinct cognitive moments should make this skill fire?"
    - "For each moment, does deeper content load on demand (`_<verb>.md`) or is it terse enough to inline in SKILL.md's body?"
    - The Surface is the progressive-disclosure shape SKILL.md will materialize; capture it now even at a rough level.

5. Once name + description are chosen, agent uses the Write tool to create `<scope>/.claude/skills/<chosen-name>/composition.md` using the scaffold template (see *composition.md scaffold template* below). Substitute placeholders with values collected in steps 3–4.

6. Agent asks about exemplar sources. For each chosen source, agent invokes the sub-op:

    ```
    uv run -m scripts.compose add-source <chosen-name> <url>:<skill>[@<ref>] --scope <scope>
    ```

   The sub-op sparse-checks the source skill into `<scope>/.claude/skills/<chosen-name>/sources/<source-slug>/` and appends the source to composition.md frontmatter with a pinned commit.

7. Agent reads each embedded source's SKILL.md (and supporting files) at `<scope>/.claude/skills/<chosen-name>/sources/<source-slug>/SKILL.md` to understand what each exemplar offers.

8. Agent fills in the **Sources** body section with per-source rationale. For each source, prompts include:
    - "Looking at `<slug>:<skill>`, what's worth keeping verbatim?"
    - "What needs adapting to fit our Surface?"
    - "What should be rejected or replaced?"
    - "Which Surface entries does this source inform?"

   Agent edits composition.md body via Edit tool — populates one `### <slug>:<skill>` subsection under `## Sources` per source.

9. When the user is satisfied with the design, agent invokes the build verb:

    ```
    uv run -m scripts.compose build <chosen-name> --scope <scope>
    ```

   This scaffolds the live skill (SKILL.md + scripts/) from the composition. Build is the **initial materialization**, not a regenerator — once SKILL.md exists, the agent refines it directly; composition.md tracks intent only.

## composition.md scaffold template

The agent writes this exact shape via Write tool after collecting name + description + Surface in dialogue. Substitute placeholders (`<...>`) with values from the dialogue.

```markdown
---
spec_version: 1
name: <chosen-name>
description: <one-line cognitive trigger; carries to the built SKILL.md frontmatter>
sources: []
---

# Goal

<why this skill exists; what value it provides; current intent. Edited in place as the design evolves — no historical journal; describe the destination, not the path.>

## Surface

<the cognitive moments this skill carries and where each routes — the progressive-disclosure shape SKILL.md will materialize. One subsection per moment.>

### <cognitive moment>

Routes to: `_<verb>.md` (or inline)

<what fires this; what content loads when it does>

## Sources

<per-source rationale, aligned with the Surface above. One subsection per `compose add-source` invocation; remove the subsection (and call `compose remove-source`) when a source no longer informs the skill.>

### <source-slug>:<skill>

Informs: <which Surface entries>. <Keep verbatim / adapt / reject — current rationale.>
```

## Body section conventions

| Section | Owner | Content |
|---|---|---|
| `# Goal` | Agent during dialogue | Why this skill exists; current intent. Edited in place; no historical journal. |
| `## Surface > ### <cognitive moment>` | Agent during dialogue | The progressive-disclosure shape the skill carries. Each moment names what fires it and where deeper content loads. One subsection per cognitive moment. |
| `## Sources > ### <slug>:<skill>` | Agent during dialogue | Per-source: which Surface entries it informs, plus keep / adapt / reject rationale. One subsection per `compose add-source`. Remove when a source stops earning its keep. |

The frontmatter is machine-managed — only the script (via sub-ops add-source, remove-source, update-sources, purge-sources) writes the source list and pinned commits. The agent never edits frontmatter `sources` directly.

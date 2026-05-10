# Compose new

Open a new-composition workflow. The script prints orchestration; the agent drives the dialogue. The user has not yet chosen a skill name when this verb fires — name + goal are collected through agent-led conversation, then the agent uses Write tool to author the initial composition.md scaffold.

## Arguments

`--scope <user|project>`

- `--scope` — scope where the composition will live (`<scope>/.claude/skills/<name>/`).

## Process

1. Invoke — bash: `uv run -m scripts.compose new --scope <user|project>`

2. The script outputs orchestration guidance plus the composition.md scaffold template — no disk operations yet.

3. Agent collects the skill name and high-level goal through dialogue:
    - "What should this skill enable Claude to do?"
    - "When should this skill fire? (user phrases / contexts)"
    - "What's the expected output format?"
    - "What name should the skill have? (lowercase, hyphenated)"

4. Once a name and goal are chosen, agent uses the Write tool to create `<scope>/.claude/skills/<chosen-name>/composition.md` with the documented frontmatter scaffold (see template below) and body section headers.

5. Agent asks the user about exemplar sources. For each chosen source, agent invokes the sub-op:

    ```
    uv run -m scripts.compose add-source <chosen-name> <url>:<skill>[@<ref>] --scope <scope>
    ```

   The sub-op sparse-checks the source skill into `<scope>/.claude/skills/<chosen-name>/sources/<source-slug>/` and appends the source to composition.md frontmatter with a pinned commit.

6. Agent reads each embedded source's SKILL.md (and supporting files) at `<scope>/.claude/skills/<chosen-name>/sources/<source-slug>/SKILL.md` to understand what each exemplar offers.

7. Agent walks the user through goal articulation and per-source mapping. For each source, prompts include:
    - "Looking at `<source-slug>:<skill>`, what's worth keeping verbatim?"
    - "What needs adapting to fit your goal?"
    - "What should be rejected or replaced?"

   Agent edits the spec body via Edit tool — fills in `# Goal`, populates one `### <source-slug>:<skill>` subsection per source under `## Source mapping`.

8. When the user is satisfied with the design, agent invokes the build verb:

    ```
    uv run -m scripts.compose build <chosen-name> --scope <scope>
    ```

   This generates SKILL.md at the skill folder and advances the spec to `build_status: built`.

## composition.md scaffold template

The agent writes this exact shape via Write tool after collecting name + goal in dialogue. Substitute placeholders (`<...>`) with values from the dialogue.

```markdown
---
spec_version: 1
name: <chosen-name>
type: composed
description: <one-line description for SKILL.md frontmatter>
scope: <user|project>
sources: []
goal_summary: <one-line summary the deployed SKILL.md body opens with>
last_build: null
build_status: draft
---

# Goal

<articulated through dialogue — what does this skill enable Claude to do, when does it fire, expected output format>

## Source mapping

<one ### subsection per source after compose add-source invocations>

## Design refinements

<dated entries appended on subsequent compose refine sessions>
```

## Body section conventions

| Section | Owner | Content |
|---|---|---|
| `# Goal` | Agent during dialogue | What the skill enables, when it fires, expected output. Detailed enough that `compose build` can synthesize SKILL.md from it. |
| `## Source mapping > ### <source-slug>:<skill>` | Agent during dialogue | Per-source: what to keep verbatim, what to adapt, what to reject. One subsection per `compose add-source`. |
| `## Design refinements` | Agent during refine sessions | Append-only log. Each refinement appends a dated entry; previous entries preserved unless explicitly superseded. |

The frontmatter is machine-managed — only the script writes `last_known_commit`, `last_build`, `build_status`, and the source list. Sub-ops (add-source, remove-source, update-sources, purge-sources) handle frontmatter edits; the agent never edits frontmatter directly.

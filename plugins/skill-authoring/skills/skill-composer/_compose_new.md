# Compose new

Workflow component for the `new` verb of compose. Owns new-skill composition from one or more exemplar sources.

## Arguments

`--destination <user|project|path>`

- `--destination` — where the composition lives. `user`, `project`, or a path (absolute or relative to the project root). The skill folder is created at `<destination-parent>/<name>/`.

## Process

1. Invoke — bash: `uv run -m scripts.compose new --destination <user|project|path>`

2. The script emits resolved state — scope and the target composition.md path with `<chosen-name>` as placeholder.

3. Agent collects the skill's **high-level intent** through dialogue:
    - What should this skill enable Claude to do?
    - When should it fire? (user phrases / contexts)
    - What's the expected output format?

4. Agent collects the **Surface** — the cognitive moments the skill carries and where each routes:
    - What distinct cognitive moments should make this skill fire?
    - For each moment: deeper content in a `_<verb>.md` component, or terse enough to inline?

5. {chosen-name}: a skill name derived from the interview answers and Surface. Offer 2–3 lowercase-hyphenated candidates and refine with the user until they settle on one.

6. Agent creates `<destination-parent>/{chosen-name}/composition.md` from `assets/composition-template.md`, substituting placeholders with values from steps 3–5.

7. Agent asks about exemplar sources. For each chosen source:

    ```
    uv run -m scripts.compose add-source {chosen-name} <url>:<skill>[@<ref>] --destination <destination>
    ```

   The sub-op sparse-checks the source into `<destination-parent>/{chosen-name}/sources/<source-slug>/` and appends it to composition.md frontmatter with a pinned commit.

8. Agent reads each embedded source's `SKILL.md` (and supporting files) at `<destination-parent>/{chosen-name}/sources/<source-slug>/` to understand what each exemplar offers.

9. Agent populates the `## Sources` section in composition.md. For each source:
    - What's worth keeping verbatim?
    - What needs adapting to fit our Surface?
    - What should be rejected or replaced?
    - Which Surface entries does it inform?

10. Agent scaffolds the live skill from bundled templates:
    1. `<destination-parent>/{chosen-name}/SKILL.md` from `assets/skill-template.md`, substituting from composition.md.
    2. For each cognitive moment in `## Surface`, `<destination-parent>/{chosen-name}/_<verb>.md` from `assets/verb-workflow-template.md`.
    3. If any verb has mechanical work, create `<destination-parent>/{chosen-name}/scripts/__init__.py` and the relevant Python module; the workflow invokes it via `uv run`.

    Refinement continues live — composition.md tracks intent; the skill files are the implementation. `compose refine` re-engages this dialogue when sources drift upstream.

## Body section conventions

| Section | Owner | Content |
|---|---|---|
| `# Goal` | Agent during dialogue | Why this skill exists; current intent. Edited in place; no historical journal. |
| `## Surface > ### <cognitive moment>` | Agent during dialogue | The shape the skill carries. Each moment names what fires it and where deeper content loads. |
| `## Sources > ### <slug>:<skill>` | Agent during dialogue | Per-source: which Surface entries it informs, plus keep / adapt / reject rationale. Remove when a source stops earning its keep. |

The frontmatter `sources` list is machine-managed — only the script (via add-source, remove-source, update-sources, purge-sources) writes source entries and pinned commits.

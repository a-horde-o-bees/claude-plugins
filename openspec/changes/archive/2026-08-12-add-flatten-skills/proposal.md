## Why

Skill-to-skill composition is unreliable: a skill referencing `/other-skill` depends on the model choosing to invoke it, and empirical testing showed the runtime alternative (`!` bash preprocessing) hard-caps inlined output at a ~2KB preview — too small for any real dependency body. The suite needs deterministic composition: a dependency's full text physically present in the file the runtime loads.

## What Changes

- New `flatten_skills.py` script colocated in `skill-authoring/scripts/` beside `lint_skill.py`: materializes each skill's declared dependencies into a single marker-delimited generated region inside its SKILL.md at build time (`refresh`), and verifies freshness by full recompute-and-compare (`--check`).
- Marker region format: `<!-- flatten-skills START {"deps": [...]} -->` … `<!-- flatten-skills STOP -->` — one region per file, placeable anywhere, JSON declaration on START, everything between markers generated (heading, demoted dependency bodies as the flat deduplicated transitive closure).
- **BREAKING**: suite-wide removal of `/skill-name` cross-references from skill bodies; after migration, a slash reference to another suite skill in source is a lint error (definitional/self-referential uses excepted via fence-awareness).
- Skills reference their own bundled files as `${CLAUDE_SKILL_DIR}/…` (replacing hardcoded absolute paths); the build rewrites a transplanted dependency's occurrences to `${CLAUDE_SKILL_DIR}/../<dep-folder>/…`, so non-self-contained skills are valid dependencies.
- Rewrites queued behind the mechanism: `procedure-authoring` (Call/Apply constructs are the model-mediated indirection this deletes), `/git` (router self-reference folded into in-place instruction plus deeper script mechanization), `skill-authoring` § Skill layout (per-verb component decomposition no longer prescribed), `file-decomposition` (reliability-precedence clause when the navigator is the model), `reauthor` (refocused: invoked when fresh composition is the directive; "When not to reauthor" dropped; concise-prose materialized as its first dependency).
- `apply-over-queue`'s `flatten.py` slash-reference expansion retires once dependencies arrive pre-materialized; operation flattening approaches concatenation.

## Capabilities

### New Capabilities
- `skill-dependency-flattening`: the marker region format and the refresh/check behavior of `flatten_skills.py` — declaration parsing, dependency-graph construction, cycle rejection, component extraction, deduplicated transitive closure, uniform heading demotion, and bundled-file path rewriting.
- `skill-source-conventions`: lintable authoring rules that make flattening mechanical — component structure (one H1, H2 sections), `${CLAUDE_SKILL_DIR}` self-references, no cross-skill slash references, marker hygiene.

### Modified Capabilities

(none — no existing specs in this project)

## Impact

- Live suite at `~/.claude/skills/` (source of truth): `skill-authoring` (gains the script; layout section rewritten), `procedure-authoring`, `git`, `file-decomposition`, `reauthor`, and every skill touched by the slash-reference purge.
- `lint_skill.py` grows the new source-convention checks; the lint pass adds `flatten_skills.py --check`.
- This repo's mirror (`skills/`) picks the changes up through the existing sync-skills workflow; materialized regions are build output with a mechanically checkable freshness invariant, the same status `skills/` already has.
- Reference dummies from the design session live at `tmp/skills/{concise-prose,reauthor}/SKILL.md`.

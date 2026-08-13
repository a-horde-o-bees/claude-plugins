# Ref-driven flattening

## Why

Flattening currently declares dependencies in a JSON payload inside the START marker while the host body may never reference the inlined content — a skill gets dropped into another with no connective tissue dictating how to leverage it, and there is no established way to scope another skill's application from within a skill. The declaration and the prose that motivates it are two disconnected surfaces that drift.

## What Changes

- **BREAKING** — The JSON `deps` payload in the START marker is removed. Dependencies are derived from `/skill-name` references in the source layer: scoped references in prose at the point of use ("Apply /concise-prose to the commit summaries") and ambient references as list items under `## Dependencies`.
- The flatten tool detects and verifies every `/skill-name` reference against sibling skill folders, rewrites bare references to in-file anchor links (`[/concise-prose](#concise-prose)`), and materializes the closure as before — so every reference visibly remains a skill call while resolving to the flattened copy.
- The tool appends a `## Dependencies` section at end of file when refs exist but the section doesn't, and moves the section to the end when it isn't last. Hand-authored content between the heading and the START marker is source; the region stays generated.
- Region ordering becomes topological — every unit appears above the units it references, ties broken by first appearance in the host — establishing a uniform "referenced content is further down" reading pattern.
- A post-materialization link check closes the implicit-detection typo hole: every rewritten anchor must resolve to a heading in-file, and unresolved `/name` references outside fences and self-invocation surfaces are errors.
- Lint inverts the cross-skill slash-reference rule: the ban on `/skill-name` becomes a requirement that every such reference compile (resolve and link).
- apply-over-queue's payload assembly applies the same reference rewrite against its `## <name>` sections.
- Suite-wide hand pass: every skill is reviewed to establish appropriate connective tissue — scoped references at the point of use where the host dictates how a dependency applies, ambient listing where the dependency stacks obviously — and migrated off the JSON declaration.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `skill-dependency-flattening` — declaration moves from JSON payload to verified `/skill-name` references; anchor linking; section placement; topological ordering; link check.
- `skill-source-conventions` — the slash-reference ban is replaced by a compile requirement: references must resolve and link.

## Impact

- `~/.claude/skills/skill-authoring/scripts/flatten_skills.py` — detection, verification, linking, placement, topological ordering, link check, marker simplification.
- `~/.claude/skills/skill-authoring/scripts/lint_skill.py` — inverted slash-reference rule.
- `~/.claude/skills/apply-over-queue/scripts/flatten.py` — reference rewrite in payload assembly.
- `~/.claude/skills/skill-authoring/SKILL.md`, `~/.claude/skills/procedure-authoring/SKILL.md` — doctrine updates (reference audit, Apply-label form).
- Every skill in `~/.claude/skills/` with a flatten region or a citation of another skill — hand migration pass.
- `skills/` mirror regenerated via sync; `scripts/sync_skills.py` freshness gate unchanged in spirit.

# Tasks — ref-driven flattening

## 1. Flatten tool (`~/.claude/skills/skill-authoring/scripts/flatten_skills.py`) — reauthored fresh from the new docstring, no legacy paths

- [x] 1.1 Reference detection and verification: slash-token regex shared with lint, fence-aware, sibling-folder filter, self-invocation exemption; linked and bare forms count identically
- [x] 1.2 Bare START marker only: a payload-bearing START line is a malformed-file error; no parser for the retired JSON form exists anywhere in the tool
- [x] 1.3 `## Dependencies` placement: append section+region at EOF when references exist and no region does; relocate the whole section (hand content + region) to EOF when not last
- [x] 1.4 Topological unit ordering: Kahn's with first-appearance tie-break, replacing BFS-from-declaration order
- [x] 1.5 Convergent link rewriting: bare refs → `[/name](#name)` in the source layer and inside emitted units; idempotent under re-run
- [x] 1.6 Post-materialization link check: every rewritten anchor resolves in the materialized file; unresolved reference-shaped tokens error; nothing written on any error
- [x] 1.7 `--check` strictness: stale = region body, section position, missing section, or unlinked bare ref; the docstring (source of truth) describes only the new contract

## 2. Lint (`~/.claude/skills/skill-authoring/scripts/lint_skill.py`)

- [x] 2.1 Invert the slash-reference rule: unresolved → error, resolved-but-unlinked → stale warning deferring to flatten, linked → pass; fence and self-invocation exemptions carried over; the old ban's code deleted, not gated

## 3. apply-over-queue parity (`~/.claude/skills/apply-over-queue/scripts/flatten.py`)

- [x] 3.1 Apply the same reference detection and anchor rewrite against the payload's `## <name>` sections; SKILL.md notes updated

## 4. Doctrine

- [x] 4.1 skill-authoring SKILL.md: rewrite Declared dependencies → reference-derived declaration (scoped vs ambient), update Reference audit and marker examples
- [x] 4.2 procedure-authoring SKILL.md: admit `Apply [/skill-name](#skill-name) to:` as the scoped-dependency label form

## 5. Suite migration — hand pass over every skill

Review each skill for connective tissue: anything a path through the skill needs is force-loaded and explicitly wired — scoped `/refs` at the point of use where the host dictates how a dependency applies, ambient list items where it stacks obviously. This pass is where the one-time marker conversion happens: strip each existing START payload to the bare form (the new tool rejects payload-bearing markers). Verify each materialized result reads correctly.

- [x] 5.1 reauthor (existing region: concise-prose — restore scoped ref at the Anti-staleness citation)
- [x] 5.2 skill-authoring (existing region: markdown-authoring, description-authoring, concise-prose)
- [x] 5.3 apply-over-queue (existing region: procedure-authoring, concise-prose)
- [x] 5.4 procedure-authoring, git, file-decomposition (doctrine-adjacent; wire or list any latent dependencies)
- [x] 5.5 concise-prose, description-authoring, markdown-authoring, rule-authoring (leaf skills; confirm no refs needed, self-surfaces stay unlinked)
- [x] 5.6 confirm-shared-intent, grounded, principled-pushback, context-mechanics (review citations for promotion to scoped refs)
- [x] 5.7 engaged-time, export-pdf, export-diff (component fan-outs reference skills by bare name today; promote where the host should declare)

## 6. Gates, sync, land

- [x] 6.1 Full-suite gates green: `flatten_skills.py --check`, `lint_skill.py`, repo markdown lint
- [x] 6.2 sync-skills (reconcile + regenerate mirror), then `/git checkpoint` to branch, commit, PR, and merge

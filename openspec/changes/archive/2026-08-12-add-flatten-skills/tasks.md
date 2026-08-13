## 1. Mechanism

- [x] 1.1 Write `skill-authoring/scripts/flatten_skills.py` (refresh + `--check`) per `skill-dependency-flattening` spec: JSON declaration, fence-aware marker parsing, graph-first with cycle error, closure-over-sources dedup, H1→H3/H2→H4 demotion, `${CLAUDE_SKILL_DIR}` sibling rewriting, `-->` guard
- [x] 1.2 Extend `lint_skill.py` with the `skill-source-conventions` checks (structure, portable self-references, slash-reference errors with fence/self exemptions, marker hygiene) — slash-reference check lands as warn until task 3.2 completes, then flips to error
- [x] 1.3 Add `flatten_skills.py --check` to skill-authoring's lint pass and to this repo's sync-skills flow

## 2. First consumers

- [x] 2.1 Rewrite `reauthor` live source: new trigger description, drop "When not to reauthor", keep Scope, declare `concise-prose`, refresh (reference shape: `tmp/skills/reauthor/SKILL.md`)
- [x] 2.2 Convert suite skills' hardcoded `/home/dev/...` bundled-file paths to `${CLAUDE_SKILL_DIR}` form

## 3. Doctrine and migration wave

- [x] 3.1 Rewrite `procedure-authoring`: replace Call/Apply model-mediated constructs; expect body shrink
- [x] 3.2 Suite-wide slash-reference purge (apply-over-queue wave): convert true dependencies to declarations, citations to bare names
- [x] 3.3 Rewrite `/git`: fold operational partials in-place, remove router self-reference, migrate more procedure into `gitflow_*.py` scripts, keep DECISIONS.md out of the invocation path
- [x] 3.4 Rewrite `skill-authoring` § Skill layout (drop per-verb component prescription) and re-scope its applied-disciplines list into dependencies vs citations with the ~26KB closure cost in view
- [x] 3.5 Add reliability-precedence clause to `file-decomposition`
- [x] 3.6 Retire slash-reference expansion from `apply-over-queue/scripts/flatten.py`; operations reference materialized skills directly

## 4. Landing

- [x] 4.1 Full-suite `flatten_skills.py --check` + `lint_skill.py` pass clean
- [x] 4.2 sync-skills: reconcile manifest, regenerate mirror, checkpoint PR
- [x] 4.3 Delete `tmp/skills/` dummies once the live suite embodies the spec

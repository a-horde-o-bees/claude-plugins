# Design — ref-driven flattening

## Context

`flatten_skills.py` and the conventions linter shipped in `add-flatten-skills` with a JSON `deps` payload as the declaration surface and a suite-wide ban on `/skill-name` references. That produced regions with no connective tissue: reauthor carries a concise-prose unit its body cites only as loose prose ("concise-prose § Anti-staleness"), and there is no idiom for scoping a dependency's application. This change makes references the declaration.

## Decisions

### One declaration form: references

Every dependency is a `/skill-name` reference in the source layer. Scoped use sites live in prose (`Apply /concise-prose to the commit summaries`); ambient dependencies are list items under `## Dependencies` above the START marker. The JSON payload dies — deriving the declaration from the text that motivates it eliminates the drift class between "declared" and "wired in". The START marker becomes bare, and the tool carries **no legacy parser**: a payload-bearing START line is malformed, full stop. The one-time conversion of existing markers happens in the migration pass, not in permanent tool code.

**Detection**: candidate regex for slash-prefixed tokens (reusing lint's `(?<![\w./-])/([\w][\w-]*)\b` boundary), filtered to names that are sibling skill folders, outside fences (existing `iter_lines`), excluding the skill's own name. A candidate inside an existing `[/name](#name)` link counts as the same reference (idempotence). Non-sibling candidates like `/usr/bin` fail the sibling filter and fall through to the link-check error only when `/name`-shaped and plausibly a skill reference — concretely: the same regex that lint uses, so tool and lint agree on what "reference-shaped" means.

### Reauthor the tool, don't patch it

`flatten_skills.py` is rewritten fresh from its new docstring rather than incrementally extended: one detection pass over the source layer yields references, links, and the dependency graph together; no dual code paths, no deprecated flags, no retired-format handling. The docstring stays the source of truth for the whole contract. `lint_skill.py` keeps only the inverted rule — the old ban's code is deleted, not gated.

### Convergent link rewriting

Refresh rewrites bare references to `[/skill-name](#skill-name)`. The anchor is the GitHub slug of the unit's demoted H3 title; unit H1s are the folder name, folder names are kebab-case, so slug == folder name. Already-linked references are recognized and left byte-identical, so refresh converges after one pass and `--check`'s byte-compare works unchanged. The same rewrite applies to unit bodies during emission (their references target sibling units in the same closure). Self-invocation references stay unlinked.

### Topological unit ordering

References establish a "look further down" pattern, so every unit must sit above every unit it references. Order = topological sort of the closure (host implicitly the root), ties broken by first-appearance order of references in the host source. Kahn's algorithm with a first-appearance priority queue gives a deterministic result; cycles already abort the run, so the sort always completes. This replaces BFS-from-declaration-order.

### Section placement is tool-owned

`## Dependencies` is appended (with markers) when references exist and no region does, and the whole section — hand content plus region — is relocated to end of file when other sections follow it. Prompt shape: host guidance first, dependency bulk last. `--check` reports wrong position, missing section, and unlinked bare references as stale, so hand drift lands in CI, not silently.

### Post-materialization link check

Implicit detection opens a typo hole the JSON payload didn't have (`/concise-pros` would silently not flatten). Compensating guarantee: after computing each file, every rewritten anchor must resolve to a heading in the materialized text, and every unresolved reference-shaped token errors. Strictly stronger than the JSON form's missing-sibling error.

### Lint inversion, not lint removal

`lint_skill.py` keeps the slash-reference detector but flips its judgment: unresolved → error, resolved-but-unlinked → stale (flatten owns the fix), linked-and-resolvable → pass. Fence and self-invocation exemptions carry over verbatim.

### apply-over-queue parity

`flatten.py` payload assembly emits `## <name>` top-level sections, so the same rewrite targets `#<name>` anchors there. Detection/verification logic is the same contract; the two scripts stay separate implementations per the standing decision (no third consumer, different emission/substitution/lifecycle), with this spec as the shared contract.

### Migration is deliberately hand work

The wave that purged slash references flattened citation into bare names; the script can verify and link references but cannot invent scoping intent. Every suite skill gets a review pass: where the host should dictate *how* a dependency applies, restore a scoped reference at the point of use; where the dependency stacks obviously, list it ambiently. Force-loading everything a path through a skill needs remains the goal — the pass checks connective tissue, not just syntax.

## Risks

- **Tool now edits source prose.** Mitigated by convergence (idempotent rewrite) and `--check` in CI; diffs show the one-time linking pass then go quiet.
- **Anchor collisions.** A source heading whose slug equals a unit anchor would shadow it. The link check validates against the materialized file; a collision surfaces as a duplicate-heading lint (markdown linter already flags these).
- **Order churn.** Switching BFS → topological reorders existing regions once; single mechanical diff, covered by the migration commit.

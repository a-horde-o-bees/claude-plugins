# Pass 2 Refinements — Bin 8

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none — all factual content from the three samples mapped onto existing paths in the consolidated)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `User configuration and authentication` > `userConfig declared but not wired through manifest substitution` — supporting sample: SkinnnyJay--wiki-llm — the existing description covers the case where fields are declared but not substituted in `.mcp.json`/hooks. SkinnnyJay also exhibits the cross-ecosystem-duplication failure mode where `userConfig` is duplicated verbatim into the Cursor manifest (`.cursor-plugin/plugin.json`) with no sync mechanism. Today this concern is buried as a sub-bullet under the *adjacent* `Native userConfig with ${user_config.KEY} substitution` path, but it equally applies here and arguably belongs as a shared sub-bullet visible from both. Suggestion: add a sub-bullet to `userConfig declared but not wired through manifest substitution` mirroring the "Cross-ecosystem duplication" note already present on `Native userConfig with ${user_config.KEY} substitution`.

- `Plugin-component registration` > `Default convention discovery` — supporting sample: SkinnnyJay--wiki-llm — the description covers Claude-side default discovery thoroughly. SkinnnyJay illustrates a specific mismatch: the same plugin tree pairs Claude `plugin.json` (defaults) with `.cursor-plugin/plugin.json` (explicit `rules`/`skills`/`commands`/`agents`/`hooks` paths) — Claude's silence vs Cursor's verbosity for the same content. Suggestion: add a sentence noting "When the same tree publishes to multiple ecosystems, Cursor-style runtimes that demand explicit paths force authors to maintain a parallel manifest while the Claude side stays default-discovered — the two manifests' shape diverges by ecosystem convention."

- `Bin entry mechanism` > `Multi-script bin family / CLI dispatcher` — supporting sample: ShaheerKhawaja--ProductionOS — the existing description covers the multi-verb pattern. The ProductionOS case shows mixed-language bin family (10 bash pos-* tools plus one Node `install.cjs` for `npx productionos@latest`) — bash for plugin-internal tooling, Node for the npm-distributed installer. Suggestion: note the cross-language case as a sub-shape — "When the plugin also distributes via npm, one entry in the bin family is the Node installer (`install.cjs`) carrying `#!/usr/bin/env node` while the rest are bash; the bash tools serve hooks and users with the plugin installed, the Node entry serves new installs via `npx <plugin>@latest`."

- `Tool-use enforcement` > `Stop-event handlers for session-end aggregation` — supporting sample: ShaheerKhawaja--ProductionOS — the description already mentions multi-hook usage. ProductionOS uses three Stop hooks (`stop-session-handoff.sh`, `stop-extract-instincts.sh`, `stop-eval-gate.sh`) that compose: handoff summary + instinct extraction (cross-session learning) + eval gate. Suggestion: the existing description covers this; no sharpening needed if the reconciler considers it sufficiently general.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- ShaheerKhawaja--ProductionOS exhibits both `Self-referential single-plugin marketplace at repo root` and the sample's `strict: false` discipline (which the consolidated treats under `Plugin source binding > strict field default`). The path under `strict field default` reads "absent on every marketplace entry, taking the implicit-true default" but ProductionOS sets `strict: false` explicit. The existing path text already addresses this case ("`strict: false` set on a plugin entry without a corresponding `skills`/`agents`/etc override array reads as defensive ceremony or copy-paste") so the sample fits, but the path name implies "default" which can read as misleading when describing an entry that set `strict: false` explicitly. Reconciler might consider whether `strict field default` should split into two paths (explicit-default-true vs explicit-false-without-narrowing). Flagging not requesting.

- SkinnnyJay--wiki-llm carries a `release.yml` workflow that has never fired (no tags pushed since first commit) — the consolidated has both `Tag-on-main, single branch` (about the branch+tag posture) and `Tag-triggered test verification only` (about what the workflow does). I assigned it to both since they describe different facets: the repo's overall posture vs. the specific automation shape. Surfacing here in case the reconciler prefers one or the other as canonical for "release intent declared via workflow but no tags yet" cases.

- All three samples treat `### bin` as both the level-3 path under `Component composition` and the level-2 role for the bin-entry-mechanism sample-origin. The consolidated path `Component composition > bin` is correct for the inventory observation; the sample-origin focus on bin mechanics flows through `Bin entry mechanism > <specific path>`. No conflict, but worth flagging: the orientation question "what role does the bin observation answer" can route to either depending on whether the answer is "yes, a bin/ directory exists" (Component composition) or "this is HOW the bin works" (Bin entry mechanism). Both are exhibited and both are populated correctly.

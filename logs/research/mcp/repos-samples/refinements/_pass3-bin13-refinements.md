# Pass 3 Refinements — Bin 13

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from the second normalize cycle on this bin's samples. Pass 2 already converted samples to role-tree shape; Pass 3 verified alignment, applied targeted fixes, and surfaced remaining structural concerns. The reconciler integrates accepted refinements into the next consolidated revision.

## Pass 3 fixes applied to samples

> Targeted updates made during this pass; not refinement proposals — already in the samples.

- `viant--mcp.md` Build and packaging — replaced `### npm/Node toolchain` (with body "Not applicable — Go module distribution") with `### Go modules (\`go.mod\` / \`go.sum\`)`. The previous shape was a non-fitting placeholder; the correct canonical path already exists in the consolidated and matches what the Go SDK actually uses (go.mod / go.sum + `go get` / `go build`).
- `viant--mcp.md` Distribution channel — removed `### Source build with make / CMake`. The path is for native build systems (CMake / make); Go builds via `go install` / `go build` are already covered by the sibling `Go module via \`go get\` / \`go install\`` path. The previous body ("Source build available as an alternative") didn't actually anchor to make/CMake.
- `v-3--discordmcp.md` Authentication — removed the `### where credentials come from` artifact heading. It was a leftover fragment (literally the lowercase prose phrase "where credentials come from" used as a heading). Its body content (Discord Developer Portal credentials supplied via `DISCORD_TOKEN` env var) was merged into the existing `### Bot identity (third-party platform)` paragraph since it elaborates the same path's mechanics.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none from Pass 3 on this bin)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Authentication > where credentials come from` — this canonical-tree node appears to be an artifact of the synthesis process rather than an intentional path. It was carried into one bin-13 sample (`v-3--discordmcp.md`) as a literal heading with that lowercase prose phrasing. The reconciler should consider whether to drop this node from the consolidated entirely (it duplicates information that belongs inside the parent path's body) or to rename it to a real path label if the underlying observation is worth preserving as a structural concern. Pass 3 removed the heading from the sample; the consolidated entry remains.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from Pass 3 on this bin)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from Pass 3 on this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`Authentication > where credentials come from` is not a real path.** The phrasing is lowercase prose, not a path label, and the parent role already has dedicated path siblings for every credential-source pattern (`Static API key / token via env var`, `Bot identity (third-party platform)`, etc.). Recommend the reconciler delete this node from the consolidated; supporting samples should fold the content into the role's actual path.
- **Pass 2 `Build and packaging > npm/Node toolchain` placeholder for Go projects.** Pass 2 placed `viant--mcp.md` under `npm/Node toolchain` with body "Not applicable — Go module distribution". This is an anti-pattern — the rule is "include only role/path nodes the sample actually exhibits". Pass 3 corrected to `Go modules (\`go.mod\` / \`go.sum\`)`. Reconciler may want to spot-check other Go samples in the corpus for the same placeholder shape.
- **Pass 2 `Distribution channel > Source build with make / CMake` for Go.** Same Pass 2 placeholder pattern — Go projects don't use make/CMake, but the path was applied with a thin generic body ("Source build available as an alternative"). Pass 3 removed it for `viant--mcp.md`; the canonical Go distribution path (`Go module via \`go get\` / \`go install\``) already covers source consumption. Reconciler may want to spot-check other Go samples for the same misuse.
- **Cross-corpus phrasing audit.** The Pass 3 spawn instructions flagged "Watch for cross-corpus phrasing — samples should describe themselves, not compare to other samples." Re-reading bin 13 samples, several preambles and bodies use comparative phrases ("the lowest in the corpus", "Uncommon floor", "Unusual for vendor-official servers", "contrasts sharply with 50–250-tool servers in the same domain", "Rare among MCP servers"). These compare the sample to the population. Per the principle, sample bodies should describe the sample's own choices; cross-sample comparison belongs in the consolidated. Pass 3 did not strip these because the language is informational about the sample's *posture* (the sample's choice is meaningful precisely because it sits at an extreme), not citation of other samples by name. Surface as a reconciler decision: tighten these phrasings (e.g., "Python 3.13 floor — aggressive vs widely-targeted 3.10" → "Python 3.13 floor"), or accept that adjective-only comparison is allowed.

## Convergence assessment

This bin is **converged**. All eight samples already adhered to role-tree format from Pass 2; Pass 3 found two mechanical alignment issues (both on `viant--mcp.md` related to Go-vs-non-Go build/distribution paths) and one artifact heading (`v-3--discordmcp.md`'s `### where credentials come from`). All three were targeted fixes that did not cascade. No new paths were proposed, no new roles surfaced, no buckets need splitting from this bin. The remaining structural concern (the canonical-tree artifact `Authentication > where credentials come from`) is upstream of any individual sample and only the reconciler can act on it.

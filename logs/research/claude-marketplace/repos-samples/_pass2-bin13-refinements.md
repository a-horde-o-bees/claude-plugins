# Pass 2 Refinements — Bin 13

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

`Tag and release lifecycle > No tags at all` — supporting samples: `damionrashford--trader-os`. The existing description covers untagged plugins broadly. Sharpening: add the case where a repo documents tag conventions in CLAUDE.md ("Tag git releases `v<MAJOR>.<MINOR>.<PATCH>`", "Releases via GitHub Releases tagged `v<SEMVER>`") but has cut zero tags — the conventions exist as future-state documentation but are untested in practice. Distinguishes "no tag discipline" from "documented-but-unused tag discipline."

`Documentation surface > Comprehensive single README + ad-hoc CLAUDE.md` — supporting samples: `damionrashford--trader-os`. Sharpening: add the variant where CLAUDE.md explicitly enumerates supported vs silently-ignored agent frontmatter fields (e.g., supported: `name description model effort maxTurns tools disallowedTools skills memory background isolation`; unsupported: `color hooks mcpServers permissionMode`). Most repos don't document what they're deliberately NOT using; this enshrines the constraint. Worth noting because it surfaces harness-version-specific silently-dropped fields explicitly to contributors.

`Agent declaration conventions > Rich behavior fields (background, isolation, memory)` — supporting samples: `damionrashford--trader-os`. Sharpening: include the constraint that `memory: project` is used uniformly across all agents in some plugins (not just specific roles). Existing description treats these as docs-prescribed-or-not unverified; the trader-os case demonstrates a plugin-wide commitment to these fields with consistent usage.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

`damionrashford--trader-os` notes that CLAUDE.md ALSO contains an explicit list of frontmatter fields that the harness silently drops (`color`, `hooks`, `mcpServers`, `permissionMode`). This sits at the boundary between `Agent declaration conventions` (which catalogs what frontmatter shapes exist) and `Documentation surface` (which catalogs what docs exist). I placed the documentation-surface aspect under "Comprehensive single README + ad-hoc CLAUDE.md" but the underlying observation — that contributors document what's NOT supported as a contributor-facing constraint — could itself be a path under `Agent declaration conventions`. Surfacing for reconciler judgment.

`heliohq--ship` carries a non-standard `<EXTREMELY_IMPORTANT>` XML wrapper in SessionStart context injection. The consolidated already has an "XML-tag emphasis wrapping" path under `Session context loading`; the heliohq--ship case is mapped there cleanly. Surfacing only because the consolidated description is brief; if more samples adopt similar prompt-engineering tag conventions (`<CRITICAL>`, `<URGENT>`, `<EXTREMELY_IMPORTANT>`), the path may warrant elaboration.

`heliohq--ship` ships `tests/test-*.sh` files but `AGENTS.md` documents hook-testing as ad-hoc `echo '<json>' | bash scripts/<hook>.sh` rather than as scripted tests. This is a sub-shape of "Hand-rolled bash tests" — tests exist for some surfaces (orchestration, e2e phases, docs-index generator) but hooks themselves are not test-covered despite the `tests/` directory's existence. Mapped to "Hand-rolled bash tests" but the asymmetry (some surfaces tested, others ad-hoc-documented) is a sharpening candidate.

`heliohq--ship` uses Claude Code's Monitor tool (mentioned in commit `refactor(handoff): replace 30s CI poll with gh watch + Monitor`) for CI watching, which is distinct from `monitors.json`. Consolidated covers `monitors.json absent` but the Monitor-tool-as-alternative isn't currently a path under `Live monitoring`. Mapped under `monitors.json absent` with a clarifying note about the Monitor-tool alternative; a dedicated path may emerge if more samples use this primitive.

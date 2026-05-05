# Pass 2 Refinements — Bin 11

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none — all sample facts mapped cleanly to existing paths)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Per-plugin discoverability metadata > Mixed-by-origin metadata` — `anthropics--claude-plugins-official.md` exhibits a richer instance: same field set varies even within one provenance tier (118/145 entries with `category`; 3 entries with `tags: ["community-managed"]`; 1 entry with `keywords`); the existing description focuses on first-party vs vendored vs externally-pulled split, but the actual mechanism is finer-grained — different field sets per individual plugin entry regardless of provenance, with no enforced schema across siblings. Sharpening suggestion: note that mixed-by-origin can manifest as "field-set varies per entry within a single provenance tier" not just across tiers.

- `Plugin source binding > Skill-carving via shared root + \`skills\` override` — `anthropics--claude-plugins-official.md` carves skill subsets out of upstream repos via `strict: false` paired with `git-subdir`-style or `url` source kinds, not just the repo-root case. The existing description focuses on `source: "./"` + `strict: false` + `skills` override; the `netsuite-suitecloud` entry uses an upstream-mirrored `skills: ["./packages/agent-skills/...", ...]` instead. Sharpening suggestion: clarify that skill-carving via marketplace-entry `skills` override applies to any source kind (relative-root, url, git-subdir), not only `source: "./"`.

- `Source-pin maintenance > Scheduled bot-PR with fairness ordering` — `anthropics--claude-plugins-official.md` confirms the GitHub-App-token requirement (`app-id: 2812036`) is driven by org policy that forbids `GITHUB_TOKEN` from creating PRs; the existing description mentions GitHub App token but doesn't name org policy as the rationale. Also: `--force-with-lease` push onto a date-stamped branch `auto/bump-shas-$(date +%Y%m%d)` is the specific branch convention. Sharpening suggestion: surface the org-policy rationale and the date-stamped branch convention.

- `Plugin-component registration > Marketplace-entry-only definition (no \`plugin.json\`)` — `anthropics--healthcare.md` adds a third shape: single-skill-carve where `source: "./"` + `strict: false` + `skills: ["./<skill-dir>"]` produces a 1:1 plugin-to-skill mapping. The existing description names two shapes (skill-carving on multi-plugin monorepos, hollow-umbrella with full lspServers). Sharpening suggestion: add the single-skill-carve-from-shared-root variant where multiple sibling plugins each carve exactly one skill from the same `source: "./"`.

- `Channel distribution > No pinning surface` — `anthropics--claude-plugins-official.md` notes a partial mitigation: for `git-subdir` sources, the `sha` pins the bump workflow maintains do provide upstream-content reproducibility once pinned, even though the marketplace manifest itself has no channel. Sharpening suggestion: clarify that "no pinning surface" at the marketplace level can coexist with per-entry SHA pinning that gives upstream reproducibility (the SHA pinning per external entry path covers the same observation from a different angle).

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — all observed facts fit existing roles)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- The `tags: ["community-managed"]` field in `anthropics--claude-plugins-official.md` arguably matches both `Per-plugin discoverability metadata > Mixed-by-origin metadata` (because it varies by provenance — flagging community vs Anthropic) AND `Marketplace manifest layout > Custom non-schema fields on marketplace entries` (because the field is being used as a de-facto extension point for provenance signaling). I placed it under the per-plugin-discoverability role since the docs reference `tags` as a documented per-plugin field; if the reconciler wants to surface it as a custom-field example instead, that's a judgement call. Same fact, two role mappings — flag for reconciler awareness.

- `anthropics--healthcare.md` ships a `release.yml` that triggers test-script-style packaging on `*-skill/` glob — naming-convention-driven artifact discovery. Consolidated path "Skill-zip build via filesystem glob" mentions this variant. This was an easy match but worth noting that the consolidated path description already absorbs both `*/` (any directory with SKILL.md) and `*-skill/` (suffix-bound) variants; sample 3 specifically uses the suffix-bound form.

- `anthropics--financial-services-plugins.md` ships an `~/Desktop/<plugin>-setup.md` workflow-state file consumed by `claude-in-office`'s setup command. I placed under `Session context loading > File-backed context written at SessionStart`, but strictly speaking this isn't a SessionStart-fired hook — it's invoked by the user running the setup command. The path name "File-backed context written at SessionStart" is technically a misnomer here. Reconciler may want to consider a sibling path (e.g., "User-visible markdown setup log") for setup-command-driven file workflow state, or treat the existing path as broad enough.

- `anthropics--healthcare.md`'s `claude-skill-review.yml` uses dynamic matrix construction over `find . -name SKILL.md`. This matches the consolidated description in `Marketplace validation > LLM-driven PR review` ("A dynamic matrix over `find . -name SKILL.md` runs one review job per affected skill so the workflow auto-adjusts to new skills without edits"). Already absorbed; no action needed.

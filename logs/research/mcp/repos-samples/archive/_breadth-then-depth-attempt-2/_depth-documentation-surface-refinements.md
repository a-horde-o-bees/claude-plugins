# Depth Pass Refinements — Sample > Documentation surface

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

`Sample > Documentation surface` (role-level)
- Existing role description omits that the line between sibling paths is the *structural form* of supplementary surfaces — single README vs. README + adjunct files vs. README + dedicated subdirectory vs. README + hosted site. Several adoption confusions trace back to this not being stated. Add one sentence to the role-level prose making explicit that paths capture the *form* of additional surfaces beyond the README, and that a sample exhibiting more than one form is multi-tagged.
- Suggested addition (after existing prose): "Paths beyond `README as the canonical surface` describe the *additional form* the project takes — adjunct top-level files, a `docs/` subdirectory, an `examples/` subdirectory, a hosted site, agent-facing meta-documentation, etc. A project with multiple forms is tagged under each."

`Sample > Documentation surface > README as the canonical surface`
- Description says "Universal" — true in the sense that nearly every sample has a README, but as a distinguishing path it should mark the case where the README is the *only* documentation surface (or so dominant that supplementary files are negligible). Multiple supporting samples actually exhibit additional surfaces and are dual-tagged or could be (`microsoft--playwright-mcp.md` mentions CONTRIBUTING.md and SECURITY.md alongside; `redis--mcp-redis.md` mentions an `examples/` directory; `modelcontextprotocol--servers.md` mentions per-server READMEs). The description should sharpen "canonical" to mean "the only or near-only surface".
- Suggested replacement: "Single README.md is the only meaningful documentation surface — purpose, install, config, host integration, and tool inventory all consolidated. Length and depth vary widely. When supplementary surfaces exist (`docs/`, `examples/`, per-host sections, agent-facing meta), additional paths apply alongside this one."

`Sample > Documentation surface > Per-host README integration sections`
- Existing description is accurate but doesn't sharpen the distinction from the README-canonical case where the README also embeds host-specific snippets (e.g., `riza-io--riza-mcp` has a Claude Desktop JSON snippet inside README but isn't tagged Per-host). The distinguishing structural feature is *labeled per-host sections* — discrete subsection per host with its own snippet — not just one or two embedded snippets. Cross-corpus evidence shows the supporting samples consistently describe 4+ hosts each with its own block (`alpacahq` 5 hosts, `exa-labs` 15+, `github` 5, `mongodb-js` 5, `executeautomation` 4, `sandraschi` 4).
- Suggested replacement: "README contains discrete labeled subsections per supported host (Claude Desktop, Cursor, VS Code, JetBrains, etc.), each with its canonical config snippet. Distinguished from README-canonical-with-embedded-host-snippets by structure: this path requires per-host subsection blocks, typically four or more hosts. Common where the server targets multiple host ecosystems."

`Sample > Documentation surface > README plus docs directory`
- Description names a `docs/` directory specifically, but supporting samples include cases that don't fit cleanly: `bhauman--clojure-mcp` has multiple top-level supplementary markdown files (PROJECT_SUMMARY.md, CONFIG.md, FAQ.md, BIG_IDEAS, CHANGELOG, LLM_CODE_STYLE) — none in a `docs/` subdirectory; `pragmar--mcp-server-webcrawl` uses a `sphinx/` directory plus `docs/`; `getsentry--sentry-mcp` describes "monorepo workspace scripts" which is unrelated to docs at all (likely a mis-placement, see below). Either the description should broaden to "supplementary documentation files beyond the README" or the path should split (see Sub-axis observations).
- Suggested replacement: "Supplementary documentation beyond README — typically a `docs/` subdirectory holding longer-form material (architecture, per-tool deep dives), or multiple top-level supplementary markdown files (PROJECT_SUMMARY, CONFIG, FAQ, etc.). Surfaces in larger or more mature projects where README alone exceeds a comfortable single-file length."

`Sample > Documentation surface > README + examples/`
- Description names a runnable `examples/` directory but half the supporting samples don't have one. `chroma-core--chroma-mcp` and `marlonluo2018--pandas-mcp-server` describe `.env.example` (a single config-template file, not a directory); `hugoduncan--mcp-clj` describes "representative usage patterns in the README" (no directory). Only `apollographql`, `conikeec`, `crystaldba` cleanly fit. Description should be tightened, and the off-fit samples should move (see Mis-placed samples).
- Suggested replacement: "README points to a runnable `examples/` subdirectory containing copy-paste sample clients, configurations, or usage walkthroughs. Appropriate when integration is best learned by running a small sample. Distinct from a single `.env.example` config-template file, which belongs under Configuration delivery."

`Sample > Documentation surface > GitHub Pages / hosted docs site`
- Description names GitHub Pages first but supporting samples cover varied hosting (gofastmcp.com custom domain, ReadTheDocs, Hugo `.hugo/` build artifacts, a `website/` subdirectory in repo). The distinguishing feature is "documentation hosted off-repo for discoverability/SEO, regardless of host platform." Description already mentions ReadTheDocs but title leads with GitHub Pages; consider re-phrasing.
- Suggested replacement: "External documentation site published alongside or in lieu of repository docs — GitHub Pages, ReadTheDocs, custom-domain Hugo build, or in-repo `website/` build directory. Provides discoverability outside GitHub and supports substantial reference material beyond a README."

`Sample > Documentation surface > Bundled \`cursor_rules.md\` / AI-guidance content`
- Path name is specific to `cursor_rules.md` but supporting samples include very different content types: `bhauman--clojure-mcp` ships `LLM_CODE_STYLE.md` (style guide for the LLM); `hannesrudolph--sqlite-explorer-fastmcp-mcp-server` ships `fastmcp-documentation.txt` + `mcp-documentation.txt` (framework reference docs for LLM ingestion — overlaps strongly with the `llms.txt` path, which one supporting sample tagged differently); `slackapi--slack-mcp-plugin` ships `commands/` and `skills/` directories (Claude Code skill artifacts, not cursor-rules). The path is currently bundling three distinct things. See Mis-placed samples and Proposed bucket splits.
- Suggested replacement (assuming no split): "Bundled markdown or text content shipped with the server intended for the host's LLM to read as guidance — `cursor_rules.md`, `LLM_CODE_STYLE.md`, or similar. Neither MCP tool nor MCP prompt — just bundled context the host's LLM is expected to load. Appropriate when correct usage requires conventions the per-tool descriptions cannot fully convey. Distinct from `llms.txt` (digestible LLM-ingestion docs about the project) and from runnable agent skills in `skills/` or `commands/`."

`Sample > Documentation surface > \`llms.txt\` / \`llms-full.txt\``
- Description already covers the single-large-file variant well. No sharpening needed beyond noting the boundary with `cursor_rules.md`-style guidance: `llms.txt` is *project documentation reformatted for LLMs*; `cursor_rules.md` is *behavioral guidance for the LLM when using the project*. The two roles overlap in audience but differ in content.
- Suggested addition (final sentence): "Distinct from `cursor_rules.md`-style guidance — `llms.txt` is project documentation reformatted for LLM consumption, whereas `cursor_rules.md` is behavioral guidance for the LLM when invoking the server."

`Sample > Documentation surface > Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)`
- Bullet list inside this path enumerates CLAUDE.md, `.cursorrules`, `.mcp.json`. Supporting samples include `geropl--linear-mcp-go` with a `memory-bank/` directory (Cline memory-bank convention) — this is meta-documentation for AI authoring, not currently captured by any of the three bullets. Either add a fourth bullet covering Cline memory-bank-style conventions or generalize the path's framing.
- Suggested addition (fourth bullet): "**`memory-bank/` directory (Cline convention)** — Repo carries a `memory-bank/` directory of context/memory files following the Cline memory-bank convention, indicating the maintainer dogfoods Cline-assisted authoring. Same role as CLAUDE.md or `.cursorrules` for a different agent ecosystem."

`Sample > Documentation surface > \`agents/\` example directory`
- The single supporting sample (`exa-labs--exa-mcp-server`) describes "Skills directory with specialized research templates" — this is a `skills/` directory, not literally an `agents/` directory. The path name is wrong relative to its only evidence. Either rename the path or move the sample. Cross-reference: `slackapi--slack-mcp-plugin` ships `commands/` and `skills/` directories (currently tagged under cursor_rules but a better fit here under a renamed path).
- Suggested replacement: "`agents/` or `skills/` example directory — Runnable example agents, prompts, or skill artifacts demonstrating how an agent should drive the server. Appropriate when authorship benefits from concrete invocation patterns rather than abstract protocol description."

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

`Sample > Documentation surface > README plus docs directory`
- Sub-pattern: "supplementary docs at repo root" vs. "supplementary docs in a dedicated `docs/` directory". Supporting samples split roughly 1 (`bhauman` — root-level supplementary files) vs. 8 (samples with `docs/` directory or hosted-docs build directory). The 1-sample minority does not warrant a path split, but the description should fold both forms in.

`Sample > Documentation surface > README as the canonical surface`
- Sub-pattern within README-canonical: README that embeds host snippets vs. README that doesn't. Borderline overlap with Per-host README integration. The dividing rule is structure (labeled subsections vs. embedded snippets), already captured in proposed sharpening. No split warranted; the cross-corpus visibility just reaffirms that "Per-host README integration sections" requires a structural threshold to fire.

`Sample > Documentation surface > Bundled \`cursor_rules.md\` / AI-guidance content`
- Sub-pattern: three distinct content types are currently lumped together — (a) LLM behavioral guidance (`cursor_rules.md`, `LLM_CODE_STYLE.md`), (b) framework/protocol reference docs for LLM ingestion (`fastmcp-documentation.txt` etc.), (c) runnable skill/command artifacts (`skills/`, `commands/` directories). The reconciler should consider whether (b) belongs under `llms.txt` and (c) belongs under the renamed `agents/` example directory. See Proposed bucket splits.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. The paths under this role are largely distinct; the boundary cases are placement decisions, not bucket-overlap signals.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

`Sample > Documentation surface > Bundled \`cursor_rules.md\` / AI-guidance content`
- Proposal: do not split, but tighten via mis-placement (move `hannesrudolph` to `llms.txt` path; move `slackapi` to renamed `agents/` or `skills/` path). The remaining 2 supporting samples (`bhauman` LLM_CODE_STYLE, `jbeno` cursor_rules.md) are clean fits for the path's intended meaning. A 2-sample remainder is light but the path's distinction from `llms.txt` (behavioral guidance vs. ingestion docs) is real and worth preserving.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

- `chroma-core--chroma-mcp.md` currently under `README + examples/` better fits `README as the canonical surface` (or no doc-surface tag beyond README) because the sample's evidence is `.env` example file plus a Claude Desktop snippet plus inline CLI docs in README — none of these is a runnable `examples/` directory. The `.env.example` belongs under Configuration delivery, not Documentation surface.

- `marlonluo2018--pandas-mcp-server.md` currently under `README + examples/` better fits `README as the canonical surface` (already tagged there) because the sample's evidence is `.env.example` plus per-OS Claude Desktop paths — no runnable examples directory. The "README + examples/" tag should be removed.

- `hugoduncan--mcp-clj.md` currently under `README + examples/` better fits `README as the canonical surface` because the sample's evidence is "README includes representative usage patterns" — the patterns are inside the README, not in an `examples/` subdirectory. The README content already counts as canonical-surface depth.

- `getsentry--sentry-mcp.md` currently under `README plus docs directory` better fits `README as the canonical surface` because the sample's evidence is "README plus monorepo workspace scripts (`pnpm -w run cli`)" — `pnpm -w run cli` is not a documentation directory; it's a workspace-scripts capability and belongs under Build / Repository layout. The Documentation-surface tag here looks like a mis-placement during pass 1.

- `hannesrudolph--sqlite-explorer-fastmcp-mcp-server.md` currently under `Bundled cursor_rules.md / AI-guidance content` better fits `\`llms.txt\` / \`llms-full.txt\`` because the bundled files (`fastmcp-documentation.txt`, `mcp-documentation.txt`) are framework reference documentation curated for LLM ingestion, not behavioral guidance. The `llms.txt` path's existing description already includes "Some projects ship a single large LLM-ingestion doc under a different filename (e.g., `llm_mcp_docs.txt`) that fits the same role" — these `*-documentation.txt` files fit that note exactly.

- `slackapi--slack-mcp-plugin.md` currently under `Bundled cursor_rules.md / AI-guidance content` better fits a renamed `agents/` or `skills/` example directory path (or could be tagged under `Sample > Claude Code plugin / skill wrapper > .claude-plugin/ wrapper` since `commands/` and `skills/` directories at the repo root are typical Claude Code plugin artifacts). The "AI-guidance content" framing doesn't capture that these are runnable client-side agent artifacts, not bundled prose.

- `modelcontextprotocol--servers.md` currently has both `Per-host README integration sections` and `README as the canonical surface` but the README-canonical entry says "Top-level README plus per-server READMEs" — the "per-server READMEs" piece matches the `Per-subserver README in monorepo` path, which is currently tagged on a different sample (`pathintegral-institute--mcp.science.md`). Recommend adding `Per-subserver README in monorepo` tag to `modelcontextprotocol--servers.md` (or moving the per-server-READMEs note from the README-canonical entry into a Per-subserver entry).

- `samuelgursky--davinci-resolve-mcp.md` currently under `README plus docs directory` could be additionally tagged under `README + examples/` because the evidence explicitly says "README plus `docs/` and `examples/` subdirectories" — both paths' criteria are met but only `docs/` is currently tagged.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

- **The `examples/` token is overloaded.** Across the corpus, "examples" surfaces in multiple distinct senses: a runnable `examples/` subdirectory of client/server samples (the path's intended meaning), a single `.env.example` file (config template, not docs), and "representative usage patterns" inline in the README. These three appear roughly equally distributed across the 6 supporting samples for `README + examples/`. Without a stricter rule, future researchers will continue to mis-tag.

- **Per-host integration is on a continuum, not a binary.** Several samples under `README as the canonical surface` (`mukul975`, `paypal`, `riza-io`, `rohitg00`, `sandraschi`, `ppl-ai`) describe README content that includes 1–4 host-specific snippets but lacks the labeled-section structure of the Per-host path. The line between "embedded host snippet" and "per-host integration section" is a structural threshold rather than a content threshold; cross-corpus visibility makes this fuzziness obvious. The proposed Per-host description sharpening (require labeled subsections, typically 4+) operationalizes the threshold.

- **AI-guidance documentation has fractured into multiple emerging conventions.** The corpus shows `llms.txt`/`llms-full.txt`, `cursor_rules.md`/`LLM_CODE_STYLE.md`, `CLAUDE.md`, `.cursorrules`, `.mcp.json`, `memory-bank/`, and bundled `*-documentation.txt`/`*_docs.txt` ingestion files — all distinct conventions targeting different agents and serving different roles (ingestion docs vs. behavioral rules vs. dev-environment wiring). The current path structure splits them three ways (`llms.txt`, `cursor_rules.md`, agent-facing meta-doc) but the boundaries between buckets are not crisp. A future reconciliation pass that rationalizes by *audience and role* (LLM consumes vs. IDE-agent reads vs. authoring-agent reads) might cut cleaner than the current name-based split.

- **Documentation surface vs. Distribution channel overlap.** A few samples' Documentation-surface entries describe artifacts that are arguably distribution-related rather than documentation-related: `redis--mcp-redis.md`'s mention of `server.json` for MCP server registry wiring is distribution-channel content; `pathintegral-institute--mcp.science.md`'s GitHub Pages site is partly a discovery surface (distribution-adjacent) and partly a docs surface. The role's framing is internally consistent but reconcilers should be aware that some sample evidence pulled in here belongs in sibling roles.

- **Adoption tail is largely accurate but title-fragile.** Three single-sample paths (`CITATION.cff`, `Per-subserver README in monorepo`, `Split USER_GUIDE / DEVELOPER_GUIDE`, `agents/ example directory`) are each a real, distinct pattern — but each is currently anchored to its single supporting sample's idiosyncrasies. `agents/` should be `agents/` or `skills/` (the only sample is `skills/`); `Per-subserver README` will gain a second sample if `modelcontextprotocol--servers.md` is re-tagged as suggested. None of these warrants merging or removal — they are real long-tail patterns that should remain visible — but their names should not be too tightly coupled to the single sample.

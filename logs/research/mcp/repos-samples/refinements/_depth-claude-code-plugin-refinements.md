# Depth Pass Refinements — Sample > Claude Code plugin / skill wrapper

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

**Sample > Claude Code plugin / skill wrapper** (role-level prose) — Current text: *"Whether the server ships an in-tree Claude Code skill or plugin definition, distinguishing 'MCP server only' from 'MCP server + first-class Claude Code integration.'"* Cross-corpus evidence shows the role splits on three structural axes the description bundles into one binary:

- *Wrapper vs no wrapper* (the binary the description names) — 36 bare vs 8 wrapped.
- *Plugin manifest vs skill files* (the wrapped split) — `.claude-plugin/` (manifest-driven, 4) vs `.claude/skills/` or `claude-code/` (skill-files-driven, 3).
- *Full installable plugin vs marketplace-discovery-only* (within `.claude-plugin/`) — 4 full plugin manifests vs 1 marketplace.json-only entry.

The current binary framing hides the second and third axes. Eight wrapper samples cluster across three sub-shapes that have meaningfully different lifecycle implications (plugin install/update lifecycle vs skill discovery vs marketplace surfacing).

Sharpened text addition — *"Within wrapped projects (8 of 44 samples), three sub-shapes appear: full plugin manifest under `.claude-plugin/` (Claude Code's plugin install/update lifecycle governs the server), skill files under `.claude/skills/` or `claude-code/` (the server is discoverable as a Claude Code skill, not as a plugin), and `.claude-plugin/marketplace.json` alone (marketplace-UI discovery without a full installable plugin). The sub-shapes carry different lifecycle implications — plugin manifest binds to Claude Code's update mechanism; skill files participate in skill discovery; marketplace-only is a directory listing on top of an existing distribution."*

**Sample > Claude Code plugin / skill wrapper > Bare MCP server, no Claude Code wrapper** — Current text: *"Server ships only the MCP surface; users wire it via `claude mcp add` or JSON config. Most common path."* Accurate but bland; 36 of 44 samples is the supermajority and the description doesn't surface that scale or what differentiates "bare" cases. Cross-corpus evidence:

- All 36 entries explicitly note absence of `.claude-plugin/` or `.claude/skills/`. The bin is defined by absence, not by any positive feature.
- Several samples within this bucket nonetheless ship Claude-Code-relevant content elsewhere: SDK/library projects (mark3labs, metoro-io, modelcontextprotocol/kotlin-sdk) note that no wrapper is appropriate because the consumer is another program; remote-endpoint-only projects (cloudflare, awslabs/mcp-lambda-handler, sandraschi via MCPB) note that the server is reached via URL rather than installed; configs-only repos (none in this bin — but slackapi is wrapped, suggesting the configs-only pattern bifurcates by whether plugin wrappers are also shipped).
- Several samples (modelcontextprotocol/servers, marlonluo2018, mongodb-js, opensearch-project, paypal) explicitly distinguish "no `.claude-plugin/` directory" from "no Claude Code support" — they support Claude Code via standard `claude mcp add` / `.mcp.json` (host integration) without packaging themselves as a plugin.

The path is structurally "no positive Claude-Code packaging declaration" — not "no Claude Code support." Description should clarify the boundary so readers don't conflate "bare under this role" with "no Claude Code integration anywhere" — the same project may have rich Claude Code Host integration content (under that role) while being bare under this role.

Sharpened text suggestion — *"Server ships only the MCP surface with no in-tree Claude Code packaging declaration (`.claude-plugin/` directory, `.claude/skills/`, or `claude-code/` skill files). Users wire it via `claude mcp add` or `.mcp.json` — those mechanisms belong under Host integration > Claude Code, not here. The bin captures the packaging posture, not the integration posture: a project bare under this role can still have rich Claude Code Host integration content. Default for SDK/library projects (consumer is another program), remote-endpoint-only servers (reached via URL, no install step), and the long tail of MCP servers that haven't been packaged as plugins."*

**Sample > Claude Code plugin / skill wrapper > `.claude-plugin/` wrapper** — Current text: *"Server ships a Claude plugin manifest with dedicated CLI commands. Appropriate when the team wants Claude Code's plugin install/update lifecycle to govern the server's lifecycle."* Cross-corpus evidence shows four samples with structurally different `.claude-plugin/` content:

- exa-labs — `.claude-plugin/plugin.json` carries an HTTP server config (`type: http`, `url: https://mcp.exa.ai/mcp?client=claude-code-plugin`, custom header `x-exa-source: claude-code-plugin`). The plugin manifest is wrapping a *hosted* MCP server — the plugin is install metadata pointing at a remote endpoint.
- motherduckdb — `.claude-plugin` wrapper "with dedicated CLI commands for Claude Code." Matches the current description.
- slackapi — `.claude-plugin/` directory present, but the entire repo is configs-only (server runs at `mcp.slack.com`). The plugin wrapper is part of a multi-host plugin-wrapper layout (paired with `.cursor-plugin/`).
- stripe — `.claude-plugin/` directory at repo root; full plugin layout present alongside the raw MCP entry point.

The current description captures motherduckdb's flavor only ("dedicated CLI commands"). The path actually spans: (1) plugin-as-launcher for hosted servers (exa-labs), (2) plugin-with-CLI-commands (motherduckdb), (3) plugin-as-config-bundle (slackapi), (4) plugin alongside raw MCP entry (stripe). "CLI commands" is one possible content; not the defining feature.

Sharpened text suggestion — *"Server ships a `.claude-plugin/plugin.json` manifest. Four sample-shape variants appear in the corpus: plugin-as-launcher pointing at a hosted MCP endpoint (exa-labs's `.claude-plugin/plugin.json` carries `type: http` with the remote URL), plugin-with-dedicated-CLI-commands extending Claude Code (motherduckdb), plugin-as-config-bundle within a configs-only repo whose server runs remotely (slackapi, paired with `.cursor-plugin/` for multi-host plugin-wrapper coverage), and plugin alongside a raw MCP entry point (stripe — both shapes ship together so consumers can pick install path). The unifying property is that Claude Code's plugin install/update lifecycle governs the artifact; what gets installed varies."*

**Sample > Claude Code plugin / skill wrapper > `.claude/skills/` directory in repo** — Current text: *"Repo contains Claude Code skill definitions alongside the MCP server source. Skills wrap the MCP tool surface in Claude Code workflow patterns. Appropriate when the vendor wants the server discoverable via Claude Code skills, not just as a raw MCP endpoint."* Cross-corpus evidence: 2 samples — blazickjp (`skills/` directory at repo root, not `.claude/skills/`) and neondatabase (`.claude/skills/` per the sample content). The path heading says `.claude/skills/` but blazickjp uses bare `skills/` — same pattern, different placement. The description's claim that skills "wrap the MCP tool surface in Claude Code workflow patterns" is plausible but neither sample's content surfaces this explicitly; the evidence is just "skill files shipped alongside server source." The sharpened description should not assert "wrap the MCP tool surface in workflow patterns" as a corpus-observed fact — it's an assumption from how skills work, not from the samples.

Sharpened text suggestion — *"Repo ships Claude Code skill definitions alongside the MCP server source — typically under `.claude/skills/` (neondatabase) or a top-level `skills/` directory (blazickjp). The two placements carry the same intent: surface the project to Claude Code as a skill (independent of plugin packaging). Distinct from `claude-code/` directory with skill files (that path's defining trait is the directory name, not the placement under `.claude/`)."*

**Sample > Claude Code plugin / skill wrapper > `claude-code/` directory with skill files** — Current text: *"Sibling top-level directory carries Claude Code skill files; the README documents skill-file installation alongside MCP server installation. Appropriate as an explicit 'first-class Claude Code support' signal beyond raw skill definition placement."* Cross-corpus evidence: 1 sample (openags/paper-search-mcp) with content "`claude-code/` directory contains Claude Code skill files — explicit skill-layer integration shipped in-tree alongside the MCP server (rather than just host-config JSON). First-class plugin wrapper co-located with server."

Note the openags sample calls the `claude-code/` directory a "first-class plugin wrapper," but a `claude-code/` directory of skill files is not a plugin wrapper in the `.claude-plugin/plugin.json` sense — it's skill files outside both the plugin manifest convention and the canonical `.claude/skills/` location. The path likely captures a non-canonical placement choice that predates or sidesteps the canonical convention. With one sample, it's hard to tell whether this is a stylistic choice (the author preferred `claude-code/` to `.claude/skills/`) or signals a different distribution intent.

Sharpened text suggestion — *"Repo ships skill files under a top-level `claude-code/` directory (not `.claude/skills/`). Single sample in the corpus (openags); the placement is non-canonical relative to `.claude/skills/`. Whether this signals a different distribution intent or simply the author's directory-naming preference isn't observable from one sample. Operationally close to `.claude/skills/ directory in repo` — see also possible bucket merge."*

**Sample > Claude Code plugin / skill wrapper > `.claude-plugin/marketplace.json` only** — Current text: *"Marketplace discovery metadata without a full plugin.json. Lets the project surface in Claude's marketplace UI without becoming a full installable plugin — a discovery hook on top of the existing MCP-server distribution."* Cross-corpus evidence: 1 sample (upstash/context7) — content matches the description exactly. Description accurate; rare. Marketplace-only is a layer on top of an existing distribution channel (here, the hosted MCP endpoint).

Description is accurate; no sharpening needed beyond noting that this path can co-exist with any other path under this role conceptually (marketplace-only is a discovery layer, not a packaging choice that excludes others) — but in the corpus, the only sample using it is hosted-only, so the co-existence isn't demonstrated.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

**Sample > Claude Code plugin / skill wrapper > `.claude-plugin/` wrapper** — Sub-axis: *what the plugin manifest actually wraps*.

- Plugin-as-launcher for hosted MCP endpoint (1 sample — exa-labs, `type: http`).
- Plugin-with-dedicated-CLI-commands (1 sample — motherduckdb).
- Plugin-as-config-bundle in configs-only repo (1 sample — slackapi).
- Plugin alongside raw MCP entry point (1 sample — stripe).

Whether to split: each sub-shape has 1 sample — splitting at this scale is premature. Fold into description (sharpening above does this). Reconciler should track whether future research reveals one shape dominates; the current corpus shows wide variance with no concentration.

**Sample > Claude Code plugin / skill wrapper** (role level) — Sub-axis: *whether the wrapper is the primary distribution mechanism vs an additional layer*.

- Primary distribution (3 samples — exa-labs's plugin manifest IS how Claude Code consumes the hosted endpoint; motherduckdb's CLI commands are the dedicated Claude-Code path; openags's `claude-code/` directory is the explicit Claude-Code surface).
- Additional layer (4 samples — slackapi, stripe, blazickjp, neondatabase, getsentry — all ship plugin/skill wrappers alongside another distribution channel; the wrapper is a Claude-Code-specific addition, not the only path).
- Discovery-only (1 sample — upstash's marketplace.json is purely a directory listing).

Whether to split: the axis is meaningful but not crisp from this evidence alone — each sample's "primary vs additional" framing depends on author intent that isn't always documented. Fold as an observation in role-level prose; do not split paths.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

**Sample > Claude Code plugin / skill wrapper > `.claude/skills/` directory in repo** + **Sample > Claude Code plugin / skill wrapper > `claude-code/` directory with skill files** — Both paths describe the same packaging shape: Claude Code skill files shipped in-tree as a directory alongside the MCP server. The split is by directory naming convention only:

- `.claude/skills/` (canonical placement; 2 samples — blazickjp uses bare `skills/`, neondatabase uses `.claude/skills/`).
- `claude-code/` (non-canonical placement; 1 sample — openags).

Three samples in total exhibit "skill files shipped in-tree alongside MCP server source." The directory placement varies (`.claude/skills/`, `skills/`, `claude-code/`) but the underlying packaging choice is the same: ship skills, not a plugin manifest.

Recommendation: merge into one path *Skill files shipped in-tree* with description noting the placement varies (`skills/`, `.claude/skills/`, `claude-code/`) and that these are observed naming choices rather than functionally distinct packaging shapes. Alternative: keep both if the canonical `.claude/skills/` placement is operationally privileged by Claude Code (a tooling discoverability test would settle this) — but at this corpus scale, the merge produces a cleaner description and consolidates evidence.

Caveat: the prior depth pass on Host integration noted that `claude-code/` and `skills/` are "skill-sibling directories shipping Claude Code skill files alongside the MCP server" — confirming the merge framing across roles.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None at this corpus scale. The most heterogeneous path is `.claude-plugin/ wrapper` (4 samples across 4 sub-shapes), but each sub-shape has only 1 sample — splitting at this scale is premature. Description sharpening surfaces the variance without restructuring.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

None observed at the path level within this role. All 36 "Bare" entries explicitly state the absence of a wrapper, all 4 `.claude-plugin/` entries show plugin manifests, the skills entries show skill files, and upstash genuinely has marketplace.json only.

**Cross-role mis-placement observation (not within this role):**

The Host integration > `.claude-plugin/` directory in repo path has 2 supporting samples (getsentry, slackapi), and the prior depth pass flagged that stripe likely belongs there too. Meanwhile, this role's `.claude-plugin/ wrapper` path has 4 samples (exa-labs, motherduckdb, slackapi, stripe) — slackapi and stripe appear in both. **getsentry appears only under Host integration, not under this role's `.claude-plugin/ wrapper` path** — this is a corpus-level inconsistency. If `.claude-plugin/` packaging is the defining trait of "wrapper" under this role, getsentry should appear here too. Reconciler check: pull getsentry's source content and verify the `.claude-plugin/` presence; either add to `.claude-plugin/ wrapper` here or move from Host integration if the directory is incidental.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

- **The role overlaps significantly with Host integration > Claude Code and Host integration > `.claude-plugin/` directory in repo.** The prior depth pass on Host integration (line 268 of that report) called out: *"The `Sample > Claude Code plugin / skill wrapper` role exists at top level — significant overlap with Host integration > Claude Code. Many of the integration mechanisms (`.claude-plugin/`, `skills/`) are arguably about Claude-Code-specific packaging, and the top-level role probably owns them."* Cross-corpus inspection from this side confirms: every supporting sample under `.claude-plugin/ wrapper` (4) also has a corresponding Host integration > Claude Code entry, often with the same `.claude-plugin/` content described. The two roles are reading the same artifact from different angles — Host integration views `.claude-plugin/` as a Claude Code consumption mechanism; this role views it as a packaging shape. **Reconciler decision needed**: either (1) make this role authoritative for `.claude-plugin/`-related packaging and have Host integration > Claude Code reference it for those mechanisms; or (2) collapse this role into Host integration > Claude Code as a sub-classification; or (3) keep both roles and make the boundary crisp ("packaging shape" vs "host-launch mechanism"). Option (1) preserves the role distinction and cleans up the duplication; option (3) is the lightest change.

- **The role is dominated by absence** — 36 of 44 samples (82%) are "bare." The 8 wrapped samples are the interesting population, but the role's adoption table foregrounds the 82% "no wrapper" finding. If the research goal is understanding Claude-Code-specific packaging, the role's signal-to-noise is low — the bare bucket is a single binary fact ("no wrapper present"), and the 8 wrapped samples cluster across 5 paths, none with more than 4. The role may be more useful as a sub-section under Host integration > Claude Code or Distribution channel than as a top-level role of its own.

- **`.claude-plugin/` plus `.cursor-plugin/` co-occurrence** — slackapi and stripe ship both `.claude-plugin/` and `.cursor-plugin/` directories (per Host integration depth pass). This is a multi-host plugin-wrapper pattern. Within this role, the `.claude-plugin/` half is captured but the `.cursor-plugin/` half belongs under a Cursor-specific role — which doesn't exist as a top-level role. The asymmetry is a corpus artifact: the research subject is MCP, and Claude Code is the dominant host, so Claude-Code-specific packaging earned its own role. Other host-specific packaging (Cursor, Gemini CLI) lives under Host integration > First-party host extension manifest. Reconciler should consider whether the asymmetry is justified by Claude Code's dominance in MCP or whether all host-specific packaging shapes should be unified under one role.

- **Hosted-server `.claude-plugin/` is its own pattern.** exa-labs and upstash both ship Claude-Code-specific metadata (full plugin manifest vs marketplace.json-only) for hosted MCP endpoints — the plugin/marketplace artifact wraps a remote URL, not a local install. This is a distinct subset within the role: 2 of 8 wrapped samples are hosted-endpoint wrappers. The plugin's role is to give Claude Code a discoverable install path that resolves to a remote URL. This pattern is meaningfully different from local-install plugins (motherduckdb, stripe) but the corpus is too thin (2 samples) to break out. Worth noting for future research: as more remote MCP endpoints emerge, this sub-pattern may concentrate.

- **The role's name "plugin / skill wrapper" suggests an OR but the corpus shows AND is rare.** Only 1 sample (slackapi or stripe, depending on whether the marketplace metadata of the broader Claude Code ecosystem is considered) ships both plugin manifest AND skill files. The other 7 wrapped samples pick one mechanism. The OR in the role name reflects the conceptual space; the corpus shows authors choose one packaging convention and stick with it.

- **Single-sample paths under this role carry weak descriptions vs evidence.** `claude-code/ directory with skill files` (1 sample), `.claude-plugin/marketplace.json only` (1 sample) both have full-paragraph descriptions in the consolidated. The descriptions read confidently but are based on minimal evidence — the same caveat the prior Host integration depth pass surfaced for low-mention paths. Reconciler should consider whether single-sample paths warrant trimmed descriptions to honestly reflect the evidence base.

# Depth Pass Refinements — Sample > Host integration

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

**Sample > Host integration > Claude Desktop** — Description claims this is the "universal floor" and "most-documented host across the corpus" — accurate. But cross-corpus visibility surfaces a meaningful sub-axis the existing description hides: the *depth* at which the sample documents Claude Desktop varies enormously, from "primary documented host with copy-paste JSON" (twolven, microsoft/playwright-mcp, korotovsky, executeautomation, v-3, pragmar) to "implied via stdio transport" (jbeno/cursor-notebook-mcp, isaaccorley/planetary-computer-mcp, sajal2692/mcp-weaviate) to "listed as MCP-compatible (assumed)" (elastic, supabase-community, neondatabase, sooperset). The path conflates "primary documented host" with "host that consumes MCP at all" — these are very different documentation postures. Cross-corpus evidence:

- *Primary documented host* (≈30 samples): README leads with Claude Desktop, full JSON snippet with command/args/env block.
- *Standard documented host* (≈30 samples): JSON snippet shown as one of several hosts, equal weight with Cursor/VS Code.
- *Implied / minimal mention* (≈10 samples): "supported via stdio", "listed as compatible", or per-OS path documentation only.
- *MCPB / native-connector / FastMCP-CLI install* (≈5 samples): the host integration goes through a different mechanism entirely (drag-drop bundle, native vendor connector, `fastmcp install`). These appear under both Claude Desktop AND a more-specific path.

Sharpened text addition — *"Documentation depth varies across the corpus from primary documented host (README leads with the JSON snippet) through standard listing (one of several hosts shown with equal weight) to implied compatibility (no Claude-specific snippet, just 'works with any MCP host'). Several samples document Claude Desktop alongside a more-specific install mechanism (MCPB drag-drop, FastMCP CLI install, vendor native connector); the more-specific mechanism is the primary install path even though Claude Desktop is the runtime target."*

**Sample > Host integration > Cursor** — Description correctly enumerates the file-location split (`.cursor/mcp.json` project-scoped, `~/.cursor/mcp.json` global) and mentions `.cursor-mcp.json` and `.cursor-plugin/` as variants. Cross-corpus evidence shows three genuinely-distinct Cursor integration mechanisms that the description bundles into one sentence:

- *JSON config* (most common, ≈25 samples): `.cursor/mcp.json` or `~/.cursor/mcp.json`.
- *Quick-install badge / one-click* (≈5 samples): exa-labs, mongodb-js, neondatabase, paypal, ppl-ai — README renders an install button that auto-configures Cursor.
- *Cursor-specific plugin wrapper* (`.cursor-plugin/`, 2 samples): stripe/agent-toolkit, slackapi/slack-mcp-plugin — analogous to `.claude-plugin/` for Claude Code but for Cursor. This is a different integration shape than JSON snippet — the repo packages itself as a Cursor plugin.

The `.cursor-plugin/` shape is structurally distinct enough that it parallels `.claude-plugin/ directory in repo` which has its own path. Consistency with the Claude Code sibling structure suggests `.cursor-plugin/` might warrant its own path or at least an explicit named treatment.

Sharpened text addition — *"Three integration shapes appear: JSON config (`.cursor/mcp.json` project / `~/.cursor/mcp.json` global, by far the most common), quick-install badge (URL-protocol deep link that auto-configures Cursor's MCP settings), and Cursor-specific plugin wrapper (`.cursor-plugin/` directory in repo, structurally analogous to `.claude-plugin/`)."*

**Sample > Host integration > VS Code / VS Code Insiders / Visual Studio family** — Description bundles four genuinely-different integration surfaces that the corpus shows as structurally distinct:

- *VS Code with `.vscode/mcp.json`* (≈10 samples): the standard MCP-aware VS Code integration. Sometimes requires `chat.agent.enabled: true`.
- *VS Code with GitHub Copilot* (≈5 samples: feiskyer, lanbaoshen, neondatabase, redis, rohitg00) — Copilot Chat is the consumer; the integration is through Copilot rather than VS Code's own MCP support.
- *Visual Studio 2022 / Eclipse* (Azure successor, microsoft/mcp): IDE-extension integration via platform marketplace, not a JSON file.
- *PyCharm* (alpacahq mentions PyCharm in this path content) — but PyCharm is a JetBrains IDE; placing it here is mis-categorization. (See Mis-placed samples below.)

The path's heading naming ("Visual Studio family") implies one ecosystem but the samples show 3-4 unrelated mechanisms.

Sharpened text addition — *"Four distinct integration surfaces fall under this header: VS Code's native `.vscode/mcp.json` MCP support (sometimes gated by `chat.agent.enabled`); VS Code through GitHub Copilot Chat as the MCP consumer; Visual Studio 2022 / Eclipse via platform marketplace IDE extensions; and (rarely) IntelliJ-line products surfaced as Visual Studio peers because the same vendor authors them."*

**Sample > Host integration > Claude Code** — The description is the longest in the role and tries to cover all the integration shapes Claude Code supports. Cross-corpus evidence shows the path bundles five distinct mechanisms:

- *Project-level `.mcp.json`* (FuzzingLabs, slackapi) — file in project root.
- *`claude mcp add` CLI* (mukul975, severity1) — registered via CLI command.
- *`.claude-plugin/` directory* (stripe, getsentry, slackapi, possibly apollographql with `.claude/`+`CLAUDE.md`) — first-class Claude Code plugin wrapper.
- *Skills sibling directories* (`skills/`, `claude-code/`) — blazickjp ships `skills/`; openags ships `claude-code/` skill files; sometimes stripe under `.claude-plugin/`.
- *Hosted endpoint config* (upstash, motherduckdb) — Claude Code consumes the hosted MCP endpoint via standard `.mcp.json` plus optional `npx ctx7 setup`.

The current description covers all of these but blends them in one paragraph. Five mechanisms is enough that explicit enumeration would help.

Sharpened text suggestion — restructure as: *"Claude Code consumes MCP servers through five mechanisms across the corpus: (1) project-level `.mcp.json` file, (2) `claude mcp add` CLI registration, (3) `.claude-plugin/` directory in the repo packaging the project as a Claude Code plugin, (4) skill-sibling directories (`skills/`, `claude-code/`) shipping Claude Code skill files alongside the MCP server, (5) hosted MCP endpoint registered via standard `.mcp.json`. Multiple mechanisms often co-exist in one project — getsentry ships both `.claude-plugin/` and `.mcp.json`; stripe ships `.claude-plugin/` alongside its raw MCP entry point."*

**Sample > Host integration > Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment** — Description correctly says "same JSON-snippet pattern for other emerging MCP-aware IDEs and agents." Cross-corpus evidence reaffirms — most samples (≈18) show one-line "Cline supported" / "Windsurf supported" / "Augment supported" entries. The description's list of named hosts is incomplete vs corpus: idosal/git-mcp documents Augment Code, exa-labs documents Roo Code, awslabs/mcp documents "Cline with Amazon Bedrock" as a distinct entry. The list is open-ended; this is a "long-tail of MCP-aware IDEs" path.

Sharpened text addition — *"The named hosts in the path heading are exemplars, not exhaustive — the corpus shows additional long-tail hosts (Roo Code, Cline-with-Amazon-Bedrock, Augment Code, Highlight AI, Msty AI, OpenCode, Junie, Factory, Warp, Antigravity, Amp, opencode, LM Studio) all documented with the same JSON-snippet pattern. The path captures any MCP-aware IDE/agent that consumes a generic `mcpServers` JSON entry without host-specific config shape."*

**Sample > Host integration > Codex CLI / Copilot CLI / Gemini CLI** — Description correctly identifies these as "non-Anthropic agent CLIs that consume MCP." Cross-corpus evidence surfaces a sub-pattern: 3 of 8 samples ship a *first-class extension manifest* for a specific CLI (`.codex-plugin/` in blazickjp, `gemini-extension.json` in googleapis and exa-labs). These are structurally different from "JSON snippet for the CLI's `settings.json`" — they are first-party plugin-shape integrations distinct from generic MCP consumption. There's overlap with *First-party host extension manifest* (which has 4 supporting samples — googleapis, exa-labs, normaltusker, slackapi).

Sharpened text addition — *"Two integration shapes appear: generic JSON config (entry in the CLI's `settings.json` or `mcp.json` — the same shape used for all MCP hosts) and first-class extension manifest (`.codex-plugin/`, `gemini-extension.json`) — see also First-party host extension manifest. The first-class manifest shape shows up where the project author has a special relationship with the CLI's vendor (Google for Gemini CLI, etc.)."*

**Sample > Host integration > Smithery / Glama discovery** — Description correctly notes this is "cross-host distribution mechanism rather than a single-host integration" and points to *Distribution channel — Smithery registry*. Cross-corpus evidence shows this path actually mixes *two different registries*: Smithery (11 samples) and Glama (1 sample, sandraschi/email-mcp via `glama.json`). They are siblings — both are discovery-and-one-click-install registries — but different vendors with different YAML/JSON shapes (`smithery.yaml` vs `glama.json`). The path heading names them together as if they were one thing, but they are operationally separate.

Sharpened text addition — *"Two registry vendors appear in the corpus — Smithery (dominant; 11+ samples; install via `npx -y @smithery/cli install <name> --client <host>`; declared via `smithery.yaml` in repo root) and Glama (rare; 1 sample; declared via `glama.json`). Both are discovery-and-install registries; they're listed together because they fill the same niche, but the YAML/JSON declaration files and CLI tools differ."*

**Sample > Host integration > Inspector compatibility called out** — Description correctly notes Inspector is "a verification tool rather than a host per se." Cross-corpus evidence (5 samples — ahmedmustahid, apollographql, korotovsky, upstash, v-3) confirms this is a thin path: every sample mentions Inspector as a debugging/verification surface, never as the primary integration. Description is accurate; no sharpening needed.

**Sample > Host integration > JetBrains IDE** — Description says "Native MCP integration documented per JetBrains product line." Cross-corpus evidence: 5 samples — Azure (IntelliJ IDEA via successor microsoft/mcp), alpacahq (PyCharm via Settings → Tools → MCP), github (Docker config), lanbaoshen (generic), normaltusker (native support documented). Note alpacahq's content also appears under *VS Code / VS Code Insiders / Visual Studio family* — PyCharm is a JetBrains IDE, mis-classified there. (See Mis-placed samples.) The github sample's content "Docker-based config with PAT env injection" doesn't say *which* JetBrains product or *how* the integration works; it's underspecified for this path.

Sharpened text addition — *"JetBrains products that surface MCP integration in the corpus: IntelliJ IDEA, PyCharm (alpacahq documents Settings → Tools → MCP path), generic 'JetBrains IDE' (no specific product). Integration is via the platform's plugin mechanism rather than a project-local JSON file."*

**Sample > Host integration > No host integration documentation** — Description correctly identifies "SDK-style or library projects skip host-specific docs because the consumer is another program." Cross-corpus evidence: 5 samples — but they fall into three different reasons:

- *SDK / library* (mark3labs, modelcontextprotocol/kotlin-sdk, viant) — consumer is another program.
- *Remote-endpoint-only* (awslabs/mcp-lambda-handler) — server is reached via API Gateway URL; no host-launch exists.
- *Sample didn't enumerate* (misbahsy/video-audio-mcp) — author didn't document hosts in the README; "host integrations not enumerated in the sample" — this is a research-data limitation, not a deliberate omission.

Sharpened text addition — *"Three reasons drive samples into this bucket: (1) SDK/library — consumer is another program, not a host (mark3labs/mcp-go, kotlin-sdk, viant); (2) remote-endpoint-only — server is reached via URL with no host-launch step (mcp-lambda-handler); (3) author didn't document hosts in README (research-sample artifact rather than deliberate posture). The first two are intentional; the third is a documentation gap."*

**Sample > Host integration > `.mcp.json` in project root** — Description says this is "a project-local MCP-config file convention used by Claude Desktop and similar hosts that read `.mcp.json`." Cross-corpus evidence: this is actually the Claude Code convention specifically — `.mcp.json` is read by Claude Code at project level, not Claude Desktop (which reads `claude_desktop_config.json` from the OS user-config location). The description conflates the two hosts. The github/github-mcp-server sample's content reads "`.vscode/` ships editor configuration samples" — entirely about VS Code, not `.mcp.json`; mis-placed.

Sharpened text suggestion — *"`.mcp.json` is the Claude Code project-level MCP-config file (read at project root, distinct from Claude Desktop's `claude_desktop_config.json` in the OS user-config location). Repos that ship a `.mcp.json` are pre-configuring themselves for Claude Code workspace consumption — useful when the repo is intended to be cloned and opened in Claude Code with MCP active out of the box. Sometimes co-shipped with `.claude-plugin/` (slackapi) or `.cursor-mcp.json` (slackapi) as part of a multi-host plugin-wrapper layout."*

**Sample > Host integration > First-party host extension manifest** — Description: "host-specific manifest file (e.g., `gemini-extension.json`, `.gemini/` directory) declares the integration with a specific host the project has a special relationship with. Appropriate when the project is owned by or aligned with the host's vendor." Cross-corpus evidence: 4 samples — exa-labs (`gemini-extension.json` + `server.json`), googleapis (`gemini-extension.json` from Google), normaltusker (HTTP REST bridge — *mis-placed* — that's not a host extension manifest), slackapi (`.cursor-plugin/` + `.claude-plugin/` in same repo). Three different host-specific manifest shapes appear: Gemini (`gemini-extension.json`), Cursor (`.cursor-plugin/`), Claude (`.claude-plugin/`). They are structurally analogous — vendor-aligned plugin/extension manifest in repo — but the description focuses on the Gemini case.

Sharpened text addition — *"Manifest shapes appear for multiple hosts: `gemini-extension.json` (Gemini CLI, exa-labs and googleapis), `.cursor-plugin/` (Cursor, slackapi and stripe), `.claude-plugin/` (Claude Code, slackapi/stripe/getsentry — see also `.claude-plugin/` directory in repo path). The vendor relationship varies — Google authors googleapis directly; exa-labs and slackapi ship vendor-aligned manifests for hosts they target as primary audience."*

**Sample > Host integration > Cloudflare AI Playground / OpenAI Responses API / OpenAI Agents SDK** — Description says "First-party platform integrations for hosted-only servers, plus documented support for non-MCP-host MCP-consuming runtimes (OpenAI Agents SDK)." Cross-corpus evidence: only 3 supporting samples but they exhibit FIVE different integrations bundled into one path:

- cloudflare/mcp-server-cloudflare — Cloudflare AI Playground (first-party platform) + OpenAI Responses API (documented integration).
- exa-labs/exa-mcp-server — v0 by Vercel, OpenCode, Antigravity, Warp (these are non-Anthropic agent CLIs, *not* OpenAI/Cloudflare specifically).
- redis/mcp-redis — OpenAI Agents SDK (development SDK, not a hosted platform).

The path's heading lumps three unrelated things together: a Cloudflare-vendor platform, an OpenAI runtime API, and an OpenAI development SDK. The exa-labs entry doesn't fit the heading at all (v0/OpenCode/Warp aren't OpenAI or Cloudflare). This path is poorly named for its content.

Sharpened text suggestion — rename the path to something broader like *"Non-Anthropic AI runtime integrations"* and explicitly enumerate: *"Three structurally-distinct integrations bundled here: hosted vendor AI playgrounds (Cloudflare AI Playground), AI-platform consumer APIs (OpenAI Responses API for hosted MCP servers), and SDK-level integrations for AI-runtime authors (OpenAI Agents SDK). The path also catches scattered mentions of v0, OpenCode, Antigravity, Warp — non-Anthropic agents that consume MCP via standard transport."* See also *Proposed bucket splits* below.

**Sample > Host integration > MCPB / DXT bundle manifest** — Description correctly identifies "Claude Desktop-specific extension packaging; `.mcpb` bundles ship as drag-and-drop installs." Cross-corpus evidence: 2 samples (korotovsky `manifest-dxt.json`, sandraschi `manifest.json` for MCPB / Desktop Extension). Description accurate; the path is operationally a Claude Desktop sub-mechanism.

**Sample > Host integration > Vendor-specific companion config** — Description: "first-party agent surface gets its own dedicated config file." Cross-corpus evidence: 2 samples — docker (`gordon-mcp.yml` for Docker's "Ask Gordon" agent), slackapi (configs-only repo *is* the companion config). These are very different things — gordon-mcp.yml is a single config file shaping the integration; slackapi's "configs-only repo" is the entire repo IS metadata. The description's framing fits docker but not slackapi.

Sharpened text addition — *"Two flavors appear: dedicated companion config file (docker's `gordon-mcp.yml` for the Ask Gordon agent — single file shaping the integration with a first-party downstream tool) and configs-only repository (slackapi's whole repo IS host-integration metadata; no server implementation lives here, the server runs at `mcp.slack.com`). The first is a single artifact; the second is a packaging strategy."*

**Sample > Host integration > Generic / host-agnostic snippet** — Description: "Stdio-launch instructions framed for any compliant MCP host without naming specifics. Default fallback when authors don't want to enumerate hosts." Cross-corpus evidence: 10 samples — most fit this framing exactly (PagerDuty "Other MCP-enabled clients", apollographql "AI model/LLM client", riza-io "any MCP client", stripe `npx @stripe/mcp` universal). Two samples don't quite fit: zongmin-yu's content describes an HTTP bridge for non-MCP consumers ("HTTP bridge serves on `0.0.0.0:8000`" — that's a completely different integration shape), and modelcontextprotocol/servers describes a "generic listing of clients that support MCP" which is more of a top-level documentation overview than a snippet.

Sharpened text addition — *"The 'generic snippet' framing fits most cases (a stdio-launch JSON applicable across MCP-compatible hosts). Two adjacent uses of this label appear: (1) HTTP-bridge for non-MCP consumers (zongmin-yu publishes a `0.0.0.0:8000` HTTP endpoint as a generic non-MCP integration alongside MCP) and (2) registry-style listings of MCP-compatible clients (modelcontextprotocol/servers' top-level README enumerates compatible clients without per-server snippets). Both are border-case mis-fits — see Mis-placed samples."*

**Sample > Host integration > Multi-host catalog (30+ agents)** — Description: "README documents support for 30+ different agent platforms with per-agent config snippets." Cross-corpus evidence: 4 supporting samples — but the actual host counts vary widely: idosal (8 hosts), microsoft/playwright-mcp (20+), rohitg00 (15+), upstash (30+). The "30+" in the path heading is misleading; the path is really "many-host catalog" of varying sizes. Also, *Per-host README JSON snippets* is a near-overlapping path (count 6) — both describe README enumeration of multiple hosts. The two paths' descriptions don't make the distinction crisp.

Sharpened text addition — *"Threshold is fuzzy in the corpus — observed counts include 8, 15+, 20+, 30+. The 'catalog' framing applies whenever the sample treats host-enumeration as primary documentation strategy, even when the count is below 30. Adjacent path *Per-host README JSON snippets* (count 6) overlaps significantly — both describe README-as-host-catalog. The difference is degree: per-host snippets is the practice; multi-host catalog is the practice taken to scale."*

**Sample > Host integration > Production reference implementation** — Description: "the README points to a real-world server built on the SDK as a reference." Cross-corpus evidence: 4 samples — mark3labs (20 example implementations covering client/server/HTTP/SSE/OAuth), metoro-io (Metoro Kubernetes monitoring as reference), modelcontextprotocol/kotlin-sdk (`./samples/`), viant (`/example` directory). All are SDK-style projects. The path is well-described; cross-corpus evidence reinforces the description without adding new sub-axes.

**Sample > Host integration > Monorepo catalog** — Description: "Sub-server READMEs defer host-integration examples to the parent monorepo's catalog page." Cross-corpus evidence: 4 samples — all from awslabs (aws-api, aws-documentation, bedrock-kb-retrieval, openapi). The path is essentially "AWS monorepo's deferred-documentation pattern"; it's a corpus artifact of having 4 awslabs sub-servers in the sample. Description is accurate but the pattern's prevalence across the broader MCP ecosystem is unknown — only awslabs exhibits it in this corpus.

Sharpened text addition — *"In the corpus this pattern is exclusive to awslabs sub-servers; whether it generalizes to other monorepos isn't observable from this sample (the only other monorepo, modelcontextprotocol/servers, ships per-server READMEs that include host snippets directly)."*

**Sample > Host integration > Universal installer covering many hosts** — Description: "A single `install.py` script writes per-host configs to up to 10 MCP client locations." Cross-corpus evidence: 1 sample (samuelgursky/davinci-resolve-mcp). The description is accurate; the path is rare. samuelgursky also appears under several specific-host paths (Claude Desktop, Cursor, Windsurf, Claude Code) all marked "Supported via the universal installer" — which is correct cross-categorization (the installer wires each host).

**Sample > Host integration > Per-OS path documentation** — Description: "The Claude Desktop section enumerates Windows, macOS, and Linux config paths." Cross-corpus evidence: 1 sample (marlonluo2018) explicitly under this path. But OTHER samples (JackKuo666, alpacahq, mukul975, mahdin75, metoro-io) ALSO enumerate per-OS paths in their Claude Desktop sections. The path's count of 1 understates the pattern — but the other samples document per-OS paths within their *Claude Desktop* path, not as a separate path. Whether that's mis-classification or just a different documentation choice is a reconciler call.

Sharpened text addition — *"Single sample explicitly under this path; cross-corpus evidence shows ≥5 other samples (JackKuo666, alpacahq, mukul975, mahdin75, metoro-io) document per-OS paths in their Claude Desktop section without a separate path classification. Count understates corpus prevalence; the path captures the documentation choice rather than the underlying pattern."*

**Sample > Host integration > nREPL host** — Description: "The host is itself a running REPL process; the server connects to it. Native to the Clojure ecosystem." Cross-corpus evidence: 1 sample (bhauman/clojure-mcp). Description accurate; rare.

**Sample > Host integration > JupyterLab as a host** — Description: "Server runs as an extension inside JupyterLab and is configured via the standard Jupyter extension mechanism." Cross-corpus evidence: 1 sample (datalayer/jupyter-mcp-server `jupyter-config/`). Description accurate.

**Sample > Host integration > NixOS / Home Manager module** — Description: "Declarative config entry (an attribute set added to `configuration.nix` or `home.nix`)." Cross-corpus evidence: 1 sample (utensils/mcp-nixos). Description accurate; ties tightly to the *Nix distribution channel*.

**Sample > Host integration > Vercel AI SDK native integration** — Description: "Server exports a `createToolSchemas()` (or equivalent) function that lets a Vercel-AI-SDK-based app consume the same tool schemas without going through MCP transport." Cross-corpus evidence: 1 sample (supabase-community/supabase-mcp). Description accurate.

**Sample > Host integration > LangChain integration** — Description: "Server documents LangChain consumption (typically via a LangChain MCP adapter)." Cross-corpus evidence: 1 sample (opensearch-project — "LangChain integration supported per README" — minimal mention). Description is more aspirational than the evidence shows; the sample's content is one sentence.

**Sample > Host integration > Native host connector** — Description: "The host has built-in awareness of the server (Claude Desktop's native connector for exa); no manual config is needed." Cross-corpus evidence: 1 sample (exa-labs). Description accurate; rare.

**Sample > Host integration > Co-located VS Code extension** — Description: "A parallel VS Code extension (TypeScript) ships in the same repo as the MCP server." Cross-corpus evidence: 1 sample (isaaccorley `vscode-extension/`). Description accurate.

**Sample > Host integration > WSL configuration guidance** — Description: "Documentation specifically addressing Windows users running the host through WSL." Cross-corpus evidence: 1 sample (spences10/mcp-turso-cloud). Description accurate; rare.

**Sample > Host integration > Zed** — Description: "Documented as a Zed extension. Less common; sometimes the only sample in a bin to mention it." Cross-corpus evidence: 4 samples — exa-labs (JSON `mcp.json`), modelcontextprotocol/servers (`settings.json` snippet), neondatabase (supported), sandraschi (Zed extension ships in repo). One sample (sandraschi) ships an actual Zed extension (different mechanism), the other three document JSON config. The description should distinguish.

Sharpened text addition — *"Two integration shapes: JSON config (`settings.json` or `mcp.json`-style entry — most common across the corpus) and Zed extension shipped in repo (sandraschi). The extension shape is rarer and structurally analogous to *Co-located VS Code extension*."*

**Sample > Host integration > `.claude-plugin/` directory in repo** — Description: "Project ships a Claude-Code plugin wrapper directory at the repo root, encoding the plugin manifest alongside the code. Distinct from JSON-snippet host config — this packages the project as a discoverable Claude Code plugin." Cross-corpus evidence: 2 supporting samples (getsentry, slackapi). HOWEVER stripe/agent-toolkit ALSO has `.claude-plugin/` per its repo content ("`.claude-plugin/` and `.cursor-plugin/` ship alongside code") and stripe IS classified under this path's content according to the inspection — but stripe is listed under *Claude Code* path with `.claude-plugin/` mentioned, NOT under `.claude-plugin/` directory in repo path. apollographql is also ambiguous — repo has `.claude` directory and `CLAUDE.md`, but `.claude-plugin/` presence is "not explicitly confirmed." Count 2 likely undercounts by 1 (stripe should be here).

Sharpened text addition — *"Three samples in the corpus ship `.claude-plugin/` (getsentry, slackapi, stripe per repo content); apollographql ships `.claude/` + `CLAUDE.md` which is similar but specifically NOT `.claude-plugin/`. The directory typically pairs with `.cursor-plugin/` (slackapi, stripe) as a multi-host plugin-wrapper layout. See also `.cursor-plugin/` analog under Cursor and `.claude-plugin/marketplace.json` under Distribution channel."*

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

**Sample > Host integration > Claude Desktop** — Sub-axis: *documentation depth*.

- Primary documented host (≈30 samples) — README leads with Claude Desktop, full snippet.
- Standard documented host (≈30 samples) — listed alongside other hosts, equal weight.
- Implied / minimal mention (≈10 samples) — no Claude-specific snippet, just compatibility statement.

Whether to split: fold into description. The depth axis matters but doesn't justify splitting the path — Claude Desktop is the host either way; what varies is the documentation posture, which is a property of *how* the sample documents its host integration rather than *which* host it integrates with.

**Sample > Host integration > Claude Code** — Sub-axis: *integration mechanism*.

- Project-level `.mcp.json` (≈4 samples).
- `claude mcp add` CLI (≈2 samples).
- `.claude-plugin/` plugin wrapper (≈3 samples — already has its own path).
- Skill-sibling directories `skills/` or `claude-code/` (≈2 samples).
- Hosted-endpoint `.mcp.json` config (≈2 samples — hosted variants).

Whether to split: the `.claude-plugin/` mechanism already has its own path. Other mechanisms could reasonably split into sub-paths but the per-mechanism counts are too low (1-4 each) to warrant separate paths. Fold into description (Description sharpenings above suggests explicit enumeration in the prose).

**Sample > Host integration > Cursor** — Sub-axis: *integration mechanism*.

- `.cursor/mcp.json` or `~/.cursor/mcp.json` (≈25 samples) — JSON config.
- Quick-install badge (≈5 samples) — URL-protocol install.
- `.cursor-plugin/` directory (2 samples) — Cursor plugin wrapper.

Whether to split: the `.cursor-plugin/` shape parallels `.claude-plugin/` which has its own path. Consistency suggests `.cursor-plugin/ directory in repo` could be a peer path. Counts are low (2) so the case is borderline. Fold into description first; reconciler can elevate if the parallelism with `.claude-plugin/` matters.

**Sample > Host integration > VS Code / VS Code Insiders / Visual Studio family** — Sub-axis: *which IDE / which integration mechanism*.

- VS Code with `.vscode/mcp.json` (≈10 samples) — native MCP support.
- VS Code with GitHub Copilot Chat (≈5 samples) — Copilot is the consumer.
- Visual Studio 2022 / Eclipse via marketplace extensions (≈2 samples).
- PyCharm — mis-placed (belongs under JetBrains).

Whether to split: the path heading already implies a family but the cross-corpus samples show the family is heterogeneous. A possible split is *VS Code (including Copilot)* + *Visual Studio family (VS 2022, Eclipse, etc.)* — but counts (10+5 vs 2) are uneven. Fold into description; reconciler decides whether to split.

**Sample > Host integration > Codex CLI / Copilot CLI / Gemini CLI** — Sub-axis: *generic JSON vs first-class extension manifest*.

- Generic JSON config in CLI's `settings.json` or `mcp.json` (≈5 samples) — same shape as other MCP hosts.
- First-class extension manifest (3 samples — `.codex-plugin/`, `gemini-extension.json`) — vendor-aligned plugin shape.

Whether to split: there's overlap with *First-party host extension manifest* (which already covers `gemini-extension.json` and `.cursor-plugin/`/`.claude-plugin/`). The 3-sample first-class-manifest cluster could either stay under this path with description sharpening or move under *First-party host extension manifest*. Cross-classification is fine if samples appear under both. Fold into description.

**Sample > Host integration > Smithery / Glama discovery** — Sub-axis: *which registry*.

- Smithery (≈11 samples).
- Glama (1 sample).

Whether to split: Glama is genuinely a different registry but with only 1 supporting sample, splitting is premature. Fold into description (sharpening above does this). Reconciler can split if more Glama samples surface in future research.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

**Sample > Host integration > Per-host README JSON snippets** + **Sample > Host integration > Multi-host catalog (30+ agents)** — Two paths describing the same documentation pattern at different scales. Per-host snippets covers samples documenting "several" hosts (≈4-10); multi-host catalog covers "many" (15-30+). The threshold is arbitrary — microsoft/playwright-mcp (20+) is in catalog; severity1 (5-6) is in per-host. Both paths describe the same author choice: enumerate multiple hosts in README. The split is by count, not by mechanism.

Recommendation: merge into one path *Per-host README catalog* with a description noting "scale ranges from a handful of hosts to 30+; the choice is whether to enumerate at all, not how many to enumerate." Or keep both with crisp threshold language ("up to 10" vs "10+"). The current adjacency is muddled.

Alternative: keep both if the catalog at 30+ scale is *qualitatively* different (the README becomes a host-table rather than a config-snippet section). 4 samples (idosal at 8, rohitg00 at 15+, microsoft at 20+, upstash at 30+) suggests the catalog scale really does shift documentation strategy — README real estate dedicated to per-host setup becomes the dominant content type. Reconciler call.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

**Sample > Host integration > Cloudflare AI Playground / OpenAI Responses API / OpenAI Agents SDK** — As written, the path bundles three structurally-different integrations:

- *Vendor AI playground / hosted-test-runtime* (Cloudflare AI Playground) — interactive web UI for testing MCP servers in vendor's playground.
- *Hosted MCP runtime API* (OpenAI Responses API) — non-Anthropic platform consuming hosted MCP endpoints.
- *Development SDK for AI runtime authors* (OpenAI Agents SDK) — library for building agent runtimes that consume MCP.

Plus the exa-labs sample mentions v0/OpenCode/Antigravity/Warp under this path which don't fit the heading at all (they're non-Anthropic agent CLIs, closer to *Codex CLI / Copilot CLI / Gemini CLI* path).

Proposed split:

- *Vendor-operated AI playground integration* (Cloudflare AI Playground; possibly a future "Anthropic Workbench" if it surfaces). Cross-overlap with *Distribution channel — Hosted endpoint*.
- *Cross-runtime consumption (OpenAI Responses API, OpenAI Agents SDK, Vercel AI SDK)* — non-Anthropic AI runtimes that consume MCP. (Vercel AI SDK already has its own path.)
- Move v0/OpenCode/Antigravity/Warp under *Codex CLI / Copilot CLI / Gemini CLI* or *Windsurf / Goose / etc.* depending on integration shape.

Caveat — total supporting sample count is 3, which makes splitting border-case. The current path's heading is just structurally inaccurate for the content; even without splitting, renaming or reframing would help.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

**`alpacahq--alpaca-mcp-server.md`** is under *Sample > Host integration > VS Code / VS Code Insiders / Visual Studio family* with content `.vscode/mcp.json` AND *also* under JetBrains IDE with content "PyCharm via Settings → Tools → MCP". PyCharm is a JetBrains IDE, not a Visual Studio-family one — but the alpacahq sample's PyCharm content is correctly under JetBrains IDE. The issue is in the *path-heading* of *VS Code / VS Code Insiders / Visual Studio family*: alpacahq's PyCharm content is in the JetBrains path (correct), so this isn't a sample-level mis-placement — but the path heading's "Visual Studio family" framing might lead readers to expect PyCharm/IntelliJ content under it.

**`normaltusker--kotlin-mcp-server.md`** under *Sample > Host integration > First-party host extension manifest* — content reads "HTTP REST bridge for custom client integration outside the MCP host model." That's a generic HTTP REST bridge, NOT a first-party host extension manifest (no `gemini-extension.json` or `.cursor-plugin/`-style file). Mis-placed; this content fits *Generic / host-agnostic snippet* (HTTP variant) or potentially *Co-located non-MCP integration* if such a path existed. Recommend the reconciler move this entry out of *First-party host extension manifest*.

**`github--github-mcp-server.md`** under *Sample > Host integration > `.mcp.json` in project root* — content reads "`.vscode/` ships editor configuration samples." That's about VS Code, not `.mcp.json`. Mis-placed; this content belongs under *VS Code / VS Code Insiders / Visual Studio family* (where github already has an entry). The `.mcp.json in project root` entry for github should either be removed or reworked with actual `.mcp.json`-relevant content from the github sample.

**`github--github-mcp-server.md`** under *Sample > Host integration > JetBrains IDE* — content is "Docker-based config with PAT env injection." This describes *how* the integration runs (Docker + env), not the JetBrains IDE specifics. The content doesn't actually demonstrate JetBrains integration; it's the same Docker config pattern github uses for every host. Reconciler check: is github really documented for JetBrains, or is this a copy-paste error from the Docker-config pattern?

**`zongmin-yu--semantic-scholar-fastmcp-mcp-server.md`** under *Sample > Host integration > Generic / host-agnostic snippet* — content reads "HTTP bridge serves on `0.0.0.0:8000` for non-MCP consumers — generic HTTP integration alongside MCP." This is a non-MCP HTTP-bridge endpoint, not an MCP host integration. Mis-placed; this content describes a *Capability surface* or *Distribution channel* (HTTP API alongside MCP), not host integration. Recommend the reconciler move this out of host integration entirely.

**`modelcontextprotocol--servers.md`** under *Sample > Host integration > Generic / host-agnostic snippet* — content reads "Generic listing of 'clients that support MCP' in top-level README without per-tool snippets. Mentions Zencoder." This is a documentation overview / registry-style listing, not a generic snippet. modelcontextprotocol/servers also appears under Per-host README JSON snippets (correct — each sub-server README has snippets) and Claude Desktop / VS Code / Zed (correct — top README ships snippets for each). The "generic listing" entry is borderline mis-placed; could be its own meta-categorization ("Documentation-only catalog of clients") but the supporting count is 1.

**`apollographql--apollo-mcp-server.md`** under *Sample > Host integration > Claude Code* — content reads "`.claude` directory and `CLAUDE.md` file present in repo. The `.claude` directory may be Claude Code's workspace config rather than a plugin wrapper; `.claude-plugin/` presence not explicitly confirmed." This is uncertain and differs from the other Claude Code samples which have clear plugin wrappers, CLI registrations, or `.mcp.json` files. apollographql's `.claude/` is more likely a Claude Code session-history directory than an integration mechanism. Reconciler check: confirm whether apollographql has a meaningful Claude Code integration or whether the `.claude/` directory is incidental.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

- **Most-documented host is by far Claude Desktop.** 73 of 96 host-integration-documenting samples (76%) include Claude Desktop. The runner-up Cursor is at 35%. Claude Desktop functions as the *de facto* baseline host that authors document first; everything else is incremental coverage. The corpus reflects the MCP ecosystem's origin in Anthropic tooling.

- **Multi-host samples cluster around 4-6 hosts.** The 22 samples documenting VS Code also tend to document Cursor (intersection ~18) and Windsurf-family (~14). The author choice to "support multiple hosts" rarely stops at 2 — once a sample documents Cursor or VS Code, it usually also documents 3-4 more. The exception is single-vendor samples (slackapi for Slack-only Cursor+Claude, samuelgursky's universal-installer covering 10).

- **`.claude-plugin/` and `.cursor-plugin/` co-occur as a multi-host plugin-wrapper pattern.** Both supporting samples (slackapi, stripe per repo content) ship both directories side-by-side — these aren't independent Claude-only and Cursor-only choices, they're a single "ship vendor-aligned plugin wrappers across major hosts" strategy. The corpus suggests this is becoming a recognized pattern for projects with first-party-plugin ambitions on multiple AI assistants.

- **Universal installer is a one-author solution.** Only samuelgursky uses the universal-installer pattern (`install.py` writing to 10 host-config locations). The pattern isn't yet commodified in the corpus; the MCP ecosystem hasn't standardized on a "host-configuration manager" tool. Smithery is the closest cross-host-install offering but works through registry+CLI rather than per-host file writes.

- **First-party host extension manifests cluster around vendor identity.** Of the 4 first-party-extension-manifest samples, 3 ship vendor-specific manifests aligned with the project's authoring company: googleapis ships `gemini-extension.json` (Google authors Gemini); exa-labs ships `gemini-extension.json` and is a Google partner; slackapi ships `.claude-plugin/` and `.cursor-plugin/` (Slack first-party). The pattern signals "we are aligned with this host's vendor and ship a privileged integration shape." Independent authors don't reach for first-party manifests.

- **Inspector compatibility is a documentation-quality signal.** 5 samples explicitly mention MCP Inspector. The samples that do (ahmedmustahid, apollographql, korotovsky, upstash, v-3) tend to be more thoroughly documented overall — Inspector mention correlates with README quality. It's not a host integration in any meaningful sense; it's a verification surface authors mention when they want their docs to be self-contained for debugging.

- **The "Visual Studio family" framing is strained by IDE diversity.** The path bundles VS Code (Microsoft's primary editor, MCP-native), Visual Studio 2022 (Microsoft's IDE, marketplace integration), Eclipse (Foundation, marketplace integration), and IntelliJ-line (Azure successor docs IntelliJ). These are 4 different vendors and 4 different integration mechanisms. The path heading reflects an author's mental model ("Microsoft IDE family") that doesn't match the corpus reality.

- **Documentation depth heavily underdetermined for low-mention paths.** Single-sample paths (Universal installer, JupyterLab, NixOS, Per-OS path, nREPL host, Native host connector, WSL, LangChain) all have descriptions stronger than the evidence — one-line content in the sample, paragraph-length aspirational description in the consolidated. This isn't mis-placement; it's the methodology working from minimal evidence to over-confident description. Reconciler should consider whether single-sample paths warrant trimmed descriptions.

- **Many "Claude Code" path entries are about side-channels (skills, marketplace, plugin), not direct MCP consumption.** Of 16 Claude Code samples, only ≈8 document direct MCP consumption (`.mcp.json`, `claude mcp add`); the others document `.claude-plugin/`, `skills/`, `claude-code/`, hosted-endpoint config — adjacent to MCP rather than direct MCP host integration. The path is overloaded with the Claude Code ecosystem's broader plugin/skill/marketplace surface, not just MCP host integration. Reconciler may want to factor this out — either by tightening the path to "Claude Code MCP host config" specifically and moving plugin/skill/marketplace cases to *Distribution channel — `.claude-plugin/marketplace.json`* or to *Claude Code plugin / skill wrapper* (which is a separate top-level role in the consolidated).

- **The `Sample > Claude Code plugin / skill wrapper` role exists at top level (line 2812) — significant overlap with Host integration > Claude Code.** Many of the integration mechanisms (`.claude-plugin/`, `skills/`) are arguably about Claude-Code-specific packaging, and the top-level role probably owns them. Cross-role observations: getsentry's content under Host integration > `.claude-plugin/ directory in repo` and under (presumably) the Claude Code plugin / skill wrapper role would be parallel entries. Reconciler should check whether both roles need entries for the same artifact or whether one is the canonical home.

# Depth Pass Refinements — Sample > Distribution channel

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

**Sample > Distribution channel > Docker / OCI image** — The existing description is dense and accurate but mixes two different posture flavors that the corpus shows as distinct: (1) Docker as the *primary/canonical* channel (README leads with `docker run`/`docker pull`; sometimes the *only* channel), and (2) Docker as a *supplementary* channel alongside PyPI/npm. Cross-corpus evidence:

- Docker-primary / Docker-only cluster (≈12 samples): elastic (Docker is the only shipping channel), voska/hass-mcp (README leads with `docker pull`), github/github-mcp-server (`docker run` is the canonical install path, not `go install`), alexei-led/k8s-mcp-server ("Docker-first README"), duolingo/slack-mcp ("Containerization-first pattern; no PyPI"), FuzzingLabs/mcp-security-hub (Docker-only, no PyPI), microsoft/playwright-mcp (`mcr.microsoft.com/playwright/mcp`), korotovsky/slack-mcp-server (Docker + multiple compose variants), HenkDz/postgresql-mcp-server (`docker pull henkey/postgres-mcp:latest`).
- Docker-supplementary cluster (the majority, ≈35 samples): ClickHouse, AlwaysSany/deepl-fastmcp, JackKuo666/PubMed, blazickjp/arxiv, chroma-core/chroma-mcp, etc. — these list a Dockerfile alongside PyPI uvx/pip as the primary path.
- Registry distribution shape varies meaningfully and is worth retaining at description level: vendor registries (`docker.elastic.co`, `mcr.microsoft.com`, AWS public ECR, `us-central1-docker.pkg.dev/...`), GitHub Container Registry (`ghcr.io/...` — preferred by 8+ samples), Docker Hub `mcp/...` namespace (4+ samples — Notion, modelcontextprotocol/servers, Playwright, rust-mcp-filesystem).

Sharpened text suggestion — split the description into two flavors with a leading sentence: *"Docker appears in two postures across the corpus — primary/canonical (README leads with `docker run` or `docker pull`; sometimes the only shipping channel) and supplementary (Dockerfile alongside PyPI/npm for users who prefer container isolation)."* Then keep the existing details about registries, multi-arch, host-address remapping, system-tool dependencies. The current description does state "Surfaces both as the primary distribution channel … and as a secondary channel" but as one clause inside a long paragraph; making it the structural lead surfaces the most-actionable axis at a glance.

**Sample > Distribution channel > Source clone with editable install** — The existing description bundles two distinct sub-postures that the corpus shows are different: (1) "developer-mode-as-release" — *no registry publication exists*, clone-and-install IS the release (reminia/zendesk-mcp-server, hannesrudolph/sqlite-explorer-fastmcp-mcp-server, twolven/mcp-server-puppeteer-py, mukul975/cve-mcp-server, labeveryday/mcp_pdf_reader, misbahsy/video-audio-mcp, normaltusker/kotlin-mcp-server, isaaccorley/planetary-computer-mcp, AlwaysSany/deepl-fastmcp-python-server, JackKuo666/PubMed-MCP-Server, duolingo/slack-mcp, hugoduncan/mcp-clj, idosal/git-mcp self-host, cyanheads/perplexity-mcp-server, marlonluo2018/pandas-mcp-server, v-3/discordmcp); (2) "fallback developer-mode" — registry publication exists, clone path is documented for development only (sooperset/mcp-atlassian, redis/mcp-redis, openags/paper-search-mcp, blazickjp/arxiv-mcp-server, lanbaoshen/mcp-jenkins, ckreiling/mcp-server-docker, awslabs/* family, jbeno/cursor-notebook-mcp, mahdin75/gis-mcp, tumf/grafana-loki-mcp, shibuiwilliam/mcp-server-scikit-learn).

The split is structurally meaningful: the first cluster *cannot* be installed any other way (limits adoption to git-aware users), the second cluster offers clone alongside a canonical PyPI/npm install. Adoption count of 41 conflates these two different choices.

Sharpened text suggestion — open with: *"Two postures appear across the corpus — clone-as-only-release (no PyPI/npm publication exists; users must clone) and clone-as-developer-fallback (registry path is canonical, clone is documented for dev work)."* Then keep existing prose about extras and motivations. Optionally see *Proposed bucket splits* below.

**Sample > Distribution channel > PyPI via uvx (zero-install runner)** — Description accurate but two sub-flavors merit explicit naming:

- `uvx <package>` (per-invocation ephemeral, fetches each call) — most common form (≈25 samples).
- `uv tool install <package>` then invoke (persists in user's tool dir) — observed at openags/paper-search-mcp, blazickjp/arxiv-mcp-server. Worth noting because it's a *persistent* install on top of uvx infrastructure; users who don't want per-call fetches reach for it.
- `uv run --with <package>` — observed at ClickHouse/mcp-clickhouse (`uv run --with mcp-clickhouse --python 3.10 mcp-clickhouse`); a third uvx-family form that pins Python version inline.

Sharpened text suggestion — already present but understated. Consider explicitly enumerating the three forms: *"Three uv-family invocation forms appear: `uvx <package>` (ephemeral per-call), `uv tool install <package>` (persistent install), and `uv run --with <package>` (per-call with inline Python version pin)."*

Also, name normalization — AWS uses `awslabs.<name>` (dot-separated), most others use kebab-case (`mcp-server-git`). Worth a sentence: AWS family namespaces packages with `awslabs.` prefix (40+ servers under one PyPI namespace).

**Sample > Distribution channel > PyPI via pip / pipx** — The current description hedges that pip/pipx is "Older idiom than uvx; positioned for users on plain Python rather than uv" — but cross-corpus evidence shows pip-only-no-uvx samples are also distinct from pip-as-alternative-alongside-uvx samples. Pip-only cluster: pragmar/mcp-server-webcrawl ("`pip install mcp-server-webcrawl` is the only install path shown… No uv/uvx/pipx/Docker mentioned — positioned for plain Python users rather than uv-native ecosystem"), echelon-ai-labs/servicenow-mcp ("Plain `pip install -e .` workflow with stdlib `venv`; no uv/uvx workflow declared"), opensearch-project/opensearch-mcp-server-py, designcomputer/mysql_mcp_server (mentioned in pip path; uvx is also present though). The cluster signals projects that haven't moved to the uv ecosystem at all — useful nuance but the existing description hedge already gestures at this. A sentence about "pip-only positioning" would clarify.

Sharpened text addition — *"A subset of samples publish *only* to pip with no uvx command shown — positions the project for the plain-Python audience that hasn't adopted uv. Most others co-publish, with `uvx` taking primary billing in README and `pip install` listed as alternative."*

**Sample > Distribution channel > Smithery registry** — Description accurate. Evidence sharpens one underplayed point: the corpus shows that Smithery is *primary* in only a tiny minority (1-2 samples — JackKuo666 "distributed via Smithery without ever being published to PyPI"; shreyaskarnik/huggingface-mcp-server "Smithery-first distribution"). For 11+ other samples Smithery is purely additive — a discoverability-and-one-click-install layer atop existing PyPI/npm. Also, the canonical install command shape `npx -y @smithery/cli install <name> --client <host>` includes a `--client` flag that the current description doesn't surface as a meaningful detail; it's the host-targeting mechanism that makes Smithery's offering structurally different from npm/PyPI alone.

Sharpened text addition — *"The `--client <host>` flag in the install command is what makes Smithery's offering distinct: the same install line wires the server into the user's chosen MCP host (Claude Desktop, Cursor, etc.) without requiring host-specific config edits."*

**Sample > Distribution channel > Hosted endpoint (no install)** — The description is accurate but currently mixes two structurally-distinct deployment shapes that show up across samples:

- Single-endpoint vendor host (most common) — exa-labs at `mcp.exa.ai/mcp`, getsentry at `mcp.sentry.dev`, neondatabase at `mcp.neon.tech`, supabase-community at `mcp.supabase.com/mcp`, stripe at `mcp.stripe.com`, upstash at `mcp.context7.com/mcp`, slackapi at `mcp.slack.com`.
- Multi-endpoint catalog — cloudflare publishes 14 separate Worker-hosted servers at distinct URLs (`https://observability.mcp.cloudflare.com/mcp` and 13 others); the README's primary content is *which URL serves which capability*. The current description gestures at this ("a single monorepo deploys N domain-scoped endpoints") but it's buried late in the paragraph.

Also, the description claims hosted-endpoint distribution can collapse the README's role to "a single URL plus OAuth bootstrap" — but the corpus shows substantial public-repo content alongside hosted endpoints (cloudflare ships actual Worker source; supabase ships `@supabase/mcp-server-supabase` for self-host; stripe co-publishes `@stripe/mcp` to npm; upstash ships marketplace.json + skills + plugins). The pattern is more nuanced than "README collapses to URL" — public repos remain rich, but ship *operational* artifacts (CLI, marketplace metadata, plugins, OAuth helpers) rather than the server itself.

Sharpened text suggestion — restructure into three short sentences leading the description: *"Three hosted-endpoint shapes appear: single-endpoint vendor host (most common — paste one URL), multi-endpoint catalog (one repo deploys N domain-scoped endpoints, README's primary content is which URL serves which capability), and hybrid (hosted endpoint plus operational artifacts the public repo ships — CLI, plugins, marketplace metadata, OAuth bootstrap)."* Then keep existing detail about iteration and OAuth.

**Sample > Distribution channel > Multi-channel publication** — The description treats this as a path on equal footing with PyPI/Docker/npm, but cross-corpus evidence shows it functions as a *meta-tag* that always co-occurs with 3+ underlying channel paths in the same sample. Inspected samples (10 of them — crystaldba, datalayer/earthdata, datalayer/jupyter, executeautomation, googleapis, modelcontextprotocol/servers, openags, qdrant, rohitg00, rust-mcp-stack) all simultaneously appear under their underlying channels. This is structural overlap, not a distinct choice. See *Proposed bucket merges/splits* below for treatment options.

Sharpened text suggestion — if the path stays, lead with: *"This is a meta-classification, not a distinct channel — every sample here also appears under its underlying channels. The path captures intentional cross-ecosystem reach: 3-5 channels published simultaneously (5+ at the corpus extreme — googleapis ships across binary releases, Docker, `go install`, Homebrew, npm shim; rust-mcp-stack ships across Cargo, Homebrew, npm, Docker Hub, GitHub releases)."*

**Sample > Distribution channel > Pre-built binary release** — Description is accurate. Cross-corpus evidence sharpens one pattern: pre-built binaries exclusively appear paired with Docker (and often npm shim or `go install`); they never stand alone. 6 samples — apollographql, geropl, github, googleapis, rohitg00, rust-mcp-stack — and all 6 also have Docker. Worth a sentence noting this complementarity: binary releases serve users with locked-down container policies, where Docker isn't an option.

**Sample > Distribution channel > Configs-only repo (no server artifact)** — Description accurate but extremely close in scope to *Hosted endpoint (no install)*. Both inspected samples (slackapi, upstash) appear under both paths. This is a near-duplicate categorization — see *Proposed bucket merges* below.

**Sample > Distribution channel > Source clone with `uv run` from source tree** — Existing description captures the shape well. Cross-corpus evidence: 4 samples (crystaldba, shibuiwilliam, shreyaskarnik, zilliztech) — three of these *also* publish to PyPI (crystaldba, shreyaskarnik, zilliztech), so the path is the *documented invocation form for development*, not necessarily the only install. Only zilliztech leads with this shape as primary in README; the others position it as a development-mode launch alongside PyPI. Worth a sentence: *"In most samples this path coexists with a PyPI-published variant — `uv run` from source tree is the development-mode invocation, not the canonical end-user install."*

**Sample > Distribution channel > Windows .exe variant** — Mixed cluster. Two samples (awslabs/aws-documentation, awslabs/bedrock-kb-retrieval) document an explicit `.exe` invocation through `uv tool run --from <pkg>@latest <pkg>.exe` — that's not really a separate channel, it's a Windows-shell quoting/invocation note for the same uvx PyPI release. The third (rust-mcp-stack) is genuinely different: a WiX-built MSI installer in the `wix/` directory. These are two structurally different things classified together. See *Proposed bucket splits* below.

**Sample > Distribution channel > docker-compose variants** — Path is genuinely thin. Only one sample (FuzzingLabs/mcp-security-hub) is here, and the content reads "Docker Compose for orchestration of the multi-server bundle" — closer to the consolidated's concept of compose-for-deployment than the consolidated's own description ("Multiple compose files for distinct use cases"). The current description is more aspirational than evidenced. Also, korotovsky/slack-mcp-server explicitly mentions "multiple `docker-compose` variants" but it's classified under Docker / OCI image, not here. See *Mis-placed samples*.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

**Sample > Distribution channel > Docker / OCI image** — Sub-axis: *registry namespace*.

- Vendor-owned registry: docker.elastic.co, mcr.microsoft.com, AWS public ECR, GCP Artifact Registry — used by enterprise vendors (≈8 samples).
- GitHub Container Registry (`ghcr.io/<owner>/<repo>`) — most-used for open-source projects (≈10 samples).
- Docker Hub (`<vendor>/...` or `mcp/<name>` namespace) — most-used overall (≈20 samples).

Whether to split: fold into description as enumerated namespace patterns. Doesn't justify separate paths — the act of publishing to a Docker registry is one choice; the registry chosen is a sub-axis of branding/policy.

**Sample > Distribution channel > Source clone with editable install** — Sub-axis: *intentionality*.

- Clone-as-only-release (no registry path) — ≈16 samples (developer-mode-as-release).
- Clone-as-developer-fallback (registry path exists) — ≈22 samples.
- Clone with non-Python build steps (Go: github/github-mcp-server uses `go build`; Kotlin: modelcontextprotocol/kotlin-sdk uses Gradle) — ≈3 samples; arguably misplaced under a path that conventionally implies pip/npm install.

Whether to split: fold into description with the two intentionality flavors (covered in Description sharpenings). The non-Python build cases warrant the split discussion in *Proposed bucket splits* below — `go build` and Gradle aren't really "editable installs."

**Sample > Distribution channel > Hosted endpoint (no install)** — Sub-axis: *number of endpoints* (single-vendor URL vs catalog of N endpoints) — covered in description sharpening above.

**Sample > Distribution channel > Windows .exe variant** — Sub-axis: *what is actually shipping* — uvx invocation note vs MSI installer. Covered in description sharpening; corresponding split proposal below.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

**Sample > Distribution channel > Hosted endpoint (no install)** + **Sample > Distribution channel > Configs-only repo (no server artifact)** — Same underlying user choice expressed two ways. "Hosted endpoint" describes what the user is reaching for (a remote URL); "Configs-only repo" describes what the public repo contains (no server, just config metadata). Both inspected configs-only samples (slackapi, upstash) also appear under hosted endpoint. The configs-only label is a property of the *repo*, while hosted endpoint is a property of the *distribution*; they are two views of one shape. Canonical name: keep *Hosted endpoint (no install)* and dissolve *Configs-only repo* into a sentence within hosted-endpoint's description ("public repo content varies — some ship configs-only, some include operational artifacts like CLI, plugins, marketplace metadata; in all cases the actual server runtime is hosted by the vendor").

Alternative: keep both if the reconciler views configs-only as a meaningful sub-axis of how the public repo presents (a "what does the repo contain" question that's downstream of "where does the server run"). Not strongly objectionable; but the inspected evidence shows total overlap.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

**Sample > Distribution channel > Source clone with editable install** — As written, the path bundles three structurally different choices: (1) Python clone-and-`pip install -e .` / `uv sync` (≈30 samples); (2) Node clone-and-`npm install && npm run build` (cyanheads/perplexity-mcp-server, idosal/git-mcp self-host, makenotion/notion-mcp-server, v-3/discordmcp, docker/hub-mcp); (3) Native-build clone (github/github-mcp-server `go build`, modelcontextprotocol/kotlin-sdk Gradle, the-momentum/fhir-mcp-server `make uv`, thenets/ghost-mcp `make run`).

Group 3 in particular is misnamed — `go build` produces a binary, not an "editable install." Group 2 is technically different from Python's editable-install semantics (npm has no equivalent of `pip install -e .`).

Proposed split:

- *Source clone — Python editable install* (`pip install -e .`, `uv sync`, etc.) — ≈30 samples.
- *Source clone — Node build-and-run* (`npm install && npm run build`) — ≈5 samples.
- *Source clone — Native build* (`go build`, Gradle, `make`, `cargo build`) — ≈4-5 samples.

Caveat — this reorganization may overlap with *Server runtime* and is borderline against the methodology's rule that paths are named by *choice* (the Python/Node/Native split is a runtime axis). The simpler alternative is a description sharpening per *Description sharpenings* above (intentionality split: only-release vs developer-fallback) and leaving the runtime axis in *Server runtime*. Reconciler decides; the cleaner option may be *to keep one path and sharpen the description* rather than split, given the methodology's rule that the same role shouldn't be sliced by an axis owned by another role.

**Sample > Distribution channel > Windows .exe variant** — Currently three samples conflate two structurally different things:

- *Windows uvx invocation note* (awslabs/aws-documentation, awslabs/bedrock-kb-retrieval) — these are documenting a Windows-shell quoting variant of `uv tool run --from <pkg>@latest <pkg>.exe`, on top of the same uvx PyPI publication. Not really a separate channel; it's a Windows-shell invocation footnote.
- *Native Windows installer* (rust-mcp-stack/rust-mcp-filesystem) — WiX-built MSI installer in `wix/` directory. This is a genuinely different artifact (an MSI), distributed alongside binaries on GitHub releases.

Proposed split: dissolve the awslabs entries into the *PyPI via uvx* description as a Windows-invocation note; rename the rust-mcp-stack entry to *Native Windows installer (MSI)* or roll it into *Pre-built binary release* (since rust-mcp-stack also ships GitHub release binaries). The current path is structurally inconsistent.

**Sample > Distribution channel > Multi-channel publication** — Either dissolve or convert to a meta-tag.

- Option A (dissolve into description): note multi-channel publication patterns within the existing channel descriptions where relevant ("often co-published with…"). The path itself goes away; supporting sample count is captured implicitly by adoption-table breadth.
- Option B (keep as meta-tag): explicitly mark it as a meta-classification ("samples that publish 3+ channels simultaneously"), recognize that every sample under it also appears under its constituent channels, and lead the description with that fact. This preserves the cross-corpus signal that some projects deliberately maximize reach.
- Option C (split into 3-channel vs 5+-channel): the corpus shows two clusters — projects that publish 3 channels (most multi-channel cases) and projects that publish 5+ (googleapis, openags, rust-mcp-stack — these treat cross-ecosystem distribution as positioning). Worth recognizing only if the reconciler thinks the 5+ extreme is meaningfully different from 3.

Recommendation: Option B — keep but mark as meta-tag. The 5+-channel cluster (3 samples — googleapis, openags, rust-mcp-stack) is a notable corpus pattern but doesn't justify a separate path.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

**`korotovsky--slack-mcp-server.md`** is currently under *Sample > Distribution channel > Docker / OCI image* with content "Distributed as Docker (`Dockerfile` + multiple `docker-compose` variants)." That sample is *the* canonical example of "multiple compose files for distinct use cases" (as the *docker-compose variants* path's description names) and is a stronger fit there than FuzzingLabs (whose compose file orchestrates multiple servers — one compose file, not "variants"). Recommendation: add korotovsky to *docker-compose variants* (it can stay under Docker too — sample-multi-classification is fine).

**`FuzzingLabs--mcp-security-hub.md`** under *Sample > Distribution channel > docker-compose variants* — content reads "Docker Compose for orchestration of the multi-server bundle." That's a single compose file orchestrating a bundle, not multiple compose files for distinct use cases. Mis-placed; this content fits *Docker / OCI image* (with a multi-server-bundle nuance) rather than the "multiple compose files" path. The path's existing description doesn't actually fit FuzzingLabs's case.

**`shibuiwilliam--mcp-server-scikit-learn.md`** under *Sample > Distribution channel > Source clone with `uv run` from source tree* — content shows `uv --directory=src/mcp_server_scikit_learn run mcp-server-scikit-learn` as the host-config invocation. Note that this is the *invocation form* in host config, not necessarily the install posture; the sample also has PyPI publication implied. Probably correctly placed (the sample documents this as primary), but the description's framing of this path as "user must clone the repository" doesn't match the host-config-invocation case shibuiwilliam exhibits. Reconciler check: confirm with the sample whether the PyPI form is documented; if so, the *uv run* path may be a development-mode invocation, not the install channel.

**Cross-channel pattern note (not a single mis-placement):** a few samples categorize their MCP-aware install registry under *Host integration — Smithery / Glama discovery* rather than (or in addition to) *Distribution channel — Smithery registry* — sandraschi/email-mcp uses Glama (`glama.json`); geropl/linear-mcp-go and upstash/context7 mention Smithery without listing themselves under the distribution-channel Smithery path. The path counts under *Distribution channel > Smithery registry* (13) may understate the corpus because 3 additional samples surface Smithery only under *Host integration*. The cross-role link in the consolidated already gestures at this; reconciler should confirm whether these belong in both roles or just *Host integration*.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

- **Adoption-table coverage anomaly: `Sample > Distribution channel > .claude-plugin/marketplace.json`** is listed in the adoption table with count 2, but `references "Sample > Distribution channel > .claude-plugin/marketplace.json"` returns "No samples contain chain key" (likely due to the leading `.` or path-special-character escaping in the chain-key index). Both contributing samples (upstash, getsentry) do exist on disk — getsentry has `### .claude-plugin/marketplace.json` under Distribution channel. The depth-pass tooling doesn't surface evidence here, so the path was inspected via direct grep. Reconciler: the adoption-table count 2 looks correct; the indexing/lookup gap is a methodology artifact, not a real data gap.

- **The "Multi-channel publication" path is a methodology smell.** Every sample under it co-occurs with its constituent channels — see merge proposal. Notably, the multi-channel-publication paths cluster around 3-5 channels: googleapis (5), openags (5), rust-mcp-stack (5), executeautomation (4), rohitg00 (4), datalayer/earthdata (4), modelcontextprotocol/servers (3). The 5-channel mark is a positioning signal: the project is treating cross-ecosystem reach as canonical strategy.

- **Vendor-versus-community Docker registry split.** Vendor-published samples (Microsoft, AWS, Elastic, Google, GitHub) almost always use first-party container registries (`mcr.microsoft.com`, AWS public ECR, `docker.elastic.co`, GCP Artifact Registry, `ghcr.io/github`). Community-published samples almost always use Docker Hub or `ghcr.io`. The choice signals organizational backing and is an axis worth a sentence in the Docker description.

- **PyPI uvx is dominant for Python; npm npx for Node — but the Python+npm cross-publication pattern is rare and notable.** Only 2 samples cross-publish: rohitg00/kubectl-mcp-server (PyPI + npm wrapper) and stripe/agent-toolkit (`stripe-agent-toolkit` on PyPI + `@stripe/agent-toolkit` + `@stripe/mcp` on npm). These are categorized as *Cross-ecosystem packaging*. The pattern is rare because it doubles publication and version-coordination work for a usually-modest reach gain.

- **Hosted endpoints rarely live alone in the corpus.** Of the 11 hosted-endpoint samples, only 2 (slackapi, cloudflare) ship *no* installable artifact. The other 9 hosted-endpoint samples *also* publish PyPI/npm/Docker for self-host — most users hit the hosted endpoint, but the underlying server is also distributable. Vendors with operational infrastructure choose hosted as primary but rarely close the door on local install entirely.

- **Smithery and pre-built host installers are thin in the corpus** despite getting individual paths. Smithery has 13 samples, pre-built host installer/one-click only 3. These are interesting strategically but adoption is modest enough that the "install ergonomics" axis as a whole — Smithery + one-click installers + SDK CLI installer + interactive installer — represents fewer than 20 samples combined. The corpus doesn't strongly differentiate among these "automated-install" paths; they're all small clusters of authors solving the same friction (host config copy-paste) with different mechanisms.

- **Docker is the floor of multi-channel publication.** Every multi-channel-publication sample (10/10) includes Docker. Docker is the lowest-effort additional channel for a project already publishing PyPI or npm — and the corpus reflects that. If a project commits to multi-channel reach, Docker is always one of the channels.

- **Smithery and Multi-channel publication co-occur.** 4 of the 10 multi-channel samples (executeautomation, datalayer/earthdata, openags, qdrant) also appear under Smithery — Smithery is part of the cross-ecosystem reach strategy for projects already maximizing channels, not a substitute for any one channel.

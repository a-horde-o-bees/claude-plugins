# Depth Pass Refinements — Sample > Container artifacts

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

**Sample > Container artifacts (role-level)** — The role description currently disambiguates against `Distribution channel — Docker image` ("this role tracks the build artifact regardless of whether it's published"). Cross-corpus inspection shows the disambiguation does not hold cleanly for one path: `Published Docker image` is an artifact-AND-distribution claim, and every one of its 15 supporting samples also appears under `Distribution channel > Docker / OCI image`. The role's framing should sharpen the boundary so authors and the reconciler can tell which path captures which fact.

Sharpened framing — *"Container-related files in the repo and what role each plays in build, dev, and contribution. The boundary against Distribution channel: this role tracks files in the tree (Dockerfile shape, compose layouts, devcontainer config, baked-in security posture); Distribution channel tracks how end users obtain a runnable artifact (registry URLs, install commands). When the same Docker image is both published and consumed, the published-image fact lives under Distribution channel; this role records the in-tree Dockerfile shape that produced it."*

**Sample > Container artifacts > Dockerfile (single-stage, build-from-source)** — Description is accurate but bins 46 samples whose evidence shows clustering on three sub-axes the current text doesn't surface:

- *Slim-base + lock-file install* (the dominant baseline): `python:3.11-slim`, `node:22-alpine` plus `requirements.lock`, `uv.lock`, `package-lock.json`. Examples — reminia/zendesk-mcp-server (`requirements.lock`), duolingo/slack-mcp (`python:3.11-slim` + `uv run python main.py`).
- *Quality-of-life bridging touches*: crystaldba/postgres-mcp's host-address auto-remap (localhost → host.docker.internal on macOS/Windows, 172.17.0.1 on Linux). Mentioned in current description as "Sometimes adds quality-of-life touches" but understated — this is the *only* sample with explicit cross-platform host-address bridging documented.
- *Entry-point script wrapper*: HenkDz/postgresql-mcp-server uses an `entrypoint` script for runtime parameterization.

The vast majority (38+/46) report only "Dockerfile present" or "Dockerfile at repo root" with no further structure surfaced. The current description uses the qualifier "Universal across runtimes — present in nearly every sample even when not the primary distribution channel" — true within the 46 supporting samples but should be stated against the 82-sample role denominator (56% of samples in this role; not 56% of the corpus). Wording is imprecise.

Sharpened text suggestion — keep the existing structural description but tighten coverage framing: *"At 46 of 82 samples in this role (56% of the role's corpus, ≈45% of the full corpus), this is the lowest-common-denominator container shape across runtimes."* Drop the "even when not the primary distribution channel" hedge — the corpus shows the opposite is also common: many samples have a Dockerfile but list Docker as just one of several distribution channels.

**Sample > Container artifacts > No container artifacts** — Description bundles three structurally-distinct sub-postures that the supporting samples make visible:

- *Substrate replaces container* (4 samples): cloudflare ("Workers replace containers"), neondatabase ("deployment is Vercel-hosted instead of containerized"), upstash ("runtime is hosted; users don't run a local server"), awslabs/mcp-lambda-handler ("Lambda zip is the packaging target"). The container artifact is absent because *something else fills the deployment-substrate role*.
- *Bundle format replaces container* (2 samples): motherduckdb and sandraschi/email-mcp both have `.mcpbignore` for MCPB packaging — the MCPB bundle plays the container role.
- *Genuine omission* (16+ samples): no container, no replacement substrate — the project ships only language-package or source distribution. hannesrudolph, marlonluo2018, mukul975, twolven, sandraschi, etc. — host-direct install is the entire shape.

The current description mentions "MCPB bundling replaces the container role" and gestures at desktop applications / local-process IPC as reasons but doesn't name the substrate-replacement axis explicitly. The three-way split has cross-corpus support and could either be folded into the description or proposed as a split (see below).

Sharpened text suggestion — *"Three sub-postures appear: (1) substrate replaces container — the project's deployment substrate (Cloudflare Workers, Vercel, Lambda, hosted endpoint) supplants the container role; (2) bundle format replaces container — MCPB bundle is the packaging artifact; (3) genuine omission — no container and no substitute, host-direct install is the entire shape (most common, especially for stdio servers targeting desktop integrations)."*

**Sample > Container artifacts > Published Docker image** — Cross-corpus evidence shows this path is structurally overlapping with `Distribution channel > Docker / OCI image`: all 15 supporting samples appear under both. The description's claim *"Doubles as a distribution channel (consumers `docker pull`) and a deployment artifact (operators run the image directly)"* explicitly admits the overlap.

Per the role-level framing in this report: this path captures the registry-publication fact, which structurally belongs to Distribution channel. Container artifacts should track *what's in the tree that produces the image*. The right move is either to:

- Refocus the description on what the path adds *beyond* `Distribution channel > Docker / OCI image` — typically nothing new at the artifact level once the Dockerfile path captures the in-tree file. Then this path becomes a duplicate.
- Or rename to capture an in-tree fact this path uniquely holds — e.g., "Image-publishing CI workflow" if the focus is on the GitHub Actions / release workflow that pushes the image (apollographql captures this: "Docker image built and published via the release-container workflow"). That would tie the path to a tree artifact (workflow file) rather than a registry fact.

See *Proposed bucket merges* and *Cross-corpus observations* below.

Sharpened text suggestion (if the path stays as-is) — at minimum, lead with the cross-role pointer: *"Cross-role: this path overlaps with Distribution channel > Docker / OCI image — every sample here also appears there. The artifact-side fact this path captures is the existence of a release pipeline that publishes the image (often a GitHub Actions workflow or `release-container` job); the registry URL and `docker pull` command live under Distribution channel."*

**Sample > Container artifacts > Docker Compose for local dev** — Description accurate. Cross-corpus evidence shows two sub-flavors:

- *Single compose file* (most common, 6 of 8): standard `docker-compose.yml` orchestrating server + backing service.
- *Multi-variant compose layout* (2 of 8): korotovsky/slack-mcp-server ships `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.toolkit.yml`. This pattern is identical to what `Distribution channel > docker-compose variants` describes — same sample, same files, classified twice. AlwaysSany/deepl-fastmcp also has compose for "SSE/HTTP transports' multi-container orchestration" — straddles dev-loop and transport-mode-test.

The description claims "Compose owns the dev-loop experience, the Dockerfile owns the runtime artifact" — true for most, but normaltusker explicitly uses Compose for *deployment* (`docker-compose up -d kotlin-mcp-server`), not local dev. Single sample, but the description's framing should not categorically exclude prod use.

Sharpened text suggestion — soften the dev-vs-prod claim: *"Most often a local-dev orchestration concern (server + backing service for the test/dev loop), but a minority of samples document Compose as the production deploy path. Multi-variant compose layouts (`.yml` + `.dev.yml` + `.toolkit.yml`) appear when the project distinguishes operating modes meaningfully."*

**Sample > Container artifacts > Multi-stage Dockerfile** — Description accurate. Cross-corpus evidence: 4 samples cluster cleanly on language — 3 are TypeScript/Node (DaInfernalCoder, cyanheads/perplexity-mcp-server, mongodb-js — Node 18-Alpine builders), 1 is Rust (rust-mcp-stack with `clux/muslrust` builder + `alpine:latest` final). Path is well-defined; description could note the language pattern: multi-stage is reached for primarily by compiled-asset languages (Rust static binary) and by Node builds that want to drop dev dependencies from the runtime image.

Sharpened text addition — *"Across the corpus, multi-stage builds cluster on Node (drop dev dependencies from runtime image) and Rust (separate builder image with toolchain from minimal final image with just the static binary)."*

**Sample > Container artifacts > Multi-architecture image publishing** — Description accurate. Cross-corpus evidence: 4 samples — baryhuang (`linux/amd64`, `arm64`, `arm/v7`), github (multi-platform Dockerfile), lanbaoshen (multi-platform builds in Docker artifact path), microsoft (multi-arch on `mcr.microsoft.com`). All 4 are in the *vendor-published-image* posture; none are user-build-from-source. The path is genuinely about publish-time architecture coverage, not in-tree Dockerfile shape — like Published Docker image, this is closer to a Distribution channel concern than an artifact concern. Worth flagging.

**Sample > Container artifacts > Multi-Dockerfile (prod / dev split)** — Description accurate. Cross-corpus evidence — 2 samples with distinct motivations: elastic uses `Dockerfile-8000` for *port-convention tuning* (alternate port for specific deployments — EC2/ECS/EKS), mahdin75 uses `Dockerfile.local` for *base-image / tooling differences* (dev image differs from prod). Two distinct rationales bundled under one path; with only 2 samples, splitting isn't justified, but the description currently glosses both as "alternates" without naming the two motivations.

Sharpened text addition — *"Two motivations observed: alternate-port-or-environment tuning (same artifact, different deployment defaults) and dev-vs-prod base/tooling split (genuinely different images)."*

**Sample > Container artifacts > Per-server Dockerfile in monorepo** — Description accurate. Cross-corpus evidence — 3 samples (FuzzingLabs, awslabs/mcp, modelcontextprotocol/servers) all monorepo-of-servers shape; per-server Dockerfile exists *because* the monorepo packages many independent servers. Path is structurally tied to the *Repository layout — Monorepo* role. Worth a cross-role pointer.

Sharpened text addition — *"Cross-role: see Repository layout — Monorepo. This path appears only in monorepo-of-servers layouts; it is the artifact-level expression of the per-server packaging discipline."*

**Sample > Container artifacts > Vendor-namespaced image** — Description accurate. Cross-corpus evidence — 3 samples cluster on what counts as "vendor": Microsoft (`mcr.microsoft.com/playwright/mcp`), Elastic (`docker.elastic.co/mcp/elasticsearch`), and rust-mcp-stack (`mcp/server/...` Docker Hub MCP Registry namespace). The third doesn't fit "vendor-namespaced" cleanly — `mcp/server/*` is the Docker Hub MCP Registry, not a single-vendor registry. This is closer to `Distribution channel > Docker Hub MCP Registry` than to the corporate-vendor-registry pattern of the other 2. Likely a mis-placement; see below.

**Sample > Container artifacts > Devcontainer for contributors** — Description accurate. 2 samples (awslabs/mcp, geropl/linear-mcp-go); both use it for contributor onboarding. The path is unambiguously about *contribution surface* not runtime — the description states this clearly.

**Sample > Container artifacts > Docker-Compose backend for end-to-end tests** — Description accurate. 2 samples (ClickHouse `test-services/`, thenets ghost-mcp full Compose) — both bring up the *upstream service* the MCP server wraps, for integration tests, not the MCP server itself. Cross-role: this is the artifact-level expression of *Test stack — Integration tests with real backend*. Worth a cross-role pointer.

**Sample > Container artifacts > Hardened-by-default container posture** — Description accurate. 2 samples (FuzzingLabs full posture — non-root + capability drop + read-only mounts + resource limits; rust-mcp-stack non-root user only). Description claims "Surfaces in security-focused projects where the wrapped CLI tools are themselves attack surface; uncommon in general-purpose MCP servers" — true for FuzzingLabs (security-tools wrapper); less so for rust-mcp-stack (filesystem MCP server, security-conscious by design). The two samples fit the "security-conscious posture" frame even if only one is a "security-focused project."

Sharpened text addition — *"Two depths observed: full posture (FuzzingLabs — non-root + capability drop + read-only mounts + resource limits) and minimum-viable posture (rust-mcp-stack — non-root user only). The richer posture surfaces in projects whose wrapped tools are themselves attack surface; the lighter posture surfaces in projects with security-conscious authoring discipline."*

**Sample > Container artifacts > Vercel deployment config** — Description accurate. 2 samples (exa-labs, neondatabase) — both are hosted-endpoint deployments where Vercel is the substrate. Cross-role with `Deployment topology — Hosted SaaS endpoint` (and `Edge / serverless deployment`).

**Sample > Container artifacts > Cloudflare Workers config** — Description accurate. 3 samples (cloudflare, cyanheads/git-mcp-server, idosal/git-mcp). cyanheads's evidence frames Wrangler as "an additional deploy target alongside the Dockerfile" — meaning Workers config can coexist with a Dockerfile, contradicting the current description's *"There is no Dockerfile because the runtime substrate is the Workers platform."* Cross-corpus, the corpus is split: idosal and cloudflare have no Dockerfile (Workers replaces it), but cyanheads has both.

Sharpened text suggestion — soften the categorical claim: *"Often the only deployment artifact when Workers is the runtime substrate, but the corpus also shows Wrangler config coexisting with a Dockerfile when the project supports both deploy targets."*

**Sample > Container artifacts > `.mcpbignore` for bundle packaging** — Description accurate. 2 samples (motherduckdb, sandraschi/email-mcp). Cross-role with `Distribution channel > MCPB bundle / Desktop Extension manifest`. The path's name slightly mis-frames the artifact: `.mcpbignore` is the *exclusion file*, but the underlying artifact is the `.mcpb` bundle layout it controls. Renaming to "MCPB bundle layout (`.mcpbignore`)" would put the artifact first and the file second.

**Sample > Container artifacts > Azure deployment artifacts** — 1 sample (mongodb-js — `deploy/` with Azure guides). Description accurate but path is structurally a *Deployment topology* concern (where the server runs in production) rather than a container-artifact concern. Mongodb-js is the only sample; no cluster to split into. Flagged.

**Sample > Container artifacts > Docker Compose for multi-server orchestration** — 1 sample (FuzzingLabs). Description accurate; path is structurally tied to Repository layout — Monorepo and to Hardened-by-default posture (same sample). Cluster of 1 — not splittable.

**Sample > Container artifacts > Dockerfile.template as scaffold** — 1 sample (FuzzingLabs). Description accurate. Contribution-surface artifact distinct from runtime artifact — the description states this clearly.

**Sample > Container artifacts > Nix flake / NixOS module** — 1 sample (utensils). Description accurate but acknowledges *"Doubles as distribution (consumers `nix run`) and dev environment (`nix develop` provides a reproducible shell)"* — the dual role is identical to the cross-role concern flagged for Published Docker image. The Distribution channel role has a `Nix flake (\`nix run github:...\`)` path and a `Declarative NixOS / Home Manager module via nixpkgs` path; this Container artifacts entry duplicates both.

**Sample > Container artifacts > Podman alternative** — 1 sample (ahmedmustahid). The description frames this as documentation acknowledging Podman; the supporting evidence is "Podman documented as a Docker alternative for the same image." This is a *Documentation surface* concern (alternative-tool note in README) rather than an artifact concern — there is no Podman-specific file in the tree. Likely a mis-placement; see below.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

**Sample > Container artifacts > Dockerfile (single-stage, build-from-source)** — Sub-axis: *base-image discipline*. Cluster on slim/alpine bases with lock-file installs is dominant but most samples don't surface enough detail to characterize at the path level. Fold-in suggestion only — not enough cluster definition for a split.

**Sample > Container artifacts > Dockerfile (single-stage, build-from-source)** — Sub-axis: *production-runtime vs reference-recipe*. Some samples treat the Dockerfile as the production artifact (alexei-led: "ghcr.io image is the canonical distribution form"; voska/hass-mcp: "produces the runtime image used in production"), others treat it as a reference recipe consumers may or may not build (most of the 46). The current description hedges with "produces the runtime image used in production" but the corpus reality is more bimodal. Fold-in to description.

**Sample > Container artifacts > No container artifacts** — Sub-axis: *substrate-replaces vs MCPB-replaces vs genuine omission* — already detailed under Description sharpenings. Fold-in to description; not strong enough to split (combined evidence span is uneven).

**Sample > Container artifacts > Hardened-by-default container posture** — Sub-axis: *full posture (1 sample) vs minimum-viable non-root posture (1 sample)*. Too small to act on; fold into description.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

**Sample > Container artifacts > Published Docker image + Sample > Distribution channel > Docker / OCI image** — Cross-role merge candidate. Every one of the 15 samples under Container > Published Docker image also appears under Distribution > Docker / OCI image. The artifact-vs-distribution boundary doesn't justify two paths for the same fact. Resolution options:

- *Drop Container > Published Docker image; keep Distribution > Docker / OCI image as the single home for "this image is published."* The Container role retains Dockerfile shape paths (single-stage, multi-stage, multi-Dockerfile, per-server, etc.) but not the publication fact.
- *Refocus Container > Published Docker image on the in-tree publication-pipeline artifact (release workflow file).* Rename to "Image-publishing CI workflow" and link Distribution-side for the registry URL.

The first option is structurally cleaner; the second preserves an in-tree artifact angle that workflow-files do represent (apollographql's `release-container` workflow, github's multi-platform Dockerfile build pipeline). Reconciler should pick.

**Sample > Container artifacts > Multi-architecture image publishing → fold into Distribution > Docker / OCI image** — Same logic. Multi-arch is a *publication-time* fact (which archs are pushed), not a tree-shape fact (the Dockerfile itself doesn't intrinsically carry multi-arch — Buildx / GitHub Actions matrix does). All 4 supporting samples are also in Distribution > Docker / OCI image. Fold-in suggestion: a sentence in the Distribution path's description capturing the multi-arch axis (already partially present: "Multi-arch publication (linux/amd64, arm64, arm/v7) extends platform reach").

**Sample > Container artifacts > Vendor-namespaced image → fold into Distribution > Docker / OCI image** — Same logic. Vendor-namespacing is a registry-publication fact (which registry, what image namespace). Distribution's Docker / OCI image description already enumerates vendor registries inline.

**Sample > Container artifacts > Nix flake / NixOS module + Sample > Distribution channel > Nix flake (\`nix run github:...\`) + Sample > Distribution channel > Declarative NixOS / Home Manager module via nixpkgs** — Three paths for one sample (utensils). The Container artifacts entry duplicates both Distribution paths, exactly as Published Docker image does. Drop Container > Nix flake / NixOS module; keep the Distribution paths.

**Sample > Container artifacts > Vercel deployment config + Sample > Container artifacts > Cloudflare Workers config + Sample > Container artifacts > Azure deployment artifacts** — These three are all *substrate-deployment* configs (`vercel.json`, `wrangler.jsonc`, Azure `deploy/` directory) — files that exist *because the substrate replaces containerization*. Currently classified separately under Container artifacts; they don't belong to "container" semantically — they're substrate-replaces-container. Two structural options:

- *Merge into a single "Substrate-deployment config (no container)" bucket* with sub-rows for Vercel/Workers/Azure.
- *Move all three to Deployment topology* where they sit naturally alongside `Hosted SaaS endpoint`, `Serverless (Lambda + API Gateway)`, `Edge / serverless deployment`.

The second is structurally cleaner and matches what `_depth-distribution-channel-refinements.md` is already gesturing at for hosted-endpoint shapes. Reconciler should evaluate.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

No splits proposed. The cross-corpus evidence supports merges and description sharpenings rather than new structural splits. The two candidate splits surfaced during inspection — `No container artifacts` into 3 sub-postures, and `Multi-Dockerfile` into port-tuning vs dev-prod — both have evidence small enough that fold-into-description is the proportional response.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

**rust-mcp-stack--rust-mcp-filesystem** currently under `Container artifacts > Vendor-namespaced image` better fits `Distribution channel > Docker Hub MCP Registry` because the supporting evidence ("Published under the `mcp/server/...` Docker Hub MCP Registry namespace") describes the Docker Hub MCP Registry namespace, not a single-vendor private registry like `mcr.microsoft.com` or `docker.elastic.co`. Microsoft and Elastic are the actual vendor-registry samples; rust-mcp-stack is a Docker Hub MCP Registry sample.

**ahmedmustahid--postgres-mcp-server** currently under `Container artifacts > Podman alternative` is a poor fit because the supporting evidence is documentation prose ("Podman documented as a Docker alternative for the same image"), not an in-tree artifact. There is no Podman-specific file. This entry belongs under `Documentation surface` (alternative-tool note) or could be folded into the parent Dockerfile path's description as "Some authors document Podman as an alternative runtime."

**normaltusker--kotlin-mcp-server** currently under `Container artifacts > Docker Compose for local dev` may be mis-placed. The supporting evidence (`docker-compose up -d kotlin-mcp-server`) describes Compose as a *deployment* path, not a local-dev orchestration. Either the path's description should expand (proposed under Description sharpenings) or this sample moves to a deploy-oriented compose path. With only one sample fitting "compose for deployment" the description-expansion option is proportional.

**duolingo--slack-mcp** currently under `Container artifacts > Dockerfile (single-stage, build-from-source)` fits — but the supporting evidence ("Containerization-first pattern; no PyPI" — captured in Distribution channel > Docker / OCI image) tells a richer story than "Dockerfile present." The Dockerfile path here only captures the file's existence, not the *primary-channel* posture. Not strictly mis-placed, but the path is the wrong granularity to capture this sample's distinguishing fact. The Distribution channel path holds the substantive content.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

**The artifact-vs-distribution boundary doesn't hold in this role's current shape.** Five paths in Container artifacts (Published Docker image, Multi-architecture image publishing, Vendor-namespaced image, Nix flake / NixOS module, plus the substrate-deployment trio Vercel/Workers/Azure) capture *publication or deployment-substrate* facts that structurally belong elsewhere — Distribution channel for the first three plus Nix; Deployment topology for Vercel/Workers/Azure. The role's prose tries to disambiguate ("this role tracks the build artifact regardless of whether it's published") but the path-level structure doesn't follow through. Cleaning this up is the highest-leverage refinement available for this role.

**Container artifacts is a leaky abstraction across three sibling roles.** The same Docker fact splits across Container artifacts (file in tree), Distribution channel (registry publication), and Deployment topology (where the running container lives). Some samples are classified under all three; others only under one or two depending on what the sample's prose surfaced. The reconciler may want to consider: should this role narrow to *strictly tree-shape facts* (Dockerfile shape, compose layouts, devcontainer, hardening posture, contribution-surface scaffolds), and let Distribution channel + Deployment topology hold the publication and runtime-substrate angles entirely?

**Per-runtime container patterns cluster cleanly when visible.** Multi-stage Dockerfile clusters on Node and Rust. Multi-arch clusters on vendor-published images. Hardened posture clusters on security-focused projects. Devcontainer clusters on monorepos. None of these clusters are surprising, but the path-level descriptions don't currently call out the language/posture clusters even though every supporting sample exhibits them.

**Description-evidence asymmetry on Dockerfile (single-stage).** The path's description is the most detailed in the role (slim base, lock-file install, host-address remap, entry-point wrapper) but the supporting samples mostly say "Dockerfile present" — the description is reaching into corpus knowledge the supporting evidence doesn't carry per-sample. This is fine if the description honestly reflects the cross-corpus pattern, but the gap between "what this sample said" and "what the description claims" is widest here.

**The role's adoption table omits Lambda zip and Makefile-driven Docker build (count 0).** Both have entries in the adoption table at count 0 — neither has any supporting samples. They appear in the table because they were proposed in earlier passes but never picked up. Either delete (no evidence) or hold for the reconciler's discretion. They're not mis-placements but they're noise in the path inventory.

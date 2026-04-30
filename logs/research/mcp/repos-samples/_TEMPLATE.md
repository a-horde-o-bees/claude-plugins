---
log-role: reference
---

# Sample

Per-repo evidence for an MCP server. The literal level-1 heading is `# Sample` — uniform across every file in this directory so heading-tree tooling can aggregate cross-sample by chain key. The repo identity lives in the Identification section's `### url`, not in the heading.

The prose between this heading and the `---` separator below is **for the agent reading the template**, not template structure. Only the headings *after* the separator transfer to samples (when the sample needs them).

**How the template is consumed.** This template describes the *shape* of a sample through its heading tree. An agent reading the template learns which sections exist as canonical homes for which kinds of evidence, the canonical sub-purposes under each closed-set section (the `###` headings under each `##`), the open-enumeration sections where any sub-purpose name is allowed (slot is content-driven), and the freeform sections where no `###` headings appear at all (slot accepts paragraphs or bullets). Only the headings transfer from template to samples; descriptive prose under each heading in this template is for the agent, not for samples to copy. The heading tree is the single source of truth — there is no frontmatter declaration of structure that mirrors the headings.

**Section optionality.** Every section is optional. A sample includes only the sections relevant to its repo; sections that would have nothing to say are omitted entirely. Sub-purposes within a section are also optional; populate the ones the source supports, omit the rest. Heading order in samples should follow the order in this template — order is the only structural property carried by sequence; section numbering is not used.

**Sub-purpose vocabulary.** Sub-purposes use the canonical labels from this template's heading tree. Under a closed-set section, a non-canonical sub-purpose heading is a compliance violation — fix the sample (merge into the canonical vocabulary) or escalate to a template revision. Open-enumeration sections (Host integrations) accept any sub-purpose name; the template's `### <placeholder>` marker declares the slot but the canonical vocabulary is content-driven. Compliance tooling surfaces every name used as the "canonicalization workspace," not a violation list.

**Pitfalls discipline.** `### pitfalls observed` is optional within every section that lists it. Populate only when there is a real, section-specific pitfall worth surfacing. Empty pitfalls headings ("none noted in this repo") are not canonical — omit the heading. Generic gaps and "what couldn't be determined" notes belong in `## Gaps`.

**Where never-before-seen content goes.** When the source has content that doesn't fit any template section, the agent does *not* invent a new section. The two freeform catch-alls handle this: `## Notable structural choices` for distinctive facts about *this* sample that don't fit a labeled section; `## Unanticipated axes observed` for design dimensions or axes the original research framework didn't anticipate (explicitly the slot for "this is a new concept worth flagging"). Cross-sample analysis later spots clusters in those sections — recurring observations across multiple samples become candidate new sections in a future template revision. The feedback loop runs at template-revision time, not at sample-recording time, so the agent recording samples is never blocked by the template's current vocabulary. `## Gaps` is for *unknowns about the repo*, not for unaccommodated content patterns — Gaps describes information we couldn't extract; Notable structural choices / Unanticipated axes describe information we *did* extract that doesn't fit elsewhere.

**Conditional sections.** `## Python-specific` is conditional — present only when the repo's primary language is Python. Other languages omit the section entirely; do not adapt sub-purposes for other ecosystems.

**Filename convention.** `<owner>--<repo>.md` (double-hyphen separator). Not-found / unresolvable records go to `_missing--<best-guess>.md` with a brief note.

---

## Identification

Stable repo-metadata header.

### url

GitHub URL for the repo. `https://github.com/<owner>/<repo>` form.

### stars

Star count at time of research. Any form: integer (`646`), abbreviated (`24.7k`), approximate (`~158`), or `not captured`.

### last-commit

Most recent activity anchor. Any form: ISO date (`2026-04-18`), release tag (`v0.11.1`), version+date, activity description (`103 commits`), or `not captured`.

### license

License identifier. Dual-license repos record both (`Apache-2.0 / MIT`).

### default branch

Repo's default branch (`main` dominant, `master` legacy).

### one-line purpose

Single sentence summarizing what this MCP server does, extracted from the README opening.

## Language and runtime

### language(s) + version constraints

Primary language(s) and version floor (e.g. `Python >=3.10`, `Rust 2024 edition`, `Go 1.23+`).

### framework/SDK in use

Which MCP SDK or framework variant. Common values: raw `mcp` Python SDK, FastMCP 1.x / 2.x / 3.x, `@modelcontextprotocol/sdk`, `mcp-go`, `rmcp`, custom.

### pitfalls observed

Optional. Populate only when there is a real language- or runtime-level pitfall.

## Transport

### supported transports

Common values: stdio, Streamable HTTP, SSE (legacy), WebSocket, in-memory.

### how selected

Mechanism by which the active transport is chosen. Common values: default-only, CLI flag, env var, separate console-script entry, separate subcommand, URL path on a hosted server, auto-detect.

### pitfalls observed

Optional.

## Distribution

### every mechanism observed

Inventory of every distribution channel. Common values: PyPI, uvx, npm, npx, Docker (Hub / GHCR / vendor registry), Homebrew, Cargo, `go install`, GitHub release binary, MCP Bundle (`.mcpb`), Smithery, mcp-get, source clone, hosted SaaS endpoint.

### published package name(s)

Canonical package identifier(s) under each channel. When unpublished or remote-only, state explicitly.

### install commands shown in README

The README's recommended install one-liner(s), verbatim where possible.

### pitfalls observed

Optional.

## Entry point / launch

### command(s) users/hosts run

The exact command end users or MCP hosts invoke.

### wrapper scripts, launchers, stubs

Wrapper layer between the host and the binary, or `none` for direct invocation.

### pitfalls observed

Optional.

## Configuration surface

### how config reaches the server

Channels through which configuration arrives. Common values: env vars, CLI flags, JSON/YAML config files, `.env`, host-passed params, persistent state, OS-native config dir, URI/URL params, runtime tool-call reconfiguration. Document precedence between channels when multiple are supported.

### pitfalls observed

Optional.

## Authentication

### flow

Auth mechanism. Common values: none, static token, API key, bearer token, OAuth, JWT, AWS credential chain, kubeconfig, transport-conditional, multi-mode.

### where credentials come from

Source channel. Common values: env var, `.env` file, CLI argument, OS keyring, request header, OAuth provider, kubeconfig file, AWS profile / instance role.

### pitfalls observed

Optional.

## Multi-tenancy

### tenancy model

Common values: single-user, single-connection-per-instance, per-request tenant via auth token, workspace-keyed, base-directory sandboxed, tenancy-as-tool-argument, multi-spec composition, not applicable.

### pitfalls observed

Optional.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Inventory of MCP capability surfaces. List tool count and grouping; name resources/prompts/sampling/roots/logging when present. When per-primitive enumeration is useful (resource URIs, prompt names), use sub-bullets inside the paragraph rather than splitting into separate `###` sub-purposes.

### pitfalls observed

Optional.

## Observability

### logging destination + format, metrics, tracing, debug flags

Where logs go, what format, whether metrics/tracing exist, debug flags. `not documented in README` is a valid signal.

### pitfalls observed

Optional.

## Host integrations shown in README or repo

Open enumeration. One `### <Host>` per host the README documents. Body names integration form (JSON snippet, install badge, deeplink, registration command, plugin wrapper) and where it lives.

### <host name>

Placeholder marking the slot. Real samples replace the placeholder with one heading per host using the host's canonical name.

**Canonicalization rules.** Use canonical host names from the table; do not invent variants. Hosts not in the table get a new `### <Host>` with the source's verbatim name.

| Source variant | Canonical |
|---|---|
| Claude (when context implies Desktop), Claude (Desktop implied) | Claude Desktop |
| Cursor IDE | Cursor |
| Cline (VS Code), Cline with Amazon Bedrock | Cline |
| VS Code (Insiders), VS Code + GitHub Copilot, VSCode, VSCode Copilot Chat | VS Code |
| Google Antigravity | Antigravity |
| JetBrains IDE | JetBrains IDEs |

**What does NOT belong here.** Items that aren't host integrations move to the section they describe:

- Deployment targets ("Docker-based deployment", "EC2/ECS/EKS", "Cloudflare Workers as deployment") → Container / packaging artifacts or Notable structural choices
- Distribution channels ("HTTP bridge", "NixOS/Home Manager module") → Distribution
- Generic catch-alls ("Other", "Other editors/CLIs", "General MCP-compatible clients") → drop entirely
- Production references that are themselves MCP servers → Notable structural choices

When the README enumerates 10+ hosts as a flat list with identical integration form, one consolidated heading like `### MCP-compatible hosts` with the host list inline is acceptable.

When the section is empty (sub-server defers to parent monorepo, library/SDK with no host integrations), use a single paragraph rather than per-host empty entries.

### pitfalls observed

Optional.

## Claude Code plugin wrapper

### presence and shape

Whether the repo ships an in-tree Claude Code plugin wrapper, and the shape if present. Common values: `not present` (dominant — ~90% of corpus), `.claude-plugin/plugin.json`, `.mcp.json` at repo root, `.claude-plugin/marketplace.json`, full plugin layout (`skills/`, `commands/`, hooks). Negative answers are data — keep the section even when empty.

### pitfalls observed

Optional.

## Tests

### presence, framework, location, notable patterns

Tests presence; framework (pytest, vitest, jest, cargo-nextest, go testing); location; notable patterns (cassette recording, evaluation harnesses, multi-phase live suites, custom markers).

### pitfalls observed

Optional.

## CI

### presence, system, triggers, what it runs

CI system in use; trigger model; what jobs run.

### pitfalls observed

Optional.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Inventory of container and OS-packaging artifacts. List all present; specify multi-arch / multi-stage when relevant.

### pitfalls observed

Optional.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Developer-facing affordances.

### pitfalls observed

Optional.

## Repo layout

### single-package / monorepo / vendored / other

Top-level repository organization. Brief enumeration of top-level dirs and config files inline. Do NOT split into separate `### dirs`, `### config`, `### additional`, `### documentation` sub-purposes.

### pitfalls observed

Optional.

## Notable structural choices

Freeform. Bullets or short paragraphs — bullets when the source clearly enumerates discrete observations. Captures distinctive design or product choices that don't fit elsewhere — pinning conventions, dependency-set quirks, dual-mode architectures, safety flag schemes, multi-backend abstractions, lifecycle posture (deprecated, archive, vendor-published), license unusualness.

The home for cross-cutting structural facts. When a "pitfall" in another section is actually a structural observation about the whole repo, move it here. Also the home for never-before-seen content patterns about this specific sample — record them here rather than inventing a new section.

## Unanticipated axes observed

Freeform. Bullets or short paragraphs. Names design dimensions or axes the original research framework didn't anticipate — vendor-vs-community trust, paper-mode safety patterns, transport-specific concerns, bundled-tooling axes, capability gating models, dispatcher monorepos.

Explicitly the slot for "this is a new concept worth flagging." Cross-sample clustering of entries here is the feedback signal that drives template revisions; record what you saw, the orchestrator notices when it recurs.

Do NOT use `### decision dimensions this repo reveals` — that text is scaffolding from the original research prompt and should be stripped.

## Python-specific

Conditional — include only when the repo's primary language is Python. Other languages omit entirely.

### SDK / framework variant

Which Python MCP SDK is in use. Include version pin from `pyproject.toml` and import pattern observed.

### Python version floor

`requires-python` value. Note CI matrix confirming tested versions if README shows it.

### Packaging

Build backend (hatchling dominant; setuptools, uv_build, poetry-core, flit, pdm); lock-file presence; version-manager convention.

### Entry point

How the server is launched. Name actual console-script(s) registered and host-config snippet shape.

### Install workflow expected of end users

pip / pipx / `uv tool install` / uvx / poetry / from-source / Docker. Include the README's recommended one-liner.

### Async and tool signatures

Sync vs async tool declarations; explicit asyncio / anyio usage.

### Type / schema strategy

Pydantic / dataclasses / TypedDict / raw dict; auto-derived vs hand-authored schemas.

### Testing

pytest / pytest-asyncio / unittest / none. Fixture style.

### Dev ergonomics

`mcp dev`, `fastmcp dev`, MCP Inspector launcher, Makefile / Justfile, hot-reload tooling, type-check/lint toolchain.

### Notable Python-specific choices

Anything unusual about this repo's Python stack. Freeform paragraph.

## Gaps

Freeform. The canonical home for "what couldn't be determined within research budget" — unknowns about the repo, not unaccommodated content patterns. Each item names what's unknown and (optionally) what source would resolve it. Examples: "exact CI workflow contents — not extracted from README", "last-commit date — not surfaced via WebFetch", "Python version floor — `pyproject.toml` not opened".

Do NOT use `### what couldn't be determined` — that text is scaffolding from the original prompt; the section heading itself names the slot.

When a per-section "pitfall" content overlaps with a Gap item, the Gap is the canonical home — leave the per-section pitfalls slot empty (omit the heading).

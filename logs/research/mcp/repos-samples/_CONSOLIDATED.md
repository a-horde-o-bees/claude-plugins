# Sample

Heading-by-heading accumulation of synthesized findings across the 104 MCP server repos under `repos-samples/`. Empty sections are unsynthesized; populated sections carry the canonical synthesis for that section.

## Identification

Stable repo-metadata header. What we capture, how reliably each field surfaces from a README/landing-page fetch, and what the distribution of values reveals about the corpus shape — popularity skew, license discipline, branch-naming inertia, and the special case of monorepo sub-servers whose identity lives below the repo root.

### url

99/104 samples carry a standard `https://github.com/<owner>/<repo>` URL. The 5 outliers are all `awslabs/mcp` sub-servers (`aws-api-mcp-server`, `aws-documentation-mcp-server`, `bedrock-kb-retrieval-mcp-server`, `mcp-lambda-handler`, `openapi-mcp-server`) whose URLs use the `tree/main/src/<sub>` form to point inside the parent monorepo. This is the only multi-sample monorepo-with-per-sub-server-record in the corpus; other monorepos (`modelcontextprotocol/servers`, `cloudflare/mcp-server-cloudflare`, `mcp.science`, `FuzzingLabs/mcp-security-hub`) are recorded as single samples covering the whole repo.

### stars

Captured for 98/104 samples; the 6 unknowns are the 5 awslabs sub-servers (no independent star count under the parent monorepo) plus `slackapi/slack-mcp-plugin` (private/unlisted). Distribution skews heavy-tailed:

| Bucket | Count | Notes |
|---|---|---|
| 10k+ | 7 | `modelcontextprotocol/servers` 84.2k, `upstash/context7` 53.3k, `microsoft/playwright-mcp` 31.1k, `github/github-mcp-server` 29.1k, `jlowin/fastmcp` 24.7k, `googleapis/mcp-toolbox` 14.7k, `GLips/Figma-Context-MCP` 14.4k |
| 1k-9.9k | 22 | Vendor-authored servers and prominent community projects cluster here |
| 100-999 | 36 | The corpus middle |
| 10-99 | 24 | Long-tail community servers |
| <10 | 9 | Early-stage or low-discoverability projects |
| unparsed | 6 | 5 awslabs sub-servers + slackapi |

Mixed-precision encoding is universal — integers (`646`), abbreviated (`24.7k`), approximate (`~158`), and `not captured` all appear; the schema accepts all four shapes by design and corpus practice confirms the freedom is exercised.

### last-commit

The most volatile field. Only 51/104 surface a concrete date or version+date; 45/104 record `not captured` / `not surfaced` / `not extracted within budget`, 7/104 capture activity-only (commit count, "active on main") without a date, and 1/104 (`Azure/azure-mcp`) is `ARCHIVED` with conflicting dates between the GitHub banner and README body. Lifecycle status — `deprecated`, `archived` — appears here when the repo signals it explicitly: `Azure/azure-mcp`, `conikeec/mcpr`, `elastic/mcp-server-elasticsearch` are the three with explicit deprecation/archival flags. Pattern: when the README/landing page does not surface a recent activity anchor, recording the commit count or "active" tag is the corpus-accepted fallback.

### license

MIT and Apache-2.0 dominate (88/104 combined); the long tail of license outliers is small but instructive about the design space:

| License | Adoption | Exemplars |
|---|---|---|
| MIT | 58/104 | majority across community and vendor servers |
| Apache-2.0 | 34/104 | concentrated in vendor- and foundation-authored repos (`awslabs/*`, `cloudflare/*`, `apollographql/*`, `googleapis/*`, `microsoft/playwright-mcp`) |
| AGPL-3.0/v3 | 2/104 | `HenkDz/postgresql-mcp-server`, `normaltusker/kotlin-mcp-server` |
| EPL-2.0 | 2/104 | `bhauman/clojure-mcp`, `hugoduncan/mcp-clj` (Clojure-ecosystem default) |
| BSD-3-Clause | 2/104 | both Datalayer (`earthdata-mcp-server`, `jupyter-mcp-server`) |
| GPL-3.0 | 1/104 | `ckreiling/mcp-server-docker` |
| CC BY-NC-SA 4.0 | 1/104 | `jbeno/cursor-notebook-mcp` (NonCommercial — the only non-OSI license in the corpus) |
| unspecified / not captured | 4/104 | `getsentry/sentry-mcp` (LICENSE.md unread), `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` (no LICENSE confirmed), `pragmar/mcp-server-webcrawl` (not extracted), `slackapi/slack-mcp-plugin` (proprietary inferred) |

Two repos record dual-license relicensing: `modelcontextprotocol/kotlin-sdk` and `modelcontextprotocol/servers` both use "Apache-2.0 for new contributions / MIT for existing code," reflecting the official-MCP relicensing pattern. The schema's dual-license slash-form (`Apache-2.0 / MIT`) accommodates this without modification. The CC BY-NC-SA outlier and the proprietary slackapi entry mark the two ends of the OSS-vs-restrictive axis the rest of the corpus collapses around.

### default branch

`main` 92/104, `master` 12/104. Master-branch repos are a mix of older projects and a few recently-active ones: `FuzzingLabs/mcp-security-hub`, `alexei-led/k8s-mcp-server`, `conikeec/mcpr` (archived), `duolingo/slack-mcp`, `hugoduncan/mcp-clj`, `korotovsky/slack-mcp-server`, `lanbaoshen/mcp-jenkins`, `pragmar/mcp-server-webcrawl`, `qdrant/mcp-server-qdrant`, `sandraschi/email-mcp`, `upstash/context7`, `voska/hass-mcp`. No tertiary branch names appear — the binary main/master split exhausts the corpus.

### one-line purpose

Universally populated (104/104), with one near-empty entry (`Azure/azure-mcp`'s `TBD — repo archived; technical surface redirected to microsoft/mcp.` reflects the repo's own state rather than a corpus gap). Sentence shape converges on `<Domain> MCP server — <distinguishing detail>`, with the em-dash separating the categorical name from the differentiator. Differentiators commonly encode tool count (`28 tools`, `60+ tools`, `253 tools`), a structural fact (`Docker-only distribution`, `dual Node+Bun runtime`), an authoring signal (`Microsoft-authored`, `community-canonical`), or a lifecycle note (`deprecated`, `archived Feb 2026`). Several samples explicitly mark the repo as a framework/SDK rather than a server — `jlowin/fastmcp` ("Python framework — not a server"), `mark3labs/mcp-go` ("Go MCP SDK — framework for building MCP servers"), `awslabs/mcp-lambda-handler` ("Framework — not server — for building Lambda-hosted MCP servers"); the corpus carries that distinction in the one-liner rather than in a separate field.

## Language and runtime

### language(s) + version constraints

### framework/SDK in use

## Transport

### supported transports

### how selected

## Distribution

### every mechanism observed

### published package name(s)

### install commands shown in README

## Entry point / launch

### command(s) users/hosts run

### wrapper scripts, launchers, stubs

## Configuration surface

### how config reaches the server

## Authentication

### flow

### where credentials come from

## Multi-tenancy

### tenancy model

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

## Observability

### logging destination + format, metrics, tracing, debug flags

## Host integrations shown in README or repo

## Claude Code plugin wrapper

### presence and shape

## Tests

### presence, framework, location, notable patterns

## CI

### presence, system, triggers, what it runs

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

## Repo layout

### single-package / monorepo / vendored / other

## Notable structural choices

## Unanticipated axes observed

## Python-specific

### SDK / framework variant

### Python version floor

### Packaging

### Entry point

### Install workflow expected of end users

### Async and tool signatures

### Type / schema strategy

### Testing

### Dev ergonomics

### Notable Python-specific choices

## Gaps

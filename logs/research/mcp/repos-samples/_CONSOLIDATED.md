# Sample

Heading-by-heading accumulation of synthesized findings across the 104 MCP server repos under `repos-samples/`. Each section below mirrors the canonical heading tree from `_TEMPLATE.md` and accumulates: dominant patterns, adoption counts against the applicable sample subset, outliers and counter-examples worth naming, and per-entity citations supporting each claim.

Synthesis pending — populate via `ocd-run log research consolidate --chain "Sample > <Section>" --subject mcp` per canonical section. After all sections complete, sanity-check against `_phase-a-mcp-archive/_legacy-decisions-for-sanity-check.md` and reconcile divergences.

## Identification

### url

### stars

### last-commit

### license

### default branch

### one-line purpose

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

Open-enumeration. Synthesis pass replaces this prose with one `### <Host>` per host the corpus surfaces, ordered by adoption count, with body capturing the canonical integration form (JSON snippet, install badge, plugin wrapper) and the dominant variant.

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

Synthesis pending — cross-cutting structural facts that don't fit a labeled section. Cluster recurring entries from samples' `## Notable structural choices` blocks here.

## Unanticipated axes observed

Synthesis pending — design dimensions or axes the original framework didn't anticipate, surfacing where they recur across samples. Candidate signals for a future template revision.

## Python-specific

Conditional — applies to the 62 Python-carrying repos in the corpus.

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

Synthesis pending — what couldn't be determined within research budget. Aggregate the per-sample `## Gaps` entries and surface what's systematically missing.

# Release Methodology

Project-specific methodology for cutting tagged releases of this marketplace's plugins. Read by `/ocd:git release` to validate inputs, locate the manifest to bump, format the CHANGELOG, and execute commit/tag/push correctly.

## Versioning scheme

**Semver `x.y.z`** — major.minor.patch. The release series tracks whatever `y` is at the most recent tag; `z` auto-increments between tags. Tags on `main` only; no release branches.

## Manifest paths

Single version-bearing manifest in this marketplace:

- `plugins/ocd/.claude-plugin/plugin.json`

The glob `plugins/*/.claude-plugin/plugin.json` accommodates future plugins; bump each match in lockstep when more ship. Project `pyproject.toml` files (root, plugin, tests) carry runtime/test dependencies, not release versions.

## Auto-bump (out of release scope)

- **Mechanism**: pre-commit hook at `.githooks/pre-commit`
- **Trigger**: increments `z` on every commit to `main` that stages changes under the plugin tree (`plugins/<name>/`) other than `plugin.json` itself
- **Skip rule the release flow relies on**: commits that stage only `plugin.json` (and `CHANGELOG.md`) skip the auto-bump — that's the escape hatch the release commit uses

## Bump axis decision rules

- **`x` (major)** — breaking change to a public agent-facing surface: skill removed/renamed, MCP tool removed/renamed, CLI verb removed/renamed, manifest schema break, deployed-rule meaning inverted
- **`y` (minor)** — new user-facing capability: new skill, new verb, new MCP tool, new hook, new rule/convention, new behavior visible to consumers
- **`z` (patch)** — auto-incremented per commit between tags; not part of release flow. A `z`-only release is just a tag at the current auto-bumped version (no commit needed)

When categories straddle, pick the more conservative axis (larger bump) and surface the rationale in the review gate.

## Commit + tag conventions

- **Commit message**: `release v<x.y.z>`
- **Stage rule**: `plugin.json` + `CHANGELOG.md` only (avoids double auto-bump)
- **Tag format**: `v<x.y.z>` annotated, with message `release v<x.y.z>`
- **Push order**: `git push origin main <tag>` — single command pushing both refs

## CHANGELOG format

- **Format reference**: Keep a Changelog 1.1.0
- **Section heading**: `## [<version>] - YYYY-MM-DD` (UTC date)
- **Categories**: Added / Changed / Fixed / Removed (in that order; only include categories with entries)
- **Special rules**: do not log auto-bumped `z` values; the section heading carries only the released version
- **`[Unreleased]` policy**: pointer paragraph at release time; not maintained manually between releases — git log + the synthesizer are the sources of truth

## Synthesize source

- **Default range**: `<last-tag>..HEAD`
- **First release**: `HEAD` (no prior tag)
- **Commit-message convention**: `Topic — subject` style; topic prefix groups commits naturally (e.g., `Transcripts —`, `Principles —`, `Docs —`, `Logs —`, `Deployed —`)
- **Skip patterns**: `Deployed — ...` commits represent template→deployed syncs, not user-facing changes — treat as candidates for omission unless they introduce new deployed content

## Post-tag-push automation

- **Workflow file**: `.github/workflows/release.yml`
- **Trigger**: tag push matching `v*`
- **What it does**: verifies tag format `^v\d+\.\d+\.\d+$`; verifies `plugin.json` version at tag commit equals tag's version; runs full test suite via `bin/project-run tests`; creates GitHub release via `gh release create --generate-notes`

## Preconditions

- **Branch**: `main` (no release branches; tags live on main)
- **Working tree**: clean (no uncommitted, no staged)
- **Remote alignment**: local `main` matches `origin/main` (fetch first to verify)
- **Tag uniqueness**: target tag does not yet exist locally or on origin
- **Version monotonicity**: target version > current manifest version

## Install command for users

`/plugin marketplace add a-horde-o-bees/claude-plugins@v<x.y.z>`

Stable channel users pin to a specific tag. Dev channel users track main without a pin.

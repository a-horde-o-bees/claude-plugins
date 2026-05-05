# Sample

Mirrors of `https://github.com/anthropics/claude-plugins-community`. Read-only mirror of the community plugin marketplace for Claude Cowork and Claude Code; the `.claude-plugin/marketplace.json` lists 1636 community plugins (1,079,680 bytes) and is synced from Anthropic's internal review pipeline. 54 stars; default branch `main`; Apache-2.0 license; latest sync 2026-04-17 (PR #10). Repo carries only `.claude-plugin/marketplace.json`, `.github/workflows/close-external-prs.yml`, `LICENSE`, `README.md` — no plugin payload, no skills, no agents, no hooks, no bin scripts.

## Marketplace manifest layout

### Pure external aggregator manifest

Repo holds only `.claude-plugin/marketplace.json` (1,079,680 bytes, 1636 plugin entries) plus LICENSE, README, and one CI workflow. Every plugin is sourced externally via `url` (1461/1636, 89.3%) or `git-subdir` (174/1636, 10.6%); plus one stale string relative source (`./cowork-plugin-management`) whose target directory is not in the repo. The repo authors zero plugin content. Top-level keys are `name` (`claude-community`), `owner`, and `plugins` — no `metadata` wrapper, no top-level `description`, no top-level `version`, no `pluginRoot`, no `$schema`.

## Per-plugin discoverability metadata

### Description-only with sparse opt-in category

`description` is universal (1636/1636) and carries all discoverability weight. Only 45/1636 plugins (≈2.75%) carry a `category` string; among those 45, 12 distinct values appear including variant capitalizations (`development` vs `Developer Tools`) — uncontrolled vocabulary even within the opt-in subset. No `tags`, no `keywords` on any entry. Most entries rely on `name` + `description` only.

## Plugin source binding

### `url` clone with `sha` pin

1461 entries (89.3%) use `{source: "url", url, sha}` with universal SHA pinning — 1461/1461 carry a 40-char `sha`. Pinning is the contract on this source format; the entire marketplace can move only as a unit when the nightly sync updates SHAs.

### `git-subdir` into upstream

174 entries (10.6%) use `{source: "git-subdir", url, ref [, sha]}` reaching into a path inside an external monorepo. `url` is mixed in practice — 165/174 are bare `owner/repo` slugs and 9/174 are full `https://...` URLs. `ref` is dominated by `main` (173/174); only 1/174 uses a fixed ref (`v1.0.1`). Most git-subdir plugins float on upstream branch tip rather than a fixed ref, so SHA-pinning is essentially opt-out for this source format — the inverse of the `url` source where SHA-pinning is universal.

## Channel distribution

### Sync-PR cadence with no tags

Single `main` branch, single marketplace name `claude-community`; users install `<plugin>@claude-community` directly. Pinning happens per-plugin via `source.sha` or `source.ref`, not via channel split. Sync branches (`sync/manual-2026-04-17`, `sync/manual-2026-04-07`, `sync/manual-2026-03-31`, `sync/manual-2026-03-24`, `sync/manual-initial`, `sync/auto-vendor`, `sync/batch-plus-197`) are short-lived PR branches that merge into main and persist only as refs. Cadence is weekly with growing batch sizes (2026-03-23 214 plugins → 2026-03-24 500 → 2026-03-31 814 → 2026-04-07 1095 → 2026-04-17 1636 over ~4 weeks). The README references a "nightly sync" but observed cadence is weekly.

## Version coordination

### Marketplace-side pin via source ref

Pinning is done via `source.sha` (1461/1461 url entries) or `source.ref` (173/174 git-subdir entries use `main`). No `version` field on any entry; no `plugin.json` lives in this repo since it hosts no plugins. Authority sits on the marketplace side of the fence; upstream `plugin.json` versions are not surfaced.

## Tag and release lifecycle

### No tags at all

Zero tags on the repo. The entire release surface is the sync-PR merge stream. Every commit is effectively a release for any consumer running `claude plugin marketplace add anthropics/claude-plugins-community`. The aggregator has no independent release identity; its own "version" is just the commit SHA of the latest sync. Pinning to a marketplace snapshot requires a git commit SHA of this repo itself, which the standard install command does not capture by default.

## Plugin-component registration

### Marketplace-entry-only definition (no `plugin.json`)

Repo hosts no plugins of its own. Every plugin entry is sourced externally (`url` clone or `git-subdir` path-in-upstream); component registration for those plugins lives in each upstream repo's `.claude-plugin/plugin.json`. Per-entry surviving fields are `name`, `description`, `source`, and optionally `homepage` and `category` — five fields total. Upstream `version`, `author`, `license`, `dependencies`, `tags`, `keywords`, `strict`, `skills` are dropped at the mirror layer and resurface only after install.

## CI workflow shape

### Single PR-gatekeeper workflow

The only workflow is `.github/workflows/close-external-prs.yml` (1698 bytes), triggered on `pull_request_target` with `types: [opened, reopened]`. Uses `actions/github-script@v7` (major-tag pin, not SHA) to call `getCollaboratorPermissionLevel` on the PR author; if permission is not `admin` or `write`, posts a canned redirect comment pointing at `clau.de/plugin-directory-submission` and closes the PR via `pulls.update({state: 'closed'})`. No matrix, no caching, no test run, no manifest validation. Permissions on the workflow include `pull-requests: write` and `issues: write` to support the comment + close action.

### Organizational PR bouncer

The same `close-external-prs.yml` implements admin-controlled merging by closing every PR from non-admin/non-write users. Routes contributors to the external submission form rather than soliciting direct PRs.

## Marketplace validation

### No validation

No CI step validates manifest shape, version agreement, or frontmatter conformance. The 1MB `marketplace.json` can be merged with invalid entries (e.g., the stale `./cowork-plugin-management` source whose target directory is not in the repo) without being caught. All validation presumably happens inside Anthropic's internal review pipeline (the README references automated security scanning), but none of it is visible in the repo. The public-facing repo has no recovery path if the internal pipeline misses something — a malformed merge could publish a broken manifest to every consumer.

## Documentation surface

### Minimal consumer-facing README only

`README.md` at repo root is ~1.4 KB — short, consumer-facing; explains the read-only mirror model, install commands for Cowork (web) and Claude Code (CLI), and directs submissions to `clau.de/plugin-directory-submission`. No `CHANGELOG.md`. No `architecture.md`. No `CLAUDE.md`. No per-plugin READMEs (there are no plugin directories in this repo).

## License declaration

### Single repo-level license

Apache-2.0 (`LICENSE` file at repo root, 11358 bytes; SPDX identifier `Apache-2.0`).

## Community health files

### Anti-contribution with auto-close gatekeeper

The "contributing" path is intentionally routed away from the repo. `close-external-prs.yml` enforces this with a comment-and-close on every external PR. No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` — a first-time visitor encounters the redirect when they try to open a PR rather than discovering the gate at `.github/CONTRIBUTING.md` where GitHub's UI would render "before opening a PR" guidance.

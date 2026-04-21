# anthropics/claude-plugins-community

## Identification

- **URL**: https://github.com/anthropics/claude-plugins-community
- **Stars**: 54
- **Last commit date**: 2026-04-17T21:29:59Z (most recent merged sync PR #10)
- **Default branch**: main
- **License**: Apache-2.0 (SPDX: `Apache-2.0`)
- **Sample origin**: primary (Anthropic-owned; pure aggregator marketplace, not a plugin-hosting repo)
- **One-line purpose**: Read-only mirror of the community plugin marketplace for Claude Cowork and Claude Code; the `.claude-plugin/marketplace.json` lists all community plugins and is synced nightly from Anthropic's internal review pipeline.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (1079680 bytes, 1636 plugin entries)
- **Marketplace-level metadata**: none — top-level keys are only `name`, `owner`, `plugins`; no `metadata` wrapper, no top-level `description`, no `version`, no `pluginRoot`
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: none uniformly — only 45/1636 plugins (≈2.75%) carry a `category` string; no `tags`, no `keywords` on any entry. `description` is universal (1636/1636) and carries all discoverability weight. Most entries rely on `name` + `description` only
- **`$schema`**: absent
- **Reserved-name collision**: no — marketplace `name` is `claude-community`, which is the recommended handle users install from (`<plugin>@claude-community`)
- **Pitfalls observed**: per-plugin `category` is used inconsistently (12 distinct values among only 45 entries, including variant capitalizations like `development` vs `Developer Tools`) — because discoverability is optional and unscoped, even the 45 that opt in don't form a controlled vocabulary. One plugin (`cowork-plugin-management`) has a relative source `./cowork-plugin-management` but no matching directory exists in the repo — a stale/invalid entry that would fail for a user installing from this marketplace directly.

## 2. Plugin source binding

- **Source format(s) observed**: `url` (1461/1636, 89.3%) and `git-subdir` (174/1636, 10.6%); plus one string relative source `./cowork-plugin-management` (stale — dir not present in repo)
- **`strict` field**: default (implicit true) — field appears on 0/1636 entries; no explicit `strict` anywhere
- **`skills` override on marketplace entry**: absent — 0/1636 entries carry a `skills` field
- **Version authority**: marketplace entry only — pinning is done via `source.sha` (1461/1461 `url` entries carry a 40-char `sha`) or `source.ref` on git-subdir (173/174 use `main`, 1/174 uses `v1.0.1`). No `version` field on any entry; no `plugin.json` lives in this repo since it hosts no plugins. Authority sits on the marketplace side of the fence; upstream `plugin.json` versions are not surfaced here
- **Pitfalls observed**: git-subdir `url` field is a bare `owner/repo` slug for 165/174 entries and a full `https://…` URL for 9/174 — the doc-published `git-subdir` source allows both but the mix inside one manifest is a parsing surprise. Ref choice is dominated by `main` (173/174), meaning most git-subdir plugins float on the upstream branch tip rather than a fixed ref — the `url` source's SHA pinning is strictly enforced (1461/1461) while git-subdir pinning is essentially opt-out. The single string-source entry (`./cowork-plugin-management`) is an outright defect because the directory isn't in the repo.

## 3. Channel distribution

- **Channel mechanism**: no split — single `main` branch, single marketplace name `claude-community`; users install `<plugin>@claude-community` directly. Pinning happens per-plugin via `source.sha`/`source.ref`, not via channel
- **Channel-pinning artifacts**: absent — no `stable`/`latest` twin marketplaces, no split manifest, no dev-counter + release-branch pattern
- **Pitfalls observed**: none — channel split isn't the contract model; pin-per-plugin SHA is the stabilization layer. The trade-off is that the entire marketplace can only move as a unit (a nightly sync PR), so a user pulling this marketplace at time T gets a snapshot of whatever was current in the internal pipeline at T.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: none — 0 tags total on the repo
- **Release branching**: none — `main` is the only long-lived branch; sync branches (`sync/manual-2026-04-17`, `sync/manual-2026-04-07`, `sync/manual-2026-03-31`, `sync/manual-2026-03-24`, `sync/manual-initial`, `sync/auto-vendor`, `sync/batch-plus-197`) are short-lived PR branches that merge into main and persist only as refs
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent — no `plugin.json` at all in this repo; the marketplace manifest itself has no `version` field
- **Pre-commit version bump**: no — nothing to bump
- **Pitfalls observed**: release cadence is the sync-PR cadence (2026-03-20 scaffold → 2026-03-23 214 plugins → 2026-03-24 500 → 2026-03-31 814 → 2026-04-07 1095 → 2026-04-17 1636 — ~weekly with growing batch sizes). No tags means there is no way for a consumer to pin to a specific marketplace snapshot other than a git commit SHA of this repo itself; the README's doc-recommended `claude plugin marketplace add anthropics/claude-plugins-community` floats on `main`.

## 5. Plugin-component registration

- **Reference style in plugin.json**: not applicable — this repo hosts no plugins of its own (it is a pure aggregator). Every plugin entry is sourced externally (`url` clone / `git-subdir` path-in-upstream-repo); component registration for those plugins lives in each upstream repo's `.claude-plugin/plugin.json`
- **Components observed**: skills no / commands no / agents no / hooks no / .mcp.json no / .lsp.json no / monitors no / bin no / output-styles no — repo has only `.claude-plugin/marketplace.json`, `.github/workflows/close-external-prs.yml`, `LICENSE`, `README.md`
- **Agent frontmatter fields used**: not applicable — no agents in this repo
- **Agent tools syntax**: not applicable — no agents
- **Pitfalls observed**: because no plugins live here, the repo is invisible to any audit that expects `plugins/<name>/` layout — the marketplace is effectively a denormalized index pointing outward, and pattern-verification work that wants to observe a plugin's manifest has to traverse every `source.url` or `source.url + path` to reach the actual `plugin.json`.

## 6. Dependency installation

- **Applicable**: no — repo has no code, no scripts, no hooks, no runtime components; it ships a JSON manifest only
- **Dep manifest format**: none
- **Install location**: not applicable
- **Install script location**: not applicable
- **Change detection**: not applicable
- **Retry-next-session invariant**: not applicable
- **Failure signaling**: not applicable
- **Runtime variant**: not applicable
- **Alternative approaches**: not applicable
- **Version-mismatch handling**: not applicable
- **Pitfalls observed**: none — scope clean.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — no `bin/` directory, no executables, no shebang scripts anywhere in the repo
- **`bin/` files**: none
- **Shebang convention**: not applicable
- **Runtime resolution**: not applicable
- **Venv handling (Python)**: not applicable
- **Platform support**: not applicable
- **Permissions**: not applicable
- **SessionStart relationship**: not applicable
- **Pitfalls observed**: none.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable
- **Pitfalls observed**: not applicable — aggregator has nothing to configure.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none — repo has no `hooks/` or `hooks.json`
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: not applicable
- **Failure posture**: not applicable
- **Top-level try/catch wrapping**: not applicable
- **Pitfalls observed**: not applicable — no runtime surface.

## 10. Session context loading

- **SessionStart used for context**: no — no hooks of any kind
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no
- **SessionStart matcher**: not applicable
- **Pitfalls observed**: not applicable.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: not applicable.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — neither at the marketplace level nor in any of the 1636 plugin entries (plugin entries here carry only `name`, `description`, `source`, `homepage`, occasional `category` — no `dependencies`, no `version`, no `author`, no `license`)
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — zero tags on the repo, and the marketplace is a single flat list (not a multi-plugin source-of-truth repo where per-plugin tags would make sense)
- **Pitfalls observed**: if any of the 1636 upstream plugins declare `dependencies`, that information is lost at this mirror layer — the aggregator discards everything that isn't `name`/`description`/`source`/`homepage`/`category`, so dependency resolution necessarily happens downstream (at plugin install, against the fetched upstream `plugin.json`).

## 13. Testing and CI

- **Test framework**: none — no tests in the repo
- **Tests location**: not applicable
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: yes (one workflow)
- **CI file(s)**: `.github/workflows/close-external-prs.yml` (1698 bytes)
- **CI triggers**: `pull_request_target` with `types: [opened, reopened]` only
- **CI does**: automatic PR gatekeeping — uses `actions/github-script@v7` to check `getCollaboratorPermissionLevel` on the PR author; if permission is not `admin` or `write`, posts a canned comment directing submitters to `clau.de/plugin-directory-submission` and closes the PR via `pulls.update({state: 'closed'})`. No test run, no linting, no manifest validation
- **Matrix**: none
- **Action pinning**: tag — `actions/github-script@v7` (major-tag pin, not SHA)
- **Caching**: none — not applicable; the workflow does no build step
- **Test runner invocation**: not applicable
- **Pitfalls observed**: the workflow has zero manifest validation — the 1MB `marketplace.json` can be merged with invalid entries (e.g., the `./cowork-plugin-management` stale relative source) without being caught. The `pull_request_target` trigger with `pull-requests: write`/`issues: write` is the conventional pattern for close-on-open gatekeepers but it does run with repo-scoped secrets — safe here only because the inline script doesn't check out PR code. Major-tag pin on the third-party action means a compromised tag could inject code; SHA-pin would be the hardening, but the blast radius is small given the single-script scope.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — there are no releases (0 tags, 0 GitHub releases); distribution happens by sync PRs merging into `main`, not by tagged releases
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable
- **Pitfalls observed**: the "release" surface is implicit — every merged sync PR into `main` is effectively a release, but there is no corresponding tag/changelog/announcement, so downstream consumers have no structured way to detect "a new batch of plugins landed" besides polling `git log` on this repo.

## 15. Marketplace validation

- **Validation workflow present**: no — the only workflow closes external PRs; it does not parse or lint `marketplace.json`
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: not applicable — no skill/agent markdown files in this repo
- **Hooks.json validation**: not applicable — no hooks.json
- **Pitfalls observed**: all validation presumably happens inside Anthropic's internal review pipeline (the README references automated security scanning), but none of it is visible in the repo. The public-facing side has no sanity gate — a malformed merge could publish a broken manifest to every consumer running `claude plugin marketplace add anthropics/claude-plugins-community`. The stale `./cowork-plugin-management` entry is live evidence: no validator rejected a source pointing at a non-existent path.

## 16. Documentation

- **`README.md` at repo root**: present (~1.4 KB) — short, consumer-facing; explains the read-only mirror model, install commands for Cowork (web) and Claude Code (CLI), and directs submissions to `clau.de/plugin-directory-submission`
- **`README.md` per plugin**: not applicable — no plugin directories in this repo
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: absent
- **`CLAUDE.md`**: absent
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`. The "contributing" path is intentionally routed away from the repo (PR = auto-close) to the submission URL
- **LICENSE**: present (Apache-2.0, 11358 bytes)
- **Badges / status indicators**: absent
- **Pitfalls observed**: the anti-contribution posture is by design but worth flagging — a first-time visitor may not realize direct issues/PRs are unwelcome until they try. The README surfaces this clearly; the workflow enforces it with a comment. No `CONTRIBUTING.md` to make the gate discoverable at `.github/CONTRIBUTING.md`, which is where GitHub's UI would render "before opening a PR" guidance.

## 17. Novel axes

- **Pure aggregator marketplace pattern**: repo hosts *only* `marketplace.json` + LICENSE + README + one gatekeeper workflow. Every plugin is sourced externally via `source.url` (full clone) or `source.source: git-subdir` (path into upstream monorepo). This is a distinct distribution shape from "one repo = one plugin" or "one repo = N owned plugins" — it's an index with no authored content. Pattern doc candidate for a "marketplace shape" axis (self-hosting vs aggregating vs hybrid).
- **Read-only mirror + auto-close gatekeeper**: the `close-external-prs.yml` pattern (permission-check → close → redirect comment) is a distinctive contribution-routing mechanism. Pattern doc candidate as a "contribution posture" axis.
- **SHA-universal pinning for `url` sources, branch-dominant floating for `git-subdir`**: 1461/1461 `url` entries carry a SHA; 173/174 `git-subdir` entries use `main` as ref. The inconsistency across source types inside one manifest is a novel observation — different source formats create different pinning contracts.
- **Lossy aggregation**: only 5 fields survive the aggregator boundary (`name`, `description`, `source`, `homepage`, `category`). Upstream `version`, `author`, `license`, `dependencies`, `tags`, `keywords`, `strict`, `skills` are dropped from the mirror view and only resurface after install. Pattern doc candidate as a "field-preservation" axis for aggregators.
- **Weekly batch growth**: sync PRs land in growing batches (214 → 500 → 814 → 1095 → 1636 over ~4 weeks). The cadence metadata itself is a pattern candidate — how mirrored marketplaces advertise freshness.
- **`git-subdir` url format inconsistency**: bare `owner/repo` slug (165/174) vs full `https://` URL (9/174) within the same source type; both appear to be accepted by the plugin framework per the documented examples but the mix within one manifest is unusual.

## 18. Gaps

- Cannot observe how `git-subdir` with a bare `owner/repo` slug is resolved by Claude Code's plugin fetcher (assumed GitHub-only) — would need `docs-plugin-marketplaces.md` cross-reference or the plugin-install code path. The context resource at `/home/dev/projects/claude-plugins/research/claude-marketplace/context-resources/docs-plugin-marketplaces.md` was not opened within this budget.
- Cannot observe the *internal review pipeline* the README references (automated security scanning, approval flow) — that machinery lives in a private Anthropic repo and is not visible here. This is the actual source of truth for how entries land in `marketplace.json`; the public repo only shows the merge side.
- Cannot verify whether the nightly sync described in the README actually runs nightly — observed commit history shows weekly merges (2026-03-23, 2026-03-24, 2026-03-31, 2026-04-07, 2026-04-17), not daily. Either the internal pipeline batches, or the "nightly" wording in the README is aspirational/stale.
- Cannot verify whether the stale `./cowork-plugin-management` relative-source entry is a bug or an in-repo escape hatch for Anthropic-authored bundled plugins — the referenced directory isn't in the repo, but a dedicated fetch of the Anthropic-owned cowork plugin (if one exists at a separate repo) was not attempted within the WebFetch budget.
- Cannot verify whether consumers actually pin to a marketplace commit SHA vs always tracking `main` — would require checking the Claude Code CLI's `plugin marketplace add` implementation for whether it captures a ref.
- Did not sample any of the 1636 upstream plugin repos to confirm the `source.sha` pins correspond to existing commits — would require 1636 HEAD checks or a representative sample and was out of scope for this per-repo report.

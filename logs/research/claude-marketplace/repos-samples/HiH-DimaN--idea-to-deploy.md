# Sample

Mirrors of `https://github.com/HiH-DimaN/idea-to-deploy` (resolves to `https://github.com/hihol-labs/idea-to-deploy` after a 2026-04-20 owner rename from user `HiH-DimaN` to organisation `hihol-labs`; both paths resolve to the same repo id via GitHub redirect). A complete project-lifecycle methodology plugin for Claude Code: 25 skills + 7 specialised subagents + 13 enforcement hooks spanning discovery, planning, scaffolding, coding, testing, security/deps audit, migration, deployment, hardening, and session persistence. Default branch `main`, MIT licensed, `plugin.json.version` `1.20.3`, last commit `2026-04-20` (`chore: migrate repo URLs HiH-DimaN → hihol-labs across docs and promo (#52)`), 16 stars at sample capture.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root (1.8 KB), one plugin entry whose source is the same repo (`source.source: "github"`, `repo: "hihol-labs/idea-to-deploy"`). Top-level fields are flat: `$schema`, `name`, `description`, `owner`, `plugins[]`. No `metadata` wrapper. Marketplace-level `description` is `"Complete project lifecycle methodology — 25 skills + 7 specialized subagents + 13 hooks from idea to deployed product."`. `metadata.pluginRoot` absent.

### `$schema` declaration on marketplace.json

`$schema` present on `marketplace.json` with value `"https://anthropic.com/claude-code/marketplace.schema.json"`. Declarative only — no CI step validates against this schema; the schema link enables IDE-level validation for anyone editing the file.

### Custom non-schema fields on marketplace entries

Two non-schema fields appear on the plugin entry: `images: [url]` carrying `https://raw.githubusercontent.com/hihol-labs/idea-to-deploy/main/docs/demo.svg` (de-facto marketing-asset carrier; not in any documented marketplace schema), and `tags: ["community-managed"]` used as a provenance-signalling flag distinct from the `keywords` array. Permissive consumers ignore both; strict consumers reject them.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

Plugin entry carries `category: "development"`, a 16-entry `keywords` array (`claude-code`, `methodology`, `project-lifecycle`, `developer-tools`, `ai-coding`, `testing`, `deployment`, `code-review`, `security-audit`, `session-persistence`, `self-review`, `meta-review`, `daily-work-router`, `methodology-validation`, `product-discovery`, `safety-guardrails`), and `tags: ["community-managed"]` (single-element provenance flag).

## Version coordination

### Multi-site sprawl (5+ locations)

Five version-carrying files require simultaneous bumps per release: `plugin.json`, `marketplace.json`, README badge, `README.ru.md` badge, and per-skill `metadata.version` in any SKILL.md edited that release cycle. CHANGELOG v1.20.3 Ops section explicitly enumerates all five as a manual checklist. The meta-review rubric (`tests/meta_review.py`) validates post-hoc that all five agree on version. `v1.20.3` is in manifests and CHANGELOG dated 2026-04-18 but not yet in the API's tag list at inspection — either tag push lagged the commit or a patch release is in progress.

## Plugin source binding

### `source: github` with explicit coords or `ref` pinning

Plugin entry `{ "source": "github", "repo": "hihol-labs/idea-to-deploy" }`. Single format. Users install via `/plugin install hihol-labs/idea-to-deploy` from `main`.

### `strict` field default

`strict` not present on the plugin entry (default implicit). No `skills` override or per-component carving on the marketplace entry. Plugin components are discovered from `plugin.json` pointing at `./skills/` and `./agents/`.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split. Users consume from `main` via `/plugin install hihol-labs/idea-to-deploy`. Semver tags (`v1.20.3`, `v1.20.2`, ...) exist on `main` commits; no separate `stable-*` or `latest-*` marketplace. Consumers wanting a pinned version do so with a `@v1.20.x` ref. Release branches `release/*` exist (see *Tag and release lifecycle*) but are short-lived gates for the fixture-smoke workflow, not published channels.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Default branch `main`. Tags observed span `v1.2.0 → v1.20.2` (20+ tags, including `v1.3.0`, `v1.3.1`, then a jump to `v1.13.2` reflecting an internal version-scheme change rather than orphan commits). All commits on `main` use real semver directly — no dev-counter scheme.

### Short-lived `release/*` branches as workflow gate

Releases are cut by creating a `release/v1.x.y` branch, running `fixture-smoke.yml` on that branch (the workflow is otherwise disabled — see *CI workflow shape*), then merging back and tagging on `main`. `release/*` branches are PR-gated release scaffolding, not long-lived release channels. Topic branches `feat/v1.x.x-*` and `audit/*` accompany the cadence.

## Plugin-component registration

### Asymmetric registration: file paths for agents, directory for skills/commands

`plugin.json` contains `"skills": ["./skills/"]` and `"agents": ["./agents/"]`. No `commands`, `hooks`, `mcpServers`, or `monitors` fields. Discovery is directory-based from the listed roots.

### Out-of-band hook registration

13 shell/Python hook scripts live under `hooks/*.sh` but `plugin.json` has no `hooks` field. Registration is out-of-band: either `scripts/sync-to-active.sh` patches the user's `~/.claude/settings.json`, or the `/adopt` skill writes `$PROJECT_ROOT/.claude/settings.json` from `skills/adopt/references/project-settings-template.json`. The `/plugin install` flow delivers skills + agents but the hook layer requires a manual `bash scripts/sync-to-active.sh` or `/adopt` run. CHANGELOG v1.20.1 documents a regression: `check-review-before-commit.sh` existed in the repo but was never added to `DESIRED_HOOKS` in `sync-to-active.sh`, so users following the README got 12/13 hooks; the gap was closed by adding `scripts/verify-sync-to-active.sh` as a CI drift verifier. The `/adopt` settings template uses a substitution token `{{PLUGIN_HOOKS_DIR}}` resolving to `~/.claude/plugins/idea-to-deploy/hooks` (post-install path) with legacy fallback to `~/.claude/hooks` (sync-to-active.sh path).

## Component composition

### Skills (universal)

25 skills under `skills/<name>/SKILL.md`, organised by category (entry points, project creation, QA, daily work, supply-chain QA, operations, workflow). Skills act as the command surface via the `Skill` tool — no separate `commands` field.

### Agents

7 agents in `agents/*.md`: `architect`, `business-analyst`, `code-reviewer`, `devils-advocate`, `doc-writer`, `perf-analyzer`, `test-generator`.

## Skill authoring conventions

### Standard frontmatter

Skill frontmatter fields: `name`, `description`, `argument-hint`, `allowed-tools`, `license`, `metadata.{author, version, category, tags}`.

### `disable-model-invocation: true` for high-blast-radius skills

Applied to `/autopilot`, `/deploy`, `/migrate`, `/migrate-prod` (per CHANGELOG v1.20.1). Skills won't be auto-invoked via embedding-match on vaguely similar prompts; users must call by name, or a router skill must explicitly delegate.

### `context: fork` invocation hint

Present on `/autopilot`. Inferred subagent-like forked-context invocation for the auto-pipeline.

### `allowed-tools` with permission-rule syntax

Permission-rule syntax observed: `/kickstart` carries `Bash(git:*) Bash(npm:*) Bash(pnpm:*) Bash(docker:*) Bash(pytest:*) Bash(go:*) Bash(cargo:*)`; `/migrate-prod` carries `Bash(ssh:*) Bash(scp:*) Bash(rsync:*) Bash(docker:*) Bash(pg_dump:*) Bash(dig:*) Bash(curl:*)`.

### Mixed `allowed-tools` syntax

The same skill file mixes plain tool names and permission-rule syntax — e.g., plain `Read Write Edit Glob Grep` alongside permission-rule `Bash(git:*) Bash(npm:*)`.

## Agent declaration conventions

### Standard fields plus model / color

Agent frontmatter uses `name`, `description`, `model` (`opus` or `sonnet`), `effort` (`high`), `maxTurns` (15 or 20), `allowed-tools`. No `skills`, `memory`, `background`, `isolation`, or object-form `tools` permission rules. Example (devils-advocate): `model: opus`, `effort: high`, `maxTurns: 15`, `allowed-tools: Read Grep Glob`.

### `model` + `effort` + `maxTurns` for cost control

Agents declare `model`, `effort: high`, `maxTurns` (15 or 20) directly in frontmatter as orchestration knobs.

### Plain tool-name list

Agent `allowed-tools` is a space-separated list of plain tool names (`Read Grep Glob`), not permission-rule syntax. All 7 agents are read-only by design (no `Write`/`Edit` in their `allowed-tools`); agents return structured markdown that the caller skill writes.

### Read-only agents

All 7 agents (`architect`, `business-analyst`, `code-reviewer`, `devils-advocate`, `doc-writer`, `perf-analyzer`, `test-generator`) carry tool sets that exclude `Write` and `Edit`. Outputs are structured markdown handed back to the calling skill.

## Dependency installation

### Zero dependencies / stdlib only

Plugin ships markdown skills/agents + shell-or-Python hook scripts with zero runtime dependencies. All Python tooling uses Python 3.11 stdlib only — explicit design choice documented in `docs/CI.md` ("both scripts are intentionally zero-dependency"). No `requirements.txt`, no `pyproject.toml`, no `package.json`. `/plugin install` copies the repo into `~/.claude/plugins/idea-to-deploy/`; no `SessionStart` hook runs pip/uv/npm/bun. README lists Requirements as Python 3 (for hooks) + Bash (for scripts) + `claude` CLI v2.1+ (for the headless fixture runner) — assumed available on host with no `SessionStart` runtime probe. The `scripts/sync-to-active.sh` script is a sync-to-`~/.claude/` copy utility, not a dep installer; its change-detection style uses `diff -rq` for skills (content compare) and `cmp -s` for hooks/agents (byte-exact compare).

## User configuration and authentication

### No userConfig, env-var only

Neither `marketplace.json` nor `plugin.json` declares `userConfig`. No `${user_config.KEY}` substitution. The plugin has no tunable parameters — methodology behaviour is fixed. The only secret in the ecosystem is `ANTHROPIC_API_KEY` for the headless fixture-smoke CI job, provisioned as a GitHub Actions repository secret.

## Session context loading

### Per-prompt context reminder

No `SessionStart` hook event registered. Three hooks fire on every `UserPromptSubmit`: `session-open-diagnostic.sh` (first-turn diagnostics), `pre-flight-check.sh` (injects recent git history, active-session lockfiles, memory-index state per script docstring), and `check-skills.sh` (regex-scans the prompt and emits routing reminders for matched triggers). Per-turn cost is the trade-off versus per-session state management.

### `UserPromptSubmit` fuzzy-matched skill injection

`check-skills.sh` regex-scans the user prompt for trigger phrases and emits routing reminders via `hookSpecificOutput.additionalContext` JSON when matched. Trigger phrases are bilingual (English + Russian) in every skill's `## Trigger phrases` section.

## Tool-use enforcement

### Multi-pattern PreToolUse safety stack

Four hooks registered across three matcher groups, per `skills/adopt/references/project-settings-template.json`: matcher `Bash|Edit|Write|NotebookEdit` runs `check-tool-skill.sh` (reminds Claude to route via a skill before ad-hoc tool use; rate-limited; escalates to blocking after 3 consecutive ignores per `hooks/README.md`); matcher `Bash` runs `check-commit-completeness.sh` (blocks `git commit` when staged SKILL.md lacks referenced `references/`, triggers, or fixtures); matcher `Bash` runs `check-review-before-commit.sh` (requires `/review` invocation before commits touching >2 files); matcher `Write|Edit|MultiEdit` runs `check-skill-completeness.sh` (blocks writes to `skills/<name>/SKILL.md` when completeness invariants fail). Opt-in (not in `DESIRED_HOOKS`, not auto-synced): `careful.sh` (destructive-command warner for `rm -rf` / `DROP TABLE` / `git push --force`), `freeze.sh` (scope-restriction gate), `context-aware.sh`, `cost-tracker.sh`, `crash-recovery.sh`, `stuck-detection.sh`.

### Soft-then-escalating PreToolUse hook

`check-tool-skill.sh` is soft for the first 3 ignores (additionalContext reminders), then blocks. Most hooks fail-open with soft reminders injected as `additionalContext`; the four in `DESIRED_HOOKS` are documented in `hooks/README.md` as "Hard Enforcement (Blocking)" for commit-completeness and skill-completeness checks.

### Repo-scope self-restriction

Hooks `cd` to cwd and detect `.claude-plugin/plugin.json` at repo root; if absent, exit silently. Restricts enforcement to methodology repositories — running Claude in an unrelated repo sees no blocking behaviour. Prevents the plugin's hooks from interfering with unrelated projects but means the hooks never fire outside the plugin's own context unless `/adopt` has written a project `.claude/settings.json`.

### Documented bypass mechanism

`hooks/README.md` documents a `.methodology-self-extend-override` sentinel file at repo root that bypasses hard enforcement. The `docs/CI.md` defense-in-depth table names it "Only via documented `.methodology-self-extend-override` file." The hook's invariant is "block unless this file is present at repo root," not "block always" — a documented escape hatch for users legitimately extending the methodology.

## Hook output contract

### `hookSpecificOutput.additionalContext` envelope versus bare top-level

All hooks read JSON on stdin and write `hookSpecificOutput.additionalContext` JSON on stdout (observed in `check-skills.sh` module docstring). Hooks are silent (exit 0, no output) when no triggers match — keeps normal turns noise-free.

## Hook failure posture

### Silent-ignore graceful degradation

Hooks fail-open by design — `check-skills.sh` docstring says "Silent (exit 0, no output) if no triggers match"; the four hard-enforcement hooks block specifically, and the rest soft-warn via additionalContext.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. Feature unused.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field — single-plugin marketplace. Tags use plain `v1.x.y` form (no plugin-name prefix).

## Testing

### Stdlib-only Python rubric tests

Tests are zero-dependency Python 3.11 stdlib scripts: `tests/meta_review.py`, `tests/verify_snapshot.py`, `tests/verify_triggers.py`. Plus bash fixture-runners `tests/run-fixtures.sh` and `tests/run-fixture-headless.sh`. Test model is "structural-rubric + golden snapshots", not unit tests. Each rubric check has a stable ID — `M-C1`...`M-C16` (Critical) and `M-I1`...`M-I9` (Important) — referenced in CHANGELOG entries (e.g. "M-C12 regex now catches Markdown-bold counts", "CI Gate 1 caught the drift correctly confirming the gate's value"). Stdlib-only is an explicit design constraint per `docs/CI.md`: <30s runs, no supply-chain risk in CI itself, runnable locally without setup.

### Headless `claude -p` snapshot testing

`fixture-smoke.yml` (when enabled) runs the `claude -p` CLI in non-interactive `--input-format stream-json --output-format stream-json --no-session-persistence --dangerously-skip-permissions --max-budget-usd <N>` mode against 3 active fixtures (fixture-01: $10, fixture-02: $5, fixture-03: $5; total ~$8–$12 per release). Pre-seeded `stream.jsonl` carries the user turns. Output validated with `tests/verify_snapshot.py` against `expected-snapshot.json`. Outputs uploaded as 14-day artifacts. 17 fixture directories under `tests/fixtures/fixture-NN-<name>/` (each with `idea.md`, `notes.md`, `expected-files.txt`, `expected-snapshot.json`; 3 active have `stream.jsonl`, the rest are `status: pending` stubs).

### Centralized `tests/` placement

All tests under `tests/` at repo root.

### Retroactive CI as documented regression response

CHANGELOG v1.8.0 documents that CI was added specifically because the repo got "3 GitHub stars within 24h of publishing", flipping the "wait for first PR" cost/benefit. CHANGELOG v1.20.1 documents adding `scripts/verify-sync-to-active.sh` after the `check-review-before-commit.sh` registration drift was discovered.

## CI workflow shape

### Multi-workflow split by trigger and concern

Two CI workflows. `meta-review.yml` triggers on `push: branches: [main]` + `pull_request: branches: [main]` and runs `python3 tests/meta_review.py --verbose`, `python3 tests/verify_triggers.py`, and `bash scripts/verify-sync-to-active.sh`. `fixture-smoke.yml` triggers on `push: branches: ['release/*']` + `workflow_dispatch` (with `fixtures`, `model`, `budget` inputs) and runs the headless `claude -p` snapshot suite. Single Ubuntu runner, single Python (3.11), no matrix. Action pinning by tag (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`). No SHA pinning. No caching declared (stdlib-only Python removes the motivation).

### Disabled-channel skeleton

`fixture-smoke.yml` is fully written and committed but gated by both a job-level `if: false` AND absence of `ANTHROPIC_API_KEY`. Header comment frames it as "v1.16.0 initial state — skeleton only, not yet activated"; activation requires both provisioning the secret and removing the guard. Cost rationale (~$8–$12/release) documented in-tree.

### CI-trigger-as-signal-of-traction

CHANGELOG v1.8.0 documents that CI was added specifically because the repo gained 3 GitHub stars within 24h of publishing — the first-mover community signal flipped the cost/benefit on adding CI infrastructure.

## Marketplace validation

### Custom rubric covering methodology invariants

`tests/meta_review.py` runs as `meta-review.yml`'s primary step. Validates: version parity across `plugin.json`, `marketplace.json`, README badges; skill-count parity (25 skills); SKILL.md frontmatter fields (`name`, `description`, `license`, `allowed-tools`, `metadata.version`); `marketplace.json` internal consistency; subagent-contract disclaimers; trigger-phrase drift between each skill's `## Trigger phrases` section and the regex table in `hooks/check-skills.sh` (via `tests/verify_triggers.py`, enforced as gate M-C11); fixture snapshot schema validity; sync-to-active hook registration drift (via `scripts/verify-sync-to-active.sh`). Validator is Python+stdlib custom — not bun+zod, not `claude plugin validate`, not a pre-commit hook. Marketplace-schema validity per the `https://anthropic.com/claude-code/marketplace.schema.json` `$schema` link is not wired into CI (declarative only). Triggers on `push` to main and `pull_request` to main.

### Cross-manifest version-sync as validation

The meta-review rubric validates post-hoc that `plugin.json`, `marketplace.json`, README.md badge, README.ru.md, and per-skill `metadata.version` all agree on version. Catches drift but does not prevent it. Enforced via gates `M-C5/M-C6`. CHANGELOG v1.20.3 lessons-learned explicitly cites an instance where pre-merge `/review` missed the drift because the bump happened after review.

## Source-pin maintenance

### Derived-artifact drift detector

`tests/verify_triggers.py` cross-checks every `## Trigger phrases` list in `skills/*/SKILL.md` against the regex patterns in `hooks/check-skills.sh`. Treats the regex-driven skill router as a derived artifact of the SKILL.md bodies and enforces authoritative direction (SKILL.md is source of truth per `CONTRIBUTING.md`).

### Registration-list drift guard

`scripts/verify-sync-to-active.sh` cross-checks every `hooks/*.sh` against a `DESIRED_HOOKS` allowlist in `sync-to-active.sh`, with an explicit `EXEMPT` list for opt-in-only hooks. Added in v1.20.1 after `check-review-before-commit.sh` shipped to the repo but never landed in the sync script — users following the README got 12/13 hooks for two minor versions. Validates the registration list against the filesystem inventory with a documented exempt list.

## Release automation

### No release automation / manual

Releases are created via the GitHub UI (20 releases observed, all non-draft, titled `v1.x.y — <summary>`). No `softprops/action-gh-release`, no `release-please`, no `semantic-release`. `gh release create` or GitHub UI; not committed automation. CHANGELOG.md is Keep a Changelog 1.1.0 format. The meta-review rubric validates version-string parity at commit/CI time but does not gate tag creation. Full release automation deferred — `fixture-smoke.yml` is the release-gate skeleton (runs on `release/*` branches); cutting a release from a passing branch is manual. When `ANTHROPIC_API_KEY` lands, the `release/*` branch → smoke-passes → manual merge + manual tag pattern will become the cadence — still not `release:[published]`-triggered automation.

## Documentation surface

### Substantial root README + CHANGELOG + community files + badges

`README.md` at repo root with 24 top-level headings (Problem, Solution, Quick Start, How It Works, End-to-End Example, Skills (7 categories), Subagents, Skill Contracts, Call Graph, Recommended Setup, Quality Gates, What Gets Generated, Seamless Route Switching, Recommended Models, Who Is This For, Project Types, What This Does NOT Do, Troubleshooting/FAQ, Contributing, Requirements, Changelog, License, Author). README.md badges: License, Skills count (25), Agents count (7), Version (1.20.3), meta-review CI badge (live workflow status), Status (Stable), Type (Claude Code Plugin). Architecture content lives inline in README (Call Graph, Skill Contracts, How It Works) — no separate `architecture.md`. No `CLAUDE.md` at repo root: a CLAUDE.md template is shipped inside `/adopt` at `skills/adopt/references/claude-md-template.md` to be written into a legacy project's root when `/adopt` onboards the methodology.

### CHANGELOG with "Why" and "Migration" subsections

`CHANGELOG.md` in Keep a Changelog 1.1.0 format. Per-release sections: `Added`, `Changed`, `Fixed`, `Ops`, `Context`, `Rationale`, `Lessons learned`, `Deliberately not done (deferred)`. Entries cite external sources (e.g., v1.20.3 cites Karpathy analysis). The "Deliberately not done" sections enumerate deferred work with rationale per release (e.g., v1.20.3: "Test-first enforcement hook — rejected per ROADMAP_v1.21 criteria (n=0 signal, solo-maintainer surface cost)"). The "Lessons learned (meta-review gap)" sections post-mortem which gate caught what the author missed, feeding back into rubric improvements.

### Multi-language READMEs

`README.md` and `README.ru.md` (full Russian translation). README.md links to Russian README and to Changelog/Contributing/CI docs.

### Bilingual content

Trigger phrases are bilingual (Russian + English) in every skill's `## Trigger phrases` section and in every `check-skills.sh` regex. SKILL.md descriptions also bilingual (e.g., `code-reviewer` agent description lists Russian trigger phrases `'проверь код', 'code review', 'ревью', 'проверь PR', 'найди косяки'`). Bilingualism extends from documentation into the runtime regex matchers.

### Shipped planning corpus visible in public repo

Three roadmap files (`ROADMAP_v1.19.md`, `ROADMAP_v1.20.md`, `ROADMAP_v1.21.md`) accumulate one per planned minor version with no pruning convention beyond what's implicit in the release cycle.

### Promotion drafts in-repo

`docs/promotion/drafts/` contains marketing copy for six channels (HN, devto, habr, reddit, twitter, plus another). CHANGELOG v1.20.2 calls out "content correctness in promo drafts" and "demonstrative-bug quoting patterns" as a validator concern — the meta-rubric also scans promo drafts for drift (stale version/count references). Other supplementary docs: `docs/CI.md` (CI design + branch-protection walkthrough), `docs/CONTENT-PLAN.md`, `docs/competitive-analysis.md`, `docs/cast-to-svg.js` + `docs/demo.cast` + `docs/demo.svg` (asciinema demo pipeline).

## Community health files

### LICENSE + CODE_OF_CONDUCT + issue templates

`LICENSE` (MIT) at repo root. `CONTRIBUTING.md` is extensive — includes meta-review gate, `## Trigger phrases` canonicity rule, three-file requirement for new skills (SKILL.md + references/ + fixture). `.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md` present. No `SECURITY.md`, no `CODE_OF_CONDUCT.md`.

## Author identity and provenance

### Owner-rename in flight

Most recent commit (2026-04-20) migrates repo URLs from `HiH-DimaN` to `hihol-labs`. `marketplace.json.owner.name` and every plugin `author.name` still say `HiH-DimaN`, while `source.repo` and `homepage` already point at `hihol-labs/...`. Both owner paths resolve to the same repo id via GitHub redirect. Consumers reading `owner.name` alone get the pre-rename identity — a drift the meta-rubric does not check.

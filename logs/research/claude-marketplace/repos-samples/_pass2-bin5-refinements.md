# Pass 2 Refinements — Bin 5

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Marketplace validation > External validator referenced by name only` — Emasoft/token-reporter-plugin — `scripts/publish.py` invokes a validator named `cpv-validate` ("claude-plugins-validation") twice (pre-bump and post-bump) but the validator binary is not vendored or fetched into the repo. The validator is referenced by name only; its schema and field coverage are unknown to the plugin author at edit time. Distinct from the existing `External validator referenced by name` path under *Marketplace validation* if that path covers a different mechanism — verify whether to merge or keep separate.

  > Note: an `External validator referenced by name` path already exists (line 2682); confirm whether the Emasoft case fits that existing path. If yes, treat as a description sharpening (see below) rather than a new path.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Marketplace validation > External validator referenced by name` — current description may not cover the network-dependency failure mode the Emasoft sample illustrates. Sharpening: when the validator is fetched per-invocation (`uvx cpv-validate`) rather than vendored, a network failure on release day blocks the release. Add the network-availability constraint as a load-bearing trade-off of the pattern.

- `Marketplace validation > Cross-manifest version-sync as validation` — HiH-DimaN/idea-to-deploy adds a different facet: the validator targets methodology invariants (not just version parity) and the cross-manifest sync is one of many checks (alongside skill-count parity, frontmatter validity, trigger-phrase drift between SKILL.md and `hooks/check-skills.sh`). Sharpening: the existing path could note that "sync-as-validation" can be one rubric within a broader methodology validator that also checks structural invariants beyond version strings.

- `Tool-use enforcement > Documented bypass mechanism` — HiH-DimaN/idea-to-deploy ships a `.methodology-self-extend-override` sentinel file documented in `hooks/README.md` and `docs/CI.md` defense-in-depth table as the explicit bypass for hard-enforcement hooks. Sharpening: the existing path could note that the bypass is itself a sentinel-file convention; the hook's invariant is "block unless this file is present at repo root," not "block always." Names the override-file mechanism explicitly.

- `Bin entry mechanism > Python `bin/` script with uv injection` — Emasoft/token-reporter-plugin sharpens the Windows-portability constraint: README documents the cross-platform claim but does not document that the `.py` extension must be associated with Python on Windows for PATH-invocation to work. Also: the validator (CPV) flagged extensionless executables and `.sh` files as platform-specific, motivating the `.py` choice. Add the validator-driven choice rationale.

- `Tag and release lifecycle > Process-ancestry-verified pre-push gate` — Emasoft/token-reporter-plugin's `scripts/pre-push` walks the process tree via `ps -p <pid> -o args=` and rejects pushes to main unless `scripts/publish.py` is an ancestor process (absolute path match, with CWD-qualified relative-path fallback). Sharpening: the existing description could spell out the spoofing-resistance rationale ("env-var / marker-file schemes are trivially spoofable" — the plugin's own code comment) and note the chicken-and-egg constraint that `.githooks/pre-push` must be wired via `git config core.hooksPath .githooks` or a manual symlink before the gate is active.

- `Live monitoring and notifications > Status line via user-settings mutation` — IgorGanapolsky/ThumbGate ships a `statusLine` entry in `.claude/settings.json` that runs `node bin/cli.js statusline-render` (per-session status panel populated by hook output). Sharpening: this is observed only in the dogfood `.claude/settings.json` (not shipped to plugin consumers via `.claude-plugin/`), illustrating the dogfood-only-status-line variant.

- `Plugin-component registration > Out-of-band hook registration` — HiH-DimaN/idea-to-deploy: hooks are first-class enforcement (13 shell scripts under `hooks/`) but `plugin.json` has no `hooks` field. Registration is via `scripts/sync-to-active.sh` (patches the user's `~/.claude/settings.json`) or the `/adopt` skill (writes `$PROJECT_ROOT/.claude/settings.json` from a template). Sharpening: emphasize the contract split — `/plugin install` delivers skills + agents but the hook layer requires a separate manual step; a regression in this split was observed (a hook shipped to the repo but never landed in `DESIRED_HOOKS`, so users got 12/13 hooks for two minor versions).

- `CI workflow shape > Sprawling autonomous workflows` — IgorGanapolsky/ThumbGate has 36 workflows including ~20+ autonomous-operations workflows (`daily-revenue-loop.yml`, `instagram-autopilot.yml`, `gtm-autonomous-loop.yml`, `marketing-autopilot.yml`, `ralph-loop.yml`, `self-healing-auto-fix.yml`, `perplexity-command-center.yml`, etc.) running on cron. Orthogonal to plugin distribution but a hallmark of this repo's "the repo runs the business" stance. Sharpening: extend with the "repo as autonomous business operations driver" angle if the existing description is more conservative.

- `Channel distribution > Dual-asset filename aliasing on GitHub Release` — IgorGanapolsky/ThumbGate's `publish-claude-plugin.yml` uploads both `thumbgate-claude-desktop.mcpb` (channel-latest filename) and `thumbgate-claude-desktop-v1.14.1.mcpb` (versioned) via `cp`. Sharpening: existing description could clarify that this gives consumers both a "latest" link (silently rolls forward across majors) and a pinned link (stable for reproducibility), with the channel-latest behavior being explicit.

- `Release automation > Post-publish runtime smoke` — IgorGanapolsky/ThumbGate's `prove-packaged-runtime.js --package-spec "thumbgate@${VERSION}" --install-attempts 12 --install-delay-ms 10000` pulls the freshly-published tarball back from npm with retries to ride out CDN propagation, then smoke-tests it. Sharpening: the existing description may not cover the explicit retry-loop-for-CDN-propagation aspect (12 attempts, 10s delay) and the "publish verified only when the thing downstream users would pull actually works" framing. Add the closed-loop verification detail.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Categorization decisions worth flagging for the reconciler

- **Emasoft's only cloud workflow (`notify-marketplace.yml`) was placed under `## CI workflow shape > ### Minimal cloud CI`**, not under `### Cross-repo notify on plugin.json change` (which lives under `## Release automation`). The `Minimal cloud CI` description in the consolidated literally references the `notify-marketplace.yml` `repository_dispatch` pattern, so the categorization is precise. Same workflow then re-described under `## Release automation > ### Cross-repo notify on plugin.json change` from the release-automation angle.

- **Emasoft's `Process-ancestry-verified pre-push gate`** — the consolidated places this only under `## Pre-commit and pre-push hooks (git)`. I placed it there alone and folded the related content (release-script ancestry rationale, manual symlink instructions) into that single occurrence rather than duplicating across `## Tag and release lifecycle`.

- **ThumbGate's multi-adapter publish workflows (`mcp-registry-publish.yml`, `publish-codex-plugin.yml`, `publish-tessl.yml`)** — placed under `## Release automation > ### Multi-target release pipeline (npm + cross-repo marketplace dispatch)` since the surface is "one push triggers multiple distribution-target workflows in parallel." The existing path's description is npm + cross-repo dispatch but the same shape generalizes to ThumbGate's npm + GitHub `.mcpb` + MCP Registry + adapter-specific targets. The reconciler may want to broaden the path's qualitative description or split into a more general "multi-workflow target pipeline" path.

- **ThumbGate's `Pre-release tag suffixes on a single channel`** — moved from `## Tag and release lifecycle` to `## Channel distribution` to match the consolidated tree's section placement.

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **HiH-DimaN/idea-to-deploy "owner-rename in flight" content.** The sample documents that the most recent commit migrates URLs from `HiH-DimaN` to `hihol-labs`, but `marketplace.json.owner.name` and plugin `author.name` still say `HiH-DimaN`. Mapped to the existing `## Author identity and provenance` role with `### Owner-rename in flight` path. Confirm that the path applies as-is — the consolidated path name matches.

- **HiH-DimaN/idea-to-deploy bilingual methodology** (Russian + English trigger phrases in every skill, README.ru.md, `code-reviewer` agent description with Russian trigger phrases). Mapped to `## Documentation surface > Multi-language READMEs` and `### Bilingual content`. Both consolidated paths apply. Confirm whether `## Documentation surface > Bilingual content` should also surface the trigger-phrase / regex-table dimension (since the bilingual content extends into the runtime regex matchers, not just docs).

- **HiH-DimaN/idea-to-deploy ROADMAP_v1.xx.md files accumulating per planned minor version.** Mapped to `## Documentation surface > Shipped planning corpus visible in public repo`. The accumulation aspect (one per minor version, no pruning) may be a sharpening of the existing description.

- **HiH-DimaN/idea-to-deploy `images: [url]` non-schema field on marketplace plugin entry** — already in consolidated as `## Marketplace manifest layout > Custom non-schema fields on marketplace entries`. Confirm.

- **HiH-DimaN/idea-to-deploy `tags: ["community-managed"]` provenance flag** — already in consolidated under `## Marketplace manifest layout > Custom non-schema fields on marketplace entries`. Confirm.

- **HiH-DimaN/idea-to-deploy `disable-model-invocation: true` for high-blast-radius skills** — already in consolidated as `## Skill authoring conventions > `disable-model-invocation: true` for high-blast-radius skills`. Confirm.

- **HiH-DimaN/idea-to-deploy `context: fork` on a skill** — already in consolidated as `## Skill authoring conventions > `context: fork` invocation hint`. Confirm.

- **HiH-DimaN/idea-to-deploy `$schema` declaration on marketplace.json** — already in consolidated as `## Marketplace manifest layout > `$schema` declaration on marketplace.json`. Confirm.

- **HiH-DimaN/idea-to-deploy disabled-by-default committed CI workflow (`fixture-smoke.yml` with `if: false` and absent `ANTHROPIC_API_KEY`)** — mapped to `## Testing > Headless `claude -p` snapshot testing` and `## CI workflow shape > Disabled-channel skeleton`-adjacent. Confirm: the existing `Disabled-channel skeleton` path is under `## Channel distribution`; a disabled CI workflow may need its own path under `## CI workflow shape` if not already covered. Tentatively mapped under existing paths but flagging for reconciler review.

- **HiH-DimaN/idea-to-deploy trigger-phrase drift detector (`tests/verify_triggers.py`)** — mapped to `## Governance and self-audit > Derived-artifact drift detector`. Confirm.

- **HiH-DimaN/idea-to-deploy sync-to-active drift guard (`scripts/verify-sync-to-active.sh`)** — mapped to `## Governance and self-audit > Registration-list drift guard`. Confirm.

- **HiH-DimaN/idea-to-deploy methodology meta-gates with stable IDs (`M-C1`...`M-C16` Critical, `M-I1`...`M-I9` Important)** — mapped to `## Marketplace validation > Custom rubric covering methodology invariants` and `## Testing > Stdlib-only Python rubric tests`. The CI-check-as-named-entity angle may need its own path or sharpening.

- **HiH-DimaN/idea-to-deploy CHANGELOG "Deliberately not done" and "Lessons learned" sections** — mapped to `## Documentation surface > CHANGELOG with "Why" and "Migration" subsections` (closest existing path). The "Deliberately not done" angle may warrant a sharpening.

- **HiH-DimaN/idea-to-deploy bilingual trigger-phrase regex tables** — extends `## Documentation surface > Bilingual content` into the runtime layer (regex matchers in hooks). Cross-cuts documentation and tool-use enforcement; flagged for the reconciler.

- **IgorGanapolsky/ThumbGate dogfood-only `.claude/settings.json`.** The `.claude/settings.json` is in the repo for ThumbGate's own dev sessions — not shipped to plugin consumers via `.claude-plugin/`. Mapped via "Pitfalls observed" in each section to flag the shipping gap. Existing path coverage is a question: the dogfood pattern (where the plugin uses its own CLI against itself during development, hooks fire only on the developer's repo) doesn't map cleanly to a single path. Closest match is `## Sandbox and security posture` or a new path under `## Plugin/state separation`. Tentatively mapped via `Repo-local hooks in `.claude/settings.json`` (line 3413) under `## Distribution exclusion and dogfood layout`.

- **IgorGanapolsky/ThumbGate multi-adapter single-package shape** — `adapters/{amp,chatgpt,claude,codex,forge,gemini,mcp,opencode}/` ships in one npm tarball. Mapped to `## Cross-ecosystem distribution > Multi-adapter single-package shape`. Confirm.

- **IgorGanapolsky/ThumbGate proof pipeline as a test tier** — seven `prove:*` scripts emitting `proof/<area>/report.{json,md}`, distinct from `test:*`. Mapped to `## Testing > Node `node:test` chained suite` (line 2402, which mentions the prove tier as part of the existing description). Confirm.

- **IgorGanapolsky/ThumbGate publish-trigger paths-filter on `package.json`** with workflow-internal tag creation. Mapped to `## Release automation > Multi-trigger workflow with single-snapshot path`. Confirm.

- **IgorGanapolsky/ThumbGate silent-no-op regression detector** — mapped to `## Release automation > Silent-no-op regression detector`. Confirm.

- **IgorGanapolsky/ThumbGate version-sync-as-validation (`scripts/sync-version.js --check`)** — mapped to `## Marketplace validation > Cross-manifest version-sync as validation`. Confirm.

- **IgorGanapolsky/ThumbGate MCP Registry `server.json` with `$schema` pin** — mapped to `## Cross-ecosystem distribution > MCP Registry presence (`server.json`)` and `## Cross-ecosystem distribution > Multi-registry: PyPI + MCP Registry + ghcr.io + Claude marketplace` (the latter is the closest fit; ThumbGate's three-registry pattern is npm + GitHub Release .mcpb + MCP Registry, not exactly the consolidated path). Suggest the reconciler check whether a new path "Triple-target publish on single tag (npm + GitHub Release .mcpb + MCP Registry)" applies — the existing `Triple-target publish on single tag (PyPI + MCP Registry + Docker)` path describes a different combination.

- **IgorGanapolsky/ThumbGate changeset governance in CI** — mapped to `## CI workflow shape > Discipline-checking CI on push and PR`. Confirm.

- **IgorGanapolsky/ThumbGate `npx --yes --package thumbgate thumbgate serve` unpinned launch** — already covered by `## Dependency installation > Ad-hoc per-invocation fetch via `npx --yes --package``. Confirm.

- **IgorGanapolsky/ThumbGate `engines.node >= 18.18.0` declared via package.json** — could surface under `## Server runtime (MCP)` or `## Plugin source binding > `source: npm``. Tentatively flagged.

- **Emasoft/token-reporter-plugin `uv run --with <pkg>` per-invocation as alternative to SessionStart venv management** — mapped to `## Dependency installation > Ad-hoc per-invocation fetch via `uv run --with``. Confirm.

- **Emasoft/token-reporter-plugin marketplace-notify dispatch workflow (`notify-marketplace.yml` fires `repository_dispatch` event on `Emasoft/emasoft-plugins` when `plugin.json` changes)** — mapped to `## Release automation > Cross-repo notify on plugin.json change`. Confirm.

- **Emasoft/token-reporter-plugin HTML-always + inline-truncated dual-output for hook reports** — mapped to `## Hook output contract > Inline-truncated + full-HTML dual output`. Confirm.

- **Emasoft/token-reporter-plugin Env-var backcompat for userConfig (`TOKEN_REPORTER_<KEY>` env-var override)** — mapped to `## User configuration and authentication > Env-var fallback alongside userConfig`. Confirm.

- **Emasoft/token-reporter-plugin `bin/` directory with one Python wrapper using `uv run --with` internally** — mapped to `## Bin entry mechanism > Python `bin/` script with uv injection`. Confirm.

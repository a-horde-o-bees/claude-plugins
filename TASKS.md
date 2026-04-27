# Tasks

Project-scoped task list — outstanding work synthesized across the project, organized by theme for prioritization. Operational, not aspirational: every entry maps to a concrete next-action and graduates out as work lands.

Scope boundaries — sibling docs that overlap but each own a distinct slice:

- **This file (`TASKS.md`)** — project-scoped, scan-once view of what's open across the whole repo. Pulls from the docs below.
- **`SANDBOX-TASKS.md` (per sandbox branch)** — branch-scoped task list seeded by `/ocd:sandbox new` and `/ocd:sandbox pack`; read via `/ocd:sandbox tasks`; cleared on unpack so it never lands on main.
- **`logs/idea/<title>.md`** — full context for any task listed here; the idea log owns the detail, this file is a pointer.

## High priority

Items tagged `priority:high` in their idea logs' frontmatter — floated up for scan-once visibility. Full entries remain in their theme sections below.

- **`ocd:init-python-project` skill** — scaffold a fresh Python project with the patterns this repo dogfoods: project-root `tools/environment.py` + `tools/errors.py`, `bin/project-run`, testing harness, content-equality contract test, minimum doc trio. Foundation landed in centralize-tools (PR #1); the skill itself is the next branch. Full spec: [plan-init-project.md](plan-init-project.md)
- **Agent-synthesized CHANGELOG at release time** — `/ocd:git release` verb that crawls git log since last tag, agent-synthesizes a Keep-a-Changelog entry (grouping by topic, deconflicting cross-commit overrides), writes draft for operator review, tags + pushes. Drops `[Unreleased]` in favor of synthesis at release time. Full context: Methodology and meta section. [idea log](logs/idea/Agent-synthesized%20CHANGELOG%20at%20release%20time.md)
- **Per-plugin permission contribution** — each plugin with a CLI runner owns its own permissions template rather than coupling to ocd's. Blocker for the imminent blueprint plugin. Full context: Governance and ecosystem section. [idea log](logs/idea/Per-plugin%20permission%20contribution.md)
- **Standard system init + propagate internal resolution** — collapse the per-system `_init.py` boilerplate into `framework.standard_init()` (auto-deploys templates, rules, conventions, paths.csv per system) and drop `plugin_root`/`project_dir` args from `framework.deploy_paths_csv` (already globally resolvable). Currently every new system writes ~20–60 lines of duplicated deployment code; freshly-written calls perpetuate the anti-pattern. Full context: Infrastructure section. [idea log](logs/idea/Standard%20system%20init%20%2B%20propagate%20internal%20resolution.md)

## Active sandbox features

Four features packed off main onto sandbox branches. Each carries its own `SANDBOX-TASKS.md` at the sibling's project root — open the sandbox and run `/ocd:sandbox tasks` to read the running checklist.

| Feature | Branch | Status highlights |
|---------|--------|-------------------|
| Blueprint plugin parity | `sandbox/blueprint-plugin` | Mirror ocd's `systems/` layout; add `bin/blueprint-run`; update `run.py` auto-promotion; sweep SKILL.md invocations; rename colliding skills. 6 post-v1 improvements queued (external research ingestion, conditional measure clearing, PFN gaps, static content recipe, duplicate resolution timing, Phase 1 gate criteria). |
| audit-governance skill | `sandbox/ocd/audit-governance` | Exercise on full governance chain end-to-end; decide whether A/B workflow split is still live; self-audit via audit-static once stable. Open defect: `--target project` silently accepted. |
| audit-static skill | `sandbox/ocd/audit-static` | Verify positional argument resolution for all input forms; self-audit once stable. Open defect: can't resolve bare subsystem paths like `systems/navigator/server.py`. |
| update-system-docs skill | `sandbox/ocd/update-system-docs` | Design-only placeholder (`_DESIGN.md` is canonical). Implementation queue: discovery CLI, fact-bundle builder, navigator schema extension for `doc_verified_at` hashes, idempotence verification, end-to-end calibration on `systems/governance`. Once stable → mass documentation audit whole-project. |

## Skill surface polish

Quality-of-life improvements to existing shipped skills. Mix of older sandbox-exercise findings and newer idea logs.

- **Skill description framing polish on `/ocd:pdf` and `/ocd:navigator`** — sharpen toward explicit "when to use" trigger-verb framing. [idea log](logs/idea/Skill%20description%20framing%20polish.md)
- **`/ocd:log <bogus-type>` validation** — skill routes to `_add.md` without checking whether the type exists under `logs/`. Add pre-dispatch validation.
- **`/ocd:pdf` sensitive-file mkdir ceremony** — Workflow has no escape hatch when gate blocks `.claude/ocd/pdf/templates/` mkdir. Either document `--css <preset>` bypass, move mkdir behind a lazy initializer, or provide a flag that skips directory creation.
- **Scan output omits `staled N parent(s)` on single-parent cascade** — DB state correct, but user-visible summary doesn't include the count.
- **`setup init` no-op output is noisy** — prints all subsystem sections and "Done" even when deploy was a no-op.
- **`setup badverb` error comes from argparse, not SKILL.md unrecognized-verb branch** — either dead code in SKILL.md fallback or argparse shadowing.
- **`paths_upsert` returns `action: "updated"` for first-ever purpose on scan-inserted row** — semantics track row existence, not purpose transitions. Document or change so `"added"` covers first meaningful purpose assignment.
- **Log cleanup feature for `/ocd:log`** — add cleanup-oriented verb or mode that surfaces stale entries. [idea log](logs/idea/Log%20cleanup%20feature%20for%20ocd-log.md)

## Infrastructure and tooling

Work that improves the machinery agents operate through.

- **`ocd:init-python-project` skill** ⭐ priority:high — scaffold a fresh Python project with this repo's dev-infra patterns; sync templates via the propagation hook so they stay byte-equal to the canonical sources. [plan-init-project.md](plan-init-project.md)
- **Standard system init + propagate internal resolution** ⭐ priority:high — collapse per-system `_init.py` boilerplate into `framework.standard_init()` (auto-deploys templates, rules, conventions, paths.csv); drop redundant args from `framework.deploy_paths_csv`. [idea log](logs/idea/Standard%20system%20init%20%2B%20propagate%20internal%20resolution.md)
- **Callable-surface coverage crawler** — automate the `rules/testing.md` Callable Surface Coverage bar as a `/ocd:check` dimension. Walks the repo, lists every callable, confirms each has a test reference. [idea log](logs/idea/Callable-surface%20coverage%20crawler.md)
- **Check dimension — import-time state dependency** — catch systems with implicit cwd assumptions at import time. [idea log](logs/idea/Check%20dimension%20—%20import-time%20state%20dependency.md)
- **Expand check with community linter dimensions** — layer shellcheck, ruff, PyMarkdownLnt, and typos under `/ocd:check` as additional dimensions wrapping their findings into the unified `Violation` report. Project-specific rules stay; community rules add breadth. Adoption order: shellcheck → ruff → PyMarkdownLnt → typos. [idea log](logs/idea/Expand%20check%20with%20community%20linter%20dimensions.md)
- **JSON schema validators for Claude Code manifests** — validate `plugin.json`, `marketplace.json`, `hooks.json`, `settings.json` against documented Claude Code shapes via a `/ocd:check json-schema` dimension. Catches typos and missing fields before runtime. [idea log](logs/idea/JSON%20schema%20validators%20for%20Claude%20Code%20manifests.md)
- **Plugin init auto-stages deployed files to git** — `setup init` stages its own outputs when a git root is present, eliminating the agent judgment call about whether a deployed file should be tracked. Symmetric with `/ocd:git`'s existing downstream automation. [idea log](logs/idea/Plugin%20init%20auto-stages%20deployed%20files%20to%20git.md)
- **Move check to project root tooling** — `systems/check/` verifies dormancy across plugin systems; its domain is cross-plugin and inherently project-level. [idea log](logs/idea/Move%20check%20to%20project%20root%20tooling.md)
- **Convention-gate re-delivery measurement via total token exposure** — test that detects whether convention gate re-delivers per-file vs once-per-session. [idea log](logs/idea/Convention-gate%20re-delivery%20measurement%20via%20total%20token%20exposure.md)
- **Sandbox run — markdown-driven agent tests** — new `/ocd:sandbox run <test.md>` verb loading an agent-test markdown file and driving it via `claude -p`. [idea log](logs/idea/Sandbox%20run%20—%20markdown-driven%20agent%20tests.md)
- **Push blocking for project-wide integration testing** — broaden the pushurl-block pattern beyond evaluate-skill. [idea log](logs/idea/Push%20blocking%20for%20project-wide%20integration%20testing.md)
- **Refactor system — per-language codemod backends** — grow language-specific subcommands under `systems/refactor/` as cross-language rename needs surface. [idea log](logs/idea/Refactor%20system%20—%20per-language%20codemod%20backends.md)
- **Runtime skill evaluation via gate-scripted path exercise** — runtime evaluation harness driving skills through defined execution paths with hook gates as pass/fail signals. [idea log](logs/idea/Runtime%20skill%20evaluation%20via%20gate-scripted%20path%20exercise.md)
- **pdf-skill post-generation sanity check** — verify the produced PDF has expected structure (page count, no missing glyphs, searchable text). [idea log](logs/idea/pdf-skill-post-generation-sanity-check.md)
- **Backfill decision rationale from transcripts** — mine past conversation transcripts for decision rationale that never made it to `logs/decision/`. Extraction substrate now ships as `/ocd:transcripts`; the unbuilt half is the mining/query layer over the extracted chat. [idea log](logs/idea/Backfill%20decision%20rationale%20from%20transcripts.md)
- **Approval and permission signals export** — sibling `approvals_export` verb on `/ocd:transcripts` that pulls hook decisions, denial events, and session-allowlist additions out of raw transcripts into companion `<stem>_approvals.json` files. Reference taxonomy already captured. [idea log](logs/idea/Approval%20and%20permission%20signals%20export.md)
- **A-B test discipline for spawned work** — methodology for comparing two approaches when spawning parallel agents. [idea log](logs/idea/A-B%20test%20discipline%20for%20spawned%20work.md)
- **Import progress functionality from no-kill-cat-collective** — capability worth porting from the referenced external repo. [idea log](logs/idea/Import%20progress%20functionality%20from%20no-kill-cat-collective.md)
- **Research-and-refactor loop for blueprint** — disciplined loop taking a design goal and producing an ecosystem-aligned project. Prereq for blueprint work. [idea log](logs/idea/Research-and-refactor%20loop%20for%20blueprint.md)

## Governance and ecosystem

Work that shapes how rules, conventions, and cross-plugin interactions evolve.

- **Locked-down status hard to track across governance chain** — each rule/convention/skill has a "locked-down" state (systematically walked against governors and verified coherent); today that status is scattered. Needs a tracking mechanism. [idea log](logs/idea/Locked-down%20status%20hard%20to%20track%20across%20governance%20chain.md)
- **PFN recursion awareness on Spawn and Call** — current PFN doesn't make recursion semantics explicit. [idea log](logs/idea/PFN%20recursion%20awareness%20on%20Spawn%20and%20Call.md)
- **PFN self-description audit** — verify PFN prescribes chains of events unambiguously (e.g. prior issues with `isolation: "worktree"` and `When:` constructs that relied on runtime resolution). [idea log](logs/idea/PFN%20self-description%20audit.md)
- **Purpose-first framing for pattern research** — methodology discipline for authoring pattern docs: purpose-organized from the start rather than feature-organized and refactored later. [idea log](logs/idea/Purpose-first%20framing%20for%20pattern%20research.md)
- **Per-plugin permission contribution** ⭐ priority:high — each plugin with a CLI runner should own a permissions template its own init deploys. Blueprint / future plugins have no mechanism today. [idea log](logs/idea/Per-plugin%20permission%20contribution.md)
- **Permissions skill design** — surface for managing permissions as a user-facing operation. [idea log](logs/idea/Permissions%20skill%20design.md)
- **Opt-in clean for navigator log permissions** — three systems with non-template state need `clean()` implementations. [idea log](logs/idea/Opt-in%20clean%20for%20navigator%20log%20permissions.md)

## Methodology and meta

Tools and disciplines for how work gets done across the project.

- **Agent-synthesized CHANGELOG at release time** ⭐ priority:high — `/ocd:git release` verb that crawls git log, synthesizes Keep-a-Changelog entries with cross-commit deconfliction, tags + pushes. Replaces manual `[Unreleased]` curation. [idea log](logs/idea/Agent-synthesized%20CHANGELOG%20at%20release%20time.md)
- **needs-map forward-looking work** — reusable failure-mode-framing methodology, audit-governance inversion technique, stale-component cleanup. [idea log](logs/idea/needs-map.md)
- **Audit-testing skill for test infrastructure quality** — audit skill focused on test infrastructure rather than production code. [idea log](logs/idea/Audit-testing%20skill%20for%20test%20infrastructure%20quality.md)
- **honesty-as-paramount-design-principle** — proposed design principle (epistemic honesty / admit-what-you-don't-know). [idea log](logs/idea/honesty-as-paramount-design-principle.md)
- **workflow-rule-prefer-explicit-commands-over-loops** — proposed workflow rule. [idea log](logs/idea/workflow-rule-prefer-explicit-commands-over-loops.md)
- **Extend claude-marketplace research to cover discovery channels** — existing research covers marketplace shape; doesn't cover where authors get listed (Anthropic-blessed pipeline, auto-crawled aggregators, awesome lists, organic channels). Preliminary leads captured in the idea log; gated on `/log research` skill tree update landing first. [idea log](logs/idea/Extend%20claude-marketplace%20research%20to%20cover%20discovery%20channels.md)

## Friction and problems

Captured discipline gaps and concrete defects.

- **`auto_approval` misses if-case-function splitting** — splitter in auto_approval can fail to decompose certain bash compound shapes (shell-function definitions with if-cases inside). [friction log](logs/friction/auto_approval%20misses%20if-case-function%20splitting.md)
- No open entries under `logs/problem/` at the moment.

## Non-blocking concerns

Surfaced during earlier work; intentionally kept from promoting to action items until they become painful.

- **`install_deps.sh` plugin-binary collision check** — no guard for cases where `bin/<plugin>-run` collides with an existing PATH command. Low risk since `<plugin>-run` is unique-ish; `command -v` probe during install_deps could warn proactively.
- **`test_deploy_exits_zero` permissions test fixture** — pre-existing failure in `tests/test_invocation.py`. Needs fixture rework to place the recommended-permissions template where deploy expects it.
- **Print() usage review** — deferred during the logging convention drop. Pick up next time CLI output surface gets substantial edits.

## Exploratory / maybe-someday

Ideas without a near-term driver.

- **turbo-mode skill** — aggressive parallelism stance for spawnable work. [idea log](logs/idea/turbo-mode%20skill.md)
- **Session branching for multi-file workflows** — isolate parallel edits across files. [idea log](logs/idea/Session%20branching%20for%20multi-file%20workflows.md)

## Deferred

Known future work, not currently scheduled.

- **Community health files** — `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` at project root. Pull in when external contributors arrive. [idea log](logs/idea/Community%20health%20files.md)
- **adhd plugin** — name reservation only. Not yet created; noted so the name isn't taken.

## Priority tagging

Idea logs that warrant elevated attention add `priority:high` to their YAML frontmatter:

```yaml
---
tags: ["priority:high"]
---
```

The High priority section at the top of this doc lists these items with a short pointer to their theme-section home. In-place theme entries are annotated with `⭐ priority:high` so readers browsing by theme see the flag too.

The tag is sparing — use for items that are concrete blockers, imminent triggers (e.g. a dependency soon to arrive), or regression risks if left unaddressed. Not every good idea qualifies. When the trigger resolves or the blocker clears, drop the tag and let the item live in its theme section.

Only `priority:high` floats to the top. `priority:medium` / `priority:low` aren't a thing — unflagged means standard theme-section priority, decided by reader judgment when scanning the section.

## How this doc stays accurate

- New idea logs default to being added here in the relevant theme on creation.
- When a sandbox branch changes status (packed / opened / unpacked), update the Active sandbox features table.
- When an item completes, remove it from here; git history preserves the trail.
- When the classification drifts (an Exploratory item becomes Active, a Deferred item becomes Open), move the entry rather than letting it sit mis-grouped.
- Review on release-prep to catch items that should ship with the next release or explicitly defer.

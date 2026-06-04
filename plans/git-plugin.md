# Git plugin — full-lifecycle orchestration

North star and principles live in [`plugins/git/GOALS.md`](../plugins/git/GOALS.md) — read it first. This plan now tracks the **remaining** work; the original build path (PR loop, orchestrator, bump-check) shipped in #20.

## Shipped (#20 and earlier)

- **Lifecycle leaves**, submodule-aware (depth-first `.gitmodules` recursion): `/git-commit`, `/git-push`, `/git-ci`, `/git-doctor` (submodule conformance), `/git-release`.
- **PR loop (Workstream A):** `/git-pr-open`, `/git-pr-status`, `/git-pr-merge`, `/git-pr-cleanup` over a deterministic merge gate (`plugins/git/skills/git-pr-status/scripts/pr.py`) — two `gh` calls (PR state + commit-level CI annotations) + branch-protection probe → solo-vs-team path, blockers by severity. `open` idempotent + authors against the branch diff; `cleanup` uses PR merged-state as authority.
- **Orchestrator (Workstream B):** `/git-checkpoint` branches on context — feature branch → full lifecycle (commit→push→CI→open→status→merge `--cleanup`→sync base), each gate a hard stop; base branch → commit→push→CI. Leaves gate; orchestrator sequences.
- **bump-check (Workstream C):** `.github/workflows/bump-check.yml` + `scripts/bump-check.py` fail a PR that changes `plugins/<name>/` code without a version increment. Verified live on #20. Script paths standardized on the documented `${CLAUDE_SKILL_DIR}`.

Verified: `pr.py gate` classified PR #20 live (protection, strategies, mergeability, blockers); `bump-check.yml` passed live; cross-plugin dep check clean (`git` declares `writing`, `communication`). **Not yet done:** live dogfooding of the *deployed* orchestrator driving a real feature branch end-to-end (needs `claude plugins update`).

---

## Active workstreams (this push)

W2/W3/W4 landed this session (#21 harden+self-containment, #22 merge-gate, #23 Dependabot); **W1 (CI-doctor) is the remaining build.** git is at 0.0.12.

### W1 — CI doctor / integration capability (the gap) — first slice landed

**Built (this session):** `git-ci-doctor` skill + `scripts/ci_doctor.py` — `audit` (unpinned actions, missing `permissions:`, missing job timeout, missing concurrency; severity-classified JSON) and `reconcile` (branch-protection required contexts ↔ defined job names; flags required-without-job and jobs-not-required). Tested with synthetic + unit checks; dogfooded clean against our hardened workflows; `harden` verb proposes scoped fixes (SHA resolution via `gh api`) + applies on approval + offers Dependabot. **Follow-ons (not yet built):** wrap `actionlint` as a deeper validator; the per-stack hardened scaffolder; `tests/` harness beside the skill; `startup_failure` detector.

A `git-doctor`-shaped capability for **CI**, not submodules: diagnose → classify by fix-risk → propose scoped diffs → apply on approval. Research (2026-06) confirmed **no community Claude skill does CI setup/hardening** — genuine gap. Self-contained, `gh`-native, deterministic-script-backed (same shape as `ci.py`/`pr.py`), project-agnostic (no hardcoded project specifics).

**Shape:** new skill `plugins/git/skills/git-ci-doctor/` (name TBD; sibling to `git-doctor`) + packaged `scripts/ci_doctor.py` emitting JSON classification. Verbs/modes: `audit` (report), `harden` (apply fixes), `scaffold` (new workflow per stack). Consider whether `/git-ci` gains a `doctor` verb vs. a standalone skill — lean standalone (mirrors `git-doctor`).

**Checks to build (ranked by impact; from research):**

1. **SHA-pin audit + auto-fix.** Flag every `uses:` not a 40-hex SHA; resolve tag→SHA via `gh api repos/{o}/{r}/git/ref/tags/{tag}`; propose `uses: o/r@<sha> # vX.Y.Z`. Highest security ROI (the `tj-actions` supply-chain vector). Prior art: `pinact` (`--check` non-mutating gate + fix mode), `ratchet` (fallback).
2. **Least-privilege `permissions:` injector.** Flag any workflow lacking a top-level block; propose `permissions: contents: read` + per-job escalation inferred from job content (release→`contents: write`, PR-comment→`pull-requests: write`, OIDC→`id-token: write`). Scorecard `Token-Permissions` (0→10 from one line).
3. **Required-check ↔ job-name reconciler.** Read `gh api .../branches/{b}/protection` → `.required_status_checks.contexts`; diff against job names parsed from `.github/workflows/*.yml`. Flag required-but-no-matching-job (the "check stuck pending forever" failure) and gating-job-but-not-required. Propose the `gh api -X PUT` reconciliation. **This is also the engine for W2.**
4. **`startup_failure` / no-jobs-ran detector.** `gh run list --json conclusion,status,name` + `gh api .../actions/runs?status=startup_failure`; surface required contexts with no completed run. Warn when a *required* check sits under `concurrency: cancel-in-progress: true` (cancelled run never reports). Partly present in `/git-ci` already.
5. **`actionlint` wrapper.** Wrap the static binary (YAML, expression types, `runs-on` labels, `needs:` cycles, script-injection, deprecated runners) as the deterministic validator — embedded DBs, no API calls. Opt-in `act` (Docker) behind a capability check; never a hard dep.
6. **Per-stack hardened scaffolder.** Detect stack (node/python/rust/go) → emit a correct-by-construction starter that already bakes in #1, #2, `timeout-minutes`, `concurrency`, lockfile cache. Template + metadata-sidecar (à la `actions/starter-workflows`). Note: Rust has **no** official setup action — use `actions/cache`/`rust-cache`. `gh workflow` cannot create workflows — own the scaffolding via packaged templates + file writes.

**Report model:** Scorecard-style per-check pass/warn/fail + remediation text + a single consolidated "harden" PR (à la StepSecurity Secure-Repo) rather than drip fixes. **Reject:** `act` as hard dep, StepSecurity action/SaaS, Renovate/Mergify defaults.

Prior art URLs to mine during build: rhysd/actionlint, suzuki-shunsuke/pinact, ossf/scorecard, actions/starter-workflows, akin-ozer/cc-devops-skills (generator→validator loop).

### W2 — Merge-gate → required-checks ✅ LANDED (#22)

Done: `pr.py` reads `required_status_checks.contexts`; required-check fail/pending → hard, non-required fail/pending + annotation counts → advisory (never gate); conflicts/behind hard; review/draft soft. Verified live on #22 (required pass, markdown-lint + 7 annotations → advisory, `merge_ready: true`). Original design notes below.

`pr.py gate` currently **hard-blocks on any failing rollup check**, independent of branch protection — so this repo's perpetual report-only `markdown-lint` would block every PR even though GitHub reports `mergeStateStatus: UNSTABLE` (mergeable; only the non-required check fails) and required `test`/`validate` pass. Surfaced live on #20. **Standard team convention** (GitHub auto-merge, Mergify, Git Town, Graphite, merge trains) gates on *required* checks + reviews, never "any red."

**Fix:** classify against branch protection's `required_status_checks.contexts` (reuse W1 check #3) and/or trust `mergeStateStatus` — `BLOCKED`/`BEHIND`/`DIRTY` hard, `UNSTABLE` mergeable-with-advisory. Required-check failures hard; non-required failures + annotations → advisory/soft. This is also the **plug-and-play extension API**: a project expresses its own merge preconditions (version bump, license header) as *required CI checks*, and the generic gate honors them with zero skill changes. `bump-check` is exactly such a check.

Touches `plugins/git/skills/git-pr-status/scripts/pr.py` (`classify_gate`) + `git-pr-status`/`git-pr-merge` blocker handling. Update the `pr.py` module docstring's blocker model. After landing, **make `bump-check` a required status check** (branch-protection config; admin) so the generic gate enforces the project bump rule.

Decision settled: gate on required checks (the team standard). Open sub-choice at build time: read `required_status_checks.contexts` explicitly vs. trust `mergeStateStatus` — prefer reading contexts (explicit, lets us name *which* required check is red).

### W3 — Harden our own workflows ✅ LANDED (#21, Dependabot #23)

We don't follow the practices W1 would enforce. Audit of `.github/workflows/`:

| Practice | ci.yml | validate.yml | bump-check.yml | release.yml |
|---|---|---|---|---|
| `timeout-minutes` | ✗ | ✗ | ✗ | ✗ |
| `permissions:` block | ✗ | ✗ | ✗ | ✓ |
| Actions SHA-pinned | ✗ | ✗ | ✗ | ✗ |
| `concurrency:` | ✓ | ✗ | ✗ | ✗ |

Fix all four: SHA-pin every `uses:` (with `# vX.Y.Z` comment), add top-level `permissions: contents: read` (escalate per-job where a job writes — release pushes tags/commits), add `timeout-minutes`, add `concurrency` to PR-feedback workflows. These workflows become W1's first test subject. Not plugin code → no plugin bump, but lands via PR (required `test`/`validate`).

### W4 — Self-containment fixes ✅ LANDED (#21)

A shippable skill must not name the containing project's concepts. Leaks found:

- **`git-checkpoint/SKILL.md`** — description says "no marketplace, plugin-lifecycle concerns"; rule line names "Marketplace refresh, plugin-version sync, and restart recommendations." Genericize to "project-specific delivery steps live in a project-level wrapper" without naming marketplace/plugin-version.
- **`git-release/_synthesize.md`** — (a) references `.claude/ocd/git/release.md` — **wrong + project-specific path**; bootstrap uses `.claude/git/release.md`. Fix the path. (b) Hardcodes this project's commit-prefix examples ("Transcripts —", "Principles —", "Docs —") — genericize to abstract examples.
- **`git-release/assets/release.md`** — "multi-plugin marketplace" / "`/plugin marketplace add`" lines lean project-specific; `plugin.json` as one manifest example among npm/Cargo/etc. is fine. Soften the marketplace-specific lines to generic examples.

`.claude/git/...` and "the project's local config" phrasings are fine (generically refer to the consuming project).

---

## Deferred / carried

- **PFN realignment sweep (post-context-clear).** `/reauthor` sweep over all git skills aligning to the compressed PFN; **drop the `## Dependencies: /process-flow-notation` runtime-dep framing** (confirmed: skills are self-contained; there is no runtime "load PFN" mechanism — PFN is an authoring aid, the bodies stand alone); ensure skills **correctly invoke** the writing skills (namespaced `/writing:concise-prose` etc. + `Skill` in allowed-tools where invoked — note `git-pr-open` currently lacks `Skill`); **mechanically document** cross-plugin deps per best practice — `plugin.json dependencies` (the real mechanism; `git` already declares `writing`,`communication`) + a documentation-only `## Dependencies` section. Per claude-code-guide: `plugin.json dependencies` is plugin-level and official; `## Dependencies` is documentation, not an enforced contract.
- **Make `bump-check` a required check** — branch-protection config (admin); gates merges on the in-PR bump. Do after W2 so the gate model is required-checks-based.
- **Submodule hardening** (mined from jimmyff/submodules): pin-reachability guard in `/git-push` (verify each pinned submodule SHA is on its remote before pushing the parent — `git -C {sub} branch -r --contains {sha}`); batched cross-submodule commit-message review (one summary, not per-submodule `AskUserQuestion`); a submodule read/sync direction (ahead/behind vs pin; pull to tracking tips) as a `/git-doctor` read-mode or deferred verb.
- **Invocation-cost dedups** (measured; see [`assertions/skill-invocation/`](../plugins/skill-authoring/skills/skill-architecture/assertions/skill-invocation/)): `git-pr-status` dedup (~875 tok/run — have `/git-pr-merge` consume the status `/git-checkpoint` already holds instead of re-invoking); `git-doctor` dedup (hoist one pre-check to checkpoint, flag-gate commit/push to skip — weakens standalone safety, so flag-gated only). Self-recursion of commit/push/ci left as-is (per-submodule isolation worth the re-injection).
- **Live orchestrator dogfooding** on a deployed feature branch (needs `claude plugins update`).

---

## Message-authoring patterns (implemented; reference)

Applied across commit / PR / release — the plugin's distinctive value: adaptive description depth (weight scales with change weight; lead with why; omit empty sections); diff-avoidance ladder (seed from commit subjects, descend to diffs only when ambiguous); untrusted text is inert evidence (trust the diff over a contradicting message); authored against the diff not the journey; avoid `#1.` list syntax (GitHub auto-links to issue #1); heredoc always.

## Critical files

| Purpose | Path |
|---|---|
| North star | `plugins/git/GOALS.md` |
| PR loop skills | `plugins/git/skills/git-pr-{open,status,merge,cleanup}/` |
| Merge gate script (W2) | `plugins/git/skills/git-pr-status/scripts/pr.py` |
| CI doctor (W1, new) | `plugins/git/skills/git-ci-doctor/` + `scripts/ci_doctor.py` |
| Orchestrator | `plugins/git/skills/git-checkpoint/SKILL.md` |
| Self-containment (W4) | `git-checkpoint/SKILL.md`, `git-release/_synthesize.md`, `git-release/assets/release.md` |
| Our workflows (W3) | `.github/workflows/{ci,validate,bump-check,release}.yml` |
| bump-check CI | `.github/workflows/bump-check.yml` + `scripts/bump-check.py` |

## Out of scope

Per `GOALS.md`: PR review automation (inline comments, diff summaries), auto-merge *policy* ownership, stacked-PR management, release-after-merge orchestration. W1 adds CI *setup/hardening* — distinct from PR-review automation (it doesn't review code, it audits CI config).

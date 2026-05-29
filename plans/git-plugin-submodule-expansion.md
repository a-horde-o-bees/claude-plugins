# Git plugin submodule expansion

Extend the git plugin's skills to handle project submodules — registered submodules processed recursively before the parent, with the same commit/push/CI cycle the parent runs. Captures aligned design plus the related pre-rollout adjustments to git skills (allowed-tools, `## Dependencies` declarations, support-script extraction).

## Goal

`/git-commit`, `/git-push`, `/git-ci`, and `/git-checkpoint` become submodule-aware. For a project with N registered submodules, the workflow runs N+1 times — once per submodule (depth-first), then once at the parent.

## Driving observations

- User: "Does the current version of the git skills account for and update project submodules as well?" — currently they don't.
- User on submodule handling: "it should all be assuming changes are intentional or raising for suspicious ones, otherwise basically doing the workflow per registered submodule recursively before parent."
- User on tool variance: "I want to either make functions that run the commands for us so there is no variance... I think a support script might be better because most users probably won't put 'git' in their auto-approvals."

## Decisions captured

- **Classifier recurses** — the working-tree-state inspector walks into submodules rather than ignoring them.
- **Always runs submodules** — no conditional skip based on "no changes detected." Running unconditionally prevents accumulating dissonance from skipped iterations.
- **Non-blocking on suspicious changes** — surfaces suspicious patterns (large generated dirs, credentials, etc.) for user confirmation; does not block the workflow.
- **Depth-first order** — submodules before parent. A submodule's commit/push/CI completes before the parent's runs.
- **Support script over inline commands** — packaged executable invoked from skill bodies, not ad-hoc Bash steps. Reduces permission-prompt churn for users without `git` in their auto-approvals, and eliminates command variance across skills.

## Open items

- **Support script location** — `plugins/git/scripts/` adjacent to `skills/`, or inside `plugins/git/skills/_support/`?
- **Support script language** — bash (parity with current Skill body usage) or python (stricter parsing of `git submodule status`)?
- **Recursion ownership** — does `/git-checkpoint` orchestrate the recursive walk while `/git-commit`/`/git-push`/`/git-ci` each take a `--cwd` flag and act locally, or does each lower skill handle its own recursion? Cleanest split is checkpoint-orchestrates, leaf-skills-local — confirm.
- **CI within submodules** — most submodules won't have their own CI. `/git-ci` should soft-skip (no error) when a submodule has no `.github/workflows/`. Today it returns `no-runs` for this — verify that handling is appropriate as the recursion default.
- **Submodule detached-HEAD** — `/git-push` refuses detached HEAD. Submodules routinely check out specific commits (detached). Need either an explicit branch override or a "submodule mode" that handles detached HEAD gracefully (likely: push the commit to a tracked branch in the submodule's upstream, or skip with a clear message).
- **Frontmatter allowed-tools coverage** — user asked: "is the skill's frontmatter approved tools covering everything we call already?" Need an audit pass once the support script and recursion patterns are settled. Specifically: does `Bash(git *)` still cover all invocations? Does the support script need its own allowance line?

## Related pre-rollout adjustments to git skills

These were discussed in the same arc and are prerequisites or close adjacencies. None are submodule-specific, but they land cleanly in the same workstream.

- **`## Dependencies` declarations** — git skills currently don't declare their cross-skill dependencies. At minimum:
  - All 5 git skills depend on `/process-flow-notation` (their bodies use PFN; the agent needs the spec in context to interpret correctly when invoked from a cold session).
  - `/git-commit` depends on `/concise-prose`, `/description-authoring`, `/honesty` (already referenced inline at step 5 — `## Dependencies` makes the load mechanism explicit; inline mention then acts as the soft "surgical" reminder per `logs/assertions/skill-runtime/surgical-step-apply.md`).
- **Canonical scope grammar application** — once the canonical is settled in `logs/assertions/skill-runtime/` (currently being worked in another session — Variant D vs G1 hinges on depth coverage), apply the closing release line to whichever git skills carry behavioral directives. Most git skills are procedural (no behavioral rules to scope); `/git-commit`'s prose-generation step is the candidate where the loaded prose-discipline skills' release lines will matter.

## Dependencies

- **Canonical scope grammar settlement** — `logs/assertions/skill-runtime/` work currently underway in another session. The `## Dependencies` rollout above doesn't require the canonical to settle (the idempotent loading directive is already confirmed). The closing-release-line application does. Submodule expansion itself is grammar-independent.

## Status

Pending implementation. Design alignment captured 2026-05-21; awaiting user signal to start. Frontmatter audit and `## Dependencies` rollout are low-risk and can land before submodule recursion is implemented if desired — they don't depend on the recursion design.

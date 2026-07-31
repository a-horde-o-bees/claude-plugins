# DECISIONS

Choices behind the git skill's script-driven shape, each recorded over its rejected alternatives.

## The pipeline is a driver script; judgment enters at named stop-points

**Decision.** `gitflow.py` owns everything deterministic — submodule recursion, pin detection, conformance checks, staging, committing, the rebase-then-push flow — and the verb docs carry only the judgment contracts: topic grouping, message authoring, and the pin, untracked, and PII dispositions. The apply step accepts judgment only as a plan file.

**Forces.** Markdown process steps were routinely skipped because the agent already "knows" git — attentional compliance failed exactly where the process added its value. A driver that will not apply without a plan makes the judgment path the only path, and the skills governing that judgment fire at the stop-points where the plan is composed.

**Rejected.**

- *Markdown orchestration* (the prior form): each verb re-litigated its process against the agent's trained prior, and steps went silently unrun under load.
- *Full automation, messages included*: grouping and message quality are judgment governed by the authoring skills; templating them trades the skill layer away.

## Direct git and gh are denied; the driver is the doorway

**Decision.** A boxed repo denies the direct `git` and `gh` Bash patterns in its project settings — installed by `gitflow.py setup-deny` — so the driver, invoked via `uv run`, is the only route to those commands.

**Forces.** Deny rules take precedence over allows, so no skill-level `allowed-tools` grant can reopen direct access — the doorway must be a permitted executable whose subprocesses the Bash-pattern deny does not reach. That precedence is the feature: the box cannot be quietly unboxed from inside a skill.

**Rejected.**

- *Denying git only*: `gh` remains a side door for the PR and merge half of the lifecycle.
- *User-level deny instead of per-project*: boxes every repo at once, including ones whose flows predate the driver; per-project opt-in migrates repos deliberately.

**Consequence accepted.** Command-string matching can be evaded by compound commands; the box is strong friction plus routing, not a jail.

## Message authoring applies concise-prose and description-authoring only

**Decision.** The lens for commit messages and PR descriptions is `/concise-prose` + `/description-authoring`; `/grounded` is not applied, and its unverified-assertion guard survives as each surface rule's own clause — no claim the diff or a named decision doesn't carry.

**Forces.** Both surface rules pin every fact to diff visibility, which grounds by construction; the general verification skill adds context weight at the stop-point without adding a constraint that binds there.

**Rejected.** *Applying `/grounded` as a lens* (the prior form, on both surfaces): redundant with the surface rule for everything the message or description can contain, while loading verification machinery — API checks, research-scope bounding — with no referent at the authoring prompt.

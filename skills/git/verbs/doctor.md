# git doctor

> The repo-health doctor. A cheap, local detector (`scripts/detect.sh`) scans the problem domains that gate everyday work; each domain's repair process loads into context **only when that domain is flagged** — so a healthy repo (the common case) pays just the detector, which is why this is cheap enough to pre-check on every commit and push.

## Dependencies

- `partials/doctor-submodule.md`, `partials/doctor-default-branch.md`, `partials/doctor-ci.md` — per-domain processes, Called only for a detected domain (so unneeded repair content stays out of context).

## Variables

- `{verb}` — `ci` runs the CI domain on demand (optionally `audit` | `harden` | `reconcile`); empty runs the pre-flight detector across the always-on domains.

## Rules

- **Detect cheap, repair lazy.** `detect.sh` is local and fast; heavy per-domain content reads in only when its domain is flagged.
- **Severity gates the process.** `BLOCKING` (submodule drift — committing through it escalates Tier 1 into Tier 2 history pollution) halts until resolved or deliberately deferred. `ADVISORY` (default-branch, CI) is surfaced, never blocks.
- **Conform, don't circumvent.** Repairs restore canonical git structure; never a workaround. Per-domain risk-tiering and scoping live in the components.

## Process

1. {verb}: first token of this verb's arguments
2. If {verb} is `ci`: Call: partials/doctor-ci.md ({ci-args}: remainder of this verb's arguments); Exit process — on-demand CI domain
3. {detect}: bash: `sh ${CLAUDE_SKILL_DIR}/scripts/detect.sh` — capture stdout + exit code + stderr
4. If `STATUS: not-a-repo`: Exit process — not a git repository
5. If `STATUS: healthy`: Exit process — emit ### healthy
6. For each problem line in {detect} stdout (`<domain> <severity> <detail>`), dispatch by domain:
    - `submodule` → Call: partials/doctor-submodule.md (the {detect} stderr state table is its diagnosis input)
    - `submodule-routing` → Call: partials/doctor-submodule.md (routing-gap mode — write the missing native `.gitmodules` key)
    - `default-branch` → Call: partials/doctor-default-branch.md
    - `ci` → Call: partials/doctor-ci.md ({ci-args}: `audit`)
7. Emit ### result

## Report

### healthy

```
Repo health: clean — no blocking or advisory problems detected.
```

### result

```
Repo health:
{per domain handled: <domain> (<severity>) — repaired | deferred | advised, with its component's surface}
Blocking unresolved: {yes — do not commit/push until resolved | none}
Next: {what the caller must decide, or — proceed}
```

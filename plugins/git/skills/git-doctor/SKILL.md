---
name: git-doctor
description: Use when a repository's mechanically-detectable health needs checking or repair before commit/push/checkpoint, or on demand. Submodule structure broken — "fix submodules", "git submodule status shows nothing", interior files staged as blobs, a commit pre-check reported drift. CI config on demand — "audit my CI", "harden the workflows", "pin my actions", "are my required checks wired", "why is a required check stuck pending". Runs a cheap mechanical detector and dispatches into the affected domain only — submodule conformance (blocking; reversible index fix vs. destructive history rewrite), default-branch resolvability (advisory), CI config (on demand / when workflows change). Diagnoses, classifies by repair risk, proposes scoped fixes, applies only on approval. Conforms to canonical git; never rewrites history or force-pushes automatically.
argument-hint: "[ci [audit|harden|reconcile]]"
allowed-tools:
  - Bash(git *)
  - Bash(sh *)
  - Bash(gh *)
  - Bash(uv run *)
  - Read
  - Edit
  - AskUserQuestion
---

# /git:git-doctor

The repo-health doctor. A cheap, local detector (`scripts/detect.sh`) scans the problem domains that gate everyday work; each domain's repair workflow loads into context **only when that domain is flagged** — so a healthy repo (the common case) pays just the detector, which is why this is cheap enough to pre-check on every commit and push.

## Dependencies

- `_submodule.md`, `_default-branch.md`, `_ci.md` — per-domain workflows, Called only for a detected domain (so unneeded repair content stays out of context).

## Variables

- `{verb}` — `ci` runs the CI domain on demand (optionally `audit` | `harden` | `reconcile`); empty runs the pre-flight detector across the always-on domains.

## Rules

- **Detect cheap, repair lazy.** `detect.sh` is local and fast; heavy per-domain content reads in only when its domain is flagged.
- **Severity gates the workflow.** `BLOCKING` (submodule drift — committing through it escalates Tier 1 into Tier 2 history pollution) halts until resolved or deliberately deferred. `ADVISORY` (default-branch, CI) is surfaced, never blocks.
- **Conform, don't circumvent.** Repairs restore canonical git structure; never a workaround. Per-domain risk-tiering and scoping live in the components.

## Process

1. {verb}: first token of $ARGUMENTS
2. If {verb} is `ci`: Call: `_ci.md` ({ci-args}: remainder of $ARGUMENTS); Exit process — on-demand CI domain
3. {detect}: bash: `sh ${CLAUDE_SKILL_DIR}/scripts/detect.sh` — capture stdout + exit code + stderr
4. If `STATUS: not-a-repo`: Exit process — not a git repository
5. If `STATUS: healthy`: Exit process — emit ### healthy
6. For each problem line in {detect} stdout (`<domain> <severity> <detail>`), dispatch by domain:
    - `submodule` → Call: `_submodule.md` (the {detect} stderr state table is its diagnosis input)
    - `default-branch` → Call: `_default-branch.md`
    - `ci` → Call: `_ci.md` ({ci-args}: `audit`)
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

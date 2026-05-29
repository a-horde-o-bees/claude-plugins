---
name: git-doctor
description: Use when a repository's submodule structure is broken or suspect — `git-roots.sh` exited non-zero, "fix submodules", "repo health", "git submodule status shows nothing", submodule files staged as plain blobs, or a commit pre-check reported drift. Diagnoses each declared submodule's conformance, classifies problems by repair risk (reversible index fix vs. destructive history rewrite), proposes scoped repairs, and applies them only on approval. Conforms the repo to canonical git rather than working around it. Never rewrites history or force-pushes automatically.
allowed-tools:
  - Bash(git *)
  - Bash(sh *)
  - AskUserQuestion
---

# /git-doctor

Diagnose and repair git submodule conformance so canonical git (`submodule status --recursive`, `foreach`, `--show-superproject-working-tree`) works. Detects drift, classifies by risk tier, proposes scoped fixes, applies only on approval.

## Rules

- **Conform, don't circumvent** — repairs restore proper submodule structure (gitlinks) so standard git commands operate; never substitute a filesystem-scan workaround for git's own machinery.
- **Scope every repair to the one broken path** — `git rm --cached`/`git add` target a single submodule border; never project-wide, never `git add -A`.
- **Tier the risk, never auto-refactor:**
  - *Tier 1 — index-only* (gitlink missing, interior files staged as blobs, **0 commits in history**): reversible. Propose with file count + exact commands; apply on approval.
  - *Tier 2 — history-polluted* (interior files committed to superproject history): destructive to fix (history rewrite → SHA churn, force-push, broken clones). **Never automatic.** Surface with a heavy warning as a separate, deliberate decision.
- **Postpone → stop.** If the caller declines a repair, halt — do not proceed to commit. Committing while a submodule is staged-as-blobs is exactly what escalates Tier 1 into Tier 2.
- Never force-push or rewrite history without explicit per-item approval.
- Submodule **name ≠ path** is legal — resolve checkouts by the `.path` field of `.gitmodules`, never the section name.

## Process

1. {gate}: bash: `sh ${CLAUDE_SKILL_DIR}/scripts/git-roots.sh roots` (capture stderr + exit code)
2. If {gate} exit 0: Exit to user — repo conforming, emit ### healthy with the printed roots
3. If {gate} exit 2: Exit to user — not a git repository
4. Bind from the {gate} stderr table — it already enumerates every detected submodule (declared OR found on disk) with its state and scope counts:
    - {superproject}: the `superproject:` line
    - For each non-conforming row: {path}, {detect-state} (`broken-link` | `undeclared` | `uninitialized` | `anomaly`), {staged}, {history}
5. Assign a repair tier per {path} from {detect-state} + {history} (conformance needs BOTH a gitlink AND a `.gitmodules` declaration — `gitsubmodules(7)`):
    - `broken-link`, {history} = 0 → **Tier 1 (index-only)** — reversible
    - `broken-link`, {history} > 0 → **Tier 2 (history-polluted)** — destructive fix
    - `orphan-gitlink` → **declare-or-drop** — gitlink in index, no declaration (invisible to `git submodule`); either add a `.gitmodules` entry to conform, or `git rm --cached` to drop the gitlink
    - `not-checked-out` / `declared-only` → **init** (`git submodule update --init -- {path}`)
    - `undeclared` → **ambiguous** — an on-disk repo not in `.gitmodules` and not parent-gitignored; intent unknown (forgotten submodule vs. deliberately vendored code)
    - `nested-independent` → **benign, skip** — on-disk repo that the parent gitignores (agent-os umbrella pattern); intentionally not a submodule, no action
    - `anomaly` → **surface** — doesn't fit a known pattern; report, don't act
6. Emit ### diagnosis (per-path state + tier + scope counts)
7. For each **Tier 1** {path}: AskUserQuestion — approve the scoped repair? On approval:
    1. bash: `git -C {superproject} rm -r --cached --quiet -- {path}`
    2. bash: `git -C {superproject} add -- {path}` (the "adding embedded git repository" warning is expected — not a failure)
8. If any Tier 1 repaired: bash: `git -C {superproject} commit -m "Repair submodule gitlinks: <paths>"`
9. For each **undeclared** {path}: AskUserQuestion — declare + link it as a submodule, leave it as vendored content, or stop for manual handling? Act only on the chosen option; never guess intent.
10. For each **Tier 2** {path}: present the history-rewrite warning; do NOT act — require a separate explicit instruction
11. {verify}: bash: `sh ${CLAUDE_SKILL_DIR}/scripts/git-roots.sh roots` (capture exit)
12. Emit ### result

## Report

### healthy

```
Repo: {superproject}
Submodules: all conforming
Roots:
{roots}
```

### diagnosis

```
Repo: {superproject}
Submodule conformance (every detected boundary, declared or on-disk):
{per-path: <path> — <state> (staged: {staged}, history: {history})}
Tier 1 (reversible index repair): {tier1-list}
Tier 2 (history rewrite — needs deliberate decision): {tier2-list}
Undeclared (on-disk repo not in .gitmodules — intent decision): {undeclared-list}
Uninitialized: {uninit-list}
```

### result

```
Repo: {superproject}
Repaired (Tier 1): {repaired-list}
Deferred (Tier 2 / postponed): {deferred-list}
Verify: {gate exit 0 = conforming, roots listed | still drifting — see diagnosis}
Next: {if deferred — what the caller must decide; if clean — proceed to commit}
```

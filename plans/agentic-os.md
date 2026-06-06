# Agentic OS — live skill source-of-truth + home-as-repo backup

Invert skill authoring so the working copy lives where Claude Code reads it (instant, no checkpoint cycle), keep `claude-plugins` as a generated distribution mirror, and back the whole machine structure with a bare home repo.

## Context

Today `claude-plugins` is the source of truth for every skill. Making an edit globally available means the full cycle: edit → commit (auto-bump) → push → CI → `/checkpoint` on main → `claude plugins update` → restart. Skills are also *trapped* in the plugin repo — elevating a project-level skill to global is awkward, and nothing edited there is live until it has shipped.

The goal is an "agentic operating system": a version-controlled home where Claude Code is the kernel, `~/.claude/` is system config, skills are installed programs read live, `claude-plugins` is the package *publisher*, and the home repo is the reproducible OS image.

Decisions already made (see `logs/research/agentic-os/` for the four research reports backing them):

- **Skill mechanism = generated mirror (Option B), not symlink (Option A).** Claude Code's skill *discovery* scan does not reliably follow symlinks (issue #14836, last seen open at 2.0.73; status on 2.1.159 unverified). Real files in `~/.claude/skills/` discover and auto-trigger correctly and refresh live mid-session. So skills are authored as **real files**; a one-way publish copies them into `claude-plugins`. (If #14836 is later confirmed fixed, Option A's symlink shortcut becomes available as a simplification — out of scope here.)
- **Home backup = bare repo + allowlist `.gitignore` + manifest of project remotes.** Not submodules — the goal is "re-clone latest," not pinned cross-repo coordination, so submodules' per-commit pointer churn and detached-HEAD footguns aren't worth it.
- **Secrets = four fail-closed layers** (allowlist gitignore → gitleaks pre-commit → chezmoi+age for the rare tracked secret → private remote with push protection). A host-privileged, live-editable home is the OWASP-2026 failure mode; this is the load-bearing risk control.

## Target architecture

```
SOURCE OF TRUTH                         DISTRIBUTION                 CONSUMERS
~/.claude/skills/<name>/      --publish-->  claude-plugins/          other machines
  (real files, live here)      one-way      plugins/<plugin>/        + people
<project>/.claude/skills/<n>/             skills/<name>/             (via marketplace
  (project-local source)                    (generated mirror,        pull from GitHub)
                                            committed, never
                                            hand-edited)

BACKUP / OS IMAGE
~ (bare repo)  tracks: ~/.claude/ (incl. skills source) + dotfiles
               + projects.manifest + restore.sh ;  projects/* untracked
```

Key split: **this machine consumes the live source** in `~/.claude/skills/`; **other machines consume the published marketplace.** They are never both active for the same skill on one machine — see Phase 1 step 5 (decommission redundant local plugin installs) to avoid user-scope vs plugin-scope collisions.

---

## Phase 1 — Skill source-of-truth inversion

The core ask. Establishes the live-authoring path and the publish mirror.

### 1.1 Build the source→plugin map

Create `/home/dev/projects/claude-plugins/.claude/skill-sources.json` (committed; the inverse of the per-user `installed-skills.json`). One entry per published skill:

```json
{
  "skills": [
    { "name": "git-commit",    "plugin": "git" },
    { "name": "concise-prose", "plugin": "writing" }
  ]
}
```

Source path is derived: `~/.claude/skills/<name>/` by default; add `"source": "<abs-path>"` only for a project-local skill that is also published. Enumerate all ~43 currently-bundled skills (writing, communication, design, testing, git, skill-authoring, transcripts, pdf-plus, memory).

### 1.2 Migrate skill bytes to the live source

For each mapped skill, move the real folder out of the plugin tree into the user-global source:

```
for entry in skill-sources.json.skills:
    git mv  plugins/<entry.plugin>/skills/<entry.name>/  →  ~/.claude/skills/<entry.name>/
```

`~/.claude/skills/` is currently empty, so there are no collisions on arrival. After migration the plugin tree's `skills/<name>/` folders are repopulated by the publish step (1.3) as generated copies — so the repo still ships real files. Keep `.claude/skills/checkpoint/` (a claude-plugins-local wrapper) where it is; it is not a published skill.

### 1.3 Write the publish script

`/home/dev/projects/claude-plugins/scripts/publish-skills.py` (alongside `validate-manifests.py`). One-way mirror, idempotent:

```
publish(check=False):
    map = read(.claude/skill-sources.json)
    for entry in map.skills:
        src = entry.source or ~/.claude/skills/<entry.name>
        dst = plugins/<entry.plugin>/skills/<entry.name>
        if not exists(src):
            if check: continue            # source absent (CI / other contributor) → skip, don't fail
            else: error "source missing: <src>"
        if check:
            if dirs_differ(src, dst): record drift(entry)
        else:
            mirror src → dst              # rsync --delete semantics: dst becomes exact copy of src
    if check and any(drift): exit nonzero, list drifted skills
```

`--check` is a read-only drift detector; bare invocation regenerates the mirror.

### 1.4 Rewire `/checkpoint`

In `.claude/skills/checkpoint/SKILL.md`, add a publish step **before** `/git-commit` so the regenerated mirror lands in the same commit and the existing `.githooks/pre-commit` auto-bumps the affected plugins (a changed skill → changed `plugins/<plugin>/...` → patch bump → distribution signal — this composes for free):

```
Workflow (revised):
  0. Publish — bash: `uv run python scripts/publish-skills.py`   # regenerate mirror from live source
  1. {branch} = git branch --show-current
  2. Commit — /git-commit            # picks up regenerated mirror; pre-commit bumps touched plugins
  3..5. push + CI gate (unchanged)
  6. If main: marketplace refresh stays as the *publish-to-others* step (serves the GitHub marketplace).
     Local availability is already satisfied by the live source — no `claude plugins update` needed on THIS machine.
```

Set `.claude/skills/checkpoint/settings.json` accordingly (the `installed`/`marketplace` distinction now only describes how *other* machines consume; document that local consumption is the live source). The `installed-skills.json` + `scripts/sync_skills.py` path is superseded for this machine — retire or repurpose after migration.

### 1.5 Decommission redundant local plugin installs

To avoid a skill resolving twice (user-scope live source **and** plugin-scope marketplace cache), uninstall each `@a-horde-o-bees` plugin on this machine once all its skills are migrated to live source:

```
for plugin whose skills are fully migrated:
    claude plugins uninstall <plugin>@a-horde-o-bees
```

Other machines/people keep installing from the marketplace as before.

### 1.6 Local drift guard

Add a `claude-plugins` pre-commit check (extend `.githooks/pre-commit` or a sibling hook): run `publish-skills.py --check`; if the committed mirror differs from live source, fail with the drifted skill list. Runs only where source exists (skipped in CI / for contributors who edit the mirror as their own de-facto source). This enforces "never hand-edit the mirror" for the single-user setup.

### Phase 1 verification

1. Edit `~/.claude/skills/concise-prose/SKILL.md` body; in the **same session**, re-invoke the skill → confirm the edit is live (no restart).
2. `uv run python scripts/publish-skills.py` → confirm `plugins/writing/skills/concise-prose/` now matches source.
3. `publish-skills.py --check` → exits 0; hand-edit a mirror file → `--check` exits nonzero naming it.
4. `/checkpoint` on a branch → publish runs, commit captures mirror, pre-commit bumps `writing`, push + CI pass.
5. Confirm no double-trigger: with the live source present and the `writing` plugin uninstalled locally, the skill registry lists `concise-prose` exactly once.

---

## Phase 2 — Home-as-repo backup

Independent of Phase 1; can land before, after, or in parallel. Does **not** affect skill availability (Claude Code reads files on disk regardless of how they're tracked).

### 2.1 Bare repo + allowlist gitignore

```
git init --bare ~/.local/share/home.git
alias home='git --git-dir=$HOME/.local/share/home.git --work-tree=$HOME'
home config status.showUntrackedFiles no       # noisy $HOME → allowlist by `home add`, never blocklist
```

Write an **allowlist** `~/.gitignore` (`*` then `!`-reinclude tracked paths). Track: `~/.claude/` (config, skills source, CLAUDE.md, keybindings, settings.json — minus secrets), selected dotfiles, `projects.manifest`, `restore.sh`. Leave `projects/*` and all system/cache dirs untracked.

### 2.2 Secrets layers (before the first `home add`)

- Allowlist gitignore is layer 1 (fails closed — `.ssh/`, `.aws/`, tokens never included unless explicitly re-included).
- `home`-scoped **gitleaks** pre-commit hook (layer 2).
- **chezmoi + age** for any secret genuinely worth backing up — only ciphertext is committed, age key kept outside the repo (layer 3).
- **Private remote with push protection + secret scanning** (layer 4, the un-bypassable backstop).
- WSL note: rely on encryption + Windows Credential Manager (GCM), not Linux file perms — `~` is readable from the host via `\\wsl$`. Pin `core.autocrlf false`; mark encrypted blobs `binary` in `.gitattributes`.

### 2.3 Fold in the existing `~/.claude` repo

`~/.claude` is currently its own repo (`claude-user-config`). The new home repo supersedes it: either absorb its history (subtree/import) or start the home repo fresh and archive the old remote. Decide retention before removing `~/.claude/.git`.

### 2.4 Project manifest + restore

`projects.manifest` — generated sweep, committed to the home repo:

```
for d in ~/projects/*/.git:
    emit  "<basename>  <git remote get-url origin>  <current-branch>"   # skip dirs with no remote
```

`restore.sh` — reads the manifest and `git clone`s each project into `~/projects/`. New-machine bootstrap: clone home repo → `restore.sh` → projects re-cloned → live source (`~/.claude/skills/`) present → optionally run `publish-skills.py` against a freshly cloned `claude-plugins`.

---

## Phase 3 — Hardening (future, optional)

- **Sandboxing**: scope what the live-editable, host-privileged agent can reach (the concept report's #1 flagged risk). Permissions in `settings.json`, restricted tokens.
- **Hermeticity**: the home repo pins file contents, not the Claude Code version, MCP binaries, or model — it's dotfiles-in-git, not NixOS. Record versions in the manifest if true reproducibility is wanted later.
- **Drift guard in CI**: only viable if source is reachable in CI; out of scope while source is single-machine.

---

## Known costs / trade-offs (accepted)

- **Two commits per skill change.** The source edit commits to the home repo (backup); publish + mirror commit to `claude-plugins` (distribution). Option A would have been one commit; B trades that for robustness against #14836 and real-bytes backup. `/checkpoint` orchestrates the distribution side; the home-repo backup is a separate cadence.
- **Committed generated artifacts.** The mirror in `claude-plugins` is build output that must be committed (the marketplace serves files from GitHub). The drift guard (1.6) keeps it honest.
- **Migration is one-directional and bulk.** Once skills move to live source, `claude-plugins` skill folders are generated; editing them directly is a mistake the guard catches.

## Critical files

| Purpose | Path |
|---|---|
| Source→plugin map (new) | `claude-plugins/.claude/skill-sources.json` |
| Publish script (new) | `claude-plugins/scripts/publish-skills.py` |
| Checkpoint rewire | `claude-plugins/.claude/skills/checkpoint/SKILL.md`, `settings.json` |
| Auto-bump + drift guard | `claude-plugins/.githooks/pre-commit` |
| Live skill source (new home) | `~/.claude/skills/<name>/` |
| Generated mirror (existing) | `claude-plugins/plugins/<plugin>/skills/<name>/` |
| Home repo bootstrap (new) | `~/.gitignore`, `~/projects.manifest`, `~/restore.sh` |
| Research backing | `claude-plugins/logs/research/agentic-os/*.md` |

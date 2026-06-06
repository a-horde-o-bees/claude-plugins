# Home-directory version control: tooling and patterns

Survey of established approaches for putting `~` under git — bare-repo, dedicated managers, allowlist vs blocklist, nested repos, and machine restore — with a recommendation for a structure+config backup repo.

## 1. The bare-repo dotfiles pattern

**Mechanic.** `git init --bare $HOME/.dotfiles` creates a repo whose git internals live in `~/.dotfiles` but whose *work tree* is `$HOME` itself. You drive it with an alias that points git at that split:

```sh
git init --bare $HOME/.dotfiles
alias dot='git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
dot config status.showUntrackedFiles no   # the key trick
```

Files stay exactly where the tools that consume them expect (`~/.bashrc`, `~/.config/...`). There is no `.git` directory in `$HOME`, so the repo does not collide with project repos beneath it ([Atlassian — How to Store Dotfiles](https://www.atlassian.com/git/tutorials/dotfiles)).

**How it handles "track a few files in a noisy $HOME" without a giant gitignore.** The bare repo tracks *nothing by default* — there is no automatic staging of `$HOME`. You explicitly `dot add ~/.bashrc`, and that is the entire tracked set. The noise is handled not by ignore rules but by `status.showUntrackedFiles no`, which silences the thousands of untracked files so `dot status` only reports changes to files you have already added. This is an **allowlist by addition**: a file is tracked only once named, so no blocklist is needed ([sglavoie — bare repo dotfiles](https://www.sglavoie.com/posts/2021/05/30/managing-dotfiles-with-git-bare-repository/)).

**Pros.** No extra tooling, no symlinks, no file movement; branches per machine; trivial to replicate on a new box ([ennanco gist](https://gist.github.com/ennanco/d1c6a228f5aac23a3af6592135f0f8ae)). It is plain git — every git feature works unchanged.

**Cons.** Every command needs the `--git-dir/--work-tree` prefix (mitigated by the alias, but the alias must exist before you can even check out on a fresh machine). With `showUntrackedFiles no` you lose the safety net that would warn you about a *new* config file you forgot to add. Subtle gotcha: before a subdirectory has its own `.git`, the bare repo can "see into" it as part of the work tree; once a project is `git init`/`clone`d it becomes its own repo and the bare repo ignores its internals ([Stegosaurus Dormant](https://stegosaurusdormant.com/bare-git-repo/)).

## 2. Dedicated managers

| Tool | Model | Secrets | Multi-machine / OS | Learning curve |
|---|---|---|---|---|
| **chezmoi** | Source dir + state engine; `apply` writes real files (no symlinks) | Native age/gpg whole-file encryption + password-manager integration (1Password, Bitwarden, pass, Keychain, Vault, …) — public repo safe | Go templates keyed on `.chezmoi.hostname/os/arch`; first-class Windows | Moderate — concepts (source state, templates) but excellent docs |
| **yadm** | Thin git wrapper; files in place, no symlinks (bare-repo-like) | transcrypt / git-crypt if installed; `##os.Linux` alternate files | Alternate files + Jinja templates; `##os.*` syntax | Low if you know git; OS-alternate syntax is a known pain point |
| **GNU Stow** | Symlink farm — `~/dotfiles/<pkg>/` mirrors `$HOME` layout, `stow` symlinks it in | None (use git-crypt on the repo yourself) | Per-package selective stowing; no templating | Low concept, but directory layout must mirror `$HOME` exactly |
| **rcm** (thoughtbot) | Symlink farm via `rcup`/`rcdn`/`mkrc`/`lsrc`; repo root == `$HOME` | None built in | Host-specific + tag dirs (`host-*`, tagged files) | Low; older, less active than chezmoi/yadm |
| **Nix home-manager** | Declarative — `home.nix` *generates* config + installs packages; symlinks into `~/.config` | sops-nix / agenix: encrypted in repo, decrypted at activation | Fully reproducible across machines via flakes; per-host modules | Steep — whole Nix language + ecosystem |

**Model axis.** Three families: **symlink farm** (Stow, rcm — repo holds real files, `$HOME` holds links), **files-in-place / bare-repo-style** (yadm, and the manual bare repo), and **declarative state** (chezmoi renders from a source-of-truth; home-manager *builds* the environment, packages included) ([chezmoi comparison table](https://www.chezmoi.io/comparison-table/); [System Crafters — GNU Stow](https://systemcrafters.net/managing-your-dotfiles/using-gnu-stow/); [rcm guide](https://distro.tube/guest-articles/managing-dotfiles-with-rcm.html)).

**Secrets.** chezmoi is strongest out of the box: age/gpg encryption plus pulling live secrets from a password manager, so the repo holds only ciphertext or references and can be public ([chezmoi encryption](https://www.chezmoi.io/user-guide/encryption/); [Kasberg — chezmoi secrets](https://www.mikekasberg.com/blog/2026/01/31/dotfiles-secrets-in-chezmoi.html)). yadm leans on transcrypt/git-crypt ([yadm encryption](https://yadm.io/docs/encryption)). Nix uses sops-nix/agenix — encrypted in git, decrypted atomically at activation ([sops-nix](https://github.com/Mic92/sops-nix)). Stow and rcm have no secrets story; you bolt git-crypt onto the repo.

**Reproducibility ceiling.** home-manager is the only one that reproduces *the whole environment* — installed packages, services, and config — deterministically; the rest reproduce *config files* and leave package installation to you ([NixOS Discourse — 2025 dotfiles](https://discourse.nixos.org/t/my-2025-dotfiles-home-manager-nix-darwin-nixos-terraform-kubernetes-on-vms/73690)). That power costs the steepest learning curve in the table.

## 3. Allowlist vs blocklist for a whole-$HOME repo

Two philosophies when `$HOME` itself is the work tree:

- **Blocklist (track-all, ignore-noise):** `git init` in `$HOME`, then a `.gitignore` that excludes caches, downloads, `projects/`, etc. *Practitioners avoid this for $HOME.* `$HOME` generates new noise directories constantly (`.cache`, `.local/state`, app dirs, `.vscode-server`), so the blocklist is never finished and a single missed entry stages a 5 GB cache. `git status` is permanently dirty.
- **Allowlist (track only named paths):** the default behavior of the bare-repo pattern (add-only) and of every dedicated manager (only files in the source dir exist). The whitelist-style `.gitignore` — `/*`, then `!/.config`, `/.config/*`, `!/.config/whitelisted`, … — is *possible* but fiddly because **git cannot re-include a file under an excluded directory**, forcing the un-ignore/re-ignore dance at every level ([How-To Geek — .gitignore as whitelist](https://www.howtogeek.com/devops/how-to-set-up-gitignore-as-a-whitelist/); [git-scm gitignore docs](https://git-scm.com/docs/gitignore)).

**What people actually do:** allowlist, almost universally. With the bare repo they get it for free via `add`-only + `showUntrackedFiles no`; with managers they get it because only files placed in the source dir are managed. The verbose whitelist `.gitignore` is a last resort for people insisting on a real `.git` in `$HOME`. **Verdict for a whole-$HOME repo: track specific paths (allowlist), do not track-all-and-blocklist.**

## 4. Nested repos (the `projects/*` case)

`$HOME` containing other git repos is the central friction point. Three handlings:

1. **Just ignore them (recommended here).** With the bare repo, an inner `.git` makes git treat that subtree as a foreign repo and stop descending — its files never appear as untracked in the outer repo. With a real `$HOME/.git`, add `projects/` (or each repo) to `.gitignore`. The inner repos remain fully independent; the outer repo simply does not see them. Pitfall: an inner directory that does *not yet* have `.git` is briefly visible to the outer bare repo as untracked content ([Stegosaurus Dormant](https://stegosaurusdormant.com/bare-git-repo/); [dotfiles.github.io tips](https://dotfiles.github.io/tips/)).
2. **Submodules.** The outer repo records each inner repo as a pinned commit + remote URL, not its files; histories stay separate and `git submodule update --init` re-clones them on restore ([Build with Matija — submodules](https://www.buildwithmatija.com/blog/git-submodules-nested-repositories-guide)). This is the only option that *captures which projects exist and at what commit*, but it adds submodule ceremony, detached-HEAD friction, and noise from untracked inner commits.
3. **gitignore + symlink.** Clone the inner repo elsewhere, ignore it, symlink it in — avoids submodule noise but doesn't record the project set anywhere ([razzi — gitignore and symlinks](https://razzi.abuissa.net/2023/10/11/gitignore-and-symlinks/)).

**Key pitfall across all of these:** nesting a real, non-bare `.git` *above* live project repos invites accidental staging of a whole project into the parent if an ignore line is missing, and `git status` from `$HOME` becoming meaningless. The bare repo sidesteps this by never auto-staging.

## 5. Machine reproducibility / restore workflow

**Bare repo restore:**

```sh
git clone --bare <remote> $HOME/.dotfiles
alias dot='git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
dot checkout            # back up & move any conflicting pre-existing files, then retry
dot config status.showUntrackedFiles no
```

The checkout writes every tracked dotfile into the fresh `$HOME` ([Atlassian](https://www.atlassian.com/git/tutorials/dotfiles)). **chezmoi** collapses this to one line: `chezmoi init --apply https://github.com/<user>/dotfiles.git` ([chezmoi quick start](https://www.chezmoi.io/quick-start/)). **home-manager** rebuilds config *and packages* from the flake.

**What is recoverable vs not:**

| Recoverable from the home repo | NOT recoverable — needs a separate step |
|---|---|
| Dotfiles, `~/.claude/` config + skills | The project repos' contents (gitignored — clone each from its own remote) |
| Directory skeleton / folder structure | Installed system packages (unless home-manager) |
| A *manifest* of project remotes (if you commit one) | Live secrets (re-fetch from password manager / decrypt) |

The crucial design point: **the project repos themselves are not backed up by this repo — only the knowledge of which they are.** Capture that as either submodules (pinned, auto-re-clonable) or, lighter, a committed **manifest** (`projects.txt` of `name → remote URL`) plus a re-clone script. Restore then = checkout home repo → run the re-clone script → `chezmoi apply`/secrets decrypt. Files inside `projects/*` are recovered by *cloning from their remotes*, never from the home repo.

## 6. Recommendation for this user

Goal: `~` as a structure + config backup, `projects/*` gitignored, `~/.claude/` skills tracked, recreatable on a new machine, superseding the existing `~/.claude` git repo.

**Use the bare-repo pattern as the spine, allowlist (add-only).** It is the lowest-friction fit:

- It puts `$HOME` under version control with **no symlinks and no file movement** — `~/.claude/` and dotfiles are tracked in place, and the existing `~/.claude` repo is cleanly absorbed (delete its `.git`, `dot add ~/.claude`).
- `status.showUntrackedFiles no` solves the noisy-$HOME problem without a sprawling blocklist — pure allowlist by `add`.
- Nested `projects/*` repos are **ignored automatically** because each has its own `.git`; add `projects/` to the bare repo's ignore as a belt-and-suspenders measure so a not-yet-`init`ed project can't leak in.
- **Track a project manifest, not the projects.** Commit `~/projects/manifest.txt` (or a small script) listing each project's remote so a new machine re-clones them. Submodules are overkill and add detached-HEAD friction for repos you actively develop in.
- **Secrets:** keep them out of the repo. If any tracked config carries tokens, layer `git-crypt` on the bare repo, or graduate to **chezmoi** — which gives native age encryption + password-manager pulls, `--apply` one-line restore, and host/OS templating — if you later want WSL-vs-other-machine variation or public-repo safety.

Skip Stow/rcm (symlink farms force a mirrored layout and don't fit "track files where they are"). Skip home-manager unless you want full declarative package reproducibility and are willing to absorb Nix — it is the most powerful and the most expensive to learn, and it is a different project from "git-back my existing `$HOME`."

**One-line summary:** bare repo + add-only allowlist + `showUntrackedFiles no` + a project-remotes manifest; reach for chezmoi only when secrets or multi-machine templating enter the picture.

## Sources

- [Atlassian — How to Store Dotfiles: A Bare Git Repository](https://www.atlassian.com/git/tutorials/dotfiles)
- [sglavoie — Managing dotfiles with a Git bare repository](https://www.sglavoie.com/posts/2021/05/30/managing-dotfiles-with-git-bare-repository/)
- [Stegosaurus Dormant — Using a bare Git repo for dotfiles](https://stegosaurusdormant.com/bare-git-repo/)
- [ennanco — Managing dotfiles with style (gist)](https://gist.github.com/ennanco/d1c6a228f5aac23a3af6592135f0f8ae)
- [chezmoi — Comparison table](https://www.chezmoi.io/comparison-table/)
- [chezmoi — Encryption](https://www.chezmoi.io/user-guide/encryption/) · [Quick start](https://www.chezmoi.io/quick-start/)
- [Mike Kasberg — Dotfiles secrets in chezmoi](https://www.mikekasberg.com/blog/2026/01/31/dotfiles-secrets-in-chezmoi.html)
- [yadm — Encryption](https://yadm.io/docs/encryption)
- [System Crafters — GNU Stow](https://systemcrafters.net/managing-your-dotfiles/using-gnu-stow/)
- [distro.tube — Managing dotfiles with rcm](https://distro.tube/guest-articles/managing-dotfiles-with-rcm.html)
- [Mic92/sops-nix](https://github.com/Mic92/sops-nix) · [NixOS Discourse — 2025 dotfiles](https://discourse.nixos.org/t/my-2025-dotfiles-home-manager-nix-darwin-nixos-terraform-kubernetes-on-vms/73690)
- [How-To Geek — .gitignore as a whitelist](https://www.howtogeek.com/devops/how-to-set-up-gitignore-as-a-whitelist/) · [git-scm — gitignore](https://git-scm.com/docs/gitignore)
- [Build with Matija — Git submodules for nested repos](https://www.buildwithmatija.com/blog/git-submodules-nested-repositories-guide) · [razzi — gitignore and symlinks](https://razzi.abuissa.net/2023/10/11/gitignore-and-symlinks/) · [dotfiles.github.io — tips](https://dotfiles.github.io/tips/)

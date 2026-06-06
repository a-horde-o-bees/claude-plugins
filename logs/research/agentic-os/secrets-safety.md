# Keeping secrets out of a version-controlled `$HOME`

> Layered defense for a git-tracked home directory: allowlist `.gitignore` as the primary gate, a gitleaks pre-commit hook as the net, encrypted-in-repo storage for the few secrets worth tracking, and GitHub push protection plus rotation/history-scrub as the backstop.

The core risk: `~` holds `.ssh/`, `.aws/credentials`, `.config/**` tokens, `.netrc`, `.git-credentials`, shell history, `.env` files, `gh/hosts.yml`, and more. A single `git add --all` can publish all of it. The defenses below are ordered by where they sit in the commit pipeline — author time, commit time, repo, and remote — so a miss at one layer is caught at the next.

## 1. Prevention via `.gitignore` — allowlist, not blocklist

For a `$HOME` repo, **deny everything, then explicitly re-include**. The opposite (a blocklist enumerating known secret paths) is a losing game: new tools drop new secret files into `~` constantly (`~/.config/<newtool>/token`, `~/.local/share/...`), and a blocklist only protects against the leaks you already thought of. The allowlist fails *closed* — anything you forgot stays untracked.

### Canonical allowlist `.gitignore`

`.gitignore` is evaluated top-to-bottom, so the catch-all `*` must come first, then `!` exceptions re-include specific paths.

```gitignore
# Ignore everything by default
*

# ...but track the allowlist itself
!.gitignore

# Re-include specific dotfiles
!.bashrc
!.bash_profile
!.profile
!.zshrc
!.gitconfig
!.tmux.conf
!.vimrc

# Re-include a directory: you must un-ignore the DIRECTORY,
# then re-ignore its contents, then un-ignore what you want inside it.
!.config/
.config/*
!.config/nvim/
!.config/git/
```

Critical caveat ([coreyja](https://coreyja.com/posts/dotfiles-git-in-home-dir/)): git will not descend into an ignored directory, so to reach a nested file you must un-ignore **every directory level** on the path. The pattern is: `!dir/` (allow the dir) → `dir/*` (re-ignore its contents) → `!dir/keep/` (allow the subdir you want). Without the intermediate `dir/*`, the `!dir/` un-ignores the *entire* subtree, defeating the point.

### Why allowlist wins

- **Fails closed.** A forgotten `~/.aws/credentials` stays ignored because nothing un-ignored it. A blocklist that never added `.aws/` would happily commit it.
- **Stable against churn.** New secret-bearing files appear in `~` with every tool you install; the allowlist needs no maintenance to keep them out.
- **Auditable.** The complete set of tracked paths is the `!` lines — a short, reviewable list, versus an unbounded blocklist you can never prove complete.

The standard ergonomic wrapper is a **bare repo**: `git init --bare $HOME/.dotfiles.git` with alias `dotfiles='git --git-dir=$HOME/.dotfiles.git --work-tree=$HOME'`, plus `dotfiles config status.showUntrackedFiles no` so a bare `status` doesn't list all of `~`. The allowlist `.gitignore` still does the secret-blocking work.

`.gitignore` only blocks **untracked** files. A path already committed stays tracked even if a later rule would ignore it — so set the allowlist up *before* the first `git add`, and use `git rm --cached` to untrack anything that slipped in.

## 2. Pre-commit secret scanning — the net under the allowlist

The allowlist stops files; it does not stop a *secret pasted into a tracked file* (an API key hardcoded in `.bashrc`, a token in a config you do track). A content scanner at commit time catches that.

| Tool | Engine | Speed | FP rate (untuned) | Live verification | Best role |
|---|---|---|---|---|---|
| **gitleaks** | regex + entropy | <1s on diffs | ~5–15% | no | pre-commit hook (default choice) |
| **trufflehog** | detectors + live verify | slower, heavier | <2% on verified | yes (700+ types, read-only API calls) | CI / full-history sweeps |
| **detect-secrets** (Yelp) | plugins + entropy, baseline | fast | ~0–5% with baseline | no | onboarding a dirty repo via baseline allowlist |
| **git-secrets** (AWS) | AWS-focused regex | fast | low scope | no | AWS-only, mostly superseded |
| **GitGuardian** | ML-filtered, commercial | fast | 1–3% | partial | org-wide platform monitoring |

Sources: [devsecops.ae 2026 comparison](https://devsecops.ae/secrets-scanners-comparison-2026/), [Jit](https://www.jit.io/resources/appsec-tools/trufflehog-vs-gitleaks-a-detailed-comparison-of-secret-scanning-tools).

**Detection quality vs. false positives.** gitleaks is pure pattern/entropy — fastest, but base64 blobs, test fixtures, and example values trigger it; tune via `.gitleaks.toml` allowlists. trufflehog's edge is *verification*: it attempts a read-only auth call against the provider, so it reports only secrets that are actually **live**, collapsing the largest FP class (already-revoked credentials that still match a pattern). detect-secrets' niche is the **baseline** — snapshot existing findings as "known", then flag only new ones, ideal for retrofitting scanning onto a `~` that already has years of files.

### Wiring the hook (pre-commit framework)

The [pre-commit](https://pre-commit.com) framework is the cleanest way to manage the hook. `~/.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.x.x          # pin to a current release
    hooks:
      - id: gitleaks
```

Then `pre-commit install`. For a bare dotfiles repo, point the hook dir at it: `pre-commit install --hook-type pre-commit` against the bare git-dir, or install gitleaks' own hook directly:

```bash
gitleaks install   # or copy gitleaks' pre-commit script into .git/hooks
```

The hook runs `gitleaks protect --staged` on each commit and exits non-zero (blocking the commit) if a credential pattern matches the staged diff. Recommended layering: **gitleaks pre-commit** for instant local blocking, **trufflehog in CI** for verified, full-history depth ([devsecops.ae](https://devsecops.ae/secrets-scanners-comparison-2026/)).

A local pre-commit hook is advisory — `--no-verify` bypasses it, and it only protects machines where you installed it. Treat it as a net, not a wall; the remote-side controls in §4 are the enforced layer.

## 3. Encrypted secrets *in* the repo — when you do want to track one

Sometimes a secret belongs in the backup (a license key, a self-hosted service token you want restored on a new machine). Encrypt it so the ciphertext is safe to push.

| Tool | Granularity | Key model | Dotfile-manager fit |
|---|---|---|---|
| **git-crypt** | whole file, transparent on checkout | GPG (or symmetric key) | works, but GPG key sharing is clunky; whole-file only |
| **SOPS + age** | per-field (YAML/JSON/env) | age or GPG; Shamir multi-key | best for structured config; only encrypts the secret values, leaves the rest diffable |
| **chezmoi + age/gpg** | whole file (`chezmoi add --encrypt`) | age passphrase or key | native to a dotfile manager; encrypted blob in repo, decrypts on `apply` |
| **transcrypt** | whole file, transparent | symmetric (shared passphrase) | simple, but symmetric key distribution is the weak point |

Sources: [chezmoi encryption FAQ](https://www.chezmoi.io/user-guide/frequently-asked-questions/encryption/), [NixOS secrets overview](https://discourse.nixos.org/t/handling-secrets-in-nixos-an-overview-git-crypt-agenix-sops-nix-and-when-to-use-them/35462), [dotfiles.io secret management](https://dotfiles.io/en/guides/secret-management/).

**Trade-offs.**
- **git-crypt** is transparent — files decrypt automatically on checkout once your key is unlocked — but it's all-or-nothing per file and its GPG dependency makes onboarding a new machine heavy. A diff of an encrypted file is opaque binary.
- **SOPS + age** encrypts only the *values* of recognized fields, so the file structure stays readable and diffable, and supports per-secret keys / Shamir splitting so one compromised key doesn't expose everything. Best when secrets live in structured config. age is the modern, small, no-keyring alternative to GPG.
- **chezmoi** integrates encryption into the dotfile-management flow itself: `chezmoi add --encrypt <file>` stores ciphertext in the source repo; `chezmoi apply` decrypts to the target. The age **private key lives outside the repo** (e.g. `~/.config/chezmoi/key.txt`, itself git-ignored), and age's passphrase mode prompts only once at `chezmoi init`. For someone already adopting a dotfile manager, this is the lowest-friction option.

**Recommendation for dotfile managers:** if you're using **chezmoi**, use its built-in **age** integration — one tool, one workflow. If you're not on a manager and your secrets are structured config, **SOPS + age** gives the best granularity. Reserve git-crypt/transcrypt for simple whole-file cases where transparency matters more than key hygiene.

These tools encrypt content but the **filename and existence** are still visible in the repo — name files generically and never let the cleartext path leak the secret's nature.

## 4. GitHub push protection & secret scanning — the enforced backstop

Even with a private remote, turn this on; it's the only layer that can't be `--no-verify`'d away.

- **Push protection** scans each push *before it lands* and **rejects** the push if it detects a known secret pattern — blocking the leak at the server, independent of any local hook ([GitHub Docs](https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection)). Now available for **private repos** under GitHub Secret Protection (and free for public repos).
- **Secret scanning** continuously scans commit history and notifies (or auto-revokes, for partner patterns) on detected credentials.

Scale of the problem this guards against: GitGuardian's 2026 *State of Secrets Sprawl* reported **28.65 million** new secrets in public GitHub commits during 2025 ([Snyk summary](https://snyk.io/articles/state-of-secrets/)).

### When a secret leaks anyway

Order matters — **rotate first, scrub second** ([GitHub remediation guide](https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/remediating-a-leaked-secret)):

1. **Rotate / revoke at the provider immediately.** Assume the secret is compromised the instant it's pushed — bots scrape public commits within seconds. Removing it from history does *not* undo exposure; only revocation does.
2. **Scrub history (compliance/hygiene, secondary).** Use **`git filter-repo`** — the Git-project-recommended modern replacement for **BFG Repo-Cleaner** (BFG is no longer actively maintained):
   ```bash
   git filter-repo --invert-paths --path path/to/leaked.file
   # or replace a literal string across history:
   git filter-repo --replace-text <(echo 'SECRET==>***REMOVED***')
   ```
   Then force-push, and have all collaborators re-clone (rewritten history diverges from every existing clone). Caches/forks/PRs may retain the old blob — another reason rotation is the real fix.

## 5. WSL-specific notes

- **Don't store credentials in plaintext on the WSL side.** `gh` writes tokens to `~/.config/gh/hosts.yml` in plaintext unless a keyring is configured; `.git-credentials` (the `store` helper) is plaintext too. Both land in `~` — your backup target. Prefer **Git Credential Manager (GCM)** running on the Windows host, which stores tokens in the **Windows Credential Manager** (DPAPI-protected), keeping them *out* of the WSL filesystem entirely ([GCM WSL docs](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/wsl.md), [MS Learn](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-git)). Set `git config --global credential.helper "/mnt/c/.../git-credential-manager.exe"`.
- **`\\wsl$` / `\\wsl.localhost` exposure.** The WSL2 ext4 filesystem is reachable from Windows via the `\\wsl$\<distro>\...` share. Anything in `~` — including a clear-text key before you encrypt it, or a decrypted secret — is visible to any Windows process and to Windows-side malware. Linux file permissions (`chmod 600 ~/.ssh/id_ed25519`) are **not** enforced for access coming through the Windows side. Keep the real secret store on the Windows credential manager, and don't rely on `~` permissions as a security boundary against the host.
- **Line-ending gotchas.** Crossing the Windows/Linux boundary, autocrlf can rewrite line endings and make git report whole files as modified — and, more dangerously for crypt tools, **CRLF injection corrupts binary/encrypted blobs**. Commit a `.gitattributes` to pin behavior:
  ```gitattributes
  * text=auto eol=lf
  *.age binary
  *.gpg binary
  # mark any git-crypt/sops outputs binary so they're never EOL-converted
  ```
  Set `git config --global core.autocrlf false` on the WSL side ([scivision](https://www.scivision.dev/git-line-endings-windows-cygwin-wsl/), [jessehouwing](https://jessehouwing.net/tips-tricks-git-under-wsl-and-windows/)). Without `binary` on encrypted files, EOL normalization can silently break decryption.

## 6. Recommendation — concrete layered setup

For this user's git-tracked `~` on WSL, push to a **private** GitHub repo, with four independent layers:

1. **Allowlist `.gitignore` (primary gate).** Start the repo with `*` + explicit `!` re-includes, set up *before the first `git add`*. Use a bare repo + alias with `status.showUntrackedFiles no`. This is the layer that keeps `.ssh/`, `.aws/`, tokens, and shell history out by default — fails closed.
2. **gitleaks pre-commit hook (the net).** Via the pre-commit framework, blocking any commit whose staged diff contains a credential — catches secrets *pasted into* tracked files that the allowlist can't see. Optionally add a trufflehog CI sweep for verified full-history depth.
3. **chezmoi + age (encrypted store for the few secrets worth tracking).** For the handful of secrets you genuinely want backed up, `chezmoi add --encrypt` with an age key kept *outside* the repo (and git-ignored). Ciphertext is safe to push; mark `*.age binary` in `.gitattributes`.
4. **GitHub push protection + secret scanning (enforced backstop).** Enable on the private repo — the only layer immune to `--no-verify`. On any leak: **rotate at the provider first**, then `git filter-repo` to scrub history and force-push.

WSL hardening throughout: keep git/`gh` credentials in the **Windows Credential Manager via GCM** (never plaintext in `~`), pin `core.autocrlf false` + a `.gitattributes`, and treat `~` as readable by the Windows host — so the encrypted-store and credential-manager layers, not Linux file permissions, are what actually protect the secrets.

---

### Sources

- [Dotfiles — Put your home directory under git (coreyja)](https://coreyja.com/posts/dotfiles-git-in-home-dir/)
- [How to manage your dotfiles using Git (Patrick Gaskin)](https://pgaskin.net/posts/git-dotfiles/)
- [Secrets scanner comparison 2026 (devsecops.ae)](https://devsecops.ae/secrets-scanners-comparison-2026/)
- [TruffleHog vs Gitleaks (Jit)](https://www.jit.io/resources/appsec-tools/trufflehog-vs-gitleaks-a-detailed-comparison-of-secret-scanning-tools)
- [chezmoi encryption FAQ](https://www.chezmoi.io/user-guide/frequently-asked-questions/encryption/)
- [Handling secrets in NixOS — git-crypt, agenix, sops-nix (NixOS Discourse)](https://discourse.nixos.org/t/handling-secrets-in-nixos-an-overview-git-crypt-agenix-sops-nix-and-when-to-use-them/35462)
- [Secret management best practices (dotfiles.io)](https://dotfiles.io/en/guides/secret-management/)
- [Working with secret scanning and push protection (GitHub Docs)](https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection)
- [Remediating a leaked secret (GitHub Docs)](https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/remediating-a-leaked-secret)
- [State of Secrets — 28.65M leaked in 2025 (Snyk)](https://snyk.io/articles/state-of-secrets/)
- [Git Credential Manager on WSL (git-ecosystem)](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/wsl.md)
- [Get started using Git on WSL (Microsoft Learn)](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-git)
- [Git line endings on Windows with WSL (scivision)](https://www.scivision.dev/git-line-endings-windows-cygwin-wsl/)
- [Tips & tricks — Git under WSL and Windows (jessehouwing)](https://jessehouwing.net/tips-tricks-git-under-wsl-and-windows/)

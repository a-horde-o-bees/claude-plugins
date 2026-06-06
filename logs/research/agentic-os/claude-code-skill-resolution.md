# Claude Code skill & config resolution

How Claude Code discovers, orders, caches, and refreshes skills across user, project, and plugin scopes — with the live-edit freshness rules and the symlink caveat that decide whether live-file authoring works.

> Compiled 2026-06-01 from official docs (code.claude.com), two anthropics/claude-code GitHub issues, and local on-disk evidence on this machine. Every claim is sourced inline. Items that could not be verified are flagged **[UNVERIFIED]**.

---

## TL;DR for the live-file authoring architecture

- **Authoring live in `~/.claude/skills/` and `<project>/.claude/skills/` works** — Claude Code watches these directories and picks up adds/edits/removes mid-session, no restart. This is the supported "instant edit" path.
- **Body edits and frontmatter (`description`) edits are both live for *future* invocations** — the watcher re-registers the whole `SKILL.md`, frontmatter included. The one subtlety is *already-invoked* skills: once a skill's body is in the conversation, Claude does not re-read it that turn (see §2).
- **Symlinked skill folders are the sharp edge.** Execution follows the symlink, but *discovery/registration does not* (open bug, see §3). The empty `~/.claude/skills/` on this machine plus the checkpoint skill's `installed` mode (which symlinks via `npx skills`) both assume symlinks-followed — that assumption is **only partly true** and currently buggy for the listing/registry path.
- **Plugins/marketplace remain the distribution channel**; they are cached (copied) under `~/.claude/plugins/cache/` and gated by a version cache-key, so they require an explicit update + (effectively) a restart to propagate.

---

## 1. Skill discovery scopes and precedence

### The four scopes

Per [Extend Claude with skills — Where skills live](https://code.claude.com/docs/en/skills):

| Scope | Path | Applies to |
|---|---|---|
| Enterprise / managed | via [managed settings](https://code.claude.com/docs/en/settings#settings-files) | All users in the org |
| Personal (user) | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `<project>/.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where the plugin is enabled |

### Name-collision precedence

> "When skills share the same name across levels, enterprise overrides personal, and personal overrides project. Plugin skills use a `plugin-name:skill-name` namespace, so they cannot conflict with other levels." — [skills doc](https://code.claude.com/docs/en/skills)

So the loose-skill precedence chain is **enterprise > personal (`~/.claude`) > project (`.claude`)**. Plugin skills sit outside this chain entirely: they are always namespaced `/plugin-name:skill-name` (or `/marketplace`-qualified) and therefore never collide with a loose skill of the same bare name. A skill also beats a same-named legacy `.claude/commands/` file ("if a skill and a command share the same name, the skill takes precedence").

> **Note on the precedence direction:** personal overriding project is the opposite of what many tools do (project-local usually wins). For the live-authoring architecture this matters: a personal `~/.claude/skills/foo` will *shadow* a project `.claude/skills/foo` of the same name. Keep names distinct, or rely on plugin namespacing, to avoid a personal skill silently masking a project one.

### Project-scope discovery walks up and down the tree

> "Project skills load from `.claude/skills/` in your starting directory and in every parent directory up to the repository root… When you work with files in subdirectories below your starting directory, Claude Code also discovers skills from nested `.claude/skills/` directories on demand." — [skills doc](https://code.claude.com/docs/en/skills)

`--add-dir` / `/add-dir` is a documented exception: a `.claude/skills/` inside an added directory *is* loaded (the only `.claude/` config that is). The `permissions.additionalDirectories` setting in `settings.json` does **not** load skills — only the flag/command do.

### Loading model: descriptions always, body on demand

In a normal session the **descriptions** of all visible skills are loaded into context so Claude can route, but the **full body loads only when the skill is invoked** ([Control who invokes a skill](https://code.claude.com/docs/en/skills)). With `disable-model-invocation: true`, even the description is withheld until you invoke `/name`. The combined `description` + `when_to_use` is truncated at 1,536 chars per entry in the listing, and the whole listing is capped at ~1% of the context window (tunable via `skillListingBudgetFraction` / `SLASH_COMMAND_TOOL_CHAR_BUDGET`); descriptions for least-used skills are dropped first when it overflows.

---

## 2. Caching & freshness — the body-vs-frontmatter rule

This is the crux for live authoring. There are **two distinct mechanisms** and they interact:

### (a) Live change detection — registration is uncached for user & project scopes

> "Claude Code watches skill directories for file changes. Adding, editing, or removing a skill under `~/.claude/skills/`, the project `.claude/skills/`, or a `.claude/skills/` inside an `--add-dir` directory takes effect within the current session without restarting. Creating a top-level skills directory that did not exist when the session started requires restarting Claude Code so the new directory can be watched." — [Live change detection](https://code.claude.com/docs/en/skills)

> "Live change detection covers `SKILL.md` text **only**. For a skill folder that is also a [plugin](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins), changes to `hooks/`, `.mcp.json`, `agents/`, and `output-styles/` need `/reload-plugins` to take effect." — same section

So for a plain loose skill: **the entire `SKILL.md` — body and YAML frontmatter alike — is re-watched and re-registered live.** The doc draws no body-vs-frontmatter line for `SKILL.md` text itself; the only carve-out is *non-`SKILL.md` plugin sidecar files* (hooks, MCP, agents, output-styles), which need `/reload-plugins`.

Two restart-required edge cases:
- Creating a **top-level skills directory that did not exist at session start** — needs restart so the new dir gets watched. (Adding a *skill folder inside* an already-watched skills dir does not.)
- Plugin sidecar component changes — need `/reload-plugins`.

### (b) Skill content lifecycle — an *invoked* skill's body is frozen for that session

> "When you or Claude invoke a skill, the rendered `SKILL.md` content enters the conversation as a single message and stays there for the rest of the session. **Claude Code does not re-read the skill file on later turns**, so write guidance that should apply throughout a task as standing instructions rather than one-time steps." — [Skill content lifecycle](https://code.claude.com/docs/en/skills)

### The synthesized body-vs-frontmatter freshness rule

Combining (a) and (b):

| What you edit | When it takes effect |
|---|---|
| **Frontmatter `description`** (the trigger matcher) | Re-registered **live**, no restart. The next routing decision / `/`-menu render uses the new description. (It is read from the registry, not from an already-injected body.) |
| **Body** of a skill **not yet invoked** this session | Picked up **live** — the *next* invocation renders the current file. |
| **Body** of a skill **already invoked** this session | The already-injected copy is **frozen** for the rest of the turn/session; later turns do not re-read it. **Re-invoking the skill** renders the fresh file again (a fresh invocation = a fresh render). A hard restart also clears it. |

Net: **editing `SKILL.md` does not need a session restart to re-register** — neither for the body nor for the `description`. The only "staleness" is the in-context copy of a skill you *already ran* this session, and that is cleared by simply invoking it again. The trigger matcher (`description`) re-registers live because it lives in the registry, not in the conversation transcript.

**[UNVERIFIED]** The docs do not explicitly state "an edited `description` re-registers without restart" as a single sentence. It is inferred from (i) live change detection covering all `SKILL.md` text and (ii) descriptions being a registry/listing property rather than invoked-body content. No source contradicts it, but treat the description-live claim as inferred, not verbatim. Worth a one-line assertion test under `plugins/skill-authoring/skills/skill-architecture/assertions/` to pin it down.

---

## 3. Symlink handling — the sharp edge

**Short answer: execution follows symlinks; discovery/registration currently does not.** This is the single biggest risk for any architecture that symlinks skills into `~/.claude/skills/`.

### Discovery does NOT follow symlinks (open bug)

[Issue #14836 — "/skills command doesn't find skills in symlinked directories"](https://github.com/anthropics/claude-code/issues/14836) (Claude Code 2.0.73, **OPEN** as of the issue, no maintainer fix shown):

> The `/skills` command "fails to detect skills when the skill directory is a symlink… shows 'No skills found' even though symlinked skills are correctly loaded and usable by the model." The reporter's repro:
> ```
> find -L ~/.claude/skills -name "*.md"   # finds the symlinked SKILL.md (follows symlinks)
> find    ~/.claude/skills -name "*.md"   # finds nothing (default: doesn't follow)
> ```
> i.e. the scan uses the no-`-L` semantics.

### Validation/registration also stumbles, but execution resolves the link

[Issue #25367 — "Custom skills via symlinked ~/.claude/skills/ directory fail validation but execute correctly"](https://github.com/anthropics/claude-code/issues/25367) (**closed as duplicate**):

> Setup: `~/.claude/skills -> ~/dotfiles/.claude/skills`. Discovery/registration fails with `Error: Unknown skill: jira`, **but the skill executes correctly afterward** — "the symlink is resolved at execution time." Other symlinked configs (CLAUDE.md, settings.json) work fine; only skill discovery/registration trips. Suggested workaround: copy instead of symlink (`cp -r` rather than `ln -s`).

### What this means for the two install models

- **`npx skills` "installed" mode** (the `installed` sync mode in this repo's checkpoint skill) symlinks `~/.claude/skills/<name>/ → ~/.agents/skills/<name>/`. Vercel-labs has its own open bugs about *not even creating* the `~/.claude/skills` symlink in some configs ([vercel-labs/skills #744](https://github.com/vercel-labs/skills/issues/744), [#851](https://github.com/vercel-labs/skills/issues/851)). And even when the symlink exists, Claude Code's discovery may not list it (#14836). So the `installed` mode's premise — "new artifacts symlink into `~/.claude/skills/<name>/` and appear in the registry mid-session" (`/home/dev/projects/claude-plugins/.claude/skills/checkpoint/_sync_installed.md`) — is **optimistic**: execution will work, but model-driven *discovery* and the `/skills` menu may not show the symlinked skill until a fix lands or you replace the symlink with a real directory.
- **Direct authoring (no symlink)** — writing real directories straight into `~/.claude/skills/` or `<project>/.claude/skills/` — sidesteps every symlink bug. This is the robust live-file path. On this machine `~/.claude/skills/` is currently empty (`ls` shows no entries, no symlinks), so nothing is presently exposed to the symlink hazard.

### Symlinks *inside a plugin* (different, well-specified, and supported)

When a plugin is copied into the cache, symlinks inside the plugin dir are handled deterministically ([Plugins reference — Share files within a marketplace with symlinks](https://code.claude.com/docs/en/plugins-reference)):
- target **within the plugin's own dir** → preserved as a relative symlink in the cache;
- target **elsewhere in the same marketplace** → dereferenced (content copied in) — this is how a meta-plugin's `skills/` links to sibling plugins' skills;
- target **outside the marketplace** → skipped for security.
For `--plugin-dir`/local installs, only within-plugin symlinks are preserved.

> **Recommendation:** For the live-authoring tier, **author real directories, not symlinks**, in `~/.claude/skills/` and `<project>/.claude/skills/`. Reserve symlinks for the *within-marketplace* sharing case, which is explicitly supported.

---

## 4. Plugin vs loose-skill differences

From [Plugins — When to use plugins vs standalone configuration](https://code.claude.com/docs/en/plugins):

| | Loose skill (`~/.claude/skills`, `.claude/skills`) | Plugin (marketplace) |
|---|---|---|
| Skill name | `/foo` (bare) | `/plugin-name:foo` (namespaced) |
| Edit latency | **Instant**, live-watched, no restart (§2) | Cached copy; needs `update` + restart (§5) |
| Distribution | Manual (copy / commit `.claude/skills/` to the repo) | Marketplace install across machines/people |
| Versioning | None — the file *is* the version | Explicit `version` or git-SHA cache-key (§5) |
| Bundled extras | `SKILL.md` + supporting files only | Can bundle agents, hooks, MCP servers, LSP servers, monitors, `bin/`, default `settings.json` |
| Best for | Personal/project workflows, quick iteration | Sharing, versioned releases, reuse across projects |

> "Start with standalone configuration in `.claude/` for quick iteration, then convert to a plugin when you're ready to share." — plugins doc. This is exactly the proposed architecture: **author live, distribute via plugin/marketplace.**

### Skills-directory plugins — the hybrid middle

A loose skill folder can carry a `.claude-plugin/plugin.json`, which promotes it to a plugin `<name>@skills-dir` *discovered in place* (not copied to the cache) ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference)):

> "Any folder under a skills directory that contains a `.claude-plugin/plugin.json` manifest is loaded as a plugin named `<name>@skills-dir` **on the next session**, with no marketplace and no install step… discovered in place rather than copied into the plugin cache."

> "Changes you make to a skill's `SKILL.md` take effect immediately in the current session. Changes to the plugin's other components, such as `hooks/`, `.mcp.json`, `agents/`, and `output-styles/`, do not. Run `/reload-plugins` or restart Claude Code to pick those up."

So a skills-dir plugin gets **live `SKILL.md` editing** (like a loose skill) *plus* the ability to bundle agents/hooks/MCP (like a plugin), at the cost of a once-per-new-folder next-session load and `/reload-plugins` for sidecar changes. It does **not** give cross-machine distribution by itself — that still needs a marketplace. Scaffold with `claude plugin init <name>` (writes `~/.claude/skills/<name>/`); remove by deleting the folder or `claude plugin disable <name>@skills-dir` (no uninstall step).

---

## 5. The `claude plugins update` / marketplace cache refresh cycle

### Where the cache lives (confirmed on this machine)

- **Marketplace clones:** `~/.claude/plugins/marketplaces/<marketplace>/` — the git checkout of each marketplace. Tracked in `~/.claude/plugins/known_marketplaces.json` with `installLocation`, `lastUpdated`, and `autoUpdate`.
- **Plugin code cache:** `~/.claude/plugins/cache/<marketplace>/<plugin>/` — copies of installed plugin code.

> "For security and verification purposes, Claude Code copies *marketplace* plugins to the user's local **plugin cache** (`~/.claude/plugins/cache`) rather than using them in-place… Each installed version is a separate directory in the cache. When you update or uninstall a plugin, the previous version directory is marked as orphaned and removed automatically 7 days later." — [Plugins reference — Plugin caching](https://code.claude.com/docs/en/plugins-reference)

Local evidence matches exactly (`path`: on-disk listing):
```
~/.claude/plugins/marketplaces/{a-horde-o-bees, claude-plugins-official, ...}
~/.claude/plugins/cache/{a-horde-o-bees, claude-plugins-official}/<plugin>/
~/.claude/plugins/known_marketplaces.json   # a-horde-o-bees has "autoUpdate": true
~/.claude/plugins/data/{id}/                 # ${CLAUDE_PLUGIN_DATA}, survives updates
```

### What triggers a refresh — the version cache-key

> "Claude Code uses the plugin's version as the cache key that determines whether an update is available. When you run `/plugin update` or auto-update fires, Claude Code computes the current version and skips the update if it matches what's already installed." — [Version management](https://code.claude.com/docs/en/plugins-reference)

Version resolves from the first set of: (1) `version` in `plugin.json`; (2) `version` in the marketplace entry; (3) the **git commit SHA** (for github/url/git-subdir/relative sources in a git-hosted marketplace); (4) `unknown`.

> "If you set `version` in `plugin.json`, you must bump it every time you want users to receive changes. **Pushing new commits alone is not enough**, because Claude Code sees the same version string and keeps the cached copy. If you're iterating quickly, leave `version` unset so the git commit SHA is used instead." — Version management warning

This is precisely why this repo's workflow auto-bumps each affected plugin's patch version on merge: with an explicit `version`, the bump *is* the deployment signal. (CLAUDE.md and the checkpoint skill both encode this.) Two-step refresh:
1. `claude plugins marketplace update <marketplace>` — re-pulls the marketplace clone so the new version/SHA is visible.
2. `claude plugins update <plugin>@<marketplace>` — re-copies the plugin into the cache if the version differs (`-s/--scope` defaults to `user`).

### Restart requirement

A mid-session plugin update does **not** fully hot-swap:

> "When a plugin updates mid-session, hook commands, monitors, MCP servers, and LSP servers keep using the previous version's path. Run `/reload-plugins` to switch hooks, MCP servers, and LSP servers to the new path; **monitors require a session restart**." — [Plugins reference](https://code.claude.com/docs/en/plugins-reference)

And the checkpoint workflow's own guidance (`/home/dev/projects/claude-plugins/.claude/skills/checkpoint/_sync_marketplace.md`): *"Restart: recommended (`/exit` then `claude --continue`) — cached plugin install only re-reads at session start."* So the practical rule for the **marketplace** distribution tier: **bump version → `marketplace update` → `plugins update` → restart the session** to be sure everything (skills, hooks, MCP, monitors) is on the new copy. `/reload-plugins` covers most components but not monitors.

> Contrast with the live-authoring tier (§2), where loose-skill `SKILL.md` edits need *no* restart at all. The two tiers have deliberately opposite freshness models: **author uncached (instant), distribute cached (versioned + restart).**

---

## Implications for the live-file + marketplace architecture

1. **Author as real directories** under `~/.claude/skills/` (cross-project) and `<project>/.claude/skills/` (project-pinned). Edits to body and `description` are live; no build step, no restart (modulo re-invoking an already-run skill, and the one new-top-level-dir restart case).
2. **Avoid symlinking skills into the skills dirs.** Discovery/registration does not reliably follow symlinks (#14836 open; #25367 dup) even though execution does. If a tool like `npx skills` insists on symlinking, expect the skill to *run* but not always *list* — prefer copying, or adopt skills-dir plugins / real dirs.
3. **Mind the personal > project precedence:** a personal skill shadows a same-named project skill. Namespace via plugins or keep names distinct.
4. **Use the marketplace/plugin path purely as the distribution channel** to other machines/people. Pin explicit `version` and bump on every release (this repo already auto-bumps on merge), then `marketplace update` + `plugins update` + restart downstream.
5. **Skills-directory plugins** (`<name>@skills-dir`) are the bridge if a locally-authored skill needs to bundle hooks/agents/MCP while keeping live `SKILL.md` editing — but they still need a marketplace for cross-machine reach.

---

## Verification ledger

| Claim | Status | Source |
|---|---|---|
| Scope paths + precedence (ent > personal > project; plugins namespaced) | **Verified** | [skills doc](https://code.claude.com/docs/en/skills) |
| Loose `SKILL.md` body + frontmatter re-register live, no restart | **Verified** (body+text), see below for description nuance | [Live change detection](https://code.claude.com/docs/en/skills) |
| Editing `description` (trigger matcher) re-registers live without restart | **Inferred / [UNVERIFIED]** as a verbatim statement | derived from live-change-detection + listing model |
| Invoked skill body is frozen for the session; re-invoke to refresh | **Verified** | [Skill content lifecycle](https://code.claude.com/docs/en/skills) |
| New top-level skills dir / plugin sidecars need restart or `/reload-plugins` | **Verified** | [skills doc](https://code.claude.com/docs/en/skills) Note |
| Execution follows symlinks | **Verified** (issue-confirmed) | [#25367](https://github.com/anthropics/claude-code/issues/25367) |
| Discovery/registration does NOT follow symlinks (open bug) | **Verified open as of 2.0.73** | [#14836](https://github.com/anthropics/claude-code/issues/14836) |
| Plugin cache at `~/.claude/plugins/cache`; versioned dirs; 7-day orphan GC | **Verified** + on-disk confirmed | [Plugins reference](https://code.claude.com/docs/en/plugins-reference); `path`: local listing |
| Version cache-key (explicit vs git-SHA); bump-to-ship | **Verified** | [Version management](https://code.claude.com/docs/en/plugins-reference) |
| Mid-session update restart requirement | **Verified** | [Plugins reference](https://code.claude.com/docs/en/plugins-reference); local `_sync_marketplace.md` |

### Could not verify
- A single verbatim doc sentence stating that an edited frontmatter `description` re-registers the trigger without restart (inferred, §2).
- Whether issue #14836 has been fixed in a Claude Code release *after* 2.0.73 — the issue was open at filing and no later fix was located. **Re-check before relying on symlinked-skill discovery.**

## Sources

- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Create plugins — Claude Code Docs](https://code.claude.com/docs/en/plugins)
- [Plugins reference — Claude Code Docs](https://code.claude.com/docs/en/plugins-reference)
- [anthropics/claude-code #14836 — /skills doesn't find skills in symlinked directories](https://github.com/anthropics/claude-code/issues/14836)
- [anthropics/claude-code #25367 — symlinked ~/.claude/skills fails validation but executes](https://github.com/anthropics/claude-code/issues/25367)
- [vercel-labs/skills #744](https://github.com/vercel-labs/skills/issues/744), [#851](https://github.com/vercel-labs/skills/issues/851) — npx skills not creating ~/.claude/skills symlink
- Local: `/home/dev/projects/claude-plugins/.claude/skills/checkpoint/SKILL.md`, `_sync_marketplace.md`, `_sync_installed.md`; on-disk `~/.claude/plugins/{cache,marketplaces,known_marketplaces.json}`

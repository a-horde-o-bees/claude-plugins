---
log-role: reference
---

# Progressive Composer

Decisions governing the new meta-plugin that fills the ergonomic gap between plugin-grained marketplace UX and individual skill consumption. Tracks external repos, installs selectively, refactors third-party skills into the progressive-disclosure shape.

## Meta-plugin scope and rationale

### Context

The skills-as-atomic-unit architecture (see `skill-architecture.md`) implies users want to install individual skills, not entire plugin bundles. But the official Claude Code marketplace doesn't support per-skill install — `/plugin install <bundle>@<marketplace>` is plugin-atomic. Anthropic's own [skills repo](https://github.com/anthropics/skills) bundles 17 skills across 3 plugins; the README documents only `/plugin install` paths.

Skills CAN be installed standalone — Claude Code loads from `~/.claude/skills/<skill>/SKILL.md` and `<scope>/.claude/skills/<skill>/SKILL.md` directly per the [Skills doc](https://code.claude.com/docs/en/skills). Aggregators like skillsmp.com leverage this. But the path is manual `git clone + cp` today; no first-class tool exists for ergonomic individual skill management.

Research surveyed existing aggregators (netresearch/claude-code-marketplace, jeremylongshore/claude-code-plugins-plus-skills, alirezarezvani/claude-skills, sickn33/antigravity-awesome-skills, daymade/claude-code-skills, skillsmp.com). None do progressive-disclosure refactoring of upstream skills. The closest prior art is format-translation across agent ecosystems (Cursor/Codex/Gemini). The refactor-redistribute niche is unoccupied.

### Options Considered

**Skill-atomic plugin design alone — restructure our plugins to be one-skill or few-skills each.** Rejected: solves only our own bundling; doesn't help users wanting to install third-party skills selectively. The ecosystem-wide gap remains.

**Source-reference catalog (netresearch model) — marketplace.json pointing at upstream repos.** Rejected: doesn't solve refactoring; users still end up cloning and managing manually.

**Meta-plugin that tracks, installs selectively, and refactors.** Adopted. Fills the unoccupied niche; provides power-user UX that the official marketplace doesn't.

### Decision

`progressive-composer` is a new plugin separate from the ocd plugin. Scope:

| Capability | Behavior |
|---|---|
| Track sources | Config file lists tracked repos and marketplaces, with last-sync timestamps and per-skill sync mode (synced vs reimplemented) |
| Clone unmodified | `git clone` source repos to a managed cache; preserve LICENSE, attribution, and metadata |
| Install selectively | Copy `<source>/skills/<skill>/` to `<scope>/.claude/skills/<skill>/`; user picks which skills go where |
| Session-start sync | For source-tracking skills, diff cache against source on session start; refresh on drift |
| Intelligent recheck | For reimplemented skills (user has refactored them), diff cache against last-known-source; surface diffs to user without auto-applying |
| Refactor on demand | Take a skill folder, produce a progressive-disclosure-shaped variant; the user keeps both reference (source) and implementation (refactored) in the same place |
| Personal-track via branch | User maintains own customizations as a branch of the core plugin; usable across machines |

The plugin lives separate from ocd because it's a meta-tool that operates on any skill — its installed audience is broader than ocd-content consumers.

### Consequences

- **Enables:** ergonomic individual skill install (the gap official Claude Code marketplace doesn't cover); ability to consume third-party skills with our authoring discipline applied; cross-machine personal customization via branch tracking; reference-and-implementation in the same managed cache
- **Constrains:** the plugin must be built before ocd's own skills migrate to the new format (Phase B precedes Phase C of `plans/architecture-refactor.md`) — we dogfood progressive-composer on ourselves
- **Discovery surface:** progressive-composer ships as a plugin via marketplace (own bundle); becomes the install path for users who want individual-skill control beyond what `/plugin install` offers

## Distribution model — both paths from one source

### Context

With progressive-composer providing individual-skill install, the question is whether we keep plugin packaging at all, or go standalone-only.

### Options Considered

**Standalone-only — drop plugin packaging.** Rejected: official `/plugin install` UX is the discovery path most users reach for; abandoning it loses marketplace-surface visibility entirely.

**Plugin-only — drop standalone install path.** Rejected: defeats the meta-plugin's value; users wanting individual skills can't get them.

**Both paths from the same source.** Adopted. Plugin manifests bundle subsets of skills; skill folders are independently portable. Same source content materializes to both paths.

### Decision

The source repo ships:

- `.claude-plugin/marketplace.json` defining N thematic plugin bundles (marketplace surface for `/plugin install` users)
- `skills/<skill>/` folders that are independently portable (standalone surface for progressive-composer / direct `~/.claude/skills/` clone)

Users pick their preferred consumption path:

- `/plugin install <bundle>@<marketplace>` for atomic bundle install
- progressive-composer for individual-skill control with refactoring and source tracking
- Manual `git clone + cp` for users who want neither

### Consequences

- **Enables:** broadest reach across user types; aggregators like skillsmp can index our skills the same way they index any standard-format skill folder
- **Constrains:** marketplace.json must stay accurate as skills move between bundles or new bundles form; both surfaces share the same authoring discipline (the standard format works in both)

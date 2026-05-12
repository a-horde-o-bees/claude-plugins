---
log-role: reference
---

# Plugin Compartmentalization

Decisions governing how the source repo is split into thematic plugin bundles and how skills migrate out of the monolithic ocd plugin into more focused buckets.

## Thematic split from start

### Context

With skills as the atomic unit (see `skill-architecture.md`) and plugins as packaging conveniences, the question becomes how granular to make plugin packaging. Two extremes:

- One plugin per skill — maximum atomicity, maximum install ceremony. Each plugin needs its own marketplace entry; users install N times for N skills.
- One plugin for all skills — minimum ceremony, atomic install gives everything. Users get content they don't want.

Anthropic's pattern (anthropics/skills): single repo, multiple plugin manifests organized by category (`document-skills`, `example-skills`, `claude-api`). Roughly 5-7 skills per bundle. This is the middle ground.

### Options Considered

**Two-bucket start — disclosure-framework plugin + single ocd-content plugin with all skills. Split content further when growth justifies.** YAGNI lean from earlier in the design conversation; rejected when the user revoked YAGNI as a project principle (see `yagni-revocation.md`).

**Thematic split from start — multiple plugins from the same source repo, organized by domain. Migrate skills out of ocd one at a time.** Adopted. Forward-thinking design; allows progressive migration without forcing wholesale restructuring.

### Decision

The source repo ships multiple thematic plugin bundles via `.claude-plugin/marketplace.json`. Skills migrate out of the monolithic `ocd` plugin one at a time as each refactor completes; new plugins fork off naturally as content shape locks. The source repo stays one unit; plugin manifests carve it as packaging convenience.

Concrete migration:

| Step | Action |
|---|---|
| 1 | Skills source tree restructures from `plugins/ocd/systems/<sys>/` to `plugins/<plugin>/skills/<sys>/` per the anthropic-style layout |
| 2 | `marketplace.json` defines initial thematic plugins (likely candidates: rules-library, workflow-skills, navigation-skills, conventions-skills) |
| 3 | Each system migrates as a focused commit — moves to its target plugin's `skills/` directory; SKILL.md authored to format conventions; verbs/components extracted to `_<name>.md` siblings |
| 4 | ocd plugin shrinks as systems move out; eventually retains only the systems whose theme stays "ocd" (possibly setup, possibly nothing — TBD as the migration progresses) |

Compartmentalization is reversible — moving a skill between plugin bundles is editing one file (marketplace.json) plus moving the skill folder. No content rewrite. The plugin boundary is just packaging.

### Consequences

- **Enables:** users install only the thematic plugin(s) matching their needs; new plugins fork off without disrupting existing structure; compartmentalization decisions can refine as content shape locks
- **Constrains:** marketplace.json must stay accurate; every skill belongs to exactly one bundle (no cross-bundle ownership); per-bundle install ceremony multiplies with N (mitigated by skill-authoring for individual-skill control)
- **Open:** the natural thematic clusters are not yet locked. Likely candidates emerge as Phase E (system migration) progresses; final shape settles before Phase G

## Source repo stays singular

### Context

Compartmentalization could in principle split the source repo into N separate repos (one per plugin). Anthropic doesn't do this — their skills repo is one unit despite shipping multiple plugin bundles.

### Options Considered

**Multiple source repos, one per plugin.** Rejected: multiplies maintenance overhead; cross-plugin shared content (dependencies like PFN) becomes harder to keep canonical; users tracking via skill-authoring track N repos instead of one.

**Single source repo with multiple plugin manifests.** Adopted. Mirrors Anthropic's pattern; keeps shared content (dependencies/, READMEs, CONTRIBUTING) in one place.

### Decision

`.claude-plugin/marketplace.json` is the single source of truth for plugin bundle definitions. Skills live in `<repo-root>/skills/` (or under specific plugin directories if the structure evolves). Dependencies live in `<repo-root>/dependencies/`. One repo, multiple plugins.

### Consequences

- **Enables:** single CI surface; shared dependencies stay canonical; one source for skill-authoring to track for all our content; consistent authoring discipline applied across bundles
- **Constrains:** repo-level concerns (CHANGELOG, LICENSE, governance) cover all bundles uniformly; users can't selectively clone "just one plugin's source" without filtering

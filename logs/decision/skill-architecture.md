---
log-role: reference
---

# Skill Architecture

Decisions governing how skills exist as the atomic unit of distribution and consumption. Plugins are packaging conveniences for marketplace surfaces, not the architectural primitive.

## Skills as the atomic distribution unit

### Context

A prior architectural attempt made plugins the atomic unit and tried to manage context cost via per-system routing files at `<scope>/.claude/rules/<plugin>/<system>/triggers.md`. Two problems surfaced with that approach:

- Mainstream skill marketplaces (skillsmp.com and similar aggregators) discover and index `<skill-name>/SKILL.md` folders, not custom routing structures. Our cognitive-trigger frontmatter discipline made our skills less discoverable, not more — we were authoring against the ecosystem's grain.
- Plugins bundle skills atomically. The official Claude Code marketplace UX is `/plugin install <bundle>@<marketplace>` — no per-skill selective install. A user wanting one capability gets the entire bundle.

Per the [Skills doc](https://code.claude.com/docs/en/skills), Claude Code loads skills directly from `~/.claude/skills/<skill>/SKILL.md` and `<scope>/.claude/skills/<skill>/SKILL.md` — no plugin wrapper required. The runtime treats skills as the atomic unit; only the marketplace UX is plugin-grained. Aggregators like skillsmp leverage this, distributing skills as portable folders.

### Options Considered

**Keep plugins as the architectural primitive — fix discovery via custom routing layer.** Rejected: fights the ecosystem, sacrifices mainstream discoverability, requires every consumer to learn our routing model.

**Make skills the architectural primitive; plugins are packaging conveniences.** Adopted. Aligns with how Claude Code actually loads skills. Reuses the universal `<skill-name>/SKILL.md` format. Lets us produce both plugin bundles (for marketplace surface) and standalone skills (for direct copy / aggregator consumption) from the same source.

### Decision

Skills are the atomic unit of distribution. Each skill is a folder following the universal mainstream format. Plugins exist as marketplace-surface packaging — one source repo can ship N thematic plugin bundles. Plugin install gives users a bundle; standalone skill install gives users individual skills.

Three-mechanism content delivery:

| Mechanism | What | Where deployed | Triggering |
|---|---|---|---|
| Rules | Always-on disciplines (honesty, principle-not-symptom, etc.) | `<scope>/.claude/rules/<plugin>/<system>/` | Auto-loaded into every conversation |
| Skills | Reach-for capabilities (workflows, tool bridges, conventions) | `<scope>/.claude/skills/<skill>/` | Frontmatter description matches conversation context |
| Dependencies | Shared content (PFN, etc.) | `<scope>/.claude/dependencies/` | Sources `requires:` declaration; loaded by referrer |

### Consequences

- **Enables:** mainstream discoverability via standard format; selective install per skill via progressive-composer; per-skill upgrades; ecosystem alignment; same source content materializes to both distribution paths
- **Constrains:** plugin packaging is no longer the only mechanism — install machinery now spans plugin marketplace AND individual skill install paths; the new meta-plugin (progressive-composer) is required to make individual skill install ergonomic
- **Migration:** every ocd system reframes as a skill folder; current system structure (workflows/, components/, code) reorganizes around the skill format

## Rules-system retains the always-on discipline library

### Context

The pivot to skills-as-atomic raised the question of where always-on behavioral disciplines (honesty, principle-not-symptom, fix-foundations-not-symptoms, agent-first-interfaces) live. Skills are reach-for; they can't enforce continuous discipline since the agent doesn't reach for them on every utterance. A discipline like *honesty* must already be active when the agent makes any claim — not summoned at the moment of claim-making.

### Options Considered

**Convert all rules to skills.** Rejected: behavioral disciplines fire on every utterance; an agent doesn't "reach for honesty" before stating something.

**Eliminate rules entirely; rely on frontmatter description for skill-loaded discipline.** Rejected: the description sits in always-on context once the skill is installed, but the agent only acts on it when reaching for the skill — not on every utterance.

**Keep rules-system as the always-on discipline layer; default new behavioral content to skills.** Adopted.

### Decision

The rules-system maintains the curated always-on discipline library. Rule files deploy to `<scope>/.claude/rules/<plugin>/<system>/` and load on every conversation. Disciplines that genuinely fire on every utterance — pure behavioral guards like honesty, principle-not-symptom, fix-foundations-not-symptoms — live as rules.

New behavioral content defaults to skills, not rules. Rules are skeptical to add to; the bar is "this fires on every utterance and the agent cannot reach for it."

Categorization tests for new content:

- Can the agent reach for this guidance at a recognizable cognitive moment? If yes → skill.
- Does this need to fire across every utterance regardless of recognition? If yes → rule.

### Consequences

- **Enables:** always-on enforcement for disciplines that need it; clear default home for new content (skills); reduced rules-layer growth
- **Constrains:** rules-system curation is more important — adding to rules is the path of last resort; existing rules library is the canonical opt-in catalog projects pull from
- **Audit signal:** if a current rule never fires its always-on enforcement (no utterance benefits from its presence in every conversation), it's miscategorized — convert to skill

## Conventions become categorical skills

### Context

Conventions in the prior model were lazy-loaded content indexed via the discovery substrate's purposes section. Under the skill-atomic architecture, they need a new home. Conventions are project-shape-changing — installing a markdown convention changes how every markdown file in the project should be authored. Opt-in is appropriate; rules are too strong (always-on disciplines apply universally regardless of project context).

### Options Considered

**Conventions become rules.** Rejected: rules are too strong for project-shape-changing content; user wants opt-in semantics matching the influence the conventions exert.

**Conventions become individual reach-for skills (one skill per convention).** Rejected: skill-floor cost multiplies; too many tiny skills for related conventions; users opting into "documentation conventions" want the cluster, not each individually.

**Conventions become categorical skills — clusters of related conventions per skill.** Adopted.

### Decision

Conventions cluster into categorical skills. Examples of natural clusters: a `documentation-conventions` skill bundling claude-md, plans-md, tasks-md; a `system-structure-conventions` skill bundling system-structure, plugin-system. Installing a conventions-skill is opt-in: the user understands they're accepting project-shape-changing influence on the artifacts the skill governs.

The skill body indexes its conventions and reaches them via `_<convention>.md` siblings (per the flat-layout authoring shape). The `<scope>/.claude/conventions/` deployment directory dies — convention bodies live inside skill folders.

### Consequences

- **Enables:** opt-in semantics matching content's strength; categorical grouping reduces skill-floor cost; conventions become discoverable on mainstream marketplaces alongside other skills
- **Constrains:** clustering decisions need authoring — what conventions belong together? Resolved per cluster as it migrates
- **Migration:** existing `plugins/ocd/systems/conventions/templates/` content moves into per-skill bodies during Phase H of the architecture refactor (see `plans/architecture-refactor.md`)

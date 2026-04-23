# Skill description framing polish

Sharpen `/ocd:pdf` and `/ocd:navigator` SKILL.md `description` frontmatter toward the explicit "when to use" trigger-verb framing that the other skills and docs-prescribed guidance favor.

## Context

Surfaced by the comprehensive resample across the 54-repo claude-marketplace research corpus. Of the 14 skill/command descriptions sampled across 9 repos, 9/14 lead with trigger-verb framing ("Use when the user...", "Activated automatically when..."); 5/14 are bare "what it does" descriptors. Docs (`https://code.claude.com/docs/en/skills#frontmatter-reference`) explicitly prescribe the former: "Front-load the key use case."

This repo's 8 skills split:

- **Strong match:** `/ocd:log` uses explicit "Reach for this when encountering non-obvious context a future session will need..." — the clearest trigger-verb form in the set.
- **Action-verb hybrid:** `/ocd:git`, `/ocd:check`, `/ocd:setup`, `/ocd:refactor`, `/ocd:sandbox` lead with action verbs ("Manage", "Run", "Execute", "Work on") followed by scope. In the spirit of trigger-verb but not as explicit.
- **Shorter descriptors, no when-to-use:** `/ocd:pdf` ("Export markdown files to PDF using WeasyPrint.") and `/ocd:navigator` ("Sync navigator database with filesystem and populate purposes for paths that need them.") don't name trigger conditions.

## Proposed change

Rewrite the two short descriptors toward explicit framing. One-line-per-skill diff:

- `/ocd:pdf` current: `Export markdown files to PDF using WeasyPrint.` → proposed: `Export markdown files to PDF. Use when the user asks to publish, share, render, or convert markdown output to a printable or distributable format.`
- `/ocd:navigator` current: `Sync navigator database with filesystem and populate purposes for paths that need them.` → proposed: `Sync the navigator database with the filesystem and write purpose descriptions for new or stale entries. Use when the project structure has changed or when prompted that paths lack descriptions.`

## Why deferred

Not a release blocker. `MARKETPLACE-STANDARDS.md` notes the current state as aligned "in the spirit of" the trigger-verb cohort. The polish would bring `/ocd:pdf` and `/ocd:navigator` in line with `/ocd:log`'s stronger framing.

## Verification

After editing, verify via a fresh session that the skill-matcher surfaces these skills when a user describes the action rather than the domain. No automated test exists for description-matcher behavior — this is a judgment call against docs guidance.

# ocd init scope bleeds into non-development artifacts

`/ocd:init` deploys rules (design-principles, markdown, system-documentation, workflow) as always-on context for the entire project, with no distinction between development artifacts (code, skills, conventions, CLAUDE.md) and non-development content (resume text, cover letters, application materials, prose documents, policy drafts).

## Observed

Initialized `/ocd:init --force` in a job-search workspace where the primary artifacts are a resume (.docx/.pdf), tailored application bundles (prose + markdown), and a recommendation letter. The deployed always-on rules introduce direct conflicts with prose writing:

- `design-principles.md` — "Describe current reality only; do not reference previous states" directly conflicts with resume work, whose purpose is describing past achievements.
- `design-principles.md` — "Examples are generic — use concepts, not project-specific names" conflicts with resumes that need specific project names, companies, and metrics.
- `markdown.md` — "Every file opens with a level-1 heading... followed by a purpose statement" is wrong for cover letters drafted in markdown.
- `design-principles.md` Economy of Expression + YAGNI — risks stripping narrative voice from cover letters and recommendation letters where human reasoning matters.

Conventions target specific file types (SKILL.md, README.md, architecture.md, python, MCP servers) and do not match prose files, so the conventions layer is correctly scoped. The rules layer is not.

## Suspected root cause

Rules have no `applies_to` or `scope` mechanism. Unlike conventions (which carry glob patterns and are resolved per file via `governance_match`), rules load as context regardless of what the agent is about to do. There is no way to say "these rules govern development artifacts under `plugins/`, `src/`, `.claude/`, but not prose content under `applications/` or `resume/`."

User observation prompting this log: "they need to be scoped to apply to development artifacts, not everything." The user's global CLAUDE.md already warns of the symmetric failure mode at user scope — project-specific writing disciplines cross-contaminating unrelated domains.

## Possible directions

- Scope field on rules (analogous to convention `applies_to`) so rules can declare which directories or artifact classes they govern.
- Distinction between "always-on foundational rules" (workflow, process-flow-notation for agent behavior) vs "artifact discipline rules" (design-principles, markdown) — the latter should be governance-resolved per file like conventions.
- Init-time opt-in for which rule sets deploy, so projects that are not primarily code can decline the artifact-discipline rules.

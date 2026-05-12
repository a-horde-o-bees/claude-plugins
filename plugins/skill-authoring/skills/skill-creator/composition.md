---
spec_version: 1
name: skill-creator
description: "Use whenever the user wants to create a new skill from scratch — interview, draft, iterate, optimize the trigger, and package — with PFN + progressive-disclosure + description-authoring + workflow-vs-script disciplines applied at every authoring moment. Companion to skill-composer (compose layers existing sources; create authors from scratch with discipline)."
sources:
- url: "https://github.com/anthropics/skills"
  skill: skill-creator
  ref: main
  commit: f458cee31a7577a47ba0c9a101976fa599385174
---

# Goal

Help users design new skills that conform to our project's authoring disciplines from the first draft. Inherits the proven skill-creator workflow (interview → draft → test → iterate → optimize description → package) and bakes in PFN notation, progressive-disclosure layering, description-authoring discipline, and workflow-vs-script decomposition at every authoring moment. The community skill-creator covers *what* the loop is; this composition adds *how* the project's disciplines apply at each step of that loop.

Pairs with `/skill-authoring:skill-composer`: compose layers existing sources into a new skill; create authors a new skill from scratch with the same authoring discipline. Together they cover the two ways new skills enter the project.

## Surface

### Start designing a new skill from scratch

Routes to: `_new.md`

User wants to begin a new skill. Workflow handles interview-driven intent capture, initial SKILL.md and component-file scaffolding from bundled templates, and initial test-case scaffolding. Lives in `_new.md` so a false-positive trigger doesn't pay the full interview cost.

### Iterate on an in-progress skill

Routes to: `_refine.md`

User wants to keep working on a skill — run test cases, review outputs, apply feedback, repeat. Workflow handles the test-evaluate-iterate loop from skill-creator. On user signal of satisfaction: description optimization (run_loop) + packaging.

### Enumerate in-progress skills

Routes to: `_list.md`

User asks what skills are in flight. Terse listing — name + state (new / refining / ready). Decision-aid; not a workflow.

## Sources

### anthropics-skills--skill-creator:skill-creator

Informs: `_new.md`, `_refine.md`. **Keep**: the overall loop shape (interview → draft → test → iterate → optimize description → package), the description-optimization `run_loop.py`, the eval viewer (`generate_review.py`), the packaging script (`package_skill.py`), the eval JSON schema (`references/schemas.md`), the grader / comparator / analyzer agent prompts. **Adapt**: decompose the monolithic SKILL.md into a verb-shaped surface (`_new.md` / `_refine.md` / `_list.md`); author all workflow content in PFN; extract mechanical work to `scripts/`. **Reject**: Claude.ai-specific and Cowork-specific instructions (we're in Claude Code). The community skill-creator answers *what* the steps are; this composition adds *how* the project's disciplines apply at each step.

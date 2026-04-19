# Abstraction Instructions

Analyze an existing capability and produce a generalized problem description suitable for unbiased solution research. The goal is to describe what the capability does at the problem level so that research discovers existing tools, proven approaches, and established patterns that fulfill the same purpose — including solutions that could be adopted directly.

## Process

1. Read all provided target content thoroughly
2. Identify the core problem the capability solves — what need does it address, what outcome does it produce, who benefits
3. Extract system constraints — literal deployment facts that are non-negotiable
4. Produce a generalized scope statement using domain-neutral language

## Scope Statement

Describe the problem space, not the tool. The scope should be recognizable to someone who has never seen the current implementation but understands the domain.

Structure:
- One sentence: the core problem being solved
- Two to three sentences: what a solution in this space does — inputs, evaluation approach, outputs — without naming specific techniques
- One sentence: the value proposition — what improves when this works well

## System Constraints

Literal facts about the deployment environment that any solution must satisfy. Constraints filter research results — they exclude impossible approaches without favoring any particular valid approach.

Include:
- Platform and runtime requirements (e.g., runs as CLI tool, operates within terminal session)
- Integration requirements (e.g., must integrate with specific platform, must read project files)
- Invocation model (e.g., user-triggered, runs on-demand, produces report)
- Output requirements (e.g., must produce actionable findings, must identify specific locations)

Exclude:
- Architecture choices (e.g., uses SQLite, spawns parallel agents, has plugin system)
- Data format choices (e.g., reads criteria from markdown, stores results in database)
- Structural decisions (e.g., separates evaluation into focus areas, extracts components to files)
- Workflow patterns (e.g., orchestrator/agent split, convergence loops)
- Feature counts or categorizations (e.g., has 4 focus areas, supports 12 criteria categories)

## Distinguishing Constraints from Bias

Test: "Could a fundamentally different implementation satisfy this requirement?"
- Yes → it is a constraint (keep)
- No, it describes how the current implementation works → it is bias (exclude)

Example: "Must produce findings tied to specific file locations" is a constraint — many different approaches could satisfy this. "Uses per-finding report format with 5 fields" is bias — it describes the current report structure.

## Output Format

Return two clearly labeled sections:

**Generalized Scope:**
[scope statement as described above]

**System Constraints:**
- [constraint 1]
- [constraint 2]
- ...

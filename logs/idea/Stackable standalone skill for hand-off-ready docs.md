# Stackable `/standalone` skill for hand-off-ready docs

A skill (working name `/standalone`) that applies a "standalone hand-off" lens to whatever document the rest of the prompt or stacked skills would produce. Stacks on top of any document-producing skill or freeform doc-writing request and adjusts the output to be suitable for hand-off to an outside audience.

## Motivation

Surfaced during the Monaco executive-summary work: a doc intended for a non-technical client requires fundamentally different discipline than a doc intended for an internal agent or developer audience, and the discipline doesn't naturally emerge from "write an executive summary." Specifically the hand-off doc needs to be:

- **Self-contained.** No references to project-internal files, paths, or systems the recipient doesn't have access to. Every claim has to be readable on its own.
- **Hour-estimated, not calendar-projected.** "2–4 weeks of work" reads ominously to non-technical readers; hour ranges convey the same information without implying a deadline.
- **Direct-link where action is being asked for.** If the doc asks the recipient to inspect a system, log into a service, or review records, the doc carries the direct URLs.
- **Free of technical jargon and code references** in prose. Internal terms get spelled out or replaced with natural-language equivalents.

The Monaco executive summary went through three rounds of revision to apply each of these disciplines after the fact; a `/standalone` lens would apply them up front.

## Shape

Stackable means: the user's prompt can invoke `/standalone` alongside other skills (`/standalone /executive-summary <topic>` or, freeform, `/standalone <write a release note>`). The skill is a *lens*, not a generator — it doesn't produce a doc on its own; it constrains and post-processes whatever the rest of the prompt produces.

Concrete behaviors the lens would enforce:

- After draft, scan for internal file paths (`logs/...`, `pipeline/...`, `tests/...`, any `*.md` reference) and either remove them or replace with prose explaining the same concept.
- Scan for calendar projections (`N weeks of work`, `N days`, `by end of <month>`) and rewrite as hour ranges plus an acknowledgment that calendar depends on parallel-track variables.
- Scan for code-format inline references (backticked paths, env var names, schema column names) and either lift into plain prose or remove if they're not load-bearing for the reader.
- For any "review this" / "log into this" instruction, ensure a direct URL is present.
- Open with "what this is and who it's for" and close without a "where to find more detail" section pointing back at internal docs.

## Open questions

- Is this best as a true stackable skill (modifying another skill's output via post-process) or as a pre-prompt that adjusts how the rest of the prompt is interpreted?
- Where does this lens fit relative to `/blueprint:status`-style summary skills that already exist? Probably composes on top of them rather than replacing.
- Should the lens carry conventions for different hand-off audiences (executive, end-user, board, vendor) or stay generic with the discipline above?

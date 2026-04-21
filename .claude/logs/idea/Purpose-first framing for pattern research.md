# Purpose-first framing for pattern research

## Purpose

When cataloging patterns across a design space, group by purpose (what users are trying to accomplish) rather than by system feature (what the API exposes). Same system mechanism often serves multiple purposes; same purpose often composites multiple mechanisms — grouping by mechanism fragments guidance a reader needs assembled, and groups unrelated things under one heading because they share a tool.

## The reframe

**Feature-oriented (wrong for pattern docs):** start from the API surface. "Hooks" as a component, then subsections for event coverage, hook type, modifiers, output convention, monitors. Produces API documentation the reader has to re-assemble to answer their actual question.

**Purpose-oriented (right for pattern docs):** start from what builders do. "Dependency installation" as a purpose, combining SessionStart hooks + `${CLAUDE_PLUGIN_DATA}` + manifest diff + retry-next-session + failure signaling into one coherent recipe. "Tool-use enforcement" as a separate purpose, reusing the hook system for a different goal with its own idioms and pitfalls.

## Tests for whether a heading is purpose or feature

- **Does the heading name a problem a builder might have?** → purpose. ("I need to install dependencies.")
- **Does it name a system capability?** → feature. ("Hooks.")
- **Would two unrelated recipes land under the same heading because they share a mechanism?** → feature, regroup.
- **Would one coherent recipe fragment across multiple headings because it uses multiple mechanisms?** → feature, regroup.
- **Pitfalls and constraints: are they specific to the purpose, or generic to the mechanism?** Purpose-specific pitfalls live inside the purpose; mechanism-specific quirks mostly don't need their own home.

## When to apply

Any pattern-cataloging research where the output is guidance for builders, not API reference. Plugin marketplace patterns, library integration patterns, testing patterns, CI/CD patterns. If the output's audience is "someone deciding how to solve problem X," purpose-first organizes the evidence around their decision; feature-first makes them reconstruct it.

## Counter-cases

API reference docs legitimately group by feature — the reader already knows what API to use and is looking up mechanics. Don't collapse the two genres.

## Prior instance

Emerged during claude-marketplace pattern research (2026-04-20). First draft grouped by system component (Hooks, Bin wrappers, CI/CD). User caught the drift: "you're basically enumerating the API and matrixing with what users are calling in the wild." Reframe to purpose-oriented produced much cleaner sections — dependency installation, tool-use enforcement, session context loading, channel distribution — each composite and coherent.

# description-authoring description doesn't fire Haiku matcher

## Observed defect

Single-query pilot ran:

```bash
unset CLAUDECODE
claude -p "Help me write the description for this new skill" \
  --output-format stream-json --verbose --include-partial-messages \
  --model claude-haiku-4-5-20251001
```

Skill installed at `.claude/skills/description-authoring/SKILL.md` with frontmatter description:

> "Use when writing the lead at a structural boundary — SKILL.md description, docstring, README opener, commit subject, section head, file header, log entry opener, schema title — where a reader or matcher decides engage-vs-skip from the lead alone. The lead must encode the cognitive moment, exclude internal mechanism, and stay non-confusable with neighboring artifacts."

Stream-json output showed:

- `tools called: []` — agent did NOT invoke the Skill tool
- Agent emitted text directly (328 output tokens, 1 turn)
- Skill body never loaded into context

## Hypothesis

Three plausible causes, listed in order of cheapest-to-test:

1. **Haiku invocation threshold is lower than Opus.** Haiku may be more willing to answer directly than to invoke a skill. Test by re-running with `--model claude-opus-4-7` — the model the user actually runs interactively.
2. **Description is still too abstract.** Reads like guidance about descriptions in general, not like "I help with this specific situation." Agent may think it can handle a generic "write a description" request without the skill.
3. **Query is too lightweight.** "Help me write the description for this new skill" doesn't signal "I need careful authoring discipline applied." A heavier framing might trigger invocation.

## Next step

Opus dry-test before any description rewriting — distinguishes (1) from (2)/(3). Same query, same SKILL.md, only the model changes. Result either fires or doesn't.

- Fires → description is OK at Opus, Haiku threshold is the explanation, move on.
- Doesn't fire → description itself needs reshaping. Spawn a Phase 1 agent (per [logs/patterns/description-refinement-two-phase-loop.md](../patterns/description-refinement-two-phase-loop.md)) to derive a fresh candidate without my prior draft visible. Or feed the failed query back through `improve_description.py` for an automated rewrite.

## Status

Open. Pending Opus dry-test after `/skill-creator` is verified surfaced post-restart.

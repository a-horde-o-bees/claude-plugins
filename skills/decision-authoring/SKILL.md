---
name: decision-authoring
description: Use when writing or revising a DECISIONS.md record — to capture why a choice was made and which alternatives were rejected, scoped to what the current code and docs cannot show on their own.
---

# decision-authoring

A decision record preserves only what the decision's artifacts cannot show on their own: the forces that made it a decision, the choice (referenced, not re-described), and the alternatives rejected with their reasoning. Everything a reader can derive by reading the current code and docs is description, not decision — it does not belong here, and a copy of it rots the moment the artifact changes.

The current-state artifact shows *what is*. A decision record's unique job is the counterfactual — *why this, and why not that* — which the artifact structurally cannot show.

## The necessity test — the gate on every line

For each sentence ask: **can a reader derive this by reading the artifacts this decision governs?**

- **Yes** → cut it. It is description; the artifact already carries it. Replace it with a pointer if locating it helps.
- **No** → keep it. It is load-bearing: a force, a rejected alternative, a rationale or tradeoff that left no trace in the result.

This is the slim test specialized to decisions. When a line feels important but fails the test, it is almost always *curse of knowledge* — it reads as essential to the author because they remember the decision, but the reader gets the same fact from the artifact.

## What a record contains

- **Forces / context** — the constraints and the problem that made the obvious choice wrong, so a reader sees why a decision was needed at all. Not discernible from the solution, which shows only the resolution.
- **The decision** — one claim a reader can agree or disagree with, plus a pointer to where the resulting design is documented. Reference the design; never restate its structure, file roles, or mechanics.
- **Rejected alternatives, each with its reasoning** — the paths not taken leave no trace in the artifact, so this is the most irreplaceable content. The fence: a future reader must know why X was tried and dropped, or they re-propose it.
- **Consequences** — only the non-obvious ones: a tradeoff accepted, a constraint now imposed, a cost paid. Skip any consequence the artifact makes evident.

## Cut

- Any description of *what was built* — structure, file roles, section contents, the mechanics of the chosen design. It lives in the artifact; link to it.
- Restatement of a rule, schema, contract, or process documented elsewhere — point, don't duplicate.
- "How it works" walkthroughs — the code is the authority.
- Status, dates, counts, and progress — those are tracker state, not a decision; they rot fastest.

## One decision per record

A record answers one choice. Two independent choices are two records — each is rejected, revisited, and superseded on its own. A record that needs "and we also decided…" is two records.

## Supersede, never accrete

A record survives only while it describes the current model. When a choice is reversed, **replace** the record (carrying forward any still-valid rejected alternative as a fresh entry's reasoning); do not leave the old and new side by side. A DECISIONS file is the set of currently-load-bearing choices, not their history.

## Form

Lead with the decision claim, then the forces, then the rejected alternatives — not the backstory first. Slim the prose with /concise-prose once the necessity test has set the content.

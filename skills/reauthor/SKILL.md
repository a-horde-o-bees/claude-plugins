---
name: reauthor
description: Use when the user wants an artifact composed fresh rather than patched — "rebuild X", "rewrite from scratch", "reauthor", "regenerate" — or when a correction should land cleanly, with no comparative residue ("previously X, now Y", "this replaces the old approach"). X is any nameable artifact: file, section, function, paragraph, schema.
---

# Reauthor

Compose the artifact as if authoring it for the first time. The current form is informative — it represents what worked before whatever now wants to change it. Treat it as a sketch you have discarded.

## What survives

- **Outcome** — what the artifact produces, causes, or enables.
- **Identity** — name, path, public interface.

Everything else — organization, phrasing, ordering, examples, headings — is yours to set from the constraints in play now.

## Rules

- Read the current artifact along with every rule, convention, and skill in context, plus the surrounding conversation. Let all of them shape the new version at once.
- Build the structure from what the artifact must do now, not what it used to do.
- Eliminate duplication: content stated twice, examples making the same point, parallel sections that hedge each other.
- Rephrase only when it strictly tightens or corrects — a phrasing already at the bar stays; swapping it for an equally good one is churn, not improvement.
- Output the whole artifact end-to-end. No `...`, no `[unchanged]`, no implied continuation.
- Don't spot-edit section by section — local fixes accumulate as patches; only an end-to-end pass restores coherence.
- Don't anchor on existing phrasing or organization — both solved a problem set that may no longer apply.
- Don't leave comparative or relational residue: no temporal trace ("previously this was X", "removed the old behavior", "as opposed to before"), and no dependence on context that no longer sits with the artifact — a pointer to a sibling that's been cleared away, or a position/sequence label (`Phase 2`, `Step 3`, "see the fix below", "carried from above") that only meant something beside what's now gone. A reader picking the artifact up cold should see no trace of prior versions and need nothing absent to understand it — every fact stated directly, not by reference.

## When not to reauthor

- Local correction or clarification — apply it in place. Reauthor only when the change reaches the artifact's structure, ordering, or coherence, not a single spot.
- Localized bug fix — patch it.
- Rename, file move, pure refactor.
- Conformance check without intent to change — audit.

## Scope

Default to the unit the user named. Widen only with explicit approval, and only when the named unit can't cohere without touching neighbors — say so first.

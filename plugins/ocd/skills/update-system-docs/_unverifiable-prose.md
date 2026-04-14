# Unverifiable Prose Classification

Deterministic markers for identifying claims that should pass through untouched. Five categories; each has regex-level signals plus LLM fallback. Any claim matching these markers is classified `unverifiable-prose` at claim-extraction time and never reaches the verification or edit stages.

## Categories

| Category | Markers | Example |
|----------|---------|---------|
| motivation | Modal "so that", "to let", "helps you"; present-subjunctive; no concrete symbols | "A goal is to make it easier to ship small tools without boilerplate." |
| tradeoff-discussion | Comparative adjectives, "instead of", "rather than", "prefer ... over"; mentions approaches not implemented | "Prefers explicit configuration over convention because the latter fails silently when versions drift." |
| historical-context | Past-tense verbs, years, "originally", "was introduced", "replaced" | "Originally started as a fork of earlier tooling, now rewritten from scratch." |
| external-integration-reference | Brand or project names not present in fact bundle; "compatible with", "works with" | "Compatible with any OpenAI-style chat completions endpoint." |
| design-rationale | "because", "this means", "the reason", "we chose" — paired with a claim but giving the reasoning | "Each command is a class because the test harness needs to introspect argument parsers." |

## Deterministic Pre-Classification

Applied before the claim-extraction prompt runs. Marks candidates for the LLM to confirm:

```
1. For each sentence in doc:
    1. If sentence matches historical-marker regex (past-tense + temporal reference):
        - Mark as unverifiable-prose candidate (historical-context)
    2. If sentence matches tradeoff regex ("instead of", "rather than", "prefer ... over"):
        - Mark as unverifiable-prose candidate (tradeoff-discussion)
    3. If sentence contains rationale markers ("because", "the reason", "we chose") AND the rationale itself is not a fact-checkable claim:
        - Mark as unverifiable-prose candidate (design-rationale)
    4. If sentence contains brand/project names not present in fact bundle dependencies AND no code-identifier tokens:
        - Mark as unverifiable-prose candidate (external-integration-reference)
    5. If sentence uses modal constructions ("so that", "to let", "helps you", "a goal is to") AND has no concrete symbol reference:
        - Mark as unverifiable-prose candidate (motivation)
2. Pass pre-classifications to LLM as input — LLM confirms or reclassifies
```

## Mixed Claims

A sentence like:

> "Templates live under `plugins/ocd/templates/` rather than `.claude/` so edits propagate through sync."

mixes a verifiable claim (`located-at` for the path) with design rationale (`rather than X so Y`). Handle at claim-extraction time:

```
1. LLM emits two claims:
    - claim_text: "Templates live under `plugins/ocd/templates/`"
      claim_type: located-at
      verifiable: true
    - claim_text: "rather than `.claude/` so edits propagate through sync"
      claim_type: unverifiable-prose
      verifiable: false
2. Verification runs only on the first; edit (if needed) targets only that span
3. The "rather than" clause remains untouched in the doc
```

Claim-extraction rule #2 ("Emit one claim per atomic proposition") drives this split.

## Examples for LLM Calibration

10 concrete examples included in the claim-extraction prompt as few-shot guidance (may be pulled into the prompt or kept as reference):

1. "This tool exists to reduce the manual effort of keeping docs in sync with code." — motivation
2. "We preferred a single binary over a plugin architecture to keep installation one step." — tradeoff-discussion
3. "The project started as an internal script before being open-sourced." — historical-context
4. "Works with any OpenAI-compatible endpoint, including Ollama and vLLM." — external-integration-reference (pass through unless fact bundle has explicit adapter code)
5. "Each phase is a separate module because the test suite exercises them independently." — design-rationale
6. "Prior versions used YAML for config; the current version uses TOML for inline comment support." — historical-context (split: "current version uses TOML" may be verifiable if pyproject.toml is in fact bundle)
7. "Parallelism is bounded by a semaphore to avoid saturating the LLM endpoint." — borderline: if fact bundle has a `Semaphore` use, reclassify as `implements-pattern`
8. "The goal is to be conservative — false positives waste developer time." — motivation
9. "Templates live under `plugins/ocd/templates/` rather than `.claude/` so edits propagate through sync." — mixed; split at extraction
10. "We do not plan to support Windows shells natively; use WSL." — design-rationale + negative claim; pass through

## Regeneration Handling

When regenerating a doc (rare v2 case), unverifiable-prose entries from the prior doc's extraction must splice back into the regenerated output. See `_doc-generation.md` Preserved-Prose Splicing.

## Anti-Stripping During Update

When updating (not regenerating) an existing doc:

```
1. Claims classified unverifiable-prose are NEVER queued for verification
2. Claims classified unverifiable-prose are NEVER queued for surgical edit
3. The surrounding text is never touched by the edit stage
4. If the user's prior prose is adjacent to a contradicted verifiable claim, the edit's minimal-span rule ensures the unverifiable prose is not captured in the {original} span
```

This combination — deterministic pre-classification + LLM confirmation + extraction splitting mixed claims + edit stage never seeing unverifiable claims — is the end-to-end enforcement of the "leave alone what isn't provably incorrect" discipline.

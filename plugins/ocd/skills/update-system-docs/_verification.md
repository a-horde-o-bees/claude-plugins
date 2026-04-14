# Claim Verification

Verify a single extracted claim against the system's fact bundle. Uses deterministic candidate-fact selection first; LLM judgment only for remaining cases. Outputs a verdict plus evidence and contradicted spans that the conservative-edit stage quotes for replacement.

### Variables

- {claim} — one claim object from `_claim-extraction.md` output
- {fact-bundle} — full deterministic fact bundle for the system

## Candidate Fact Selection (deterministic, pre-LLM)

Map each claim_type to the fact bundle slice that could speak to it:

| claim_type | Candidate facts |
|------------|-----------------|
| exposes | file inventory + public symbols (functions, classes, MCP tools, CLI commands) with name overlap to subject |
| depends-on | imports graph + requirements.txt + pyproject.toml dependencies + declared system dependencies |
| located-at | file/directory inventory from navigator paths_list |
| command-is | CLI command registry (argparse/click) + MCP tool registry + shebang-prefixed scripts |
| supports | version metadata from pyproject.toml classifiers, setup.cfg, package.json engines |
| requires | imports graph + env var usage + runtime checks (`command -v X` in bash steps) |
| implements-pattern | pattern_signals entries (decorators, base classes, library usages) |
| structure | imports graph + call graph |
| other | union of exposes, depends-on, located-at |

## Empty-Candidate Short Circuit

```
1. If candidate facts for {claim} is empty:
    1. Mark verdict = no-evidence
    2. Skip LLM call
    3. Return
```

This distinguishes `no-evidence` (claim could be checked but no fact bundle entry spoke to it) from `contradicted` (claim directly conflicts with a fact).

## Prompt

```
<role>
You verify one documentation claim against a fact bundle extracted from
the system's source code. Be conservative: when evidence is partial or
ambiguous, say so — never invent a verdict.
</role>

<claim>
{claim.claim_text}
</claim>
<claim_metadata>
type:    {claim.claim_type}
subject: {claim.subject}
section: {claim.section}
</claim_metadata>

<fact_bundle>
{candidate_facts}
</fact_bundle>

<task>
Determine whether the claim is consistent with the fact bundle. Use EXACTLY
one of these verdicts:

- verifiable-consistent    — fact bundle confirms every proposition in the claim
- contradicted             — fact bundle directly contradicts at least one proposition
- partial                  — claim lists N items; some confirmed, some contradicted or absent
- no-evidence              — no fact in the bundle speaks to this claim; do not guess
</task>

<rules>
1. "Claim names 3 functions; 2 match" => partial. Enumerate matched and unmatched in evidence.
2. Type-level mismatches (claim says "returns dict", fact says "returns list") => contradicted.
3. Missing from fact bundle is not the same as contradicted. If the bundle is silent, use no-evidence.
4. Surface-form differences (snake_case vs camelCase, trailing slash on paths) => contradicted only if the user-facing form matters for the claim_type (command-is, located-at). For exposes, normalize before comparing.
5. Do not infer absence from a subset bundle. If you are unsure whether the bundle is exhaustive for the claim's scope, prefer no-evidence over contradicted.
</rules>

<output_format>
{
  "verdict":             "verifiable-consistent" | "contradicted" | "partial" | "no-evidence",
  "evidence":            [ { "fact": string, "relation": "confirms" | "contradicts" | "silent" } ],
  "contradicted_spans":  [ string ],   // substrings of claim_text that are wrong; [] if none
  "confidence":          "high" | "medium" | "low"
}
</output_format>
```

## Bias: False-Alert Over Silent-Pass

Per Stanford SSP+24, LLM semantic equivalence judgments skew toward acceptance. To counter this:

- Prompt explicitly permits `contradicted` only with direct conflict, but also permits `partial` when confirmation is incomplete
- `no-evidence` does not equal `verifiable-consistent` — it is reported to the user as a claim the skill could not check
- When two verdicts seem plausible, the prompt instructs `no-evidence` over `verifiable-consistent` for partial bundles

The report stage surfaces no-evidence counts per system so the user can sanity-check the classifier.

## Downstream Consumption

- `verdict` = verifiable-consistent → no action
- `verdict` = contradicted or partial → drive `_conservative-edit.md` with contradicted_spans
- `verdict` = no-evidence → no action; counted in report

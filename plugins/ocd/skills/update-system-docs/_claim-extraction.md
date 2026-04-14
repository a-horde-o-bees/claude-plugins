# Claim Extraction

Prompt template for extracting structured claims from existing documentation. Run once per doc file. Output is a list of claim objects consumed by `_verification.md` and `_conservative-edit.md`.

### Variables

- {doc-content} — full markdown content of the doc being analyzed
- {source-doc} — short identifier: "readme" | "architecture" | "claude-md" | "skill-md"
- {system-name} — name of the system being documented

## Prompt

Given to the LLM via the agent's own reasoning (no sub-agent spawn):

```
<role>
You are extracting check-worthy claims from system documentation for a
code-versus-docs fact-checking pipeline. Your output drives surgical
edits — claim spans must be copied verbatim from the input.
</role>

<inputs>
<system_name>{system-name}</system_name>
<source_doc>{source-doc}</source_doc>
<content>
{doc-content}
</content>
</inputs>

<taxonomy>
A claim's type is exactly one of:
- exposes            — names a public function, class, CLI command, MCP tool, HTTP endpoint
- depends-on         — names a required library, binary, service, env var
- located-at         — asserts a file, directory, or path
- command-is         — gives a literal shell / CLI invocation
- supports           — asserts a supported platform, version, format, language
- requires           — asserts a precondition (Python >=3.10, ripgrep installed)
- implements-pattern — asserts an architectural pattern used in the code (singleton, pipeline stage, ast visitor)
- structure          — asserts a structural relationship (module X imports Y, component A calls B)
- unverifiable-prose — motivation, tradeoff discussion, historical context, external-integration reference, or design rationale
- other              — check-worthy but does not fit above
</taxonomy>

<rules>
1. claim_text MUST be a verbatim substring of the input. No paraphrase, no normalization, no ellipsis.
2. Emit one claim per atomic proposition. A sentence that names three exposed functions emits three claims.
3. section is the full heading breadcrumb from the H1 down to the nearest heading, joined with " > ".
4. subject is the primary entity the claim is about — a file path, symbol, command string, or component name. If no single subject, use null.
5. verifiable = false iff claim_type is unverifiable-prose. Every other type is verifiable = true.
6. Do not infer claims from absence. If the doc does not state X, do not emit a claim that X is or isn't the case.
7. Prefer precision over recall. When you hesitate, emit the claim as claim_type=other and let the downstream stage decide.
</rules>

<output_format>
Return a single JSON array. Each element:
{
  "claim_text":  string,   // verbatim substring of the input doc
  "claim_type":  string,   // one of the taxonomy labels
  "section":     string,   // heading breadcrumb
  "subject":     string | null,
  "verifiable":  boolean,
  "source_doc":  string    // echoed from input
}
Return [] if no claims are found. Emit no prose outside the JSON array.
</output_format>
```

## Pre-LLM Deterministic Filtering

Before invoking the prompt, apply the unverifiable-prose pattern matchers from `_unverifiable-prose.md` to mark obvious pass-through content. These pre-classified regions are still included in the prompt input so the LLM can cross-check, but the pre-classification acts as a signal the downstream stage respects.

## Post-LLM Validation

```
1. For each {claim} in LLM output:
    1. Assert {doc-content}.count({claim}.claim_text) >= 1 — claim_text must be verbatim
    2. If count == 0: discard the claim (LLM paraphrased despite rules)
    3. If count > 1: note ambiguity; downstream edit stage must extend original with context to uniquify
    4. Validate claim_type is in taxonomy; map unknowns to "other"
2. Deduplicate by (source_doc, claim_text)
3. Return filtered list
```

## Chunking Strategy

For docs exceeding ~4k tokens:

```
1. Split on H2 boundaries
2. For each chunk: invoke prompt with chunk as {doc-content}, inject enclosing H1 + H2 path into system-name
3. Merge results; deduplicate
```

Most project docs are small enough that chunking is not triggered.

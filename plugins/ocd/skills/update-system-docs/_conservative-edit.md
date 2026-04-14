# Conservative Edit

Produce a surgical edit for a single contradicted claim. Quote-then-replace pattern, not whole-file rewrite. Every edit is verifiable via substring match; the Edit tool's unique-match requirement fails loudly on re-application, giving built-in idempotence.

### Variables

- {claim} — claim object with verdict ∈ {contradicted, partial}
- {evidence} — evidence array from `_verification.md`
- {fact-bundle-slice} — candidate facts that drove the verdict
- {doc-path} — path to the doc file
- {doc-content} — full doc content

## Prompt

```
<role>
You produce one surgical edit that fixes a documentation claim contradicted
by the code. You are not improving the doc — only repairing the specific
wrong substring. Everything outside the quoted excerpt must remain untouched.
</role>

<contradicted_claim>
{claim.claim_text}
</contradicted_claim>

<verdict_evidence>
{evidence}
</verdict_evidence>

<fact_bundle_slice>
{fact-bundle-slice}
</fact_bundle_slice>

<doc_file>
path: {doc-path}
content:
{doc-content}
</doc_file>

<constraints>
1. original MUST be a verbatim substring of doc_file.content. No rewrites, no added whitespace, no trimmed trailing punctuation.
2. original MUST be minimal — the smallest span that still encloses every contradicted proposition. Do not expand to "clean up" surrounding prose.
3. replacement MUST be consistent with every fact in fact_bundle_slice. If the fact bundle is silent on a detail that appeared in original, drop that detail — do not invent a substitute.
4. Preserve markdown: code fences stay fenced, inline code stays backticked, list items stay in list syntax, headings untouched.
5. If the only correct fix is to remove the claim entirely, set replacement to "" — the skill handles deletion, including collapsing a surrounding blank line if needed.
6. Never introduce a NEW claim. The replacement may restate the same proposition correctly, shorten to a weaker true form, or go empty — nothing more.
7. Do not touch anything outside the quoted span — not an adjacent sentence, not a neighboring bullet, not the heading above.
</constraints>

<output_format>
{
  "original":    string,    // verbatim substring of doc_file.content
  "replacement": string,    // new text; "" means delete
  "rationale":   string,    // one sentence citing the fact that drove the edit
  "action":      "replace" | "delete"
}
</output_format>
```

## Post-LLM Validation (deterministic)

```
1. Assert {doc-content}.count({original}) == 1
    - If 0: reject; LLM paraphrased despite rules
    - If >1: reject; ambiguous — retry once asking LLM to extend {original} with more surrounding context to uniquify
2. Assert len({replacement}) <= 2 * len({original}) + 50 — guardrail against rewrites; small absolute buffer for short strings
3. If action=delete, {replacement} must be ""
4. Apply: Edit tool with old_string={original}, new_string={replacement}
5. Re-parse modified doc as markdown:
    - Assert heading count unchanged
    - Assert code fence count unchanged
    - Assert paired brackets/parens balanced
    - If structure broke: revert via a second Edit, reversing the operation; surface failure to agent
```

## Retry Logic

If the first LLM response fails either the verbatim-substring check or the size guardrail:

```
1. Retry once with appended instruction: "Your previous attempt failed {reason}. Re-emit original as a verbatim substring of doc_file.content, expanding to include surrounding punctuation or an adjacent word to ensure uniqueness."
2. If second attempt also fails: abandon this edit; log claim as 'edit-failed' in summary; do not apply
```

## Idempotence Mechanism

Edit tool requires a unique match. On second run of the skill over stable reality:

- Same fact bundle → same verdicts
- Same contradicted_spans → same `{original}` produced by LLM
- Doc was already edited on first run → `{original}` no longer present in doc
- Edit tool fails loudly with "old_string not found"
- Skill logs as expected no-op, continues

No content hashing needed — the substring-match semantics enforce idempotence naturally.

## Deletion Handling

When `action=delete`:

```
1. Compute expanded-original: include one trailing newline if present in doc-content immediately after {original}
2. Edit with old_string=expanded-original, new_string=""
3. Post-check: if two consecutive blank lines result, do a second Edit removing one
```

This avoids leaving orphan blank lines when a whole paragraph or bullet is removed.

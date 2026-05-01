# Plain text

Unstructured UTF-8 text with no encoded format. The baseline against which every other format adds structural overhead. Use when the payload itself has no structure to encode.

## Metadata

- **File extensions:** `.txt`, no extension
- **MIME type:** `text/plain`
- **Spec:** None beyond character encoding (UTF-8 universally assumed in modern contexts)
- **Primary use cases:** Single-purpose payloads (a UUID, a path, a status flag, a token), README files in legacy ecosystems, log output where structure is noise, scratch notes

## Token efficiency

Optimal — no delimiter overhead. Every byte is content.

## LLM parse reliability

Strong for prose. The model interprets natural language directly without format-specific parsing. Reliability degrades only when the content is itself structured-looking but not in any specific format (e.g., colon-separated key-value lines that the model might misread as markdown or YAML).

## LLM generation reliability

Strong — no constraints to satisfy. The model emits text and the result is valid by definition.

## Modification ergonomics

Strong for text editors. Append, edit, replace — all line-oriented operations work without format constraints.

## Diff and human readability

Strong on both — line-grain diffs, no rendering artifacts.

## Tooling and ecosystem

No format-specific tooling because there's no format. `grep`, `sed`, `awk`, `cat`, every text editor.

## Random access and queryability

Weak — search via `grep`. No structural lookup.

## Scale ceiling

Bound only by file size — text can stream indefinitely. The LLM's context window is the practical limit for "read all at once" workloads.

## Failure mode

Silent — there's nothing to fail because there's nothing to validate. This is plain text's chief liability when the content has implicit structure consumers depend on.

## Claude-specific notes

No Anthropic guidance specific to plain text. Used everywhere as the substrate for prompts, completions, and any unstructured payload.

## Pitfalls and anomalies

- Encoding ambiguity — without a BOM or `Content-Type` header, plain text could be UTF-8, UTF-16, Latin-1, or anything else. UTF-8 is the modern default
- Line endings vary (`\n` Unix, `\r\n` Windows, `\r` legacy Mac) — diff and parse behavior depends on consumer
- Trailing newlines are conventionally required by Unix tools (POSIX defines a "text file" as ending with a newline) — many editors enforce this; some don't
- "Plain text" containing markdown/code/JSON/etc. invites readers to interpret it; if the content is meant literally, surrounding context must say so

## Open questions

- For Claude prompts that mix multiple text payloads, are there documented benefits to using XML tags vs plain text separators (`---`, `===`) vs no separators?
- Is there a token-cost difference between plain text and minimal markdown for the same prose content (e.g., adding `#` headings)?
- What's the recommended escape from plain text when implicit structure starts to matter (most often: switch to markdown)?

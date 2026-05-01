# HTML

Tag-based markup language for browser rendering. Rarely a primary storage format outside web contexts; mentioned here primarily because it competes with markdown in some authoring workflows.

## Metadata

- **File extensions:** `.html`, `.htm`
- **MIME type:** `text/html`
- **Spec:** HTML Living Standard (WHATWG), HTML5 (W3C). Both define the same language with slightly different stewardship models
- **Primary use cases:** Browser-rendered content, email templates, generated documentation (e.g., from markdown via Pandoc or static-site generators), web scraping inputs

## Token efficiency

Among the worst of structured formats — closing tags, attribute syntax, and namespace-style class/id naming all add overhead. Comparable to or worse than XML.

## LLM parse reliability

Acceptable — LLMs handle HTML because their training corpora are HTML-heavy. Tag noise can distract the model from prose content; well-formed HTML fragments are read more reliably than full documents with `<head>`, `<script>`, `<style>` boilerplate.

## LLM generation reliability

Comparable to XML — closing-tag symmetry is a forcing function. Browsers tolerate malformed HTML, which means the LLM can emit subtly wrong markup that still renders, masking errors.

## Modification ergonomics

Weak — same nested-edit problem as XML and JSON, with additional complications from class/id references that may be queried elsewhere (CSS, JS).

## Diff and human readability

Verbose. Pretty-printed HTML is scannable; minified HTML is unreadable. Diffs are line-grain when formatted.

## Tooling and ecosystem

DOM parsers in every browser and language (`BeautifulSoup`, `lxml.html`, `cheerio`). CSS selectors and XPath for query. Heavy linting/formatting ecosystem (`prettier`, `htmlhint`).

## Random access and queryability

Selector-based queries (CSS, XPath) work in-memory after parse. No streaming query without specialized parsers.

## Scale ceiling

Single-document HTML degrades past the megabyte scale for the same reasons as XML.

## Failure mode

Tolerant by design — browsers render malformed HTML rather than refusing it. This is the worst failure-mode profile for content where correctness matters: errors don't surface until much later.

## Claude-specific notes

No Anthropic guidance specific to HTML. When HTML appears in Claude's input (e.g., scraped web content), the standard recommendation in the broader prompt-engineering community is to convert to markdown first, both for token efficiency and to strip browser-rendering noise the model doesn't need.

## Pitfalls and anomalies

- The `<head>` section commonly contains scripts and tracking that are noise for content extraction
- Self-closing-tag handling differs between HTML (`<br>` valid, `<br/>` also valid in HTML5) and XHTML (`<br/>` required)
- Inline event handlers (`onclick="..."`) and inline styles complicate scraping and storage
- Encoding declared in `<meta charset="...">` may conflict with HTTP `Content-Type` header — browsers have priority rules; storage tools may not
- Nested tables (a common 1990s/2000s pattern) defeat most cell-extraction tooling

## Open questions

- For HTML inputs to Claude (e.g., documentation pages), is there a published recommended preprocessing step beyond markdown conversion?
- Does Claude have any documented behavior on raw HTML containing scripts/styles vs cleaned HTML?
- Is there a use case where HTML is a defensible storage choice over markdown for Claude-consumed content? (Likely no.)

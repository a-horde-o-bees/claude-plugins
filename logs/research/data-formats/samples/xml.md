# XML

Tag-delimited markup language with required closing tags and attribute support. Anthropic-recommended for structuring content inside Claude prompts; less common as a file storage format outside specific ecosystems.

## Metadata

- **File extensions:** `.xml` (and many domain-specific variants: `.xhtml`, `.svg`, `.rss`, `.atom`, `.plist`)
- **MIME type:** `application/xml`, `text/xml`
- **Spec:** W3C XML 1.0 (Fifth Edition), 2008. XML 1.1 exists but is rarely used. XPath, XSLT, XSD are companion specs for query/transform/validation
- **Primary use cases:** SOAP web services, enterprise integration, RSS/Atom feeds, SVG and other markup languages, configuration in some ecosystems (Maven, Spring), content delimitation inside Claude prompts

## Token efficiency

Worst of the structured formats — every element pays a closing-tag tax (`<key>value</key>` doubles the key). Attributes mitigate this for short values (`<key value="..."/>`) but most XML in the wild uses element form.

## LLM parse reliability

Excellent — Anthropic specifically recommends XML tags inside prompts because Claude parses them unambiguously. Tag boundaries are explicit, nesting is unambiguous, and the model is trained to recognize the pattern.

## LLM generation reliability

Strong — closing-tag symmetry is a forcing function the model can self-check. The cost is the verbosity, not the reliability.

## Modification ergonomics

Weak for nested edits — same problem as JSON, plus the closing-tag must be kept in sync. XPath-based edit tools exist but are rarely used by agents.

## Diff and human readability

Verbose but scannable. Indentation and tag names give visual structure. Diffs are line-grain when the file is pretty-printed; minified XML diffs are unreadable.

## Tooling and ecosystem

XPath for query, XSLT for transform, XSD/Relax NG/Schematron for validation, lxml/xerces/MSXML for parsing in every major language. The tooling is mature but heavyweight relative to JSON's.

## Random access and queryability

XPath gives in-document query without parsing the whole file in some implementations (streaming XPath via SAX parsers). In practice most consumers parse fully.

## Scale ceiling

Single-document XML degrades at the megabyte scale. Streaming SAX parsers extend the ceiling but are uncommon. Multi-megabyte XML files appear in legacy enterprise contexts; modern systems rarely choose XML at that scale.

## Failure mode

Loud — unclosed tags or attribute syntax errors fail at the parser. Mismatched namespaces are a more subtle hazard but still loud.

## Claude-specific notes

This is the format Anthropic explicitly recommends for one specific use: structuring sections inside a prompt. The guidance:

> XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs. Wrapping each type of content in its own tag (e.g. `<instructions>`, `<context>`, `<input>`) reduces misinterpretation.

For multi-document inputs the docs prescribe:

```xml
<documents>
  <document index="1">
    <source>...</source>
    <document_content>...</document_content>
  </document>
</documents>
```

Source: [Anthropic — Prompting best practices (use-xml-tags)](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags).

This is guidance about prompt structure, not file storage. XML earns its place at the prompt-assembly boundary, not on disk.

## Pitfalls and anomalies

- Namespaces (`xmlns:...`) add complexity most authors don't need but parsers must handle
- DTD and entity references are an attack surface (XXE — external entity injection) — modern parsers should disable external entity resolution
- Whitespace inside elements has multiple handling modes (`xml:space="preserve"` vs default normalization)
- The character data section (`<![CDATA[...]]>`) is the only escape for content containing tag-like characters; misuse produces silently wrong parses
- Mixed content (text and elements interleaved) is allowed but rarely useful; many parsers handle it awkwardly

## Open questions

- For prompt assembly that uses XML tags, what's the actual measured improvement on Claude's adherence to instructions? Anthropic's guidance is qualitative; published quantitative studies were not found.
- Are there cases where XML is a defensible storage format choice over JSON for Claude-consumed content? (Likely no, given JSON's tooling advantage.)
- How does Claude handle XML attributes vs nested elements — any documented preference?

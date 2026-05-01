# Markdown with YAML frontmatter

Composite format pairing a small machine-readable YAML header with a markdown prose body, separated by `---` delimiters. Standard for static-site generators (Jekyll, Hugo, Pelican) and a common pattern for skill descriptors, log entries, and content-with-metadata files.

## Metadata

- **File extensions:** `.md` (the frontmatter is invisible to most renderers that don't recognize it; readers strip and parse it before rendering)
- **MIME type:** `text/markdown`
- **Spec:** No single spec — the convention started with Jekyll (~2008) and propagated. Frontmatter delimited by `---` lines at file start; body is the markdown after the second `---`
- **Primary use cases:** Static-site post metadata, skill descriptors (e.g., Claude Code SKILL.md `description`/`argument-hint`), log entries with type/role frontmatter, any content where prose dominates but a small structured header is needed

## Token efficiency

Same as markdown for the body. Frontmatter adds a small fixed overhead (`---` delimiters + key/value pairs). Net efficient for the use case — the frontmatter avoids inventing a parallel sidecar file.

## LLM parse reliability

LLMs reliably distinguish frontmatter from body. Most parsers (Python `python-frontmatter`, JS `gray-matter`) handle the split deterministically.

## LLM generation reliability

Body generation is markdown-reliable. Frontmatter generation inherits YAML's risks — indent errors, missing colons, type-coercion surprises. Risk is bounded because frontmatter is typically flat and short.

## Modification ergonomics

Strong split: edit the prose body without touching the structured header, or vice versa. Both regions are line-oriented enough for tight Edit-tool replacements.

## Diff and human readability

Strong. Frontmatter is at the top where reviewers see it first; body diffs are markdown-grain.

## Tooling and ecosystem

Ubiquitous frontmatter parsers across languages. Static-site ecosystems (Jekyll, Hugo, Astro, Eleventy, Pelican, MkDocs) all consume the format. Some renderers (raw GitHub markdown view) display frontmatter as a literal `---`-fenced block; most modern ones strip it.

## Random access and queryability

Frontmatter is queryable with low cost — parse the YAML header, ignore the body. This makes frontmatter the natural index for a corpus of markdown files (e.g., "find all skills with `argument-hint: <verb>`").

## Scale ceiling

Same as markdown — bound by context window for the body. Frontmatter should stay small (a few flat keys); large frontmatter is a signal to split into a separate JSON sidecar or move to a different format.

## Failure mode

Frontmatter parse errors fail loudly (most parsers refuse). Body parse errors are silent (it's just markdown). The split is useful: machine-critical content lives in the loud-failing region.

## Claude-specific notes

Heavily used in the Claude Code ecosystem — every `SKILL.md` carries YAML frontmatter with `description`, `argument-hint`, and other metadata Claude reads directly. Plugin manifests reference these by path. The format choice is established convention rather than an Anthropic prescription per se.

## Pitfalls and anomalies

- Frontmatter must start at line 1 — leading whitespace or a BOM breaks detection
- Indented values inside frontmatter inherit YAML's spec ambiguity (e.g., `description: yes` becomes `True` unless quoted)
- Some renderers display frontmatter literally; others strip it — output depends on the consumer
- Long string values in frontmatter (>~80 chars) tempt multi-line YAML scalars (`|`, `>`) which are easy to misindent

## Open questions

- Does Claude Code have documented limits on frontmatter size or structure for skill descriptors?
- Are there published benchmarks on the cost of frontmatter parsing in static-site tooling at scale (10K+ files)?
- What's the project convention for choosing between frontmatter and a sidecar JSON file when the metadata grows nested?

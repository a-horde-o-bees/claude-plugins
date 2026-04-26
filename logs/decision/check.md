---
log-role: reference
---

# Check

Decisions governing the `/ocd:check` skill and its discipline-check dimensions.

## Markdown dimension: deterministic scanner, selective autofix

### Context

The `markdown.md` rule prescribes defensive backticking of characters that markdown/template renderers may interpret — `{}`, `<>`, `*`, `_`. Empirically (session 2026-04-23) these characters cause actual rendering loss only in narrow contexts (attr_list consumption at trailing heading position or trailing table cell), but the rule is broad-defensive so that authors build one simple habit and content stays portable across renderers with varying interpretations. Adjacent blank-line discipline issues (gaps between list items, missing blanks around blocks, more than one blank in a row) cause visible rendering inconsistency and in some cases break list continuity. The ocd plugin needed a programmatic way to detect these violations without requiring human eyeball review of every markdown file after changes.

### Options Considered

**Enforce via CI-only markdownlint** — requires a Node toolchain and externally-authored rules. Rejected: ocd is a Python-first plugin, and the rules we care about are project-specific conventions (PFN-style placeholders are benign in most contexts but risky at a few; auto-fixing literal chars would destroy legitimate attr_list usage).

**Regex-only detection** — simple implementation. Rejected: regex cannot reliably pair matching backticks (inline code with N backticks closes at a matching run of N), track fenced-code-block state across lines, or skip HTML tags and blockquote prefixes. Pairing and state require a line+char state machine.

**Parse markdown to AST and walk it** — CommonMark-spec-compliant, handles all edge cases. Rejected as overkill for the current scope: the scanner must detect literal `*`, `_`, `{`, `}`, `<`, `>` in the *source* text before the markdown parser consumes them, so AST-level analysis of the post-parse tree doesn't help for this specific rule; we'd end up scanning raw text anyway.

**Line+char state machine in pure Python (module `systems/check/_markdown.py`).** Tracks fenced-code-block state across lines, finds inline-backtick-protected spans within each line (with multi-backtick matching), skips HTML-tag-like spans (`<tag>`, `<!--...-->`, autolinks) and blockquote prefixes. Reports violations with file:line:col:char:context. Accepted.

**Auto-fix all violations** — tried. Rejected for literal-character rules: `{target}` → `` `{target}` `` preserves intent, but `{#id .class}` is legitimate attr_list syntax that the fixer would destroy by wrapping in backticks. `-> arrow` or `> 50` math would become `` `->` `` / `` `>` `` mid-prose — ugly and often better rewritten ("proposes to Aaron", "over 50"). Intent requires judgment the fixer cannot make reliably.

**Auto-fix only blank-line rules** — blank-line discipline has no intent ambiguity. Deleting a blank line between list items, inserting a blank before/after a block, collapsing consecutive blanks are all structurally deterministic with no content change. Accepted.

**ALLCAPS rule labels (`LITERAL`, `BLANK-IN-LIST`, …)** — tried briefly. Rejected: labels are visible to agents and humans in CLI output and test assertions, and the ALLCAPS tokens force readers to translate a symbolic handle back into intent. Descriptive labels like `"Markdown - blank line in continuous list"` and `"Markdown - multiple sequential blank lines"` read at a glance, self-describe across dimensions (`Python - …` / `Markdown - …`), and remain stable as rule-string keys — diagnostic output, test-fixture assertions, and future dimension prefixes all compose without a central registry.

### Decision

`ocd-run check markdown [<path>...]` scans for violations with descriptive rule labels (prefix `"Markdown - "` for this dimension; parallel `"Python - "` / `"JS - "` prefixes reserved for future dimensions):

- **`"Markdown - unprotected literal character"`** — unprotected `{`, `}`, `<`, `>` (and `*`, `_` under `--strict`) outside backtick-delimited inline code or fenced code blocks. Blockquote markers and HTML-tag-like spans are exempt. **Never auto-fixed** — the scanner reports file:line:col:char:context for human/agent judgment.
- **`"Markdown - blank line in continuous list"`** — blank line between two same-indent list items with no interrupting block. **Auto-fixable** (delete). **Interrupter exemption:** a heading or blockquote between same-indent items resets list-continuity tracking; the blank lines that must surround those blocks (enforced by the two rules below) are legitimate and not flagged.
- **`"Markdown - missing blank line before block"`** — heading or fenced-code-start preceded immediately by non-blank content. **Auto-fixable** (insert blank before).
- **`"Markdown - missing blank line after heading"`** — heading followed immediately by non-blank content. **Auto-fixable** (insert blank after).
- **`"Markdown - multiple sequential blank lines"`** — more than one blank line in a row. **Auto-fixable** (collapse to one).

`fix_blank_lines(path)` applies the four blank-line fixes in a convergence loop (up to 5 iterations) and is idempotent. Literal-char violations stay reported after autofix for agent/human resolution.

### Consequences

- **Enables:** pre-commit-style check for markdown discipline violations; agents touching markdown can run the lint and see a clean `file:line:col:char` report for judgment-required items
- **Enables:** deterministic auto-cleanup of blank-line discipline issues with one command — no human review needed for those rules
- **Enables:** integration tests pin the lint's behavior against a shared "messy fixture" markdown file that packs every pathological case into one document — a single scan produces many assertions, keeping test time low
- **Constrains:** scanner uses source-level char scanning, not AST walking — a future rule that must distinguish e.g. an emphasis marker that was parsed as emphasis from one that was escaped at the literal layer would require AST analysis. Current rules don't need this
- **Constrains:** `LITERAL` rule is broad-defensive by design — flags `{placeholder}` in prose even though python-markdown's `attr_list` only consumes it at specific block-end positions. This is intentional (portability across renderers and future attr_list behavior changes) but produces what read as false positives to users who know only python-markdown

## Python dimension: AST-based parent-walking scanner

### Context

Tests and helper scripts repeatedly reached for patterns like `Path(__file__).resolve().parents[6]` or `Path(__file__).parent.parent.parent` to locate the project root, a CSS preset, or a neighbor fixture. Each of these couples the caller to its own depth in the directory tree — when the file moves (into a deeper test folder, under a new `integration/` subdirectory, etc.) the count silently breaks or, worse, resolves to the wrong directory. The fix pattern is already established: a shared `project_root` / preset-path fixture in the test conftest, or a constant in the plugin's CLI resolver. But the old forms kept being reintroduced because nothing flagged them in review.

### Options Considered

**Rely on human review** — has already failed. The patterns are small (`.parents[N]` is one line) and slip past without comment.

**Regex-based scan** — fast to implement. Rejected: catches `.parent.parent` but false-positives on `.parent` inside string literals, docstrings, or comments, and can't reliably parse `.parents[N]` out of expressions with whitespace, method chains, or line continuations.

**AST walk (stdlib `ast`)** — parses the file, walks `Attribute`, `Subscript`, `Call` nodes with cheap O(N) over the tree. Strings, comments, and docstrings are excluded by definition. A single `.parent` access is structurally distinguishable from a `.parent.parent` chain (an `Attribute(attr='parent')` whose value is another `Attribute(attr='parent')`), so legitimate and illegitimate forms are separable. Accepted.

### Decision

`ocd-run check python [<path>...]` scans for one rule:

- **`"Python - parent-walking"`** — fires on any `.parent`, `.parents[N]`, or `os.path.dirname(...)` traversal whose expression chain **roots at `__file__`**. Depth is not the threshold; the anti-pattern is a file *anchoring to its own location* to find an ancestor. One blessed file per project may legitimately do so (conftest, plugin entry-point); every other file reads through those anchors.

  Chain-rooting detection walks leftward through `Attribute.value`, `Subscript.value`, and `Call.args[0]` (the chain-extension nodes for the patterns we detect). When the leftmost expression is `Name("__file__")`, the whole chain is flagged — regardless of depth. When it is any other identifier, call, or literal, the chain is ignored: `Path(some_var).parent.parent` is not parent-walking, it is path manipulation.

  De-duplication: a `.parent.parent…` chain reports once on the outermost Attribute, not once per inner `.parent`. `dirname(dirname(...))` calls, by contrast, each report — because each `Call` node is itself an upward traversal.

**Report-only.** No auto-fix. Remediation is situational: reuse a shared conftest fixture, introduce a new one, restructure so the caller takes the anchor as an argument. The scanner cannot make that judgment.

Parse failures (SyntaxError, decode errors) return an empty list for that file — the lint is a lint, not a compiler.

### Allowlist: (rule, path) suppression via CSV

The anti-pattern needs an escape hatch for files whose entire job is to be the anchor. A list of blessed paths lives in `plugins/ocd/systems/check/allowlist.csv` — the CLI loads it, renders each violation's path project-relative, and suppresses any `(rule, path)` matching an `fnmatch` row.

Schema: `rule, pattern, reason`. One row per allowed path pattern. Reasons are surfaced via `--show-allowed` so reviewers can audit the list.

Seed patterns:

- `**/conftest.py` — pytest fixture anchor; other fixtures read through it rather than anchoring themselves
- `plugins/*/run.py` — plugin CLI entry-point; the blessed plugin-root resolver
- `plugins/*/bin/*` — plugin shim entry scripts; must anchor before the Python package is importable
- `plugins/*/systems/*/__main__.py` — per-system CLI dispatchers; locate sibling config (e.g. `allowlist.csv` itself) via their own directory

**Why CSV, not JSON/YAML.** Matches the existing `systems/navigator/paths.csv` convention (the plugin's one precedent for tabular pattern-lists). The data is rectangular; nesting would be fake. YAML adds a dep the plugin doesn't otherwise need.

**Why a single `allowlist.csv`, not per-rule files.** As new rules ship (future `"Python - bare-except"`, `"Python - mutable-default-arg"`, etc.), one file stays coherent. Per-rule files would drift and fragment discovery.

**Why path patterns, not `# noqa` comments.** The allowlist is for files built to be the anchor — a file-level property. If a per-line suppression need emerges (one line in a non-anchor file is defensible), `# noqa: Python - parent-walking` is a clean additive feature.

### Consequences

- **Enables:** regression guard against file-anchored parent-walking re-entering the codebase. Existing anchors pass via the allowlist; new anchors added consciously via a CSV row
- **Enables:** test fixture convention formalized — `fixture_*.*` files co-locate with the tests that consume them (same directory as the `test_*.py`), and a wildcard `*,**/fixture_*.*` allowlist row suppresses them across every dimension. No `fixtures/` folder; file naming is the convention. Pytest's default discovery glob is `test_*.py`, so `fixture_*.py` doesn't need explicit collection exclusion
- **Enables:** `--show-allowed` flag surfaces the suppressed entries so the allowlist itself stays reviewable — no silent exemptions
- **Constrains:** rule is AST-only, so two-line laundering (`here = Path(__file__).parent; root = here.parent`) catches the first line but not the second. Accepted: the first line already flags, so the laundering is cosmetic
- **Constrains:** `.parents[N]` with non-constant N (`.parents[some_var]`) still matches because the subscript's value chain is what's checked, not the index value. `dirname` with bare import name relies on identifier — an unrelated `dirname` function would false-positive if chained to `__file__`; in practice, `os.path.dirname` is the only dirname in use

## Markdown dimension: frontmatter and fenced-code-block opacity

### Context

The literal-character and blank-line rules originally treated every line identically. In practice that meant SKILL.md frontmatter (where `argument-hint: "<verb1 | verb2>"` is the prescribed PFN shape) was flagged on the trailing `>`, and fenced code blocks fired blank-line discipline rules on their interior content. Closing fence lines got classified as block-starts that needed blank lines above; `### foo` inside a code block fired the missing-blank-after-heading rule. Real discipline gaps in templates, rules, and skill files were drowning in detector false positives.

### Options Considered

**Backtick-protect the offending characters at the source** — would suppress the LITERAL rule's hits but cannot solve the structural false-firings (closing-fence-as-block-start), and backticking inside YAML values corrupts what Claude Code displays in the autocomplete. Rejected — symptom-level workaround.

**Update the markdown convention to forbid YAML frontmatter and inner code blocks with these patterns** — would push the work onto every skill author and require ongoing convention maintenance. Rejected — the convention should describe what's correct, not encode the linter's limitations.

**Fix the detector** — make YAML frontmatter opaque to all rules; treat fenced code blocks as a single structural unit (block-boundary rules don't peek inside; fence opener is the only line that participates as a block-start). Accepted.

### Decision

`_markdown.py` adds:

- **`_frontmatter_end_index`** — recognizes `---`-fenced YAML frontmatter at file start; both literal-character scan and blank-line passes skip the contained line range.
- **`_LineState`** dataclass — per-line flags for `in_frontmatter`, `in_fence_body`, `is_fence_open`, `is_fence_close`, plus an `is_structurally_opaque` derived view used by block-boundary rules.
- **Fence opener distinction** — `is_fence_open` is structurally visible (block-start needing blank above); `is_fence_close` and `in_fence_body` are opaque to block-start detection.

Two rules deliberately pierce fence opacity:

- **Markdown - multiple sequential blank lines** — runs of 2+ blank lines fire inside fenced bodies too. Code-block noise is noise.
- **Markdown - blank line at start of fenced block** / **Markdown - blank line at end of fenced block** — new rules forbidding leading/trailing blanks inside the fence body. Auto-fixable (delete) like the other blank-line rules.

### Consequences

- **Enables:** every SKILL.md across the project clears its frontmatter false positives without source changes; templates with fenced ASCII diagrams stop spuriously firing block-discipline rules
- **Enables:** the discipline floor for code blocks now matches prose — multi-blank consolidation everywhere, no leading/trailing blanks in fenced bodies, autofix handles all four blank-line rules uniformly
- **Constrains:** the project's custom rule set has grown beyond what any single community linter (PyMarkdownLnt, markdownlint-cli2) covers — these specific behaviors are not in the standard `MD###` registry. Adoption of a community linter would layer under our custom rules, not replace them. See `logs/idea/Expand check with community linter dimensions.md`

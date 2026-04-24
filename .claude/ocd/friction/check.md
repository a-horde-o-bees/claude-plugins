# check

- 2026-04-24 — markdown lint rule "missing blank line before block" fires on fenced-code-block CLOSING lines, not just openings (scan_blank_lines in `_markdown.py` uses `_is_fenced_code_start(line)` which matches any `^\`\`\`` line regardless of fence-state, so the first ``` of a block and the closing ``` are both treated as block starts); expected: only the opening fence of a fenced code block should require a blank line before; workaround: ignore false positives on pattern docs and other prose-heavy docs with fenced code blocks

"""Markdown literal-character lint.

Enforces the `markdown.md` rule: characters that markdown/template renderers
may interpret — `{}`, `<>`, `*`, `_` — must appear within backtick-delimited
inline code or fenced code blocks when used literally. Without protection,
renderers strip `<>` as HTML tags, template engines and markdown extensions
(e.g. python-markdown's `attr_list`) consume `{}` as variables, and `*`/`_`
trigger emphasis formatting.

Scans `.md` files with a deterministic line+char state machine:

1. Fenced-code-block state — toggles on a line that starts with `` ``` `` or
   `~~~` (3+ matching chars); closed by a line with the same marker char and
   matching or greater count. Lines inside a fence are fully protected.
2. For each non-fenced line, identifies inline-backtick-protected spans using
   multi-backtick matching rules (opener of N backticks pairs with closer of
   exactly N backticks).
3. Walks each character outside protected spans and reports occurrences of
   the target characters with file:line:col and surrounding context.

Strict vs lax:

- Lax (default) — reports only `{`, `}`, `<`, `>`. These are always literal
  violations when unprotected; markdown itself has no syntactic use for them
  in prose.
- Strict — also reports `*` and `_`. These often are intentional emphasis
  (`*italic*`, `**bold**`), so strict mode produces many "review manually"
  flags rather than clean violations.

Import note: this module is intentionally dependency-free — no framework
import, no filesystem discovery side effects — so it can be unit-tested in
isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

LAX_TARGETS = frozenset("{}<>")
STRICT_TARGETS = LAX_TARGETS | frozenset("*_")


@dataclass(frozen=True)
class Violation:
    """One markdown-lint rule violation.

    - rule "LITERAL": unprotected literal target character at (line, col).
      `char` is the offending character.
    - rule "Markdown - blank line in continuous list" / "Markdown - missing blank line before block" / "Markdown - missing blank line after heading" /
      "Markdown - multiple sequential blank lines": blank-line discipline violation. `char` is None;
      `col` is 1 since these are line-granular rules.
    """

    path: Path
    line: int  # 1-indexed
    col: int  # 1-indexed (1 for line-granular rules)
    char: str | None
    context: str  # full line for report framing
    rule: str = "Markdown - unprotected literal character"


def _inline_code_spans(line: str) -> list[tuple[int, int]]:
    """Return [(start, end)) spans where inline backtick protection applies.

    CommonMark inline-code rule: N opening backticks pair with exactly N
    closing backticks, where N is the longest unbroken run at the opener.
    Between them, any content is protected — including other backticks of
    different run lengths.

    Unpaired openers (no matching closer on the line) are not treated as
    protection; the backtick chars themselves pass through as literal text.
    """
    spans: list[tuple[int, int]] = []
    i, n = 0, len(line)
    while i < n:
        if line[i] != "`":
            i += 1
            continue
        # opener run length
        j = i
        while j < n and line[j] == "`":
            j += 1
        opener_len = j - i
        # search for matching closer of exactly opener_len backticks
        k = j
        while k < n:
            if line[k] != "`":
                k += 1
                continue
            m = k
            while m < n and line[m] == "`":
                m += 1
            closer_len = m - k
            if closer_len == opener_len:
                spans.append((i, m))
                i = m
                break
            k = m  # skip this run, continue scanning
        else:
            # no matching closer; opener is literal, advance past it
            i = j
    return spans


def _in_any_span(col: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= col < end for start, end in spans)


def _fence_state_update(
    line: str, in_fence: bool, fence_char: str | None, fence_len: int
) -> tuple[bool, str | None, int]:
    """Advance fenced-code-block state for one line.

    Returns new (in_fence, fence_char, fence_len). Fence rules follow
    CommonMark: opener and closer may be indented up to 3 spaces; closer
    must use the same char and at least as many repeats as opener; closer
    line must have no additional content after the fence chars.
    """
    stripped = line.lstrip(" ")
    # too much leading whitespace disqualifies as a fence line
    if len(line) - len(stripped) >= 4:
        return in_fence, fence_char, fence_len

    for marker_char in ("`", "~"):
        if stripped.startswith(marker_char * 3):
            run = 0
            for ch in stripped:
                if ch == marker_char:
                    run += 1
                else:
                    break
            rest = stripped[run:]
            if not in_fence:
                return True, marker_char, run
            if in_fence and marker_char == fence_char and run >= fence_len:
                # closer line: no content after the fence chars (tabs/spaces OK)
                if rest.strip() == "":
                    return False, None, 0
            break  # matched a fence-marker prefix; don't try the other char
    return in_fence, fence_char, fence_len


def _blockquote_prefix_len(line: str) -> int:
    """Return the length of leading blockquote-marker prefix to skip, or 0.

    Markdown blockquotes start with `>` (optionally after 0-3 spaces), can
    nest (`>>`, `> > `), and typically have a space after each `>`. The `>`
    characters in this prefix are syntactic, not literal.
    """
    i, n = 0, len(line)
    # up to 3 leading spaces
    while i < n and i < 3 and line[i] == " ":
        i += 1
    if i >= n or line[i] != ">":
        return 0
    # consume repeated `>` markers with optional single spaces between them
    while i < n:
        if line[i] == ">":
            i += 1
            if i < n and line[i] == " ":
                i += 1
            continue
        break
    return i


_HTML_TAG_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


def _html_tag_spans(line: str) -> list[tuple[int, int]]:
    """Return [(start, end)) spans that look like balanced HTML tags on this line.

    Conservative heuristic — matches a literal `<` followed by a tag-name char
    or `/` or `!`, up to the matching `>`. This skips `<br>`, `<em>`, `</td>`,
    `<!-- comment -->`, `<td attr="val">`, etc., which are intentional HTML
    passthrough in markdown. Literal `<` or `>` standing alone (math, shell
    redirect, etc.) still flags as a violation.
    """
    spans: list[tuple[int, int]] = []
    i, n = 0, len(line)
    while i < n:
        if line[i] != "<":
            i += 1
            continue
        # check for comment `<!--`
        if line.startswith("<!--", i):
            close = line.find("-->", i + 4)
            if close != -1:
                spans.append((i, close + 3))
                i = close + 3
                continue
            i += 1
            continue
        # check for tag: `<tag`, `</tag`, `<!doctype`
        nxt = i + 1
        if nxt < n and (line[nxt] in _HTML_TAG_CHARS or line[nxt] in ("/", "!")):
            close = line.find(">", nxt)
            if close != -1:
                spans.append((i, close + 1))
                i = close + 1
                continue
        i += 1
    return spans


def scan_literal_chars(path: Path, strict: bool = False) -> list[Violation]:
    """Return LITERAL-rule violations (unprotected target chars) found in path."""
    text = path.read_text(encoding="utf-8", errors="replace")
    targets = STRICT_TARGETS if strict else LAX_TARGETS
    in_fence = False
    fence_char: str | None = None
    fence_len = 0
    violations: list[Violation] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        next_fence, next_char, next_len = _fence_state_update(
            line, in_fence, fence_char, fence_len
        )
        # If this line IS the fence toggle (open or close), protect it fully.
        if next_fence != in_fence or (in_fence and next_fence):
            in_fence, fence_char, fence_len = next_fence, next_char, next_len
            continue

        if in_fence:
            continue

        # Skip blockquote prefix — `>` markers here are syntactic.
        bq_skip = _blockquote_prefix_len(line)
        # Precompute exempt spans: inline code + well-formed HTML tags.
        spans = _inline_code_spans(line) + _html_tag_spans(line)

        for col_idx, ch in enumerate(line):
            if col_idx < bq_skip:
                continue
            if ch not in targets:
                continue
            if _in_any_span(col_idx, spans):
                continue
            # strict-only chars may be escaped with backslash
            if ch in "*_" and col_idx > 0 and line[col_idx - 1] == "\\":
                continue
            violations.append(
                Violation(
                    path=path,
                    line=lineno,
                    col=col_idx + 1,
                    char=ch,
                    context=line,
                    rule="Markdown - unprotected literal character",
                )
            )

    return violations


# ─── Blank-line discipline rules ──────────────────────────────────────────

# Regex-free list-item detection. An "item line" starts (after leading
# whitespace) with one of:
#   - `- `, `* `, `+ ` — unordered marker + space
#   - `N. ` or `N) ` — ordered marker (1+ digits) + terminator + space
# Indent is leading whitespace length; two items at the same indent
# belong to the same list level.
def _classify_list_item(line: str) -> tuple[bool, int]:
    """Return (is_list_item, indent_width). indent_width 0 when not an item."""
    i = 0
    while i < len(line) and line[i] in (" ", "\t"):
        i += 1
    rest = line[i:]
    if not rest:
        return False, 0
    if rest[:2] in ("- ", "* ", "+ "):
        return True, i
    # ordered: digits, '.' or ')', space
    j = 0
    while j < len(rest) and rest[j].isdigit():
        j += 1
    if j > 0 and j + 1 < len(rest) and rest[j] in (".", ")") and rest[j + 1] == " ":
        return True, i
    return False, 0


def _is_heading(line: str) -> bool:
    """ATX heading: 1–6 `#` followed by a space."""
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) >= 4:
        return False  # indented by 4+ spaces = code block, not heading
    i = 0
    while i < len(stripped) and i < 6 and stripped[i] == "#":
        i += 1
    if 1 <= i <= 6 and i < len(stripped) and stripped[i] == " ":
        return True
    return False


def _is_fenced_code_start(line: str) -> bool:
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) >= 4:
        return False
    return stripped.startswith("```") or stripped.startswith("~~~")


def _is_block_start_that_needs_blank_before(line: str) -> bool:
    """Return True when this line begins a block element that requires a
    blank line above (unless the file starts here).

    Scope: headings and fenced-code fences. Tables and thematic breaks
    are out of scope for v1 — add incrementally as the need is proven.
    """
    return _is_heading(line) or _is_fenced_code_start(line)


def scan_blank_lines(path: Path) -> list[Violation]:
    """Return violations for the four blank-line discipline rules:

      Markdown - blank line in continuous list           blank line between same-level list items
      Markdown - missing blank line before block   block element (heading, fence) with no blank above
      Markdown - missing blank line after heading  heading with no blank line after
      Markdown - multiple sequential blank lines      second (or later) blank in a row
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    violations: list[Violation] = []

    # Fence state — don't apply rules inside fenced code.
    in_fence = False
    fence_char: str | None = None
    fence_len = 0

    # Cache: per-line metadata
    # blank[i] = is line i blank?
    blanks = [line.strip() == "" for line in lines]

    # Markdown - blank line in continuous list detection
    # Track: last non-blank line index that was a list item at indent X.
    # When we encounter a new list item at the same indent X after
    # intervening blank(s), flag each blank in between.
    #
    # Interruption exemption: a heading or blockquote between same-indent
    # items (with blank lines around it, as those blocks require) is a
    # legitimate continuation pattern — resets tracking so the blank
    # lines bracketing the interruption are not flagged.
    last_list_item_indent: int | None = None
    blanks_pending: list[int] = []  # 1-indexed line numbers

    for idx, line in enumerate(lines):
        lineno = idx + 1
        # fence toggle update (blank-line rules suspend inside fences)
        next_fence, next_char, next_len = _fence_state_update(
            line, in_fence, fence_char, fence_len
        )
        if next_fence != in_fence:
            in_fence, fence_char, fence_len = next_fence, next_char, next_len
            last_list_item_indent = None
            blanks_pending = []
            continue
        if in_fence:
            continue

        if blanks[idx]:
            blanks_pending.append(lineno)
            continue

        is_item, indent = _classify_list_item(line)

        # Markdown - blank line in continuous list: blank(s) between two list items at same indent
        if (
            is_item
            and last_list_item_indent == indent
            and blanks_pending
        ):
            for blank_line in blanks_pending:
                violations.append(
                    Violation(
                        path=path,
                        line=blank_line,
                        col=1,
                        char=None,
                        context=lines[blank_line - 1],
                        rule="Markdown - blank line in continuous list",
                    )
                )

        # Interruption: a heading or blockquote line between items breaks
        # list continuity for purposes of the blank-in-list rule. The
        # blanks that must surround these blocks are legitimate, not
        # violations, so reset tracking rather than pair across them.
        if _is_heading(line) or _blockquote_prefix_len(line) > 0:
            last_list_item_indent = None
            blanks_pending = []
            continue

        last_list_item_indent = indent if is_item else None
        blanks_pending = []

    # Markdown - multiple sequential blank lines: second blank in a row (and each subsequent blank)
    in_fence = False
    fence_char = None
    fence_len = 0
    prev_blank = False
    for idx, line in enumerate(lines):
        lineno = idx + 1
        next_fence, next_char, next_len = _fence_state_update(
            line, in_fence, fence_char, fence_len
        )
        if next_fence != in_fence:
            in_fence, fence_char, fence_len = next_fence, next_char, next_len
            prev_blank = False
            continue
        if in_fence:
            prev_blank = False
            continue
        is_blank = blanks[idx]
        if is_blank and prev_blank:
            violations.append(
                Violation(
                    path=path,
                    line=lineno,
                    col=1,
                    char=None,
                    context=line,
                    rule="Markdown - multiple sequential blank lines",
                )
            )
        prev_blank = is_blank

    # Markdown - missing blank line before block: block start with non-blank immediately above
    for idx in range(1, len(lines)):
        line = lines[idx]
        if not _is_block_start_that_needs_blank_before(line):
            continue
        prev = lines[idx - 1]
        if prev.strip() != "":
            # fence check — if we're inside a fence, skip
            # (we won't bother replaying the full fence state here; the
            #  check is overly conservative if a fence happens to enclose
            #  this line, but such cases are rare for our content.)
            violations.append(
                Violation(
                    path=path,
                    line=idx + 1,
                    col=1,
                    char=None,
                    context=line,
                    rule="Markdown - missing blank line before block",
                )
            )

    # Markdown - missing blank line after heading: heading followed by non-blank content
    for idx in range(len(lines) - 1):
        if not _is_heading(lines[idx]):
            continue
        next_line = lines[idx + 1]
        if next_line.strip() != "":
            violations.append(
                Violation(
                    path=path,
                    line=idx + 1,
                    col=1,
                    char=None,
                    context=lines[idx],
                    rule="Markdown - missing blank line after heading",
                )
            )

    return violations


def scan_file(path: Path, strict: bool = False) -> list[Violation]:
    """Return all violations (literal-char + blank-line rules) found in path."""
    return scan_literal_chars(path, strict=strict) + scan_blank_lines(path)


def fix_blank_lines(path: Path, max_iterations: int = 5) -> int:
    """Auto-fix blank-line discipline violations in place.

    Applies deterministic fixes:
      Markdown - blank line in continuous list         → delete the offending blank line
      Markdown - multiple sequential blank lines    → delete the extra blank(s), leaving one
      Markdown - missing blank line before block → insert blank line before the block
      Markdown - missing blank line after heading → insert blank line after the heading

    Iterates until stable or max_iterations hit. Returns the number of
    distinct edits applied across all iterations.
    """
    total_edits = 0
    for _ in range(max_iterations):
        violations = scan_blank_lines(path)
        if not violations:
            break

        text = path.read_text(encoding="utf-8", errors="replace")
        had_trailing_newline = text.endswith("\n")
        lines = text.splitlines()

        # Collect per-line intentions.
        delete: set[int] = set()
        insert_before: set[int] = set()
        insert_after: set[int] = set()
        for v in violations:
            if v.rule in ("Markdown - blank line in continuous list", "Markdown - multiple sequential blank lines"):
                delete.add(v.line)
            elif v.rule == "Markdown - missing blank line before block":
                insert_before.add(v.line)
            elif v.rule == "Markdown - missing blank line after heading":
                insert_after.add(v.line)

        edits_this_iter = len(delete) + len(insert_before) + len(insert_after)
        if edits_this_iter == 0:
            break

        # Emit new content.
        new_lines: list[str] = []
        for idx, line in enumerate(lines):
            lineno = idx + 1
            if lineno in delete:
                continue
            if lineno in insert_before:
                new_lines.append("")
            new_lines.append(line)
            if lineno in insert_after:
                new_lines.append("")

        out = "\n".join(new_lines)
        if had_trailing_newline:
            out += "\n"
        if out == text:
            break  # no effective change — converged

        path.write_text(out, encoding="utf-8")
        total_edits += edits_this_iter

    return total_edits


DEFAULT_EXCLUDES = (
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".claude/plugins/cache",
    ".claude/plugins/data",
)


def iter_markdown_files(
    root: Path, excludes: Iterable[str] = DEFAULT_EXCLUDES
) -> list[Path]:
    """Walk root for `.md` files, skipping `excludes` path-segment matches."""
    results: list[Path] = []
    if root.is_file():
        return [root] if root.suffix == ".md" else []
    excludes_set = set(excludes)
    for p in sorted(root.rglob("*.md")):
        if any(part in excludes_set for part in p.relative_to(root).parts):
            continue
        results.append(p)
    return results


def scan_paths(
    paths: Iterable[Path], strict: bool = False
) -> list[Violation]:
    """Scan a collection of files and/or directories; return all violations.

    No auto-fix: violations are reported with full context for an agent or
    human to resolve by judgment. Auto-wrapping would destroy legitimate
    attr_list usage ({#id .class}) and produce jarring monospace spans in
    mid-prose arrows or math-like comparisons.
    """
    all_violations: list[Violation] = []
    for path in paths:
        if path.is_file():
            if path.suffix == ".md":
                all_violations.extend(scan_file(path, strict=strict))
        else:
            for md_path in iter_markdown_files(path):
                all_violations.extend(scan_file(md_path, strict=strict))
    return all_violations

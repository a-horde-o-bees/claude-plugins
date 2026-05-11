"""Python parent-walking lint.

Flags any upward traversal from `__file__` — `.parent`, `.parents[N]`,
or `os.path.dirname(...)` — regardless of chain depth. The anti-pattern
is using a file's own location as an anchor to reach ancestor
directories; one blessed file per project may do this (conftest.py,
plugin CLI entry points, etc.) and everything else reads through it.
The allowlist in `allowlist.csv` names the blessed anchors; the CLI
applies it before printing.

Detection walks the AST for:

  1. `Attribute(attr='parent')` whose chain roots at `__file__` —
     reports once on the OUTERMOST attribute (so `.parent.parent.parent`
     is one violation, not three).
  2. `Subscript` of `.parents` with any integer index whose chain
     roots at `__file__`.
  3. `Call` to `os.path.dirname` (or a bare `dirname` name, covering
     `from os.path import dirname`) whose first argument's chain
     roots at `__file__`.

Chains are considered to root at `__file__` when the leftmost
expression reachable through `Attribute.value`, `Subscript.value`,
or `Call.args[0]` is the Name `__file__`. This catches
`Path(__file__).parent`, `Path(__file__).parents[0]`, and
`os.path.dirname(__file__)` identically. Chains that root at any
other identifier (`Path(some_var).parent`) are ignored — they are
not anchoring to the file's location.

Import note: dependency-free — uses only the stdlib `ast` module —
so it can be unit-tested in isolation.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PARENT_WALKING = "Python - parent-walking"


@dataclass(frozen=True)
class PyViolation:
    """One Python discipline violation with source location and snippet."""

    path: Path
    line: int  # 1-indexed
    col: int  # 1-indexed (ast provides col_offset 0-indexed)
    snippet: str
    rule: str = PARENT_WALKING


def _unparse(node: ast.AST) -> str:
    """Best-effort single-line rendering of a node's source expression."""
    try:
        return ast.unparse(node)
    except Exception:
        return "<unparse failed>"


def _roots_at_file(node: ast.AST) -> bool:
    """Return True when the chain's leftmost expression is `__file__`.

    Walks through `Attribute.value`, `Subscript.value`, and
    `Call.args[0]` — the chain extension points for parent-walking
    patterns — until a Name is reached. Any other base node type
    returns False conservatively.
    """
    current: ast.AST = node
    while True:
        if isinstance(current, ast.Name):
            return current.id == "__file__"
        if isinstance(current, ast.Attribute):
            current = current.value
            continue
        if isinstance(current, ast.Subscript):
            current = current.value
            continue
        if isinstance(current, ast.Call):
            if current.args:
                current = current.args[0]
                continue
            return False
        return False


def _is_dirname_call(node: ast.Call) -> bool:
    """True when node is a call to `os.path.dirname` or bare `dirname`.

    Matches the fully qualified form (`os.path.dirname(x)`) and the
    bare form when `dirname` is imported directly from `os.path`.
    False positives on unrelated `dirname` functions are possible but
    rare — the convention is `os.path.dirname` or `from os.path import
    dirname`.
    """
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "dirname":
        return True
    if isinstance(func, ast.Name) and func.id == "dirname":
        return True
    return False


class _ParentWalkVisitor(ast.NodeVisitor):
    """Collect parent-walking violations from a parsed module.

    Chain de-dup: when a `.parent` Attribute whose chain roots at
    `__file__` is reported, inner `.parent` Attributes in the same
    chain are marked so they do not fire again on descent.
    """

    def __init__(self, path: Path):
        self.path = path
        self.violations: list[PyViolation] = []
        self._seen_ids: set[int] = set()

    def _add(self, node: ast.AST) -> None:
        line = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0) + 1
        snippet = _unparse(node).strip()
        if len(snippet) > 120:
            snippet = snippet[:117] + "..."
        self.violations.append(
            PyViolation(
                path=self.path,
                line=line,
                col=col,
                snippet=snippet,
                rule=PARENT_WALKING,
            )
        )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # Skip if this node is the inner of an already-reported chain.
        if id(node) in self._seen_ids:
            self.generic_visit(node)
            return
        if node.attr == "parent" and _roots_at_file(node):
            self._add(node)
            # Mark inner .parent Attributes so chain de-dup works.
            inner = node.value
            while isinstance(inner, ast.Attribute) and inner.attr == "parent":
                self._seen_ids.add(id(inner))
                inner = inner.value
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if (
            isinstance(node.value, ast.Attribute)
            and node.value.attr == "parents"
            and _roots_at_file(node)
        ):
            # .parents[N] — report for any integer constant index,
            # including 0. (Previously 0 was legitimate under the
            # depth-≥-2 model; under the __file__-rooted model, any
            # upward traversal from __file__ is a violation.)
            self._add(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if _is_dirname_call(node) and node.args and _roots_at_file(node.args[0]):
            self._add(node)
        self.generic_visit(node)


def scan_parent_walking(path: Path) -> list[PyViolation]:
    """Return parent-walking violations found in a Python file.

    Raw scan — does NOT apply the allowlist. CLI and aggregate-scan
    entry points apply the allowlist on top. Files that fail to parse
    (SyntaxError, decode error) return an empty list.
    """
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    visitor = _ParentWalkVisitor(path)
    visitor.visit(tree)
    return visitor.violations


DEFAULT_EXCLUDES = (
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".claude/plugins/cache",
    ".claude/plugins/data",
)


def iter_python_files(
    root: Path, excludes: Iterable[str] = DEFAULT_EXCLUDES
) -> list[Path]:
    """Walk root for `.py` files, skipping path-segment matches in excludes."""
    if root.is_file():
        return [root] if root.suffix == ".py" else []
    excludes_set = set(excludes)
    results: list[Path] = []
    for p in sorted(root.rglob("*.py")):
        if any(part in excludes_set for part in p.relative_to(root).parts):
            continue
        results.append(p)
    return results


def scan_paths(paths: Iterable[Path]) -> list[PyViolation]:
    """Scan a collection of files and/or directories; return raw violations.

    Does NOT apply the allowlist — that is the CLI's responsibility,
    since the CLI knows the project root for relative-path matching.
    """
    all_violations: list[PyViolation] = []
    for path in paths:
        if path.is_file():
            if path.suffix == ".py":
                all_violations.extend(scan_parent_walking(path))
        else:
            for py_path in iter_python_files(path):
                all_violations.extend(scan_parent_walking(py_path))
    return all_violations

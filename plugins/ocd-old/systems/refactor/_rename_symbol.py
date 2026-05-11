"""AST-aware Python identifier rename.

Walks each file's libcst tree and rewrites occurrences of the old name
in three contexts that cover common module-rename cases without
over-matching:

- `import OLD` and `import OLD.sub` — the top-level imported module
- `from OLD import X` and `from OLD.sub import X` — the module-path prefix
- `OLD.attr` when OLD is a Name at the base of an Attribute access

Deliberately excludes bare Name references (local variables or
function/class definitions happening to share the identifier) because
that requires scope analysis. Also excludes string literals, comments,
and any token inside a string or comment — libcst parses these
distinctly from code, so they are structurally immune to substitution.

Each renamed file is rewritten in place. The caller is responsible for
diffing/verifying the result. Non-Python files and files with parse
errors are skipped (reported, not failed) so the tool can run across a
mixed tree.
"""

from dataclasses import dataclass
from pathlib import Path

import libcst as cst


@dataclass
class RenameResult:
    file: Path
    rewritten: bool
    edits: int
    error: str | None = None


class _Renamer(cst.CSTTransformer):
    def __init__(self, old: str, new: str) -> None:
        super().__init__()
        self.old = old
        self.new = new
        self.edits = 0

    def leave_ImportAlias(
        self,
        original_node: cst.ImportAlias,
        updated_node: cst.ImportAlias,
    ) -> cst.ImportAlias:
        new_name = self._rename_name_or_attribute(updated_node.name)
        if new_name is not updated_node.name:
            self.edits += 1
            return updated_node.with_changes(name=new_name)
        return updated_node

    def leave_ImportFrom(
        self,
        original_node: cst.ImportFrom,
        updated_node: cst.ImportFrom,
    ) -> cst.ImportFrom:
        if updated_node.module is None:
            return updated_node
        new_module = self._rename_name_or_attribute(updated_node.module)
        if new_module is not updated_node.module:
            self.edits += 1
            return updated_node.with_changes(module=new_module)
        return updated_node

    def leave_Attribute(
        self,
        original_node: cst.Attribute,
        updated_node: cst.Attribute,
    ) -> cst.Attribute:
        if isinstance(updated_node.value, cst.Name) and updated_node.value.value == self.old:
            self.edits += 1
            return updated_node.with_changes(
                value=cst.Name(value=self.new),
            )
        return updated_node

    def _rename_name_or_attribute(
        self,
        node: cst.BaseExpression,
    ) -> cst.BaseExpression:
        """Rewrite a `Name` or dotted `Attribute` tree whose leftmost part is the old identifier.

        Leaves everything else untouched, including suffix segments.
        """
        if isinstance(node, cst.Name):
            if node.value == self.old:
                return cst.Name(value=self.new)
            return node
        if isinstance(node, cst.Attribute):
            new_value = self._rename_name_or_attribute(node.value)
            if new_value is not node.value:
                return node.with_changes(value=new_value)
        return node


def rename_symbol_in_file(path: Path, old: str, new: str) -> RenameResult:
    """Rename `old` → `new` in a single Python file.

    Parses the file via libcst. Rewrites in place when at least one edit
    fires. Returns a RenameResult summarizing what happened (including
    parse errors, which are non-fatal — the caller decides how to react).
    """
    try:
        source = path.read_text()
    except (OSError, UnicodeDecodeError) as exc:
        return RenameResult(file=path, rewritten=False, edits=0, error=str(exc))

    try:
        tree = cst.parse_module(source)
    except cst.ParserSyntaxError as exc:
        return RenameResult(file=path, rewritten=False, edits=0, error=f"parse error: {exc}")

    renamer = _Renamer(old=old, new=new)
    new_tree = tree.visit(renamer)

    if renamer.edits == 0:
        return RenameResult(file=path, rewritten=False, edits=0)

    path.write_text(new_tree.code)
    return RenameResult(file=path, rewritten=True, edits=renamer.edits)


def rename_symbol_in_scope(
    old: str,
    new: str,
    scope: Path,
) -> list[RenameResult]:
    """Rename `old` → `new` across every .py file under `scope`.

    Walks `scope` recursively, skipping __pycache__ and hidden directories.
    Returns one RenameResult per file touched (or attempted); files with
    zero edits appear with `rewritten=False` so the caller sees the full
    surface scanned.
    """
    results: list[RenameResult] = []
    for py_file in sorted(scope.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        if any(part.startswith(".") for part in py_file.relative_to(scope).parts):
            continue
        results.append(rename_symbol_in_file(py_file, old, new))
    return results

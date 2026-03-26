"""Extract Python symbols from source files without importing them.

Uses ast module for exact line boundaries. No side effects, no dependencies.

Usage:
  python3 scripts/pyextract.py index <file>
  python3 scripts/pyextract.py extract <file> <name>
  python3 scripts/pyextract.py extract <file> <class>.<method>

Index mode: list all top-level functions and classes with line ranges and docstrings.
Extract mode: print a specific function or class body by name.
"""

import ast
import sys
from pathlib import Path


def _get_docstring(node) -> str:
    """Extract first-line docstring from a node, or empty string."""
    ds = ast.get_docstring(node)
    if ds:
        return ds.split("\n")[0]
    return ""


def _decorator_start(node) -> int:
    """Get the earliest line including decorators."""
    if node.decorator_list:
        return node.decorator_list[0].lineno
    return node.lineno


def index_file(source: str, lines: list[str]) -> list[dict]:
    """Return list of symbols with type, name, start, end, docstring."""
    tree = ast.parse(source)
    symbols = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append({
                "type": "function",
                "name": node.name,
                "start": _decorator_start(node),
                "end": node.end_lineno,
                "doc": _get_docstring(node),
            })
        elif isinstance(node, ast.ClassDef):
            symbols.append({
                "type": "class",
                "name": node.name,
                "start": _decorator_start(node),
                "end": node.end_lineno,
                "doc": _get_docstring(node),
            })
            # Index methods within class
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append({
                        "type": "method",
                        "name": f"{node.name}.{child.name}",
                        "start": _decorator_start(child),
                        "end": child.end_lineno,
                        "doc": _get_docstring(child),
                    })

    return symbols


def extract_symbol(source: str, lines: list[str], name: str) -> str | None:
    """Extract source of a named symbol. Supports 'Class.method' notation."""
    tree = ast.parse(source)

    # Check for Class.method notation
    if "." in name:
        class_name, method_name = name.split(".", 1)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == method_name:
                        start = _decorator_start(child) - 1
                        return "\n".join(lines[start:child.end_lineno])
        return None

    # Top-level function or class
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            start = _decorator_start(node) - 1
            return "\n".join(lines[start:node.end_lineno])

    return None


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/pyextract.py index <file>", file=sys.stderr)
        print("       python3 scripts/pyextract.py extract <file> <name>", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    filepath = Path(sys.argv[2])

    if not filepath.exists():
        print(f"File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    source = filepath.read_text()
    lines = source.splitlines()

    if command == "index":
        symbols = index_file(source, lines)
        for s in symbols:
            doc = f"  {s['doc']}" if s["doc"] else ""
            print(f"{s['start']}-{s['end']}  {s['type']:8}  {s['name']}{doc}")

    elif command == "extract":
        if len(sys.argv) < 4:
            print("Usage: python3 scripts/pyextract.py extract <file> <name>", file=sys.stderr)
            sys.exit(1)
        name = sys.argv[3]
        result = extract_symbol(source, lines, name)
        if result is None:
            print(f"Symbol not found: {name}", file=sys.stderr)
            sys.exit(1)
        print(result)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

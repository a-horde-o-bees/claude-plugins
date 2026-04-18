"""System surface scanner.

Inspects a system directory and reports which dormancy-relevant surfaces
it exposes. The dormancy checker and future dimension checkers consume
this inventory to decide which assertions to run.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SystemSurfaces:
    """Inventory of dormancy-relevant surfaces a system folder exposes."""

    path: Path
    name: str
    has_init: bool
    has_status: bool
    has_ready: bool
    has_ensure_ready: bool
    has_mcp_server: bool
    rule_files: tuple[Path, ...]
    has_skill: bool

    @property
    def declares_init_contract(self) -> bool:
        return self.has_init and self.has_status

    @property
    def declares_readiness_interface(self) -> bool:
        return self.has_ready and self.has_ensure_ready


def _module_defines(module_path: Path, names: set[str]) -> set[str]:
    """Return the subset of `names` that appear as top-level function definitions in `module_path`."""
    if not module_path.is_file():
        return set()
    try:
        tree = ast.parse(module_path.read_text())
    except SyntaxError:
        return set()
    found = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    return names & found


def scan_system(system_path: Path) -> SystemSurfaces:
    """Inspect a system folder and return its dormancy-relevant surfaces."""
    init_py = system_path / "_init.py"
    init_contract_names = _module_defines(init_py, {"init", "status", "ready", "ensure_ready"})

    server_py = system_path / "server.py"
    has_mcp_server = server_py.is_file() and "FastMCP" in server_py.read_text()

    rules_dir = system_path / "rules"
    rule_files = (
        tuple(sorted(rules_dir.glob("*.md")))
        if rules_dir.is_dir()
        else ()
    )

    return SystemSurfaces(
        path=system_path,
        name=system_path.name,
        has_init="init" in init_contract_names,
        has_status="status" in init_contract_names,
        has_ready="ready" in init_contract_names,
        has_ensure_ready="ensure_ready" in init_contract_names,
        has_mcp_server=has_mcp_server,
        rule_files=rule_files,
        has_skill=(system_path / "SKILL.md").is_file(),
    )

"""Dormancy checker.

Verifies a system's dormancy surfaces conform to the System Dormancy
discipline — see marketplace-level architecture.md. Runs against any
system with an init contract, exercising its readiness interface and
rule deployment in an isolated project directory. Does not depend on
which plugin owns the system.
"""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from pathlib import Path

import plugin

from ._scanner import SystemSurfaces, scan_system


@dataclass
class CheckResult:
    """Outcome of running one dimension of checks against one system."""

    system: str
    dimension: str
    passes: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


def _run_in_project(project_dir: Path, fn):
    """Call fn() with CLAUDE_PROJECT_DIR pointed at project_dir, restoring prior value after."""
    prior = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = str(project_dir)
    try:
        return fn()
    finally:
        if prior is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = prior


def _check_readiness_dormant(facade, result: CheckResult) -> None:
    if facade.ready():
        result.failures.append("ready() returned True against an empty project dir")
    else:
        result.passes.append("ready() returns False when infrastructure absent")

    try:
        facade.ensure_ready()
    except plugin.NotReadyError as e:
        if str(e).strip():
            result.passes.append("ensure_ready() raises NotReadyError with a non-empty message")
        else:
            result.failures.append("ensure_ready() raised NotReadyError with an empty message")
    except Exception as e:
        result.failures.append(
            f"ensure_ready() raised {type(e).__name__} instead of NotReadyError: {e}"
        )
    else:
        result.failures.append("ensure_ready() did not raise against an empty project dir")


def _check_readiness_operational(facade, result: CheckResult) -> None:
    if facade.ready():
        result.passes.append("ready() returns True after init")
    else:
        result.failures.append("ready() returned False after init")

    try:
        facade.ensure_ready()
        result.passes.append("ensure_ready() does not raise after init")
    except plugin.NotReadyError as e:
        result.failures.append(f"ensure_ready() raised after init: {e}")
    except Exception as e:
        result.failures.append(f"ensure_ready() raised {type(e).__name__} after init: {e}")


def _run_init(init_mod, result: CheckResult) -> bool:
    """Attempt to run the system's init(). Returns True on success."""
    try:
        init_mod.init()
        return True
    except Exception as e:
        result.failures.append(f"init() raised unexpectedly: {type(e).__name__}: {e}")
        return False


def _check_rule_deployment(surfaces: SystemSurfaces, project_dir: Path, result: CheckResult) -> None:
    """Verify rule files deployed to .claude/rules/<plugin>/<system>/ after init."""
    plugin_name = plugin.get_plugin_name(plugin.get_plugin_root())
    deployed_dir = project_dir / ".claude" / "rules" / plugin_name / surfaces.name
    for src in surfaces.rule_files:
        deployed = deployed_dir / src.name
        if not deployed.exists():
            rel = deployed.relative_to(project_dir) if deployed.is_absolute() else deployed
            result.failures.append(f"rule file {src.name} not deployed to {rel} after init")
        elif deployed.read_bytes() != src.read_bytes():
            result.failures.append(f"rule file {src.name} deployed but content diverges from source")
        else:
            result.passes.append(f"rule file {src.name} deploys correctly")


def _check_mcp_dormancy_pattern(surfaces: SystemSurfaces, result: CheckResult) -> None:
    """Static inspection: server.py gates tool registration on a readiness predicate."""
    server_src = (surfaces.path / "server.py").read_text()
    has_ready_call = "ready(" in server_src
    has_dormant_conditional = "if _READY" in server_src or "if READY" in server_src
    has_dormant_instruction = "dormant" in server_src.lower()

    if has_ready_call and has_dormant_conditional:
        result.passes.append("MCP server gates tool registration on readiness predicate")
    else:
        result.failures.append(
            "MCP server.py does not appear to gate tool registration on ready() — "
            "expected a module-level readiness check conditioning @mcp.tool() decorations"
        )

    if has_dormant_instruction:
        result.passes.append("MCP server emits a dormant-state instruction string")
    else:
        result.failures.append(
            "MCP server.py does not mention 'dormant' — expected a dormant-state "
            "instruction pointing to the setup skill"
        )


def check_dormancy(
    surfaces: SystemSurfaces,
    facade_import_path: str,
    init_import_path: str,
    tmp_project_dir: Path,
) -> CheckResult:
    """Run dormancy checks against a system using a temp project directory."""
    result = CheckResult(system=surfaces.name, dimension="dormancy")

    if not surfaces.declares_init_contract:
        result.skipped.append("init-contract absent (no init/status) — dormancy checks do not apply")
        return result

    has_runtime_ops = surfaces.has_mcp_server
    needs_readiness = has_runtime_ops

    if needs_readiness and not surfaces.declares_readiness_interface:
        result.failures.append(
            "system exposes runtime operations (MCP server) but ready()/ensure_ready() "
            "not defined in _init.py — runtime-operational systems must guard their "
            "surface internally"
        )
        return result

    try:
        init_mod = importlib.import_module(init_import_path)
    except ImportError as e:
        result.failures.append(f"init module import failed: {e}")
        return result

    facade = None
    if surfaces.declares_readiness_interface:
        try:
            facade = importlib.import_module(facade_import_path)
        except ImportError as e:
            result.failures.append(f"facade import failed: {e}")
            return result

    if facade is not None:
        _run_in_project(tmp_project_dir, lambda: _check_readiness_dormant(facade, result))

    init_ok = _run_in_project(tmp_project_dir, lambda: _run_init(init_mod, result))

    if not init_ok:
        return result

    if facade is not None:
        _run_in_project(tmp_project_dir, lambda: _check_readiness_operational(facade, result))

    if surfaces.rule_files:
        _check_rule_deployment(surfaces, tmp_project_dir, result)

    if surfaces.has_mcp_server:
        _check_mcp_dormancy_pattern(surfaces, result)

    if not surfaces.declares_readiness_interface and not has_runtime_ops:
        result.skipped.append(
            "deploy-only system — readiness interface not required; "
            "init/status contract is sufficient"
        )

    return result


def check_system(
    system_path: Path,
    facade_import_path: str,
    init_import_path: str,
    tmp_project_dir: Path,
) -> CheckResult:
    """Scan a system folder and run all applicable dimension checks."""
    surfaces = scan_system(system_path)
    return check_dormancy(surfaces, facade_import_path, init_import_path, tmp_project_dir)

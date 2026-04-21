"""Integration tests for framework CLI invocation through run.py.

Verifies framework's user-facing CLI — init, status, permissions
subcommands, and the MCP server launch path — invokes cleanly through
the full import chain: run.py → framework/__main__.py →
framework/__init__.py → importlib.import_module(systems.X._init).

Hook invocations live under tests/plugins/ocd/hooks/<hook>/test_invocation.py
(per-hook home); skill --help coverage was removed as argparse
library behavior (testing.md's overhead rule).
"""

import os
import subprocess
import sys
from pathlib import Path

import framework

PLUGIN_ROOT = framework.get_plugin_root()
RUN_PY = str(PLUGIN_ROOT / "run.py")


def run(module: str, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a module through run.py via subprocess."""
    full_env = os.environ.copy()
    full_env["CLAUDE_PROJECT_DIR"] = str(Path.cwd())
    full_env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, RUN_PY, module, *args],
        capture_output=True, text=True, env=full_env,
    )


class TestFrameworkCLI:
    """Verify framework init/status invoke through run.py and exercise
    the full import chain."""

    def test_status_exits_zero(self) -> None:
        result = run("framework", "status")
        assert result.returncode == 0, result.stderr

    def test_status_shows_plugin_name(self) -> None:
        result = run("framework", "status")
        assert "ocd" in result.stdout

    def test_status_shows_version(self) -> None:
        result = run("framework", "status")
        assert "v0.0." in result.stdout

    def test_status_shows_skills(self) -> None:
        result = run("framework", "status")
        assert "/ocd:navigator" in result.stdout

    def test_init_exits_zero(self, tmp_path: Path) -> None:
        result = run("framework", "init", env={"CLAUDE_PROJECT_DIR": str(tmp_path)})
        assert result.returncode == 0, result.stderr

    def test_invalid_command_exits_nonzero(self) -> None:
        result = run("framework", "bogus")
        assert result.returncode != 0

    def test_init_rejects_permissions_flag(self) -> None:
        result = run("framework", "init", "--permissions")
        assert result.returncode != 0


class TestPermissionsCLI:
    """Verify permissions subcommands invoke through run.py."""

    def test_status_exits_zero(self) -> None:
        result = run("framework", "permissions", "status")
        assert result.returncode == 0, result.stderr

    def test_status_shows_both_scopes(self) -> None:
        result = run("framework", "permissions", "status")
        assert "project" in result.stdout
        assert "user" in result.stdout

    def test_deploy_requires_scope(self) -> None:
        result = run("framework", "permissions", "deploy")
        assert result.returncode != 0

    def test_deploy_exits_zero(self, tmp_path: Path) -> None:
        result = run(
            "framework", "permissions", "deploy", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr
        assert "added" in result.stdout or "already present" in result.stdout

    def test_analyze_exits_zero(self) -> None:
        result = run("framework", "permissions", "analyze")
        assert result.returncode == 0, result.stderr
        assert "health:" in result.stdout

    def test_clean_requires_scope(self) -> None:
        result = run("framework", "permissions", "clean")
        assert result.returncode != 0

    def test_clean_exits_zero(self, tmp_path: Path) -> None:
        result = run(
            "framework", "permissions", "clean", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr


def _run_server_briefly(module: str) -> subprocess.CompletedProcess:
    """Launch an MCP server through run.py with empty stdin and a short timeout.

    A successful import lets the server reach mcp.run() which reads from stdin.
    Empty stdin produces EOF; the FastMCP stdio loop exits cleanly. An import
    failure inside run.py exits non-zero before mcp.run() is reached.
    """
    full_env = os.environ.copy()
    full_env["CLAUDE_PROJECT_DIR"] = str(Path.cwd())
    full_env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    return subprocess.run(
        [sys.executable, RUN_PY, module],
        capture_output=True, text=True, env=full_env,
        input="", timeout=10,
    )


class TestServerInvocation:
    """Each MCP server module loads cleanly through run.py.

    Verifies the launcher establishes package context so relative imports
    inside servers/ resolve. Catches ImportError and missing __init__.py
    issues that unit tests miss because they patch sys.path themselves.
    """

    def test_navigator_loads(self) -> None:
        result = _run_server_briefly("systems.navigator.server")
        assert result.returncode == 0, result.stderr

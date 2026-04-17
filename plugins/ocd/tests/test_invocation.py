"""Integration tests for module invocation through run.py.

Verifies that the plumbing works: run.py can invoke plugin CLI,
hook scripts, and skill CLIs via runpy.run_module. These tests
catch broken import chains, missing __main__.py files, and
sys.path issues that unit tests miss.
"""

import json
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
RUN_PY = str(PLUGIN_ROOT / "run.py")


def run(module: str, *args: str, stdin: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a module through run.py via subprocess."""
    import os
    full_env = os.environ.copy()
    full_env["CLAUDE_PROJECT_DIR"] = str(Path.cwd())
    full_env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, RUN_PY, module, *args],
        capture_output=True, text=True, env=full_env,
        input=stdin,
    )


# ===========================================================================
# Plugin CLI
# ===========================================================================


class TestPluginCLI:
    """Verify plugin init/status invoke through run.py and exercise
    the full import chain: run.py → plugin/__main__.py → plugin/__init__.py
    → importlib.import_module(systems.X._init) → import plugin."""

    def test_status_exits_zero(self) -> None:
        result = run("plugin", "status")
        assert result.returncode == 0, result.stderr

    def test_status_shows_plugin_name(self) -> None:
        result = run("plugin", "status")
        assert "ocd" in result.stdout

    def test_status_shows_version(self) -> None:
        result = run("plugin", "status")
        assert "v0.0." in result.stdout

    def test_status_shows_skills(self) -> None:
        result = run("plugin", "status")
        assert "/ocd:navigator" in result.stdout

    def test_init_exits_zero(self, tmp_path: Path) -> None:
        result = run("plugin", "init", env={"CLAUDE_PROJECT_DIR": str(tmp_path)})
        assert result.returncode == 0, result.stderr

    def test_invalid_command_exits_nonzero(self) -> None:
        result = run("plugin", "bogus")
        assert result.returncode != 0

    def test_init_rejects_permissions_flag(self) -> None:
        result = run("plugin", "init", "--permissions")
        assert result.returncode != 0


class TestPermissionsCLI:
    """Verify permissions subcommands invoke through run.py."""

    def test_status_exits_zero(self) -> None:
        result = run("plugin", "permissions", "status")
        assert result.returncode == 0, result.stderr

    def test_status_shows_both_scopes(self) -> None:
        result = run("plugin", "permissions", "status")
        assert "project" in result.stdout
        assert "user" in result.stdout

    def test_deploy_requires_scope(self) -> None:
        result = run("plugin", "permissions", "deploy")
        assert result.returncode != 0

    def test_deploy_exits_zero(self, tmp_path: Path) -> None:
        result = run(
            "plugin", "permissions", "deploy", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr
        assert "added" in result.stdout or "already present" in result.stdout

    def test_analyze_exits_zero(self) -> None:
        result = run("plugin", "permissions", "analyze")
        assert result.returncode == 0, result.stderr
        assert "health:" in result.stdout

    def test_clean_requires_scope(self) -> None:
        result = run("plugin", "permissions", "clean")
        assert result.returncode != 0

    def test_clean_exits_zero(self, tmp_path: Path) -> None:
        result = run(
            "plugin", "permissions", "clean", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr


# ===========================================================================
# Hook invocation
# ===========================================================================


class TestHookInvocation:
    """Verify hooks load and execute through run.py with correct I/O."""

    def test_auto_approval_blocks_cd(self) -> None:
        hook_input = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "cd /tmp"},
        })
        result = run("hooks.auto_approval", stdin=hook_input)
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output.get("decision") == "block"

    def test_auto_approval_approves_allowed_compound(self) -> None:
        hook_input = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "ls | grep foo"},
        })
        result = run("hooks.auto_approval", stdin=hook_input)
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output.get("hookSpecificOutput", {}).get("permissionDecision") == "allow"

    def test_auto_approval_no_output_for_unknown_tool(self) -> None:
        hook_input = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/test"},
        })
        result = run("hooks.auto_approval", stdin=hook_input)
        assert result.returncode == 0
        assert result.stdout == ""

    def _setup_governance(self, tmp_path: Path, monkeypatch) -> None:
        """Shared governance setup for convention gate tests."""
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        conv_dir = tmp_path / ".claude" / "conventions"
        conv_dir.mkdir(parents=True, exist_ok=True)
        (conv_dir / "python.md").write_text(
            '---\nincludes: "*.py"\n---\n\n# Python\n'
        )

    def test_convention_gate_edit_returns_directive(self, tmp_path: Path, monkeypatch) -> None:
        """Edit injects directive additionalContext — read and conform."""
        self._setup_governance(tmp_path, monkeypatch)
        hook_input = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/app.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "python.md" in ctx
        assert "refactor immediately" in ctx

    def test_convention_gate_write_returns_directive(self, tmp_path: Path, monkeypatch) -> None:
        """Write injects directive additionalContext — same as Edit."""
        self._setup_governance(tmp_path, monkeypatch)
        hook_input = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "src/new_module.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "python.md" in ctx
        assert "refactor immediately" in ctx

    def test_convention_gate_read_returns_informational(self, tmp_path: Path, monkeypatch) -> None:
        """Read injects informational context — no refactor directive."""
        self._setup_governance(tmp_path, monkeypatch)
        hook_input = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "src/app.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "python.md" in ctx
        assert "immediately refactor" not in ctx
        assert "govern" in ctx.lower()

    def test_convention_gate_silent_for_ungoverned_file(self, tmp_path: Path) -> None:
        """Convention gate produces no output for files with no conventions."""
        hook_input = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/app.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        assert result.stdout == ""

    def test_convention_gate_silent_when_no_conventions_dir(self, tmp_path: Path) -> None:
        """Convention gate allows silently when conventions directory doesn't exist."""
        hook_input = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/app.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        assert result.stdout == ""

    def test_convention_gate_excludes_respected(self, tmp_path: Path, monkeypatch) -> None:
        """Convention gate respects excludes — __init__.py skips mcp-server."""
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))

        conv_dir = tmp_path / ".claude" / "conventions"
        conv_dir.mkdir(parents=True, exist_ok=True)
        (conv_dir / "mcp-server.md").write_text(
            '---\nincludes: "servers/*.py"\nexcludes:\n  - "__init__.py"\n---\n\n# MCP\n'
        )

        hook_input = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "servers/__init__.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        assert result.stdout == ""


# ===========================================================================
# Skill CLIs
# ===========================================================================


class TestSkillCLI:
    """Verify skill packages invoke through run.py."""

    def test_navigator_help(self) -> None:
        result = run("systems.navigator", "--help")
        assert result.returncode == 0
        assert "describe" in result.stdout
        assert "scan" in result.stdout

    def test_governance_help(self) -> None:
        result = run("systems.governance", "--help")
        assert result.returncode == 0
        assert "load" in result.stdout
        assert "order" in result.stdout

    def test_governance_for_help(self) -> None:
        result = run("systems.governance", "for", "--help")
        assert result.returncode == 0
        assert "files" in result.stdout


# ===========================================================================
# MCP server invocation
# ===========================================================================


def _run_server_briefly(module: str) -> subprocess.CompletedProcess:
    """Launch an MCP server through run.py with empty stdin and a short timeout.

    A successful import lets the server reach mcp.run() which reads from stdin.
    Empty stdin produces EOF; the FastMCP stdio loop exits cleanly. An import
    failure inside run.py exits non-zero before mcp.run() is reached.
    """
    import os
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



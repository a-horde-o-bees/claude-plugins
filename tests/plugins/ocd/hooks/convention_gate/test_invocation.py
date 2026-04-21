"""Integration tests for convention_gate invoked through run.py.

Exercises the full subprocess path — stdin JSON → run.py dispatcher →
hooks.convention_gate → hookSpecificOutput.additionalContext on stdout.
Validates dispatch, governance lookup across Read/Edit/Write, and
silent-allow behavior when no conventions apply.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import framework
import pytest

PLUGIN_ROOT = framework.get_plugin_root()
RUN_PY = str(PLUGIN_ROOT / "run.py")


def run(module: str, *args: str, stdin: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run a module through run.py via subprocess."""
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


@pytest.fixture
def governance_project(tmp_path: Path) -> Path:
    """Tmp project tree with a single python.md convention matching *.py files."""
    conv_dir = tmp_path / ".claude" / "conventions"
    conv_dir.mkdir(parents=True, exist_ok=True)
    (conv_dir / "python.md").write_text(
        '---\nincludes: "*.py"\n---\n\n# Python\n'
    )
    return tmp_path


class TestConventionGateInvocation:
    """Verify convention_gate loads and executes through run.py with correct I/O."""

    def test_edit_returns_directive(self, governance_project: Path) -> None:
        """Edit injects directive additionalContext — read and conform."""
        hook_input = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/app.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(governance_project)},
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "allow"
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "python.md" in ctx
        assert "refactor immediately" in ctx

    def test_write_returns_directive(self, governance_project: Path) -> None:
        """Write injects directive additionalContext — same as Edit."""
        hook_input = json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "src/new_module.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(governance_project)},
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "python.md" in ctx
        assert "refactor immediately" in ctx

    def test_read_returns_informational(self, governance_project: Path) -> None:
        """Read injects informational context — no refactor directive."""
        hook_input = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "src/app.py"},
        })
        result = run(
            "hooks.convention_gate",
            stdin=hook_input,
            env={"CLAUDE_PROJECT_DIR": str(governance_project)},
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "python.md" in ctx
        assert "immediately refactor" not in ctx
        assert "govern" in ctx.lower()

    def test_silent_for_ungoverned_file(self, tmp_path: Path) -> None:
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

    def test_silent_when_no_conventions_dir(self, tmp_path: Path) -> None:
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

    def test_excludes_respected(self, tmp_path: Path) -> None:
        """Convention gate respects excludes — __init__.py skips mcp-server."""
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

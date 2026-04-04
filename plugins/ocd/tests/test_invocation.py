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
    → importlib.import_module(skills.X._init) → import plugin."""

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
        assert "/ocd-navigator" in result.stdout

    def test_init_exits_zero(self, tmp_path: Path) -> None:
        result = run("plugin", "init", env={"CLAUDE_PROJECT_DIR": str(tmp_path)})
        assert result.returncode == 0, result.stderr

    def test_invalid_command_exits_nonzero(self) -> None:
        result = run("plugin", "bogus")
        assert result.returncode != 0


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

    def test_session_start_writes_plugin_root(self, tmp_path: Path) -> None:
        result = run(
            "hooks.session_start",
            env={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0, result.stderr
        plugin_root_file = tmp_path / ".claude" / "ocd" / ".plugin_root"
        assert plugin_root_file.exists()
        assert plugin_root_file.read_text() == str(PLUGIN_ROOT)


# ===========================================================================
# Skill CLIs
# ===========================================================================


class TestSkillCLI:
    """Verify skill packages invoke through run.py."""

    def test_navigator_help(self) -> None:
        result = run("skills.navigator", "--help")
        assert result.returncode == 0
        assert "describe" in result.stdout
        assert "scan" in result.stdout

    def test_navigator_governance_help(self) -> None:
        result = run("skills.navigator", "governance", "--help")
        assert result.returncode == 0
        assert "governance" in result.stdout

    def test_navigator_governance_for_help(self) -> None:
        result = run("skills.navigator", "governance-for", "--help")
        assert result.returncode == 0
        assert "files" in result.stdout

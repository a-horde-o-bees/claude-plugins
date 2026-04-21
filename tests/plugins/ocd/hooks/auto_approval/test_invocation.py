"""Integration tests for auto_approval invoked through run.py.

Exercises the full subprocess path — stdin JSON → run.py dispatcher →
hooks.auto_approval → hookSpecificOutput on stdout. Complements the
per-module unit tests under this directory (test_command_parsing,
test_hardcoded_blocks, test_pattern_matching, test_path_resolution,
test_settings_enforcement) by validating end-to-end dispatch and
output-schema adherence rather than internal function behavior.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import framework

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


class TestAutoApprovalInvocation:
    """Verify auto_approval loads and executes through run.py with correct I/O."""

    def test_blocks_cd(self) -> None:
        hook_input = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "cd /tmp"},
        })
        result = run("hooks.auto_approval", stdin=hook_input)
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Directory changes" in output["hookSpecificOutput"]["permissionDecisionReason"]

    def test_approves_allowed_compound(self, tmp_path: Path) -> None:
        # Isolate from ambient user settings by pointing HOME + project dir at
        # a scratch tree with a controlled allowlist for ls and grep.
        home = tmp_path / "home"
        home.mkdir()
        project = tmp_path / "project"
        (project / ".claude").mkdir(parents=True)
        (project / ".claude" / "settings.json").write_text(json.dumps({
            "permissions": {"allow": ["Bash(ls:*)", "Bash(grep:*)"]}
        }))
        hook_input = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "ls | grep foo"},
        })
        result = run(
            "hooks.auto_approval",
            stdin=hook_input,
            env={"HOME": str(home), "CLAUDE_PROJECT_DIR": str(project)},
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output.get("hookSpecificOutput", {}).get("permissionDecision") == "allow"

    def test_no_output_for_unknown_tool(self) -> None:
        hook_input = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/test"},
        })
        result = run("hooks.auto_approval", stdin=hook_input)
        assert result.returncode == 0
        assert result.stdout == ""

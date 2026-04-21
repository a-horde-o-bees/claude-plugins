"""Integration tests for .claude/hooks/guard_derived.py.

The hook blocks direct edits to derived files — deployed (rectified
from plugin templates) and propagated (copied by pre-commit). It reads
a PreToolUse JSON payload from stdin, matches `tool_input.file_path`
against guarded patterns, and emits a permissionDecision=deny plus
exit 2 when matched — silent exit 0 otherwise.
"""

import json
import subprocess
from pathlib import Path

import pytest


HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "guard_derived.py"


def _run_hook(file_path: str, cwd: str = "") -> subprocess.CompletedProcess[str]:
    payload = json.dumps({
        "tool_input": {"file_path": file_path},
        "cwd": cwd,
    })
    return subprocess.run(
        ["python3", str(HOOK_PATH)],
        input=payload,
        capture_output=True,
        text=True,
    )


class TestDeployedFilesBlocked:
    @pytest.mark.parametrize("path", [
        ".claude/rules/ocd/design-principles.md",
        ".claude/rules/ocd/testing.md",
        ".claude/conventions/ocd/python.md",
        ".claude/patterns/some-pattern.md",
    ])
    def test_deployed_path_denied(self, path: str):
        result = _run_hook(path)
        assert result.returncode == 2
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny"
        assert path in decision["permissionDecisionReason"]

    def test_log_template_denied(self):
        result = _run_hook(".claude/logs/decision/_template.md")
        assert result.returncode == 2
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny"


class TestPropagatedFrameworkBlocked:
    @pytest.mark.parametrize("path", [
        "plugins/some-other-plugin/plugin/__init__.py",
        "plugins/some-other-plugin/plugin/__main__.py",
    ])
    def test_non_ocd_framework_denied(self, path: str):
        result = _run_hook(path)
        assert result.returncode == 2
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny"

    def test_ocd_framework_allowed(self):
        """Canonical source in ocd/ is editable — regex excludes ocd/."""
        result = _run_hook("plugins/ocd/plugin/__init__.py")
        assert result.returncode == 0
        assert result.stdout == ""


class TestUnguardedPathsAllowed:
    @pytest.mark.parametrize("path", [
        "README.md",
        "plugins/ocd/systems/pdf/_generate.py",
        ".claude/logs/decision/some-entry.md",  # real log entries, not templates
        ".claude/hooks/guard_derived.py",
    ])
    def test_path_allowed(self, path: str):
        result = _run_hook(path)
        assert result.returncode == 0
        assert result.stdout == ""


class TestCwdPrefixStripping:
    def test_absolute_path_with_cwd_prefix_matched(self):
        """Hook strips cwd prefix so absolute file paths still match patterns."""
        result = _run_hook(
            file_path="/tmp/project/.claude/rules/ocd/design.md",
            cwd="/tmp/project",
        )
        assert result.returncode == 2
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny"

    def test_path_without_cwd_prefix_left_unchanged(self):
        result = _run_hook(
            file_path=".claude/rules/ocd/design.md",
            cwd="/unrelated",
        )
        assert result.returncode == 2

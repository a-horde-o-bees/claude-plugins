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
        ".claude/rules/dependencies/process-flow-notation.md",
        ".claude/rules/dependencies/testing.md",
        ".claude/conventions/ocd/python.md",
        "logs/research/_samples-template.md",
    ])
    def test_deployed_path_denied(self, path: str):
        result = _run_hook(path)
        assert result.returncode == 2
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny"
        assert path in decision["permissionDecisionReason"]

    def test_log_template_denied(self):
        result = _run_hook("logs/decision/_template.md")
        assert result.returncode == 2
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny"


class TestPropagatedSkillScriptsBlocked:
    @pytest.mark.parametrize("path", [
        "plugins/skill-authoring/skills/skill-composer/scripts/_environment.py",
        "plugins/skill-authoring/skills/skill-composer/scripts/_deps.py",
        "plugins/some-plugin/skills/some-skill/scripts/_environment.py",
        "plugins/some-plugin/skills/some-skill/scripts/_deps.py",
        "plugins/some-plugin/skills/some-skill/dependencies/process-flow-notation.md",
        "plugins/some-plugin/skills/some-skill/dependencies/file-decomposition.md",
        "plugins/some-plugin/skills/some-skill/dependencies/dependency-resolution.md",
    ])
    def test_skill_scripts_denied(self, path: str):
        """Each skill's scripts/_environment.py, scripts/_deps.py, and
        dependencies/*.md propagated rule canonicals are copies of the
        project-root canonical — block direct edits so changes route
        through the canonical."""
        result = _run_hook(path)
        assert result.returncode == 2
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny"

    def test_skill_scripts_other_files_allowed(self):
        """Only the specific propagated filenames are blocked;
        other skill scripts are skill-owned and editable."""
        result = _run_hook(
            "plugins/skill-authoring/skills/skill-composer/scripts/compose.py"
        )
        assert result.returncode == 0
        assert result.stdout == ""

    def test_project_root_shared_allowed(self):
        """Canonical sources at project root are editable."""
        for path in (
            "shared/scripts/_environment.py",
            "shared/scripts/_deps.py",
            "shared/dependencies/process-flow-notation.md",
            "shared/dependencies/file-decomposition.md",
            "shared/dependencies/dependency-resolution.md",
        ):
            result = _run_hook(path)
            assert result.returncode == 0, f"{path} should be editable"
            assert result.stdout == "", f"{path} should be editable"


class TestUnguardedPathsAllowed:
    @pytest.mark.parametrize("path", [
        "README.md",
        "logs/decision/some-entry.md",  # real log entries, not templates
        ".claude/hooks/guard_derived.py",
        "plugins/ocd-old/systems/pdf/_generate.py",  # legacy code editable
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

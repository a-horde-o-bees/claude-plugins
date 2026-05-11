"""Integration tests for setup CLI invocation through run.py.

Verifies setup's user-facing CLI — meta verbs, per-system dispatch,
permissions subcommands, and the MCP server launch path — invokes
cleanly through the full import chain: run.py →
systems/setup/__main__.py → systems/setup/__init__.py →
importlib.import_module(systems.X.setup).

Hook invocations live under tests/plugins/ocd/hooks/<hook>/test_invocation.py
(per-hook home); skill --help coverage was removed as argparse
library behavior (testing.md's overhead rule).
"""

import os
import subprocess
import sys
from pathlib import Path

from dependencies import environment

PLUGIN_ROOT = environment.get_plugin_root()
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


class TestSetupSkillUsage:
    """`ocd-run setup` (no args) prints usage including migrated systems."""

    def test_no_args_exits_zero(self) -> None:
        result = run("setup")
        assert result.returncode == 0, result.stderr

    def test_no_args_lists_meta_verbs(self) -> None:
        result = run("setup")
        assert "list" in result.stdout
        assert "status" in result.stdout
        # permissions is a regular migrated system, not a meta verb
        assert "permissions" in result.stdout

    def test_no_args_lists_migrated_systems(self) -> None:
        result = run("setup")
        # Rules is the first migrated system.
        assert "rules" in result.stdout

    def test_unknown_verb_exits_nonzero(self) -> None:
        result = run("setup", "bogus")
        assert result.returncode != 0
        assert "Unknown" in result.stderr or "unknown" in result.stderr.lower()


class TestSetupMetaVerbs:
    """Meta verbs list and status aggregate across migrated systems."""

    def test_list_lists_systems(self) -> None:
        result = run("setup", "list")
        assert result.returncode == 0, result.stderr
        assert "rules" in result.stdout
        assert "permissions" in result.stdout

    def test_status_reports_each_system(self) -> None:
        result = run("setup", "status")
        assert result.returncode == 0, result.stderr
        assert "Rules" in result.stdout or "rules" in result.stdout.lower()


class TestSetupSystemDispatch:
    """`ocd-run setup <system>` and `<system> <verb>` dispatch correctly."""

    def test_system_usage_for_rules(self) -> None:
        result = run("setup", "rules")
        assert result.returncode == 0, result.stderr
        assert "rules" in result.stdout.lower()
        assert "install" in result.stdout
        assert "uninstall" in result.stdout

    def test_unknown_system_exits_nonzero(self) -> None:
        result = run("setup", "not_a_real_system")
        assert result.returncode != 0

    def test_install_at_project_scope(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "rules", "install", "honesty", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert (git_project_dir / ".claude/rules/ocd/honesty.md").is_file()

    def test_install_requires_scope(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "rules", "install", "honesty",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode != 0

    def test_uninstall_at_project_scope(self, git_project_dir: Path) -> None:
        run(
            "setup", "rules", "install", "honesty", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        result = run(
            "setup", "rules", "uninstall", "honesty", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert not (git_project_dir / ".claude/rules/ocd/honesty.md").exists()

    def test_status_dispatches_to_system(self) -> None:
        result = run("setup", "rules", "status")
        assert result.returncode == 0, result.stderr

    def test_list_dispatches_to_system(self) -> None:
        result = run("setup", "rules", "list")
        assert result.returncode == 0, result.stderr
        assert "honesty" in result.stdout
        assert "verified evidence" in result.stdout

    def test_show_dispatches_to_system(self) -> None:
        result = run("setup", "rules", "show", "honesty")
        assert result.returncode == 0, result.stderr
        assert "# Honesty" in result.stdout
        assert "tagline:" not in result.stdout

    def test_show_requires_target(self) -> None:
        result = run("setup", "rules", "show")
        assert result.returncode != 0

    def test_show_unknown_target_exits_nonzero(self) -> None:
        result = run("setup", "rules", "show", "not-a-rule")
        assert result.returncode != 0
        assert "unknown" in (result.stdout + result.stderr).lower()

    def test_unknown_verb_exits_nonzero(self) -> None:
        result = run("setup", "rules", "bogus")
        assert result.returncode != 0


class TestPermissionsCLI:
    """Verify permissions subcommands invoke through run.py."""

    def test_status_exits_zero(self) -> None:
        result = run("setup", "permissions", "status")
        assert result.returncode == 0, result.stderr

    def test_status_shows_both_scopes(self) -> None:
        result = run("setup", "permissions", "status")
        assert "project" in result.stdout
        assert "user" in result.stdout

    def test_deploy_requires_scope(self) -> None:
        result = run("setup", "permissions", "deploy")
        assert result.returncode != 0

    def test_deploy_exits_zero(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "permissions", "deploy", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert "added" in result.stdout or "already present" in result.stdout

    def test_analyze_exits_zero(self) -> None:
        result = run("setup", "permissions", "analyze")
        assert result.returncode == 0, result.stderr
        assert "health:" in result.stdout

    def test_clean_requires_scope(self) -> None:
        result = run("setup", "permissions", "clean")
        assert result.returncode != 0

    def test_clean_exits_zero(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "permissions", "clean", "--scope", "project",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr


def _run_server_briefly(module: str) -> subprocess.CompletedProcess:
    """Launch an MCP server through run.py with empty stdin and a short timeout."""
    full_env = os.environ.copy()
    full_env["CLAUDE_PROJECT_DIR"] = str(Path.cwd())
    full_env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    return subprocess.run(
        [sys.executable, RUN_PY, module],
        capture_output=True, text=True, env=full_env,
        input="", timeout=10,
    )


class TestServerInvocation:
    """Each MCP server module loads cleanly through run.py."""

    def test_navigator_loads(self) -> None:
        result = _run_server_briefly("systems.navigator.server")
        assert result.returncode == 0, result.stderr

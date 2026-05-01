"""Integration tests for setup CLI invocation through run.py.

Verifies setup's user-facing CLI — init, status, permissions
subcommands, and the MCP server launch path — invokes cleanly through
the full import chain: run.py → systems/setup/__main__.py →
systems/setup/__init__.py → importlib.import_module(systems.X._init).

Hook invocations live under tests/plugins/ocd/hooks/<hook>/test_invocation.py
(per-hook home); skill --help coverage was removed as argparse
library behavior (testing.md's overhead rule).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from tools import environment

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


class TestSetupCLI:
    """Verify setup init/status invoke through run.py and exercise
    the full import chain."""

    def test_status_exits_zero(self) -> None:
        result = run("setup", "status")
        assert result.returncode == 0, result.stderr

    def test_status_shows_plugin_name(self) -> None:
        result = run("setup", "status")
        assert "ocd" in result.stdout

    def test_status_shows_version(self) -> None:
        result = run("setup", "status")
        assert re.search(r"v\d+\.\d+\.\d+", result.stdout)

    def test_status_shows_skills(self) -> None:
        result = run("setup", "status")
        assert "/ocd:navigator" in result.stdout

    def test_init_exits_zero(self, git_project_dir: Path) -> None:
        result = run("setup", "init", env={"CLAUDE_PROJECT_DIR": str(git_project_dir)})
        assert result.returncode == 0, result.stderr

    def test_invalid_command_exits_nonzero(self) -> None:
        result = run("setup", "bogus")
        assert result.returncode != 0

    def test_init_rejects_permissions_flag(self) -> None:
        result = run("setup", "init", "--permissions")
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


class TestOptInInit:
    """Opt-in surface on `setup init` — --all, --systems, first-time
    default, and mutual-exclusivity validation."""

    def _config(self, project_dir: Path) -> Path:
        return project_dir / ".claude" / "ocd" / "enabled-systems.json"

    def test_first_init_enables_all_and_writes_config(self, git_project_dir: Path) -> None:
        result = run("setup", "init", env={"CLAUDE_PROJECT_DIR": str(git_project_dir)})
        assert result.returncode == 0, result.stderr
        config = self._config(git_project_dir)
        assert config.is_file()
        import json
        data = json.loads(config.read_text())
        assert "rules" in data["enabled"]
        assert "conventions" in data["enabled"]

    def test_init_all_enables_every_system(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "init", "--all",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        import json
        enabled = json.loads(self._config(git_project_dir).read_text())["enabled"]
        assert set(enabled) >= {"rules", "conventions", "log", "navigator"}

    def test_init_systems_limits_to_list(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "init", "--systems", "rules,conventions",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        import json
        enabled = json.loads(self._config(git_project_dir).read_text())["enabled"]
        assert sorted(enabled) == ["conventions", "rules"]
        # Only enabled systems' deploys exist
        assert (git_project_dir / ".claude" / "rules" / "ocd").is_dir()
        assert (git_project_dir / ".claude" / "conventions" / "ocd").is_dir()
        assert not (git_project_dir / "logs" / "decision").is_dir()

    def test_init_systems_rejects_unknown(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "init", "--systems", "rules,not_a_real_system",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0  # orchestration prints + returns, not exit(1)
        assert "Unknown system" in result.stdout

    def test_all_and_systems_mutually_exclusive(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "init", "--all", "--systems", "rules",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode != 0
        assert "mutually exclusive" in result.stderr

    def test_subsequent_init_respects_persisted_selection(self, git_project_dir: Path) -> None:
        """First init with --systems; second init without flags deploys
        only what was persisted, not everything."""
        run(
            "setup", "init", "--systems", "rules",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        result = run("setup", "init", env={"CLAUDE_PROJECT_DIR": str(git_project_dir)})
        assert result.returncode == 0, result.stderr
        assert (git_project_dir / ".claude" / "rules" / "ocd").is_dir()
        assert not (git_project_dir / ".claude" / "conventions" / "ocd").is_dir()

    def test_disabled_tree_pruned_when_selection_shrinks(self, git_project_dir: Path) -> None:
        """Init with --all, then init with --systems limited — the
        removed systems' deploy trees are cleaned up."""
        run("setup", "init", "--all", env={"CLAUDE_PROJECT_DIR": str(git_project_dir)})
        assert (git_project_dir / ".claude" / "conventions" / "ocd").is_dir()

        result = run(
            "setup", "init", "--systems", "rules",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert not (git_project_dir / ".claude" / "conventions" / "ocd").is_dir()


class TestOptInEnableDisable:
    """enable/disable verbs toggle a single system and reconcile disk state."""

    def test_disable_removes_deployed_tree(self, git_project_dir: Path) -> None:
        run("setup", "init", "--all", env={"CLAUDE_PROJECT_DIR": str(git_project_dir)})
        assert (git_project_dir / ".claude" / "rules" / "ocd").is_dir()

        result = run(
            "setup", "disable", "rules",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert not (git_project_dir / ".claude" / "rules" / "ocd").is_dir()

        import json
        enabled = json.loads(
            (git_project_dir / ".claude" / "ocd" / "enabled-systems.json").read_text(),
        )["enabled"]
        assert "rules" not in enabled

    def test_enable_restores_deployed_tree(self, git_project_dir: Path) -> None:
        run(
            "setup", "init", "--systems", "conventions",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert not (git_project_dir / ".claude" / "rules" / "ocd").is_dir()

        result = run(
            "setup", "enable", "rules",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert (git_project_dir / ".claude" / "rules" / "ocd").is_dir()

    def test_enable_unknown_system(self, git_project_dir: Path) -> None:
        result = run(
            "setup", "enable", "not_a_real_system",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0
        assert "Unknown system" in result.stdout

    def test_disable_already_disabled_is_noop(self, git_project_dir: Path) -> None:
        run(
            "setup", "init", "--systems", "conventions",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        result = run(
            "setup", "disable", "rules",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert "already disabled" in result.stdout


class TestOptInStatus:
    """Status reflects opt-in state per system."""

    def test_status_marks_enabled_systems(self, git_project_dir: Path) -> None:
        run(
            "setup", "init", "--systems", "rules",
            env={"CLAUDE_PROJECT_DIR": str(git_project_dir)},
        )
        result = run("setup", "status", env={"CLAUDE_PROJECT_DIR": str(git_project_dir)})
        assert result.returncode == 0, result.stderr
        assert "Rules [enabled]" in result.stdout
        assert "[disabled]" in result.stdout

"""Integration tests for `ocd-run` — exercise the user-facing entry point.

These tests subprocess the actual bin wrapper rather than importing modules
directly. Failure modes they catch that unit tests don't:

- `bin/ocd-run` venv-resolution fallback chain
- `run.py` module promotion (bare name → `systems.<name>`; dotted names stay as-is)
- Argparse dispatch from the real CLI surface
- Exit-code propagation through the bash wrapper

Representative — not exhaustive. Per-verb coverage across every system is a
separate initiative; this suite validates dispatch mechanics against each
invocation class so bin-wrapper and run.py regressions surface before release.
"""

import json
import subprocess
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[4] / "plugins" / "ocd"
OCD_RUN = PLUGIN_ROOT / "bin" / "ocd-run"


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(OCD_RUN), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


class TestEntryPoint:
    def test_bin_is_executable(self) -> None:
        assert OCD_RUN.is_file()
        assert OCD_RUN.stat().st_mode & 0o111, "bin/ocd-run must be executable"

    def test_no_args_exits_nonzero(self) -> None:
        """With no module name, run.py crashes at argv[1] access — bin wrapper
        should surface that non-zero exit rather than silently succeed."""
        result = _run()
        assert result.returncode != 0


class TestModulePromotion:
    """run.py auto-promotes bare names to `systems.<name>` when that
    submodule exists. Dotted names pass through unchanged.
    """

    def test_bare_name_promoted_to_systems(self) -> None:
        """`ocd-run framework status` resolves to `systems.framework`."""
        result = _run("framework", "status")
        assert result.returncode == 0, result.stderr
        # Output shape: plugin header + per-system sections + skills list
        assert "ocd" in result.stdout.lower()

    def test_unknown_bare_name_fails(self) -> None:
        """Bare name with no matching systems.<X> module fails — run.py falls
        through to runpy which raises ModuleNotFoundError."""
        result = _run("nonexistent_system")
        assert result.returncode != 0
        assert (
            "nonexistent_system" in (result.stderr + result.stdout).lower()
            or "modulenotfound" in (result.stderr + result.stdout).lower()
        )


class TestSubsystemDispatch:
    """Verbs with internal argparse subparsers route correctly through the
    wrapper. Chosen for deterministic output and no destructive side effects.
    """

    def test_sandbox_sibling_path(self) -> None:
        """`ocd-run sandbox sibling-path <name>` prints the computed sibling
        path. Exercises argparse subparser dispatch + path composition.
        """
        result = _run("sandbox", "sibling-path", "tmp-integration-probe")
        assert result.returncode == 0, result.stderr
        printed = result.stdout.strip()
        # Sibling path is <parent>/<project>--<name>; just check shape.
        assert "--tmp-integration-probe" in printed

    def test_sandbox_cleanup_inventory_emits_json(self) -> None:
        """`ocd-run sandbox cleanup inventory` emits parseable JSON on stdout.
        Exercises a nested-subparser verb and verifies contract.
        """
        result = _run("sandbox", "cleanup", "inventory")
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert "siblings" in payload
        assert "worktrees" in payload
        assert isinstance(payload["siblings"], list)
        assert isinstance(payload["worktrees"], list)

    def test_framework_status_scopes_to_system(self) -> None:
        """`ocd-run framework status --system <name>` narrows the report to one
        subsystem. Exercises argparse flag marshaling through the bash layer.
        """
        result = _run("framework", "status", "--system", "conventions")
        assert result.returncode == 0, result.stderr
        assert "Conventions" in result.stdout

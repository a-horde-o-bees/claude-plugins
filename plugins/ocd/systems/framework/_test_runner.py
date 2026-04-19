"""Test runner orchestration.

Discovers project and per-plugin test suites in the current working
directory, runs pytest for each suite under its resolved venv, compiles
a report, and returns the highest exit code. Stateless — does not create
or clean up any filesystem or git state.

Worktree isolation is a separate concern handled by `/ocd:sandbox tests`,
which creates a detached worktree at a ref and invokes `ocd-run tests`
inside it. Running `ocd-run tests` directly (without sandbox) exercises
the current working tree — useful for fast dev feedback.
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from . import _test_discovery


@dataclass
class SuiteResult:
    name: str
    passed: int
    failed: int
    errors: int
    skipped: int
    exit_code: int
    summary_lines: list[str] = field(default_factory=list)


def tests_run(
    plugin_filter: str | None = None,
    project_only: bool = False,
) -> int:
    """Run discovered test suites in the current working directory.

    Returns the highest pytest exit code across suites — 0 when every
    suite passes, non-zero when any suite fails or errors.
    """
    cwd = Path.cwd()
    suites = _test_discovery.discover_suites(cwd, plugin_filter, project_only)
    if not suites:
        _print_no_suites(plugin_filter, project_only)
        return 0

    results = [_run_suite(suite, cwd) for suite in suites]
    _print_report(results)
    return max(r.exit_code for r in results)


def test_runner_main() -> int:
    """CLI entry — parse args and dispatch to `tests_run`."""
    parser = argparse.ArgumentParser(
        prog="ocd-run tests",
        description="Run project and plugin test suites in the current working directory.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--plugin",
        help="Run only the named plugin's tests",
    )
    group.add_argument(
        "--project",
        action="store_true",
        help="Run only the project-level tests/ suite",
    )
    args = parser.parse_args()
    return tests_run(plugin_filter=args.plugin, project_only=args.project)


def _run_suite(suite: _test_discovery.Suite, cwd: Path) -> SuiteResult:
    print(f"\n=== {suite.name} ===", flush=True)
    args = [str(suite.venv), "-m", "pytest", str(suite.rel_path), "-v"]
    if suite.pytest_ini is not None:
        args.extend(["-c", str(suite.pytest_ini)])

    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    combined = result.stdout + result.stderr
    sys.stdout.write(combined)
    sys.stdout.flush()

    return _parse_pytest_output(suite.name, combined, result.returncode)


def _parse_pytest_output(name: str, output: str, exit_code: int) -> SuiteResult:
    passed = _count_outcome(output, "passed")
    failed = _count_outcome(output, "failed")
    errors = _count_outcome(output, "error") + _count_outcome(output, "errors")
    skipped = _count_outcome(output, "skipped")

    summary_lines = [line for line in output.splitlines() if line.startswith("FAILED")]

    return SuiteResult(
        name=name,
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
        exit_code=exit_code,
        summary_lines=summary_lines,
    )


def _count_outcome(output: str, label: str) -> int:
    """Extract count from pytest's final summary line.

    Pytest summary looks like: `=== 354 passed, 16 failed, 7 skipped in 3.78s ===`
    """
    pattern = rf"(\d+)\s+{label}\b"
    matches = re.findall(pattern, output)
    if not matches:
        return 0
    return int(matches[-1])


def _print_no_suites(plugin_filter: str | None, project_only: bool) -> None:
    if plugin_filter is not None:
        print(f"No suite found for plugin `{plugin_filter}`")
    elif project_only:
        print("No project tests/ directory found")
    else:
        print("No suites discovered")


def _print_report(results: list[SuiteResult]) -> None:
    print("\n=== Summary ===")
    total_passed = total_failed = total_errors = total_skipped = 0
    for r in results:
        print(_format_counts(r.name, r.passed, r.failed, r.errors, r.skipped))
        total_passed += r.passed
        total_failed += r.failed
        total_errors += r.errors
        total_skipped += r.skipped
    if len(results) > 1:
        print(_format_counts("total", total_passed, total_failed, total_errors, total_skipped))

    failures = [line for r in results for line in r.summary_lines]
    if failures:
        print("\nFailing tests:")
        for line in failures:
            print(f"  {line}")

    verdict = "PASS" if total_failed == 0 and total_errors == 0 else "FAIL"
    print(f"\nVerdict: {verdict}")


def _format_counts(name: str, passed: int, failed: int, errors: int, skipped: int) -> str:
    return f"{name} — {passed} passed, {failed} failed, {errors} errors, {skipped} skipped"

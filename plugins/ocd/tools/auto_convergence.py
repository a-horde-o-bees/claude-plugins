"""Deterministic convergence loop operations for --auto skill dispatch.

Handles git mechanics (precondition check, baseline capture, convergence
detection) so skill workflows delegate only the non-deterministic inner
workflow execution to agents.

Usage:
    python3 run.py tools.auto_convergence precondition
    python3 run.py tools.auto_convergence check --baseline <hash> [--prev-diff <file>]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        capture_output=True, text=True,
    )


def precondition() -> None:
    """Verify clean working tree and print baseline hash.

    Exits 1 with message if tree is dirty. Prints baseline hash on success.
    """
    status = _git("status", "--porcelain")
    if status.stdout.strip():
        print("dirty — commit pending changes before running --auto", file=sys.stderr)
        sys.exit(1)

    baseline = _git("rev-parse", "HEAD")
    if baseline.returncode != 0:
        print(f"git error: {baseline.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    print(baseline.stdout.strip())


def check(baseline: str, prev_diff_file: str | None = None) -> None:
    """Check convergence against baseline.

    Captures current diff against baseline. If prev_diff_file provided,
    compares current diff to previous — outputs "converged" if identical,
    "not-converged" if different. Always writes current diff to a temp
    file and prints its path for the next iteration.

    Output format (two lines):
        converged|not-converged|first-iteration
        <path-to-current-diff-file>
    """
    diff = _git("diff", baseline, "--stat")
    current_diff = diff.stdout

    # Write current diff to temp file for next iteration comparison
    current_file = tempfile.NamedTemporaryFile(
        mode="w", prefix="auto-diff-", suffix=".txt", delete=False,
    )
    current_file.write(current_diff)
    current_file.close()

    if prev_diff_file is None:
        print("first-iteration")
    else:
        prev_diff = Path(prev_diff_file).read_text()
        if current_diff == prev_diff:
            print("converged")
        else:
            print("not-converged")

    print(current_file.name)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="auto_convergence",
        description="Deterministic convergence loop operations for --auto dispatch.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser(
        "precondition",
        help="Verify clean tree, print baseline hash",
    )

    check_p = commands.add_parser(
        "check",
        help="Check convergence against baseline",
    )
    check_p.add_argument("--baseline", required=True, help="Baseline commit hash")
    check_p.add_argument("--prev-diff", default=None, help="Path to previous diff file")

    args = parser.parse_args()

    if args.command == "precondition":
        precondition()
    elif args.command == "check":
        check(args.baseline, args.prev_diff)


if __name__ == "__main__":
    main()

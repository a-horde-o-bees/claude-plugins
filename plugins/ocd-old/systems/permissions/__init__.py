"""Permissions subsystem facade.

Public interface for auto-approve pattern management — coverage report,
deploy recommended patterns, analyze cross-scope health, clean redundant
entries. Permissions has its own verb shape (status / deploy / analyze
/ clean) rather than the standard install / uninstall — exposed via
`dispatch(verb, args)` so the setup CLI routes every verb through this
system rather than assuming a fixed contract.
"""

from __future__ import annotations

import argparse
import sys

from ._operations import *  # noqa: F403
from ._init import *  # noqa: F403
from . import _operations


def purpose() -> str:
    """One-line purpose statement for setup-level discovery."""
    return (
        "Auto-approve permission patterns — deploy, analyze, and clean "
        "recommended Bash and tool allow-list entries across user and project scopes."
    )


def verbs() -> list[dict]:
    """Verb catalog for setup-level usage rendering."""
    return [
        {"name": "status", "description": "coverage report across both scopes"},
        {"name": "deploy", "description": "merge recommended patterns into one scope"},
        {"name": "analyze", "description": "cross-scope health analysis (redundancy, broad patterns, contradictions)"},
        {"name": "clean", "description": "remove recommended entries from scope that are redundant with the other"},
    ]


def dispatch(verb: str, args: list[str]) -> None:
    """Route permissions verbs to their handlers.

    Permissions does not fit the standard install / uninstall contract —
    its operations are deploy (merge into a scope) and clean (remove
    redundant), with status and analyze as read-only views. Dispatch
    parses each verb's argparse and calls the matching CLI-print
    function in `_operations`.
    """
    if verb == "status":
        argparse.ArgumentParser(prog="setup permissions status").parse_args(args)
        _operations.run_permissions_status()
        return

    if verb == "deploy":
        parser = argparse.ArgumentParser(prog="setup permissions deploy")
        parser.add_argument("--scope", required=True, choices=["user", "project"])
        parsed = parser.parse_args(args)
        _operations.run_permissions_deploy(scope=parsed.scope)
        return

    if verb == "analyze":
        argparse.ArgumentParser(prog="setup permissions analyze").parse_args(args)
        _operations.run_permissions_analyze()
        return

    if verb == "clean":
        parser = argparse.ArgumentParser(prog="setup permissions clean")
        parser.add_argument("--scope", required=True, choices=["user", "project"])
        parsed = parser.parse_args(args)
        _operations.run_permissions_clean(scope=parsed.scope)
        return

    print(f"Unknown verb '{verb}' for permissions.", file=sys.stderr)
    print("Available verbs: status, deploy, analyze, clean", file=sys.stderr)
    sys.exit(1)

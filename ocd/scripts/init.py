#!/usr/bin/env python3
"""Initialize ocd conventions and skill infrastructure in a project.

Copies rule files from plugin to .claude/rules/ and initializes
navigator database. Deterministic operations only — no agent judgment.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


def get_plugin_root() -> Path:
    """Resolve plugin root from script location."""
    return Path(__file__).parent.parent


def get_project_dir() -> Path:
    """Resolve project directory from environment or cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


CAPABILITIES = {
    "agent-authoring": {
        "rule": "ocd-agent-authoring.md",
    },
    "communication": {
        "rule": "ocd-communication.md",
    },
    "workflow": {
        "rule": "ocd-workflow.md",
    },
    "navigator": {
        "rule": "ocd-navigator.md",
        "init_db": True,
    },
}


def deploy_rules(plugin_root: Path, project_dir: Path, only: list[str] | None = None) -> list[str]:
    """Copy rule files from plugin to .claude/rules/. Returns status lines."""
    rules_src = plugin_root / "rules"
    rules_dst = project_dir / ".claude" / "rules"
    rules_dst.mkdir(parents=True, exist_ok=True)

    lines = []

    if only:
        rule_files = []
        for name in only:
            cap = CAPABILITIES.get(name)
            if cap and "rule" in cap:
                rule_files.append(cap["rule"])
            else:
                lines.append(f"  Unknown capability: {name}")
    else:
        rule_files = [cap["rule"] for cap in CAPABILITIES.values() if "rule" in cap]

    for filename in rule_files:
        src = rules_src / filename
        dst = rules_dst / filename
        if not src.exists():
            lines.append(f"  Missing source: {filename}")
            continue
        if dst.exists():
            lines.append(f"  Skipped (exists): {filename}")
            continue
        shutil.copy2(src, dst)
        lines.append(f"  Deployed: {filename}")

    return lines


def init_navigator(plugin_root: Path, project_dir: Path) -> list[str]:
    """Initialize navigator database. Returns status lines."""
    scripts_dir = plugin_root / "skills" / "navigator" / "scripts"
    sys.path.insert(0, str(scripts_dir))

    try:
        import navigator
        db_path = project_dir / "docs" / "ocd" / "navigator" / "navigator.db"
        result = navigator.init_db(str(db_path))
        return [f"  {result}"]
    except Exception as e:
        return [f"  Error: {e}"]
    finally:
        sys.path.pop(0)


def main():
    parser = argparse.ArgumentParser(
        prog="ocd_init.py",
        description="Initialize ocd conventions and skill infrastructure in current project.",
    )
    parser.add_argument(
        "--rules-only",
        action="store_true",
        help="Deploy rules only, skip infrastructure initialization",
    )
    parser.add_argument(
        "--only",
        type=str,
        default=None,
        help="Comma-separated list of capabilities to deploy (e.g., agent-authoring,navigator)",
    )
    args = parser.parse_args()

    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    only = [s.strip() for s in args.only.split(",")] if args.only else None

    print("ocd init")
    print()

    # Deploy rules
    print("Rules:")
    rule_lines = deploy_rules(plugin_root, project_dir, only=only)
    for line in rule_lines:
        print(line)
    print()

    # Initialize infrastructure
    if args.rules_only:
        print("Infrastructure: skipped (--rules-only)")
    else:
        caps_with_infra = {k: v for k, v in CAPABILITIES.items() if v.get("init_db")}
        if only:
            caps_with_infra = {k: v for k, v in caps_with_infra.items() if k in only}

        if caps_with_infra:
            print("Infrastructure:")
            for name in caps_with_infra:
                if name == "navigator":
                    lines = init_navigator(plugin_root, project_dir)
                    for line in lines:
                        print(line)
        else:
            print("Infrastructure: none required")

    print()
    print("Done. Restart Claude session to load new rules.")


if __name__ == "__main__":
    main()

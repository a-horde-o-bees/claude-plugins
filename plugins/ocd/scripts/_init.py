"""Init orchestration.

Deploy rules and run skill init subcommands.
"""

import os
import subprocess
from pathlib import Path

from _deploy import deploy_files, discover_skill_clis, format_columns, get_plugin_root, get_project_dir


def deploy_rules(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy rule files from plugin to .claude/rules/. Returns deploy results."""
    return deploy_files(
        src_dir=plugin_root / "rules",
        dst_dir=project_dir / ".claude" / "rules",
        pattern="*.md",
        force=force,
    )


def format_deploy_results(results: list[dict]) -> list[str]:
    """Format deploy results as columnar output with transitions."""
    rows = []
    for r in results:
        if r["before"] == r["after"]:
            state = r["after"]
        else:
            state = f"{r['before']} → {r['after']}"
        rows.append((state, r["name"]))
    return format_columns(rows)


def run_skill_cli(cli_path: Path, subcommand: str, force: bool = False) -> list[str]:
    """Run skill CLI subcommand and return output lines."""
    cmd = ["python3", str(cli_path), subcommand]
    if force and subcommand == "init":
        cmd.append("--force")
    result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    output = result.stdout.strip()
    if result.returncode != 0 and result.stderr:
        output = result.stderr.strip()
    return output.splitlines() if output else []


def run_init(force: bool = False) -> None:
    """Full init: deploy rules, run skill inits. Prints output directly."""
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()

    print("ocd init")
    print()

    print("Rules:")
    results = deploy_rules(plugin_root, project_dir, force=force)
    for line in format_deploy_results(results):
        print(f"  {line}")
    print()

    skill_clis = discover_skill_clis(plugin_root)
    if skill_clis:
        for skill_name, cli_path in sorted(skill_clis.items()):
            print(f"{skill_name.capitalize()}:")
            lines = run_skill_cli(cli_path, "init", force=force)
            for line in lines:
                print(f"  {line}")
            print()
    else:
        print("Skills: no CLI scripts found")
        print()

    rules_changed = any(r["before"] != r["after"] for r in results)
    if rules_changed:
        print("Done. Restart Claude session to load new rules.")
    else:
        print("Done.")

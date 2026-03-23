"""Initialize ocd rules and skill infrastructure in a project.

Deploys rule files from plugin to .claude/rules/, then discovers and
runs each skill's init.py for infrastructure setup.
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path


def get_plugin_root() -> Path:
    """Resolve plugin root from script location."""
    return Path(__file__).parent.parent


def get_project_dir() -> Path:
    """Resolve project directory from environment or cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def deploy_rules(plugin_root: Path, project_dir: Path, force: bool = False) -> list[str]:
    """Copy all rule files from plugin to .claude/rules/. Returns status lines."""
    rules_src = plugin_root / "rules"
    rules_dst = project_dir / ".claude" / "rules"
    rules_dst.mkdir(parents=True, exist_ok=True)

    lines = []
    for src in sorted(rules_src.glob("*.md")):
        dst = rules_dst / src.name
        if dst.exists() and not force:
            lines.append(f"  Skipped (exists): {src.name}")
            continue
        action = "Overwritten" if dst.exists() else "Deployed"
        shutil.copy2(src, dst)
        lines.append(f"  {action}: {src.name}")

    return lines


def discover_skill_inits(plugin_root: Path) -> list[Path]:
    """Find all skills/*/scripts/init.py files."""
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(skills_dir.glob("*/scripts/init.py"))


def run_skill_init(init_script: Path, force: bool = False) -> list[str]:
    """Run a skill's init.py and return output lines."""
    cmd = ["python3", str(init_script)]
    if force:
        cmd.append("--force")
    result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    output = result.stdout.strip()
    if result.returncode != 0 and result.stderr:
        output = result.stderr.strip()
    return output.splitlines() if output else []


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ocd_init.py",
        description="Initialize ocd rules and skill infrastructure in current project.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing rules and conventions with plugin defaults",
    )
    args = parser.parse_args()

    plugin_root = get_plugin_root()
    project_dir = get_project_dir()

    print("ocd init")
    print()

    # Deploy rules (cross-cutting)
    print("Rules:")
    for line in deploy_rules(plugin_root, project_dir, force=args.force):
        print(line)
    print()

    # Run each skill's init
    skill_inits = discover_skill_inits(plugin_root)
    if skill_inits:
        for init_script in skill_inits:
            skill_name = init_script.parent.parent.name
            print(f"{skill_name.capitalize()}:")
            lines = run_skill_init(init_script, force=args.force)
            for line in lines:
                print(f"  {line}")
            print()
    else:
        print("Skills: no init scripts found")
        print()

    print("Done. Restart Claude session to load new rules.")


if __name__ == "__main__":
    main()

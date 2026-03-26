"""Rule state check.

Compares plugin source rules against deployed rules in user project.
Deterministic diff-based evaluation — no state file needed.
"""

from pathlib import Path


def check_rules(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Compare source rules against deployed rules.

    For each rule in plugin source:
    - adopted: deployed file matches source
    - modified: deployed file exists but content differs
    - skipped: deployed file does not exist

    Returns list of {"rule": name, "state": state} dicts, sorted by rule name.
    """
    source_dir = plugin_root / "rules"
    deploy_dir = project_dir / ".claude" / "rules"

    results = []

    if not source_dir.is_dir():
        return results

    for src_file in sorted(source_dir.glob("*.md")):
        name = src_file.stem.removeprefix("ocd-")
        dst_file = deploy_dir / src_file.name

        if not dst_file.exists():
            results.append({"rule": name, "state": "skipped"})
            continue

        src_content = src_file.read_bytes()
        dst_content = dst_file.read_bytes()
        # Compare with stamp applied — template has "type: template", deployed has "type: deployed"
        src_deployed = src_content.replace(b"type: template", b"type: deployed", 1)

        if src_deployed == dst_content:
            results.append({"rule": name, "state": "adopted"})
        else:
            results.append({"rule": name, "state": "modified"})

    return results

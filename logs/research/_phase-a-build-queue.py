"""Build the Phase A research-migration work queue (per-file).

For each subject under `logs/research/`, emit one CSV row per sample file
with the file's byte size as `measured_size`. The orchestrator bin-packs
file paths into spawn batches; each spawn restructures the files it
receives and returns accumulated section observations.

One-shot scaffolding script — runs once during Phase A setup, then is
deleted at sandbox cleanup.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def project_root() -> Path:
    """Resolve this script's owning git repository root.

    Mirrors `tools.environment.get_git_root_for(Path)` semantics —
    deterministic via `git -C <dir> rev-parse --show-toplevel`. Inlined
    rather than imported because this one-shot script lives outside any
    package context that could surface the helper without sys.path
    manipulation.
    """
    here = Path(__file__).resolve().parent
    result = subprocess.run(
        ["git", "-C", str(here), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def main() -> int:
    project = project_root()
    research = project / "logs" / "research"
    queue_path = research / "_phase-a-queue.csv"

    rows: list[tuple[str, int]] = []
    for subject_dir in sorted(research.iterdir()):
        if not subject_dir.is_dir() or subject_dir.name.startswith("_"):
            continue
        samples_dir = subject_dir / "samples"
        if not samples_dir.is_dir():
            continue
        for md in sorted(samples_dir.glob("*.md")):
            if md.name.startswith("_"):
                continue
            rel = md.relative_to(project)
            rows.append((str(rel), md.stat().st_size))

    with queue_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["path", "measured_size", "status", "batch_id", "notes"])
        for key, size in rows:
            writer.writerow([key, size, "pending", "", ""])

    print(f"Total items: {len(rows)}")
    print(f"Total size: {sum(s for _, s in rows):,} bytes")
    by_subject: dict[str, tuple[int, int]] = {}
    for path, size in rows:
        subject = path.split("/")[2]
        count, total = by_subject.get(subject, (0, 0))
        by_subject[subject] = (count + 1, total + size)
    print("\nBy subject:")
    for subject, (count, total) in sorted(by_subject.items()):
        avg = total // count if count else 0
        print(f"  {subject}: {count} files, {total:,} bytes total, {avg:,} avg")
    print(f"\nQueue written to: {queue_path.relative_to(project)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

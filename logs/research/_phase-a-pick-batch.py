"""Pick the next Phase A batch by byte budget against running cost-per-byte estimate.

Reads _phase-a-log.csv to get the running ratio (work tokens per byte) and the
list of already-processed files. Picks the next N files in alphabetical order
under the byte cap that fits in 90% of the 200K-token budget minus base cost.
"""

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(
    subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
)
QUEUE = ROOT / "logs/research/_phase-a-queue.csv"
LOG = ROOT / "logs/research/_phase-a-log.csv"
ARCHIVE = ROOT / "logs/research/_phase-a-mechanical-pass-archive"

CONTEXT_BUDGET = 200_000
UTILIZATION = 0.90  # target 90% of context window
BASE_TOKENS = 38_000  # measured from context-aware-iteration baseline
TRAILING_WINDOW = 3  # use last N batches for ratio estimate (more responsive than lifetime avg)

SUBJECT = "mcp"


def read_processed() -> set[str]:
    """Files already processed in non-archived (current) batches."""
    processed: set[str] = set()
    for batch_yaml in sorted((ROOT / "logs/research").glob("_phase-a-batch-*.yaml")):
        for line in batch_yaml.read_text().splitlines():
            line = line.strip()
            if line.startswith("- path:"):
                path = line.split(":", 1)[1].strip()
                if path.startswith("/"):
                    path = str(Path(path).relative_to(ROOT))
                processed.add(path)
    return processed


def running_ratio() -> tuple[float, int]:
    """Return (work_tokens_per_byte, batches_seen) using trailing window over non-anomaly rows."""
    if not LOG.exists():
        return 3.16, 0  # bootstrap from calibration
    rows = list(csv.DictReader(LOG.open()))
    if not rows:
        return 3.16, 0
    eligible = [r for r in rows if r.get("anomaly", "false").lower() != "true"]
    window = eligible[-TRAILING_WINDOW:]
    total_work = sum(int(r["work_tokens"]) for r in window)
    total_bytes = sum(int(r["total_measured_size"]) for r in window)
    return total_work / total_bytes, len(rows)


def pick_next(max_files: int | None = None) -> list[dict]:
    processed = read_processed()
    rows = list(csv.DictReader(QUEUE.open()))
    pending = [r for r in rows if f"/{SUBJECT}/" in r["path"] and r["path"] not in processed]
    pending.sort(key=lambda r: r["path"])  # alphabetical

    ratio, n_batches = running_ratio()
    work_budget = int(CONTEXT_BUDGET * UTILIZATION) - BASE_TOKENS
    byte_budget = int(work_budget / ratio)

    print(f"Trailing-{TRAILING_WINDOW} cost: {ratio:.3f} work-tokens/byte (after {n_batches} batches total)")
    print(f"Token budget: 90% × {CONTEXT_BUDGET} = {int(CONTEXT_BUDGET * UTILIZATION)} total")
    print(f"  - base cost: {BASE_TOKENS}")
    print(f"  = work budget: {work_budget} tokens")
    print(f"  = byte budget: {byte_budget} bytes")
    print(f"Pending mcp files: {len(pending)}")

    picked: list[dict] = []
    bytes_used = 0
    for r in pending:
        sz = int(r["measured_size"])
        if bytes_used + sz > byte_budget:
            break
        if max_files is not None and len(picked) >= max_files:
            break
        picked.append(r)
        bytes_used += sz

    print(f"\nPicked {len(picked)} files, {bytes_used} bytes ({100 * bytes_used / byte_budget:.1f}% of budget):")
    for r in picked:
        print(f"  {int(r['measured_size']):>6}  {r['path']}")
    print(f"\nProjected work tokens: {int(bytes_used * ratio)}")
    print(f"Projected total tokens: {int(bytes_used * ratio) + BASE_TOKENS} ({100 * (int(bytes_used * ratio) + BASE_TOKENS) / CONTEXT_BUDGET:.1f}% of {CONTEXT_BUDGET})")

    return picked


if __name__ == "__main__":
    max_files = int(sys.argv[1]) if len(sys.argv) > 1 else None
    pick_next(max_files)

"""Phase B mechanical sweep — strip section numbering and empty pitfalls blocks from mcp samples.

Two transformations, both pure-text and idempotent:

1. `## N. <text>` → `## <text>` at level-2 headings only. The new template defines
   section order without numeric prefix; chain-key lookups operate on heading text,
   not numbers.

2. `### pitfalls observed\\n\\nnone noted in this repo\\n` blocks (heading + body)
   are removed entirely. The new template makes pitfalls observed optional; an
   empty subheading carries no signal.

Skips meta files (`_TEMPLATE.md`, `_INDEX.md`, `_missing--*.md`).
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(
    subprocess.run(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
)
SAMPLES = ROOT / "logs/research/mcp/samples"

# Match `## N. <rest>` where N is 1-20 (the canonical section count).
NUMBERED_HEADING = re.compile(r"^## (\d{1,2})\. (.+)$", re.MULTILINE)

# Match `### pitfalls observed` block whose body is exactly "none noted in this repo"
# (with optional trailing whitespace) followed by either another heading or end-of-file.
EMPTY_PITFALLS = re.compile(
    r"^### pitfalls observed\s*\n\s*\nnone noted in this repo\s*\n\s*\n",
    re.MULTILINE,
)

# Variant where there is no trailing blank line (block ends at next heading).
EMPTY_PITFALLS_TERMINAL = re.compile(
    r"^### pitfalls observed\s*\n\s*\nnone noted in this repo\s*\n?\Z",
    re.MULTILINE,
)


def transform(text: str) -> tuple[str, int, int]:
    """Apply both transformations; return (new_text, n_renumbered, n_pitfalls_stripped)."""
    new_text, n_renumbered = NUMBERED_HEADING.subn(r"## \2", text)
    new_text, n_block = EMPTY_PITFALLS.subn("", new_text)
    new_text, n_terminal = EMPTY_PITFALLS_TERMINAL.subn("", new_text)
    return new_text, n_renumbered, n_block + n_terminal


def main() -> None:
    samples = sorted(p for p in SAMPLES.glob("*.md") if not p.name.startswith("_"))
    total_files = 0
    total_renumbered = 0
    total_stripped = 0
    files_changed = 0
    for path in samples:
        original = path.read_text(encoding="utf-8")
        new_text, n_renumbered, n_stripped = transform(original)
        if new_text != original:
            path.write_text(new_text, encoding="utf-8")
            files_changed += 1
        total_files += 1
        total_renumbered += n_renumbered
        total_stripped += n_stripped
    print(f"Files processed: {total_files}")
    print(f"Files changed: {files_changed}")
    print(f"Section numbers stripped: {total_renumbered}")
    print(f"Empty pitfalls blocks stripped: {total_stripped}")


if __name__ == "__main__":
    main()

"""Mechanical retrofit of research/mcp/repos/*.md to match the updated _TEMPLATE.md.

Adds:
- `- one-line purpose: TBD` bullet to Identification if missing.
- `- pitfalls observed:` bullet as last item of each structured section (1-16) if missing.

Does NOT:
- Number sections (deferred to Phase 4b).
- Derive content (deferred to Phase 4b).
- Touch _TEMPLATE.md, _INDEX.md, or _missing--*.md files.
- Touch sections 17+ (Notable structural choices, Unanticipated axes observed, Python-specific, Gaps).

Idempotent: safe to re-run. Detects existing fields and skips.
"""

from pathlib import Path
import re

ROOT = Path(__file__).parent / "repos"

STRUCTURED_SECTIONS = [
    "Language and runtime",
    "Transport",
    "Distribution",
    "Entry point / launch",
    "Configuration surface",
    "Authentication",
    "Multi-tenancy",
    "Capabilities exposed",
    "Observability",
    "Host integrations shown in README or repo",
    "Claude Code plugin wrapper",
    "Tests",
    "CI",
    "Container / packaging artifacts",
    "Example client / developer ergonomics",
    "Repo layout",
]


def retrofit(text: str) -> tuple[str, list[str]]:
    """Return (new_text, changes_made)."""
    changes: list[str] = []
    lines = text.split("\n")

    # Find section header line indices
    header_idx: dict[str, int] = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^## (.+)$", ln)
        if m:
            header_idx[m.group(1).strip()] = i

    # 1. Add one-line purpose to Identification
    if "Identification" in header_idx:
        ident_start = header_idx["Identification"]
        # Find end of Identification bullets
        i = ident_start + 1
        ident_end = i
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("## "):
                break
            if s.startswith("- "):
                ident_end = i
            i += 1
        ident_block = "\n".join(lines[ident_start : ident_end + 1])
        if "one-line purpose" not in ident_block.lower():
            lines.insert(ident_end + 1, "- one-line purpose: TBD")
            changes.append("Identification: added one-line purpose")
            # Rebuild header_idx because inserts shift
            header_idx = {}
            for i, ln in enumerate(lines):
                m = re.match(r"^## (.+)$", ln)
                if m:
                    header_idx[m.group(1).strip()] = i

    # 2. For each structured section, ensure `- pitfalls observed:` is the last bullet
    for section in STRUCTURED_SECTIONS:
        if section not in header_idx:
            continue
        start = header_idx[section]
        # Find end of this section (next ## header or EOF)
        end = len(lines)
        for i in range(start + 1, len(lines)):
            if lines[i].startswith("## "):
                end = i
                break
        section_text = "\n".join(lines[start:end])
        if re.search(r"(?mi)^-\s*pitfalls observed", section_text):
            continue
        # Find the last non-blank line before `end`
        insert_idx = end
        for j in range(end - 1, start, -1):
            if lines[j].strip():
                insert_idx = j + 1
                break
        # Insert `- pitfalls observed:` (with a blank line before if needed)
        new_lines = ["- pitfalls observed:"]
        # Ensure a blank line after the pitfalls bullet if the next content is a new section
        if insert_idx < len(lines) and lines[insert_idx].startswith("## "):
            new_lines.append("")
        lines[insert_idx:insert_idx] = new_lines
        changes.append(f"{section}: added pitfalls observed")
        # Rebuild header_idx because inserts shifted
        header_idx = {}
        for i, ln in enumerate(lines):
            m = re.match(r"^## (.+)$", ln)
            if m:
                header_idx[m.group(1).strip()] = i

    return "\n".join(lines), changes


def main() -> None:
    total = 0
    changed = 0
    skipped = 0
    details: list[tuple[str, list[str]]] = []

    for p in sorted(ROOT.glob("*.md")):
        name = p.name
        if name.startswith("_"):
            skipped += 1
            continue
        total += 1
        original = p.read_text()
        new_text, changes = retrofit(original)
        if new_text != original:
            p.write_text(new_text)
            changed += 1
            details.append((name, changes))

    print(f"Processed: {total} files")
    print(f"Changed:   {changed} files")
    print(f"Skipped:   {skipped} files (underscore-prefixed)")
    if details[:3]:
        print("\nExample changes:")
        for name, ch in details[:3]:
            print(f"  {name}:")
            for c in ch:
                print(f"    - {c}")


if __name__ == "__main__":
    main()

"""Output formatting for plugin status and init displays.

Column alignment, section rendering, and skill header formatting.
"""


def format_columns(rows: list[tuple[str, ...]], separator: str = "  ") -> list[str]:
    """Format rows into aligned columns."""
    if not rows:
        return []
    widths = [max(len(cell) for cell in col) for col in zip(*rows)]
    return [separator.join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip() for row in rows]


def format_section(header: str, items: list[dict], extra: list[dict] | None = None) -> list[str]:
    """Render a section with header, file items, and optional extra lines.

    Items are dicts with {path, before, after}.
    Extra are dicts with {label, value}.
    """
    rows = []
    for item in items:
        if item["before"] == item["after"]:
            value = item["after"]
        else:
            value = f"{item['before']} \u2192 {item['after']}"
        rows.append((item["path"], value))

    if extra:
        for e in extra:
            rows.append((e["label"], e["value"]))

    lines = [header]
    for row in format_columns(rows):
        lines.append(f"  {row}")
    return lines


def format_bare_skill(plugin_name: str, skill_name: str) -> str:
    """Render a skill header with no infrastructure.

    Claude Code namespaces plugin slash commands automatically
    (`/<plugin>:<command>` on collision, `/<command>` when unique),
    so the skill name is used verbatim without a plugin prefix.
    """
    del plugin_name  # retained for signature compatibility with init-skill branch
    return f"/{skill_name}"

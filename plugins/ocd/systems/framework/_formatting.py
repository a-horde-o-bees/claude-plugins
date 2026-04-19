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
    """Render a skill header in qualified `/plugin:skill` form.

    Per design-principles Agent-First Interfaces, every agent-emitted
    skill reference uses the qualified form to stay unambiguous across
    contexts and installed plugins.
    """
    return f"/{plugin_name}:{skill_name}"

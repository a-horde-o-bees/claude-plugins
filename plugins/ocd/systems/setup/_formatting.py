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


def format_status(
    header: str,
    rows: list[dict],
    columns: list[str],
    extra: list[dict] | None = None,
) -> list[str]:
    """Render a status section as a per-scope table.

    rows: [{"name": str, **{column: state}}, ...] — one row per item.
    columns: column names (typically scopes like "user", "project") in
        display order.
    extra: optional [{"label", "value"}, ...] rendered after the table.

    The first cell of the header row is empty so column names align over
    their data columns, with the row name occupying the leftmost column.
    """
    lines = [header]

    if rows and columns:
        header_row: tuple[str, ...] = ("",) + tuple(columns)
        data_rows: list[tuple[str, ...]] = [
            (str(r["name"]),) + tuple(str(r.get(c, "")) for c in columns)
            for r in rows
        ]
        for line in format_columns([header_row] + data_rows):
            lines.append(f"  {line}")

    if extra:
        extra_rows = [(e["label"], e["value"]) for e in extra]
        for line in format_columns(extra_rows):
            lines.append(f"  {line}")

    return lines


def format_catalog(header: str, items: list[dict]) -> list[str]:
    """Render a catalog of available items with name + tagline.

    Items are dicts with {name, tagline}. Emits the header, then a column-
    aligned list of name → tagline. Used by `setup <system> list` to show
    a system's available templates so the user can scan at a glance and
    reach for `setup <system> show <name>` for full details.
    """
    rows = [(item["name"], item.get("tagline", "")) for item in items]
    lines = [header]
    if not rows:
        lines.append("  (no items)")
        return lines
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

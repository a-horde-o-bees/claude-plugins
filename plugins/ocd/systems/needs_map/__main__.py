"""needs-map CLI.

Presentation layer: argument parsing, dispatch, and formatted output.
Business logic lives in the facade (__init__.py) and internal modules
(_db, _entities, _edges, _queries, _init). The CLI ensures the database
is ready before each read or write — callers invoking the CLI do not
need to pre-check.
"""

import argparse
import sqlite3
import sys

from tools.errors import InitError, NotReadyError

from . import _db, _entities, _edges, _queries, _init


def _connect() -> sqlite3.Connection:
    """Return a connection to the deployed needs-map database.

    Ensures readiness first — if the DB is absent or has a divergent
    schema, raises NotReadyError so the CLI catch-and-format path runs.
    """
    _init.ensure_ready()
    return _db.get_connection(str(_init._db_path()))


def _fmt_component(cid: str, description: str, validated: int) -> str:
    glyph = "◈" if validated else "? ◈"
    return f"{glyph} [{cid}] {description}"


def _fmt_need(
    nid: str, description: str, validated: int, is_root: bool = False,
) -> str:
    glyph = "☆" if is_root else "◇"
    marker = glyph if validated else f"? {glyph}"
    return f"{marker} [{nid}] {description}"


def _print_dep_tree(
    conn: sqlite3.Connection,
    comp_id: str,
    description: str,
    validated: int,
    header_prefix: str = "",
    cont_prefix: str = "",
) -> None:
    print(f"{header_prefix}{_fmt_component(comp_id, description, validated)}")
    children = _queries.dependents_of(conn, comp_id)
    for i, (cid, cdesc, cvalidated) in enumerate(children):
        is_last = i == len(children) - 1
        branch = "└── " if is_last else "├── "
        cont = "    " if is_last else "│   "
        _print_dep_tree(
            conn, cid, cdesc, cvalidated,
            cont_prefix + branch, cont_prefix + cont,
        )


def _print_need_tree(
    conn: sqlite3.Connection,
    need_id: str,
    description: str,
    validated: int,
    header_prefix: str = "",
    cont_prefix: str = "",
    is_root: bool = False,
) -> None:
    status, _ = _queries.coverage(conn, need_id)
    marker = {"covered": "✓", "gap": "✗", "abstract": " ", "unrefined": "○"}[status]
    direct_count = conn.execute(
        "SELECT COUNT(*) FROM addresses WHERE need_id = ?", (need_id,)
    ).fetchone()[0]

    label = _fmt_need(need_id, description, validated, is_root=is_root)
    suffix = (
        f"  ({direct_count} addresser{'s' if direct_count != 1 else ''})"
        if direct_count else ""
    )
    print(f"{header_prefix}{marker} {label}{suffix}")

    children = _queries.need_children(conn, need_id)
    for i, (cid, cdesc, cvalidated) in enumerate(children):
        is_last = i == len(children) - 1
        branch = "└── " if is_last else "├── "
        cont = "    " if is_last else "│   "
        _print_need_tree(
            conn, cid, cdesc, cvalidated,
            cont_prefix + branch, cont_prefix + cont, is_root=False,
        )


def _cmd_add_component(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    description = " ".join(args.description)
    new_id = _entities.add_component(conn, description)
    print(f"Added: [{new_id}] {description}")


def _cmd_set_component(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    description = " ".join(args.description)
    _entities.set_component(conn, args.id, description)
    print(f"Updated: [{args.id}] {description}")


def _cmd_remove_component(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _entities.remove_component(conn, args.id)
    print(f"Removed component: [{args.id}]")


def _cmd_add_need(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    description = " ".join(args.description)
    new_id = _entities.add_need(conn, description)
    print(f"Added root: [{new_id}] {description}")


def _cmd_refine(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    description = " ".join(args.description)
    new_id = _entities.refine(conn, args.parent, description)
    print(f"Added: [{new_id}] (child of {args.parent}) {description}")


def _cmd_set_need(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    description = " ".join(args.description)
    _entities.set_need(conn, args.id, description)
    print(f"Updated: [{args.id}] {description}")


def _cmd_set_parent(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    new_parent = None if args.parent == "root" else args.parent
    _entities.set_parent(conn, args.id, new_parent)
    if new_parent is None:
        print(f"Re-parented: {args.id} → root")
    else:
        print(f"Re-parented: {args.id} → child of {args.parent}")


def _cmd_remove_need(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _entities.remove_need(conn, args.id)
    print(f"Removed need: [{args.id}]")


def _cmd_depend(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _edges.depend(conn, args.component, args.dependency)
    print(f"Dependency: {args.component} depends on {args.dependency}")


def _cmd_undepend(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _edges.undepend(conn, args.component, args.dependency)
    print(f"Removed: {args.component} depends on {args.dependency}")


def _cmd_address(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rationale = " ".join(args.rationale)
    _edges.address(conn, args.component, args.need, rationale)
    print(f"Addresses: {args.component} → {args.need}")
    print(f"  rationale: {rationale.strip()}")


def _cmd_unaddress(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _edges.unaddress(conn, args.component, args.need)
    print(f"Removed: {args.component} → {args.need}")


def _cmd_set_rationale(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    rationale = " ".join(args.rationale)
    _edges.set_rationale(conn, args.component, args.need, rationale)
    print(f"Updated rationale: address {args.component} → {args.need}")
    print(f"  rationale: {rationale.strip()}")


def _cmd_add_path(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _edges.add_path(conn, args.component, args.path)
    print(f"Path: {args.component} @ {args.path}")


def _cmd_remove_path(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _edges.remove_path(conn, args.component, args.path)
    print(f"Removed: {args.component} @ {args.path}")


def _cmd_validate(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _entities.validate(conn, args.id)
    print(f"Validated: {args.id}")


def _cmd_invalidate(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _entities.invalidate(conn, args.id)
    print(f"Invalidated: {args.id}")


def _cmd_dependencies(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    if args.component:
        desc, validated = _queries.component_row(conn, args.component)
        _print_dep_tree(conn, args.component, desc, validated)
        if args.verify:
            print()
            _verify_one(conn, args.component)
    else:
        for cid, cdesc, cvalidated in _queries.dependency_roots(conn):
            _print_dep_tree(conn, cid, cdesc, cvalidated)
        if args.verify:
            print()
            _verify_all(conn)


def _cmd_needs(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    if args.root:
        desc, validated, parent = _queries.need_row(conn, args.root)
        _print_need_tree(
            conn, args.root, desc, validated, is_root=(parent is None),
        )
    else:
        roots = _queries.need_roots(conn)
        if not roots:
            print("(no needs)")
            return
        for nid, ndesc, nvalidated in roots:
            _print_need_tree(conn, nid, ndesc, nvalidated, is_root=True)


def _cmd_addresses(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    if args.gaps:
        _print_leaf_gaps(conn)
        return
    if args.orphans:
        _print_orphans(conn)
        return
    if args.entity:
        if conn.execute(
            "SELECT 1 FROM needs WHERE id = ?", (args.entity,)
        ).fetchone():
            _print_addresses_for_need(conn, args.entity)
        elif conn.execute(
            "SELECT 1 FROM components WHERE id = ?", (args.entity,)
        ).fetchone():
            _print_addresses_for_component(conn, args.entity)
        else:
            raise LookupError(
                f"'{args.entity}' is not a known need or component"
            )
        return
    needs = _queries.all_needs(conn)
    for i, (nid,) in enumerate(needs):
        _print_addresses_for_need(conn, nid)
        if i < len(needs) - 1:
            print()


def _cmd_where(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    desc, validated = _queries.component_row(conn, args.component)
    print(_fmt_component(args.component, desc, validated))
    paths = _queries.component_paths(conn, args.component)
    if not paths:
        print("  (no recorded paths)")
        return
    for p in paths:
        print(f"  @ {p}")


def _cmd_why(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    desc, validated = _queries.component_row(conn, args.component)
    print(_fmt_component(args.component, desc, validated))
    addressed = _queries.addressed_needs(conn, args.component)
    if not addressed:
        print("  (addresses nothing)")
        return
    for nid, ndesc, nvalidated, rationale, nparent in addressed:
        print(
            f"  ↑ addresses: "
            f"{_fmt_need(nid, ndesc, nvalidated, is_root=(nparent is None))}"
        )
        if rationale:
            print(f"      rationale: {rationale}")


def _cmd_how(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    _queries.need_row(conn, args.need)
    _print_addresses_for_need(conn, args.need)


def _cmd_compare(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    a_desc, a_validated = _queries.component_row(conn, args.a)
    b_desc, b_validated = _queries.component_row(conn, args.b)

    print(f"=== {args.a} ===")
    print(_fmt_component(args.a, a_desc, a_validated))
    print(f"\n=== {args.b} ===")
    print(_fmt_component(args.b, b_desc, b_validated))

    addr_a = {
        r[0]: r for r in _queries.addressed_needs(conn, args.a)
    }
    addr_b = {
        r[0]: r for r in _queries.addressed_needs(conn, args.b)
    }

    common = sorted(set(addr_a) & set(addr_b), key=lambda x: int(x[1:]))
    only_a = sorted(set(addr_a) - set(addr_b), key=lambda x: int(x[1:]))
    only_b = sorted(set(addr_b) - set(addr_a), key=lambda x: int(x[1:]))

    if common:
        print(f"\n=== COMMON NEEDS ({len(common)}) — both components address ===")
        for nid in common:
            row = addr_a[nid]
            print(_fmt_need(nid, row[1], row[2], is_root=(row[4] is None)))
            print(f"  {args.a}: {row[3]}")
            print(f"  {args.b}: {addr_b[nid][3]}")

    if only_a:
        print(f"\n=== {args.a} ONLY ({len(only_a)}) ===")
        for nid in only_a:
            row = addr_a[nid]
            print(_fmt_need(nid, row[1], row[2], is_root=(row[4] is None)))
            if row[3]:
                print(f"  rationale: {row[3]}")

    if only_b:
        print(f"\n=== {args.b} ONLY ({len(only_b)}) ===")
        for nid in only_b:
            row = addr_b[nid]
            print(_fmt_need(nid, row[1], row[2], is_root=(row[4] is None)))
            if row[3]:
                print(f"  rationale: {row[3]}")

    if not common and not only_a and not only_b:
        print("\n(neither component addresses any need)")


def _cmd_summary(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    counts = _queries.summary_counts(conn)
    print(
        f"Components: {counts['components']} "
        f"({counts['validated_components']} validated)"
    )
    print(
        f"Needs: {counts['needs']} "
        f"({counts['roots']} roots, {counts['leaves']} leaves, "
        f"{counts['validated_needs']} validated)"
    )
    print(
        f"Dependencies: {counts['dependencies']} | "
        f"Addresses: {counts['addresses']}"
    )
    print(
        f"Unrefined roots: {counts['unrefined']} "
        f"(need refinement before any component can address)"
    )
    print(f"Gaps: {counts['gaps']} (refined leaves with no addressers)")
    print("\nUse `needs` to view the need tree.")


def _cmd_uncovered(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    files = _queries.uncovered_files(conn)
    if not files:
        print("All git-tracked files are covered by component paths.")
        return
    groups: dict[str, list[str]] = {}
    for f in files:
        parts = f.split("/")
        group = parts[0] if len(parts) > 1 else "."
        groups.setdefault(group, []).append(f)
    print(f"Uncovered files: {len(files)} (not attached to any component)\n")
    for group in sorted(groups):
        fs = groups[group]
        print(f"{group}/ ({len(fs)})")
        for f in fs:
            print(f"  {f}")
        print()


def _print_addresses_for_need(conn: sqlite3.Connection, need_id: str) -> None:
    desc, validated, parent = _queries.need_row(conn, need_id)
    print(_fmt_need(need_id, desc, validated, is_root=(parent is None)))
    direct = _queries.direct_addressers(conn, need_id)
    if not direct:
        print("  ✗ unaddressed (gap)")
        return
    for cid, cdesc, cvalidated, rationale in direct:
        print(f"  ↳ {_fmt_component(cid, cdesc, cvalidated)}")
        if rationale:
            print(f"      rationale: {rationale}")


def _print_addresses_for_component(conn: sqlite3.Connection, comp_id: str) -> None:
    desc, validated = _queries.component_row(conn, comp_id)
    print(_fmt_component(comp_id, desc, validated))
    addressed = _queries.addressed_needs(conn, comp_id)
    if not addressed:
        print("  (addresses nothing)")
        return
    for nid, ndesc, nvalidated, _rationale, nparent in addressed:
        print(
            f"  → {_fmt_need(nid, ndesc, nvalidated, is_root=(nparent is None))}"
        )


def _print_leaf_gaps(conn: sqlite3.Connection) -> None:
    rows = _queries.leaf_gaps(conn)
    if not rows:
        print("No gaps — every refined leaf need has at least one addresser")
        return
    print(f"Gaps ({len(rows)}) — refined leaf needs with no addressers:")
    for nid, desc in rows:
        print(f"  ✗ [{nid}] {desc}")


def _print_orphans(conn: sqlite3.Connection) -> None:
    rows = _queries.orphans(conn)
    if not rows:
        print("No orphans — every component addresses at least one need")
        return
    print(f"Orphan components ({len(rows)}):")
    for cid, desc, validated in rows:
        print(f"  {_fmt_component(cid, desc, validated)}")


def _verify_one(
    conn: sqlite3.Connection, comp_id: str, quiet: bool = False,
) -> bool:
    _queries.component_row(conn, comp_id)
    rows = _queries.dependency_ancestors(conn, comp_id)
    if not rows:
        if not quiet:
            print(f"✓ {comp_id} has no dependency ancestors")
        return True
    unvalidated = [(cid, desc) for cid, desc, validated in rows if not validated]
    all_validated = not unvalidated
    if not quiet or not all_validated:
        if all_validated:
            print(f"✓ [{comp_id}] all dependencies validated")
        else:
            print(f"✗ [{comp_id}] unvalidated dependencies:")
            for cid, desc in unvalidated:
                print(f"    ✗ [{cid}] {desc}")
    return all_validated


def _verify_all(conn: sqlite3.Connection) -> None:
    any_unvalidated = False
    for cid in _queries.all_component_ids(conn):
        if not _verify_one(conn, cid, quiet=True):
            any_unvalidated = True
    if not any_unvalidated:
        print("✓ All dependency chains fully validated")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="needs-map",
        description="Component-needs audit model for project evaluation.",
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    # Component CRUD
    p = sub.add_parser("add-component", help="Create a component")
    p.add_argument("description", nargs="+")
    p.set_defaults(func=_cmd_add_component)

    p = sub.add_parser("set-component", help="Update component description")
    p.add_argument("id")
    p.add_argument("description", nargs="+")
    p.set_defaults(func=_cmd_set_component)

    p = sub.add_parser("remove-component", help="Remove a component and its edges")
    p.add_argument("id")
    p.set_defaults(func=_cmd_remove_component)

    # Need CRUD
    p = sub.add_parser("add-need", help="Create a root need")
    p.add_argument("description", nargs="+")
    p.set_defaults(func=_cmd_add_need)

    p = sub.add_parser("refine", help="Add a child need under an existing parent")
    p.add_argument("parent")
    p.add_argument("description", nargs="+")
    p.set_defaults(func=_cmd_refine)

    p = sub.add_parser("set-need", help="Update need description")
    p.add_argument("id")
    p.add_argument("description", nargs="+")
    p.set_defaults(func=_cmd_set_need)

    p = sub.add_parser("set-parent", help="Re-parent a need (use `root` to detach)")
    p.add_argument("id")
    p.add_argument("parent")
    p.set_defaults(func=_cmd_set_parent)

    p = sub.add_parser("remove-need", help="Remove a childless need")
    p.add_argument("id")
    p.set_defaults(func=_cmd_remove_need)

    # Edges
    p = sub.add_parser("depend", help="Record a dependency between components")
    p.add_argument("component")
    p.add_argument("dependency")
    p.set_defaults(func=_cmd_depend)

    p = sub.add_parser("undepend", help="Remove a dependency edge")
    p.add_argument("component")
    p.add_argument("dependency")
    p.set_defaults(func=_cmd_undepend)

    p = sub.add_parser("address", help="Record that a component addresses a need")
    p.add_argument("component")
    p.add_argument("need")
    p.add_argument("rationale", nargs="+")
    p.set_defaults(func=_cmd_address)

    p = sub.add_parser("unaddress", help="Remove an addressing edge")
    p.add_argument("component")
    p.add_argument("need")
    p.set_defaults(func=_cmd_unaddress)

    p = sub.add_parser("set-rationale", help="Update rationale on an existing edge")
    p.add_argument("component")
    p.add_argument("need")
    p.add_argument("rationale", nargs="+")
    p.set_defaults(func=_cmd_set_rationale)

    # Paths
    p = sub.add_parser("add-path", help="Record a source-location path")
    p.add_argument("component")
    p.add_argument("path")
    p.set_defaults(func=_cmd_add_path)

    p = sub.add_parser("remove-path", help="Remove a recorded path")
    p.add_argument("component")
    p.add_argument("path")
    p.set_defaults(func=_cmd_remove_path)

    # Validation
    p = sub.add_parser("validate", help="Mark a component or need as validated")
    p.add_argument("id")
    p.set_defaults(func=_cmd_validate)

    p = sub.add_parser("invalidate", help="Revert validation")
    p.add_argument("id")
    p.set_defaults(func=_cmd_invalidate)

    # Analysis
    p = sub.add_parser("dependencies", help="Dependency tree view")
    p.add_argument("component", nargs="?")
    p.add_argument("--verify", action="store_true",
                   help="Report unvalidated dependency ancestors")
    p.set_defaults(func=_cmd_dependencies)

    p = sub.add_parser("needs", help="Need tree with coverage markers")
    p.add_argument("root", nargs="?")
    p.set_defaults(func=_cmd_needs)

    p = sub.add_parser("addresses", help="Addressing graph and specialty views")
    p.add_argument("entity", nargs="?")
    p.add_argument("--gaps", action="store_true",
                   help="List unaddressed leaf needs")
    p.add_argument("--orphans", action="store_true",
                   help="List components addressing nothing")
    p.set_defaults(func=_cmd_addresses)

    p = sub.add_parser("where", help="Show source-location paths for a component")
    p.add_argument("component")
    p.set_defaults(func=_cmd_where)

    p = sub.add_parser("why", help="What needs does this component address?")
    p.add_argument("component")
    p.set_defaults(func=_cmd_why)

    p = sub.add_parser("how", help="What addresses this need?")
    p.add_argument("need")
    p.set_defaults(func=_cmd_how)

    p = sub.add_parser("compare", help="Side-by-side addressing comparison")
    p.add_argument("a")
    p.add_argument("b")
    p.set_defaults(func=_cmd_compare)

    p = sub.add_parser("summary", help="High-level counts and gap status")
    p.set_defaults(func=_cmd_summary)

    p = sub.add_parser("uncovered", help="Git-tracked files not attached to a component")
    p.set_defaults(func=_cmd_uncovered)

    # Lifecycle — does not require a ready DB.
    p = sub.add_parser(
        "reset",
        help="Backup, wipe, and rebuild the needs-map database",
    )
    p.set_defaults(func=_cmd_reset, needs_conn=False)

    return parser


def _cmd_reset(conn_unused, args: argparse.Namespace) -> None:
    """Wipe the needs-map DB and rebuild empty. Always backs up first."""
    result = _init.reset()
    for entry in result["files"]:
        if entry["before"] == entry["after"]:
            print(f"{entry['path']}: {entry['after']}")
        else:
            print(f"{entry['path']}: {entry['before']} → {entry['after']}")
    for extra in result["extra"]:
        print(f"{extra['label']}: {extra['value']}")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if getattr(args, "needs_conn", True):
            conn = _connect()
            try:
                args.func(conn, args)
            finally:
                conn.close()
        else:
            args.func(None, args)
    except (LookupError, ValueError, NotReadyError, InitError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

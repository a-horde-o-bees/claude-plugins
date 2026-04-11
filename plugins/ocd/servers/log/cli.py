"""Log CLI.

Presentation layer — argument parsing and dispatch wrappers only. Business
logic lives in the package facade (`from . import log_add, ...`). The CLI
mirrors the MCP tool surface for interactive debugging and bulk operations.
"""

import argparse
import json
import sys

from . import (
    log_add,
    log_get,
    log_list,
    log_remove,
    log_search,
    log_update,
    tag_add,
    tag_list,
    tag_remove,
    tag_update,
    type_add,
    type_list,
    type_remove,
    type_update,
)

DEFAULT_DB = ".claude/ocd/log/log.db"


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=False))


def _print_records(entries: list[dict]) -> None:
    if not entries:
        print("No records.")
        return
    for e in entries:
        tags = f"  [{', '.join(e.get('tags', []))}]" if e.get("tags") else ""
        detail_marker = " *" if e.get("has_detail") else ""
        print(f"  {e['id']:4}  {e['log_type']:12}  {e['summary']}{detail_marker}{tags}")


# --- Record dispatch ---


def _dispatch_add(args: argparse.Namespace) -> None:
    result = log_add(
        args.db,
        log_type=args.type,
        summary=args.summary,
        detail_md=args.detail,
        tags=args.tag or None,
    )
    _print_json(result)


def _dispatch_list(args: argparse.Namespace) -> None:
    result = log_list(
        args.db,
        log_type=args.type,
        tags=args.tag or None,
        limit=args.limit,
    )
    print(f"{result['total']} record(s):")
    _print_records(result["entries"])


def _dispatch_search(args: argparse.Namespace) -> None:
    result = log_search(
        args.db,
        pattern=args.pattern,
        log_type=args.type,
        tags=args.tag or None,
    )
    print(f"{result['total']} match(es):")
    _print_records(result["entries"])


def _dispatch_get(args: argparse.Namespace) -> None:
    result = log_get(args.db, ids=args.ids)
    _print_json(result)


def _dispatch_update(args: argparse.Namespace) -> None:
    result = log_update(
        args.db,
        id=args.id,
        summary=args.summary,
        detail_md=args.detail,
        tags=args.tag if args.tag is not None else None,
    )
    _print_json(result)


def _dispatch_remove(args: argparse.Namespace) -> None:
    result = log_remove(args.db, id=args.id)
    _print_json(result)


# --- Type dispatch ---


def _dispatch_type_add(args: argparse.Namespace) -> None:
    result = type_add(args.db, name=args.name, instructions=args.instructions)
    _print_json(result)


def _dispatch_type_list(args: argparse.Namespace) -> None:
    result = type_list(args.db)
    types = result["types"]
    if not types:
        print("No types registered.")
        return
    for t in types:
        print(
            f"  {t['name']:16}  {t['record_count']:4} records  "
            f"{t['tag_count']:4} tags"
        )
    if args.verbose:
        for t in types:
            print(f"\n--- {t['name']} ---\n{t['instructions']}\n")


def _dispatch_type_update(args: argparse.Namespace) -> None:
    result = type_update(
        args.db, name=args.name, instructions=args.instructions, rename=args.rename,
    )
    _print_json(result)


def _dispatch_type_remove(args: argparse.Namespace) -> None:
    result = type_remove(args.db, name=args.name, force=args.force)
    _print_json(result)


# --- Tag dispatch ---


def _dispatch_tag_add(args: argparse.Namespace) -> None:
    result = tag_add(args.db, log_type=args.type, name=args.name)
    _print_json(result)


def _dispatch_tag_list(args: argparse.Namespace) -> None:
    result = tag_list(args.db, log_type=args.type)
    if "tags" in result:
        print(f"{result['log_type']}:")
        for t in result["tags"]:
            print(f"  {t['record_count']:4}  {t['name']}")
    else:
        for type_name, tags in result["by_type"].items():
            print(f"{type_name}:")
            if not tags:
                print("  (no tags)")
            for t in tags:
                print(f"  {t['record_count']:4}  {t['name']}")


def _dispatch_tag_update(args: argparse.Namespace) -> None:
    result = tag_update(args.db, log_type=args.type, old=args.old, new=args.new)
    _print_json(result)


def _dispatch_tag_remove(args: argparse.Namespace) -> None:
    result = tag_remove(args.db, log_type=args.type, name=args.name)
    _print_json(result)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for the log CLI."""
    db_parent = argparse.ArgumentParser(add_help=False)
    db_parent.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"Path to log database (default: {DEFAULT_DB})",
    )

    parser = argparse.ArgumentParser(
        prog="log",
        description=(
            "Project log — records across log types with per-type tag management.\n"
            "\n"
            "Record operations: add, list, search, get, update, remove\n"
            "Type management: type-add, type-list, type-update, type-remove\n"
            "Tag management:  tag-add, tag-list, tag-update, tag-remove"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)

    # Record commands
    add_p = commands.add_parser("add", help="Add a new record", parents=[db_parent])
    add_p.add_argument("--type", required=True, help="log_type (decision, friction, problem, idea, ...)")
    add_p.add_argument("--summary", required=True, help="One-line description")
    add_p.add_argument("--detail", default=None, help="Optional markdown detail")
    add_p.add_argument("--tag", action="append", default=[], help="Tag (repeatable)")
    add_p.set_defaults(_dispatch=_dispatch_add)

    list_p = commands.add_parser("list", help="List records as metadata", parents=[db_parent])
    list_p.add_argument("--type", default=None, help="Filter to one log_type")
    list_p.add_argument("--tag", action="append", default=[], help="Require tag (repeatable)")
    list_p.add_argument("--limit", type=int, default=None, help="Cap result count")
    list_p.set_defaults(_dispatch=_dispatch_list)

    search_p = commands.add_parser("search", help="Regex search records", parents=[db_parent])
    search_p.add_argument("pattern", help="Regex matched against summary and detail_md")
    search_p.add_argument("--type", default=None, help="Filter to one log_type")
    search_p.add_argument("--tag", action="append", default=[], help="Require tag (repeatable)")
    search_p.set_defaults(_dispatch=_dispatch_search)

    get_p = commands.add_parser("get", help="Get full records by id", parents=[db_parent])
    get_p.add_argument("ids", nargs="+", type=int, help="Record ids to fetch")
    get_p.set_defaults(_dispatch=_dispatch_get)

    update_p = commands.add_parser("update", help="Update a record", parents=[db_parent])
    update_p.add_argument("id", type=int, help="Record id to update")
    update_p.add_argument("--summary", default=None, help="New summary")
    update_p.add_argument("--detail", default=None, help='New detail markdown (pass "" to clear)')
    update_p.add_argument("--tag", action="append", default=None, help="Replacement tag set (repeatable)")
    update_p.set_defaults(_dispatch=_dispatch_update)

    remove_p = commands.add_parser("remove", help="Remove a record by id", parents=[db_parent])
    remove_p.add_argument("id", type=int, help="Record id to remove")
    remove_p.set_defaults(_dispatch=_dispatch_remove)

    # Type commands
    type_add_p = commands.add_parser("type-add", help="Register a new log type", parents=[db_parent])
    type_add_p.add_argument("name", help="Type name")
    type_add_p.add_argument("instructions", help="Routing instructions")
    type_add_p.set_defaults(_dispatch=_dispatch_type_add)

    type_list_p = commands.add_parser("type-list", help="List log types with counts", parents=[db_parent])
    type_list_p.add_argument("-v", "--verbose", action="store_true", help="Include full instructions")
    type_list_p.set_defaults(_dispatch=_dispatch_type_list)

    type_update_p = commands.add_parser("type-update", help="Update or rename a type", parents=[db_parent])
    type_update_p.add_argument("name", help="Current type name")
    type_update_p.add_argument("--instructions", default=None, help="New routing instructions")
    type_update_p.add_argument("--rename", default=None, help="New type name")
    type_update_p.set_defaults(_dispatch=_dispatch_type_update)

    type_remove_p = commands.add_parser("type-remove", help="Remove a log type", parents=[db_parent])
    type_remove_p.add_argument("name", help="Type to remove")
    type_remove_p.add_argument("--force", action="store_true", help="Cascade-delete records and tags")
    type_remove_p.set_defaults(_dispatch=_dispatch_type_remove)

    # Tag commands
    tag_add_p = commands.add_parser("tag-add", help="Pre-declare a tag", parents=[db_parent])
    tag_add_p.add_argument("--type", required=True, help="log_type the tag belongs to")
    tag_add_p.add_argument("name", help="Tag name")
    tag_add_p.set_defaults(_dispatch=_dispatch_tag_add)

    tag_list_p = commands.add_parser("tag-list", help="List tags with counts", parents=[db_parent])
    tag_list_p.add_argument("--type", default=None, help="Filter to one log_type")
    tag_list_p.set_defaults(_dispatch=_dispatch_tag_list)

    tag_update_p = commands.add_parser("tag-update", help="Rename or merge a tag", parents=[db_parent])
    tag_update_p.add_argument("--type", required=True, help="log_type the tag belongs to")
    tag_update_p.add_argument("old", help="Current tag name")
    tag_update_p.add_argument("new", help="Target tag name")
    tag_update_p.set_defaults(_dispatch=_dispatch_tag_update)

    tag_remove_p = commands.add_parser("tag-remove", help="Strip a tag from all records", parents=[db_parent])
    tag_remove_p.add_argument("--type", required=True, help="log_type the tag belongs to")
    tag_remove_p.add_argument("name", help="Tag to remove")
    tag_remove_p.set_defaults(_dispatch=_dispatch_tag_remove)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "_dispatch"):
        try:
            args._dispatch(args)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

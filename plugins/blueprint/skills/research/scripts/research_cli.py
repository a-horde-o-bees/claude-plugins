"""Research CLI.

Agent-facing entry point for blueprint research database operations.
Business logic lives in _db.py, _templates.py, and research.py.
"""

import argparse
import sys

import _db as db  # type: ignore[import-not-found]
import _templates as templates  # type: ignore[import-not-found]
import research  # type: ignore[import-not-found]


# --- Dispatchers ---


def _dispatch_init(args: argparse.Namespace) -> None:
    print(db.init_db(args.db))


def _dispatch_register(args: argparse.Namespace) -> None:
    print(db.register_entity(
        args.db,
        name=args.name,
        url=args.url,
        source_url=args.source_url,
        relevance=args.relevance,
        description=args.description,
        role=args.role,
    ))


def _dispatch_normalize_url(args: argparse.Namespace) -> None:
    print(db.compute_normalize_url(args.url))


def _dispatch_update_entity(args: argparse.Namespace) -> None:
    ids = args.ids.split(",") if args.ids else None
    all_entities = getattr(args, "all", False)
    try:
        print(db.update_entity(
            args.db,
            ids=ids,
            all_entities=all_entities,
            stage=args.stage,
            relevance=args.relevance,
            description=args.description,
            name=args.name,
            role=args.role,
        ))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_upsert_notes(args: argparse.Namespace) -> None:
    try:
        print(db.upsert_notes(args.db, args.entity_id, args.notes))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_get_entity(args: argparse.Namespace) -> None:
    try:
        print(db.get_entity(args.db, args.id))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_list_entities(args: argparse.Namespace) -> None:
    print(db.list_entities(
        args.db,
        role=args.role,
        stage=args.stage,
        modified_before=getattr(args, "modified_before", None),
    ))


def _dispatch_stats(args: argparse.Namespace) -> None:
    print(db.get_stats(args.db))


def _dispatch_register_batch(args: argparse.Namespace) -> None:
    import json
    try:
        entities = json.loads(args.json)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    print(db.register_batch(args.db, entities, source_url=args.source_url))


def _dispatch_upsert_provenance(args: argparse.Namespace) -> None:
    try:
        print(db.upsert_provenance(args.db, args.entity_id, args.source_url))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_upsert_url(args: argparse.Namespace) -> None:
    try:
        print(db.upsert_url(args.db, args.entity_id, args.url))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_update_note(args: argparse.Namespace) -> None:
    try:
        print(db.update_note(args.db, args.note_id, args.note))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_remove_notes(args: argparse.Namespace) -> None:
    note_ids = args.note_ids.split(",")
    try:
        print(db.remove_notes(args.db, args.entity_id, note_ids))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_touch_entities(args: argparse.Namespace) -> None:
    ids = args.ids.split(",") if args.ids else None
    all_entities = getattr(args, "all", False)
    print(db.touch_entities(args.db, ids=ids, all_entities=all_entities))


def _dispatch_list_provenance(args: argparse.Namespace) -> None:
    print(db.list_provenance(args.db, entity_id=args.entity_id))


def _dispatch_list_reach(args: argparse.Namespace) -> None:
    print(db.list_reach(args.db, min_count=args.min))


def _dispatch_search_notes(args: argparse.Namespace) -> None:
    print(db.search_notes(args.db, args.pattern, stage=args.stage, min_relevance=args.min_relevance))


def _dispatch_export(args: argparse.Namespace) -> None:
    print(db.export_db(args.db, format=args.format))


def _dispatch_upsert_measures(args: argparse.Namespace) -> None:
    try:
        print(db.upsert_measures(args.db, args.entity_id, args.measures))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_get_measures(args: argparse.Namespace) -> None:
    print(db.get_measures(args.db))


def _dispatch_clear_measures(args: argparse.Namespace) -> None:
    print(db.clear_measures(args.db))


def _dispatch_find_duplicates(args: argparse.Namespace) -> None:
    print(db.find_duplicates(args.db, templates_db=getattr(args, "templates_db", None)))


def _dispatch_merge_entities(args: argparse.Namespace) -> None:
    ids = args.ids.split(",")
    try:
        print(db.merge_entities(args.db, ids))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_upsert_source_data(args: argparse.Namespace) -> None:
    try:
        print(db.upsert_source_data(args.db, args.entity_id, args.source_type, args.data))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_list_source_data(args: argparse.Namespace) -> None:
    print(db.list_source_data(
        args.db,
        source_type=getattr(args, "source_type", None),
        key=getattr(args, "key", None),
        entity_id=getattr(args, "entity_id", None),
    ))


# --- Template dispatchers ---


def _dispatch_init_templates(args: argparse.Namespace) -> None:
    print(templates.init_templates(args.templates_db))


def _dispatch_upsert_template_key(args: argparse.Namespace) -> None:
    print(templates.upsert_template_key(
        args.templates_db, args.source_type, args.key,
        format=args.format, description=args.description,
    ))


def _dispatch_update_source_type(args: argparse.Namespace) -> None:
    try:
        print(templates.update_source_type(
            args.templates_db, args.type,
            url_pattern=args.url_pattern, dedup_key=args.dedup_key, notes=args.notes,
        ))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_get_source_template(args: argparse.Namespace) -> None:
    try:
        print(templates.get_source_template(args.templates_db, args.source_type))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_list_source_templates(args: argparse.Namespace) -> None:
    print(templates.list_source_templates(args.templates_db))


def _dispatch_match_source_type(args: argparse.Namespace) -> None:
    try:
        print(templates.match_source_type(args.templates_db, args.url))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch_autofill_source_data(args: argparse.Namespace) -> None:
    print(research.autofill_source_data(
        args.db, args.templates_db,
        source_type_filter=args.source_type,
        entity_id_filter=args.entity_id,
        dry_run=args.dry_run,
    ))


# --- Parser ---


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="research_cli.py",
        description="Blueprint research database: entity tracking, notes, measures, and analysis.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    db_parent = argparse.ArgumentParser(add_help=False)
    db_parent.add_argument(
        "--db",
        default="references/research.db",
        help="Path to SQLite database (default: references/research.db)",
    )

    templates_db_parent = argparse.ArgumentParser(add_help=False)
    templates_db_parent.add_argument(
        "--templates-db",
        default=templates.TEMPLATES_DB_DEFAULT,
        help=f"Path to source templates database (default: {templates.TEMPLATES_DB_DEFAULT})",
    )

    # init
    init_p = commands.add_parser("init", help="Initialize database", parents=[db_parent])
    init_p.set_defaults(_dispatch=_dispatch_init)
    init_sub = init_p.add_subparsers(dest="init_type")
    init_templates_p = init_sub.add_parser("templates", help="Initialize templates database", parents=[templates_db_parent])
    init_templates_p.set_defaults(_dispatch=_dispatch_init_templates)

    # register
    register_p = commands.add_parser(
        "register",
        help="Register entity with URL dedup and optional provenance",
        parents=[db_parent],
    )
    register_p.add_argument("--name", required=True, help="Display name")
    register_p.add_argument("--url", default=None, help="Entity URL")
    register_p.add_argument("--source-url", default=None, help="Source URL where entity was found (provenance)")
    register_p.add_argument("--relevance", type=int, default=None, help="Relevance score (non-negative integer)")
    register_p.add_argument("--description", default=None, help="One-line summary")
    register_p.add_argument("--role", default=None, choices=["example", "directory", "context"], help="Entity role (default: example)")
    register_p.set_defaults(_dispatch=_dispatch_register)

    # register-batch
    register_batch_p = commands.add_parser(
        "register-batch",
        help="Register multiple entities in one call via JSON array",
        parents=[db_parent],
    )
    register_batch_p.add_argument("--json", required=True, help="JSON array of entity objects")
    register_batch_p.add_argument("--source-url", default=None, help="Default source URL for provenance")
    register_batch_p.set_defaults(_dispatch=_dispatch_register_batch)

    # normalize-url
    normalize_p = commands.add_parser("normalize-url", help="Compute normalized form of a URL")
    normalize_p.add_argument("url", help="URL to normalize")
    normalize_p.set_defaults(_dispatch=_dispatch_normalize_url)

    # export
    export_p = commands.add_parser("export", help="Export full database", parents=[db_parent])
    export_p.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    export_p.set_defaults(_dispatch=_dispatch_export)

    # find-duplicates
    find_dup_p = commands.add_parser("find-duplicates", help="Find duplicate entities by URL overlap", parents=[db_parent])
    find_dup_p.add_argument("--templates-db", default=None, help="Path to source templates database")
    find_dup_p.set_defaults(_dispatch=_dispatch_find_duplicates)

    # get (read queries)
    get_parser = commands.add_parser("get", help="Get detail or list collections")
    get_sub = get_parser.add_subparsers(dest="get_type", required=True)

    get_entity_p = get_sub.add_parser("entity", help="Entity detail", parents=[db_parent])
    get_entity_p.add_argument("id", help="Entity ID (e.g., e1)")
    get_entity_p.set_defaults(_dispatch=_dispatch_get_entity)

    get_entities_p = get_sub.add_parser("entities", help="List all entities", parents=[db_parent])
    get_entities_p.add_argument("--role", choices=["example", "directory", "context"], default=None, help="Filter by role")
    get_entities_p.add_argument("--stage", choices=["new", "rejected", "researched", "merged"], default=None, help="Filter by stage")
    get_entities_p.add_argument("--modified-before", default=None, help="Filter to entities modified before ISO 8601 timestamp")
    get_entities_p.set_defaults(_dispatch=_dispatch_list_entities)

    get_stats_p = get_sub.add_parser("stats", help="Database summary statistics", parents=[db_parent])
    get_stats_p.set_defaults(_dispatch=_dispatch_stats)

    get_template_p = get_sub.add_parser("template", help="Full template for one source type", parents=[templates_db_parent])
    get_template_p.add_argument("--source-type", required=True, help="Source type name")
    get_template_p.set_defaults(_dispatch=_dispatch_get_source_template)

    get_templates_p = get_sub.add_parser("templates", help="List all source types", parents=[templates_db_parent])
    get_templates_p.set_defaults(_dispatch=_dispatch_list_source_templates)

    get_measures_p = get_sub.add_parser("measures", help="Measure distributions", parents=[db_parent])
    get_measures_p.set_defaults(_dispatch=_dispatch_get_measures)

    get_source_data_p = get_sub.add_parser("source-data", help="List structured source data", parents=[db_parent])
    get_source_data_p.add_argument("--source-type", default=None, help="Filter by source type")
    get_source_data_p.add_argument("--key", default=None, help="Filter by key")
    get_source_data_p.add_argument("--entity-id", default=None, help="Filter by entity ID")
    get_source_data_p.set_defaults(_dispatch=_dispatch_list_source_data)

    get_provenance_p = get_sub.add_parser("provenance", help="List provenance relationships", parents=[db_parent])
    get_provenance_p.add_argument("--entity-id", default=None, help="Filter by entity ID")
    get_provenance_p.set_defaults(_dispatch=_dispatch_list_provenance)

    get_reach_p = get_sub.add_parser("reach", help="Entities ranked by provenance source count", parents=[db_parent])
    get_reach_p.add_argument("--min", type=int, default=0, help="Minimum source count")
    get_reach_p.set_defaults(_dispatch=_dispatch_list_reach)

    # upsert (insert or update)
    upsert_parser = commands.add_parser("upsert", help="Insert or update records")
    upsert_sub = upsert_parser.add_subparsers(dest="upsert_type", required=True)

    upsert_notes_p = upsert_sub.add_parser("notes", help="Add notes to entity, skips duplicates", parents=[db_parent])
    upsert_notes_p.add_argument("--entity-id", required=True, help="Entity ID")
    upsert_notes_p.add_argument("--notes", required=True, nargs="+", help="Note strings")
    upsert_notes_p.set_defaults(_dispatch=_dispatch_upsert_notes)

    upsert_provenance_p = upsert_sub.add_parser("provenance", help="Record provenance", parents=[db_parent])
    upsert_provenance_p.add_argument("--entity-id", required=True, help="Entity ID")
    upsert_provenance_p.add_argument("--source-url", required=True, help="Source URL where entity was found")
    upsert_provenance_p.set_defaults(_dispatch=_dispatch_upsert_provenance)

    upsert_url_p = upsert_sub.add_parser("url", help="Add URL to existing entity", parents=[db_parent])
    upsert_url_p.add_argument("--entity-id", required=True, help="Entity ID")
    upsert_url_p.add_argument("--url", required=True, help="URL to add")
    upsert_url_p.set_defaults(_dispatch=_dispatch_upsert_url)

    upsert_measures_p = upsert_sub.add_parser("measures", help="Add or update measures (key=value pairs)", parents=[db_parent])
    upsert_measures_p.add_argument("--entity-id", required=True, help="Entity ID")
    upsert_measures_p.add_argument("--measures", required=True, nargs="+", help="key=value pairs")
    upsert_measures_p.set_defaults(_dispatch=_dispatch_upsert_measures)

    upsert_template_key_p = upsert_sub.add_parser("template-key", help="Upsert key definition for source type", parents=[templates_db_parent])
    upsert_template_key_p.add_argument("--source-type", required=True, help="Source type name")
    upsert_template_key_p.add_argument("--key", required=True, help="Key name")
    upsert_template_key_p.add_argument("--format", default="text", help="Value format")
    upsert_template_key_p.add_argument("--description", default="", help="Key description")
    upsert_template_key_p.set_defaults(_dispatch=_dispatch_upsert_template_key)

    upsert_source_data_p = upsert_sub.add_parser("source-data", help="Upsert structured source data", parents=[db_parent])
    upsert_source_data_p.add_argument("--entity-id", required=True, help="Entity ID")
    upsert_source_data_p.add_argument("--source-type", required=True, help="Source type (e.g., github)")
    upsert_source_data_p.add_argument("--data", required=True, nargs="+", help="key=value pairs")
    upsert_source_data_p.set_defaults(_dispatch=_dispatch_upsert_source_data)

    # update (modify existing)
    update_parser = commands.add_parser("update", help="Update existing records")
    update_sub = update_parser.add_subparsers(dest="update_type", required=True)

    update_entities_p = update_sub.add_parser("entities", help="Update entity properties", parents=[db_parent])
    update_entities_ids = update_entities_p.add_mutually_exclusive_group(required=True)
    update_entities_ids.add_argument("--ids", help="Comma-separated entity IDs")
    update_entities_ids.add_argument("--all", action="store_true", help="All entities")
    update_entities_p.add_argument("--stage", default=None, choices=["new", "rejected", "researched"], help="Stage to set")
    update_entities_p.add_argument("--relevance", type=int, default=None, help="Relevance score")
    update_entities_p.add_argument("--description", default=None, help="One-line summary")
    update_entities_p.add_argument("--name", default=None, help="Entity display name")
    update_entities_p.add_argument("--role", default=None, choices=["example", "directory", "context"], help="Entity role")
    update_entities_p.set_defaults(_dispatch=_dispatch_update_entity)

    update_template_p = update_sub.add_parser("template", help="Update source type metadata", parents=[templates_db_parent])
    update_template_p.add_argument("--type", required=True, help="Source type name")
    update_template_p.add_argument("--url-pattern", default=None, help="URL pattern")
    update_template_p.add_argument("--dedup-key", default=None, help="JSON array of key names")
    update_template_p.add_argument("--notes", default=None, help="Notes about source type")
    update_template_p.set_defaults(_dispatch=_dispatch_update_source_type)

    update_note_p = update_sub.add_parser("note", help="Update a single note by ID", parents=[db_parent])
    update_note_p.add_argument("--note-id", required=True, help="Note ID (e.g., n5)")
    update_note_p.add_argument("--note", required=True, help="Replacement note text")
    update_note_p.set_defaults(_dispatch=_dispatch_update_note)

    # remove
    remove_parser = commands.add_parser("remove", help="Remove records")
    remove_sub = remove_parser.add_subparsers(dest="remove_type", required=True)

    remove_notes_p = remove_sub.add_parser("notes", help="Remove specific notes by ID", parents=[db_parent])
    remove_notes_p.add_argument("--entity-id", required=True, help="Entity ID")
    remove_notes_p.add_argument("--note-ids", required=True, help="Comma-separated note IDs")
    remove_notes_p.set_defaults(_dispatch=_dispatch_remove_notes)

    # clear
    clear_parser = commands.add_parser("clear", help="Clear data")
    clear_sub = clear_parser.add_subparsers(dest="clear_type", required=True)

    clear_measures_p = clear_sub.add_parser("measures", help="Clear all measures (for re-analysis)", parents=[db_parent])
    clear_measures_p.set_defaults(_dispatch=_dispatch_clear_measures)

    # touch
    touch_parser = commands.add_parser("touch", help="Mark as reviewed")
    touch_sub = touch_parser.add_subparsers(dest="touch_type", required=True)

    touch_entities_p = touch_sub.add_parser("entities", help="Mark entities as reviewed", parents=[db_parent])
    touch_entities_ids = touch_entities_p.add_mutually_exclusive_group(required=True)
    touch_entities_ids.add_argument("--ids", help="Comma-separated entity IDs")
    touch_entities_ids.add_argument("--all", action="store_true", help="All entities")
    touch_entities_p.set_defaults(_dispatch=_dispatch_touch_entities)

    # merge
    merge_parser = commands.add_parser("merge", help="Merge records")
    merge_sub = merge_parser.add_subparsers(dest="merge_type", required=True)

    merge_entities_p = merge_sub.add_parser("entities", help="Merge entities into lowest-ID survivor", parents=[db_parent])
    merge_entities_p.add_argument("--ids", required=True, help="Comma-separated entity IDs to merge")
    merge_entities_p.set_defaults(_dispatch=_dispatch_merge_entities)

    # search
    search_parser = commands.add_parser("search", help="Search across notes")
    search_sub = search_parser.add_subparsers(dest="search_type", required=True)

    search_notes_p = search_sub.add_parser("notes", help="Search notes by keyword", parents=[db_parent])
    search_notes_p.add_argument("--pattern", required=True, help="Search pattern")
    search_notes_p.add_argument("--stage", default=None, help="Filter by entity stage")
    search_notes_p.add_argument("--min-relevance", type=int, default=None, help="Minimum entity relevance")
    search_notes_p.set_defaults(_dispatch=_dispatch_search_notes)

    # autofill
    autofill_parser = commands.add_parser("autofill", help="Autofill data from external sources")
    autofill_sub = autofill_parser.add_subparsers(dest="autofill_type", required=True)

    autofill_sd_p = autofill_sub.add_parser("source-data", help="Autofill source data from external APIs", parents=[db_parent, templates_db_parent])
    autofill_sd_p.add_argument("--source-type", default=None, help="Only process this source type")
    autofill_sd_p.add_argument("--entity-id", default=None, help="Only process this entity")
    autofill_sd_p.add_argument("--dry-run", action="store_true", help="Show what would be fetched without writing")
    autofill_sd_p.set_defaults(_dispatch=_dispatch_autofill_source_data)

    # match
    match_parser = commands.add_parser("match", help="Match URL to source type")
    match_sub = match_parser.add_subparsers(dest="match_type", required=True)

    match_template_p = match_sub.add_parser("template", help="Check URL against url_patterns", parents=[templates_db_parent])
    match_template_p.add_argument("--url", required=True, help="URL to match")
    match_template_p.set_defaults(_dispatch=_dispatch_match_source_type)

    # Dispatch
    args = parser.parse_args()
    if hasattr(args, "_dispatch"):
        args._dispatch(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

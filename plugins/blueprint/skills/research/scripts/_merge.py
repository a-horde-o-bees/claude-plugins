"""Deduplication and merge operations."""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path

from ._db import _touch, get_connection, retry_write

logger = logging.getLogger(__name__)

__all__ = [
    "find_duplicates",
    "merge_entities",
]


def _union_find_groups(pairs: list[tuple[str, str]]) -> dict[str, set[str]]:
    """Build transitive groups from pairs using union-find."""
    entity_groups: dict[str, set[str]] = {}
    entity_to_group: dict[str, str] = {}

    for a, b in pairs:
        existing_reps = set()
        for eid in (a, b):
            if eid in entity_to_group:
                existing_reps.add(entity_to_group[eid])

        all_members: set[str] = {a, b}
        for rep in existing_reps:
            all_members.update(entity_groups.pop(rep))

        new_rep = min(all_members, key=lambda e: int(e[1:]))
        entity_groups[new_rep] = all_members
        for eid in all_members:
            entity_to_group[eid] = new_rep

    return {rep: members for rep, members in entity_groups.items() if len(members) > 1}


def find_duplicates(db_path: str, templates_db: str | None = None) -> str:
    """Find duplicate entities by URL overlap and source-data key matches.

    Detection only — does not merge. Reports transitive groups with evidence.
    """
    import json

    conn = get_connection(db_path)
    try:
        # URL overlap
        url_pairs: list[tuple[str, str]] = []
        url_evidence: dict[tuple[str, str], list[str]] = defaultdict(list)

        overlaps = conn.execute(
            "SELECT url, GROUP_CONCAT(entity_id) as entity_ids, COUNT(DISTINCT entity_id) as cnt "
            "FROM entity_urls GROUP BY url HAVING cnt > 1 ORDER BY url",
        ).fetchall()

        for row in overlaps:
            ids = sorted([x.strip() for x in row["entity_ids"].split(",")], key=lambda e: int(e[1:]))
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    pair = (ids[i], ids[j])
                    url_pairs.append(pair)
                    url_evidence[pair].append(f"URL match: {row['url']}")

        # Source-data dedup keys
        source_pairs: list[tuple[str, str]] = []
        source_evidence: dict[tuple[str, str], list[str]] = defaultdict(list)

        if templates_db and Path(templates_db).exists():
            conn.execute("ATTACH DATABASE ? AS templates", (templates_db,))

            rows = conn.execute(
                "SELECT esd.entity_id, esd.source_type, GROUP_CONCAT(esd.value, '|') AS dedup_value "
                "FROM entity_source_data esd "
                "JOIN templates.source_types st ON st.type = esd.source_type "
                "JOIN json_each(st.dedup_key) dk ON esd.key = dk.value "
                "GROUP BY esd.entity_id, esd.source_type",
            ).fetchall()

            sd_groups: dict = defaultdict(list)
            for r in rows:
                sd_groups[(r["source_type"], r["dedup_value"])].append(r["entity_id"])

            dedup_key_names: dict[str, list[str]] = {}
            for source_type_key, _ in sd_groups:
                if source_type_key not in dedup_key_names:
                    dk_row = conn.execute(
                        "SELECT dedup_key FROM templates.source_types WHERE type = ?",
                        (source_type_key,),
                    ).fetchone()
                    try:
                        dedup_key_names[source_type_key] = json.loads(dk_row["dedup_key"]) if dk_row else []
                    except json.JSONDecodeError:
                        dedup_key_names[source_type_key] = []

            for (source_type_key, dedup_value), entity_ids in sd_groups.items():
                if len(entity_ids) < 2:
                    continue
                ids = sorted(entity_ids, key=lambda e: int(e[1:]))
                key_names = dedup_key_names.get(source_type_key, [])
                values = dedup_value.split("|")
                label_parts = [f"{k}={v}" for k, v in zip(key_names, values)]
                label = ", ".join(label_parts) if label_parts else dedup_value
                for i in range(len(ids)):
                    for j in range(i + 1, len(ids)):
                        pair = (ids[i], ids[j])
                        source_pairs.append(pair)
                        source_evidence[pair].append(f"Source match ({source_type_key}): {label}")

        # Combine into transitive groups
        all_pairs = url_pairs + source_pairs
        if not all_pairs:
            return "No duplicates found."

        groups = _union_find_groups(all_pairs)
        if not groups:
            return "No duplicates found."

        all_evidence: dict[tuple[str, str], list[str]] = defaultdict(list)
        for pair, evs in url_evidence.items():
            all_evidence[pair].extend(evs)
        for pair, evs in source_evidence.items():
            all_evidence[pair].extend(evs)

        entity_info: dict[str, dict] = {}
        all_ids = {eid for members in groups.values() for eid in members}
        for eid in all_ids:
            row = conn.execute("SELECT id, name, stage, relevance FROM entities WHERE id = ?", (eid,)).fetchone()
            if row:
                notes_count = conn.execute("SELECT COUNT(*) FROM entity_notes WHERE entity_id = ?", (eid,)).fetchone()[0]
                entity_info[eid] = {"name": row["name"], "stage": row["stage"], "relevance": row["relevance"], "notes": notes_count}

        stage_icons = {"new": ".", "rejected": "x", "researched": "+", "merged": "~"}
        lines = [f"Duplicate groups ({len(groups)}):\n"]
        for group_idx, (_, members) in enumerate(sorted(groups.items(), key=lambda item: int(item[0][1:])), 1):
            sorted_members = sorted(members, key=lambda e: int(e[1:]))
            lines.append(f"  Group {group_idx}:")
            for eid in sorted_members:
                info = entity_info.get(eid, {})
                icon = stage_icons.get(info.get("stage", ""), "?")
                lines.append(f"    [{icon}] {eid} {info.get('name', '?')} (relevance: {info.get('relevance', '?')}, notes: {info.get('notes', '?')})")
            lines.append("    Evidence:")
            shown = set()
            for i in range(len(sorted_members)):
                for j in range(i + 1, len(sorted_members)):
                    pair = (sorted_members[i], sorted_members[j])
                    if pair in all_evidence:
                        for ev in all_evidence[pair]:
                            ev_key = (pair, ev)
                            if ev_key not in shown:
                                lines.append(f"      {pair[0]}-{pair[1]}: {ev}")
                                shown.add(ev_key)
            lines.append("")

        lines.append(f"Found {len(groups)} duplicate groups containing {sum(len(m) for m in groups.values())} entities.")
        return "\n".join(lines)
    finally:
        conn.close()


@retry_write
def merge_entities(db_path: str, ids: list[str]) -> str:
    """Merge multiple entities into lowest-ID survivor. Fully mechanical."""
    if len(ids) < 2:
        raise ValueError("Merge requires at least 2 entity IDs")

    entity_ids_sorted = sorted(ids, key=lambda x: int(x[1:]))
    survivor_id = entity_ids_sorted[0]
    absorbed_ids = entity_ids_sorted[1:]

    conn = get_connection(db_path)
    try:
        entities = {}
        for eid in entity_ids_sorted:
            row = conn.execute("SELECT id, name, description FROM entities WHERE id = ?", (eid,)).fetchone()
            if not row:
                raise ValueError(f"Entity not found: {eid}")
            entities[eid] = row

        with conn:
            for source_id in absorbed_ids:
                conn.execute(
                    "INSERT OR IGNORE INTO entity_urls (entity_id, url) SELECT ?, url FROM entity_urls WHERE entity_id = ?",
                    (survivor_id, source_id),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) SELECT source_url, ? FROM url_provenance WHERE entity_id = ?",
                    (survivor_id, source_id),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO entity_source_data (entity_id, source_type, key, value) SELECT ?, source_type, key, value FROM entity_source_data WHERE entity_id = ?",
                    (survivor_id, source_id),
                )
                conn.execute("UPDATE entity_notes SET entity_id = ? WHERE entity_id = ?", (survivor_id, source_id))

                conn.execute("DELETE FROM entity_urls WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM url_provenance WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM entity_source_data WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM entity_measures WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM entities WHERE id = ?", (source_id,))

            absorbed_descriptions = [entities[eid]["description"] for eid in absorbed_ids if entities[eid]["description"]]
            if absorbed_descriptions:
                survivor_desc = entities[survivor_id]["description"] or ""
                combined = "\n".join([survivor_desc] + absorbed_descriptions) if survivor_desc else "\n".join(absorbed_descriptions)
                conn.execute("UPDATE entities SET description = ? WHERE id = ?", (combined, survivor_id))

            conn.execute("UPDATE entities SET relevance = NULL, stage = 'merged' WHERE id = ?", (survivor_id,))
            conn.execute("DELETE FROM entity_measures WHERE entity_id = ?", (survivor_id,))
            _touch(conn, "entities", survivor_id)

        absorbed_names = [f"{entities[eid]['name']} ({eid})" for eid in absorbed_ids]
        return f"Merged {', '.join(absorbed_names)} into {entities[survivor_id]['name']} ({survivor_id})"
    finally:
        conn.close()

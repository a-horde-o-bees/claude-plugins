"""Blueprint research facade.

Public interface for all research database operations. CLI and external
consumers import from this module. Cross-database operations (autofill)
and domain module re-exports live here.
"""

from __future__ import annotations

import json
import logging
import subprocess
from collections.abc import Callable
from pathlib import Path

from . import _db as db
from . import _templates as templates

# Re-export domain modules — CLI imports from research, not from internal modules.
from ._db import get_connection, init_db, normalize_url, retry_write  # noqa: F401
from ._entities import *  # noqa: F401,F403
from ._measures import *  # noqa: F401,F403
from ._merge import *  # noqa: F401,F403
from ._notes import *  # noqa: F401,F403
from ._provenance import *  # noqa: F401,F403
from ._search import *  # noqa: F401,F403
from ._source_data import *  # noqa: F401,F403
from ._criteria import *  # noqa: F401,F403

logger = logging.getLogger(__name__)


# --- GitHub handler ---


def _parse_github_owner_repo(url: str) -> tuple[str, str] | None:
    """Extract owner/repo from normalized GitHub URL."""
    parts = url.split("/")
    if len(parts) >= 3 and parts[0] == "github.com":
        return parts[1], parts[2]
    return None


def fetch_github(url: str) -> dict[str, str] | None:
    """Fetch GitHub repo metadata via gh API. Returns dict of template keys or None."""
    parsed = _parse_github_owner_repo(url)
    if not parsed:
        return None
    owner, repo = parsed

    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "404" in stderr or "Not Found" in stderr:
            return {"_error": "repository not found (404)"}
        if "403" in stderr:
            return {"_error": "access denied (403)"}
        return {"_error": stderr[:200]}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"_error": "invalid JSON response"}

    license_info = data.get("license") or {}
    source_data = {
        "repo_id": str(data.get("id", "")),
        "stars": str(data.get("stargazers_count", 0)),
        "forks": str(data.get("forks_count", 0)),
        "pushed_at": data.get("pushed_at", "")[:10],
        "created_at": data.get("created_at", "")[:10],
        "size_kb": str(data.get("size", 0)),
        "license": license_info.get("spdx_id") or "none",
        "default_branch": data.get("default_branch", "main"),
        "archived": str(data.get("archived", False)).lower(),
        "language": data.get("language") or "none",
    }

    default_branch = source_data["default_branch"]
    sha_result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/commits/{default_branch}", "--jq", ".sha"],
        capture_output=True, text=True,
    )
    if sha_result.returncode == 0:
        source_data["head_sha"] = sha_result.stdout.strip()[:12]
    else:
        source_data["head_sha"] = "unavailable"

    return source_data


# Handler registry: source_type -> fetch function
HANDLERS: dict[str, Callable[[str], dict[str, str] | None]] = {
    "github": fetch_github,
}


# --- Autofill ---


def _match_source_type(url: str, source_types: list[dict]) -> str | None:
    """Match normalized URL against source type patterns."""
    for st in source_types:
        pattern = st["url_pattern"].rstrip("*").rstrip("/")
        if pattern and url.startswith(pattern):
            return st["type"]
    return None


def _write_source_data(entity_id: str, source_type: str, data: dict[str, str], db_path: str) -> bool:
    """Write source data to research DB. Returns True on success."""
    pairs = [f"{k}={v}" for k, v in data.items() if not k.startswith("_")]
    if not pairs:
        return False
    try:
        upsert_source_data(db_path, entity_id, source_type, pairs)
        return True
    except Exception as e:
        logger.error("Write error for %s/%s: %s", entity_id, source_type, str(e))
        return False


def autofill_source_data(
    db_path: str,
    templates_db: str,
    source_type_filter: str | None = None,
    entity_id_filter: str | None = None,
    dry_run: bool = False,
) -> str:
    """Autofill structured source data by matching entity URLs against templates."""
    if not Path(db_path).exists():
        return f"Error: Research database not found: {db_path}"
    if not Path(templates_db).exists():
        return f"Error: Templates database not found: {templates_db}"

    # Load source types
    tpl_conn = templates.get_templates_connection(templates_db)
    source_types = [
        dict(r) for r in tpl_conn.execute(
            "SELECT type, url_pattern FROM source_types WHERE url_pattern != ''",
        ).fetchall()
    ]
    if source_type_filter:
        source_types = [st for st in source_types if st["type"] == source_type_filter]
        if not source_types:
            tpl_conn.close()
            return f"Error: Source type '{source_type_filter}' not found or has no URL pattern"

    expected_keys: dict[str, set[str]] = {}
    for st in source_types:
        rows = tpl_conn.execute(
            "SELECT key FROM source_type_keys WHERE source_type = ?", (st["type"],),
        ).fetchall()
        expected_keys[st["type"]] = {r["key"] for r in rows}
    tpl_conn.close()

    active_types = [st for st in source_types if st["type"] in HANDLERS]
    if not active_types:
        return "No handlers available for configured source types."

    # Load entities
    res_conn = db.get_connection(db_path)

    entity_filter = ""
    entity_params: list[str] = []
    if entity_id_filter:
        entity_filter = " WHERE e.id = ?"
        entity_params = [entity_id_filter]

    entities = res_conn.execute(
        f"SELECT e.id, e.name, e.stage FROM entities e{entity_filter} "
        f"ORDER BY CAST(SUBSTR(e.id, 2) AS INTEGER)",
        entity_params,
    ).fetchall()

    if not entities:
        res_conn.close()
        return "No entities to process."

    entity_urls: dict[str, list[str]] = {}
    for e in entities:
        urls = res_conn.execute(
            "SELECT url FROM entity_urls WHERE entity_id = ? ORDER BY id", (e["id"],),
        ).fetchall()
        entity_urls[e["id"]] = [r["url"] for r in urls]

    existing_data: dict[str, dict[str, set[str]]] = {}
    for e in entities:
        existing_data[e["id"]] = {}
        rows = res_conn.execute(
            "SELECT source_type, key FROM entity_source_data WHERE entity_id = ?", (e["id"],),
        ).fetchall()
        for r in rows:
            existing_data[e["id"]].setdefault(r["source_type"], set()).add(r["key"])

    res_conn.close()

    # Process
    total = len(entities)
    fetched = 0
    skipped_complete = 0
    skipped_no_match = 0
    errors = 0

    type_names = ", ".join(st["type"] for st in active_types)
    mode = " (dry run)" if dry_run else ""
    output_lines = [f"Processing {total} entities against {len(active_types)} source types ({type_names}){mode}...\n"]

    for idx, entity in enumerate(entities, 1):
        eid = entity["id"]
        name = entity["name"]
        urls = entity_urls.get(eid, [])

        matches: dict[str, str] = {}
        for url in urls:
            matched_type = _match_source_type(url, active_types)
            if matched_type and matched_type not in matches:
                matches[matched_type] = url

        if not matches:
            skipped_no_match += 1
            continue

        for st, url in matches.items():
            expected = expected_keys.get(st, set())
            existing = existing_data.get(eid, {}).get(st, set())
            missing = expected - existing

            if not missing:
                output_lines.append(f"[{idx}/{total}] {eid} {name} -- all {len(expected)} {st} keys present, skipping")
                skipped_complete += 1
                continue

            output_lines.append(f"[{idx}/{total}] {eid} {name} ({url})")
            output_lines.append(f"    Missing {len(missing)}/{len(expected)} {st} keys: {', '.join(sorted(missing))}")

            if dry_run:
                fetched += 1
                continue

            handler = HANDLERS[st]
            data = handler(url)

            if data is None:
                output_lines.append("    Handler returned no data")
                errors += 1
                continue

            if "_error" in data:
                output_lines.append(f"    Error: {data['_error']}")
                errors += 1
                continue

            if _write_source_data(eid, st, data, db_path):
                written = len([k for k in data if not k.startswith("_")])
                output_lines.append(f"    Wrote {written} {st} fields")
                fetched += 1
            else:
                errors += 1

    output_lines.append(f"\nComplete:")
    output_lines.append(f"  Fetched: {fetched}")
    output_lines.append(f"  Skipped (complete): {skipped_complete}")
    output_lines.append(f"  Skipped (no match): {skipped_no_match}")
    output_lines.append(f"  Errors: {errors}")

    return "\n".join(output_lines)

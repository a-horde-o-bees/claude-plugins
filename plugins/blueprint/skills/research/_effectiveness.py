"""Criteria effectiveness computation.

Deterministic metrics evaluating how well assessment criteria perform —
which criteria drive decisions, which never trigger, which produce
surprising results. All computed from criterion-note links and entity data.
"""

from __future__ import annotations

from . import _db as _core

get_connection = _core.get_connection


def get_criteria_effectiveness(db_path: str) -> str:
    """Compute criteria effectiveness metrics. Deterministic — all from database state.

    Returns per-criterion: pass/fail/not-assessed counts, hit rate,
    hardline rejection distribution, untriggered criteria.
    """
    conn = get_connection(db_path)
    try:
        # All criteria
        criteria = conn.execute(
            "SELECT id, type, name, gate FROM criteria ORDER BY id",
        ).fetchall()
        if not criteria:
            return "No criteria defined."

        # Total non-rejected entities for denominator
        total_entities = conn.execute(
            "SELECT COUNT(*) as cnt FROM entities WHERE stage != 'rejected'",
        ).fetchone()["cnt"]

        # Per-criterion stats
        lines = [f"Criteria effectiveness ({len(criteria)} criteria, {total_entities} active entities):"]
        lines.append("")

        hardline_rejections = []
        untriggered = []

        for c in criteria:
            cid = c["id"]
            ctype = c["type"]
            cname = c["name"]

            # Count distinct entities with pass links for this criterion
            pass_row = conn.execute(
                "SELECT COUNT(DISTINCT en.entity_id) as cnt "
                "FROM criteria_notes cn "
                "JOIN entity_notes en ON en.id = cn.note_id "
                "WHERE cn.criterion_id = ? AND cn.quality = 'pass'",
                (cid,),
            ).fetchone()
            pass_count = pass_row["cnt"]

            # Count distinct entities with only fail links (no pass) for this criterion
            fail_row = conn.execute(
                "SELECT COUNT(DISTINCT en.entity_id) as cnt "
                "FROM criteria_notes cn "
                "JOIN entity_notes en ON en.id = cn.note_id "
                "WHERE cn.criterion_id = ? AND cn.quality = 'fail' "
                "AND en.entity_id NOT IN ("
                "  SELECT DISTINCT en2.entity_id "
                "  FROM criteria_notes cn2 "
                "  JOIN entity_notes en2 ON en2.id = cn2.note_id "
                "  WHERE cn2.criterion_id = ? AND cn2.quality = 'pass'"
                ")",
                (cid, cid),
            ).fetchone()
            fail_count = fail_row["cnt"]

            assessed = pass_count + fail_count
            not_assessed = max(0, total_entities - assessed)
            hit_rate = round(pass_count / assessed, 2) if assessed > 0 else None

            # Track hardline rejections
            if ctype == "hardline":
                # Count entities rejected where this criterion was the reason
                reject_count = conn.execute(
                    "SELECT COUNT(DISTINCT en.entity_id) as cnt "
                    "FROM criteria_notes cn "
                    "JOIN entity_notes en ON en.id = cn.note_id "
                    "JOIN entities e ON e.id = en.entity_id AND e.stage = 'rejected' "
                    "WHERE cn.criterion_id = ? AND cn.quality = 'fail'",
                    (cid,),
                ).fetchone()["cnt"]
                if reject_count > 0:
                    hardline_rejections.append((cid, cname, reject_count))

            # Track untriggered
            if assessed == 0:
                untriggered.append((cid, cname))

            hit_str = f"{hit_rate:.0%}" if hit_rate is not None else "n/a"
            lines.append(
                f"  {cid}. [{ctype}] {cname}: "
                f"pass={pass_count}, fail={fail_count}, not assessed={not_assessed}, "
                f"hit rate={hit_str}"
            )

        # Discrimination: avg relevance of pass vs fail entities per relevancy criterion
        lines.append("")
        lines.append("Discrimination (relevancy criteria only):")
        for c in criteria:
            if c["type"] != "relevancy":
                continue
            cid = c["id"]

            pass_avg = conn.execute(
                "SELECT AVG(e.relevance) as avg_rel "
                "FROM criteria_notes cn "
                "JOIN entity_notes en ON en.id = cn.note_id "
                "JOIN entities e ON e.id = en.entity_id AND e.stage != 'rejected' "
                "WHERE cn.criterion_id = ? AND cn.quality = 'pass'",
                (cid,),
            ).fetchone()

            fail_avg = conn.execute(
                "SELECT AVG(e.relevance) as avg_rel "
                "FROM criteria_notes cn "
                "JOIN entity_notes en ON en.id = cn.note_id "
                "JOIN entities e ON e.id = en.entity_id AND e.stage != 'rejected' "
                "WHERE cn.criterion_id = ? AND cn.quality = 'fail' "
                "AND en.entity_id NOT IN ("
                "  SELECT DISTINCT en2.entity_id "
                "  FROM criteria_notes cn2 "
                "  JOIN entity_notes en2 ON en2.id = cn2.note_id "
                "  WHERE cn2.criterion_id = ? AND cn2.quality = 'pass'"
                ")",
                (cid, cid),
            ).fetchone()

            p = round(pass_avg["avg_rel"], 1) if pass_avg and pass_avg["avg_rel"] is not None else "n/a"
            f = round(fail_avg["avg_rel"], 1) if fail_avg and fail_avg["avg_rel"] is not None else "n/a"
            lines.append(f"  {cid}. {c['name']}: pass avg relevance={p}, fail avg relevance={f}")

        # Hardline rejection summary
        if hardline_rejections:
            lines.append("")
            lines.append("Hardline rejection distribution:")
            for cid, cname, count in sorted(hardline_rejections, key=lambda x: -x[2]):
                lines.append(f"  {cid}. {cname}: {count} rejections")

        # Untriggered
        if untriggered:
            lines.append("")
            lines.append("Untriggered criteria (no entities assessed):")
            for cid, cname in untriggered:
                lines.append(f"  {cid}. {cname}")

        return "\n".join(lines)
    finally:
        conn.close()

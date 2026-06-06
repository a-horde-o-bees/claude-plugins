"""Content hash-reference extraction and expansion (the `refs` table).

Claude Code injects deterministic-marker content — skill bodies, available-
skills lists, hook output — into the conversation stream verbatim on every
firing. The same skill body is stored once per invocation across sessions and
projects, inflating both DB size and any read-time context. This module
extracts such repeated content into a hash-keyed `refs` table and rewrites
`events.text` to carry a `[[ref:<hash>]]` token in its place.

Two independent wins (see `plans/transcripts.md` Workstream B):

- **Storage-time** — ingest substitutes refs as rows land; `events.text`
  holds the rewritten text. Mechanical, uncontested.
- **Read-time** — `exchanges --show messages` returns ref-substituted text by
  default; a consumer opts into expansion via `--expand-refs`. Conditional on
  agent dereference discipline (the B3 empirical question).

Design invariants:

- **Deterministic markers only.** Each pattern has a mechanical marker; no
  fuzzy similarity. Every pattern is documented in `extraction-patterns.md`
  before it ships.
- **Idempotent.** `extract` is a no-op on text whose body is already a
  `[[ref:...]]` token, so re-running ingest or backfill never double-extracts.
- **Safe failure.** An unresolved `[[ref:...]]` token renders as literal text;
  a broken ref never corrupts downstream consumption.
"""

import hashlib
import re
import sqlite3


# Pattern 1 — skill body injections. Marker: the leading line
# `Base directory for this skill: <path>`. The marker line is per-message
# identifying context and stays in events.text verbatim; only the body that
# follows it becomes the ref. See extraction-patterns.md.
SKILL_MARKER = "Base directory for this skill: "

# A body that is already exactly a ref token — the substituted form. Guards
# idempotency: such a body is never re-extracted.
_REF_TOKEN_RE = re.compile(r"^\[\[ref:[0-9a-f]+\]\]$")

# Inline ref token, for read-side expansion. Matches anywhere in a message.
_REF_INLINE_RE = re.compile(r"\[\[ref:([0-9a-f]+)\]\]")


def _canonicalize(body: str) -> str:
    """Canonical form of an extracted body, so identical content hashes alike.

    Normalize line endings to `\\n`, strip trailing whitespace per line, and
    strip leading/trailing blank lines. Two payloads equal by meaning collapse
    to one hash; two that differ in real content do not.
    """
    text = body.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip("\n")


def extract(text: str | None) -> tuple[str | None, str | None, str | None]:
    """Apply extraction patterns to one message body.

    Returns `(rewritten_text, hash, payload)`. On no match — or on text whose
    body is already a `[[ref:...]]` token — returns `(text, None, None)` so the
    caller writes the text unchanged.
    """
    if text is None or not text.startswith(SKILL_MARKER):
        return text, None, None
    parts = text.split("\n", 1)
    if len(parts) != 2:
        return text, None, None
    marker_line, body_raw = parts
    payload = _canonicalize(body_raw)
    if not payload or _REF_TOKEN_RE.match(payload):
        return text, None, None  # empty body or already substituted
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    rewritten = f"{marker_line}\n\n[[ref:{h}]]"
    return rewritten, h, payload


def upsert_ref(
    conn: sqlite3.Connection, h: str, payload: str, first_seen: str,
) -> None:
    """Record a ref payload, incrementing hit_count on repeat.

    Call once per event that gets substituted — ingest does this only for
    newly-inserted rows, and backfill only for rows it actually rewrites, so
    hit_count tracks the number of distinct events carrying the hash.
    """
    conn.execute(
        """
        INSERT INTO refs (hash, payload, byte_size, first_seen, hit_count)
        VALUES (?, ?, ?, ?, 1)
        ON CONFLICT(hash) DO UPDATE SET hit_count = hit_count + 1
        """,
        (h, payload, len(payload.encode("utf-8")), first_seen),
    )


def expand_text(
    conn: sqlite3.Connection, text: str | None, which: str | set[str],
) -> str | None:
    """Substitute `[[ref:<hash>]]` tokens back to their payloads.

    `which` is the literal `"all"` or a set of hashes to expand (others left
    as tokens). A token whose hash isn't in `refs` is left literal — the safe
    failure mode.
    """
    if text is None or "[[ref:" not in text:
        return text

    def repl(m: re.Match) -> str:
        h = m.group(1)
        if which != "all" and h not in which:
            return m.group(0)
        row = conn.execute(
            "SELECT payload FROM refs WHERE hash = ?", (h,)
        ).fetchone()
        return row[0] if row else m.group(0)

    return _REF_INLINE_RE.sub(repl, text)


def parse_expand_refs(value: str | None) -> str | set[str]:
    """Parse the `--expand-refs` argument into `"all"`, `"none"`, or a hash set."""
    if not value or value == "none":
        return set()
    if value == "all":
        return "all"
    return {h.strip() for h in value.split(",") if h.strip()}


def backfill(conn: sqlite3.Connection) -> int:
    """Apply current extraction patterns to existing events.text in place.

    One-shot pass for DBs ingested before extraction shipped. Idempotent —
    already-substituted rows match the marker LIKE but `extract` returns no
    hash for them, so re-running is a no-op. Returns the count of rows rewritten.
    """
    rows = conn.execute(
        "SELECT file, line, ts, text FROM events WHERE text LIKE ?",
        (SKILL_MARKER + "%",),
    ).fetchall()
    updated = 0
    for file, line, ts, text in rows:
        rewritten, h, payload = extract(text)
        if h is None or payload is None:
            continue
        upsert_ref(conn, h, payload, ts)
        conn.execute(
            "UPDATE events SET text = ? WHERE file = ? AND line = ?",
            (rewritten, file, line),
        )
        updated += 1
    conn.commit()
    return updated


def list_refs(conn: sqlite3.Connection, limit: int = 50) -> dict:
    """Summarize the refs table: counts, total bytes saved, top refs by reuse."""
    total = conn.execute("SELECT COUNT(*) FROM refs").fetchone()[0]
    agg = conn.execute(
        "SELECT COALESCE(SUM(byte_size), 0), COALESCE(SUM(byte_size * (hit_count - 1)), 0) "
        "FROM refs"
    ).fetchone()
    rows = conn.execute(
        """
        SELECT hash, byte_size, hit_count, first_seen, substr(payload, 1, 120)
        FROM refs ORDER BY byte_size * hit_count DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return {
        "n_refs": total,
        "unique_bytes": agg[0],
        "dedup_bytes_saved": agg[1],
        "refs": [
            {
                "hash": h,
                "byte_size": bs,
                "hit_count": hc,
                "first_seen": fs,
                "payload_preview": preview,
            }
            for h, bs, hc, fs, preview in rows
        ],
    }

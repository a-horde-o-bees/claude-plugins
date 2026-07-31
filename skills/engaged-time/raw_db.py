#!/usr/bin/env python3
"""Load raw transcript JSONL — EVERY line, every type — into a scratch sqlite DB
for report/visualization exploration.

Keeps one row per physical line with the full record payload in `json`, plus
promoted identity / relationship columns for joins. Nothing is interpreted and
nothing is dropped — when we don't yet know what's load-bearing, everything comes
in, including untimestamped UI-state records that a timed model would discard.

    uv run ${CLAUDE_SKILL_DIR}/raw_db.py init   [--root PATH] [--work PATH]
    uv run ${CLAUDE_SKILL_DIR}/raw_db.py ingest [--file F | --dir D] [--db ~/.claude/engaged-time/raw.db]
    uv run ${CLAUDE_SKILL_DIR}/raw_db.py reset  [--db ~/.claude/engaged-time/raw.db] [--yes]

`init` sets or confirms both path anchors and is re-runnable. `--root` is the
transcripts corpus to read: it has no default, and bare `ingest` blocks until it is
set, since a guessed root yields an empty timeline that reads as "no work happened".
`--work` is where every artifact lands (the DBs, plus logs/, diagrams/, scratch/);
repointing it warns about artifacts left behind rather than moving them.

`ingest` is always incremental + idempotent: the main file's sibling directory
(<stem>/**/*.jsonl — sub-agent transcripts) is included automatically, and files
whose (size, mtime) match the `file_state` ledger are skipped. A corrupt cache is
the only reason to rebuild from scratch — that is the gated `reset` verb (drops all
rows + the ledger after confirmation), deliberately NOT a flag on the hot path.
"""
import argparse
import json
import pathlib
import sqlite3
import sys

import _paths

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw (
    file        TEXT NOT NULL,
    line        INTEGER NOT NULL,
    type        TEXT,
    subtype     TEXT,           -- system records
    uuid        TEXT,           -- identity (conversation types)
    parent_uuid TEXT,           -- the hierarchy edge; NULL = root or field absent
    has_parent_field INTEGER,   -- distinguishes root (field present, null) from stateless (absent)
    session_id  TEXT,
    is_sidechain INTEGER,
    timestamp   TEXT,
    leaf_uuid   TEXT,           -- last-prompt → message pointer
    message_id  TEXT,           -- file-history-snapshot → message pointer
    prompt_id   TEXT,           -- user records
    request_id  TEXT,           -- assistant records
    is_compact_summary INTEGER,
    is_meta     INTEGER,
    -- canonicality as a mark, not a collapse: 1 when this uuid already
    -- occurred earlier in (file, line) order — a replay copy (compaction /
    -- resume / fork re-writing earlier events verbatim). The raw DB keeps
    -- every copy; readers decide what to do with them.
    is_replay   INTEGER NOT NULL DEFAULT 0,
    json        TEXT NOT NULL,  -- the whole record, untouched
    PRIMARY KEY (file, line)
);
CREATE INDEX IF NOT EXISTS idx_raw_uuid   ON raw(uuid);
CREATE INDEX IF NOT EXISTS idx_raw_parent ON raw(parent_uuid);
CREATE INDEX IF NOT EXISTS idx_raw_type   ON raw(type);
CREATE INDEX IF NOT EXISTS idx_raw_ts     ON raw(timestamp);
-- incremental-ingest ledger: a file is re-parsed only when its (size, mtime) changes;
-- unchanged files are skipped (their rows already current). Lets `--dir` UPSERT instead
-- of re-parsing the whole ~400MB corpus every run.
CREATE TABLE IF NOT EXISTS file_state (
    file     TEXT PRIMARY KEY,
    size     INTEGER NOT NULL,
    mtime_ns INTEGER NOT NULL,
    n_lines  INTEGER NOT NULL
);
"""


def load_file(conn: sqlite3.Connection, f: pathlib.Path, seen_uuids: set) -> int:
    """`seen_uuids` spans the whole load in file order, so a cross-file replay
    (a sub-agent re-emission) marks the same way an intra-file one does."""
    rows = []
    with open(f) as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                e = {"type": "<unparseable>"}
            u = e.get("uuid")
            is_replay = 1 if (u is not None and u in seen_uuids) else 0
            if u is not None:
                seen_uuids.add(u)
            rows.append((
                str(f), i, e.get("type"), e.get("subtype"),
                u, e.get("parentUuid"),
                1 if "parentUuid" in e else 0,
                e.get("sessionId"),
                (1 if e.get("isSidechain") else 0) if "isSidechain" in e else None,
                e.get("timestamp"), e.get("leafUuid"),
                e.get("messageId"), e.get("promptId"), e.get("requestId"),
                1 if e.get("isCompactSummary") else 0,
                1 if e.get("isMeta") else 0,
                is_replay,
                line,
            ))
    conn.execute("DELETE FROM raw WHERE file = ?", (str(f),))
    conn.executemany(
        "INSERT INTO raw VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    return len(rows)


def _first_ts(f: pathlib.Path) -> str:
    """First timestamp in a transcript — orders sessions chronologically so the
    cross-session canonicality rule (earliest occurrence wins) holds."""
    with open(f) as fh:
        for line in fh:
            try:
                ts = json.loads(line).get("timestamp")
            except json.JSONDecodeError:
                continue
            if ts:
                return ts
    return "9999"


def cmd_reset(a):
    """Drop the cache (all rows + the file ledger) so the next `ingest` rebuilds from
    scratch. Gated: a destructive rebuild belongs behind an explicit confirmation, not a
    flag a routine ingest could carry by accident."""
    db = pathlib.Path(a.db)
    if not db.exists():
        print(f"{a.db}: nothing to reset (no such DB)")
        return
    if not a.yes:
        if not sys.stdin.isatty():
            sys.exit(f"refusing to reset {a.db} non-interactively; pass --yes to confirm")
        if input(f"Drop ALL cached rows in {a.db} and rebuild from scratch on next "
                 f"ingest? [y/N] ").strip().lower() not in ("y", "yes"):
            print("aborted")
            return
    conn = sqlite3.connect(a.db)
    conn.executescript(SCHEMA)
    conn.execute("DELETE FROM raw")
    conn.execute("DELETE FROM file_state")
    conn.commit()
    conn.close()
    print(f"{a.db}: cache cleared — next ingest rebuilds from scratch")


def cmd_init(a):
    """Set or confirm both path anchors. Re-runnable: with no flags it reports what
    is already stored."""
    previous = _paths.resolve_work_dir().expanduser().resolve()
    target = pathlib.Path(a.work).expanduser().resolve() if a.work else previous

    work = _paths.set_work_dir(target)
    if previous != target and previous.is_dir() and any(previous.iterdir()):
        print(f"Warning: Existing artifacts remain at {previous}.")
        print()
    root = _paths.set_transcripts_root(
        a.root or _paths.stored_root() or _paths.CONVENTIONAL_ROOT)
    sessions = len(list(root.glob("*/*.jsonl")))
    print(f"transcripts root: {root}")
    print(f"  {sessions} session transcript(s) across {len(list(root.glob('*/')))} project dir(s)")
    print(f"working dir:      {work}")
    for name in ("raw.db", "annotations.db"):
        p = work / name
        print(f"  {name}: {p.stat().st_size / 1e6:.1f} MB" if p.exists()
              else f"  {name}: not yet built")
    print("  logs/, diagrams/, scratch/ ready")
    print(f"config:           {_paths.CONFIG_FILE}")
    if not sessions:
        print("  WARNING: no *.jsonl found one level down — is this the right root?")
    print()
    print(_paths.retention_note())


def cmd_ingest(a):
    if a.file:
        main_f = pathlib.Path(a.file).resolve()
        mains = [main_f]
    elif a.dir:
        mains = sorted((p for p in pathlib.Path(a.dir).resolve().glob("*.jsonl")),
                       key=_first_ts)
    else:                                   # whole corpus — needs the configured root
        mains = sorted(_paths.transcripts_root().glob("*/*.jsonl"), key=_first_ts)
    files: list = []
    for m in mains:
        files.append(m)
        files += sorted((m.parent / m.stem).rglob("*.jsonl"))
    pathlib.Path(a.db).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(a.db)
    conn.executescript(SCHEMA)

    # INCREMENTAL UPSERT. Walk every file in session-start (`_first_ts`) order so the
    # cross-file is_replay rule (earliest occurrence is canonical) holds: `seen` carries
    # the uuids of all earlier files. Unchanged files (size+mtime match the ledger) are
    # NOT re-parsed — their uuids are loaded from the DB into `seen` so later files still
    # mark replays correctly; only new/changed files are re-read (delete+insert that file).
    state = {f: (sz, mt) for f, sz, mt in
             conn.execute("SELECT file, size, mtime_ns FROM file_state")}
    on_disk = {str(f.resolve() if not f.is_absolute() else f): f for f in files}
    for gone in set(state) - set(on_disk):              # files removed from disk
        conn.execute("DELETE FROM raw WHERE file = ?", (gone,))
        conn.execute("DELETE FROM file_state WHERE file = ?", (gone,))
    seen_uuids: set = set()
    parsed = skipped = 0
    for f in sorted(on_disk.values(), key=_first_ts):
        key = str(f)
        st = f.stat()
        if state.get(key) == (st.st_size, st.st_mtime_ns):    # unchanged → skip parse
            seen_uuids.update(u for (u,) in conn.execute(
                "SELECT uuid FROM raw WHERE file = ? AND uuid IS NOT NULL", (key,)))
            skipped += 1
            continue
        n = load_file(conn, f, seen_uuids)                    # new/changed → re-ingest
        conn.execute("INSERT OR REPLACE INTO file_state VALUES (?,?,?,?)",
                     (key, st.st_size, st.st_mtime_ns, n))
        parsed += 1
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM raw").fetchone()[0]
    n_types = conn.execute("SELECT COUNT(DISTINCT type) FROM raw").fetchone()[0]
    n_rep = conn.execute("SELECT COALESCE(SUM(is_replay),0) FROM raw").fetchone()[0]
    conn.close()
    print(f"{a.db}: {total} rows, {n_types} types, {n_rep} replays · "
          f"parsed {parsed} file(s), skipped {skipped} unchanged")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", default=_paths.db("raw.db"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="set or confirm the transcripts root and working dir")
    p.add_argument("--root", help=f"transcripts root to read (default {_paths.CONVENTIONAL_ROOT})")
    p.add_argument("--work", help=f"working dir for DBs, logs, diagrams, scratch "
                                  f"(default {_paths.DEFAULT_WORK})")
    p.set_defaults(fn=cmd_init)
    p = sub.add_parser("ingest", parents=[common], help="JSONL → raw DB (incremental, idempotent)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--file", help="one main transcript .jsonl (+ its subagents dir)")
    g.add_argument("--dir", help="a project dir: EVERY main transcript in it "
                                 "(+ subagent dirs), loaded in session-start order "
                                 "so cross-session resume replays mark as is_replay")
    p.set_defaults(fn=cmd_ingest)
    p = sub.add_parser("reset", parents=[common],
                       help="drop the cache so the next ingest rebuilds from scratch (gated)")
    p.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    p.set_defaults(fn=cmd_reset)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

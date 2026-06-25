#!/usr/bin/env python3
"""Annotation store + CLI for the timeline model's prompt-anchored EXCHANGES, per-ROOT
focus-THREADS, and the TOPIC assignment over those threads.

The raw DB (`raw_db.py`) is a regenerable cache; THIS store (`~/.claude/a-horde-o-bees/transcripts/annotations.db`) is the
PERSISTENT annotation layer, keyed by each exchange's opening-prompt **UUID** — stable across
rebuilds, ceiling changes, and turn boundaries (the legacy positional `(session, exchange#)`
key was fragile). See `ARCHITECTURE.md` § Exchange / Topic / Population.

Exchanges are **derived** from the raw DB (`swimlane_timeline.materialize_exchanges`), never
stored — only the authored `description`, the topic vocabulary, the per-root focus-thread
synthesis, and the per-thread topic assignment persist here. Regenerate-fresh, not migrated.

    uv run ${CLAUDE_SKILL_DIR}/exchanges.py list   [--session SID | --root RID] [--from ISO] [--to ISO] [--undescribed] [--bodies]
    uv run ${CLAUDE_SKILL_DIR}/exchanges.py describe --set '{"<uuid>": "<description>", ...}'
    uv run ${CLAUDE_SKILL_DIR}/exchanges.py topics  [--set '{"<name>": "<description>", ...}']   # vocab; bare = list
    uv run ${CLAUDE_SKILL_DIR}/exchanges.py roots    [--pending]                                  # synthesis worklist
    uv run ${CLAUDE_SKILL_DIR}/exchanges.py threads  --root RID [--set '[{summary,uuids}]']        # store/count synthesis
    uv run ${CLAUDE_SKILL_DIR}/exchanges.py thread-list [--unassigned]                            # global topic-pass input
    uv run ${CLAUDE_SKILL_DIR}/exchanges.py thread-assign --set '{"<thread_key>": "<topic>", ...}'

THE ROOT is the unit of synthesis — the connected work-tree the visualization shows as one entry
(`branch_tree.session_trees`). A logical session can span several JSONL files: a cross-file resume
continues the thread in a new file whose first record parents off the old file. Those files are
ONE root component; synthesizing per-file would fragment a single objective across the resume. A
root id is the session id of the component's originating (earliest) file; a session with no
cross-file resume is its own single-file root.

THREAD-FIRST, three layers (lineage: exchange -> thread -> topic -> billable):
  1. describe   — author one description per exchange (per-session fan-out; descriptions are
                  per-exchange, so the file grain is fine here).
  2. threads    — coalesce a ROOT's described exchanges (across all its files, in time order) into
                  focus-threads, each a coherent objective owning a `summary` + its member exchange
                  UUIDs (per-root fan-out). Threads are TOPIC-FREE here — a thread's identity is the
                  sha256 of its sorted member UUIDs (`thread_key`), stable across description edits.
  3. topics + thread-assign — ONE global pass reviews every thread, refines the vocabulary to fit
                  the real threads, and assigns each thread exactly one topic. The report bills the
                  exchanges of every thread whose topic is in its filter set.

A consumed interjection has no anchor UUID of its own — its text rides on the exchange it folded
into. The leading `(continuation)` pseudo-exchange (anchor_uuid=None) can't be described or
threaded — it has no stable key; that's expected.
"""
import argparse
import collections
import hashlib
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swimlane_timeline as S  # noqa: E402
import branch_tree as BT  # noqa: E402  (canonical forest -> cross-file root components)
import _paths  # noqa: E402

ANNO_SCHEMA = """
CREATE TABLE IF NOT EXISTS exchange (
    prompt_uuid TEXT PRIMARY KEY, description TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS topic (
    name TEXT PRIMARY KEY, description TEXT, updated_at TEXT);
-- Per-ROOT focus-thread synthesis (content-addressed). One row per root component (a connected
-- work-tree, which may span several files via cross-file resume); `threads_json` is
-- [{summary, uuids:[...]}] — the root's described exchanges coalesced into coherent objectives.
-- TOPIC-FREE: topics attach via `thread_topic`, keyed by the thread's stable uuid-hash, so a
-- vocabulary refinement never disturbs the synthesis. `content_hash` is over the root's ordered
-- (uuid, description) set across all its files, so editing any description re-keys -> re-synthesis,
-- with no staleness bookkeeping.
CREATE TABLE IF NOT EXISTS root_thread (
    content_hash TEXT PRIMARY KEY, root_id TEXT NOT NULL,
    threads_json TEXT NOT NULL, updated_at TEXT);
-- Per-thread topic assignment (the global pass) — MANY-TO-MANY. `thread_key` = sha256 of the
-- thread's sorted member UUIDs, stable across description edits and re-synthesis that preserves
-- the grouping. A thread carries ONE OR MORE topic tags: most threads one, a thread whose work
-- genuinely spans buckets (e.g. a tooling discussion that bleeds into billable migration
-- debugging) carries several. The report bills on ANY-MATCH — a thread bills if ANY of its tags
-- is in the filter set — so a multi-tag thread spanning the billable boundary bills (the
-- conservative direction, the multi-tag rule applied to sharp thread units, not messy exchanges).
-- A thread whose grouping changes gets a new key and falls back to unassigned (`--unassigned`).
CREATE TABLE IF NOT EXISTS thread_topic (
    thread_key TEXT NOT NULL, topic TEXT NOT NULL, updated_at TEXT,
    PRIMARY KEY (thread_key, topic));
CREATE INDEX IF NOT EXISTS idx_tt_topic ON thread_topic(topic);
"""


def _marked(rawdb):
    """Load the raw corpus, drop sub-agents, and apply the shared synthetic/interjection
    marks (so materialize_exchanges can fold consumed-interjection text). {file: [records]}."""
    recs = [e for e in S.load(rawdb, 0)
            if e.get("timestamp") and "/subagents/" not in e["_file"]]
    by = {}
    for e in recs:
        by.setdefault(e["_file"], []).append(e)
    S.mark_synthetic(by)
    S.mark_interjections(by)
    return by


def _anno(path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    c = sqlite3.connect(path)
    c.executescript(ANNO_SCHEMA)
    return c


def _sid(f):
    """Session id from a raw-DB file key."""
    return f.rsplit("/", 1)[-1].removesuffix(".jsonl")


def _root_components(by):
    """Group files into ROOT components — the visualization's connected work-trees. Two files
    join when a record in one canonically parents off the other (a cross-file resume). Returns
    an ordered {root_id: [files, oldest-first]}, root_id = the originating file's session id,
    components ordered by their origin time. Mirrors `branch_tree.session_trees`' "resume spans
    files" grouping at the file grain (never splits a file; only merges cross-file resumes)."""
    F = BT.build_forest([e for rs in by.values() for e in rs])
    canon = F["canon"]
    parent = {f: f for f in by}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for e in canon.values():
        pu = e.get("parentUuid")
        if pu in canon and canon[pu]["_file"] != e["_file"]:
            parent[find(e["_file"])] = find(canon[pu]["_file"])

    def first_ts(f):
        return by[f][0]["timestamp"] if by[f] else ""

    comps = collections.defaultdict(list)
    for f in by:
        comps[find(f)].append(f)
    out = {}
    for fs in sorted(comps.values(), key=lambda fs: min(first_ts(f) for f in fs)):
        fs.sort(key=first_ts)
        out[_sid(fs[0])] = fs
    return out


def _resolve_root(comps, rid_prefix):
    """The single root id matching `rid_prefix`. Exits on 0 or >1."""
    m = [rid for rid in comps if rid.startswith(rid_prefix)]
    if not m:
        sys.exit(f"no root matches prefix {rid_prefix!r}")
    if len(m) > 1:
        sys.exit(f"prefix {rid_prefix!r} is ambiguous ({len(m)} roots): "
                 + ", ".join(r[:12] for r in m))
    return m[0]


def _units_for_session(records, desc, with_bodies=False):
    """Ordered exchange units for ONE file's records. [{uuid, ts, text, description}, ...] in
    time order; a continuation pseudo-exchange carries uuid=None (skipped by the hash)."""
    out = []
    for x in S.materialize_exchanges(records, with_bodies=with_bodies):
        u = x["anchor_uuid"]
        out.append({"uuid": u, "ts": x["ts"], "text": x["text"],
                    "description": desc.get(u) if u else None})
    return out


def _units_for_root(by, files, desc, with_bodies=False):
    """Ordered exchange units across a ROOT's files (oldest file first, in-file time order) —
    the synthesis input and the content-hash basis for the whole work-tree."""
    out = []
    for f in files:
        out += _units_for_session(by[f], desc, with_bodies=with_bodies)
    return out


def _content_hash(units):
    """sha256 over a root's ordered (uuid, description) set — the `root_thread` cache key.
    None if the root has no describable (uuid-anchored) exchange."""
    parts = [f"{u['uuid']}\t{u.get('description') or ''}" for u in units if u.get("uuid")]
    if not parts:
        return None
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _thread_key(uuids):
    """Stable identity of a thread = sha256 of its sorted member UUIDs. Topic-pass key."""
    return hashlib.sha256("\n".join(sorted(uuids)).encode("utf-8")).hexdigest()


def cmd_list(a):
    by = _marked(a.db)
    anno = _anno(a.anno)
    desc = dict(anno.execute("SELECT prompt_uuid, description FROM exchange"))
    out = []
    if a.root:
        comps = _root_components(by)
        rid = _resolve_root(comps, a.root)
        units = _units_for_root(by, comps[rid], desc, with_bodies=a.bodies)
        for u in units:
            if a.undescribed and (u["uuid"] is None or u["description"]):
                continue
            out.append({"root": rid[:8], "uuid": u["uuid"], "ts": u["ts"],
                        "text": u["text"], "description": u["description"]})
    else:
        for f in sorted(by, key=lambda k: by[k][0]["timestamp"] if by[k] else ""):
            sid = _sid(f)
            if a.session and not sid.startswith(a.session):
                continue
            for u in _units_for_session(by[f], desc, with_bodies=a.bodies):
                if a.undescribed and (u["uuid"] is None or u["description"]):
                    continue
                out.append({"session": sid[:8], "uuid": u["uuid"], "ts": u["ts"],
                            "text": u["text"], "description": u["description"]})
    # ISO-prefix time box: compare each ts truncated to the bound's length, so a
    # partial bound is inclusive of its whole span (--to ...T16:35 keeps all of 16:35).
    if a.date_from:
        out = [e for e in out if (e["ts"] or "")[:len(a.date_from)] >= a.date_from]
    if a.date_to:
        out = [e for e in out if (e["ts"] or "")[:len(a.date_to)] <= a.date_to]
    print(json.dumps(out, indent=1, ensure_ascii=False))


def cmd_describe(a):
    d = json.loads(a.set)
    anno = _anno(a.anno)
    anno.executemany(
        "INSERT INTO exchange(prompt_uuid, description, updated_at) VALUES (?,?,datetime('now')) "
        "ON CONFLICT(prompt_uuid) DO UPDATE SET description=excluded.description, "
        "updated_at=excluded.updated_at", list(d.items()))
    anno.commit()
    print(f"described {len(d)} exchange(s)")


def cmd_topics(a):
    anno = _anno(a.anno)
    if a.set:
        d = json.loads(a.set)
        anno.executemany(
            "INSERT INTO topic(name, description, updated_at) VALUES (?,?,datetime('now')) "
            "ON CONFLICT(name) DO UPDATE SET description=excluded.description, "
            "updated_at=excluded.updated_at", list(d.items()))
        anno.commit()
        print(f"set {len(d)} topic(s)")
    else:
        print(json.dumps([{"name": n, "description": d}
                          for n, d in anno.execute(
                              "SELECT name, description FROM topic ORDER BY name")],
                         indent=1, ensure_ascii=False))


def cmd_roots(a):
    """List root ids (oldest first) — the synthesis worklist. `--pending` restricts to roots whose
    current content hash has no cached thread set (need (re)synthesis); a description edit changes
    the hash, so an edited root reappears here automatically."""
    by = _marked(a.db)
    anno = _anno(a.anno)
    desc = dict(anno.execute("SELECT prompt_uuid, description FROM exchange"))
    cached = {h for (h,) in anno.execute("SELECT content_hash FROM root_thread")}
    out = []
    for rid, files in _root_components(by).items():
        h = _content_hash(_units_for_root(by, files, desc))
        if h is None:                       # no describable exchange — nothing to thread
            continue
        if a.pending and h in cached:
            continue
        out.append(rid)
    print("\n".join(out))


def cmd_threads(a):
    """Per-root focus-thread synthesis. `--set '[{summary, uuids:[...]}]'` stores the root's threads
    (TOPIC-FREE), keyed by the root's CURRENT content hash (recomputed here from the live
    descriptions, so the agent never handles the hash). Validates each member uuid against the
    root's files. Bare (no `--set`) prints the cached root-thread count."""
    anno = _anno(a.anno)
    if not a.set:
        (n,) = anno.execute("SELECT count(*) FROM root_thread").fetchone()
        print(f"{n} cached root-thread set(s)")
        return
    threads = json.loads(a.set)
    by = _marked(a.db)
    comps = _root_components(by)
    rid = _resolve_root(comps, a.root)
    desc = dict(anno.execute("SELECT prompt_uuid, description FROM exchange"))
    units = _units_for_root(by, comps[rid], desc)
    h = _content_hash(units)
    if h is None:
        sys.exit(f"root {rid[:8]} has no describable exchange — nothing to thread")
    root_uuids = {u["uuid"] for u in units if u["uuid"]}
    bad_u = sorted({x for t in threads for x in t.get("uuids", [])} - root_uuids)
    if bad_u:
        sys.exit(f"thread member uuid(s) not in root {rid[:8]}: {bad_u}")
    anno.execute(
        "INSERT INTO root_thread(content_hash, root_id, threads_json, updated_at) "
        "VALUES (?,?,?,datetime('now')) ON CONFLICT(content_hash) DO UPDATE SET "
        "root_id=excluded.root_id, threads_json=excluded.threads_json, "
        "updated_at=excluded.updated_at",
        (h, rid, json.dumps(threads, ensure_ascii=False)))
    anno.commit()
    n_ex = sum(len(t.get("uuids", [])) for t in threads)
    print(f"stored {len(threads)} thread(s) ({n_ex} exchange(s)) for root {rid[:8]} [{h[:12]}]")


def _all_threads(anno):
    """Every synthesized thread across all cached roots, oldest root first, in-root order.
    [{thread_key, root, summary, uuids, topics:[...]}, ...]. The topic-pass surface."""
    tags = collections.defaultdict(list)
    for k, t in anno.execute("SELECT thread_key, topic FROM thread_topic ORDER BY topic"):
        tags[k].append(t)
    rows = anno.execute(
        "SELECT root_id, threads_json, updated_at FROM root_thread").fetchall()
    rows.sort(key=lambda r: (r[2] or "", r[0]))    # by store time then root — stable order
    out = []
    for rid, tj, _ in rows:
        for t in json.loads(tj):
            uuids = t.get("uuids", [])
            k = _thread_key(uuids)
            out.append({"thread_key": k, "root": rid[:8], "summary": t.get("summary", ""),
                        "uuids": uuids, "topics": tags.get(k, [])})
    return out


def cmd_thread_list(a):
    """Emit every synthesized thread (the global topic-pass input). `--unassigned` restricts to
    threads with no topic tag yet — the worklist after a (re)synthesis or a grouping change."""
    anno = _anno(a.anno)
    rows = _all_threads(anno)
    if a.unassigned:
        rows = [r for r in rows if not r["topics"]]
    print(json.dumps(rows, indent=1, ensure_ascii=False))


def cmd_thread_assign(a):
    """Assign topic TAGS to threads (the global pass), MANY-TO-MANY. `--set '{thread_key: topic}'`
    or `'{thread_key: [topic, ...]}'` — a bare string is one tag. Replace-semantics per thread_key:
    the supplied list becomes that thread's complete tag set (idempotent). Each topic is validated
    against the vocabulary. The report bills a thread on ANY-match of its tags, so a thread spanning
    the billable boundary carries both a billable and the internal-tooling tag and still bills."""
    raw = json.loads(a.set)
    d = {k: ([v] if isinstance(v, str) else list(v)) for k, v in raw.items()}
    anno = _anno(a.anno)
    known = {n for (n,) in anno.execute("SELECT name FROM topic")}
    bad = sorted({t for ts in d.values() for t in ts} - known)
    if known and bad:
        sys.exit(f"unknown topic(s) (set them first via `topics --set`): {bad}")
    for k, ts in d.items():
        anno.execute("DELETE FROM thread_topic WHERE thread_key=?", (k,))
        anno.executemany(
            "INSERT INTO thread_topic(thread_key, topic, updated_at) VALUES (?,?,datetime('now'))",
            [(k, t) for t in dict.fromkeys(ts)])     # dedup, preserve order
    anno.commit()
    n_tags = sum(len(dict.fromkeys(ts)) for ts in d.values())
    print(f"assigned {len(d)} thread(s), {n_tags} tag(s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", default=_paths.db("raw.db"), help="raw DB (the cache)")
    common.add_argument("--anno", default=_paths.db("annotations.db"), help="annotation store")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list", parents=[common])
    p.add_argument("--session", help="session id prefix (single file)")
    p.add_argument("--root", help="root id prefix (whole work-tree, may span files)")
    p.add_argument("--undescribed", action="store_true", help="only uuid-anchored, no description yet")
    p.add_argument("--from", dest="date_from", metavar="ISO",
                   help="inclusive lower bound, ISO-ts prefix (e.g. 2026-06-23 or 2026-06-23T15:30)")
    p.add_argument("--to", dest="date_to", metavar="ISO",
                   help="inclusive upper bound, ISO-ts prefix (whole span of a partial bound)")
    p.add_argument("--bodies", action="store_true",
                   help="include the assistant's response turns in each exchange's `text` array "
                        "(role signal for authoring); without it, `text` holds only the user turns")
    p.set_defaults(fn=cmd_list)
    p = sub.add_parser("describe", parents=[common])
    p.add_argument("--set", required=True, help='JSON {uuid: description}')
    p.set_defaults(fn=cmd_describe)
    p = sub.add_parser("topics", parents=[common])
    p.add_argument("--set", help='JSON {name: description}; omit to list')
    p.set_defaults(fn=cmd_topics)
    p = sub.add_parser("roots", parents=[common])
    p.add_argument("--pending", action="store_true",
                   help="only roots whose threads are not yet synthesized (or are stale)")
    p.set_defaults(fn=cmd_roots)
    p = sub.add_parser("threads", parents=[common])
    p.add_argument("--root", help="root id prefix (required with --set)")
    p.add_argument("--set", help='JSON [{summary, uuids:[...]}]; omit to print cache count')
    p.set_defaults(fn=cmd_threads)
    p = sub.add_parser("thread-list", parents=[common])
    p.add_argument("--unassigned", action="store_true", help="only threads with no topic yet")
    p.set_defaults(fn=cmd_thread_list)
    p = sub.add_parser("thread-assign", parents=[common])
    p.add_argument("--set", required=True, help='JSON {thread_key: topic}')
    p.set_defaults(fn=cmd_thread_assign)
    a = ap.parse_args()
    if a.cmd == "threads" and a.set and not a.root:
        ap.error("threads --set requires --root")
    if a.cmd == "list" and a.session and a.root:
        ap.error("list takes --session or --root, not both")
    a.fn(a)


if __name__ == "__main__":
    main()

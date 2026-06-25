#!/usr/bin/env python3
"""Live swimlane server — queries a raw transcript DB on demand and serves JSON
geometry per session to a virtualized browser client.

Replaces the static one-file bake (`swimlane_timeline.py`) for interactive
analysis: the page loads only session *headers* up front (collapsed segments), then
fetches one session's geometry when you expand it and renders only the rows in the
viewport. So load time is independent of corpus size, sessions are segmented (never
intermixed on a shared axis), and filters are query params against the live DB —
re-stat the file and a rebuild is picked up with no regenerate step.

The Python time/layout model (`swimlane_timeline.build`/`ymap`/`session_geometry`)
stays the single source of truth; the client is a dumb renderer + virtualizer.

    uv run ${CLAUDE_SKILL_DIR}/raw_db.py --dir <project-dir> --db ~/.claude/a-horde-o-bees/transcripts/raw.db
    uv run ${CLAUDE_SKILL_DIR}/swimlane_server.py --db ~/.claude/a-horde-o-bees/transcripts/raw.db --port 8765
    # open http://localhost:8765/

No external dependencies (stdlib http.server + sqlite3, like the rest of the skill).
"""
import argparse
import bisect
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swimlane_timeline as S
import _paths  # noqa: E402
import branch_tree as BT  # noqa: E402


def _thread_key(uuids: list) -> str:
    """Stable thread identity = sha256 of sorted member UUIDs (mirrors exchanges._thread_key)."""
    return hashlib.sha256("\n".join(sorted(uuids)).encode("utf-8")).hexdigest()


class Corpus:
    """Raw-DB-backed session store, refreshed when the DB file changes (mtime), so
    a rebuilt raw DB is reflected without restarting the server."""

    def __init__(self, db: str):
        self.db = db
        self.mtime = None
        self.by_session: dict[str, list] = {}
        self.by_fl: dict[tuple, dict] = {}        # (file, line) -> record
        self.path_by_base: dict[str, str] = {}    # session-id -> full file path
        self.meta: list[dict] = []
        self.meta_by_base: dict[str, dict] = {}
        self.trees: list[dict] = []               # branch forest (one per root session)
        self.segix: dict[str, dict] = {}          # start_uuid -> segment node (for geometry)
        self.present: list = []                   # classes present corpus-wide (header)
        self.anno_desc: dict = {}                 # anchor uuid -> exchange description
        self.anchor_thread: dict = {}             # anchor uuid -> {sum, top, tj, tn}
        self.topics: list = []                    # distinct topic names present on threads

    def ensure(self):
        m = os.path.getmtime(self.db)
        if m == self.mtime:
            return
        recs = S.load(self.db, 0)
        recs = [e for e in recs if e.get("timestamp")]
        recs = [e for e in recs if "/subagents/" not in e["_file"]]
        by: dict[str, list] = {}
        for e in recs:
            by.setdefault(e["_file"], []).append(e)
        S.mark_synthetic(by)
        S.mark_interjections(by)
        self.by_session = by
        self.by_fl = {(f, e["_line"]): e for f, rs in by.items() for e in rs}
        self.path_by_base = {f.rsplit("/", 1)[-1].removesuffix(".jsonl"): f for f in by}
        self.meta = sorted((self._meta(f, rs) for f, rs in by.items()),
                           key=lambda d: d["start"])
        self.meta_by_base = {mm["sid"]: mm for mm in self.meta}
        # branch forest across ALL files (resume spans files); index every segment by
        # its start_uuid for lazy per-segment geometry. Resume children fold into their
        # ancestor's tree, so the top level is one entry per genuine root session.
        self.trees = BT.session_trees([e for rs in by.values() for e in rs])
        self.segix = {}
        for t in self.trees:
            self._index_segments(t)
        # per-segment time-box coverage (the row duration column) — computed once
        for node in self.segix.values():
            path = self.path_by_base.get(node["file"])
            rs = [self.by_fl[(path, ln)] for ln in node["lines"]
                  if path and (path, ln) in self.by_fl]
            blocks, _ = S._pair_points(S._raw_points(rs))
            node["coverage_s"] = round(sum(b[2] for b in blocks), 1)
            node["n_blocks"] = len(blocks)
            node["gap_spans"] = S.gap_spans(rs)   # ceiling-independent; adjusted per-request
        self._attach_orphan_lines(by)
        self._queue_relationships(by)
        self.present = self._present_classes(by)
        self._stats_cache = {}
        self._load_annotations()
        self.mtime = m


    def _index_segments(self, node: dict):
        self.segix[node["start_uuid"]] = node
        for b in node["branches"]:
            self._index_segments(b)
        for f in node.get("segments", []):
            self._index_segments(f)

    def _attach_orphan_lines(self, by: dict):
        """Place uuid-less timestamped records (queue-operation: enqueue/dequeue/
        remove/popAll — they carry no uuid, so the canonical-uuid forest never put
        them in any segment's `lines`) into the segment they belong to. Each attaches
        to the segment owning the nearest PRECEDING canonical line in its file — the
        conversation record it was emitted right after. Without this they vanish from
        every segment even though they're loaded; the column header still lists the
        class, so it would read as an always-empty column."""
        # per-file sorted (canonical line -> owning segment)
        owners: dict[str, list] = {}
        for node in self.segix.values():
            node.setdefault("extra_lines", [])
            path = self.path_by_base.get(node["file"])
            if path is None:
                continue
            for ln in node["lines"]:
                owners.setdefault(path, []).append((ln, node))
        for path in owners:
            owners[path].sort(key=lambda t: t[0])
        for path, rs in by.items():
            owned = owners.get(path)
            if not owned:
                continue
            lines = [o[0] for o in owned]
            for e in rs:
                if e.get("uuid"):           # has uuid → forest already placed/judged it
                    continue
                i = bisect.bisect_right(lines, e["_line"]) - 1
                if i >= 0:                  # belongs after some canonical record
                    owned[i][1]["extra_lines"].append(e["_line"])

    _TU = re.compile(r"<tool-use-id>([^<]+)</tool-use-id>")

    @staticmethod
    def _qnorm(s: str) -> str:
        return " ".join((s or "").split())

    def _queue_relationships(self, by: dict):
        """The queue ops are DISSOLVED to direct bridges: only the queued user prompt
        (its hollow signature) is kept; every dequeue/remove/popAll and notification
        enqueue is omitted, and a single `qbridge` edge connects the two ends of a
        chain that actually bridged. Pairing is eager FIFO (oldest pending enqueue per
        consuming op); delivery is content-confirmed, so a wrong pairing can't invent
        a bridge, and a chain that doesn't fully bridge draws NOTHING. Per file ->
        [(from, to, 'qbridge')]:
          • queued user prompt -> its delivered prompt (dequeued; hollow re-attaches
            to the real prompt — consume + deliver collapsed)
          • tool_use -> delivered notification         (a background task's spawn ->
            its completion notice — enqueue + dequeue collapsed)
          • removed / slash-command / no-tool_use / cross-boundary -> omitted."""
        self.qedges: dict[str, list] = {}
        for path, rs in by.items():
            edges: list = []
            tu_line: dict[str, int] = {}        # tool_use id -> emitting assistant line
            deliver_idx: dict[str, list] = {}    # delivered user content -> sorted lines
            for e in rs:
                t = e.get("type")
                if t == "assistant":
                    for c in ((e.get("message") or {}).get("content") or []):
                        if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("id"):
                            tu_line[c["id"]] = e["_line"]
                elif t == "user":
                    k = self._qnorm(S.content_text(e))
                    if k:
                        deliver_idx.setdefault(k, []).append(e["_line"])
            for v in deliver_idx.values():
                v.sort()

            def delivered_line(content: str, after: int):
                # deliver_idx is keyed on the whitespace-normalized full S.content_text;
                # normalize the enqueue's raw content identically so the keys match
                lst = deliver_idx.get(self._qnorm(content))
                if lst:
                    j = next((x for x, ln in enumerate(lst) if ln > after), None)
                    if j is not None:
                        return lst.pop(j)
                return None

            def bridge(src: dict, op_line: int):
                content = src.get("content") or ""
                dl = delivered_line(content, op_line)
                if dl is None:
                    return                                       # never reached a delivery → omit
                if not content.lstrip().startswith(("<task-notification", "<<")):
                    edges.append((src["_line"], dl, "qbridge"))  # hollow prompt → its delivery
                else:
                    m = self._TU.search(content)
                    tul = tu_line.get(m.group(1)) if m else None
                    if tul is not None:
                        edges.append((tul, dl, "qbridge"))       # tool_use → its notification

            pending: list = []                  # enqueue records awaiting a consuming op
            for e in sorted((q for q in rs if q.get("type") == "queue-operation"),
                            key=lambda q: q["_line"]):
                op = e.get("operation")
                if op == "enqueue":
                    pending.append(e)
                elif op == "dequeue":
                    if pending:
                        bridge(pending.pop(0), e["_line"])        # eager FIFO
                elif op == "remove":
                    if pending:
                        src = pending.pop(0)
                        if src.get("_consumed"):                  # consumed interjection:
                            edges.append((src["_line"], e["_line"], "qbridge"))  # enqueue → consumption
                elif op == "popAll":                              # flush: only own-content delivers
                    pc = self._qnorm(e.get("content") or "")
                    for src in pending:
                        if self._qnorm(src.get("content") or "") == pc:
                            bridge(src, e["_line"])
                    pending = []
            self.qedges[path] = edges

    @staticmethod
    def _present_classes(by: dict) -> list:
        """Classes that actually occur in main-chain segments — so the global column
        header can show them at all times (min width), not only when expanded.
        Mirrors `build`'s classification incl. the interactive-tool → user-response
        split and the replay/summary → context-prep collapse."""
        INTERACTIVE = {"AskUserQuestion", "ExitPlanMode", "EnterPlanMode"}
        present: set = set()
        for rs in by.values():
            tu = {}
            for e in rs:
                if e.get("type") == "assistant":
                    for c in ((e.get("message") or {}).get("content") or []):
                        if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("id"):
                            tu[c["id"]] = c.get("name") or ""
            for e in rs:
                if e.get("_replay") or e.get("_cs"):
                    present.add("context-prep")
                if e.get("_replay") or e.get("isSidechain") or "/subagents/" in e["_file"]:
                    continue
                cls, lbl = S.classify(e)
                if cls == "queue-operation":
                    # dissolved: a queued user prompt shows in the prompt column (hollow);
                    # every other queue op is gone, so the queue column never appears
                    if lbl == "enqueue:prompt":
                        present.add("prompt")
                    continue
                if cls == "tool_result":
                    ref = next((c.get("tool_use_id")
                                for c in ((e.get("message") or {}).get("content") or [])
                                if isinstance(c, dict) and c.get("type") == "tool_result"), None)
                    if tu.get(ref or "") in INTERACTIVE:
                        cls = "user-response"
                present.add(cls)
        return [c for c in S.CLASS_ORDER if c in present]

    def _resolve(self, sid: str) -> str | None:
        if sid in self.by_session:
            return sid
        hits = [k for k in self.by_session if k.rsplit("/", 1)[-1].startswith(sid)]
        return hits[0] if len(hits) == 1 else None

    def _meta(self, f: str, rs: list) -> dict:
        ts = [S._ep(e["timestamp"]) for e in rs]
        start, end = min(ts), max(ts)
        # genuine typed prompts only: exclude replays (re-emitted on resume/compaction)
        # and compact summaries — both read as prompts to `classify` but neither is a
        # user prompt, and counting them inflates resumed sessions badly
        n_prompt = sum(1 for e in rs if not e.get("_replay") and BT.is_typed_prompt(e))
        sid = f.rsplit("/", 1)[-1].removesuffix(".jsonl")
        dt0 = datetime.fromtimestamp(start, timezone.utc)
        dt1 = datetime.fromtimestamp(end, timezone.utc)
        # full datetimes on both ends — a session crossing midnight has an end clock
        # that belongs to a later date, so a single date + HH:MM–HH:MM misleads.
        # `date · HH:MM → date · HH:MM` (dot separates date/time; arrow spans the range)
        return {
            "sid": sid, "short": sid[:8],
            "start": start, "end": end,
            "range": f"{dt0.strftime('%Y-%m-%d · %H:%M')} → {dt1.strftime('%Y-%m-%d · %H:%M')}",
            "dur": S._fmt_hm(end - start),
            "n_rec": len(rs), "n_prompt": n_prompt,
        }

    def sessions(self, frm: float | None, to: float | None) -> list[dict]:
        out = []
        for m in self.meta:
            if frm is not None and m["end"] < frm:
                continue
            if to is not None and m["start"] > to:
                continue
            out.append({k: v for k, v in m.items()})
        return out

    def _geom(self, rs: list, compact: bool) -> dict:
        nodes, edges, lanes = S.build(list(rs))
        if not nodes:
            return {"empty": True}
        if compact:
            Y, gutter, idle, _t, h = S.ymap_compact(nodes)
        else:
            Y, _s, idle, h = S.ymap(nodes)
            gutter = None
        return S.session_geometry(nodes, edges, lanes, Y, idle, h, gutter)

    def geometry(self, sid: str, compact: bool) -> dict | None:
        """Whole-file swimlane (the flat view; kept for the static segment path)."""
        f = self._resolve(sid)
        return self._geom(self.by_session[f], compact) if f is not None else None

    def _light(self, node: dict) -> dict:
        """A tree node stripped to the client skeleton — the heavy per-record `lines`
        stays server-side (in `segix`), fetched lazily as geometry on expand."""
        return {
            "u": node["start_uuid"], "file": node["file"], "kind": node.get("kind", "root"),
            "label": node["label"], "is_prompt": node["is_prompt"], "prompt": node["prompt"],
            "first_prompt": node.get("first_prompt", ""),
            "ts": node["ts"], "n_records": node["n_records"], "n_prompts": node["n_prompts"],
            "coverage_s": node.get("coverage_s", 0),
            "n_compaction": len(node["compaction_lines"]), "no_response": node["no_response"],
            "from": node.get("from"),                       # segment re-attach point
            "branches": [self._light(b) for b in node["branches"]],
            "segments": [self._light(f) for f in node.get("segments", [])],
        }

    def trees_payload(self, frm: float | None, to: float | None) -> list[dict]:
        """One entry per root session: its file-level header meta + the nested branch
        skeleton. Resume children are already folded in (never their own entry)."""
        out = []
        for t in self.trees:
            meta = self.meta_by_base.get(t["file"])
            if meta is None:
                continue
            if frm is not None and meta["end"] < frm:
                continue
            if to is not None and meta["start"] > to:
                continue
            out.append({**{k: meta[k] for k in
                           ("sid", "short", "range", "dur", "n_rec", "n_prompt", "start", "end")},
                        "tree": self._light(t)})
        out.sort(key=lambda d: d["start"])
        return out

    def _walk_segments(self, node: dict):
        yield node
        for f in node.get("segments", []):
            yield from self._walk_segments(f)
        for b in node.get("branches", []):
            yield from self._walk_segments(b)

    def _segment_records(self, node: dict) -> list:
        """The records of a segment node (its canonical lines + attached orphan queue-op lines),
        line-ordered — what both segment_geometry and the topic-filtered stats materialize from."""
        path = self.path_by_base.get(node["file"])
        if path is None:
            return []
        lset = set(node["lines"]) | set(node.get("extra_lines", []))
        return [self.by_fl[(path, ln)] for ln in sorted(lset) if (path, ln) in self.by_fl]

    def stats(self, frm: float | None, to: float | None, active_ceiling: float,
              idle_ceiling: float, off: frozenset = frozenset()) -> dict:
        """Topic-filtered engaged-time totals over the from/to window — the Stats tab. The
        per-exchange measures (time-boxed coverage, the active/idle gap adjustments, adjusted
        active, the exchange/time-box counts) sum only over exchanges whose focus-thread has a
        SHOWN topic (ANY-match; `off` = the toggled-off topics), so toggling a topic moves the
        totals — and toggling off all but the billable topics yields the bill. Exchanges with no
        thread/topic are excluded from these measures. `total` stays the unfiltered session
        wall-clock (the honest denominator). Re-materializes per request so the live ceilings
        apply; cached per (window, ceilings, off-set)."""
        key = (frm, to, active_ceiling, idle_ceiling, off)
        if key in self._stats_cache:
            return self._stats_cache[key]
        cov = total = gap_active_s = gap_idle_s = adjusted = 0.0
        blocks = exch = nfac = gap_active_n = gap_idle_n = 0
        sess: set = set()
        for t in self.trees:
            meta = self.meta_by_base.get(t["file"])
            if meta is None:
                continue
            if frm is not None and meta["end"] < frm:
                continue
            if to is not None and meta["start"] > to:
                continue
            sess.add(t["file"])
            total += meta["end"] - meta["start"]
            for node in self._walk_segments(t):
                nfac += 1
                for ex in S.materialize_exchanges(self._segment_records(node),
                                                  active_ceiling=active_ceiling,
                                                  idle_ceiling=idle_ceiling):
                    if ex["anchor_uuid"] is None:
                        continue
                    th = self.anchor_thread.get(ex["anchor_uuid"])
                    topics = th["top"] if th else ()
                    if not topics or (off and all(tp in off for tp in topics)):
                        continue                          # untracked, or every topic toggled off
                    cov += ex["coverage_s"]; adjusted += ex["adjusted_s"]
                    gap_active_s += ex["gap_active_s"]; gap_idle_s += ex["gap_idle_s"]
                    blocks += ex["n_blocks"]; exch += 1
                    if ex["gap_active_s"] > 0:
                        gap_active_n += 1
                    if ex["gap_idle_s"] > 0:
                        gap_idle_n += 1
        out = {"time": {"total_s": round(total, 1), "timeboxed_s": round(cov, 1),
                        "gap_active_s": round(gap_active_s, 1), "gap_idle_s": round(gap_idle_s, 1),
                        "adjusted_s": round(adjusted, 1)},
               "counts": {"exchanges": exch, "timeboxes": blocks,
                          "gap_active_n": gap_active_n, "gap_idle_n": gap_idle_n},
               "active_ceiling": active_ceiling, "idle_ceiling": idle_ceiling,
               "sessions": len(sess), "segments": nfac}
        self._stats_cache[key] = out
        return out

    def segment_geometry(self, start_uuid: str, active_ceiling: float = S.GAP_ACTIVE_CEILING,
                         idle_ceiling: float = S.GAP_IDLE_CEILING) -> dict | None:
        """Class-relative ordinal segment for one segment — the run between branch
        points. `active_ceiling`/`idle_ceiling` drive the active/idle fills + gutter red
        threshold. The client lays out columns globally across expanded segments."""
        node = self.segix.get(start_uuid)
        if node is None:
            return None
        path = self.path_by_base.get(node["file"])
        if path is None:
            return None
        lset = set(node["lines"]) | set(node.get("extra_lines", []))
        rs = self._segment_records(node)
        qe = [e for e in self.qedges.get(path, []) if e[0] in lset and e[1] in lset]
        geom = S.segment_geometry(rs, extra_edges=qe,
                               active_ceiling=active_ceiling, idle_ceiling=idle_ceiling)
        if geom and not geom.get("empty"):
            self._attach_membership(geom, rs)
        return geom

    def _load_annotations(self):
        """Join annotations.db (exchange descriptions + focus-thread summaries/topics) for the
        membership lanes. Policy-neutral: reads whatever topic NAMES the project assigned — the
        skill embeds no vocabulary and no billable boundary (that is the consumer's policy)."""
        self.anno_desc = {}
        self.anchor_thread = {}
        self.topics = []
        ap = _paths.db("annotations.db")
        if not os.path.exists(ap):
            return
        try:
            con = sqlite3.connect(f"file:{ap}?mode=ro", uri=True)
        except sqlite3.Error:
            return
        try:
            try:
                self.anno_desc = {u: d for u, d in
                                  con.execute("SELECT prompt_uuid, description FROM exchange") if d}
            except sqlite3.Error:
                pass
            tags: dict = {}
            try:
                for k, t in con.execute("SELECT thread_key, topic FROM thread_topic"):
                    tags.setdefault(k, set()).add(t)
            except sqlite3.Error:
                pass
            try:
                rows = list(con.execute("SELECT threads_json FROM root_thread"))
            except sqlite3.Error:
                rows = []
            for (tj,) in rows:
                try:
                    threads = json.loads(tj)
                except (ValueError, TypeError):
                    continue
                for th in threads:
                    uuids = th.get("uuids") or []
                    if not uuids:
                        continue
                    key = _thread_key(uuids)
                    topics = sorted(tags.get(key) or ())
                    summary = th.get("summary") or ""
                    n = len(uuids)
                    for j, u in enumerate(uuids):
                        self.anchor_thread[u] = {"sum": summary, "top": topics,
                                                 "tj": j + 1, "tn": n}
            self.topics = sorted({t for ts in tags.values() for t in ts})
        finally:
            con.close()

    def _attach_membership(self, geom: dict, rs: list):
        """Decorate each event node with its exchange + focus-thread membership (lanes + Selection
        detail). Per-record exchange = the materialize_exchanges owner bisect (ts interval → the
        opening anchor uuid); thread/description join on that anchor globally — anchors are
        corpus-unique, so no file→root hop is needed. Star (context-prep) nodes get nothing."""
        if not self.anno_desc and not self.anchor_thread:
            return
        exs = S.materialize_exchanges(rs)
        if not exs:
            return
        los = [S._ep(x["ts"]) for x in exs]
        line_anchor: dict = {}
        ex_order: dict = {}
        ex_lines: dict = {}
        order = 0
        for rec in sorted(rs, key=lambda e: (S._ep(e["timestamp"]), e["_line"])):
            anchor = exs[max(0, bisect.bisect_right(los, S._ep(rec["timestamp"])) - 1)]["anchor_uuid"]
            ln = rec["_line"]
            line_anchor[ln] = anchor
            if anchor is not None:
                if anchor not in ex_order:
                    ex_order[anchor] = order
                    ex_lines[anchor] = []
                    order += 1
                ex_lines[anchor].append(ln)
        ri: dict = {}
        for anchor, lines in ex_lines.items():
            for i, ln in enumerate(lines):
                ri[ln] = (i + 1, len(lines))
        for nd in geom.get("nodes", []):
            if nd.get("star"):
                continue
            anchor = line_anchor.get(nd.get("ln"))
            if anchor is None:
                continue
            m = {"exi": ex_order[anchor]}
            riv = ri.get(nd["ln"])
            if riv:
                m["ri"], m["rn"] = riv
            desc = self.anno_desc.get(anchor)
            if desc:
                m["desc"] = desc
            th = self.anchor_thread.get(anchor)
            if th:
                m["sum"], m["top"], m["tj"], m["tn"] = th["sum"], th["top"], th["tj"], th["tn"]
            nd["m"] = m


def _fc(q: dict) -> tuple[float, float]:
    """(active_ceiling, idle_ceiling) from query params, falling back to the module defaults."""
    def f(k, d):
        try:
            return float((q.get(k) or [d])[0])
        except (TypeError, ValueError):
            return d
    return f("active", S.GAP_ACTIVE_CEILING), f("idle", S.GAP_IDLE_CEILING)


def _epoch(day: str | None, end_of_day: bool) -> float | None:
    if not day:
        return None
    try:
        d = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    if end_of_day:
        d = d.replace(hour=23, minute=59, second=59)
    return d.timestamp()


def make_handler(corpus: Corpus):
    class H(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # quiet
            pass

        def _send(self, code, body, ctype):
            data = body.encode() if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            try:
                corpus.ensure()
            except OSError as e:
                self._send(500, json.dumps({"error": str(e)}), "application/json")
                return
            if u.path == "/":
                self._send(200, CLIENT_HTML, "text/html; charset=utf-8")
            elif u.path == "/api/trees":
                frm = _epoch((q.get("from") or [None])[0], False)
                to = _epoch((q.get("to") or [None])[0], True)
                self._send(200, json.dumps({"trees": corpus.trees_payload(frm, to),
                                            "classes": S.class_meta(), "present": corpus.present,
                                            "topics": corpus.topics,
                                            "db": os.path.basename(corpus.db)}),
                           "application/json")
            elif u.path == "/api/stats":
                frm = _epoch((q.get("from") or [None])[0], False)
                to = _epoch((q.get("to") or [None])[0], True)
                active, idle = _fc(q)
                off = frozenset(filter(None, (q.get("off") or [""])[0].split(",")))
                self._send(200, json.dumps(corpus.stats(frm, to, active, idle, off)),
                           "application/json")
            elif u.path.startswith("/api/segment/"):
                start_uuid = u.path[len("/api/segment/"):]
                active, idle = _fc(q)
                geom = corpus.segment_geometry(start_uuid, active, idle)
                if geom is None:
                    self._send(404, json.dumps({"error": "no such segment"}),
                               "application/json")
                else:
                    self._send(200, json.dumps(geom), "application/json")
            elif u.path == "/api/sessions":
                frm = _epoch((q.get("from") or [None])[0], False)
                to = _epoch((q.get("to") or [None])[0], True)
                self._send(200, json.dumps({"sessions": corpus.sessions(frm, to),
                                            "db": os.path.basename(corpus.db)}),
                           "application/json")
            elif u.path.startswith("/api/session/"):
                sid = u.path[len("/api/session/"):]
                compact = (q.get("compact") or ["1"])[0] not in ("0", "false", "")
                geom = corpus.geometry(sid, compact)
                if geom is None:
                    self._send(404, json.dumps({"error": "no such session"}),
                               "application/json")
                else:
                    self._send(200, json.dumps(geom), "application/json")
            else:
                self._send(404, "not found", "text/plain")

        def do_POST(self):
            u = urlparse(self.path)
            try:
                corpus.ensure()
            except OSError as e:
                self._send(500, json.dumps({"error": str(e)}), "application/json")
                return
            if u.path == "/api/segments":
                # batch geometry: one round-trip for "expand all" instead of N fetches
                active, idle = _fc(parse_qs(u.query))
                n = int(self.headers.get("Content-Length") or 0)
                try:
                    uuids = json.loads(self.rfile.read(n) or b"[]")
                except json.JSONDecodeError:
                    uuids = []
                out = {}
                for uid in uuids:
                    g = corpus.segment_geometry(uid, active, idle)
                    if g is not None:
                        out[uid] = g
                self._send(200, json.dumps(out), "application/json")
            else:
                self._send(404, "not found", "text/plain")
    return H


# ───────────────────────── client (inline, dependency-free) ─────────────────────
# Unified shared-column tree: one scroll container holds the full segment outline
# (depth-indented rows = the tree/ancestry) interleaved with expanded event BANDS.
# Every segment shares ONE global column layout (sticky header, dot x by class), whose
# widths track only the CURRENTLY-EXPANDED segments. Ordinal pitch only. Scrolling the
# one container moves rows + dividers + dots together.
CLIENT_HTML = r"""<!doctype html><html><head><meta charset=utf-8>
<title>Swimlane — live</title><style>
 :root{--bg:#0f1115;--panel:#161a22;--line:#2a2f3a;--mut:#688;--txt:#ddd}
 *{box-sizing:border-box}
 body{margin:0;height:100vh;display:flex;flex-direction:column;font:12px/1.35 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--txt)}
 #bar{flex:none;z-index:20;display:flex;gap:10px;align-items:center;flex-wrap:wrap;
      background:var(--panel);border-bottom:1px solid #333;padding:7px 12px}
 #bar b{color:#9ab} #bar input,#bar button{background:#1d2433;color:#cde;border:1px solid #3a4a5f;
      border-radius:4px;padding:3px 7px;font:inherit} #bar button{cursor:pointer}
 #bar .sp{flex:1} #bar label{color:var(--mut)} .meta{color:var(--mut)}
 /* THE one scroll container — rows + segments scroll together (vertical) and share a
    horizontal scroll, so the sticky column header tracks the columns underneath it */
 /* main area below the bar: the scrolling table (left, flexes) + a fixed detail
    pane (right). The pane is OUTSIDE the table's scroll so it stays pinned. */
 #main{flex:1;display:flex;min-height:0}
 /* #scroll is sized to its content (capped in JS) so the detail frame begins right
    where the columns end; #detail flexes to fill the rest (min 380) */
 #scroll{flex:none;overflow:auto;position:relative;background:var(--bg)}
 #detail{flex:1;min-width:380px;display:flex;flex-direction:column;min-height:0;
      background:#0d1017;border-left:1px solid var(--line)}
 #tabs{flex:none;display:flex;background:#12151c;border-bottom:1px solid var(--line)}
 #tabs .tab{padding:6px 13px;cursor:pointer;color:#889;font-size:11px;border-right:1px solid var(--line);user-select:none}
 #tabs .tab.on{color:#9cf;background:#0d1017;box-shadow:inset 0 -2px 0 #9cf}
 #tabbody{flex:1;overflow:auto;padding:10px 12px;user-select:text;-webkit-user-select:text}
 #detail .kbtn{background:#1d2433;color:#cde;border:1px solid #3a4a5f;border-radius:4px;padding:1px 7px;font:inherit;font-size:10px;cursor:pointer;margin-left:5px}
 /* Topics pane rows: a colour swatch + name; an off topic dims + strikes through */
 #detail .trow{display:flex;align-items:center;gap:8px;padding:3px 3px;cursor:pointer;font-size:11px;color:#bcd;user-select:none;border-radius:3px}
 #detail .trow:hover{background:#171b24}
 #detail .trow.off{opacity:.45}
 #detail .trow.off .tnm{text-decoration:line-through}
 #detail .tsw{width:12px;height:12px;border-radius:3px;flex:none}
 #detail .trow.off .tsw{filter:grayscale(.75)}
 #detail .krow{font-size:11px;line-height:1.5;color:#bcd;margin:2px 0}
 /* stats rows: a per-section grid — columns sized to content (tight) and aligned within
    the section; values right-justified. 2-col (label·value) or 3-col (label·n·dur) */
 #detail .sgrid{display:grid;grid-template-columns:max-content max-content;column-gap:22px;row-gap:1px;font-size:11px;line-height:1.7;margin:1px 0 5px}
 #detail .sgrid3{display:grid;grid-template-columns:max-content max-content max-content;column-gap:16px;row-gap:1px;font-size:11px;line-height:1.7;margin:1px 0 5px}
 /* all columns content-sized & packed (no stretch), so the ceiling knob sits in the
    next column after the count — not floated to the panel edge */
 #detail .sgrid4{display:grid;grid-template-columns:max-content max-content max-content max-content;column-gap:14px;row-gap:3px;font-size:11px;line-height:1.9;margin:1px 0 5px;align-items:center}
 #detail .sgrid4 .sknob{justify-self:end;color:#9ab;white-space:nowrap}
 #detail .sgrid .slbl,#detail .sgrid3 .slbl{color:#bcd} #detail .sgrid .sub{color:#9ab;padding-left:9px}
 #detail .sgrid .sval,#detail .sgrid3 .sval,#detail .sgrid4 .sval{color:#9cf;font-variant-numeric:tabular-nums;font-weight:600;justify-self:end}
 #detail .shint{color:#667;font-weight:400;font-size:10px;text-transform:none;letter-spacing:0}
 #detail .kfc{width:52px;background:#1d2433;color:#cde;border:1px solid #3a4a5f;border-radius:4px;padding:1px 5px;font:inherit;font-size:11px;font-variant-numeric:tabular-nums}
 #detail .knob{color:#9ab;font-size:11px;margin:2px 0 5px;display:flex;gap:6px;align-items:center}
 #detail .splus{color:#6bbb84} #detail .sminus{color:#e07a7a}
 #detail .dhint{color:#667;font-size:11px}
 #detail .dkey{font-size:11px;line-height:1.8;color:#bcd} #detail .dkey b{color:#9cf}
 #detail .dkey hr{border:none;border-top:1px solid #2a2f3a;margin:7px 0} #detail .dkey .sw{display:inline-block;width:14px;text-align:center}
 #detail .dkey .ks{color:#9cf;font-weight:600;font-size:10px;letter-spacing:.06em;text-transform:uppercase;margin:9px 0 2px;border-top:1px solid #2a2f3a;padding-top:6px}
 #detail .dkey .ks:first-of-type{border-top:none;margin-top:4px}
 #detail .dback{color:#6cf;cursor:pointer;font-size:11px;margin-bottom:7px;user-select:none}
 #detail .dmeta{white-space:pre-wrap;font-size:11px;color:#bcd;user-select:text;-webkit-user-select:text}
 /* Selection-tab membership detail: the exchange description + thread summary + topic chips */
 #detail .mrow{margin-top:10px;font-size:11px;line-height:1.5;color:#bcd;white-space:pre-wrap;user-select:text}
 #detail .mlbl{display:block;color:#9cf;font-weight:600;font-size:10px;letter-spacing:.05em;text-transform:uppercase;margin-bottom:2px}
 #detail .tchip{display:inline-block;font-size:10px;padding:0 7px;margin:4px 4px 0 0;border-radius:8px;color:#0c0e13;font-weight:600}
 #detail .mhint{color:#778;font-size:10px;font-weight:400;letter-spacing:0;text-transform:none}
 /* terminal text WORD-WRAPS in its box (no horizontal scroll); vertical scroll as needed */
 #detail .dbody{margin-top:8px;padding:6px 8px;background:#0c0e13;border:1px solid #2a2f3a;border-radius:3px;
      font:11px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre-wrap;
      overflow-wrap:anywhere;overflow-x:hidden;overflow-y:auto;user-select:text;-webkit-user-select:text}
 .nd.sel{box-shadow:0 0 0 2px #0d1017,0 0 0 4px #fff}
 #colhdr{position:sticky;top:0;z-index:15;height:48px;background:#12151c;border-bottom:1px solid var(--line)}
 /* names word-wrap and sit bottom-aligned against the divider */
 #colhdr .chdr{position:absolute;top:0;height:48px;display:flex;align-items:flex-end;justify-content:center;font-size:10px;color:#9ab;font-weight:600;cursor:help;line-height:1.15;overflow:hidden;padding-bottom:4px}
 #colhdr .chdr span{text-align:center;white-space:normal}
 #tree{position:relative}
 /* outline row: depth via padding-left; the segment that follows starts at x=0 so all
    segments align regardless of a row's tree depth */
 .tnode{display:flex;align-items:center;gap:6px;padding:4px 8px;cursor:pointer;user-select:none;border-top:1px solid var(--line);font-variant-numeric:tabular-nums;white-space:nowrap;position:relative}
 /* the spine rail: one continuous vertical line; continuations sit on it, rewinds branch off */
 .tnode::before{content:'';position:absolute;left:19px;top:0;bottom:0;width:2px;background:#33414f;z-index:0}
 .tnode.root::before{top:9px}
 .tnode .railcol{flex:none;width:24px;text-align:center;font:13px/1 ui-monospace,monospace;position:relative;z-index:1;color:#9ab}
 .tnode.fork{opacity:.74} .tnode.fork .railcol{width:46px;text-align:right;color:#c79050}
 .tnode.fork .btext{color:#9a8} .tnode.spine.resume .railcol{color:#5fa8d0} .tnode.spine.compaction .railcol{color:#b07fd0}
 .tnode .chip{font-size:9px;border:1px solid #2a3340;border-radius:3px;padding:0 5px;color:#789;flex:none;width:72px;text-align:center}
 /* chip color = the structural kind (echoes the rail mark): root/session gray ·
    resume blue · compaction purple · rewind amber */
 .tnode .chip.k-root{color:#9ab;border-color:#2a3340} .tnode .chip.k-resume{color:#5fa8d0;border-color:#264a5a}
 .tnode .chip.k-compaction{color:#b07fd0;border-color:#3a2f44} .tnode .chip.k-rewind{color:#c79050;border-color:#3a3020}
 .tnode:hover{background:#171b24} .tnode.root{background:#10131a}
 .tnode .caret{color:var(--mut);width:14px;flex:none;text-align:center}
 .tnode .sid{font-weight:600;color:#9cf;font-family:ui-monospace,monospace;width:74px;flex:none}
 /* duration / prompts / records right-justified, fixed width → aligned across all
    rows; duration = sum of the row's time-box spans (coverage) */
 .tnode .m{color:var(--mut);text-align:right;flex:none;white-space:nowrap;margin-left:18px}
 .m.cov{width:74px;color:#8aa} .m.prm{width:84px}.m.rec{width:92px}
 /* chip + start datetime have fixed widths (the rail has no depth indent — every row
    is flat), so the dt and first-prompt text align straight down, like the right side */
 .tnode .dt{flex:none;width:124px;color:#9ab;font-family:ui-monospace,monospace;font-size:11px;white-space:nowrap}
 .tnode .bmark{flex:none;width:14px;text-align:center}
 .tnode.root .bmark{color:#789}
 .tnode.rewind .bmark{color:#c79050} .tnode.resume .bmark{color:#5fa8d0} .tnode.compaction .bmark{color:#b07fd0}
 .tnode .btext{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#cde}
 .tnode .bmeta{flex:none;color:var(--mut);font-size:11px;padding-left:8px}
 .segment{position:relative;background:#0c0e13;border-top:1px solid #1c2230;border-bottom:1px solid #1c2230}
 /* line semantics: blue=start · yellow=break (a pair) · red=end */
 .dl{position:absolute;border-top:1px dashed} .dlbl{position:absolute;text-align:right;font-size:9px;line-height:1;white-space:nowrap}
 .dl.start{border-color:#3b9eff;opacity:.5}.dl.end{border-color:#e05555;opacity:.5}.dl.brk{border-color:#e0c040;opacity:.7}
 /* a collapsed box bolds its boundary lines (start + last) — that's its marker */
 .dl.bold{border-top-width:3px;opacity:1}
 .dlbl.start{color:#5aa8e0}
 /* a paired start→end time-block, shaded light grey across its y-span. The
    "collapse boxes" toggle turns every box into a green dashed double-line and
    hides its interior dots, so the un-boxed (un-accounted) stretches stand out */
 .block{position:absolute;background:rgba(255,255,255,.05);z-index:0}
 /* gap adjustments: green = active (short inter-block bridge, +time); red = idle
    (over-ceiling part of a long in-block gap, −time, overlaps the grey box) */
 .afill{position:absolute;background:rgba(80,200,120,.20);z-index:1}
 .ifill{position:absolute;background:rgba(224,85,85,.22);z-index:1}
 /* membership lanes (left of the class columns, right of the gutter): one filled cell per
    row — exchange (alternating shade) + focus-thread (topic hue). Contiguous rows read as a
    continuous bar; a gap = incidental/unthreaded; a broken thread bar = non-contiguous. */
 .lane{position:absolute;z-index:3;cursor:pointer;border-radius:1px}
 .lane:hover{outline:1px solid rgba(255,255,255,.45)}
 .nd.hid{display:none}
 .boxtog{position:absolute;font-size:15px;line-height:1;color:#6bbbaa;cursor:pointer;z-index:6;user-select:none}
 .acct{position:absolute;font-size:9px;color:#7aa;white-space:nowrap}
 .gb{position:absolute;height:4px;border-radius:2px} .glbl{position:absolute;font-size:9px;color:#778;white-space:nowrap}
 .nd{position:absolute;width:12px;height:12px;border-radius:50%;z-index:5;cursor:pointer}
 .nd.borrowed{border-radius:1px;transform:rotate(45deg)} .nd.star{background:none!important;font-size:15px;line-height:12px;text-align:center;width:14px}
 /* prompt-column queue dots, all in the prompt-column color:
    ○ hollow ring = queued prompt that gets EMITTED as a prompt event (→ ● solid circle);
    △ hollow triangle = queued interjection (→ ▲ solid triangle = consumed by the turn). */
 .nd.hollow{background:none!important;border:2px solid;box-sizing:border-box}
 .nd.tri{background:none!important;border:none!important;font-size:13px;line-height:12px;text-align:center;width:14px}
 svg.arcs{position:absolute;left:0;top:0;z-index:2;pointer-events:none;overflow:visible}
 #toast{position:fixed;bottom:16px;left:16px;background:#2a3a2a;color:#cfc;padding:6px 12px;border-radius:4px;display:none;z-index:30;font-size:11px}
</style></head><body>
<div id=bar>
 <b>Swimlane</b><span id=dbname class=meta></span>
 <label>from <input id=from type=date></label>
 <label>to <input id=to type=date></label>
 <input id=q placeholder="filter sessions…" size=16>
 <button id=apply>apply</button>
 <span class=sp></span>
 <span id=count class=meta></span>
</div>
<div id=main>
  <div id=scroll><div id=colhdr></div><div id=tree></div></div>
  <div id=detail>
    <div id=tabs><span class="tab on" data-tab=key>Key</span><span class=tab data-tab=stats>Stats</span><span class=tab data-tab=sel>Selection</span></div>
    <div id=tabbody></div>
  </div>
</div>
<div id=toast></div>
<script>
// geometry constants (must mirror swimlane_timeline): node radius, sub-column pitch,
// node inset in a column, inter-column gap, left gutter (elapsed bars + time labels)
const NODER=6, SUBW=14, COLINNER=8, GAP=12, LGUT=200, INDENT=16;
// segment breathing room: MARGINL indents the gutter/bars off the left edge; MARGINR keeps
// the time-box shading off the right scrollbar/detail frame
const MARGINL=12, MARGINR=16;
// membership lanes: two thin columns LEFT of the class columns (right of the gutter) —
// exchange (alternating shade) + focus-thread (topic hue). The class columns start after them.
const LANEW=13, LANEGAP=3, LANEPAD=12;
const EXLANEX=LGUT+MARGINL, THLANEX=EXLANEX+LANEW+LANEGAP, LANES_W=LANEW*2+LANEGAP+LANEPAD;
const EXSHADE=['rgba(255,255,255,.09)','rgba(255,255,255,.20)'];
function exShade(i){return EXSHADE[i%2];}
// topic palette: the live topic set (server-supplied) spread across a maximally-distinct,
// evenly-spaced hue ring. NO embedded vocabulary and NO billable/non-billable line — every
// topic is just a colour; the consumer filters topics in the Topics pane. Palette size is the
// next multiple of 3 ≥ the topic count, so hues stay evenly spread (any spare slots go unused).
let TOPICS=[], TOPIC_COLORS={};
const TOPIC_OFF=new Set();        // topics toggled off in the Topics pane (hides their thread bars)
function buildPalette(){
  TOPIC_COLORS={};const T=TOPICS.length;if(!T)return;
  const N=Math.max(3,Math.ceil(T/3)*3);
  const pal=[];for(let s=0;s<N;s++)pal.push('hsl('+Math.round(s*360/N)+',60%,58%)');
  for(let i=0;i<T;i++)TOPIC_COLORS[TOPICS[i]]=pal[Math.round(i*N/T)%N];   // spread T topics across N slots
}
function topicColor(name){return TOPIC_COLORS[name]||'#7a8699';}
let TREES=[], CLASSES=[], PRESENT=new Set(), EXP={}, COLX={}, COLW={}, COLMS={}, GW=LGUT;
// both knobs are CEILINGS (max-gap thresholds): ACTIVEC = the longest gap we still fill in
// (active), IDLEC = the longest gap we still active before truncating (idle). Live, Stats tab.
let ACTIVEC=300, IDLEC=600;
const BOXC=new Set();   // collapsed time-boxes, keyed "segUuid:boxStartLine" (mixed state)
const $=s=>document.querySelector(s);
function toast(m){const t=$('#toast');t.textContent=m;t.style.display='block';clearTimeout(t._h);t._h=setTimeout(()=>t.style.display='none',1500);}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function countBranches(n){let c=n.branches.length+(n.segments?n.segments.length:0);
  for(const b of n.branches)c+=countBranches(b);for(const f of (n.segments||[]))c+=countBranches(f);return c;}

async function loadTrees(){
  const p=new URLSearchParams();
  if($('#from').value)p.set('from',$('#from').value);
  if($('#to').value)p.set('to',$('#to').value);
  const r=await fetch('/api/trees?'+p);const j=await r.json();
  TREES=j.trees;CLASSES=j.classes;PRESENT=new Set(j.present||[]);TOPICS=j.topics||[];buildPalette();$('#dbname').textContent='· '+j.db;
  EXP={};renderOutline();
}
// the full outline: every segment as a depth-indented row (pre-order DFS), so the
// whole tree/ancestry is visible up front; clicking a row expands ITS event segment
function renderOutline(){
  const q=$('#q').value.toLowerCase();
  const list=TREES.filter(s=>!q||s.sid.toLowerCase().includes(q));
  $('#count').textContent=list.length+' / '+TREES.length+' sessions';
  EXP={};const tree=$('#tree');tree.innerHTML='';
  for(const s of list){
    // FLAT RAIL: everything in the session — root, segments (resume/compaction), and
    // rewinds — sits on ONE rail in ts order, closest to how it actually happened.
    // The initial path is earliest; a rewind (later ts) lands below the segments it
    // branched from. No node is "main" or a dead-end; the mark says which kind it is,
    // the record/prompt counts say how deep it went.
    const rows=flattenAll(s.tree);
    let first=true;
    for(const n of rows){ emitRow(n,first?s:null); first=false; }
  }
  recomputeAndRelayout();
}
function flattenAll(tree){
  const all=[];
  (function walk(n){ all.push(n); for(const f of (n.segments||[]))walk(f); for(const b of (n.branches||[]))walk(b); })(tree);
  all.sort((a,b)=>(a.ts||'').localeCompare(b.ts||''));
  return all;
}
function fmtDT(ts){return ts?ts.slice(0,10)+' · '+ts.slice(11,16):'';}
function fmtdur(s){s=Math.round(s);if(s<60)return s+'s';if(s<3600)return Math.floor(s/60)+'m '+(s%60)+'s';return Math.floor(s/3600)+'h '+Math.floor(s%3600/60)+'m';}
// h m s with leading empty units dropped (no 0h / 0m prefix) but a 0m KEPT once an h
// shows (0h 0m 5s→5s · 1h 0m 5s→1h 0m 5s); seconds always shown
function fmthms(s){s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),sec=s%60;
  if(h)return h+'h '+m+'m '+sec+'s';if(m)return m+'m '+sec+'s';return sec+'s';}
// h m, no seconds (Stats tab) — leading 0h dropped
function fmthm(s){const tm=Math.round(s/60),h=Math.floor(tm/60),m=tm%60;return h?h+'h '+m+'m':m+'m';}
// uniform per-segment row: [mark][caret][chip] start-datetime [first-prompt text] {duration}{prompts}{records}
// chip + datetime are fixed-width, so datetime and first-prompt text align straight down
// the rail; duration/prompts/records right-aligned. Duration = Σ time-box spans (coverage).
function emitRow(node,sess){
  const row=document.createElement('div');
  const kind=sess?'root':node.kind;
  row.className='tnode spine '+kind;
  row._node=node;
  // every node sits ON the rail; the mark says which kind (no node is special)
  const mark=sess?'●':(node.kind==='compaction'?'▣':node.kind==='resume'?'⇲':node.kind==='rewind'?'↺':'●');
  // chip = the mechanically-derived STRUCTURAL kind (root→session · resume · compaction
  // · rewind) — more diagnostic than who-typed-it; the rail glyph echoes it
  const chip=sess?'session':node.kind;
  // show the first ACTUAL typed prompt for EVERY row — root + segments alike (a session/
  // segment often starts on a non-prompt record, so never the bare hash/start label)
  const text=node.first_prompt||(sess?sess.short:node.label);
  row.innerHTML='<span class=railcol>'+mark+'</span><span class=caret>▸</span>'+
    '<span class="chip k-'+kind+'">'+esc(chip)+'</span>'+
    '<span class=dt>'+esc(fmtDT(node.ts))+'</span>'+
    '<span class=btext></span>'+
    '<span class="m cov">'+fmthms(node.coverage_s||0)+'</span>'+
    '<span class="m prm">'+node.n_prompts+' prompts</span>'+
    '<span class="m rec">'+node.n_records+' records</span>';
  row.querySelector('.btext').textContent=text;
  row.onclick=()=>toggleRow(row,node);
  $('#tree').appendChild(row);
}
async function toggleRow(row,node,defer){
  const open=row.classList.toggle('open');
  row.querySelector('.caret').textContent=open?'▾':'▸';
  if(!open){ if(row._segment){row._segment.remove();row._segment=null;} delete EXP[node.u]; if(!defer)recomputeAndRelayout(); return; }
  let g=node._geom;
  if(!g){ try{g=await(await fetch('/api/segment/'+node.u+'?active='+ACTIVEC+'&idle='+IDLEC)).json();}catch(e){g={empty:1};} node._geom=g; }
  if(!row.classList.contains('open'))return;   // collapsed during the fetch — drop the segment
  if(g.empty)return;
  if(row._segment)row._segment.remove();             // guard against a double expand
  const segment=buildSegment(g);segment._u=node.u;row._segment=segment;row.after(segment);EXP[node.u]={segment:segment};
  if(!defer)recomputeAndRelayout();
}
// bulk open/close: ONE batched geometry fetch + ONE relayout (not N of each). Avoids the
// per-row round-trip and the O(n²) relayout that clicking every row would cause.
async function expandAll(){
  const rows=[...document.querySelectorAll('#tree .tnode:not(.open)')];
  if(!rows.length)return;
  const need=rows.filter(r=>!r._node._geom).map(r=>r._node.u);
  if(need.length){
    try{const res=await(await fetch('/api/segments?active='+ACTIVEC+'&idle='+IDLEC,{method:'POST',body:JSON.stringify(need)})).json();
      for(const r of rows){if(res[r._node.u])r._node._geom=res[r._node.u];}}catch(e){}
  }
  for(const r of rows)await toggleRow(r,r._node,true);
  recomputeAndRelayout();
}
function collapseAll(){
  const rows=[...document.querySelectorAll('#tree .tnode.open')];
  for(const r of rows)toggleRow(r,r._node,true);
  recomputeAndRelayout();
}
function buildSegment(g){
  const segment=document.createElement('div');segment.className='segment';segment.style.height=g.height+'px';
  segment._geom=g;segment._tips={};segment._byln={};
  for(const n of g.nodes){segment._tips[n.ln]={tip:n.tip||'',body:n.body||'',m:n.m||null};segment._byln[n.ln]=n;}
  return segment;
}
// column widths follow ONLY the currently-expanded segments (not the whole corpus, which
// could carry drastic outliers): per class, the max sub-columns across open segments
function recomputeAndRelayout(){
  const maxsub={};
  for(const u in EXP){const cl=EXP[u].segment._geom.classes;for(const c in cl)maxsub[c]=Math.max(maxsub[c]||0,cl[c]);}
  // every present class always gets a column (min/name width); expanded segments only
  // GROW the columns they use — header is visible even with nothing open
  COLX={};COLW={};COLMS={};let x=LGUT+MARGINL+LANES_W;   // leave room for the two membership lanes
  for(const cm of CLASSES){const c=cm.cls;if(!PRESENT.has(c))continue;
    const ms=maxsub[c]||1;COLMS[c]=ms;
    const dots=COLINNER+NODER*2+(ms-1)*SUBW;
    const namew=Math.ceil(longestWord(cm.name)*6.2)+10;
    const w=Math.max(dots,namew)+GAP;COLX[c]=x;COLW[c]=w;x+=w;}
  GW=Math.max(x+20+MARGINR,LGUT);
  const TW=Math.max(GW,660);
  $('#colhdr').style.width=TW+'px';$('#tree').style.width=TW+'px';
  // size the scroll to its content PLUS a vertical-scrollbar buffer (SB), so the content
  // (width TW) is never clipped by the scrollbar into a spurious horizontal scroll; the
  // detail frame begins right after that. Capped to keep the detail frame >=380px — only
  // then (or a sub-1080 window) does the left pane scroll horizontally.
  const SB=18, mainW=$('#main').clientWidth||1200;
  $('#scroll').style.width=Math.max(360,Math.min(TW+SB,mainW-380))+'px';
  renderHeader();
  for(const u in EXP)layoutSegment(EXP[u].segment);
}
function longestWord(s){return Math.max.apply(null,s.split(' ').map(w=>w.length).concat([1]));}
function renderHeader(){
  let H='';
  // the two membership-lane headers sit before the class columns
  H+='<div class=chdr style="left:'+EXLANEX+'px;width:'+LANEW+'px" title="exchange membership — each described exchange is a shaded bar; click a bar for its description"><span>ex</span></div>';
  H+='<div class=chdr style="left:'+THLANEX+'px;width:'+LANEW+'px" title="focus-thread membership — topic-hued bar; click a bar for the thread summary"><span>th</span></div>';
  for(const cm of CLASSES){const c=cm.cls;if(!(c in COLX))continue;
    // a 2-word heading stacks on two centered lines
    const p=cm.name.split(' ');
    const nm=p.length===2?esc(p[0])+'<br>'+esc(p[1]):esc(cm.name);
    H+='<div class=chdr style="left:'+COLX[c]+'px;width:'+(COLW[c]-GAP)+'px" title="'+esc(cm.desc)+'"><span>'+nm+'</span></div>';}
  $('#colhdr').innerHTML=H;
}
// center the dots within the column (column is sized to max(dots, header word), so
// the dot cluster centers in whatever the wider of the two is)
function dotX(n){
  const cx=COLX[n.cls]; if(cx==null)return LGUT;
  const ms=COLMS[n.cls]||1, span=(ms-1)*SUBW+NODER*2;
  return cx+(COLW[n.cls]-GAP-span)/2+n.sub*SUBW;
}
// heat color is computed server-side from the actual elapsed seconds (GUTTER_BUCKETS):
// <1s dark · <1m blue · <5m amber · ≥5m red. (Was inferred from bar width, which hit
// red around 60s and never showed the 1–5m amber band.)
function gcolor(b){return b.color||'#4a6e8a';}
// CH = the height a COLLAPSED box keeps — just enough for its bold start+end lines to
// read as a double line. Everything between them is removed and the rest reflows up.
const CH=7;
function layoutSegment(segment){
  const g=segment._geom;segment.style.width=GW+'px';
  let H='';
  // margin-shifted x coords: SL/SW = full-width shaded rows (blocks/fills/lines) inset by
  // MARGINL on the left and MARGINR on the right; GX = gutter bars/labels left origin
  const SL=LGUT-8+MARGINL, SW=GW-LGUT+8-MARGINL-MARGINR, GX=2+MARGINL;
  // collapsed boxes for THIS segment, as sorted [y0,y1] ordinal spans. mapY reflows every
  // element's y: a box's interior compresses to CH and everything below shifts up; mapY
  // clamps an interior y into the thin collapsed slot. inCollapsed = strictly inside one.
  const cbox=[];
  for(const bl of g.blocks){if(BOXC.has(segment._u+':'+bl.s))cbox.push([bl.y0,bl.y1]);}
  cbox.sort((p,q)=>p[0]-q[0]);
  const mapY=y=>{let s=0;for(const[a,b]of cbox){if(b<=y)s+=(b-a-CH);else if(a<y)return (a-s)+Math.min(y-a,CH);}return y-s;};
  const inCollapsed=y=>cbox.some(([a,b])=>y>a+0.5&&y<b-0.5);
  const hidNode=n=>n.box!=null&&BOXC.has(segment._u+':'+n.box);
  const reduce=cbox.reduce((s,[a,b])=>s+(b-a-CH),0), bh=g.height-reduce;
  segment.style.height=bh+'px';
  const boldY=new Set();
  for(const[a,b]of cbox){boldY.add(Math.round(a));boldY.add(Math.round(b));}
  // time-boxes: a collapsed box renders as a CH-tall grey slot at its mapped top
  for(const bl of g.blocks){const k=segment._u+':'+bl.s, c=BOXC.has(k), y0=mapY(bl.y0);
    const h=c?CH:Math.max(2,mapY(bl.y1)-y0);
    H+='<div class=block style="left:'+SL+'px;width:'+SW+'px;top:'+y0+'px;height:'+h+'px" title="block '+fmtdur(bl.dur)+'"></div>';
    H+='<div class=boxtog data-k="'+esc(k)+'" style="left:'+(LGUT-24+MARGINL)+'px;top:'+(y0+1)+'px">'+(c?'▸':'▾')+'</div>';}
  // active (green, between blocks) and idle (red, over a long in-block gap) fills —
  // a idle fill sits inside a box, so it vanishes when that box collapses
  for(const f of (g.active||[])){if(inCollapsed((f.y0+f.y1)/2))continue;const y0=mapY(f.y0);
    H+='<div class=afill style="left:'+SL+'px;width:'+SW+'px;top:'+y0+'px;height:'+Math.max(2,mapY(f.y1)-y0)+'px" title="active gap +'+fmtdur(f.dur)+'"></div>';}
  for(const f of (g.idle||[])){if(inCollapsed((f.y0+f.y1)/2))continue;const y0=mapY(f.y0);
    H+='<div class=ifill style="left:'+SL+'px;width:'+SW+'px;top:'+y0+'px;height:'+Math.max(2,mapY(f.y1)-y0)+'px" title="idle −'+fmtdur(f.idle)+' (of a '+fmtdur(f.dur)+' gap)"></div>';}
  // lines: a collapsed box keeps only its two BOLD boundary lines (the double line);
  // interior lines are removed
  for(const d of g.lines){const isBold=boldY.has(Math.round(d.y));
    if(inCollapsed(d.y)&&!isBold)continue;
    const c=d.kind=='start'?'start':(d.kind=='end'?'end':'brk'), bold=isBold?' bold':'', y=mapY(d.y);
    H+='<div class="dl '+c+bold+'" style="left:'+SL+'px;width:'+SW+'px;top:'+(y-0.5)+'px"></div>';
    if(d.label&&!inCollapsed(d.y))H+='<div class="dlbl start" style="left:'+GX+'px;width:'+(LGUT-20)+'px;top:'+(y-5)+'px">'+esc(d.label)+'</div>';}
  for(const b of g.gutter){if(inCollapsed(b.y))continue;const y=mapY(b.y);
    H+='<div class=gb style="left:'+GX+'px;width:'+b.w+'px;top:'+y+'px;background:'+gcolor(b)+'" title="+'+esc(b.hover)+'"></div>';
    if(b.label)H+='<div class=glbl style="left:'+GX+'px;top:'+(y-9)+'px">'+esc(b.label)+'</div>';}
  // first-pass accounting readout, in the headroom above the first dot
  const a=g.acct;H+='<div class=acct style="left:'+(LGUT+MARGINL+LANES_W)+'px;top:6px">cov '+fmtdur(a.coverage_s)+' / span '+fmtdur(a.span_s)+' · '+a.n_blocks+' blocks · '+a.stranded+' stranded · <span style="color:#6bbb84">+'+fmtdur(a.gap_active_s)+'</span> <span style="color:#e07a7a">−'+fmtdur(a.gap_idle_s)+'</span> → '+fmtdur(a.adjusted_s)+'</div>';
  // membership lanes: one filled cell per distinct row, drawn down to the next row so
  // contiguous same-exchange / same-thread rows read as a continuous bar; an empty cell = an
  // incidental/unthreaded record, a broken thread bar = non-contiguous (interleaved) membership
  {const seen={},yr=[];for(const n of g.nodes){if(hidNode(n)||n.star||(n.y in seen))continue;seen[n.y]=1;yr.push(n);}
   yr.sort((p,q)=>p.y-q.y);
   for(let i=0;i<yr.length;i++){const n=yr[i],m=n.m;if(!m)continue;
     const top=mapY(n.y),bot=(i+1<yr.length)?mapY(yr[i+1].y):top+10,h=Math.max(2,bot-top);
     if(m.exi!=null)H+='<div class=lane style="left:'+EXLANEX+'px;width:'+LANEW+'px;top:'+top+'px;height:'+h+'px;background:'+exShade(m.exi)+'" data-l="'+n.ln+'"></div>';
     const shown=(m.top||[]).filter(t=>!TOPIC_OFF.has(t));   // one stripe per shown topic — a multi-topic thread shows its colours side by side
     if(shown.length){const sw=LANEW/shown.length;
       for(let k=0;k<shown.length;k++)H+='<div class=lane style="left:'+(THLANEX+k*sw)+'px;width:'+sw+'px;top:'+top+'px;height:'+h+'px;background:'+topicColor(shown[k])+'" data-l="'+n.ln+'"></div>';}}}
  for(const n of g.nodes){if(hidNode(n))continue;          // collapsed-box interior dots are gone
    // prompt-column queue dots, prompt-column color: ○ hollow ring = queued prompt that
    // gets emitted (its delivery is the ● solid prompt dot); △ hollow triangle = queued
    // interjection; ▲ solid triangle = where the turn consumed it. ★ = context-prep burst.
    const glyph=n.star?'★':n.cremove?'▲':n.consumed?'△':'';
    const isRing=n.hollow&&!n.consumed;                       // queued→emitted: hollow circle
    const cls='nd'+(n.borrowed?' borrowed':'')+(n.star?' star':'')+((glyph&&!n.star)?' tri':'')+(isRing?' hollow':'');
    const paint=glyph?'color:':(isRing?'border-color:':'background:');
    const x=dotX(n),st='left:'+x+'px;top:'+mapY(n.y)+'px;'+paint+n.color;
    H+='<div class="'+cls+'" style="'+st+'" data-u="'+esc(n.uuid)+'" data-l="'+n.ln+'">'+glyph+'</div>';}
  segment.innerHTML=H;
  // arcs (real SVG nodes; innerHTML into <svg> parses to the HTML namespace and never paints)
  const NS='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(NS,'svg');svg.setAttribute('class','arcs');svg.setAttribute('width',GW);svg.setAttribute('height',bh);
  // queue bridges draw FIRST (behind), parentUuid arcs on top — SVG paint order is
  // document order, so the structural arcs win the overlap
  const ordered=g.edges.slice().sort((a,b)=>(a.kind?0:1)-(b.kind?0:1));
  for(const e of ordered){const a=segment._byln[e.a],b=segment._byln[e.b];if(!a||!b)continue;
    if(hidNode(a)&&hidNode(b))continue;                    // arc fully inside a collapsed box → gone
    const x1=dotX(a)+NODER,y1=mapY(a.y)+NODER,x2=dotX(b)+NODER,y2=mapY(b.y)+NODER;
    // bow the control point off the chord by the HORIZONTAL span (capped) — a gentle
    // constant-ish curve; scaling by vertical span made long same-column arcs swing
    // wildly right
    const bow=Math.min(70,26+Math.abs(x2-x1)*0.18),mx=(x1+x2)/2+bow;
    const p=document.createElementNS(NS,'path');
    p.setAttribute('d','M'+x1+','+y1+' Q'+mx+','+((y1+y2)/2)+' '+x2+','+y2);
    p.setAttribute('fill','none');
    // all relationship arcs share ONE weight (1.25 — between the old 1.0 and 1.5); the
    // queue bridge keeps its unique amber, parentUuid arcs stay gray (red = ts inversion)
    if(e.kind){p.setAttribute('stroke','#d8a23a');p.setAttribute('stroke-width','1.25');
      p.setAttribute('opacity','.9');
      const ti=document.createElementNS(NS,'title');ti.textContent=e.kind;p.appendChild(ti);}
    else{p.setAttribute('stroke',e.up?'#c05050':'#3a4a5f');p.setAttribute('stroke-width','1.25');
      p.setAttribute('opacity','.8');}
    svg.appendChild(p);}
  segment.appendChild(svg);
}
// detail pane: LEFT-CLICK a dot to render its metadata + terminal text in the right
// pane (selectable for manual copy — no auto-clipboard). Tips are preloaded per segment
// (segment._tips, keyed by line); walk up to the nearest segment.
// ── right frame: three tabs (Key / Stats / Selection). Key carries the legend + the
// view controls (segment + time-box collapse/expand); Stats shows corpus totals;
// Selection holds the clicked dot's detail (auto-focused on click).
let SELDOT=null, SEL=null, TAB='key';
function keyHTML(){return `<div class=dkey>
<div class=ks>Segments <button class=kbtn data-act=collapseAll>collapse all</button><button class=kbtn data-act=expandAll>expand all</button></div>
<div class=krow><span class=sw>●</span>session · <span class=sw style="color:#5fa8d0">⇲</span>resume · <span class=sw style="color:#b07fd0">▣</span>compaction · <span class=sw style="color:#c79050">↺</span>rewind — the structural kind (rail mark + worded chip)</div>
<div class=krow>Each row is one segment: mark + kind chip · start datetime · first typed prompt · then right-aligned <b>coverage</b> (Σ time-box duration) · <b>prompts</b> · <b>records</b>. Click a row to open its event segment.</div>
<div class=ks>Time-boxes <button class=kbtn data-act=boxCollapse>collapse all</button><button class=kbtn data-act=boxExpand>expand all</button></div>
<div class=krow><span style="background:rgba(255,255,255,.10);padding:0 6px">&nbsp;</span> a paired start→end block; its duration counts as coverage. Each box's ▾/▸ collapses it (hides its dots, bolds its edges).</div>
<div class=krow><span style="background:rgba(80,200,120,.20);padding:0 6px">&nbsp;</span> active gap (+time) — a short gap BETWEEN blocks, filled when under the active ceiling</div>
<div class=krow><span style="background:rgba(224,85,85,.22);padding:0 6px">&nbsp;</span> idle gap (−time) — the part of a long IN-block gap above the idle ceiling, truncated</div>
<div class=krow class=shint>both ceilings are tunable in the Stats tab; the idle ceiling also sets the red gutter threshold.</div>
<div class=ks>Dots</div>
<div><span class=sw style="color:#00d2ff">●</span> record — fill colour = its column</div>
<div><span class=sw style="color:#00d2ff">○</span>→<span class=sw style="color:#00d2ff">●</span> queued user prompt → emitted as a prompt event (hollow circle → solid circle, linked by a queue arc)</div>
<div><span class=sw style="color:#00d2ff">△</span>→<span class=sw style="color:#00d2ff">▲</span> queued interjection → consumed inline by the running turn (hollow triangle → solid triangle at the remove; text in the detail pane)</div>
<div><span class=sw>◆</span> untimestamped record — midpoint of its neighbours</div>
<div><span class=sw style="color:#e8c84a">★</span> context-prep burst (replays / compaction; zero work)</div>
<div><span class=sw style="color:#fff">◎</span> selected dot (white ring)</div>
<div class=ks>Lines</div>
<div><b style="color:#3b9eff">━</b> start (a typed prompt)</div>
<div><b style="color:#e05555">━</b> end (turn stop / interrupt)</div>
<div><b style="color:#e0c040">━</b> break (a pair — answer or auto-continue)</div>
<div class=ks>Arcs</div>
<div><b style="color:#6f8499">⌒</b> parentUuid (parent→child)</div>
<div><b style="color:#c05050">⌒</b> ts inversion (child precedes parent)</div>
<div><b style="color:#d8a23a">⌒</b> queue bridge (spawn / consume / deliver)</div>
<div class=ks>Gutter</div>
<div>left bar = elapsed since previous record (log length): <span style="color:#4a6e8a">&lt;1m</span> · <span style="color:#b08030">1–5m</span> · <span style="color:#a04040">≥5m</span></div>
<div class=ks>Membership lanes</div>
<div>two thin columns left of the event columns: <b>ex</b> = the record's described exchange (alternating shade) · <b>th</b> = its focus-thread (topic hue). A gap = incidental/unthreaded work; a broken thread bar = non-contiguous (interleaved) membership. Click a bar (or any dot) to read its exchange description + thread summary in Selection.</div>
</div>`;}
function setTab(t){TAB=t;document.querySelectorAll('#tabs .tab').forEach(el=>el.classList.toggle('on',el.dataset.tab===t));renderTab();}
function renderTab(){const body=$('#tabbody');
  if(TAB==='key')body.innerHTML=keyHTML();
  else if(TAB==='stats')renderStats(body);
  else renderSel(body);}
function renderSel(body){
  if(!SEL){body.innerHTML='<div class=dhint>Left-click a dot (or a lane bar) to inspect it here. Drag to select · Ctrl/⌘+C to copy.</div>';return;}
  body.textContent='';
  const m=document.createElement('div');m.className='dmeta';m.textContent=SEL.tip;body.appendChild(m);
  if(SEL.body){const b=document.createElement('div');b.className='dbody';b.textContent=SEL.body;body.appendChild(b);}
  // membership: the record's exchange description + its focus-thread summary + topic chips
  const mm=SEL.m;
  if(mm){
    if(mm.desc){const d=document.createElement('div');d.className='mrow';
      d.innerHTML='<span class=mlbl>Exchange'+(mm.ri?' <span class=mhint>· record '+mm.ri+'/'+mm.rn+'</span>':'')+'</span>'+esc(mm.desc);body.appendChild(d);}
    if(mm.sum){const t=document.createElement('div');t.className='mrow';
      t.innerHTML='<span class=mlbl>Thread'+(mm.tj?' <span class=mhint>· exchange '+mm.tj+'/'+mm.tn+'</span>':'')+'</span>'+esc(mm.sum);body.appendChild(t);}
    if(mm.top&&mm.top.length){const tp=document.createElement('div');tp.className='mrow';
      let chips='';for(const x of mm.top)chips+='<span class=tchip style="background:'+topicColor(x)+'">'+esc(x)+'</span>';
      tp.innerHTML='<span class=mlbl>Topics</span><div>'+chips+'</div>';body.appendChild(tp);}
    if(!mm.desc&&!mm.sum){const h=document.createElement('div');h.className='mrow mhint';h.textContent='(this record is in an exchange not yet described / threaded)';body.appendChild(h);}
  }
  body.scrollTop=0;}
// Topics pane: every topic the corpus uses, each its palette colour. Toggle one to hide its
// thread-lane bars (purely a view filter — no billable/non-billable grouping).
function relayoutOpen(){for(const u in EXP)layoutSegment(EXP[u].segment);}
// the topic toggle list (lives in the Stats tab — toggling moves the totals AND hides lane bars)
function topicTogglesHTML(){
  if(!TOPICS.length)return '';
  let H='<div class=ks>Topics <button class=kbtn data-act=topicAll>all</button><button class=kbtn data-act=topicNone>none</button></div>'
    +'<div class=shint style="margin-bottom:5px">Totals above count only threads with a SHOWN topic (ANY-match) — toggle to include/exclude (also hides its thread-lane bars).</div>';
  for(const t of TOPICS){const off=TOPIC_OFF.has(t);
    H+='<div class="trow'+(off?' off':'')+'" data-topic="'+esc(t)+'"><span class=tsw style="background:'+topicColor(t)+'"></span><span class=tnm>'+esc(t)+'</span></div>';}
  return H;}
function gcell(l,v){return '<span class=slbl>'+esc(l)+'</span><span class=sval>'+esc(''+v)+'</span>';}
async function renderStats(body){
  body.innerHTML='<div class=dhint>loading…</div>';
  const p=new URLSearchParams();if($('#from').value)p.set('from',$('#from').value);if($('#to').value)p.set('to',$('#to').value);
  p.set('active',ACTIVEC);p.set('idle',IDLEC);
  if(TOPIC_OFF.size)p.set('off',[...TOPIC_OFF].join(','));
  let j;try{j=await(await fetch('/api/stats?'+p)).json();}catch(e){body.innerHTML='<div class=dhint>error loading stats</div>';return;}
  if(TAB!=='stats')return;                          // tab changed during the fetch
  const T=j.time,C=j.counts;
  // each adjustment row inlines its own governing CEILING knob (both are max-gap ceilings)
  let H='<div class=dkey><div class=ks>Time</div><div class=sgrid>'
    +gcell('total',fmthm(T.total_s))+gcell('time-boxed',fmthm(T.timeboxed_s))
    +'<span class=slbl><b>adjusted active</b></span><span class=sval><b>'+fmthm(T.adjusted_s)+'</b></span></div>'
    +'<div class=ks>Adjustments <span class=shint>(per-segment, filtered topics)</span></div>'
    +'<div class=sgrid4>'
    +'<span class="slbl splus">active gaps</span><span class="sval splus">+'+fmthm(T.gap_active_s)+'</span><span class=sval>('+C.gap_active_n+')</span>'
    +'<span class=sknob>ceiling <input class=kfc id=kactive value="'+ACTIVEC+'">s</span>'
    +'<span class="slbl sminus">idle gaps</span><span class="sval sminus">−'+fmthm(T.gap_idle_s)+'</span><span class=sval>('+C.gap_idle_n+')</span>'
    +'<span class=sknob>ceiling <input class=kfc id=kidle value="'+IDLEC+'">s</span>'
    +'</div>'
    +'<div class=ks>Counts</div><div class=sgrid>'
    +gcell('exchanges',C.exchanges)+gcell('time-boxes',C.timeboxes)+'</div>'
    +topicTogglesHTML()
    +'<hr><div style="color:#667">'+j.sessions+' sessions · '+j.segments+' segments · over the from/to window</div></div>';
  body.innerHTML=H;}
// live ceilings: invalidate cached geometry, re-fetch open segments with the new knobs
function clearGeom(n){delete n._geom;(n.segments||[]).forEach(clearGeom);(n.branches||[]).forEach(clearGeom);}
async function applyFC(){
  const nb=parseFloat($('#kactive').value), nc=parseFloat($('#kidle').value);
  if(!isNaN(nb)&&nb>=0)ACTIVEC=nb; if(!isNaN(nc)&&nc>0)IDLEC=nc;
  TREES.forEach(s=>clearGeom(s.tree));
  const open=[...document.querySelectorAll('#tree .tnode.open')], need=open.map(r=>r._node.u);
  if(need.length){
    try{const res=await(await fetch('/api/segments?active='+ACTIVEC+'&idle='+IDLEC,{method:'POST',body:JSON.stringify(need)})).json();
      for(const r of open){const gg=res[r._node.u];if(gg){r._node._geom=gg;if(r._segment)r._segment.remove();const segment=buildSegment(gg);segment._u=r._node.u;r._segment=segment;r.after(segment);EXP[r._node.u]={segment:segment};}}}catch(e){}
  }
  recomputeAndRelayout();
  if(TAB==='stats')renderTab();
}
function showDetail(nd,rec){if(SELDOT)SELDOT.classList.remove('sel');SELDOT=nd;if(nd)nd.classList.add('sel');SEL=rec;setTab('sel');}
setTab('key');
document.addEventListener('click',ev=>{const t=ev.target.closest('#tabs .tab');if(t){setTab(t.dataset.tab);return;}
  const lane=ev.target.closest('.lane');                  // a lane bar selects that row too
  if(lane){let el=lane;while(el&&!el._tips)el=el.parentElement;const rec=el&&el._tips[lane.dataset.l];if(rec)showDetail(null,rec);return;}
  const nd=ev.target.closest('.nd');if(!nd)return;
  let el=nd;while(el&&!el._tips)el=el.parentElement;
  const rec=el&&el._tips[nd.dataset.l];
  if(rec)showDetail(nd,rec);
});
document.addEventListener('contextmenu',ev=>{const nd=ev.target.closest('.nd');if(!nd)return;ev.preventDefault();
  const u=nd.dataset.u||'';(navigator.clipboard?navigator.clipboard.writeText(u):Promise.reject())
    .then(()=>toast('copied '+u),()=>toast('copy failed'));});
$('#apply').onclick=()=>{loadTrees();if(TAB!=='key')renderTab();};
$('#q').oninput=renderOutline;
// ceiling knobs (Stats tab) — commit on change (Enter/blur)
document.addEventListener('change',ev=>{if(ev.target.closest('.kfc'))applyFC();});
// time-boxes: global Collapse/Expand are idempotent (set every open segment's boxes);
// individual ▾/▸ toggles one box — so a mixed state is reachable
function setAllBoxes(collapse){
  for(const u in EXP){const b=EXP[u].segment;for(const bl of b._geom.blocks){const k=b._u+':'+bl.s;collapse?BOXC.add(k):BOXC.delete(k);}}
  for(const u in EXP)layoutSegment(EXP[u].segment);
}
// the view-control buttons now live in the Key tab (delegated, since the tab re-renders)
document.addEventListener('click',ev=>{const b=ev.target.closest('.kbtn');if(!b)return;const a=b.dataset.act;
  if(a==='collapseAll')collapseAll();
  else if(a==='expandAll')expandAll();
  else if(a==='boxCollapse')setAllBoxes(true);
  else if(a==='boxExpand')setAllBoxes(false);
  else if(a==='topicAll'){TOPIC_OFF.clear();relayoutOpen();renderTab();}
  else if(a==='topicNone'){TOPICS.forEach(t=>TOPIC_OFF.add(t));relayoutOpen();renderTab();}});
document.addEventListener('click',ev=>{const r=ev.target.closest('.trow');if(!r)return;
  const t=r.dataset.topic;TOPIC_OFF.has(t)?TOPIC_OFF.delete(t):TOPIC_OFF.add(t);
  relayoutOpen();renderTab();});
document.addEventListener('click',ev=>{const tg=ev.target.closest('.boxtog');if(!tg)return;ev.stopPropagation();
  const k=tg.dataset.k;BOXC.has(k)?BOXC.delete(k):BOXC.add(k);
  const segment=tg.closest('.segment');if(segment)layoutSegment(segment);});
// deep-link: ?seg=<start-uuid prefix> auto-opens that segment on load (shareable link to a
// specific segment; also lets a headless capture render an expanded view)
async function autoOpenFromURL(){
  const params=new URLSearchParams(location.search);
  const seg=params.get('seg');
  if(seg){const row=[...document.querySelectorAll('#tree .tnode')].find(r=>r._node&&(r._node.u||'').startsWith(seg));
    if(row){await toggleRow(row,row._node);(row._segment||row).scrollIntoView({block:'start'});}}
  const tab=params.get('tab');if(tab)setTab(tab);   // deep-link a starting tab (key/stats/sel)
}
loadTrees().then(autoOpenFromURL);
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=_paths.db("raw.db"),
                    help="raw transcript DB built by raw_db.py --dir")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    if not os.path.exists(a.db):
        sys.exit(f"db not found: {a.db} (build it: uv run ${CLAUDE_SKILL_DIR}/raw_db.py --dir <project>)")
    corpus = Corpus(a.db)
    corpus.ensure()
    print(f"serving {len(corpus.meta)} sessions from {a.db} at http://localhost:{a.port}/")
    ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(corpus)).serve_forever()


if __name__ == "__main__":
    main()

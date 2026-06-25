#!/usr/bin/env python3
"""Swimlane timeline of one transcript's records — EVERY JSONL type, including
the ten untimestamped UI-state types the main DB drops at ingest.

Sub-agent transcripts don't draw (time-spent lens, ruled 2026-06-11): every run is
superseded by its main-chain Agent tool dots — the returning tool_result carries the
recorded totalDurationMs/status/tokens (proven 103/103 with zero runtime outliers);
the raw DB retains them. Queue operations draw as dots beside the prompt column
(enqueue = prompt typed mid-run, the interjection detector) but never as dividers.
Dividers are stop/start pairs: prompt (cyan start) · turn_duration (red stop —
incl. AskUserQuestion waits) · user answer (blue restart) · interrupt (red break).
The key is a hover button (top right). Columns pool records by class (prompt / thinking / text / tool_use /
tool_result / attachment / system / each UI-state type); the y-axis is time
flowing downward with hour ticks, idle-compressed. Within a column, greedy
sub-column packing spreads same-instant bursts sideways (a sub-column is
reused as soon as the previous node clears it).

Y spacing is piecewise linear: dt x PX_PER_S between consecutive distinct
timestamps, clamped to [MIN_STEP, MAX_STEP] px; gaps > IDLE_MIN become hatched
idle bands grown to fit their hour ticks. `--compact` switches to ordinal pitch:
uniform rows, elapsed time as log-length heat bars in the gutter (no idle bands,
no hour grid — the labeled cyan/red exchange/interrupt dividers are the time
landmarks). Ordering is always honest; proportion holds only between the clamps.
Positions come from raw record timestamps only — no DB gap model is involved.
Untimestamped records (diamonds) sit at the MIDPOINT of the neighboring
timestamped records' ts in their file.

The parentUuid hierarchy is drawn as arcs weaving between columns; a red arc
marks a child whose recorded ts precedes its parent's (write-order noise: ts
is unreliable within a burst; the chain is the true order there).

A companion markdown (same stem, `.md`) documents every entity class: its
description (also the column header's hover text) and which of its JSONL
properties the diagram shows vs hides.

    uv run ${CLAUDE_SKILL_DIR}/raw_db.py --file <transcript.jsonl> --db ~/.claude/a-horde-o-bees/transcripts/raw.db
    uv run ${CLAUDE_SKILL_DIR}/swimlane_timeline.py [--db ~/.claude/a-horde-o-bees/transcripts/raw.db] \
        [--lines 100] [--out ~/.claude/a-horde-o-bees/transcripts/diagrams/swimlane-timeline.html]
"""
import argparse
import bisect
import html
import json
import math
import pathlib
import sqlite3
from datetime import datetime, timezone

import _paths

IDLE_MIN = 90          # gaps beyond this compress to an idle band
IDLE_H = 40            # minimum px height of a compressed idle band
PER_HOUR = 16          # idle bands grow to fit their hour ticks at this pitch
                       # (like timeline.py), so the hour grid never disappears
PX_PER_S = 10.0        # active-time vertical scale
MIN_STEP = 16          # px guaranteed between consecutive distinct timestamps
MAX_STEP = 600         # cap one stretch so a single long wait can't dominate
NODE_R = 6
SUB_W = NODE_R * 2 + 2  # per-dot pitch: the 12px dot + a 2px gap. This is the ONLY
                        # width an extra simultaneous dot imposes on its column.
COL_INNER = 8           # node offset from the column's left edge
COL_GAP = 12            # whitespace between a column's nodes and the next column
HDR_CHAR_W = 6.0        # px per header char (10px semibold .cname, conservative) — a
                        # column floors wide enough to fit its longest header WORD on
                        # one line (multi-word headers still wrap at the space)
LEFT = 200              # tick-label gutter: elapsed bars (x 2-100) + right-aligned
                        # timestamps (hour ticks, exchange/interrupt dividers)

COLORS = {
    "prompt": "#00d2ff", "user-response": "#19b8a6",
    "user-interrupt": "#d05a5a",
    "thinking": "#8a6fc0", "text": "#2e8b57",
    "tool_use": "#e0a030", "tool_result": "#d2691e",
    "attachment": "#6f7f8f", "system": "#b0506e", "context-prep": "#e8c84a",
    "ai-title": "#4f6f5f", "last-prompt": "#4f5f7f", "custom-title": "#6f5f4f",
    "file-history-snapshot": "#7f6f4f", "permission-mode": "#7f4f6f",
    "mode": "#5f6f7f", "queue-operation": "#9f7f4f", "pr-link": "#4f7f7f",
    "agent-name": "#6f6f6f", "bridge-session": "#5f5f5f",
    "worktree-state": "#7f7f5f", "agent-setting": "#5f7f5f", "other": "#999",
}

CLASS_ORDER = ["prompt", "user-response", "user-interrupt",
               "thinking", "text", "tool_use",
               "tool_result", "attachment", "system", "queue-operation",
               "context-prep",
               "pr-link", "ai-title", "last-prompt", "custom-title",
               "permission-mode", "mode", "file-history-snapshot", "agent-name",
               "bridge-session", "worktree-state", "agent-setting", "other"]

# column-header hover text + the companion md's description column
CLASS_DESC = {
    "prompt": "A typed user prompt (a `user` record with no tool_result content) — opens an exchange.",
    "queue-operation": "Prompt-queue lifecycle (right of system). enqueue = a message entered the queue — a mid-run typed prompt OR a background-task notification (carries content + <tool-use-id>/<task-id>; the ONLY identity-bearing op); dequeue = head delivered; remove = head discarded; popAll = queue flushed (own message delivered, rest discarded). No uuid — attaches to a segment by line locality. Relationships (thick amber arcs) anchor on the enqueue: spawn (→ its tool_use, by id), consume (→ its next op, by stream adjacency), deliver (→ the delivered record, by content; never for remove). Not a divider — never an activity break. See ARCHITECTURE.md 'Prompt-queue resolution'.",
    "user-response": "The operator answering an interactive tool (AskUserQuestion, plan-mode approval) — a tool_result authored by a human, so its pre-gap is human decision time, not machine runtime.",
    "user-interrupt": "The operator breaking execution (Escape) — '[Request interrupted by user...]'. A hard stop of machine contiguity and an exchange border: whatever follows is a new segment. Gets its own (red) divider line.",
    "thinking": "An assistant record whose content is thinking only — internal reasoning before text/tool output.",
    "text": "An assistant record carrying visible response text (may also contain thinking).",
    "tool_use": "An assistant record emitting a tool call (first tool_use content block names the tool).",
    "tool_result": "A `user` record carrying a tool's returned output — top-level toolUseResult, or tool_result content blocks alone (the sub-agent shape, sourceToolAssistantUUID). Label resolves the tool name via its tool_use_id.",
    "attachment": "Harness-injected context payload (skills list, file snapshot, system reminder).",
    "system": "Harness-mechanical records: system notices (turn_duration with durationMs, compact_boundary chain re-roots, api_error breaks) AND harness-authored user-typed-looking records (label user-meta: slash-command stubs, the local-command caveat) — neither operator nor model.",
    "context-prep": "One star = a collapsed run of context-prep records: replay copies (a compaction/resume/fork re-writing earlier events verbatim — same uuid, original ts) and isCompactSummary headers. Zero work; the primary DB drops these at ingest (uuid canonicality). Anchored at the write moment, not the replayed timestamps.",
    "pr-link": "GitHub PR associated with the session. Timestamped.",
    "ai-title": "Auto-generated session title for the session list. No timestamp.",
    "last-prompt": "Cache of the most recent typed prompt, for the resume-picker UI. No timestamp.",
    "custom-title": "User-assigned session title. No timestamp.",
    "permission-mode": "Permission-mode state flip (auto, bypassPermissions, ...). No timestamp.",
    "mode": "UI mode state (normal, plan, ...). No timestamp.",
    "file-history-snapshot": "Tracked-file backup manifest for /rewind (nested ts only). No timestamp.",
    "agent-name": "Named-agent label attached to the session. No timestamp.",
    "bridge-session": "Companion/remote bridge linkage id. No timestamp.",
    "worktree-state": "Worktree session metadata (path, branch, original HEAD). No timestamp.",
    "agent-setting": "Agent profile setting. No timestamp.",
    "other": "Unrecognized record type.",
}

# top-level JSONL properties the diagram projects somewhere (position, color,
# shape, arcs, or tooltip). Everything else found in the data lands in the
# companion md's "hidden" column.
SHOWN_PROPS = {
    "type", "subtype", "timestamp", "uuid", "parentUuid", "isSidechain",
    "message", "toolUseResult", "attachment", "aiTitle", "customTitle",
    "lastPrompt", "permissionMode", "mode", "agentName", "operation",
    "content", "prUrl", "durationMs",
}


def classify(e: dict) -> tuple[str, str]:
    """(node class, short label) for a record."""
    t = e.get("type")
    if t == "assistant":
        kinds, tool = [], None
        for c in ((e.get("message") or {}).get("content") or []):
            if isinstance(c, dict):
                kinds.append(c.get("type"))
                if c.get("type") == "tool_use":
                    tool = c.get("name")
        if tool:
            return "tool_use", f"tool_use:{tool}"
        if "thinking" in kinds and "text" not in kinds:
            return "thinking", "thinking"
        return "text", f"assistant[{','.join(k or '?' for k in kinds)}]"
    if t == "user":
        # a tool result is marked by the top-level toolUseResult key OR by
        # tool_result content blocks alone — sub-agent transcripts carry the
        # latter shape (sourceToolAssistantUUID instead of toolUseResult)
        content = (e.get("message") or {}).get("content")
        if "toolUseResult" in e or (isinstance(content, list) and any(
                isinstance(x, dict) and x.get("type") == "tool_result"
                for x in content)):
            return "tool_result", "tool_result"
        # harness-authored user records: slash-command invocations/output stubs,
        # the local-command caveat (isMeta), interruption markers. Not typed
        # prompts — they must not read as exchange starts.
        txt = content if isinstance(content, str) else "\n".join(
            x.get("text", "") for x in (content or [])
            if isinstance(x, dict) and x.get("type") == "text")
        txt = (txt or "").strip()
        # the user breaking execution (Escape) — an exchange border and a hard
        # stop of machine contiguity, so it gets its own class, not user-meta
        if txt.startswith("[Request interrupted"):
            return "user-interrupt", "user-interrupt"
        # a delivered background-task notification (dequeued from the prompt queue):
        # harness-authored, NOT a typed prompt — it must not read as an exchange
        # start (it was polluting the START set + branch detection + prompt counts).
        # Carries <task-id>/<tool-use-id> linking it to the tool_use that spawned it.
        if txt.startswith("<task-notification"):
            return "system", "task-notification"
        # a slash command / skill the user TYPED (`<command-name>/x</command-name>`) —
        # the system consumes it under a command signature, but it's a real user prompt
        if txt.startswith("<command-name>"):
            return "prompt", "command"
        if (e.get("isMeta") or not txt or txt.startswith("<command-")
                or txt.startswith("<local-command")):
            return "system", "user-meta"      # harness-authored, pooled w/ system
        return "prompt", "PROMPT"
    if t == "system":
        return "system", f"system:{e.get('subtype', '?')}"
    if t == "attachment":
        return "attachment", f"attachment:{(e.get('attachment') or {}).get('type', '?')}"
    if t == "queue-operation":
        # the enqueue is the only identity-bearing op; its content discriminates a
        # typed user prompt from a harness notification (no explicit flag — the
        # <task-notification> wrapper is the only tell). Surface it in the label.
        op = e.get("operation") or "?"
        if op == "enqueue":
            c = (e.get("content") or "").lstrip()
            # `_synthetic` (set by the corpus loader) marks an enqueue whose delivered
            # counterpart is an isMeta user record — an agent self-authored continuation
            # (a /loop or scheduled-wakeup prompt), not a genuine operator prompt. Treat
            # it as a notification so it never draws a user-prompt (hollow) dot.
            kind = ("notification" if e.get("_synthetic") or c.startswith("<task-notification")
                    else "loop" if c.startswith("<<") else "prompt")
            return "queue-operation", f"enqueue:{kind}"
        return "queue-operation", op
    return (t if t in COLORS else "other"), (t or "?")


def content_text(e: dict) -> str:
    """The record's content with embedded newlines preserved — the tooltip tail."""
    t = e.get("type")
    if t in ("user", "assistant"):
        content = (e.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        out = []
        for c in (content or []):
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text":
                out.append(c.get("text", ""))
            elif c.get("type") == "thinking":
                out.append(c.get("thinking", ""))
            elif c.get("type") == "tool_use":
                inp = c.get("input") or {}
                out.append(inp.get("command") or json.dumps(inp, ensure_ascii=False)[:400])
            elif c.get("type") == "tool_result":
                tc = c.get("content")
                if isinstance(tc, str):
                    out.append(tc)
        return "\n".join(x for x in out if x)
    for k in ("aiTitle", "customTitle", "lastPrompt", "content", "prUrl"):
        if e.get(k):
            return str(e[k])
    return ""


def _short_file(path: str) -> str:
    name = path.rsplit("/", 1)[-1].removesuffix(".jsonl")
    return name if "/subagents/" not in path else f"sub:{name.removeprefix('agent-')[:9]}"


def _ep(ts: str) -> float:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def load(db: str, lines: int) -> list[dict]:
    """Rows from the raw DB, file order; `lines` trims each file to its first N."""
    conn = sqlite3.connect(db)
    recs = []
    for file, line, is_replay, is_cs, payload in conn.execute(
            "SELECT file, line, is_replay, is_compact_summary, json "
            "FROM raw ORDER BY file, line"):
        if lines and line > lines:
            continue
        e: dict = {"type": "<unparseable>"}
        try:
            e = json.loads(payload)
        except json.JSONDecodeError:
            pass
        e["_file"] = file
        e["_line"] = line
        # context-prep: replay copies (DB-marked via the primary DB's uuid-
        # canonicality rule) + compact-summary headers. Zero work either way.
        e["_ctx"] = bool(is_replay or is_cs)
        # the two marks kept separate (branch_tree needs them apart: a replay is
        # never a forest node, but a compact-summary stays as a single-child
        # pass-through so the post-compact chain links back through it)
        e["_replay"] = bool(is_replay)
        e["_cs"] = bool(is_cs)
        recs.append(e)
    conn.close()
    return recs


def build(recs: list[dict]) -> tuple[list, list, list]:
    """Pool records into one column per class. Returns (nodes, edges, lane_labels)."""
    # untimestamped records take the MIDPOINT of the neighboring timestamped
    # records' ts within their file (preceding-only at file end; a leading run
    # with no preceding anchor is dropped)
    for e in recs:
        e["_id"] = f"{e['_file']}:{e['_line']}"

    by_file: dict[str, list[dict]] = {}
    for e in recs:
        by_file.setdefault(e["_file"], []).append(e)
    for file_recs in by_file.values():
        # NEAREST timestamped neighbor by file order on each side — never min/max
        # over the whole file: resume replays re-write earlier events (original
        # ts) later in the file, so a global min-following reaches across hours.
        # Context-prep records never serve as anchors: their ts is the replayed
        # original, not the write moment.
        n = len(file_recs)
        prev_t: list[float | None] = [None] * n
        next_t: list[float | None] = [None] * n
        run: float | None = None
        for i, e in enumerate(file_recs):
            prev_t[i] = run
            if e.get("timestamp") and not e["_ctx"]:
                run = _ep(e["timestamp"])
        run = None
        for i in range(n - 1, -1, -1):
            next_t[i] = run
            if file_recs[i].get("timestamp") and not file_recs[i]["_ctx"]:
                run = _ep(file_recs[i]["timestamp"])
        for i, e in enumerate(file_recs):
            e["_prev_t"], e["_next_t"] = prev_t[i], next_t[i]
            if e.get("timestamp") and not e["_ctx"]:
                e["_t"] = _ep(e["timestamp"])
                e["_borrowed"] = False
                continue
            p, x = prev_t[i], next_t[i]
            if p is not None and x is not None:
                e["_t"] = (p + x) / 2
            else:
                # file edge: only one side exists — anchor to it ("None" only
                # when a file has no timestamped records at all)
                e["_t"] = p if p is not None else x
            e["_borrowed"] = True

    # collapse each consecutive run of context-prep records into ONE star node,
    # anchored at the write moment (its non-ctx neighbors), so replayed history
    # doesn't smear across the timeline and the viz stays focused on active time
    stars = []
    for file_recs in by_file.values():
        i = 0
        while i < len(file_recs):
            if not file_recs[i]["_ctx"]:
                i += 1
                continue
            j = i
            while j + 1 < len(file_recs) and file_recs[j + 1]["_ctx"]:
                j += 1
            burst = file_recs[i:j + 1]
            kinds: dict[str, int] = {}
            o_ts = []
            for e in burst:
                k = e.get("type") or "?"
                if e.get("isCompactSummary"):
                    k = "compact-summary"
                kinds[k] = kinds.get(k, 0) + 1
                if e.get("timestamp"):
                    o_ts.append(e["timestamp"])
            stars.append({
                "file": burst[0]["_file"], "line": burst[0]["_line"],
                "line_to": burst[-1]["_line"],
                "t": burst[0]["_t"], "n": len(burst), "kinds": kinds,
                "o_span": (min(o_ts), max(o_ts)) if o_ts else None,
            })
            i = j + 1
    recs = [e for e in recs if e.get("_t") is not None and not e["_ctx"]]
    recs = [e for e in recs if e.get("_t") is not None]

    by_uuid = {e["uuid"]: e for e in recs if e.get("uuid")}
    edges = []
    for e in recs:
        pu = e.get("parentUuid", "ABSENT")
        if pu not in (None, "ABSENT") and pu in by_uuid:
            edges.append((by_uuid[pu]["_id"], e["_id"]))

    # tool_use_id → tool name, for tool_result label enrichment and the
    # user-response split (an interactive tool's result is human-authored)
    tu_name: dict[str, str] = {}
    for e in recs:
        if e.get("type") == "assistant":
            for c in ((e.get("message") or {}).get("content") or []):
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("id"):
                    tu_name[c["id"]] = c.get("name") or "?"
    INTERACTIVE = {"AskUserQuestion", "ExitPlanMode", "EnterPlanMode"}
    classified = []
    for e in recs:
        cls, label = classify(e)
        if cls == "tool_result":
            ref = next((c.get("tool_use_id")
                        for c in ((e.get("message") or {}).get("content") or [])
                        if isinstance(c, dict) and c.get("type") == "tool_result"),
                       None)
            name = tu_name.get(ref or "")
            if name:
                label = f"tool_result:{name}"
                if name in INTERACTIVE:
                    cls = "user-response"
        classified.append((e, cls, label))

    counts: dict[str, int] = {}
    for _, cls, _ in classified:
        counts[cls] = counts.get(cls, 0) + 1
    stars = [s for s in stars if s["t"] is not None]
    if stars:
        counts["context-prep"] = len(stars)
    present = [c for c in CLASS_ORDER if c in counts]
    lane_idx = {c: i for i, c in enumerate(present)}
    lanes = [(c, counts[c]) for c in present]

    nodes = []
    for e, cls, label in classified:
        props = [("file", f"{_short_file(e['_file'])}:{e['_line']}")]
        if e["_borrowed"]:
            props.append(("ts", "(none — midpoint of neighbors)"))
        else:
            # tick-format ts (05-13 14:23:11) — every dot carries its time in
            # the same easy-read shape as the y-axis labels
            ts = e["timestamp"]
            props.append(("ts", f"{ts[5:10]} {ts[11:19]}"))
        props.append(("label", label))
        if e.get("uuid"):
            props.append(("uuid", e["uuid"]))
        pu = e.get("parentUuid", "ABSENT")
        if pu is None:
            props.append(("parent", "(root)"))
        elif pu != "ABSENT":
            props.append(("parent", pu))
        if e.get("isSidechain"):
            props.append(("sidechain", "true"))
        for k in ("durationMs", "permissionMode", "mode", "operation",
                  "agentName", "prUrl"):
            if e.get(k) is not None:
                props.append((k, str(e[k])))
        # machine-side break signals: api_error system records and errored tool
        # results — timestamped contiguity breaks with no user action
        err = None
        if e.get("type") == "system" and e.get("subtype") == "api_error":
            err = (e.get("error") or {}).get("formatted") or "api_error"
        elif e.get("type") == "user":
            tur_v = e.get("toolUseResult")
            if isinstance(tur_v, str) and tur_v.startswith("Error"):
                err = tur_v[:120]
            elif isinstance(tur_v, dict) and (tur_v.get("isError") or tur_v.get("is_error")):
                err = "tool error"
        if err:
            props.append(("error", err))
        if e.get("_consumed"):
            props.append(("interjection", "queued here, consumed by the running turn (answered inline, no delivered message)"))
        if e.get("_consumed_remove"):
            props.append(("interjection", "consumed HERE — the running turn answered this queued prompt at this point"))
        # machine-stop discriminator: a turn_duration is the machine halting —
        # turn end, an AskUserQuestion wait, a notification park. Queue operations
        # are deliberately NOT in the signature set: an enqueue is an attribution
        # border (the next prompt typed mid-run), never an activity break.
        closure = None
        if e.get("type") == "system" and e.get("subtype") == "turn_duration":
            closure = "turn"
        nodes.append({
            "id": e["_id"], "line": e["_line"], "file": e["_file"],
            "uuid": e.get("uuid") or "",
            "t": e["_t"], "borrowed": e["_borrowed"],
            "hms": (e.get("timestamp") or "")[11:19],
            "tlabel": (f"{e['timestamp'][5:10]} {e['timestamp'][11:19]}"
                       if e.get("timestamp") else ""),
            "sidechain": bool(e.get("isSidechain")) or "/subagents/" in e["_file"],
            "err": bool(err), "closure": closure,
            "lane": lane_idx[cls], "cls": cls,
            # a queued USER PROMPT (enqueue with typed content) — its identity is a
            # prompt, so the tree view renders it (hollow) in the prompt column, but
            # its role-class stays queue-operation so it never reads as a START
            "qprompt": label == "enqueue:prompt",
            # an interjection the running turn CONSUMED: the ENQUEUE (hollow triangle) and
            # the REMOVE = consumption point (cremove → solid triangle, carries the text)
            "consumed": bool(e.get("_consumed")),
            "cremove": bool(e.get("_consumed_remove")),
            "props": props, "content": e.get("_qtext") or content_text(e),
        })
    for s in stars:
        props = [("file", f"{_short_file(s['file'])}:{s['line']}–{s['line_to']}"),
                 ("ts", "(write moment — anchored to non-replay neighbors)"),
                 ("label", "context-prep burst (collapsed)"),
                 ("records", str(s["n"])),
                 ("kinds", ", ".join(f"{k}×{v}" for k, v in s["kinds"].items()))]
        if s["o_span"]:
            props.append(("replayed span", f"{s['o_span'][0]} → {s['o_span'][1]}"))
        nodes.append({
            "id": f"{s['file']}:{s['line']}", "line": s["line"], "uuid": "",
            "t": s["t"], "borrowed": False, "star": True,
            "sidechain": "/subagents/" in s["file"],
            "lane": lane_idx["context-prep"], "cls": "context-prep",
            "props": props, "content": "",
        })
    return nodes, edges, lanes


def _fmt_dt(dt: float) -> str:
    if dt < 60:
        return f"{dt:.0f}s"
    if dt < 3600:
        return f"{dt/60:.0f}m"
    return f"{dt/3600:.1f}h"


def _fmt_hm(dt: float) -> str:
    """Long form for hover text: 1h 32m / 4m 12s / 8s / 0.4s."""
    if dt < 10:
        return f"{dt:.1f}s"
    if dt < 60:
        return f"{dt:.0f}s"
    if dt < 3600:
        return f"{int(dt // 60)}m {int(dt % 60):02d}s"
    return f"{int(dt // 3600)}h {int(dt % 3600 // 60):02d}m"


# engaged-time gap adjustments (the "sliver" smoothing), per-segment. Both thresholds are
# CEILINGS (max-gap), tunable via the live knobs in the Stats tab:
GAP_ACTIVE_CEILING = 300.0      # active-gap ceiling: fill an inter-block gap SHORTER than this (+time)
GAP_IDLE_CEILING = 600.0   # idle-gap ceiling: truncate an in-block gap LONGER than this
                            # (−time); also the elapsed-bar RED threshold


def _heat(dt: float, idle_ceiling: float = GAP_IDLE_CEILING) -> str:
    """The elapsed-bar color for a gap of `dt` seconds: <1s dark · <1m blue · <idle_ceiling
    amber · ≥idle_ceiling red. The amber→red boundary IS the idle-gap ceiling, so tuning
    it moves the red coloring with it. Computed here, not client-side (the client
    used to infer it from bar WIDTH, which crossed red at ~60s)."""
    if dt < 1:
        return "#3a4150"
    if dt < 60:
        return "#4a6e8a"
    if dt < idle_ceiling:
        return "#b08030"
    return "#a04040"


def ymap_compact(nodes: list) -> tuple:
    """Ordinal y: uniform pitch, ONE ROW PER WALL-CLOCK SECOND. Records sharing a second
    are simultaneous for our purposes and share a row — their sub-second ms is unreliable
    (the harness writes a burst with ms often INVERTED vs write/parent order, e.g. a child
    timestamped before its parent), so ms must not drive vertical position or it scrambles
    the relationship arcs. Within a row, sub-column packing orders by line (write order),
    so parent→child links in a burst stay flat. Elapsed time between rows is the left-gutter
    bar (seconds; sub-second gaps vanish into the shared row). Coverage is unaffected — it's
    computed from real ts in `_raw_points`, not from this display y-map.
    Returns (Y fn, gutter, idle_bands(empty), ticks, height)."""
    PITCH = 14
    secs = sorted({int(n["t"]) for n in nodes})   # floor to the second
    y = 100.0
    pts: dict[int, float] = {}
    gutter = []        # (y, dt seconds) — bar at the row the gap leads INTO
    idle_bands: list = []   # none in compact mode
    ticks = []         # (y, label) — first row at/after each hour boundary
    last_hr = None
    prev = None
    for s in secs:
        hr = s // 3600
        if hr != last_hr:
            ticks.append((y, datetime.fromtimestamp(hr * 3600, timezone.utc)
                          .strftime("%m-%d %H:%M")))
            last_hr = hr
        pts[s] = y
        if prev is not None:
            gutter.append((y, s - prev))
        y += PITCH
        prev = s
    height = y + 80

    def Y(t):
        s = int(t)
        if s in pts:
            return pts[s]
        i = bisect.bisect_right(secs, s) - 1
        return pts[secs[max(0, i)]]
    return Y, gutter, idle_bands, ticks, height


def ymap(nodes: list) -> tuple:
    """Idle-compressed y(t). Returns (Y fn, segments, idle bands, total height)."""
    times = sorted({n["t"] for n in nodes})
    segs = []          # (t0, t1, y0, y1, idle?)
    y = 100.0          # clears the sticky header + column-name strip
    idle_bands = []
    for i, t in enumerate(times):
        if i == 0:
            segs.append((t, t, y, y, False))
            continue
        prev = times[i - 1]
        dt = t - prev
        if dt > IDLE_MIN:
            n_ticks = max(0, math.floor(t / 3600) - math.ceil(prev / 3600) + 1)
            h = max(IDLE_H, n_ticks * PER_HOUR)
            idle_bands.append((y, h, dt))
            segs.append((prev, t, y, y + h, True))
            y += h
        else:
            step = min(max(dt * PX_PER_S, MIN_STEP), MAX_STEP)
            segs.append((prev, t, y, y + step, False))
            y += step
    height = y + 80

    def Y(t):
        for t0, t1, y0, y1, _ in segs:
            if t0 <= t <= t1:
                return y0 + (y1 - y0) * ((t - t0) / (t1 - t0) if t1 > t0 else 0)
        return 100.0 if t < times[0] else height - 80
    return Y, segs, idle_bands, height


def pack_columns(nodes, lanes, gutter):
    """Greedy sub-column packing + per-column x/width — the geometry shared by the
    static render and the server's JSON. Mutates each node's `sub` and `x`. A node
    claims the lowest sub-column free at its y; the sub-column is reused once the
    previous node clears it (compact's 14px pitch needs clearance under one pitch —
    12px node + 1px — or consecutive same-column rows zig-zag). Column width =
    baseline (one dot + padding) + one SUB_W per *extra* simultaneous dot, floored to
    fit the longest header word on one line. Returns (col_x, col_w, width)."""
    PAD = 1 if gutter is not None else 4
    col_tracks: dict[int, list[float]] = {}
    for n in sorted(nodes, key=lambda n: (n["lane"], n["y"], n["line"])):
        tracks = col_tracks.setdefault(n["lane"], [])
        for ri, end in enumerate(tracks):
            if n["y"] > end + PAD:
                tracks[ri] = n["y"] + NODE_R * 2
                n["sub"] = ri
                break
        else:
            tracks.append(n["y"] + NODE_R * 2)
            n["sub"] = len(tracks) - 1

    col_x, x = [], float(LEFT)
    for i, (cls, _count) in enumerate(lanes):
        col_x.append(x)
        max_dots = max(1, len(col_tracks.get(i, [])))
        node_w = COL_INNER + NODE_R * 2 + (max_dots - 1) * SUB_W + COL_GAP
        longest = max((len(w) for w in cls.replace("_", " ").replace("-", " ").split()),
                      default=1)
        hdr_w = math.ceil(longest * HDR_CHAR_W) + 12 + 2
        x += max(node_w, hdr_w)
    width = x + 60
    col_w = [col_x[i + 1] - col_x[i] if i + 1 < len(col_x) else width - 60 - col_x[i]
             for i in range(len(col_x))]
    for n in nodes:
        n["x"] = col_x[n["lane"]] + COL_INNER + n["sub"] * SUB_W
    return col_x, col_w, width


def session_geometry(nodes, edges, lanes, Y, idle_bands, height, gutter=None) -> dict:
    """One session's render geometry as a JSON-serializable dict — the server's API
    payload. Same layout the static `render` draws, emitted as data: positioned
    nodes (with tooltip), arc line coords, stop/start dividers, hour ticks,
    compact gutter bars, and idle bands. The client is a dumb renderer + virtualizer
    over this; the Python time/layout model stays the single source of truth."""
    node_at = {n["id"]: n for n in nodes}
    for n in nodes:
        n["y"] = Y(n["t"])
    col_x, col_w, width = pack_columns(nodes, lanes, gutter)

    cols = [{"cls": cls, "name": cls.replace("_", " ").replace("-", " "), "count": cnt,
             "x": round(col_x[i] + 6, 1), "w": round(col_w[i] - 12, 1),
             "desc": CLASS_DESC.get(cls, "")}
            for i, (cls, cnt) in enumerate(lanes)]

    divs = []
    for n in nodes:
        if n["cls"] == "prompt":
            ty = "prompt"
        elif n["cls"] == "user-interrupt":
            ty = "interrupt"
        elif n.get("closure") == "turn" and not n.get("sidechain"):
            ty = "turn"
        elif n["cls"] == "user-response" and not n.get("sidechain"):
            ty = "answer"
        else:
            continue
        # "MM-DD HH:MM:SS" -> "MM-DD · HH:MM" (dot separates date/time; drop seconds)
        tl = n.get("tlabel", "")
        lbl = (tl[:5] + " · " + tl[6:11]) if tl else ""
        divs.append({"y": round(n["y"] + NODE_R, 1), "type": ty, "label": lbl})

    ticks = []
    if gutter is None and nodes:
        tmin = min(n["t"] for n in nodes)
        tmax = max(n["t"] for n in nodes)
        t = (int(tmin) // 3600) * 3600
        while t <= tmax:
            if t >= tmin:
                ticks.append({"y": round(Y(t), 1),
                              "label": datetime.fromtimestamp(t, timezone.utc)
                              .strftime("%m-%d %H:%M")})
            t += 3600

    gut = []
    if gutter:
        for yy, dt in gutter:
            if dt <= 0:
                continue
            gut.append({"y": round(yy, 1), "w": round(min(96, 4 + math.log2(1 + dt) * 6.2), 1),
                        "label": _fmt_dt(dt) if dt >= 60 else "", "hover": _fmt_hm(dt)})

    bands = [{"y": round(y, 1), "h": h, "dt": dt} for y, h, dt in idle_bands]

    elines = []
    for p, c in edges:
        if p not in node_at or c not in node_at:
            continue
        a, b = node_at[p], node_at[c]
        x1, y1 = a["x"] + NODE_R, a["y"] + NODE_R
        x2, y2 = b["x"] + NODE_R, b["y"] + NODE_R
        elines.append({"x1": round(x1, 1), "y1": round(y1, 1),
                       "x2": round(x2, 1), "y2": round(y2, 1), "up": y2 < y1,
                       "mx": round((x1 + x2) / 2 + (24 if x1 == x2 else 0), 1)})

    nd = []
    for n in nodes:
        item = {"x": round(n["x"], 1), "y": round(n["y"], 1), "cls": n["cls"],
                "color": COLORS.get(n["cls"], "#999"), "star": bool(n.get("star")),
                "borrowed": n["borrowed"], "err": bool(n.get("err")),
                "uuid": n["uuid"] or n["id"], "ln": n["line"]}
        # Tips ship inline with the geometry — loaded once when the session expands,
        # not fetched per hover. `tip` is the metadata header (file/ts/label/uuid/…);
        # `body` is the record's terminal-facing content (prompt / agent text / tool
        # i-o), which the client renders in a monospace subbox so aligned output
        # (progress trees, tables, ASCII) stays aligned without monospacing the
        # whole tooltip.
        item["tip"] = "\n".join(f"{k}: {v}" for k, v in n["props"])
        if n["content"]:
            item["body"] = n["content"]
        nd.append(item)

    return {"width": round(width, 1), "height": round(height, 1), "compact": gutter is not None,
            "left": LEFT, "node_r": NODE_R, "cols": cols, "nodes": nd, "edges": elines,
            "dividers": divs, "ticks": ticks, "gutter": gut, "bands": bands}


def _role_of(cls: str, closure, sidechain) -> tuple:
    """(pairing base, display kind) for one record's class. `base` drives the
    time-block pairing (start / end / break / activity); `display` drives the line
    color (start blue / end red / break yellow)."""
    if cls == "prompt":
        return ("start", "start")
    if cls == "user-interrupt":
        return ("end", "end")
    if closure == "turn" and not sidechain:
        return ("end", "end")
    if cls == "user-response" and not sidechain:
        return ("break", "break")            # AskUserQuestion/plan answer (a pair)
    if cls in ("thinking", "tool_use", "text") and not sidechain:
        return ("activity", "start")         # candidate resume-start (sweep decides) —
        # the FIRST agent re-engagement after a stop: thinking, a tool call, OR an
        # assistant message — whichever is earliest. `text` matters because a combined
        # thinking+text record classes as `text` (not `thinking`), so without it a
        # think-and-reply resume is missed. Inert mid-block (sweep fires only when closed).
    return (None, None)


def _role_items(seq: list, get) -> list:
    """Normalize a time-ordered seq into role items (t, base, payload, display). A
    break expands to a START (this dot) + an END (the preceding dot). `get(e)` ->
    (t, cls, closure, sidechain, payload)."""
    info = [get(e) for e in seq]
    items = []
    for i, (t, cls, closure, sc, pay) in enumerate(info):
        base, disp = _role_of(cls, closure, sc)
        if base == "break":
            items.append((t, "start", pay, "break"))
            if i > 0:
                items.append((info[i - 1][0], "end", info[i - 1][4], "break"))
        elif base:
            items.append((t, base, pay, disp))
    items.sort(key=lambda x: x[0])
    return items


def _sweep_points(items: list):
    """Primary start/end points + a SECOND-pass rule: where agent activity
    (thinking, a tool call, or an assistant message) resumes after an END with no
    interceding START — the FIRST re-engagement, whichever comes first — the agent CONTINUED
    the same exchange without a fresh prompt (auto-continue, a backgrounded task
    firing). Rather than a fresh start (which would split the exchange), it is a
    BREAK that overrides the stop: the resuming dot gets a yellow break line (a
    start for pairing), and the preceding stop dot gets an ADDITIONAL yellow line
    (keeping its red end). Returns (pts, lines): pts = (t, role, payload) for
    pairing; lines = (payload, display, y_offset) — a dot may appear more than once."""
    pts, lines = [], []
    state, last_end = "closed", None
    for t, base, pay, disp in items:
        if base == "start":
            pts.append((t, "start", pay)); lines.append((pay, disp, 0)); state = "open"
        elif base == "end":
            pts.append((t, "end", pay)); lines.append((pay, disp, 0))
            state, last_end = "closed", pay
        elif base == "activity" and state == "closed":
            pts.append((t, "start", pay)); lines.append((pay, "break", 0))
            if last_end is not None:
                lines.append((last_end, "break", 2))   # extra line, nudged below the red
            state = "open"
    return pts, lines


def _close_trailing(pts: list, last_t: float, last_pay):
    """A segment that ends on an OPEN start — a prompt whose turn never got a stop line
    because a system restart / interruption halted record-keeping — is real work, not a
    stranded point. Close it with a synthetic END at the segment's last record, so it
    time-boxes; any over-ceiling idle the box now spans is handled by idle-gap
    truncation. No-op when the stream closes normally (last unmatched isn't a start)."""
    open_t = None
    for t, role, *_ in pts:
        open_t = t if role == "start" else None if role == "end" else open_t
    if open_t is not None and last_t > open_t:
        return pts + [(last_t, "end", last_pay)]
    return pts


def _pair_points(pts: list):
    """pts: [(t, role, payload, …)] sorted by t. Pair each START with the next END
    that has no START between → a time-block; count stranded. Returns (blocks,
    stranded) where block = (start_payload, end_payload, dur_seconds)."""
    blocks, stranded, openp = [], 0, None
    for t, role, pay, *_ in pts:
        if role == "start":
            if openp is not None:
                stranded += 1                       # prior start never closed
            openp = (t, pay)
        elif openp is not None:
            blocks.append((openp[1], pay, round(t - openp[0], 1)))
            openp = None
        else:
            stranded += 1                           # end with no open start
    if openp is not None:
        stranded += 1
    return blocks, stranded


def _raw_points(recs: list) -> list:
    """Swept role points straight from RAW records (no layout) — mirrors
    `segment_geometry`'s rules so per-segment coverage agrees with the segment's."""
    seq = [e for e in recs if e.get("timestamp") and not e.get("_ctx")]
    seq.sort(key=lambda e: (_ep(e["timestamp"]), e["_line"]))
    tu: dict = {}
    for e in seq:
        if e.get("type") == "assistant":
            for c in ((e.get("message") or {}).get("content") or []):
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("id"):
                    tu[c["id"]] = c.get("name") or ""
    INTERACTIVE = {"AskUserQuestion", "ExitPlanMode", "EnterPlanMode"}
    cls_of: dict = {}
    for e in seq:
        cls = classify(e)[0]
        if cls == "tool_result":
            ref = next((c.get("tool_use_id")
                        for c in ((e.get("message") or {}).get("content") or [])
                        if isinstance(c, dict) and c.get("type") == "tool_result"), None)
            if tu.get(ref or "") in INTERACTIVE:
                cls = "user-response"
        cls_of[id(e)] = cls

    def get(e):
        closure = "turn" if (e.get("type") == "system"
                             and e.get("subtype") == "turn_duration") else None
        sc = bool(e.get("isSidechain")) or "/subagents/" in e["_file"]
        return (_ep(e["timestamp"]), cls_of[id(e)], closure, sc, e)  # payload = the record
    pts, _lines = _sweep_points(_role_items(seq, get))
    # close a trailing interrupted prompt at the last real ACTIVITY record (not a trailing
    # queue-op notification, and — matching segment_geometry — not a dropped queue dot)
    real = [e for e in seq if cls_of[id(e)] != "queue-operation"]
    if real:
        pts = _close_trailing(pts, _ep(real[-1]["timestamp"]), real[-1])
    return pts


def segment_coverage(recs: list) -> float:
    """Sum of the segment's time-block durations — the row duration column."""
    blocks, _ = _pair_points(_raw_points(recs))
    return round(sum(b[2] for b in blocks), 1)


def gap_spans(recs: list) -> dict:
    """The ceiling-independent gap structure a segment's active/idle adjustments
    are computed from — the same role-sweep as `segment_coverage`, so they reconcile.
    Two kinds, each `(dur_s, a_line, b_line)` (the bounding records, for rendering):
      • `between` — end-of-block_i → start-of-block_{i+1} (a bridge candidate; ACTIVE if
        short). Never overlaps a block.
      • `inblock` — consecutive records INSIDE one block (a truncation candidate; IDLE
        if long). Overlaps the block.
    Leading/trailing idle (outside any block) is neither — it was never active."""
    seq = [e for e in recs if e.get("timestamp") and not e.get("_ctx")]
    seq.sort(key=lambda e: (_ep(e["timestamp"]), e["_line"]))
    if len(seq) < 2:
        return {"between": [], "inblock": []}
    blocks, _ = _pair_points(_raw_points(recs))          # (start_rec, end_rec, dur)
    intervals = [(_ep(s["timestamp"]), _ep(e["timestamp"])) for s, e, _ in blocks]
    between = []
    for i in range(len(blocks) - 1):
        er, sr = blocks[i][1], blocks[i + 1][0]
        g = _ep(sr["timestamp"]) - _ep(er["timestamp"])
        if g > 0:
            between.append((round(g, 1), er["_line"], sr["_line"]))
    inblock = []
    for i in range(len(seq) - 1):
        ta, tb = _ep(seq[i]["timestamp"]), _ep(seq[i + 1]["timestamp"])
        g = tb - ta
        if g > 0 and any(bs <= ta and tb <= be for bs, be in intervals):
            inblock.append((round(g, 1), seq[i]["_line"], seq[i + 1]["_line"]))
    return {"between": between, "inblock": inblock}


def gap_adjust(spans: dict, active_ceiling: float = GAP_ACTIVE_CEILING,
               idle_ceiling: float = GAP_IDLE_CEILING) -> dict:
    """Apply the two ceilings to a `gap_spans` result → the active/idle totals.
    ACTIVE: inter-block gaps shorter than `active_ceiling`, filled whole (+time). IDLE:
    in-block gaps longer than `idle_ceiling`, truncated to it (−(gap−idle_ceiling))."""
    active = [d for d, _a, _b in spans["between"] if d < active_ceiling]
    idle = [d - idle_ceiling for d, _a, _b in spans["inblock"] if d > idle_ceiling]
    return {"gap_active_s": round(sum(active), 1), "gap_active_n": len(active),
            "gap_idle_s": round(sum(idle), 1), "gap_idle_n": len(idle)}


def materialize_exchanges(recs: list, with_bodies: bool = False,
                          active_ceiling: float = GAP_ACTIVE_CEILING,
                          idle_ceiling: float = GAP_IDLE_CEILING) -> list:
    """Partition a record set into prompt-anchored EXCHANGES — the annotation unit.
    An exchange runs from one typed-prompt START to the next; it spans >=1 turn (turn_durations
    joined by breaks) and folds in any consumed interjections (their server-marked `_qtext`).
    Anchored by the opening typed prompt's canonical UUID — stable across rebuilds, ceiling
    changes, and turn boundaries (unlike the legacy positional `(session, exchange#)` key).
    `classify` already keeps the anchor set clean: only typed prompts (incl. typed slash
    commands) are STARTs; meta / compact-summary / notifications / interrupts are excluded, and
    a consumed interjection has no delivered record so it never anchors — it folds in instead.

    Returns exchanges in time order, each: `{anchor_uuid, anchor_line, prompt, ts, coverage_s,
    gap_active_s, gap_idle_s, adjusted_s, n_blocks, n_records, text:[{role,text},...]}`. A leading
    run with no typed prompt (work continuing across a segment boundary) is one `anchor_uuid=None`
    "(continuation)" exchange so every block belongs somewhere.

    Two time measures: **`coverage_s`** is the raw sum of block durations (Σ coverage_s ==
    segment_coverage(recs)); **`adjusted_s`** is the gap-adjusted engaged time `coverage_s +
    gap_active_s − gap_idle_s` (`gap_active_s` = inter-block gaps shorter than `GAP_ACTIVE_CEILING`,
    filled; `gap_idle_s` = in-block gaps longer than `GAP_IDLE_CEILING`, truncated) — the measure a
    report bills on, and what the UI shows. Σ adjusted_s over a segment == its `segment_geometry`
    adjusted_s.

    **`text`** is the exchange's narration as one ts-ordered array of `{role, text}` — the opening
    prompt and folded interjections (role "user") interleaved with the assistant's visible
    responses (role "agent"). The agent turns appear only with `with_bodies=True` (they widen the
    payload); the user turns are always present. This is the conversational flow an authoring pass
    reads — the role signal the prompt alone can't carry (e.g. a bare "continue")."""
    seq = [e for e in recs if e.get("timestamp") and not e.get("_ctx")]
    seq.sort(key=lambda e: (_ep(e["timestamp"]), e["_line"]))
    if not seq:
        return []
    anchors = [e for e in seq if classify(e)[0] == "prompt"]
    ex = []
    if not anchors or _ep(seq[0]["timestamp"]) < _ep(anchors[0]["timestamp"]):
        ex.append({"anchor_uuid": None, "anchor_line": None, "prompt": "(continuation)",
                   "ts": seq[0]["timestamp"], "_lo": _ep(seq[0]["timestamp"])})
    for a in anchors:
        ex.append({"anchor_uuid": a.get("uuid") or None, "anchor_line": a["_line"],
                   "prompt": content_text(a)[:200], "ts": a["timestamp"],
                   "_lo": _ep(a["timestamp"])})
    for x in ex:
        x.update(coverage_s=0.0, n_blocks=0, n_records=0, text=[],
                 gap_active_s=0.0, gap_idle_s=0.0)
    los = [x["_lo"] for x in ex]

    def owner(t):                                   # exchange whose span [start, next) holds t
        return ex[max(0, bisect.bisect_right(los, t) - 1)]

    for s_rec, _e_rec, dur in _pair_points(_raw_points(recs))[0]:
        o = owner(_ep(s_rec["timestamp"]))
        o["coverage_s"] += dur
        o["n_blocks"] += 1
    # The exchange's narrating text, consolidated in ONE ts-ordered array — the opening prompt
    # and any folded-in interjections (role "user") interleaved with the assistant's visible
    # responses (role "agent", added only with_bodies, since they widen the payload). Order is
    # how it happened, not grouped by source — the conversational flow an authoring pass reads.
    for e in seq:
        o = owner(_ep(e["timestamp"]))
        o["n_records"] += 1
        cls = classify(e)[0]
        if cls == "prompt" or e.get("_consumed"):    # typed prompt OR a folded interjection
            o["text"].append({"role": "user", "text": content_text(e)})
        elif with_bodies and cls == "text":          # assistant visible response text
            t = (content_text(e) or "").strip()
            if t:
                o["text"].append({"role": "agent", "text": t})

    # Per-exchange gap adjustment, named for the ceilings that drive it: attribute each active
    # fill (GAP_ACTIVE_CEILING) / idle truncation (GAP_IDLE_CEILING) to the exchange owning its
    # start, so adjusted_s == coverage + gap_active − gap_idle reconciles per-exchange with
    # segment_geometry's adjusted measure (what the UI shows). Raw coverage_s OVER-COUNTS a long
    # background-spanning turn's in-block idle; adjusted_s is the engaged-time measure a report
    # bills on. Σ adjusted_s over a segment == its segment_geometry adjusted_s.
    ts_of = {e["_line"]: _ep(e["timestamp"]) for e in seq}
    spans = gap_spans(recs)
    for d, a, _b in spans["between"]:                # inter-block gap < ceiling → active fill
        if d < active_ceiling and a in ts_of:
            owner(ts_of[a])["gap_active_s"] += d
    for d, a, _b in spans["inblock"]:                # in-block gap > ceiling → idle truncation
        if d > idle_ceiling and a in ts_of:
            owner(ts_of[a])["gap_idle_s"] += d - idle_ceiling

    for x in ex:
        x["coverage_s"] = round(x["coverage_s"], 1)
        x["gap_active_s"] = round(x["gap_active_s"], 1)
        x["gap_idle_s"] = round(x["gap_idle_s"], 1)
        x["adjusted_s"] = round(x["coverage_s"] + x["gap_active_s"] - x["gap_idle_s"], 1)
        del x["_lo"]
    return ex


def _utext(e: dict) -> str:
    ct = (e.get("message") or {}).get("content")
    if isinstance(ct, str):
        return ct
    if isinstance(ct, list):
        return " ".join(b.get("text", "") for b in ct
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def mark_synthetic(by: dict) -> None:
    """Mark `queue-operation enqueue` records that are NOT genuine operator prompts — an
    agent self-authored `/loop` / scheduled-wakeup continuation, whose DELIVERED counterpart
    is an `isMeta` user record (the reliable harness-authored tell; genuine typed prompts
    never set it). Flag `_synthetic` so `classify` treats it as a notification, not a prompt.
    `by` = {file: [records]}; mutates the records in place. Shared by the server and CLI."""
    norm = lambda s: " ".join((s or "").split())
    meta = {norm(c) for rs in by.values() for e in rs
            if e.get("type") == "user" and e.get("isMeta")
            for c in [(e.get("message") or {}).get("content")] if isinstance(c, str)}
    for rs in by.values():
        for e in rs:
            if (e.get("type") == "queue-operation" and e.get("operation") == "enqueue"
                    and norm(e.get("content")) in meta):
                e["_synthetic"] = True


def mark_interjections(by: dict) -> None:
    """Mark queued prompts the running turn CONSUMED — enqueued mid-turn, `remove`d (not
    `dequeue`d), never delivered as a user message (the live turn answered them inline; ~80%
    of such removes, agent-text-validated). Per file, FIFO-pair queue ops; an enqueue a
    `remove` pops whose genuine-prompt content is delivered NOWHERE is consumed (the
    content-not-delivered test self-corrects FIFO mis-pairing). Sets `_consumed` on the
    enqueue and `_consumed_remove` + `_qtext` on the remove. Run `mark_synthetic` first.
    `by` = {file: [records]}; mutates in place. Shared by the server and CLI."""
    norm = lambda s: " ".join((s or "").split())
    genuine = lambda c: bool((c or "").lstrip()) and not (c or "").lstrip().startswith(("<task-notification", "<<"))
    for rs in by.values():
        delivered = {norm(_utext(e)) for e in rs
                     if e.get("type") == "user" and not e.get("isMeta") and genuine(_utext(e))}
        pending: list = []
        for e in sorted((q for q in rs if q.get("type") == "queue-operation"),
                        key=lambda q: q["_line"]):
            op = e.get("operation")
            if op == "enqueue":
                pending.append(e)
            elif op == "dequeue":
                if pending:
                    pending.pop(0)
            elif op == "remove":
                if pending:
                    q = pending.pop(0)
                    c = q.get("content") or ""
                    if genuine(c) and not q.get("_synthetic") and norm(c) not in delivered:
                        q["_consumed"] = True
                        e["_consumed_remove"] = True
                        e["_qtext"] = c
            elif op == "popAll":
                pending = []


def segment_geometry(recs: list, extra_edges: list | None = None,
                  active_ceiling: float = GAP_ACTIVE_CEILING,
                  idle_ceiling: float = GAP_IDLE_CEILING) -> dict:
    """Class-relative ORDINAL geometry for one segment — for the unified
    shared-column tree view. `active_ceiling`/`idle_ceiling` drive the active/idle gap
    fills and the gutter red threshold (see `gap_spans`/`gap_adjust`). Unlike `session_geometry`
    it assigns NO absolute x:
    each node carries its `cls` and its `sub`-column index, and `classes` reports
    the per-class sub-column count. The CLIENT lays out column x globally from
    whichever segments are currently expanded (dynamic widths, no whole-corpus
    outliers). Always ordinal pitch — the only mode in the tree view. Arc edges
    reference node lines (both endpoints live in the same segment); the client
    resolves their coords once columns are placed.

    `extra_edges` = [(from_line, to_line, kind)] — non-parentUuid relationships the
    caller reconstructed (e.g. queue spawn/consume/deliver links). Emitted into the
    edge list with their `kind` (the client styles them); only edges whose BOTH
    endpoints are nodes in this segment draw."""
    nodes, edges, lanes = build(recs)
    if not nodes:
        return {"empty": True}
    # drop the non-prompt queue ops (dissolved into bridge edges) BEFORE the y-map, so
    # they never occupy a row or contribute a gutter gap — otherwise their (often
    # ts-inverted) timestamps left dot-less "empty gap lines". Prompt-column queue dots
    # stay: qprompt enqueues (hollow) and consumed-remove points (cremove → solid triangle).
    nodes = [n for n in nodes
             if not (n["cls"] == "queue-operation" and not (n.get("qprompt") or n.get("cremove")))]
    if not nodes:
        return {"empty": True}
    Y, gutter, _idle, _ticks, height = ymap_compact(nodes)
    for n in nodes:
        n["y"] = Y(n["t"])
    # queued user prompts move to the PROMPT lane for display (hollow circles), so
    # they correlate with the user-prompt column instead of hiding in the queue
    # column; their `cls` stays queue-operation, so the role/time path below ignores
    # them. Add a prompt lane if the segment has none of its own.
    if any(n.get("qprompt") or n.get("cremove") for n in nodes):
        p_lane = next((i for i, (c, _c) in enumerate(lanes) if c == "prompt"), None)
        if p_lane is None:
            lanes = lanes + [("prompt", 0)]
            p_lane = len(lanes) - 1
        for n in nodes:
            if n.get("qprompt") or n.get("cremove"):
                n["lane"] = p_lane
    # greedy sub-column packing per lane (class) — same rule as `pack_columns`, but
    # keep only the sub index + per-lane count; absolute x is the client's job
    col_tracks: dict[int, list[float]] = {}
    for n in sorted(nodes, key=lambda n: (n["lane"], n["y"], n["line"])):
        tracks = col_tracks.setdefault(n["lane"], [])
        for ri, end in enumerate(tracks):
            if n["y"] > end + 1:
                tracks[ri] = n["y"] + NODE_R * 2
                n["sub"] = ri
                break
        else:
            tracks.append(n["y"] + NODE_R * 2)
            n["sub"] = len(tracks) - 1
    lane_cls = {i: cls for i, (cls, _c) in enumerate(lanes)}
    # only lanes that actually carry a node become columns (the now-empty queue lane
    # disappears once its dots are dropped)
    classes = {lane_cls[i]: len(col_tracks[i]) for i in col_tracks}

    nd = []
    for n in nodes:
        dcls = lane_cls[n["lane"]]               # display class (== cls except qprompt)
        item = {"cls": dcls, "sub": n.get("sub", 0),
                "y": round(n["y"], 1), "ln": n["line"], "uuid": n["uuid"] or n["id"],
                "color": COLORS.get(dcls, "#999"), "star": bool(n.get("star")),
                "borrowed": n["borrowed"], "err": bool(n.get("err")),
                "hollow": bool(n.get("qprompt")), "consumed": bool(n.get("consumed")),
                "cremove": bool(n.get("cremove"))}
        item["tip"] = "\n".join(f"{k}: {v}" for k, v in n["props"])
        if n["content"]:
            item["body"] = n["content"]
        nd.append(item)

    # ── line semantics + first-pass time accounting (shared with segment_coverage)
    # line colors: blue START · red END · yellow BREAK (a pair). Pairing: START →
    # next END with no START between = a time-block; activity (thinking) resuming
    # after an END with no START opens a new START (see _sweep_points). Stranded
    # points are ignored but counted.
    seq = sorted(nodes, key=lambda n: (n["t"], n["line"]))
    pts, lineitems = _sweep_points(_role_items(
        seq, lambda n: (n["t"], n["cls"], n.get("closure"), n.get("sidechain"), n)))
    # close a trailing interrupted prompt at the last real activity record — same record
    # `_raw_points` uses (non-borrowed, non-queue-op), so segment coverage stays == function
    real = [n for n in seq if not n["borrowed"] and n["cls"] != "queue-operation"]
    if real:
        pts = _close_trailing(pts, real[-1]["t"], real[-1])
    lines = []
    for n, disp, off in lineitems:
        d = {"y": round(n["y"] + NODE_R + off, 1), "kind": disp}
        if disp == "start" and n.get("tlabel"):
            tl = n["tlabel"]
            d["label"] = tl[:5] + " · " + tl[6:11]
        lines.append(d)

    paired, stranded = _pair_points(pts)                    # payload = node
    blocks = [{"y0": round(sn["y"] + NODE_R, 1), "y1": round(en["y"] + NODE_R, 1),
               "dur": dur, "s": sn["line"]} for sn, en, dur in paired]
    # tag each dot with its containing block's start line (None if uncovered) — the
    # per-box collapse hides a box's own dots; `inbox` is just "in some box"
    spans = [(sn["y"], en["y"], sn["line"]) for sn, en, _ in paired]
    for item in nd:
        item["box"] = next((sl for sy, ey, sl in spans if sy <= item["y"] <= ey), None)
        item["inbox"] = item["box"] is not None
    coverage = round(sum(b["dur"] for b in blocks), 1)
    span = round(seq[-1]["t"] - seq[0]["t"], 1) if len(seq) > 1 else 0.0

    # active / idle gap fills (the engaged-time smoothing). Map the gap-bounding
    # records (by line) back to node y's; active = short inter-block bridges (green),
    # idle = the over-ceiling part of long in-block gaps (red, overlapping the box).
    yl = {n["line"]: n["y"] for n in nodes}
    sp = gap_spans(recs)
    active_fills, idle_fills = [], []
    gap_active_s = gap_idle_s = 0.0
    for d, a, b in sp["between"]:
        if d < active_ceiling and a in yl and b in yl:
            y0, y1 = sorted((yl[a], yl[b]))
            active_fills.append({"y0": round(y0 + NODE_R, 1), "y1": round(y1 + NODE_R, 1), "dur": d})
            gap_active_s += d
    for d, a, b in sp["inblock"]:
        if d > idle_ceiling and a in yl and b in yl:
            y0, y1 = sorted((yl[a], yl[b]))
            cr = round(d - idle_ceiling, 1)
            idle_fills.append({"y0": round(y0 + NODE_R, 1), "y1": round(y1 + NODE_R, 1),
                                   "dur": d, "idle": cr})
            gap_idle_s += cr
    gap_active_s, gap_idle_s = round(gap_active_s, 1), round(gap_idle_s, 1)
    acct = {"coverage_s": coverage, "span_s": span,
            "gap_s": round(max(0.0, span - coverage), 1),
            "n_blocks": len(blocks), "stranded": stranded,
            "gap_active_s": gap_active_s, "gap_idle_s": gap_idle_s,
            "adjusted_s": round(coverage + gap_active_s - gap_idle_s, 1)}

    gut = []
    for yy, dt in gutter:
        if dt <= 0:
            continue
        gut.append({"y": round(yy, 1), "w": round(min(96, 4 + math.log2(1 + dt) * 6.2), 1),
                    "color": _heat(dt, idle_ceiling),
                    "label": _fmt_dt(dt) if dt >= 60 else "", "hover": _fmt_hm(dt)})

    node_at = {n["id"]: n for n in nodes}
    elines = []
    for p, c in edges:
        if p in node_at and c in node_at:
            elines.append({"a": node_at[p]["line"], "b": node_at[c]["line"],
                           "up": node_at[c]["y"] < node_at[p]["y"]})
    if extra_edges:
        by_line = {n["line"]: n for n in nodes}
        for fr, to, kind in extra_edges:
            a, b = by_line.get(fr), by_line.get(to)
            if a and b:
                elines.append({"a": fr, "b": to, "up": b["y"] < a["y"], "kind": kind})

    return {"height": round(height, 1), "classes": classes, "nodes": nd,
            "lines": lines, "blocks": blocks, "acct": acct,
            "active": active_fills, "idle": idle_fills,
            "gutter": gut, "edges": elines}


#  display-name overrides for the column header (the bucket keys stay unchanged)
HEADER_NAME = {"prompt": "user prompt", "queue-operation": "queue",
               "thinking": "agent thinking", "text": "agent message",
               "user-response": "user answer"}


def class_meta() -> list:
    """Ordered class metadata (name + hover description) for the single global
    column header in the tree view — every class in render order, the client shows
    only those present in expanded segments."""
    return [{"cls": c, "name": HEADER_NAME.get(c, c.replace("_", " ").replace("-", " ")),
             "color": COLORS.get(c, "#999"), "desc": CLASS_DESC.get(c, "")}
            for c in CLASS_ORDER]


def render(nodes, edges, lanes, Y, idle_bands, height, src, n_lines,
           gutter=None) -> str:
    node_at = {n["id"]: n for n in nodes}
    for n in nodes:
        n["y"] = Y(n["t"])
    col_x, col_w, width = pack_columns(nodes, lanes, gutter)
    key_lines = [
        '<div>● timestamped record — fill color = its class column</div>',
        '<div>◆ no timestamp — placed at the midpoint of its neighbors</div>',
        '<div style="color:#e8c84a">★ context-prep burst — replay copies collapsed; zero work</div>',
        '<div>⭘ red ring — error (api_error / errored tool result)</div>',
        '<div>arcs — parentUuid links; red arc = child ts precedes parent (write-order noise)</div>',
        '<div style="color:#00d2ff">━ prompt divider — typed start</div>',
        '<div style="color:#ff5555">╌ turn_duration divider — machine stop '
        '(turn end, AskUserQuestion wait, notification park)</div>',
        '<div style="color:#4d9fff">╌ user-answer divider — operator responded; restart</div>',
        '<div style="color:#d05a5a">╌ interrupt divider — operator broke execution</div>',
        '<div style="color:#9f7f4f">● queue-operation dots (beside prompt) — enqueue = prompt '
        'typed mid-run (the interjection detector; the dequeued prompt\'s ts is only delivery), '
        'dequeue = delivery, popAll/remove = queue edits; never dividers (no activity break)</div>',
        '<div>not drawn (the raw DB retains them): sub-agent transcripts — superseded by their '
        'main-chain Agent tool dots (the returning tool_result records the run\'s '
        'duration/status/tokens)</div>',
        '<div>hover a column header for its description · right-click a dot → copy uuid</div>',
    ]
    if gutter is not None:
        key_lines.append(
            '<div><b>compact mode</b>: row pitch is ordinal (sequence, not duration); '
            'elapsed time since the previous record is the gutter bar — log length, '
            'heat color (<span style="color:#4a6e8a">&lt;1m</span> '
            '<span style="color:#b08030">&lt;5m</span> '
            '<span style="color:#a04040">≥5m</span>), labeled from 60s</div>')
    key_html = "".join(key_lines)

    parts = [f"""<!doctype html><html><head><meta charset=utf-8>
<title>Swimlane timeline — {html.escape(src)}</title><style>
 body{{margin:0;font:12px/1.3 -apple-system,Segoe UI,Roboto,sans-serif;background:#0f1115;color:#ddd}}
 #hdr{{position:sticky;top:0;background:#161a22;border-bottom:1px solid #333;padding:6px 12px;z-index:10;min-width:100%;box-sizing:border-box}}
 #cols{{position:sticky;top:30px;height:54px;background:#12151c;border-bottom:1px solid #2a2f3a;z-index:9;width:{width:.0f}px}}
 #keybtn{{position:fixed;top:4px;right:12px;z-index:30;background:#1d2433;border:1px solid #3a4a5f;border-radius:4px;padding:3px 12px;cursor:help;font-weight:600;color:#9ab}}
 #keybtn .keybody{{display:none;position:absolute;right:0;top:24px;width:460px;background:#161a22;border:1px solid #3a4a5f;border-radius:4px;padding:10px 14px;font-weight:400;color:#ddd;line-height:1.7;font-size:11px}}
 #keybtn:hover .keybody{{display:block}}
 .chdr{{position:absolute;top:4px;cursor:help}}
 .cname{{font-size:10px;color:#9ab;font-weight:600;line-height:1.15;overflow-wrap:break-word}}
 .ccount{{position:absolute;top:38px;left:0;right:0;font-size:10px;color:#688}}
 #wrap{{position:relative}}
 .tick{{position:absolute;left:{LEFT - 8}px;right:0;border-top:1px dashed #2a2f3a}}
 .ticklbl{{position:absolute;left:0;width:{LEFT - 14}px;text-align:right;color:#688;font-size:10px}}
 .exline{{position:absolute;left:{LEFT - 8}px;right:0;border-top:1px dashed #00d2ff;opacity:.30;z-index:1}}
 .brkline{{position:absolute;left:{LEFT - 8}px;right:0;border-top:1px dashed #d05a5a;opacity:.45;z-index:1}}
 .tdline{{position:absolute;left:{LEFT - 8}px;right:0;border-top:1px dashed #ff5555;opacity:.30;z-index:1}}
 .ansline{{position:absolute;left:{LEFT - 8}px;right:0;border-top:1px dashed #4d9fff;opacity:.40;z-index:1}}
 .exlbl{{position:absolute;left:0;width:{LEFT - 14}px;text-align:right;color:#0aa8cc;font-size:9px}}
 .brklbl{{position:absolute;left:0;width:{LEFT - 14}px;text-align:right;color:#c46a6a;font-size:9px}}
 .idle{{position:absolute;left:{LEFT - 8}px;right:0;background:repeating-linear-gradient(135deg,#1a1d24,#1a1d24 5px,#15171d 5px,#15171d 10px);color:#667;font-size:9px;text-align:center}}
 .nd{{position:absolute;width:{NODE_R*2}px;height:{NODE_R*2}px;border-radius:50%;z-index:5}}
 .nd.borrowed{{border-radius:1px;transform:rotate(45deg)}}
 .nd.err{{box-shadow:0 0 0 2px #0f1115,0 0 0 3.5px #e05050}}
 .nd.star{{background:none;width:16px;height:16px;font-size:15px;line-height:16px;text-align:center;border-radius:0}}
 .sw{{display:inline-block;width:10px;height:10px;border-radius:5px;vertical-align:-1px;margin:0 3px 0 10px}}
 svg{{position:absolute;top:0;left:0;z-index:2;pointer-events:none}}
</style></head><body>
<div id=hdr><b>Swimlane timeline</b> · {html.escape(src)} · first {n_lines} lines</div>
<div id=keybtn>Key<div class=keybody>{key_html}</div></div>
<div id=cols>"""]
    for i, (cls, count) in enumerate(lanes):
        desc = html.escape(CLASS_DESC.get(cls, ""), quote=True)
        name = cls.replace("_", " ").replace("-", " ")
        parts.append(
            f'<div class=chdr style="left:{col_x[i] + 6:.0f}px;width:{col_w[i] - 12:.0f}px" '
            f'title="{desc}"><div class=cname>{name}</div>'
            f'<div class=ccount>({count})</div></div>')
    parts.append(f'</div><div id=wrap style="width:{width:.0f}px;height:{height:.0f}px">')

    # hour ticks: proportional mode only — under compact's scale compression the
    # hour grid carries no value; the labeled exchange/interrupt dividers are the
    # time landmarks there.
    if gutter is None and nodes:
        tmin = min(n["t"] for n in nodes)
        tmax = max(n["t"] for n in nodes)
        t = (int(tmin) // 3600) * 3600
        while t <= tmax:
            if t >= tmin:
                yy = Y(t)
                lbl = datetime.fromtimestamp(t, timezone.utc).strftime("%m-%d %H:%M")
                parts.append(f'<div class=tick style="top:{yy:.1f}px"></div>'
                             f'<div class=ticklbl style="top:{yy-5:.1f}px">{lbl}</div>')
            t += 3600
    # stop/start dividers (main chain): every typed prompt (cyan — a start), every
    # turn_duration (red dashed — the machine STOPPED: turn end, an AskUserQuestion
    # wait, a notification park), every user answer (blue dashed — the operator
    # responded: a restart), every interrupt (red — broken). Queue operations draw
    # nothing: an enqueue is an attribution border, never an activity break. Compact
    # mode labels prompt/interrupt lines — with the hour grid gone there, these ARE
    # the y-axis time landmarks; proportional mode leaves them unlabeled.
    for n in nodes:
        if n["cls"] == "prompt":
            line_cls, lbl_cls = "exline", "exlbl"
        elif n["cls"] == "user-interrupt":
            line_cls, lbl_cls = "brkline", "brklbl"
        elif n.get("closure") == "turn" and not n.get("sidechain"):
            line_cls, lbl_cls = "tdline", None    # machine stop
        elif n["cls"] == "user-response" and not n.get("sidechain"):
            line_cls, lbl_cls = "ansline", None   # operator answered — restart
        else:
            continue
        parts.append(f'<div class={line_cls} style="top:{n["y"]+NODE_R:.1f}px"></div>')
        if lbl_cls and gutter is not None and n["tlabel"]:
            parts.append(f'<div class={lbl_cls} style="top:{n["y"]+NODE_R-11:.1f}px">'
                         f'{n["tlabel"]}</div>')
    # elapsed gutter (compact mode): one bar per row, log length, heat color,
    # labeled from 60s up — the time-interval encoding that replaced spacing
    if gutter:
        for yy, dt in gutter:
            if dt <= 0:
                continue
            w = min(96, 4 + math.log2(1 + dt) * 6.2)
            col = _heat(dt)
            lbl = (f'<div style="position:absolute;left:2px;top:{yy-9:.1f}px;'
                   f'font-size:9px;color:#778">{_fmt_dt(dt)}</div>') if dt >= 60 else ""
            # 12px transparent hit-box around the 4px bar so the title hover is
            # easy to land; z-index above the (pointer-inert) arc layer
            parts.append(f'<div style="position:absolute;left:2px;top:{yy-2:.1f}px;'
                         f'width:{w:.0f}px;height:12px;z-index:3" title="+{_fmt_hm(dt)}">'
                         f'<div style="margin-top:4px;height:4px;background:{col};'
                         f'border-radius:2px"></div></div>{lbl}')
    for y, h, dt in idle_bands:
        parts.append(f'<div class=idle style="top:{y:.0f}px;height:{h}px;'
                     f'line-height:{h}px">⋯ {dt/60:.0f}m ⋯</div>')

    svg = [f'<svg width="{width:.0f}" height="{height:.0f}">']
    for p, c in edges:
        if p not in node_at or c not in node_at:
            continue
        a, b = node_at[p], node_at[c]
        x1, y1 = a["x"] + NODE_R, a["y"] + NODE_R
        x2, y2 = b["x"] + NODE_R, b["y"] + NODE_R
        up = y2 < y1                      # child rendered above parent = ts inversion
        col = "#c05050" if up else "#3a4a5f"
        mx = (x1 + x2) / 2 + (24 if x1 == x2 else 0)
        svg.append(f'<path d="M{x1:.0f},{y1:.0f} Q{mx:.0f},{(y1+y2)/2:.0f} {x2:.0f},{y2:.0f}" '
                   f'fill="none" stroke="{col}" stroke-width="1" opacity=".7"/>')
    svg.append("</svg>")
    parts.append("".join(svg))

    for n in nodes:
        col = COLORS.get(n["cls"], "#999")
        cls_attr = ("nd" + (" borrowed" if n["borrowed"] else "")
                    + (" err" if n.get("err") else ""))
        tip = "\n".join(f"{k}: {v}" for k, v in n["props"])
        if n["content"]:
            tip += "\n\n" + n["content"]
        tip = html.escape(tip, quote=True)
        uid = html.escape(n["uuid"] or n["id"], quote=True)
        if n.get("star"):
            parts.append(f'<div class="nd star" title="{tip}" data-u="{uid}" '
                         f'style="left:{n["x"]:.0f}px;top:{n["y"]:.0f}px;color:{col}">★</div>')
            continue
        parts.append(f'<div class="{cls_attr}" title="{tip}" data-u="{uid}" '
                     f'style="left:{n["x"]:.0f}px;top:{n["y"]:.0f}px;background:{col}"></div>')
    parts.append("""<div id=toast style="position:fixed;bottom:16px;left:16px;background:#2a3a2a;
color:#cfc;padding:6px 12px;border-radius:4px;display:none;z-index:20;font-size:11px"></div>
<script>
document.getElementById('wrap').addEventListener('contextmenu', function(ev){
  var nd = ev.target.closest('.nd');
  if (!nd) return;
  ev.preventDefault();
  var u = nd.dataset.u || '';
  function done(ok){
    var t = document.getElementById('toast');
    t.textContent = ok ? ('copied ' + u) : 'copy failed';
    t.style.display = 'block';
    clearTimeout(t._h); t._h = setTimeout(function(){ t.style.display='none'; }, 1600);
  }
  function fallback(){
    var ta = document.createElement('textarea');
    ta.value = u; document.body.appendChild(ta); ta.select();
    var ok = false; try { ok = document.execCommand('copy'); } catch(e){}
    document.body.removeChild(ta); done(ok);
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(u).then(function(){done(true);}, function(){fallback();});
  } else { fallback(); }
});
</script></div></body></html>""")
    return "".join(parts)


def companion_md(recs: list[dict], lanes: list, out_html: str) -> str:
    """The entity-key markdown: every class, its description, and its JSONL
    properties split shown / hidden."""
    keys_by_class: dict[str, set] = {}
    for e in recs:
        cls, _ = classify(e)
        keys = {k for k in e.keys() if not k.startswith("_")}
        keys_by_class.setdefault(cls, set()).update(keys)
    L = [f"# Swimlane timeline — entity key",
         "",
         f"Companion to `{pathlib.Path(out_html).name}`. One row per entity class "
         f"(= diagram column). **Shown** properties are projected somewhere in the "
         f"diagram (position, color, shape, arcs, or hover text); **hidden** ones "
         f"exist on the records but are not projected.",
         "",
         "| entity | description | shown properties | hidden properties |",
         "|---|---|---|---|"]
    for cls, _count in lanes:
        if cls == "context-prep":
            L.append(f"| {cls} | {CLASS_DESC.get(cls, '')} | "
                     f"*(synthetic marker — hover lists the collapsed run's "
                     f"record kinds, count, and replayed-ts span)* | |")
            continue
        keys = keys_by_class.get(cls, set())
        shown = sorted(k for k in keys if k in SHOWN_PROPS)
        hidden = sorted(k for k in keys if k not in SHOWN_PROPS)
        L.append(f"| {cls} | {CLASS_DESC.get(cls, '')} | "
                 f"{', '.join(f'`{k}`' for k in shown)} | "
                 f"{', '.join(f'`{k}`' for k in hidden)} |")
    L += ["",
          "Untimestamped UI-state types (`ai-title`, `last-prompt`, `custom-title`, "
          "`permission-mode`, `mode`, `file-history-snapshot`, `agent-name`, "
          "`bridge-session`, `worktree-state`, `agent-setting`) are excluded by "
          "default — UNIQUE'd 2026-06-10: pure session state, no timing or chain "
          "linkage, no timeline influence. Re-include with `--ui-state`.",
          "",
          "Bucket alignment with the primary DB's `event_buckets`: prompt → "
          "user-prompt · user-response → user-response (plan approvals via "
          "ExitPlanMode included; permission-dialog approvals leave NO record — "
          "the wait sits inside the tool gap) · thinking/text/tool_use → agent · "
          "tool_result → tool · attachment/system/queue-operation/pr-link → meta · "
          "ringed nodes → sub-agent · context-prep → eliminated at ingest. "
          "**Known semantic gap**: harness-authored user records (the user-meta "
          "label, pooled in the system column) and user-interrupt records are "
          "`user_msg` to the primary DB, so its exchange numbering counts them as "
          "exchange starts; the viz separates them (cyan divider = typed prompt, "
          "red divider = interrupt). An interrupt's pre-gap — the broken, "
          "unrecorded machine work — lands in the excluded user-prompt lane: "
          "conservative under-counting, by accident but honest.",
          ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=_paths.db("raw.db"),
                    help="scratch DB built by raw_db.py")
    ap.add_argument("--lines", type=int, default=0,
                    help="keep only each file's first N lines (0 = all)")
    ap.add_argument("--ui-state", action="store_true",
                    help="include the untimestamped UI-state types (ai-title, "
                         "last-prompt, permission-mode, ...). Excluded by default: "
                         "UNIQUE'd 2026-06-10 — pure state, no timeline influence")
    ap.add_argument("--compact", action="store_true",
                    help="ordinal row pitch; elapsed time becomes a log-length "
                         "heat bar in the gutter instead of vertical spacing")
    ap.add_argument("--out", default=_paths.diagram("swimlane-timeline.html"))
    a = ap.parse_args()
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    recs = load(a.db, a.lines)
    if not a.ui_state:
        recs = [e for e in recs if e.get("timestamp")]
    # time-spent lens (ruled 2026-06-11): sub-agent transcripts don't draw — proven
    # 103/103 files are superseded by their main-chain tool dots (the returning
    # tool_result carries recorded totalDurationMs; zero runtime outliers). The raw
    # DB retains them for analysis.
    recs = [e for e in recs if "/subagents/" not in e["_file"]]
    nodes, edges, lanes = build(recs)
    if a.compact:
        Y, gutter, idle_bands, _ticks, height = ymap_compact(nodes)
    else:
        Y, _, idle_bands, height = ymap(nodes)
        gutter = None
    out = render(nodes, edges, lanes, Y, idle_bands, height, a.db,
                 a.lines or len(recs), gutter=gutter)
    open(a.out, "w").write(out)
    md_path = str(pathlib.Path(a.out).with_suffix(".md"))
    open(md_path, "w").write(companion_md(recs, lanes, a.out))
    print(f"wrote {a.out}: {len(nodes)} nodes, {len(edges)} edges, "
          f"{len(lanes)} columns, {height:.0f}px tall")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()

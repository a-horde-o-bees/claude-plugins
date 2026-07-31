#!/usr/bin/env python3
"""Session FACETS over raw transcripts — the one live thread split into a flat
sequence of eras, for the flat-rail tree view.

Built on the canonical uuid forest (first-occurrence records, `is_replay=0`,
`parentUuid` chains). A session is NOT walked as a deep tree of every alternative
history — that proved too deep for what the tool diagnoses (time-blocking active
work). Instead the one live thread is partitioned into **segments**, each its own
flat row on one ts-ordered rail (`swimlane_server` renders them; `_node` builds
them). Three segment kinds:

- **resume / compaction** — a re-emission boundary. On resume/compaction the
  harness re-writes earlier history as a context-prep burst (`is_replay` /
  `is_compact_summary`) and a canonical record continues after it, often
  re-attaching far back. That continuing record begins a segment (`segment_start`,
  computed in `build_forest`); its burst lines lead the segment (→ the ★ at its
  head). Cross-file resumes (the resume file's first record parents off the parent
  file) are resume segments too. **Compaction vs resume is mechanical, not heuristic:**
  an `isCompactSummary` record (`_cs`) is emitted ONLY by a real compaction (after a
  `system/compact_boundary`) — a plain resume re-emits prior events as `_replay`
  copies with no new summary. So a segment is `compaction` iff it re-roots at a
  compact_boundary (null-parent) or its lead burst carries a `_cs` line; otherwise
  `resume`. (Earlier this keyed only on null-parent re-roots, so a compaction whose
  continuation re-attached with a parent mislabeled as resume.)
- **rewind** — a same-file fork into >=2 response-bearing prompt paths. The
  EARLIEST path is the original continuation that ran to an endpoint *before* the
  rewind, so it STAYS INLINE on the parent (we don't split every version, only the
  rewinds). The later prompt paths are the rewinds; each becomes its own flat
  segment. No-response ("superseded") and non-prompt children stay inline; nothing is
  dropped (`no_response` counts the superseded prompts a segment carries).

There are no nested branches — `out["branches"]` is always empty; `out["segments"]`
carries every split, flat. Each segment records what it re-attached from (`from`) so
the cross-segment arc dropped at render is recoverable in its start detail. A typed
slash command (`<command-name>/x</command-name>`) counts as a prompt (`classify`);
`_prompt_text` shows it as `/x`. Per-segment render geometry is produced separately
by `swimlane_timeline.segment_geometry` over each segment's record subset.
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swimlane_timeline as S
import _paths  # noqa: E402

_CMD = re.compile(r"<command-name>([^<]+)</command-name>")
_ARGS = re.compile(r"<command-args>([^<]*)</command-args>")


def _prompt_text(e: dict) -> str:
    """Display text for a prompt row — a typed slash command shows as `/x args`,
    not its raw `<command-name>` XML."""
    c = S.content_text(e)
    m = _CMD.match(c.lstrip())
    if m:
        a = _ARGS.search(c)
        return (m.group(1) + (" " + a.group(1).strip() if a and a.group(1).strip() else "")).strip()
    return c[:200]


def is_typed_prompt(e: dict) -> bool:
    """A genuine typed prompt — the branch-divergence signal. Excludes meta/
    slash-command stubs, interrupts, tool results (all handled by `classify`)
    AND compact summaries (a `user`/`isCompactSummary` record reads as a prompt
    to `classify` but is harness-authored, never a branch)."""
    if e.get("type") != "user" or e.get("isMeta") or e.get("_cs"):
        return False
    return S.classify(e)[0] == "prompt"


def _label(e: dict) -> str:
    return S.classify(e)[1]


def build_forest(recs: list[dict]) -> dict:
    """Canonical uuid forest over main-chain, non-replay, timestamped records.
    Returns dict with `canon` (uuid->record), `children` (uuid->[uuid] in line
    order), `roots` (genuine session starts + stitched compaction boundaries
    flagged), `compaction` (set of boundary uuids), `by_file`."""
    canon: dict[str, dict] = {}
    for e in recs:
        if e.get("_replay") or e.get("isSidechain") or "/subagents/" in e["_file"]:
            continue
        u = e.get("uuid")
        if not u or u in canon:
            continue
        canon[u] = e

    children: dict[str, list[str]] = {}
    for u, e in canon.items():
        pu = e.get("parentUuid")
        if pu in canon:
            children.setdefault(pu, []).append(u)
    for u in children:
        children[u].sort(key=lambda c: canon[c]["_line"])

    # per-file canon nodes in line order — to find each file's genuine first node
    # (a session start) and, for any other root, the pre-compact tail to stitch to
    by_file: dict[str, list[str]] = {}
    for u, e in canon.items():
        by_file.setdefault(e["_file"], []).append(u)
    for f in by_file:
        by_file[f].sort(key=lambda u: canon[u]["_line"])
    pos = {u: i for f in by_file for i, u in enumerate(by_file[f])}

    compaction: set[str] = set()
    roots: list[str] = []
    for u, e in canon.items():
        pu = e.get("parentUuid")
        if pu in canon:
            continue                       # has a canonical parent — not a root
        f = e["_file"]
        if u == by_file[f][0]:
            roots.append(u)                # genuine session start (or resume's
            continue                       # first new node attaches cross-file,
                                           # so it never reaches here)
        # a non-first root in its file is a compaction re-root (null-parent
        # boundary that started a fresh chain). Stitch it to the immediately
        # preceding canonical node — the pre-compact tail — as a linear, marked
        # continuation. The tail had no continuation, so this stays single-child.
        prev = by_file[f][pos[u] - 1]
        children.setdefault(prev, []).append(u)
        children[prev].sort(key=lambda c: canon[c]["_line"])
        compaction.add(u)

    # FACET STARTS: a re-emission boundary (resume / compaction) re-writes earlier
    # history as a context-prep burst (is_replay / is_compact_summary) and then a
    # canonical record continues after it — often re-attaching far back (the long
    # cross-boundary arc). Such a canonical record begins a new FACET; the burst's
    # lines lead it (collapsing into the ★ at the segment head). Scan every record in
    # raw line order; the canonical record immediately following a burst is a start.
    allbyfile: dict[str, list[dict]] = {}
    for e in recs:
        if e.get("isSidechain") or "/subagents/" in e["_file"]:
            continue
        allbyfile.setdefault(e["_file"], []).append(e)
    segment_start: dict[str, list[int]] = {}      # uuid -> leading burst lines
    for f, rs in allbyfile.items():
        rs.sort(key=lambda e: e["_line"])
        burst: list[int] = []
        for e in rs:
            if e.get("_replay") or e.get("_cs"):
                burst.append(e["_line"])
                continue
            u = e.get("uuid")
            if u and u in canon and burst:
                segment_start[u] = burst[:]
            burst = []
    # a compaction re-root with no preceding burst is still a segment boundary
    for u in compaction:
        segment_start.setdefault(u, [])

    # COMPACTION SIGNAL: an isCompactSummary record (`_cs`) is emitted only by a real
    # context compaction (after a `system/compact_boundary`), never by a plain resume
    # (resume re-emits prior events as `_replay` copies, no new summary). So a segment
    # whose lead burst carries a `_cs` line is a compaction, even when its continuation
    # re-attaches with a parent (and thus isn't a null-parent re-root). Per-file `_cs`
    # lines let `_node` separate compaction from resume reliably.
    cs_lines: dict[str, set[int]] = {}
    for f, rs in allbyfile.items():
        cs_lines[f] = {e["_line"] for e in rs if e.get("_cs")}

    return {"canon": canon, "children": children, "roots": roots,
            "compaction": compaction, "by_file": by_file,
            "segment_start": segment_start, "cs_lines": cs_lines}


def _has_agent_response(c: str, F: dict) -> bool:
    """Does this node's subtree hold any agent record (an `assistant` — thinking /
    text / tool_use)? Short-circuits on the first one found."""
    canon, children = F["canon"], F["children"]
    stack = [c]
    while stack:
        n = stack.pop()
        if canon[n].get("type") == "assistant":
            return True
        stack.extend(children.get(n, []))
    return False


def _node(F: dict, start: str) -> dict:
    """Walk one segment: accumulate the subtree rooted at `start`, descending
    through linear, structural-fanout, and no-response-prompt nodes, but STOPPING
    at branch points (a node with >=2 prompt children that each drew a response, or
    a cross-file resume) — whose branch children begin nested branches. No-response
    (superseded) prompts stay inline on the spine; nothing is dropped."""
    canon, children = F["canon"], F["children"]
    segment_start = F["segment_start"]
    seg: list[str] = []
    segment_kids: list[str] = []          # children that split into their own flat segment
    rewind_kids: set[str] = set()       # of those, the ones that are rewinds
    stack = [start]
    while stack:
        n = stack.pop()
        seg.append(n)
        cs = children.get(n, [])
        nfile = canon[n]["_file"]
        # re-emission boundaries and cross-file resumes each leave the spine for their
        # own flat segment (never inline)
        for c in cs:
            if c != start and (c in segment_start or canon[c]["_file"] != nfile):
                if c not in segment_kids:
                    segment_kids.append(c)
        rest = [c for c in cs if c not in segment_start and canon[c]["_file"] == nfile]
        # a REWIND forks the same file into >=2 response-bearing prompt paths. The
        # EARLIEST is the original continuation — it ran to an endpoint *before* you
        # rewound, so it STAYS INLINE on the parent (we don't walk down every version,
        # only split off the rewinds). The later prompt paths are the rewinds; each is
        # its own flat segment. No-response/non-prompt children stay inline as before.
        resp = [c for c in rest if is_typed_prompt(canon[c]) and _has_agent_response(c, F)]
        if len(resp) >= 2:
            resp.sort(key=lambda c: (S._ep(canon[c]["timestamp"]) if canon[c].get("timestamp") else 0,
                                     canon[c]["_line"]))
            for rw in resp[1:]:
                rewind_kids.add(rw)
                if rw not in segment_kids:
                    segment_kids.append(rw)
            stack.extend(c for c in rest if c not in resp[1:])   # earliest + the rest inline
        else:
            stack.extend(rest)
    seg.sort(key=lambda u: (canon[u]["_file"], canon[u]["_line"]))
    # superseded prompts: typed prompts on the spine that drew no agent response
    no_response = sum(1 for u in seg
                      if is_typed_prompt(canon[u]) and not _has_agent_response(u, F))

    s_e = canon[start]
    # the first ACTUAL typed prompt in the segment (seg is line-sorted) — what the row
    # shows, since a segment/compaction often starts on a non-prompt (attachment/thinking)
    fp = next((canon[u] for u in seg if is_typed_prompt(canon[u])), None)
    out = {
        "start_uuid": start,
        "file": os.path.basename(s_e["_file"]).removesuffix(".jsonl"),
        "start_line": s_e["_line"],
        "label": _label(s_e),
        "is_prompt": is_typed_prompt(s_e),
        "prompt": (_prompt_text(s_e) if is_typed_prompt(s_e) else ""),
        "first_prompt": (_prompt_text(fp) if fp else ""),
        "ts": s_e.get("timestamp", ""),
        "n_records": len(seg),
        "n_prompts": sum(1 for u in seg if is_typed_prompt(canon[u])),
        "lines": [canon[u]["_line"] for u in seg],
        "compaction_lines": [canon[u]["_line"] for u in seg if u in F["compaction"]],
        "no_response": no_response,
        "branches": [],
        "segments": [],
    }
    # segments: re-emission continuations, rewinds, and cross-file resumes — all flat,
    # in chronological order. Each leads with its burst lines (→ the ★ at its head) and
    # records what it re-attached from, so the dropped cross-segment arc's truth lives in
    # the segment's start detail.
    for c in sorted(segment_kids, key=lambda c: canon[c]["_line"]):
        fac = _node(F, c)
        burst = segment_start.get(c, [])
        # a segment is a COMPACTION if it re-roots at a compact_boundary (null-parent) OR
        # its lead burst carries an isCompactSummary line; a REWIND is a same-file
        # re-prompt fork; everything else (cross-file /resume, replay-only re-emission)
        # is a RESUME. The three are mechanically distinguished — no heuristics.
        is_compaction = (c in F["compaction"]
                         or bool(set(burst) & F["cs_lines"].get(canon[c]["_file"], set())))
        fac["kind"] = ("rewind" if c in rewind_kids
                       else "compaction" if is_compaction else "resume")
        fac["lead_burst"] = burst
        fac["lines"] = burst + fac["lines"]          # segment leads with the ★
        pu = canon[c].get("parentUuid")
        if pu in canon:
            p = canon[pu]
            fac["from"] = {
                "line": p["_line"], "uuid": pu, "label": _label(p),
                "file": os.path.basename(p["_file"]).removesuffix(".jsonl"),
                "ts": p.get("timestamp", ""),
            }
        out["segments"].append(fac)
    return out


def _elevate(t: dict) -> list[dict]:
    """A segment with zero prompts carries no attributable time, so it is not a
    real node: collapse it and elevate its branches/segments in its place
    (recursively). A prompt-less leaf with no children vanishes entirely. Every
    surviving node thus has >=1 prompt; a multi-path fork that loses its prompt-less
    parent simply rises to that level. Segments (re-emission eras) elevate the same
    way — a 0-prompt era (pure replay/tool work) collapses into its successors."""
    t["branches"] = [e for b in t["branches"] for e in _elevate(b)]
    t["segments"] = [e for f in t["segments"] for e in _elevate(f)]
    if t["n_prompts"] == 0:
        return t["branches"] + t["segments"]
    return [t]


def session_trees(recs: list[dict]) -> list[dict]:
    """Top-level session trees: one entry per genuine root (after collapsing any
    prompt-less root and elevating its branches). Resume children appear nested
    under their shared ancestor, never as their own entry. Sorted by start ts."""
    F = build_forest(recs)
    trees = []
    for r in F["roots"]:
        t = _node(F, r)
        t["kind"] = "root"
        # elevate may promote branches/segments to the top; they keep their own kind
        # (rewind / resume / compaction) so the mark stays meaningful
        trees.extend(_elevate(t))
    trees.sort(key=lambda t: t["ts"])
    return trees


def _summarize(t: dict, depth: int = 0) -> tuple[int, int, int]:
    """(branch_count, max_depth, total_records) over a tree, for validation."""
    branches = len(t["branches"])
    mdep = depth
    tot = t["n_records"]
    for b in t["branches"]:
        cb, cd, ct = _summarize(b, depth + 1)
        branches += cb
        mdep = max(mdep, cd)
        tot += ct
    return branches, mdep, tot


def _print_tree(t: dict, depth: int = 0, max_depth: int = 99):
    if depth > max_depth:
        return
    pad = "  " * depth
    kind = t.get("kind", "?")
    mark = {"root": "●", "rewind": "↺", "resume": "⇲",
            "compaction": "▣"}.get(kind, "·")
    frm = (f"  ⟵from L{t['from']['line']}({t['from']['label']})"
           if t.get("from") else "")
    desc = (t["prompt"][:54].replace("\n", " ") if t["is_prompt"]
            else t["label"])
    print(f"{pad}{mark} [{kind}] {t['file'][:8]} L{t['start_line']} "
          f"({t['n_records']} recs){frm}  {desc!r}")
    for f in t.get("segments", []):       # segments are FLAT — same indent
        _print_tree(f, depth, max_depth)
    for b in t["branches"]:             # branches NEST — indent+1
        _print_tree(b, depth + 1, max_depth)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=_paths.db("raw.db"))
    ap.add_argument("--session", help="only print this session's tree (id prefix)")
    ap.add_argument("--max-depth", type=int, default=99)
    a = ap.parse_args()
    recs = S.load(a.db, 0)
    recs = [e for e in recs if e.get("timestamp")]
    trees = session_trees(recs)
    print(f"{len(trees)} top-level session trees\n")
    nontrivial = 0
    for t in trees:
        nb, md, tot = _summarize(t)
        if a.session and not t["file"].startswith(a.session):
            continue
        if nb == 0 and not a.session:
            continue                       # skip linear sessions in the overview
        nontrivial += 1
        print(f"=== {t['file'][:8]}: {nb} branches, depth {md}, {tot} records ===")
        _print_tree(t, max_depth=a.max_depth)
        print()
    if not a.session:
        print(f"({nontrivial} sessions have branches; "
              f"{len(trees) - nontrivial} are linear)")


if __name__ == "__main__":
    main()

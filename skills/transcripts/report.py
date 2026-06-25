#!/usr/bin/env python3
"""Engaged-time rollup from the timeline model — the "Engaged Time Report".

Rolls per-exchange coverage (the engaged-time measure: Σ START→END time-blocks) into per-day /
per-month totals, filtered to a topic set via the THREAD lineage. The unit of both narrative and
billing is the per-session focus-THREAD (`exchanges.py threads`): a coherent objective owning a
`summary` + its member exchange UUIDs, assigned exactly one topic (`exchanges.py thread-assign`).
Lineage: exchange -> thread -> topic -> billable. A consuming project supplies the topic set it
counts on; the model stores no topic policy.

    uv run ${CLAUDE_SKILL_DIR}/report.py [--topics a,b,c] [--from D --to D]
                                         [--db raw.db] [--anno annotations.db]
                                         [--out FILE] [--format md|csv]

TIME FOLLOWS THREADS. An exchange bills iff it is a member of a thread whose topic is in
`--topics`. Unthreaded exchanges (incidental turns — clears, acks, interrupted) and exchanges in
non-billable-topic threads drop out entirely — of both the time and the narrative. This matches
the block model: work that never coalesced into a billable objective was never billed.

TIME IS ATTRIBUTED BY DAY ONLY. A multi-day thread cannot honestly split its time across days by
narrative; the gap overlay is recomputed per day over the billable-only record set (filter-THEN-
adjust), so a bridge into an excluded neighbour reopens — an effect that only exists at the day
grain. So time appears ONLY in the by-day / by-month / total tables; the daily breakdown lists
each billable thread as work narrative (no per-row time).

Omit `--topics` to include every exchange (no filter) — a diagnostic "everything" view in which
even unthreaded exchanges count; the bill is always a filtered run.
"""
import argparse
import calendar as _calendar
import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swimlane_timeline as S  # noqa: E402
import exchanges as X  # noqa: E402  (reuse _marked / _units_for_session / _content_hash / _thread_key)
import _paths  # noqa: E402
import sqlite3  # noqa: E402


def hhmm_ceil(secs):
    """Minute-ceiling — authoritative totals (summed from raw seconds, never rounded rows)."""
    m = math.ceil(secs / 60)
    h, mm = divmod(m, 60)
    return f"{h}h {mm}m" if h else f"{mm}m"


def _date_ok(day, date_from, date_to):
    return (not date_from or day >= date_from) and (not date_to or day <= date_to)


def calendar_table(day_secs):
    """Per-day time as a calendar grid (Sun–Sat), one table per month. Each in-month cell is the
    day number over its day total (`<br>`-stacked); a day with no billable time shows the number
    alone; out-of-month cells are blank. Each month leads with an `### Month, Year` H3 heading
    (which `export-pdf` folds into the grid's spanned top row) and is followed by an italic
    `_Month total:_` line. `day_secs`: {YYYY-MM-DD: seconds}."""
    months = sorted({(int(d[:4]), int(d[5:7])) for d in day_secs})
    cal = _calendar.Calendar(firstweekday=6)        # 6 = Sunday — weeks start Sunday
    L = []
    for y, mo in months:
        L += [f"### {_calendar.month_name[mo]}, {y}", "",
              "| Sun | Mon | Tue | Wed | Thu | Fri | Sat |",
              "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"]
        for week in cal.monthdayscalendar(y, mo):
            cells = []
            for dnum in week:
                if dnum == 0:
                    cells.append("")
                    continue
                secs = day_secs.get(f"{y:04d}-{mo:02d}-{dnum:02d}", 0)
                # day number plain, duration emphasized; a no-time day shows "-" so every
                # in-month cell is two lines (uniform rows in raw-markdown viewers).
                cells.append(f"{dnum}<br>**{hhmm_ceil(secs)}**" if secs else f"{dnum}<br>-")
            L.append("| " + " | ".join(cells) + " |")
        msum = sum(s for d, s in day_secs.items() if d[:7] == f"{y:04d}-{mo:02d}")
        L += ["", f"_Month total: {hhmm_ceil(msum)}_", ""]
    return L


def load(db, anno_path, topics_filter, date_from, date_to):
    """Returns (day_adj, threads).

    THREAD LINEAGE: focus-threads are synthesized per ROOT (a connected work-tree, possibly
    spanning files via cross-file resume — `exchanges._root_components`). A thread is billable iff
    its assigned topic is in `topics_filter` (or the filter is None); its member exchanges are the
    billable record set. The billable-uuid set is GLOBAL (a thread can span a root's files), then
    the per-file time rollup consults it.

    FILTER-THEN-ADJUST: keep the records owned by a billable exchange, group by their own day per
    file, recompute the gap ceilings on each group — so an active bridge into an EXCLUDED neighbour
    is not counted (the exclusion reopens the gap). This is how time is accounted.

    - `day_adj` — authoritative adjusted seconds per day (Σ = the bill).
    - `threads` — billable threads for the daily breakdown: {summary, days:[day,...], first_ts},
      `days` the date-filtered member-exchange days, sorted; ordered for flat per-day rendering.
    """
    import bisect
    by = X._marked(db)
    anno = sqlite3.connect(anno_path)
    desc = dict(anno.execute("SELECT prompt_uuid, description FROM exchange"))
    thread_tags = collections.defaultdict(set)          # thread_key -> {topic, ...} (many-to-many)
    for k, t in anno.execute("SELECT thread_key, topic FROM thread_topic"):
        thread_tags[k].add(t)
    threads_by_hash = {h: json.loads(tj) for h, tj in
                       anno.execute("SELECT content_hash, threads_json FROM root_thread")}
    anno.close()

    # Materialize once; build global uuid -> day / ts maps.
    exs_by_file = {f: S.materialize_exchanges(by[f]) for f in by}
    uuid_day, uuid_ts = {}, {}
    for exs in exs_by_file.values():
        for x in exs:
            if x["anchor_uuid"]:
                uuid_day[x["anchor_uuid"]] = (x["ts"] or "")[:10]
                uuid_ts[x["anchor_uuid"]] = x["ts"] or ""

    # Per-root threads -> global billable-uuid set + billable-thread narrative.
    billable_uuid = set()
    threads_out = []
    for files in X._root_components(by).values():
        units = X._units_for_root(by, files, desc)
        for t in threads_by_hash.get(X._content_hash(units), []):
            uuids = t.get("uuids", [])
            tags = thread_tags.get(X._thread_key(uuids), set())
            if topics_filter is not None and not (tags & topics_filter):
                continue                                # ANY-match: billable if any tag is in filter
            billable_uuid.update(uuids)
            days = sorted({uuid_day[u] for u in uuids
                           if uuid_day.get(u) and _date_ok(uuid_day[u], date_from, date_to)})
            if not days:
                continue
            tslist = [uuid_ts[u] for u in uuids if uuid_ts.get(u)]
            threads_out.append({"summary": t.get("summary", ""), "days": days,
                                "first_ts": min(tslist, default=""),
                                "last_ts": max(tslist, default="")})

    def billable(u):
        return topics_filter is None or u in billable_uuid

    # Time: filter-then-adjust over the billable record set, per file.
    day_adj = collections.Counter()
    for f in by:
        exs = exs_by_file[f]
        if not exs:
            continue
        los = [S._ep(x["ts"]) for x in exs]
        kept = collections.defaultdict(list)
        for e in by[f]:
            if not e.get("timestamp") or e.get("_ctx"):
                continue
            idx = max(0, bisect.bisect_right(los, S._ep(e["timestamp"])) - 1)
            if billable(exs[idx]["anchor_uuid"]):
                kept[e["timestamp"][:10]].append(e)
        for day, drecs in kept.items():
            if not _date_ok(day, date_from, date_to):
                continue
            adj = S.gap_adjust(S.gap_spans(drecs))
            day_adj[day] += S.segment_coverage(drecs) + adj["gap_active_s"] - adj["gap_idle_s"]

    threads_out.sort(key=lambda t: (t["days"][0], t["first_ts"]))
    return day_adj, threads_out


def render_md(day_adj, threads, topics_filter):
    total = sum(day_adj.values())                   # authoritative: filter-then-adjust per day
    by_month = collections.Counter()
    for day, s in day_adj.items():
        by_month[day[:7]] += s

    days = sorted(set(day_adj) | {d for t in threads for d in t["days"]})
    span = f"{days[0]} to {days[-1]}" if days else "no data"
    tset = ", ".join(sorted(topics_filter)) if topics_filter else "all topics (unfiltered)"
    L = ["# Engaged Time Report — monaco-lock-company--erp-migration", "",
         f"_Topics: {tset} · {span} · machine-evidenced engaged time (idle/suspend/wait "
         f"excluded; operator review not separately billed; background machine runtime "
         f"excluded by design) · time follows threads: only exchanges in a billable-topic "
         f"focus-thread bill · filter-then-adjust: gap ceilings applied to the billable record "
         f"set · time attributed by day only; totals are minute-ceilings of raw seconds._", ""]

    L += ["## Timesheet", ""]
    L += calendar_table(day_adj)            # per-month: H3 title row + grid + italic month total
    if len(by_month) > 1:                   # multi-month: a grand total below the calendars
        L += [f"_Total: {hhmm_ceil(total)}_", ""]

    L += daily_breakdown(threads, day_adj)
    return "\n".join(L), total


def daily_breakdown(threads, day_secs):
    """Markdown for the daily breakdown — a FLAT chronological list of billable focus-thread
    bullets per day, one bullet per thread (its synthesized `summary`). No topic subgroups, no
    per-row time — the day total is the only time shown.

    A thread is listed ONCE, on its FIRST day (`days[0]`) — no cross-day narrative duplication. A
    thread that ran past midnight still bills both days (time splits per record in `load()`), but
    its narrative appears only on the day it began; a day whose billable time is wholly continuation
    work thus shows a total with no (or few) bullets, by design.

    `threads`: [{"summary":str, "days":[day,...] sorted, "first_ts":str}, ...] (billable only);
    `day_secs`: {day: seconds}."""
    by_day = collections.defaultdict(list)
    for t in threads:
        by_day[t["days"][0]].append(t)           # first day only — appears once
    days = sorted(set(day_secs) | set(by_day))
    L = ["## Daily breakdown", ""]
    for day in days:
        L += [f"### {day}", ""]
        # within a day, order by LAST activity (when each thread's work concluded) — a uniform
        # rule that reads in completion order and sinks a cross-midnight carryover to the bottom
        # of its first day (its last activity is the latest), without special-casing.
        for t in sorted(by_day.get(day, []), key=lambda t: t.get("last_ts") or t.get("first_ts") or ""):
            L.append(f"- {t['summary']}")
        L += ["", f"_Day total: {hhmm_ceil(day_secs.get(day, 0))}_", ""]
    return L


def render_csv(day_adj):
    out = ["date,time_s,time_hhmm"]
    for day in sorted(day_adj):
        out.append(f"{day},{day_adj[day]:.1f},{hhmm_ceil(day_adj[day])}")
    return "\n".join(out), sum(day_adj.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=_paths.db("raw.db"))
    ap.add_argument("--anno", default=_paths.db("annotations.db"))
    ap.add_argument("--topics", help="comma-separated billable topic set; omit = all (unfiltered)")
    ap.add_argument("--from", dest="date_from", default="", help="inclusive YYYY-MM-DD lower bound")
    ap.add_argument("--to", dest="date_to", default="", help="inclusive YYYY-MM-DD upper bound")
    ap.add_argument("--format", choices=["md", "csv"], default="md")
    ap.add_argument("--out", help="write to FILE (default: stdout)")
    a = ap.parse_args()

    tf = set(t.strip() for t in a.topics.split(",") if t.strip()) if a.topics else None
    day_adj, threads = load(a.db, a.anno, tf, a.date_from, a.date_to)
    if a.format == "csv":
        text, total = render_csv(day_adj)
    else:
        text, total = render_md(day_adj, threads, tf)
    if a.out:
        open(a.out, "w").write(text + "\n")
        print(f"wrote {a.out}  ({len(threads)} billable threads, total {hhmm_ceil(total)})")
    else:
        print(text)


if __name__ == "__main__":
    main()

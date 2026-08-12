"""Matching engine + cell rendering for export-diff (contract: SPEC.md).

Operates on the parsed-diff row model built by render_diff.py — no DOM
scraping. Token-stream matching: greedy string tiling (RKR-GST family)
for exact anchors that cross line boundaries, anchored gap refinement,
run grouping with noise demotion, bag-of-words rewrite pairing, then
residue boxing — and emits each changed line's cell HTML directly.
"""

import html
import re
from difflib import SequenceMatcher

MIN_TILE_TOKENS = 4
MIN_TILE_CHARS = 12
JACCARD = 0.4
RUN_MIN_CHARS = 30
RUN_GAP_CAP = 24

PIECE_RE = re.compile(r"\w+|\s+|[^\w\s]")


class Token:
    __slots__ = ("norm", "key", "raw", "line", "dest", "run", "box")

    def __init__(self, norm, raw, line):
        self.norm = norm
        self.key = norm.lower()  # matching is case-insensitive
        self.raw = raw  # original text incl. trailing whitespace
        self.line = line
        self.dest = None  # counterpart Token once anchored
        self.run = None  # hover-run id once grouped
        self.box = None  # residue-box id once assigned


class Line:
    def __init__(self, row, num, visual):
        self.row = row  # semantic row id — equal across sides iff paired
        self.visual = visual  # table-row index (rendering only)
        self.numi = num  # file line number (int) or None
        self.seg = None  # document-contiguity segment id
        self.tokens = []
        self.lead_ws = ""
        self.rewrite_partner = None
        self.box = None  # line-level box id (rewrite pairs only)

    def tokenize(self, raw):
        for piece in PIECE_RE.findall(raw):
            if piece.isspace():
                if self.tokens:
                    self.tokens[-1].raw += piece
                else:
                    self.lead_ws += piece
            else:
                self.tokens.append(Token(piece, piece, self))

    @property
    def matched(self):
        return [t for t in self.tokens if t.dest is not None]


def build_lines(rows):
    """Line models for the changed sides of a file's row list.

    rows: [(kind, lnum, ltext, rnum, rtext, lsem, rsem)] — a "chg" row
    carries the deletion in (lnum, ltext) and/or the insertion in
    (rnum, rtext). The sem ids are the semantic row axis: equal across
    sides iff the lines are similarity-paired counterparts; the visual
    table row (the tuple's index) is packing only.
    """
    dels, inss = [], []
    for row_i, row in enumerate(rows):
        kind, lnum, ltext, rnum, rtext = row[:5]
        if kind != "chg":
            continue
        if ltext is not None:
            line = Line(row[5], lnum, row_i)
            line.tokenize(ltext)
            dels.append(line)
        if rtext is not None:
            line = Line(row[6], rnum, row_i)
            line.tokenize(rtext)
            inss.append(line)
    # document-contiguity segments: consecutive file line numbers only —
    # a blank line, unchanged stretch, or hunk boundary starts a new segment
    seg = 0
    for bucket in (dels, inss):
        prev = None
        for line in bucket:
            if prev is None or line.numi is None or prev.numi is None \
                    or line.numi - prev.numi != 1:
                seg += 1
            line.seg = seg
            prev = line
    return dels, inss


def trim_tile(d_stream, i_stream, i, j, length):
    """Shrink a tile whose boundary-line portion is punctuation-only.

    A tile may cross a line boundary only if its tokens on the boundary
    line include an alphanumeric one — a lone spilled "." or "##" is
    trimmed back to the line that carries the tile's substance.
    """
    def spill(stream, s, ln, step):
        # tile tokens on the edge token's line, scanning inward from s
        line = stream[s].line
        c = 0
        while c < ln and stream[s + step * c].line is line:
            c += 1
        if c < ln and not any(re.search(r"\w", stream[s + step * k].norm)
                              for k in range(c)):
            return c
        return 0

    while length >= MIN_TILE_TOKENS:
        cut = max(spill(d_stream, i, length, 1), spill(i_stream, j, length, 1))
        if cut:
            i, j, length = i + cut, j + cut, length - cut
            continue
        cut = max(spill(d_stream, i + length - 1, length, -1),
                  spill(i_stream, j + length - 1, length, -1))
        if cut:
            length -= cut
            continue
        break
    return i, j, length


def tile(d_stream, i_stream):
    """Greedy string tiling: longest exact common token runs become anchors."""
    k = MIN_TILE_TOKENS

    def same_seg(stream, a, b):
        return stream[a].line.seg == stream[b].line.seg

    while True:
        index = {}
        for j in range(len(i_stream) - k + 1):
            window = i_stream[j:j + k]
            if any(t.dest for t in window) or not same_seg(i_stream, j, j + k - 1):
                continue
            index.setdefault(tuple(t.key for t in window), []).append(j)
        best = None  # (length, -row_distance, d_pos, i_pos)
        for i in range(len(d_stream) - k + 1):
            window = d_stream[i:i + k]
            if any(t.dest for t in window) or not same_seg(d_stream, i, i + k - 1):
                continue
            for j in index.get(tuple(t.key for t in window), ()):
                length = k
                while (i + length < len(d_stream) and j + length < len(i_stream)
                       and d_stream[i + length].dest is None
                       and i_stream[j + length].dest is None
                       and d_stream[i + length].key == i_stream[j + length].key
                       and same_seg(d_stream, i, i + length)
                       and same_seg(i_stream, j, j + length)):
                    length += 1
                # trim before ranking: every ranked candidate is consumable,
                # so each round consumes a tile and the loop must terminate
                ti, tj, tlen = trim_tile(d_stream, i_stream, i, j, length)
                if tlen < MIN_TILE_TOKENS or sum(
                        len(t.norm) for t in d_stream[ti:ti + tlen]) < MIN_TILE_CHARS:
                    continue
                dist = abs(d_stream[ti].line.row - i_stream[tj].line.row)
                cand = (tlen, -dist, ti, tj)
                if best is None or cand > best:
                    best = cand
        if best is None:
            return
        length, _, i, j = best
        for off in range(length):
            d_stream[i + off].dest = i_stream[j + off]
            i_stream[j + off].dest = d_stream[i + off]


def counterpart_gap(prev_tok, next_tok):
    """Unmatched counterpart tokens between two anchors' destinations."""
    if prev_tok is not None:
        pline = prev_tok.dest.line
        pi = pline.tokens.index(prev_tok.dest)
        if next_tok is not None and next_tok.dest.line is pline:
            ni = pline.tokens.index(next_tok.dest)
            rng = pline.tokens[pi + 1:ni]
        else:
            rng = pline.tokens[pi + 1:]
    elif next_tok is not None:
        nline = next_tok.dest.line
        rng = nline.tokens[:nline.tokens.index(next_tok.dest)]
    else:
        return []
    return [t for t in rng if t.dest is None]


def refine(dels, inss):
    """Diff anchor-bracketed gaps pairwise, matching tokens of any length."""
    for lines in (dels, inss):
        for line in lines:
            toks = line.tokens
            i = 0
            while i < len(toks):
                if toks[i].dest is not None:
                    i += 1
                    continue
                j = i
                while j < len(toks) and toks[j].dest is None:
                    j += 1
                gap = toks[i:j]
                prev_tok = toks[i - 1] if i > 0 else None
                next_tok = toks[j] if j < len(toks) else None
                rng = counterpart_gap(prev_tok, next_tok)
                if rng:
                    sm = SequenceMatcher(None, [t.key for t in gap],
                                         [t.key for t in rng], autojunk=False)
                    for op, a1, a2, b1, b2 in sm.get_opcodes():
                        if op == "equal":
                            for a, b in zip(gap[a1:a2], rng[b1:b2]):
                                a.dest = b
                                b.dest = a
                i = j


def compute_runs(d_stream, i_stream, run_ids):
    """Group matched tokens into contiguous cross-side runs for hover.

    A run extends while consecutive matched deletion tokens map to
    monotonically consecutive insertion tokens, with only unmatched tokens
    (the run's own edits, up to RUN_GAP_CAP a side) between them — line
    boundaries do not break a run. Runs whose every pair is same-row
    (in-place changes) get no id; only movement is hover-traceable.
    """
    ipos = {id(t): k for k, t in enumerate(i_stream)}
    runs, cur = [], []
    prev_d = prev_i = None
    for dk, tok in enumerate(d_stream):
        if tok.dest is None:
            continue
        ik = ipos.get(id(tok.dest))
        if ik is None:
            continue
        contiguous = (prev_d is not None
                      and dk - prev_d - 1 <= RUN_GAP_CAP
                      and prev_i < ik
                      and ik - prev_i - 1 <= RUN_GAP_CAP
                      and tok.line.seg == d_stream[prev_d].line.seg
                      and i_stream[ik].line.seg == i_stream[prev_i].line.seg
                      and all(i_stream[x].dest is None for x in range(prev_i + 1, ik)))
        if contiguous:
            cur.append((dk, ik))
        else:
            if cur:
                runs.append(cur)
            cur = [(dk, ik)]
        prev_d, prev_i = dk, ik
    if cur:
        runs.append(cur)
    for pairs in runs:
        if not any(d_stream[dk].line.row != i_stream[ik].line.row for dk, ik in pairs):
            continue
        rid = next(run_ids)
        for x in range(pairs[0][0], pairs[-1][0] + 1):
            d_stream[x].run = rid
        for x in range(pairs[0][1], pairs[-1][1] + 1):
            i_stream[x].run = rid


def demote_runs(dels, inss, ids):
    """Fold noise runs back into the surrounding residue.

    Two demotions keep paragraphs whole while preserving true moves:
    - a run whose del-side and ins-side row ranges intersect never went
      anywhere (a real move lands on different rows);
    - a run under RUN_MIN_CHARS word-characters is stock-phrase scale —
      a moved-run identity fragments readable text for little value.
    A stationary run folds back into the in-place edit it belongs to,
    links intact. A demoted true move severs its matches and renders as
    plain deletion + addition ink — un-inked text must never sit in a box
    with no counterpart — but when it still has tile-scale substance
    (>= MIN_TILE_CHARS word-chars) its two sides keep one shared box id,
    so the related fragments stay connected across the gutter.
    """
    by_run = {}
    for side, lines in (("d", dels), ("i", inss)):
        for line in lines:
            for t in line.tokens:
                if t.run is not None:
                    by_run.setdefault(t.run, {"d": [], "i": []})[side].append(t)

    def substance(toks):
        return sum(len(t.norm) for t in toks
                   if any(c.isalnum() for c in t.norm))

    # runs connecting the same source segment to the same destination
    # segment are one movement, judged together — a short bullet head
    # moves with the bullet body it belongs to, not on its own weight
    coalition = {}
    for rid, grp in by_run.items():
        if grp["d"] and grp["i"]:
            key = (grp["d"][0].line.seg, grp["i"][0].line.seg)
            coalition.setdefault(key, []).append(rid)
    weight = {}
    for rids in coalition.values():
        total = sum(substance(by_run[r]["d"]) for r in rids)
        for r in rids:
            weight[r] = total

    for rid, grp in by_run.items():
        d_rows = {t.line.row for t in grp["d"]}
        i_rows = {t.line.row for t in grp["i"]}
        stationary = (d_rows and i_rows
                      and max(d_rows) >= min(i_rows)
                      and max(i_rows) >= min(d_rows))
        word_chars = substance(grp["d"])
        if not (stationary or weight.get(rid, word_chars) < RUN_MIN_CHARS):
            continue
        pair = (next(ids) if not stationary and word_chars >= MIN_TILE_CHARS
                else None)
        for t in grp["d"] + grp["i"]:
            t.run = None
            if not stationary:
                if pair is not None:
                    t.box = pair
                if t.dest is not None:
                    t.dest.dest = None
                    t.dest = None


def word_set(line):
    return {t.key for t in line.tokens if len(t.key) >= 3 and t.key.isalnum()}


def flag_rewrites(dels, inss):
    def low_cov(line):
        return line.tokens and len(line.matched) / len(line.tokens) < 0.5

    candidates = []
    for d in (l for l in dels if low_cov(l)):
        ws_d = word_set(d)
        if not ws_d:
            continue
        for i in (l for l in inss if low_cov(l)):
            ws_i = word_set(i)
            if not ws_i:
                continue
            jac = len(ws_d & ws_i) / len(ws_d | ws_i)
            if jac >= JACCARD:
                candidates.append((jac, d, i))
    for jac, d, i in sorted(candidates, key=lambda c: -c[0]):
        if d.rewrite_partner or i.rewrite_partner:
            continue
        d.rewrite_partner = i
        i.rewrite_partner = d
        # the pair claims both lines wholesale (marks come from their
        # pairwise diff), so match links crossing the pair's boundary
        # dissolve — otherwise text elsewhere would claim a counterpart
        # inside these lines that renders as something else entirely
        for line, partner in ((d, i), (i, d)):
            for t in line.tokens:
                if t.dest is not None and t.dest.line is not partner:
                    t.dest.dest = None
                    t.dest = None


def pair_flags(a, b):
    """Per-token equal/changed flags for both lines of a rewrite pair.

    Pairing is case-insensitive (keys), but a case-only difference must
    still ink as an ordinary mark (I10) — flags require exact equality.
    """
    sm = SequenceMatcher(None, [t.key for t in a.tokens],
                         [t.key for t in b.tokens], autojunk=False)
    fa, fb = [False] * len(a.tokens), [False] * len(b.tokens)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            for x in range(a2 - a1):
                same = a.tokens[a1 + x].norm == b.tokens[b1 + x].norm
                fa[a1 + x] = fb[b1 + x] = same
    return fa, fb


def assign_boxes(dels, inss, ids):
    """Box the residue — every changed token not claimed by a moved run —
    at fragment granularity.

    Rewrite pairs share one line-level id (their connector crosses
    positions). All other residue groups into blobs: maximal residue
    stretches in a side's token stream, broken by an intervening run or a
    row gap over 1 — so residue separated by moved content is separate
    boxes, never one scattered multi-fragment box. Blobs merge only on
    evidence: a surviving token match between them (every surviving
    residue match is local by construction — same-row edits, or
    stationary folds). A merged two-sided box gets a connector; an
    unlinked blob (pure removal or addition) stands alone. A whitespace-
    or punctuation-only fragment on a line that has word content
    elsewhere gets no blob — its tokens attach to a neighboring group at
    render.
    """
    for d in dels:
        if d.rewrite_partner is not None and d.box is None:
            bid = next(ids)
            d.box = bid
            d.rewrite_partner.box = bid

    def word(t):
        return any(c.isalnum() for c in t.norm)

    def blobs(lines):
        # a blob extends across a line boundary only via a *substantive*
        # span — one with word content (or a wholly word-free changed
        # line, which still needs a box). A punctuation-only span on a
        # wordful line never joins or carries a blob: it stays
        # unassigned and attaches to a neighboring group at render.
        frags, cur, prev = [], [], None
        for l in sorted(lines, key=lambda l: l.row):
            if l.box is not None:  # rewrite pair: already boxed line-level
                if cur:
                    frags.append(cur)
                cur, prev = [], None
                continue
            if cur and (prev is None or l.seg != prev.seg):
                frags.append(cur)
                cur = []
            bare = not any(word(t) for t in l.tokens)
            toks, i = l.tokens, 0
            while i < len(toks):
                if toks[i].run is not None or toks[i].box is not None:
                    if cur:  # run or severed-pair wedge
                        frags.append(cur)
                        cur = []
                    i += 1
                    continue
                j = i
                while j < len(toks) and toks[j].run is None \
                        and toks[j].box is None:
                    j += 1
                span = toks[i:j]
                if bare or any(word(t) for t in span):
                    cur.extend(span)
                    prev = l
                elif cur:
                    frags.append(cur)
                    cur = []
                i = j
        if cur:
            frags.append(cur)
        return frags

    every = blobs(dels) + blobs(inss)
    parent = list(range(len(every)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    home = {id(t): k for k, f in enumerate(every) for t in f}
    for k, f in enumerate(every):
        for t in f:
            j = home.get(id(t.dest)) if t.dest is not None else None
            if j is not None:
                parent[find(k)] = find(j)
    boxed = {}
    for k, f in enumerate(every):
        root = find(k)
        if root not in boxed:
            boxed[root] = next(ids)
        for t in f:
            t.box = boxed[root]


def resolve_groups(line):
    """Per-token box membership: run id, else the token's residue box.

    Unassigned tokens (marks, whitespace-only fragments) attach to the
    following group on the line, trailing ones to the preceding group — so
    edge deletions sit inside the box of the content they flank, and every
    token is boxed.
    """
    groups = []
    for t in line.tokens:
        if t.run is not None:
            groups.append(t.run)
        else:
            groups.append(t.box)
    nxt = None
    for i in range(len(groups) - 1, -1, -1):
        if groups[i] is None:
            groups[i] = nxt
        else:
            nxt = groups[i]
    prev = None
    for i in range(len(groups)):
        if groups[i] is None:
            groups[i] = prev
        else:
            prev = groups[i]
    return groups


def cell_html(line, mark):
    """Render one changed line's cell content as HTML.

    kind "eq" emits a plain span inside its box; "mark" emits del/ins ink.
    Adjacent boxes reserve shared-border room as a trailing margin on the
    outgoing element (`ne`) — at a soft-wrap boundary the room dies at the
    line end instead of indenting the wrapped row.
    """
    if not line.tokens:
        return html.escape(line.lead_ws)
    if line.rewrite_partner is not None:
        # one canonical alignment per pair — SequenceMatcher is order-
        # sensitive, so both sides must read the same call (del side first)
        if mark == "del":
            flags, _ = pair_flags(line, line.rewrite_partner)
        else:
            _, flags = pair_flags(line.rewrite_partner, line)
        keys = [("eq" if ok else "mark", line.box) for ok in flags]
    else:
        groups = resolve_groups(line)
        keys = [("eq" if (t.dest is not None and t.norm == t.dest.norm)
                 else "mark", g)
                for t, g in zip(line.tokens, groups)]
    segs, cur_key, cur = [], None, []
    for tok, key in zip(line.tokens, keys):
        if key != cur_key and cur:
            segs.append((cur_key, "".join(cur)))
            cur = []
        cur_key = key
        cur.append(tok.raw)
    if cur:
        segs.append((cur_key, "".join(cur)))
    items, prev_group = [], None
    for (kind, group), text in segs:
        item = {"tag": mark if kind == "mark" else "span",
                "text": text, "group": group, "ne": False}
        if group is not None:
            if prev_group is not None and group != prev_group and items:
                items[-1]["ne"] = True
            prev_group = group
        items.append(item)
    out = [html.escape(line.lead_ws)]
    for it in items:
        attrs = ""
        if it["group"] is not None:
            attrs += f' data-run="{it["group"]}"'
        if it["ne"]:
            attrs += ' class="ne"'
        out.append(f'<{it["tag"]}{attrs}>{html.escape(it["text"])}</{it["tag"]}>')
    return "".join(out)


def process_file(rows, ids):
    """Run the pipeline on one file's rows; returns per-row cell HTML maps
    for each side plus (moved, blocks, rewrites) stats."""
    dels, inss = build_lines(rows)
    d_stream = [t for l in dels for t in l.tokens]
    i_stream = [t for l in inss for t in l.tokens]
    tile(d_stream, i_stream)
    refine(dels, inss)
    compute_runs(d_stream, i_stream, ids)
    demote_runs(dels, inss, ids)
    flag_rewrites(dels, inss)
    assign_boxes(dels, inss, ids)
    left = {l.visual: cell_html(l, "del") for l in dels}
    right = {l.visual: cell_html(l, "ins") for l in inss}
    moved = len({t.run for l in dels for t in l.tokens if t.run is not None})
    rewrites = sum(1 for l in dels if l.rewrite_partner is not None)
    blocks = len({t.box for l in dels + inss for t in l.tokens
                  if t.box is not None}
                 | {l.box for l in dels + inss if l.box is not None})
    return left, right, (moved, blocks, rewrites)

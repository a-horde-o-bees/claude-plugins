# /// script
# requires-python = ">=3.10"
# dependencies = ["beautifulsoup4", "lxml"]
# ///
"""Render a unified diff as a reviewable HTML page set.

Input is either two paths (compared with `diff -ruN`) or an existing
unified diff. The diff is parsed directly and laid out as one table per
file — each change row holds its deletion and insertion cells in the
same table row, so the two sides align by construction, wrapped prose
included. engine.py attributes moved / merged / split content across
line breaks and emits word-level marks; an in-page overlay draws the
boxes and gutter connectors.

A diff spanning several top-level directories is split into one page per
directory behind a dropdown viewer (index.html); otherwise a single
index.html is produced.
"""
import argparse
import html as html_mod
import itertools
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import engine
import lint_diff

AUTO_SPLIT_BYTES = 150_000

CSS = """
/* integer vertical grid: every line-box boundary — where all box edges
   lie — lands on whole pixels, so crisp edges stay crisp */
:root { --lh: 24px; color-scheme: light dark; }
* { box-sizing: border-box; }
body { margin: 16px; color: #1f2328; background: #ffffff;
       font: 13px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas,
             "Liberation Mono", monospace; }
h1 { font: 600 20px/26px -apple-system, "Segoe UI", sans-serif;
     text-align: center; margin: 8px 0 16px; }
.xd-file { position: relative; border: 1px solid #d0d7de;
           border-radius: 6px; margin: 16px 0; }
.xd-head { font: 600 13px/20px -apple-system, "Segoe UI", sans-serif;
           padding: 8px 12px; background: #f6f8fa;
           border-bottom: 1px solid #d0d7de; border-radius: 6px 6px 0 0;
           position: relative; z-index: 1; }
table.xd { position: relative; z-index: 1; width: 100%;
           border-collapse: collapse; table-layout: fixed; }
td { vertical-align: top; padding: 0; }
col.c-ln { width: 46px; }
col.c-gut { width: 48px; }
td.ln { padding-right: 8px; text-align: right;
        color: #8b949e; font-size: 11px; line-height: var(--lh);
        user-select: none; }
td.cl { padding: 0 6px; }
.ctn { display: block; white-space: pre-wrap; overflow-wrap: anywhere;
       line-height: var(--lh); min-height: var(--lh); }
tr.gap td, tr.fold td { color: #57606a; background: #e9edf0;
                        font-size: 11px; line-height: 2; padding: 0 12px; }
tr.fold td { cursor: pointer; user-select: none; }
tr.fold:hover td { background: #dde3e8; }
tr.gap td.gut, tr.fold td.gut, tr.fold:hover td.gut {
  background: transparent; padding: 0; cursor: default; }
tr.fold .arr::before { content: "\\25B8"; }
tr.fold.open .arr::before { content: "\\25BE"; }
.xd-tools { text-align: center; margin: 0 0 8px; }
.xd-tools button { font: 12px/20px -apple-system, "Segoe UI", sans-serif;
                   padding: 2px 10px; border: 1px solid #d0d7de;
                   border-radius: 6px; background: #f6f8fa;
                   color: #24292f; cursor: pointer; }
tr.gap td { height: 10px; }
del, ins { text-decoration: none; }
[data-run] { cursor: pointer; }
.xd-toast { position: absolute; z-index: 10; background: #24292f;
            color: #ffffff; font: 11px/18px -apple-system, "Segoe UI",
            sans-serif; padding: 1px 8px; border-radius: 4px;
            pointer-events: none; }
/* adjacent boxes on one line reserve room for the shared border */
.ne { margin-right: 4px; }
/* overlay: geometry SVG beneath the text */
svg.xdov { position: absolute; inset: 0; width: 100%; height: 100%;
           pointer-events: none; z-index: 0; }
svg.xdov path { stroke: none; stroke-linejoin: round; }
/* rectilinear geometry renders on the pixel grid — no fractional AA;
   connectors keep smooth curves */
svg.xdov path.runbox, svg.xdov path.fill-l, svg.xdov path.fill-r,
svg.xdov path.ink-d, svg.xdov path.ink-i { shape-rendering: crispEdges; }
svg.xdov path.runbox, svg.xdov path.conn {
  fill: none; stroke: #8b949e; stroke-width: 1; }
svg.xdov path.conn { pointer-events: stroke; cursor: pointer; }
svg.xdov path.fill-l { fill: #ffe6e8; }
svg.xdov path.fill-r { fill: #def1e3; }
svg.xdov path.ink-d { fill: #ffc5c9; }
svg.xdov path.ink-i { fill: #b4e0be; }
/* emphasis: darker stroke + inner glow only — the glow path is clipped
   to the box interior, so it marks what belongs to the box without
   lighting up sibling boxes; stroke width never changes, crisp stays
   crisp */
svg.xdov path.glow { fill: none; stroke-width: 2; filter: blur(1px); }
svg.xdov path.hl { stroke: #57606a; }
svg.xdov path.pin { stroke: #24292f; }
svg.xdov path.conn.hl { filter: drop-shadow(0 0 1.5px #57606a); }
svg.xdov path.conn.pin { filter: drop-shadow(0 0 1.5px #24292f); }
@media (prefers-color-scheme: dark) {
  body { color: #c9d1d9; background: #0d1117; }
  .xd-file { border-color: #30363d; }
  .xd-head { background: #161b22; border-color: #30363d; }
  tr.gap td, tr.fold td { background: #1e242c; color: #8b949e; }
  tr.fold:hover td { background: #262d37; }
  tr.gap td.gut, tr.fold td.gut, tr.fold:hover td.gut {
    background: transparent; }
  .xd-tools button { background: #161b22; border-color: #30363d;
                     color: #c9d1d9; }
  svg.xdov path.runbox, svg.xdov path.conn { stroke: #6e7681; }
  svg.xdov path.fill-l { fill: #301b1e; }
  svg.xdov path.fill-r { fill: #142a20; }
  svg.xdov path.ink-d { fill: #6b2b2b; }
  svg.xdov path.ink-i { fill: #21542e; }
  svg.xdov path.hl { stroke: #adbac7; }
  svg.xdov path.pin { stroke: #cdd9e5; }
  svg.xdov path.conn.hl { filter: drop-shadow(0 0 1.5px #adbac7); }
  svg.xdov path.conn.pin { filter: drop-shadow(0 0 1.5px #cdd9e5); }
}
"""

OVERLAY_JS = """
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var entries = [];
  var pinned = null, hovered = null, clipSeq = 0;

  function bandsFor(ctns, ob) {
    var raw = [], lh = 0;
    ctns.forEach(function (ctn) {
      if (!lh) lh = parseFloat(getComputedStyle(ctn).lineHeight) || 0;
      var range = document.createRange();
      range.selectNodeContents(ctn);
      var rects = range.getClientRects();
      for (var k = 0; k < rects.length; k++) {
        var r = rects[k];
        if (r.width < 1) continue;
        var t = r.top - ob.top, b = r.bottom - ob.top, hit = null;
        for (var q = 0; q < raw.length; q++)
          if (Math.abs(raw[q].t - t) < 6) { hit = raw[q]; break; }
        if (hit) { hit.t = Math.min(hit.t, t); hit.b = Math.max(hit.b, b); }
        else raw.push({ t: t, b: b });
      }
    });
    // normalize every band to exactly one line-box height around its
    // center, keeping the measured glyph extent (gt/gb) for the ink.
    // Box edges live on line-box boundaries: the leading between lines
    // is the reserved border lane, so every edge — outer or interior —
    // has the same half-leading clearance from the glyphs, adjacent
    // lines' bands tile exactly, and a blank line (a full empty line
    // box) keeps stacked boxes naturally separate.
    raw = raw.map(function (band) {
      var c = (band.t + band.b) / 2, h = lh || (band.b - band.t);
      return { t: c - h / 2, b: c + h / 2, gt: band.t, gb: band.b };
    });
    raw.sort(function (a, b) { return a.t - b.t; });
    return raw;
  }
  function rowsFor(rects, bands) {
    var byBand = {};
    for (var k = 0; k < rects.length; k++) {
      var r = rects[k];
      if (r.r - r.l < 1) continue;
      var cy = (r.t + r.b) / 2, bi = -1;
      for (var q = 0; q < bands.length; q++)
        if (cy >= bands[q].t && cy <= bands[q].b) { bi = q; break; }
      if (bi < 0) continue;
      var row = byBand[bi];
      if (!row) row = byBand[bi] = { t: bands[bi].t, b: bands[bi].b,
                                     gt: bands[bi].gt, gb: bands[bi].gb,
                                     l: r.l - 2, r: r.r + 2, bi: bi };
      row.l = Math.min(row.l, r.l - 2);
      row.r = Math.max(row.r, r.r + 2);
    }
    return Object.keys(byBand).sort(function (a, b) { return a - b; })
                 .map(function (k) { return byBand[k]; });
  }
  function closeGaps(allRows) {
    var byBand = {};
    allRows.forEach(function (row) {
      var key = row.side + ':' + row.bi;
      (byBand[key] = byBand[key] || []).push(row);
    });
    Object.keys(byBand).forEach(function (key) {
      var rows = byBand[key];
      rows.sort(function (a, b) { return a.l - b.l; });
      for (var i = 0; i < rows.length - 1; i++) {
        var gap = rows[i + 1].l - rows[i].r;
        if (gap > -8 && gap <= 14) {
          var mid = (rows[i].r + rows[i + 1].l) / 2;
          rows[i].r = mid;
          rows[i + 1].l = mid;
        }
      }
    });
  }
  function outlinePath(rows) {
    var pts = [];
    function mid(a, b) { return (a + b) / 2; }
    pts.push([rows[0].l, rows[0].t], [rows[0].r, rows[0].t]);
    for (var i = 0; i < rows.length - 1; i++) {
      var y = mid(rows[i].b, rows[i + 1].t);
      pts.push([rows[i].r, y], [rows[i + 1].r, y]);
    }
    var last = rows[rows.length - 1];
    pts.push([last.r, last.b], [last.l, last.b]);
    for (var i = rows.length - 1; i > 0; i--) {
      var y = mid(rows[i].t, rows[i - 1].b);
      pts.push([rows[i].l, y], [rows[i - 1].l, y]);
    }
    return 'M ' + pts.map(function (pt) { return pt.join(' '); }).join(' L ') + ' Z';
  }
  function touchingSeqs(rows) {
    var seqs = [], cur = [rows[0]];
    for (var i = 1; i < rows.length; i++) {
      if (rows[i].t - rows[i - 1].b < 2) cur.push(rows[i]);
      else { seqs.push(cur); cur = [rows[i]]; }
    }
    seqs.push(cur);
    return seqs;
  }
  function addPath(parent, d, cls, id) {
    var el = document.createElementNS(NS, 'path');
    el.setAttribute('d', d);
    el.setAttribute('class', cls);
    if (id !== null) el.setAttribute('data-run', id);
    parent.appendChild(el);
  }
  function rectPath(l, t, r, b) {
    return 'M ' + l + ' ' + t + ' L ' + r + ' ' + t + ' L ' + r + ' ' + b
      + ' L ' + l + ' ' + b + ' Z';
  }

  function draw() {
    document.querySelectorAll('svg.xdov').forEach(function (s) { s.remove(); });
    entries = [];
    document.querySelectorAll('.xd-file').forEach(function (wrapper) {
      var gut = wrapper.querySelector('td.gut');
      if (!gut) return;
      var svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('class', 'xdov');
      wrapper.appendChild(svg);
      // paint layers: box fills, then word ink, then emphasis inner
      // glows, then outlines + connectors — ink can never cover an
      // outline, outlines always read on top
      var defs = document.createElementNS(NS, 'defs');
      var gFill = document.createElementNS(NS, 'g');
      var gInk = document.createElementNS(NS, 'g');
      var gGlow = document.createElementNS(NS, 'g');
      var gStroke = document.createElementNS(NS, 'g');
      svg.appendChild(defs);
      svg.appendChild(gFill); svg.appendChild(gInk);
      svg.appendChild(gGlow); svg.appendChild(gStroke);
      var ob = svg.getBoundingClientRect();
      var runs = {}, allRows = [];
      ['left', 'right'].forEach(function (side) {
        var ctns = Array.prototype.slice.call(
          wrapper.querySelectorAll('td.cl.' + side + ' .ctn'));
        var bands = bandsFor(ctns, ob);
        var rectsById = {};
        wrapper.querySelectorAll('td.cl.' + side + ' [data-run]')
          .forEach(function (el) {
            var id = el.dataset.run;
            var range = document.createRange();
            range.selectNodeContents(el);
            var list = rectsById[id] = rectsById[id] || [];
            var rects = range.getClientRects();
            for (var k = 0; k < rects.length; k++) {
              var r = rects[k];
              list.push({ t: r.top - ob.top, b: r.bottom - ob.top,
                          l: r.left - ob.left, r: r.right - ob.left });
            }
          });
        Object.keys(rectsById).forEach(function (id) {
          var rows = rowsFor(rectsById[id], bands);
          if (!rows.length) return;
          rows.forEach(function (row) { row.side = side; allRows.push(row); });
          (runs[id] = runs[id] || {})[side] = rows;
        });
        // word ink: per element, per band, at the exact glyph rect —
        // at least 2px inside every outline by construction
        wrapper.querySelectorAll('td.cl.' + side + ' del, td.cl.' + side + ' ins')
          .forEach(function (el) {
            var range = document.createRange();
            range.selectNodeContents(el);
            var rects = range.getClientRects();
            var byBand = {};
            for (var k = 0; k < rects.length; k++) {
              var r = rects[k];
              if (r.width < 1) continue;
              var cy = (r.top + r.bottom) / 2 - ob.top, bi = -1;
              for (var q = 0; q < bands.length; q++)
                if (cy >= bands[q].t && cy <= bands[q].b) { bi = q; break; }
              if (bi < 0) continue;
              var seg = byBand[bi];
              if (!seg) seg = byBand[bi] = { l: r.left - ob.left,
                                             r: r.right - ob.left };
              seg.l = Math.min(seg.l, r.left - ob.left);
              seg.r = Math.max(seg.r, r.right - ob.left);
            }
            var cls = el.tagName === 'DEL' ? 'ink-d' : 'ink-i';
            Object.keys(byBand).forEach(function (bi) {
              var seg = byBand[bi], band = bands[bi];
              addPath(gInk, rectPath(seg.l, band.gt, seg.r, band.gb),
                      cls, null);
            });
          });
      });
      closeGaps(allRows);
      var gr = gut.getBoundingClientRect();
      var gx0 = gr.left - ob.left, gx1 = gr.right - ob.left;
      Object.keys(runs).forEach(function (id) {
        var run = runs[id];
        ['left', 'right'].forEach(function (side) {
          if (!run[side]) return;
          touchingSeqs(run[side]).forEach(function (seq) {
            var d = outlinePath(seq);
            addPath(gFill, d, 'fill-' + side[0], null);
            // inner-glow path: same outline, wide blurred stroke clipped
            // to the box's own interior — visible only when emphasized
            var cid = 'xdc' + (clipSeq++);
            var cp = document.createElementNS(NS, 'clipPath');
            cp.setAttribute('id', cid);
            var cpp = document.createElementNS(NS, 'path');
            cpp.setAttribute('d', d);
            cp.appendChild(cpp);
            defs.appendChild(cp);
            var glow = document.createElementNS(NS, 'path');
            glow.setAttribute('d', d);
            glow.setAttribute('class', 'glow');
            glow.setAttribute('data-run', id);
            glow.setAttribute('clip-path', 'url(#' + cid + ')');
            gGlow.appendChild(glow);
            addPath(gStroke, d, 'runbox box-' + side[0], id);
          });
        });
        if (run.left && run.right) {
          var yL = (run.left[0].t + run.left[run.left.length - 1].b) / 2;
          var yR = (run.right[0].t + run.right[run.right.length - 1].b) / 2;
          var xm = (gx0 + gx1) / 2;
          addPath(gStroke, 'M ' + gx0 + ' ' + yL + ' C ' + xm + ' ' + yL + ' '
                  + xm + ' ' + yR + ' ' + gx1 + ' ' + yR, 'conn', id);
        }
      });
      entries.push({ svg: svg, runs: runs, wrapper: wrapper });
    });
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(function () {
        fallbackCopy(text);
      });
    } else fallbackCopy(text);
  }
  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
  }
  function blockRef(entry, id) {
    // composite handle: file:line per side for precision, verbatim block
    // contents per side for durability — the quote stays greppable in
    // the diff or either tree after line numbers drift
    var wrapper = entry.wrapper;
    function sideInfo(sideCls, lnIdx) {
      var els = wrapper.querySelectorAll(
        'td.cl.' + sideCls + ' [data-run="' + id + '"]');
      if (!els.length) return null;
      var parts = [], lo = null, hi = null, lastTr = null;
      els.forEach(function (el) {
        var tr = el.closest('tr');
        if (tr !== lastTr) {
          parts.push('');
          lastTr = tr;
          var ln = parseInt(tr.children[lnIdx].textContent, 10);
          if (!isNaN(ln)) {
            if (lo === null) lo = ln;
            hi = ln;
          }
        }
        parts[parts.length - 1] += el.textContent;
      });
      return { text: parts.join('\\n').replace(/\\s+$/, ''), lo: lo, hi: hi };
    }
    function loc(path, s) {
      if (s.lo === null) return path;
      return path + ':' + (s.lo === s.hi ? s.lo : s.lo + '-' + s.hi);
    }
    var L = sideInfo('left', 0), R = sideInfo('right', 3);
    // one stanza per present side: an ALL-CAPS marker line carrying the
    // source handle, then the verbatim contents on their own lines
    var lines = [];
    if (L) lines.push('OLD: ' + loc(wrapper.dataset.old || '?', L), L.text);
    if (R) lines.push('NEW: ' + loc(wrapper.dataset.new || '?', R), R.text);
    return { text: lines.join('\\n') };
  }
  document.addEventListener('contextmenu', function (e) {
    var id = hitRun(e);
    if (id === null) return;
    e.preventDefault();
    var entry = null;
    for (var w = 0; w < entries.length; w++)
      if (entries[w].runs[id]) { entry = entries[w]; break; }
    if (!entry) return;
    var ref = blockRef(entry, id);
    copyText(ref.text);
    var toast = document.createElement('div');
    toast.className = 'xd-toast';
    toast.textContent = 'copied block ref';
    toast.style.left = (e.pageX + 12) + 'px';
    toast.style.top = (e.pageY + 12) + 'px';
    document.body.appendChild(toast);
    setTimeout(function () { toast.remove(); }, 1000);
  });

  function set(id, cls, on) {
    document.querySelectorAll('svg.xdov path[data-run="' + id + '"]')
      .forEach(function (p) { p.classList.toggle(cls, on); });
  }
  function toFront(id) {
    document.querySelectorAll('svg.xdov path[data-run="' + id + '"]')
      .forEach(function (p) { p.parentNode.appendChild(p); });
  }
  function hitRun(e) {
    var conn = e.target.closest && e.target.closest('path.conn');
    if (conn) return conn.dataset.run;
    for (var w = 0; w < entries.length; w++) {
      var ob = entries[w].svg.getBoundingClientRect();
      if (e.clientX < ob.left || e.clientX > ob.right
          || e.clientY < ob.top || e.clientY > ob.bottom) continue;
      var x = e.clientX - ob.left, y = e.clientY - ob.top;
      var runs = entries[w].runs;
      var ids = Object.keys(runs);
      for (var q = 0; q < ids.length; q++) {
        var run = runs[ids[q]];
        var sides = ['left', 'right'];
        for (var s = 0; s < 2; s++) {
          var rows = run[sides[s]] || [];
          for (var k = 0; k < rows.length; k++) {
            var row = rows[k];
            if (x >= row.l && x <= row.r && y >= row.t && y <= row.b)
              return ids[q];
          }
        }
      }
    }
    return null;
  }

  document.addEventListener('mousemove', function (e) {
    var id = hitRun(e);
    if (id === hovered) return;
    if (hovered !== null && hovered !== pinned) set(hovered, 'hl', false);
    hovered = id;
    if (id !== null) { set(id, 'hl', true); toFront(id); }
    else if (pinned !== null) toFront(pinned);
    document.body.style.cursor = id !== null ? 'pointer' : '';
  });
  document.addEventListener('click', function (e) {
    var id = hitRun(e);
    if (id === null) return;
    if (id === pinned) {
      set(id, 'hl', id === hovered);
      set(id, 'pin', false);
      pinned = null;
      return;
    }
    if (pinned !== null) { set(pinned, 'hl', false); set(pinned, 'pin', false); }
    pinned = id;
    set(id, 'hl', true);
    set(id, 'pin', true);
    toFront(id);
  });

  var pending = null;
  function redraw() {
    if (pending) cancelAnimationFrame(pending);
    pending = requestAnimationFrame(draw);
  }
  addEventListener('resize', redraw);

  // expandable unchanged hunks: per-fold toggle + page-level toggle;
  // geometry redraws after any fold changes the layout
  function setFold(fold, open) {
    fold.classList.toggle('open', open);
    var r = fold.nextElementSibling;
    while (r && r.classList.contains('fc')) {
      r.hidden = !open;
      r = r.nextElementSibling;
    }
  }
  document.addEventListener('click', function (e) {
    var fold = e.target.closest && e.target.closest('tr.fold');
    if (!fold) return;
    setFold(fold, !fold.classList.contains('open'));
    redraw();
  });
  var allBtn = document.getElementById('xd-unchanged');
  if (allBtn) allBtn.addEventListener('click', function () {
    var open = allBtn.dataset.open !== '1';
    allBtn.dataset.open = open ? '1' : '0';
    allBtn.textContent = (open ? 'Hide' : 'Show') + ' unchanged hunks';
    document.querySelectorAll('tr.fold').forEach(function (f) {
      setFold(f, open);
    });
    redraw();
  });
  if (document.readyState === 'complete') draw();
  else addEventListener('load', draw);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
})();
"""

VIEWER = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; margin: 0; }}
  body {{ display: flex; flex-direction: column;
         font: 14px/1.4 -apple-system, "Segoe UI", sans-serif;
         color: #24292e; background: #fff; }}
  header {{ display: flex; align-items: center; gap: .8em; flex-wrap: wrap;
            padding: .6em 1em; border-bottom: 1px solid #d0d7de; }}
  header h1 {{ font-size: 1em; margin: 0; white-space: nowrap; }}
  header .total {{ color: #57606a; white-space: nowrap; }}
  select {{ font: inherit; padding: .3em .5em; min-width: 18em;
            border: 1px solid #d0d7de; border-radius: 6px;
            background: #f6f8fa; color: inherit; }}
  iframe {{ flex: 1; width: 100%; border: none; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #c9d1d9; background: #0d1117; }}
    header {{ border-color: #30363d; }}
    header .total {{ color: #8b949e; }}
    select {{ background: #161b22; border-color: #30363d; }}
  }}
</style></head><body>
<header>
  <h1>{title}</h1>
  <label for="part">Section:</label>
  <select id="part">
{options}
  </select>
  <span class="total">{total}</span>
  <span class="total">boxes mark changed regions; connectors pair counterparts (crossing = moved)</span>
  <span class="total">hover a box to trace both sides; click pins (click again to unpin)</span>
  <span class="total">right-click a box to copy its file:line + contents</span>
</header>
<iframe id="diff" title="diff section"></iframe>
<script>
  const sel = document.getElementById('part');
  const frame = document.getElementById('diff');
  function show(part) {{
    if (part && [...sel.options].some(o => o.value === part)) sel.value = part;
    frame.src = sel.value + '.html';
    history.replaceState(null, '', '#' + sel.value);
  }}
  sel.addEventListener('change', () => show());
  show(location.hash.slice(1));
</script>
</body></html>
"""


def run_diff(old, new):
    proc = subprocess.run(["diff", "-ruN", old, new], capture_output=True, text=True)
    if proc.returncode > 1:
        sys.exit(f"diff failed: {proc.stderr.strip()}")
    return proc.stdout


def file_chunks(diff_text):
    """Split a unified diff into per-file chunks with their old-side paths."""
    parts = re.split(r"(?m)^(?=diff )", diff_text)
    chunks = []
    for part in parts:
        if not part.strip():
            continue
        m = re.search(r"(?m)^--- ([^\t\n]+)", part)
        if m is None:
            m = re.match(r"diff\s+(?:-\S+\s+)*(\S+)\s+\S+\s*$", part.splitlines()[0])
        chunks.append((m.group(1) if m else "(unknown)", part))
    return chunks


def group_key(path):
    """Top-level directory once the diff root ('a', old dir name) is stripped."""
    rel = Path(path).parts
    rel = rel[1:] if len(rel) > 1 else rel
    return rel[0] if len(rel) > 1 else "(root)"


def stats(text):
    adds = len(re.findall(r"(?m)^\+(?!\+\+ )", text))
    dels = len(re.findall(r"(?m)^-(?!-- )", text))
    files = max(1, len(re.findall(r"(?m)^diff ", text)))
    return files, adds, dels


HUNK_RE = re.compile(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
PAIR_JACCARD = 0.4  # line-pair alignment floor (same family as rewrite flag)


def _wset(text):
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))


def _pair_block(pend_d, pend_i, rows):
    """Monotonic similarity alignment of one change block.

    The best-matching del/ins line pair (word-set Jaccard >= PAIR_JACCARD)
    anchors a recursive split, so true counterparts share a table row even
    when the block's line counts differ — an edited line reads as an
    in-place edit, not a delete + add. A block with no similar pair falls
    back to positional pairing.
    """
    if pend_d and pend_i:
        best = None
        for a, (_, dt) in enumerate(pend_d):
            wd = _wset(dt)
            if not wd:
                continue
            for b, (_, it) in enumerate(pend_i):
                wi = _wset(it)
                if not wi:
                    continue
                jac = len(wd & wi) / len(wd | wi)
                if jac >= PAIR_JACCARD and (best is None or jac > best[0]):
                    best = (jac, a, b)
        if best is not None:
            _, a, b = best
            _pair_block(pend_d[:a], pend_i[:b], rows)
            rows.append(("chg", pend_d[a][0], pend_d[a][1],
                         pend_i[b][0], pend_i[b][1]))
            _pair_block(pend_d[a + 1:], pend_i[b + 1:], rows)
            return
    for k in range(max(len(pend_d), len(pend_i))):
        dl = pend_d[k] if k < len(pend_d) else (None, None)
        il = pend_i[k] if k < len(pend_i) else (None, None)
        rows.append(("chg", dl[0], dl[1], il[0], il[1]))


def parse_files(diff_text):
    """Parse a unified diff into [(old_path, new_path, rows)].

    rows: (kind, lnum, ltext, rnum, rtext, lsem, rsem). Visual rows pack
    each change block compactly (positional zip — no alignment-padding
    blanks interleaved between lines); the *semantic* pairing from the
    similarity alignment is carried separately as per-side sem ids
    (equal iff the lines are counterparts), which is the row axis the
    engine classifies against. Context lines are the shared anchors.
    """
    files = []
    lines = diff_text.splitlines()
    n, i = len(lines), 0
    while i < n:
        if not (lines[i].startswith("--- ")
                and i + 1 < n and lines[i + 1].startswith("+++ ")):
            i += 1
            continue
        old = lines[i][4:].split("\t")[0]
        new = lines[i + 1][4:].split("\t")[0]
        rows = []
        files.append((old, new, rows))
        i += 2
        sem = [0]
        o_next, n_next = 1, 1
        while i < n:
            m = HUNK_RE.match(lines[i])
            if m is None:
                break
            onum, oc = int(m.group(1)), int(m.group(2) or "1")
            nnum, nc = int(m.group(3)), int(m.group(4) or "1")
            if nnum > n_next:
                # lines identical on both sides, skipped by the diff —
                # a labeled separator carrying each side's range
                rows.append(("gap", o_next, onum - 1, n_next, nnum - 1,
                             None, None))
                sem[0] += 1
            i += 1
            pend_d, pend_i = [], []

            def flush():
                semrows = []
                _pair_block(pend_d, pend_i, semrows)
                lsems, rsems = [], []
                for (_, _, lt, _, rt) in semrows:
                    s = sem[0]
                    sem[0] += 1
                    if lt is not None:
                        lsems.append(s)
                    if rt is not None:
                        rsems.append(s)
                for k in range(max(len(pend_d), len(pend_i))):
                    dl = pend_d[k] if k < len(pend_d) else (None, None)
                    il = pend_i[k] if k < len(pend_i) else (None, None)
                    rows.append(("chg", dl[0], dl[1], il[0], il[1],
                                 lsems[k] if k < len(lsems) else None,
                                 rsems[k] if k < len(rsems) else None))
                pend_d.clear()
                pend_i.clear()

            while i < n and (oc > 0 or nc > 0):
                ln = lines[i]
                tag, body = (ln[0], ln[1:]) if ln else (" ", "")
                if tag == "\\":  # "\ No newline at end of file"
                    i += 1
                    continue
                if tag == "-":
                    pend_d.append((onum, body))
                    onum += 1
                    oc -= 1
                elif tag == "+":
                    pend_i.append((nnum, body))
                    nnum += 1
                    nc -= 1
                else:
                    flush()
                    rows.append(("ctx", onum, body, nnum, body, sem[0], sem[0]))
                    sem[0] += 1
                    onum += 1
                    nnum += 1
                    oc -= 1
                    nc -= 1
                i += 1
            flush()
            o_next, n_next = onum, nnum
    return files


def make_src_reader():
    cache = {}

    def get(path):
        if path not in cache:
            try:
                p = Path(path)
                cache[path] = (p.read_text(encoding="utf-8").splitlines()
                               if p.is_file() else None)
            except OSError:
                cache[path] = None
        return cache[path]
    return get


def add_folds(files, get_src):
    """Embed unchanged gaps between hunks as hidden, expandable rows.

    Requires the new-side source file; every new-side line the diff
    carries must match the file at its claimed number (validation gate) —
    otherwise the file may have drifted since the diff was made and the
    page stays diff-only for that file.
    """
    for old, new, rows in files:
        src = get_src(new) if new != "/dev/null" else None
        if src is None:
            continue
        ok = True
        for r in rows:
            if r[0] in ("ctx", "chg") and r[3] is not None and r[4] is not None:
                if r[3] > len(src) or src[r[3] - 1] != r[4]:
                    ok = False
                    break
        if not ok:
            continue

        def fold_rows(o1, o2, n1, n2):
            out = [("fold", o1, o2, n1, n2, None, None)]
            for k in range(n2 - n1 + 1):
                text = src[n1 + k - 1]
                out.append(("fctx", o1 + k, text, n1 + k, text, None, None))
            return out

        merged, prev_o, prev_n = [], 0, 0
        for r in rows:
            if r[0] == "gap" and r[4] <= len(src):
                merged.extend(fold_rows(r[1], r[2], r[3], r[4]))
                continue
            merged.append(r)
            if r[0] in ("ctx", "chg"):
                if r[1] is not None:
                    prev_o = r[1]
                if r[3] is not None:
                    prev_n = r[3]
        tail = len(src) - prev_n
        if tail > 0:
            merged.extend(fold_rows(prev_o + 1, prev_o + tail,
                                    prev_n + 1, len(src)))
        rows[:] = merged


def head_label(old, new):
    """Collapse the common path suffix: '{old_root → new_root}/rest'."""
    if old == "/dev/null":
        return f"added: {new}"
    if new == "/dev/null":
        return f"removed: {old}"
    if old == new:
        return old
    o, ns = old.split("/"), new.split("/")
    k = 0
    while k < min(len(o), len(ns)) - 1 and o[-1 - k] == ns[-1 - k]:
        k += 1
    if k:
        return ("{" + "/".join(o[:len(o) - k]) + " → "
                + "/".join(ns[:len(ns) - k]) + "}/" + "/".join(o[len(o) - k:]))
    return f"{old} → {new}"


def esc(text):
    return html_mod.escape(text) if text else ""


def render_page(diff_text, title, out_path, get_src=None):
    files = parse_files(diff_text)
    if not files:
        sys.exit("no parseable file diffs in input")
    if get_src is not None:
        add_folds(files, get_src)
    ids = itertools.count(1)
    body = []
    moved = blocks = rewrites = 0
    for old, new, rows in files:
        left, right, (m, b, rw) = engine.process_file(rows, ids)
        moved, blocks, rewrites = moved + m, blocks + b, rewrites + rw
        trs = []
        for row_i, row in enumerate(rows):
            kind, lnum, ltext, rnum, rtext = row[:5]
            if kind in ("gap", "fold"):
                # per-side "a-b unchanged" labels; the gutter cell stays
                # transparent — connectors travel it. A fold expands;
                # a bare gap (source unavailable) just labels the span.
                o1, o2, n1, n2 = row[1], row[2], row[3], row[4]

                def rng(a, b):
                    return f"{a}" if a == b else f"{a}-{b}"
                arr = '<span class="arr"></span> ' if kind == "fold" else ""
                trs.append(
                    f'<tr class="{kind}">'
                    f'<td colspan="2">{arr}{rng(o1, o2)} unchanged</td>'
                    f'<td class="gut"></td>'
                    f'<td colspan="2">{arr}{rng(n1, n2)} unchanged</td></tr>')
                continue
            tr_open = "<tr>"
            if kind == "fctx":
                tr_open = '<tr class="fc" hidden>'
                lcell, rcell = esc(ltext), esc(rtext)
                lcls = rcls = "cl"
            elif kind == "ctx":
                lcell, rcell = esc(ltext), esc(rtext)
                lcls = rcls = "cl"
            else:
                lcell = left.get(row_i, esc(ltext))
                rcell = right.get(row_i, esc(rtext))
                lcls = "cl del" if ltext is not None else "cl"
                rcls = "cl ins" if rtext is not None else "cl"
            trs.append(
                f'{tr_open}<td class="ln">{lnum if lnum is not None else ""}</td>'
                f'<td class="{lcls} left"><span class="ctn">{lcell}</span></td>'
                f'<td class="gut"></td>'
                f'<td class="ln">{rnum if rnum is not None else ""}</td>'
                f'<td class="{rcls} right"><span class="ctn">{rcell}</span></td>'
                f'</tr>')
        body.append(
            f'<div class="xd-file" data-old="{esc(old)}" data-new="{esc(new)}">'
            f'<div class="xd-head">{esc(head_label(old, new))}</div>'
            f'<table class="xd"><colgroup><col class="c-ln"><col>'
            f'<col class="c-gut"><col class="c-ln"><col></colgroup>'
            f'{"".join(trs)}</table></div>')
    tools = ('<div class="xd-tools"><button id="xd-unchanged">'
             'Show unchanged hunks</button></div>\n'
             if any('class="fold"' in b for b in body) else '')
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, '
            'initial-scale=1">\n<title>' + esc(title) + '</title>\n<style>'
            + CSS + '</style></head>\n<body>\n<h1>' + esc(title) + '</h1>\n'
            + tools + "\n".join(body)
            + '\n<script>' + OVERLAY_JS + '</script>\n</body></html>\n')
    Path(out_path).write_text(page, encoding="utf-8")
    violations = lint_diff.lint_html(page)
    for v in violations:
        print(f"LINT {out_path}: {v}", file=sys.stderr)
    return moved, blocks, rewrites, len(violations)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--old", help="old file or directory (needs --new)")
    src.add_argument("--diff", help="existing unified diff file")
    ap.add_argument("--new", help="new file or directory")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--title", default=None, help="viewer title")
    ap.add_argument("--split", choices=["auto", "always", "never"], default="auto",
                    help="split into per-top-level-directory pages (default: auto)")
    args = ap.parse_args()

    if args.old:
        if not args.new:
            ap.error("--old requires --new")
        diff_text = run_diff(args.old, args.new)
        title = args.title or f"{Path(args.old).name} → {Path(args.new).name}"
    else:
        diff_text = Path(args.diff).read_text(encoding="utf-8")
        title = args.title or Path(args.diff).stem
    if not diff_text.strip():
        sys.exit("no differences")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    groups = {}
    for path, chunk in file_chunks(diff_text):
        groups.setdefault(group_key(path), []).append(chunk)
    split = (args.split == "always"
             or (args.split == "auto" and len(groups) > 1
                 and len(diff_text) > AUTO_SPLIT_BYTES))

    get_src = make_src_reader()
    if not split:
        moved, blocks, rewrites, lint = render_page(
            diff_text, title, out / "index.html", get_src)
        f, a, d = stats(diff_text)
        print(f"{out / 'index.html'}: {f} files, +{a}/-{d}, "
              f"{moved} moved runs, {blocks} change blocks, {rewrites} rewrite pairs"
              + (f", {lint} LINT VIOLATIONS" if lint else ""))
        return

    options, tf, ta, td = [], 0, 0, 0
    for name in sorted(groups):
        safe = re.sub(r"[^\w.-]", "_", name)
        text = "".join(groups[name])
        moved, blocks, rewrites, lint = render_page(
            text, f"{title}: {name}", out / f"{safe}.html", get_src)
        f, a, d = stats(text)
        tf, ta, td = tf + f, ta + a, td + d
        options.append(
            f'<option value="{safe}">{html_mod.escape(name)} &mdash; '
            f'{f} file{"s" if f != 1 else ""}, +{a}/&minus;{d}</option>')
        print(f"{safe}.html: {f} files, +{a}/-{d}, "
              f"{moved} moved runs, {blocks} change blocks, {rewrites} rewrite pairs"
              + (f", {lint} LINT VIOLATIONS" if lint else ""))
    (out / "index.html").write_text(VIEWER.format(
        title=html_mod.escape(title), options="\n".join(options),
        total=f"{tf} files total, +{ta}/&minus;{td}"), encoding="utf-8")
    print(f"viewer: {out / 'index.html'} ({len(groups)} sections)")


if __name__ == "__main__":
    main()

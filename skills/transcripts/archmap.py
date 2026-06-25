#!/usr/bin/env python3
"""Generate a SELF-CONTAINED architecture map of the `time` package as one HTML file.

Unlike `architecture.mmd` (a hand-kept flow sketch), this INTROSPECTS the code: every
component card lists its real file path and the functions/signatures it owns, extracted
live via `ast`, each with a hover tooltip = the symbol's docstring summary. The flow
diagram (Mermaid, clickable) sits on top; clicking a node jumps to that component's card.
Re-run after code changes — signatures can't drift because they're read, not transcribed.

    uv run ${CLAUDE_SKILL_DIR}/archmap.py                 # -> working diagrams/archmap.html
    uv run ${CLAUDE_SKILL_DIR}/archmap.py --out /tmp/a.html
"""
import argparse
import ast
import html
import pathlib

import _paths

HERE = pathlib.Path(__file__).resolve().parent

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

# Architectural metadata (design intent — the flow + ownership). Signatures are NOT here;
# they are read from the files. `file` keys are introspected; `db`/`ext`/`planned` are not.
LAYERS = [
    ("Source — Claude Code harness (not owned)", [
        {"key": "JSONL", "kind": "ext", "title": "transcript JSONL",
         "path": "~/.claude/projects/<proj>/*.jsonl  (+ <stem>/ subagent dirs)",
         "role": "Raw session records, one JSON object per line. The ground truth."},
        {"key": "SET", "kind": "ext", "title": "settings.json",
         "path": "~/.claude/settings.json",
         "role": "cleanupPeriodDays sets how far back transcripts survive — the history horizon."},
    ]),
    ("Ingest + cache", [
        {"key": "raw_db", "kind": "cache", "file": "raw_db.py",
         "role": "JSONL → raw cache. Verbs: ingest (incremental UPSERT by size+mtime), reset (gated)."},
        {"key": "RAW", "kind": "db", "title": "raw.db",
         "path": "time/~/.claude/a-horde-o-bees/transcripts/raw.db  (cwd-relative)",
         "role": "Regenerable cache: one row per physical line, full payload, is_replay/is_meta marked.",
         "tables": ["raw(file, line, type, uuid, parent_uuid, timestamp, is_replay, is_compact_summary, json, …)",
                    "file_state(file, size, mtime_ns, n_lines)  — incremental-ingest ledger"]},
    ]),
    ("Model — single source of truth", [
        {"key": "model", "kind": "model", "file": "swimlane_timeline.py",
         "role": "events → time-blocks → coverage → exchanges → segment geometry; + standalone static render. "
                 "The renderers are dumb consumers of this geometry."},
    ]),
    ("Consumers", [
        {"key": "branch_tree", "kind": "consumer", "file": "branch_tree.py",
         "role": "Session-segment forest / flat rail (root · resume · compaction · rewind)."},
        {"key": "server", "kind": "consumer", "file": "swimlane_server.py",
         "role": "Interactive shared-column segment-tree server: Corpus + stdlib HTTP + inline client HTML."},
        {"key": "exchanges", "kind": "consumer", "file": "exchanges.py",
         "role": "Annotation store CLI: derive prompt-anchored exchanges, author/join description + topic."},
        {"key": "report", "kind": "planned", "title": "report (planned)",
         "path": "(not built — verbs/report.md)",
         "role": "Roll coverage up per exchange/day, filter by topic. The engaged-time rollup verb."},
    ]),
    ("Persistence (survives cache rebuilds)", [
        {"key": "ANNO", "kind": "db", "title": "annotations.db",
         "path": "time/~/.claude/a-horde-o-bees/transcripts/annotations.db",
         "role": "Persistent, UUID-keyed — the only authored state; joined to derived exchanges by prompt UUID.",
         "tables": ["exchange(prompt_uuid PK, description, updated_at)",
                    "topic(name PK, description, updated_at)",
                    "exchange_topic(prompt_uuid PK, topic)"]},
    ]),
]

EDGES = [
    ("SET", "JSONL", "governs retention"),
    ("JSONL", "raw_db", "ingest"),
    ("raw_db", "RAW", ""),
    ("RAW", "model", "read"),
    ("model", "branch_tree", ""),
    ("branch_tree", "server", "segments"),
    ("model", "server", "geometry"),
    ("model", "exchanges", "materialize_exchanges"),
    ("exchanges", "ANNO", "r/w"),
    ("model", "report", ""),
    ("ANNO", "report", "read"),
]

KIND_CLASS = {"ext": "ext", "cache": "cache", "db": "db", "model": "model",
              "consumer": "consumer", "planned": "planned"}


def _sig(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """`name(args) -> ret` from a def node, via ast.unparse (real, not transcribed)."""
    args = ast.unparse(node.args)
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{node.name}({args}){ret}"


def _doc1(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> str:
    """First sentence of the docstring (the tooltip), collapsed to one line."""
    d = ast.get_docstring(node) or ""
    d = " ".join(d.split())
    if not d:
        return ""
    cut = d.find(". ")
    return (d[:cut + 1] if cut != -1 else d)[:240]


def _symbols(path: pathlib.Path):
    """[(signature, doc, is_private, owner_class_or_None)] for every def in the file."""
    tree = ast.parse(path.read_text())
    out = []
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((_sig(n), _doc1(n), n.name.startswith("_"), None))
        elif isinstance(n, ast.ClassDef):
            out.append((f"class {n.name}", _doc1(n), False, n.name))
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.append((_sig(m), _doc1(m), m.name.startswith("_"), n.name))
    return out


def _card(c: dict) -> str:
    key = c["key"]
    title = html.escape(c.get("title") or c.get("file") or key)
    path = html.escape(c.get("path") or (c["file"] if c.get("file") else ""))
    role = html.escape(c.get("role", ""))
    rows = ""
    if c.get("file"):
        for sig, doc, priv, _owner in _symbols(HERE / c["file"]):
            cls = "sym priv" if priv else "sym"
            if sig.startswith("class "):
                cls = "sym cls"
            tip = f' data-tip="{html.escape(doc)}"' if doc else ""
            rows += f'<div class="{cls}"{tip}>{html.escape(sig)}</div>'
    for t in c.get("tables", []):
        rows += f'<div class="sym tbl">{html.escape(t)}</div>'
    owns = f'<div class="owns">{rows}</div>' if rows else ""
    pth = f'<div class="path">{path}</div>' if path else ""
    return (f'<div class="card {KIND_CLASS[c["kind"]]}" id="card-{key}">'
            f'<div class="chead">{title}</div>{pth}'
            f'<div class="role">{role}</div>{owns}</div>')


def _mermaid() -> str:
    lines = ["flowchart LR"]
    for _, comps in LAYERS:
        for c in comps:
            label = c.get("title") or c.get("file") or c["key"]
            lines.append(f'  {c["key"]}["{label}"]:::{KIND_CLASS[c["kind"]]}')
    for a, b, lbl in EDGES:
        arrow = f'-- "{lbl}" -->' if lbl else "-->"
        lines.append(f"  {a} {arrow} {b}")
    for _, comps in LAYERS:
        for c in comps:
            lines.append(f'  click {c["key"]} "#card-{c["key"]}"')
    styles = {
        "ext": "fill:#2b3550,stroke:#5a6a8a,color:#dfe6f5",
        "cache": "fill:#3a2f1a,stroke:#b08030,color:#f5ecd8",
        "db": "fill:#23303a,stroke:#4a8aa0,color:#dff0f5",
        "model": "fill:#1f3a2a,stroke:#50c878,color:#dff5e8",
        "consumer": "fill:#2b2b40,stroke:#8a7ac0,color:#e8e0f5",
        "planned": "fill:#33333a,stroke:#666,color:#aaa",
    }
    for k, v in styles.items():
        lines.append(f"  classDef {k} {v}")
    return "\n".join(lines)


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>
 body{{margin:0;background:#0e1119;color:#cdd6e8;font:13px/1.45 system-ui,sans-serif}}
 header{{padding:10px 16px;border-bottom:1px solid #2a3145;display:flex;gap:12px;align-items:baseline}}
 header h1{{font-size:15px;margin:0;font-weight:600}} header span{{color:#6a7490;font-size:12px}}
 #flow{{padding:16px;border-bottom:1px solid #2a3145;overflow:auto}}
 .lay{{padding:6px 16px}} .lay h2{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;
   color:#7a849c;margin:14px 0 6px;font-weight:600}}
 .grid{{display:flex;flex-wrap:wrap;gap:12px}}
 .card{{background:#141925;border:1px solid #28303f;border-left-width:3px;border-radius:6px;
   padding:9px 11px;width:min(420px,100%);box-sizing:border-box}}
 .card.ext{{border-left-color:#5a6a8a}} .card.cache{{border-left-color:#b08030}}
 .card.db{{border-left-color:#4a8aa0}} .card.model{{border-left-color:#50c878}}
 .card.consumer{{border-left-color:#8a7ac0}} .card.planned{{border-left-color:#666;opacity:.78}}
 .chead{{font-weight:600;font-size:13px;color:#eaf0fb}}
 .path{{font:11px/1.4 ui-monospace,Menlo,monospace;color:#7d88a0;margin:2px 0 5px;word-break:break-all}}
 .role{{color:#aeb8cc;margin-bottom:7px}}
 .owns{{display:flex;flex-direction:column;gap:1px;max-height:340px;overflow:auto}}
 .sym{{font:11px/1.5 ui-monospace,Menlo,monospace;color:#cfe3d4;padding:1px 5px;border-radius:3px;
   white-space:pre-wrap;word-break:break-word;cursor:default}}
 .sym:hover{{background:#1d2433}}
 .sym.priv{{color:#7f8aa0}} .sym.cls{{color:#f0c674;margin-top:4px;font-weight:600}}
 .sym.tbl{{color:#8fd0e0}}
 #tip{{position:fixed;max-width:380px;background:#0a0c12;border:1px solid #3a4663;border-radius:5px;
   padding:6px 9px;font-size:12px;color:#dbe3f2;pointer-events:none;display:none;z-index:50;
   box-shadow:0 4px 14px rgba(0,0,0,.5)}}
</style></head><body>
<header><h1>{title}</h1><span>signatures introspected live via ast · click a node to jump to its card · hover a signature for its doc</span></header>
<div id="flow"><pre class="mermaid">{mmd}</pre></div>
{cards}
<div id="tip"></div>
<script type="module">
import mermaid from "{cdn}";
mermaid.initialize({{startOnLoad:true, theme:"dark", securityLevel:"loose",
  flowchart:{{useMaxWidth:false}}, themeVariables:{{fontFamily:"system-ui,sans-serif"}}}});
await mermaid.run();
const tip=document.getElementById('tip');
document.querySelectorAll('.sym[data-tip]').forEach(el=>{{
  el.addEventListener('mousemove',e=>{{tip.textContent=el.dataset.tip;tip.style.display='block';
    tip.style.left=Math.min(e.clientX+14,innerWidth-396)+'px';tip.style.top=(e.clientY+16)+'px';}});
  el.addEventListener('mouseleave',()=>tip.style.display='none');
}});
</script></body></html>
"""


def build(title: str) -> str:
    cards = ""
    for name, comps in LAYERS:
        cards += f'<div class="lay"><h2>{html.escape(name)}</h2><div class="grid">'
        cards += "".join(_card(c) for c in comps)
        cards += "</div></div>"
    return PAGE.format(title=html.escape(title), mmd=html.escape(_mermaid()),
                       cards=cards, cdn=MERMAID_CDN)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=_paths.diagram("archmap.html"))
    ap.add_argument("--title", default="time package — architecture map")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(a.title))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

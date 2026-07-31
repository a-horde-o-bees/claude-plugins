#!/usr/bin/env python3
"""Wrap a Mermaid `.mmd` source into a SELF-CONTAINED, browser-openable HTML.

The diagram source is inlined (so `file://` works with no server and no CORS), and
Mermaid renders it client-side from a CDN. The page offers Download SVG / Download PNG
buttons; for PDF use the browser's Print. Zero install — the only dependency is a
browser with network access for the one CDN script (pin below).

    uv run ${CLAUDE_SKILL_DIR}/mmd2html.py docs/architecture.mmd               # -> docs/architecture.html
    uv run ${CLAUDE_SKILL_DIR}/mmd2html.py docs/architecture.mmd --out /tmp/a.html --title "Timeline"

Heavier alternative (offline, raster/vector from CLI, pulls a headless Chromium):
    npx @mermaid-js/mermaid-cli -i docs/architecture.mmd -o docs/architecture.svg
"""
import argparse
import html
import pathlib

import _paths

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>{title}</title>
<style>
 body{{margin:0;background:#0e1119;color:#cdd6e8;font:14px/1.4 system-ui,sans-serif}}
 header{{padding:10px 16px;border-bottom:1px solid #2a3145;display:flex;gap:10px;align-items:center}}
 header h1{{font-size:15px;margin:0;font-weight:600;flex:1}}
 button{{background:#2b3550;color:#dfe6f5;border:1px solid #5a6a8a;border-radius:5px;
   padding:5px 11px;cursor:pointer;font-size:13px}}
 button:hover{{background:#3a4663}}
 #wrap{{padding:20px;overflow:auto}}
 .mermaid{{background:transparent}}
</style></head><body>
<header><h1>{title}</h1>
  <button id="svg">Download SVG</button>
  <button id="png">Download PNG</button>
  <span style="color:#6a7490;font-size:12px">PDF → browser Print</span>
</header>
<div id="wrap"><pre class="mermaid">{src}</pre></div>
<script type="module">
import mermaid from "{cdn}";
mermaid.initialize({{startOnLoad:true, theme:"dark",
  themeVariables:{{fontFamily:"system-ui,sans-serif"}}}});
await mermaid.run();
const svgEl = () => document.querySelector("#wrap svg");
const dl = (blob, name) => {{
  const a=document.createElement("a"); a.href=URL.createObjectURL(blob);
  a.download=name; a.click(); URL.revokeObjectURL(a.href);
}};
document.getElementById("svg").onclick = () =>
  dl(new Blob([new XMLSerializer().serializeToString(svgEl())],
     {{type:"image/svg+xml"}}), "{stem}.svg");
document.getElementById("png").onclick = () => {{
  const svg=svgEl(), xml=new XMLSerializer().serializeToString(svg);
  const img=new Image(), b=svg.getBoundingClientRect(), sc=2;
  img.onload = () => {{
    const c=document.createElement("canvas");
    c.width=b.width*sc; c.height=b.height*sc;
    const x=c.getContext("2d"); x.scale(sc,sc); x.drawImage(img,0,0);
    c.toBlob(bl => dl(bl, "{stem}.png"));
  }};
  img.src="data:image/svg+xml;base64,"+btoa(unescape(encodeURIComponent(xml)));
}};
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mmd", help="Mermaid source (.mmd)")
    ap.add_argument("--out", help="output .html (default: working diagrams/ dir)")
    ap.add_argument("--title", help="page title (default: the .mmd stem)")
    a = ap.parse_args()
    src = pathlib.Path(a.mmd)
    out = pathlib.Path(a.out) if a.out else pathlib.Path(_paths.diagram(src.stem + ".html"))
    title = a.title or src.stem
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(PAGE.format(title=html.escape(title), stem=src.stem,
                               src=html.escape(src.read_text()), cdn=MERMAID_CDN))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

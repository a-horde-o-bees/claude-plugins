// continuous-list-blank — no blank line between two same-indent list items.
// Interrupter exemption: a heading or blockquote (or any non-blank content)
// between the items legitimately separates them, so only runs of pure blank
// lines directly between same-indent items are flagged. Auto-fixable (delete).
module.exports = {
  names: ["continuous-list-blank"],
  description: "Blank line between same-indent list items in a continuous list",
  tags: ["bullet", "ul", "ol", "blank_lines"],
  parser: "none",
  function: (params, onError) => {
    const lines = params.lines;
    const isBlank = (l) => /^\s*$/.test(l);
    const isFence = (l) => /^\s{0,3}(```+|~~~+)/.test(l);
    const itemIndent = (l) => {
      const m = /^(\s*)(?:[-*+]|\d+[.)])\s/.exec(l);
      return m ? m[1].length : null;
    };
    let inFence = false;
    for (let i = 0; i < lines.length; i++) {
      if (isFence(lines[i])) { inFence = !inFence; continue; }
      if (inFence) continue;
      const indent = itemIndent(lines[i]);
      if (indent === null) continue;
      // gather the run of blank lines immediately following this item
      let j = i + 1;
      while (j < lines.length && isBlank(lines[j])) j++;
      if (j === i + 1) continue; // no blank gap
      if (j >= lines.length || isFence(lines[j])) continue;
      // the next non-blank must be a same-indent item, with only blanks between
      if (itemIndent(lines[j]) === indent) {
        for (let b = i + 1; b < j; b++) {
          onError({
            lineNumber: b + 1,
            detail: "Remove the blank line between continuous list items",
            fixInfo: { deleteCount: -1 },
          });
        }
      }
    }
  },
};

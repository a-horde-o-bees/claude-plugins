// fence-body-boundary-blank — no blank line immediately inside a fenced code
// block's boundaries: not right after the opening fence, not right before the
// closing fence. Auto-fixable (delete the boundary blank).
module.exports = {
  names: ["fence-body-boundary-blank"],
  description: "Blank line at the start or end of a fenced code block body",
  tags: ["code", "blank_lines"],
  parser: "none",
  function: (params, onError) => {
    const lines = params.lines;
    const isBlank = (l) => /^\s*$/.test(l);
    const isFence = (l) => /^\s{0,3}(```+|~~~+)/.test(l);
    let inFence = false;
    for (let i = 0; i < lines.length; i++) {
      if (!isFence(lines[i])) continue;
      if (!inFence) {
        // opening fence — flag a blank on the next line
        if (i + 1 < lines.length && isBlank(lines[i + 1])) {
          onError({
            lineNumber: i + 2,
            detail: "Remove the blank line at the start of the fenced block",
            fixInfo: { deleteCount: -1 },
          });
        }
        inFence = true;
      } else {
        // closing fence — flag a blank on the previous line
        if (i - 1 >= 0 && isBlank(lines[i - 1])) {
          onError({
            lineNumber: i,
            detail: "Remove the blank line at the end of the fenced block",
            fixInfo: { deleteCount: -1 },
          });
        }
        inFence = false;
      }
    }
  },
};

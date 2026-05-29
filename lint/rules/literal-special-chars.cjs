// literal-special-chars — characters a renderer may interpret as markup
// should sit inside code when used literally. Limited to { } < > : these
// read as template variables or HTML. Emphasis markers (* _) are excluded
// because a linter cannot tell literal use from intended emphasis. Warn-level.
module.exports = {
  names: ["literal-special-chars"],
  description: "Literal { } < > outside code — wrap in backticks if not markup",
  tags: ["code"],
  parser: "none",
  function: (params, onError) => {
    const lines = params.lines;
    const isFence = (l) => /^\s{0,3}(```+|~~~+)/.test(l);
    let inFence = false;
    for (let i = 0; i < lines.length; i++) {
      if (isFence(lines[i])) { inFence = !inFence; continue; }
      if (inFence) continue;
      const stripped = lines[i].replace(/(`+)[^`]*\1/g, "");
      if (/[{}<>]/.test(stripped)) {
        onError({
          lineNumber: i + 1,
          detail: "Wrap literal { } < > in backticks if not intended as markup",
          context: lines[i].slice(0, 40),
        });
      }
    }
  },
};

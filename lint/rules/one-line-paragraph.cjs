// one-line-paragraph — paragraphs are a single source line; no manual hard-wrapping.
// Two consecutive lines that both render as paragraph text mean a wrapped
// paragraph: join them, or separate them with a blank line.
module.exports = {
  names: ["one-line-paragraph"],
  description: "Paragraph spans multiple source lines (manual hard-wrapping)",
  tags: ["whitespace", "paragraphs"],
  parser: "none",
  function: (params, onError) => {
    const lines = params.lines;
    const isBlank = (l) => /^\s*$/.test(l);
    const isFence = (l) => /^\s{0,3}(```+|~~~+)/.test(l);
    const isParagraphLine = (l) => {
      if (isBlank(l)) return false;
      if (/^(\t| {4,})/.test(l)) return false;            // indented code
      const t = l.replace(/^\s+/, "");
      if (/^#{1,6}\s/.test(t)) return false;              // ATX heading
      if (/^>/.test(t)) return false;                     // blockquote
      if (/^([-*+])\s/.test(t)) return false;             // bullet list item
      if (/^\d+[.)]\s/.test(t)) return false;             // ordered list item
      if (/^\|/.test(t)) return false;                    // table row (leading pipe)
      if (/^[-=]{3,}\s*$/.test(t)) return false;          // setext underline / hr
      if (/^([*_-]\s*){3,}$/.test(t)) return false;       // thematic break
      if (/^<\/?[a-zA-Z!]/.test(t)) return false;         // html block
      return true;
    };
    let inFence = false;
    for (let i = 0; i < lines.length; i++) {
      if (isFence(lines[i])) { inFence = !inFence; continue; }
      if (inFence) continue;
      if (i > 0 && isParagraphLine(lines[i]) && isParagraphLine(lines[i - 1])) {
        onError({
          lineNumber: i + 1,
          detail: "Join with the previous line, or separate the paragraphs with a blank line",
          context: lines[i].slice(0, 40),
        });
      }
    }
  },
};

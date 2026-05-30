// heading-names-file — the level-1 heading names the file it opens.
// For container filenames (SKILL.md), the parent folder is the name.
// Descriptive container files (README, criteria, ...) carry titles that
// needn't match a filename, so they are skipped. Warn-level: the match is
// normalized and lenient, not a hard gate.
const path = require("path");

const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "");
const SKIP = new Set([
  "readme", "index", "criteria", "composition",
  "changelog", "architecture", "tasks", "license",
]);

module.exports = {
  names: ["heading-names-file"],
  description: "Level-1 heading does not name the file",
  tags: ["headings"],
  parser: "none",
  function: (params, onError) => {
    const lines = params.lines;
    const idx = lines.findIndex((l) => !/^\s*$/.test(l));
    if (idx < 0) return;
    const m = /^#\s+(.+?)\s*#*\s*$/.exec(lines[idx]);
    if (!m) return; // missing H1 is MD041's job
    const heading = m[1];

    const stem = path.basename(params.name).replace(/\.md$/i, "");
    let expected;
    if (stem.toLowerCase() === "skill") {
      expected = path.basename(path.dirname(params.name));
      if (!expected || expected === ".") return;
    } else if (SKIP.has(stem.toLowerCase())) {
      return;
    } else {
      expected = stem;
    }

    const h = norm(heading);
    const e = norm(expected);
    if (!h.includes(e) && !e.includes(h)) {
      onError({
        lineNumber: idx + 1,
        detail: `Heading "${heading}" does not name "${expected}"`,
      });
    }
  },
};

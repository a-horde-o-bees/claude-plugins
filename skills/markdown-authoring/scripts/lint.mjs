#!/usr/bin/env node
// On-demand markdown linter. Realizes ../lint-spec.md.
// Usage: node lint.mjs <file|dir|glob> ...   Exit: 0 clean or warns only, 1 errors, 2 usage/IO.
// Severity overrides: nearest .claude/markdown-lint.json at or above a linted file maps
// rule id -> "off" | "warn" | "error" (see ../lint-spec.md § Severity overrides).
import { readFileSync, readdirSync, statSync, globSync } from "node:fs";
import { join, basename, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

let applyOverrides = true; // --self-test disables overrides

const targets = process.argv.slice(2);
if (targets.length === 0) {
  console.error("usage: lint.mjs <file|dir|glob> ... | --self-test");
  process.exit(2);
}

function collect(target) {
  let st = null;
  try { st = statSync(target); } catch {}
  if (!st && /[*?[]/.test(target)) return globSync(target).flatMap(collect);
  if (!st) {
    console.error(`lint.mjs: no such path: ${target}`);
    process.exitCode = 2;
    return [];
  }
  if (st.isDirectory()) {
    return readdirSync(target, { withFileTypes: true })
      .filter((e) => !e.name.startsWith(".") && e.name !== "node_modules")
      .flatMap((e) =>
        e.isDirectory() ? collect(join(target, e.name))
        : /\.md$/i.test(e.name) ? [join(target, e.name)]
        : []
      );
  }
  return [target];
}

const RULES = new Set(["opening-heading", "heading-names-file", "blanks-around", "one-line-items",
  "one-line-paragraphs", "continuous-list", "fence-padding", "list-indent", "escape-special"]);

// Nearest-ancestor .claude/markdown-lint.json, cached per directory.
const overridesCache = new Map();
function findOverrides(dir) {
  if (overridesCache.has(dir)) return overridesCache.get(dir);
  const probe = join(dir, ".claude", "markdown-lint.json");
  let raw = null, result;
  try { raw = readFileSync(probe, "utf8"); } catch {}
  if (raw !== null) {
    try {
      result = JSON.parse(raw);
      for (const [k, v] of Object.entries(result)) {
        if (!RULES.has(k)) console.error(`lint.mjs: ${probe}: unknown rule "${k}"`);
        else if (!["off", "warn", "error"].includes(v)) {
          console.error(`lint.mjs: ${probe}: "${k}": invalid level "${v}" — use off|warn|error`);
          delete result[k];
        }
      }
    } catch {
      console.error(`lint.mjs: ${probe}: invalid JSON — ignored`);
      result = {};
    }
  } else {
    const parent = dirname(dir);
    result = parent === dir ? {} : findOverrides(parent);
  }
  overridesCache.set(dir, result);
  return result;
}

const BLANK = "blank", FM = "frontmatter", FENCE = "code", HEADING = "heading",
  LIST = "list", TABLE = "table", QUOTE = "blockquote", HR = "horizontal-rule", PARA = "paragraph";

// types[i]: element type per line; meta[i]: "fence-open"/"fence-close", or indent string for LIST
function classify(lines) {
  const types = new Array(lines.length);
  const meta = new Array(lines.length);
  let i = 0;
  if (/^---\s*$/.test(lines[0] ?? "")) {
    let j = 1;
    while (j < lines.length && !/^(---|\.\.\.)\s*$/.test(lines[j])) j++;
    if (j < lines.length) {
      for (let k = 0; k <= j; k++) types[k] = FM;
      i = j + 1;
    }
  }
  let fence = null; // { char, len }
  for (; i < lines.length; i++) {
    const line = lines[i];
    if (fence) {
      types[i] = FENCE;
      const m = line.match(/^\s*(`{3,}|~{3,})\s*$/);
      if (m && m[1][0] === fence.char && m[1].length >= fence.len) {
        meta[i] = "fence-close";
        fence = null;
      }
      continue;
    }
    let m;
    if (/^\s*$/.test(line)) types[i] = BLANK;
    else if ((m = line.match(/^\s*(`{3,}|~{3,})(.*)$/)) && !m[2].includes(m[1][0])) {
      types[i] = FENCE;
      meta[i] = "fence-open";
      fence = { char: m[1][0], len: m[1].length };
    } else if (/^ {0,3}#{1,6}\s/.test(line)) types[i] = HEADING;
    else if (/^\s*>/.test(line)) types[i] = QUOTE;
    else if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) types[i] = HR;
    else if ((m = line.match(/^(\s*)(?:[-*+]|\d{1,9}[.)])(?:\s|$)/))) {
      types[i] = LIST;
      meta[i] = m[1];
    } else if (/^\s*\|/.test(line)) types[i] = TABLE;
    else types[i] = PARA;
  }
  return { types, meta };
}

function lintFile(path) {
  const problems = [];
  const add = (line, level, rule, msg) => problems.push({ line, level, rule, msg });
  let src;
  try {
    src = readFileSync(path, "utf8");
  } catch {
    console.error(`lint.mjs: cannot read ${path}`);
    process.exitCode = 2;
    return [];
  }
  const lines = src.split("\n");
  const { types, meta } = classify(lines);
  const content = (i) => i >= 0 && i < lines.length && types[i] !== BLANK && types[i] !== FM;
  const blankRaw = (i) => /^\s*$/.test(lines[i] ?? "");

  // opening heading: first content line is an H1
  const first = types.findIndex((_, i) => content(i));
  if (first === -1) add(1, "error", "opening-heading", "file has no content");
  else if (!/^# /.test(lines[first]))
    add(first + 1, "error", "opening-heading", "first content line must be a level-1 heading");

  // heading names the file (lenient; SKILL.md -> parent folder; README/CLAUDE.md skipped)
  const name = basename(path);
  if (!/^(readme|claude\.md)/i.test(name)) {
    const h1 = types.findIndex((t, i) => t === HEADING && /^# /.test(lines[i]));
    if (h1 !== -1) {
      const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "");
      const stem = name.toLowerCase() === "skill.md" ? basename(dirname(path)) : name.replace(/\.md$/i, "");
      const headingText = lines[h1].replace(/^#\s*/, "").trim();
      const got = norm(headingText);
      // lenient: every token of the filename appears somewhere in the heading
      const tokens = stem.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
      if (got && tokens.length && !tokens.every((t) => got.includes(t)))
        add(h1 + 1, "warn", "heading-names-file", `heading "${headingText}" does not name the file ("${name}")`);
    }
  }

  for (let i = 0; i + 1 < lines.length; i++) {
    if (!content(i) || !content(i + 1)) continue;
    const a = types[i], b = types[i + 1];
    if (a === FENCE || b === FENCE) {
      // fence interiors are one element; only a boundary adjacent to a different element violates
      if ((meta[i] === "fence-close" && b !== FENCE) || (meta[i + 1] === "fence-open" && a !== FENCE))
        add(i + 2, "error", "blanks-around", `blank line required between ${a} and ${b}`);
      continue;
    }
    if (a !== b) {
      if (a === LIST && b === PARA)
        add(i + 2, "error", "one-line-items", "content wraps under a list item — one item per source line");
      else add(i + 2, "error", "blanks-around", `blank line required between ${a} and ${b}`);
    } else if (a === PARA && types[i - 1] !== PARA) {
      add(i + 2, "error", "one-line-paragraphs", "paragraph wraps across source lines — each paragraph is one line");
    }
  }

  // continuous list: same-indent items with only blanks between stay adjacent
  for (let i = 0; i < lines.length; i++) {
    if (types[i] !== LIST) continue;
    let j = i + 1;
    while (j < lines.length && types[j] === BLANK) j++;
    if (j > i + 1 && types[j] === LIST && meta[j] === meta[i])
      add(j + 1, "error", "continuous-list", "blank line splits a continuous list — same-indent items stay adjacent");
  }

  // no blank padding just inside fences
  for (let i = 0; i < lines.length; i++) {
    if (meta[i] === "fence-open" && meta[i + 1] !== "fence-close" && blankRaw(i + 1))
      add(i + 2, "error", "fence-padding", "blank line immediately after opening fence");
    if (meta[i] === "fence-close" && meta[i - 1] !== "fence-open" && blankRaw(i - 1))
      add(i, "error", "fence-padding", "blank line immediately before closing fence");
  }

  // list indentation: spaces only, multiples of 4
  for (let i = 0; i < lines.length; i++) {
    if (types[i] !== LIST) continue;
    const ind = meta[i];
    if (/\t/.test(ind)) add(i + 1, "error", "list-indent", "tab in list indentation — use spaces");
    else if (ind.length % 4 !== 0)
      add(i + 1, "error", "list-indent", `list indent of ${ind.length} — nested lists indent 4 spaces per level`);
  }

  // literal {} <> outside code (warn)
  for (let i = 0; i < lines.length; i++) {
    if (types[i] !== PARA && types[i] !== LIST && types[i] !== TABLE) continue;
    const stripped = lines[i]
      .replace(/``.*?``/g, "")
      .replace(/`[^`]*`/g, "")
      .replace(/<!--.*?-->/g, "")
      .replace(/<[a-zA-Z][a-zA-Z0-9+.-]*:[^\s>]*>/g, "")
      .replace(/<[^\s>]+@[^\s>]+>/g, "");
    const found = [...new Set(stripped.match(/[{}<>]/g) || [])];
    if (found.length)
      add(i + 1, "warn", "escape-special", `literal ${found.join(" ")} outside code — backtick if literal`);
  }

  const overrides = applyOverrides ? findOverrides(dirname(resolve(path))) : {};
  return problems.flatMap((p) => {
    const level = overrides[p.rule];
    if (level === "off") return [];
    return [level ? { ...p, level } : p];
  });
}

// Self-test: lint the bundled fixtures, compare against expected.txt exactly.
if (targets[0] === "--self-test") {
  applyOverrides = false;
  const dir = join(dirname(fileURLToPath(import.meta.url)), "..", ".fixtures");
  const fmt = (f) =>
    lintFile(join(dir, f)).sort((x, y) => x.line - y.line).map((p) => `${f}:${p.line} ${p.level} ${p.rule}`);
  const got = [...fmt("violations.md"), ...fmt("clean.md")].join("\n");
  const expected = readFileSync(join(dir, "expected.txt"), "utf8").trim();
  if (got === expected) {
    console.log(`self-test OK: findings match ${join(dir, "expected.txt")}`);
    process.exit(0);
  }
  console.error("self-test FAILED\n--- expected ---\n" + expected + "\n--- got ---\n" + got);
  process.exit(1);
}

const files = [...new Set(targets.flatMap(collect))];
let errors = 0, warns = 0;
for (const f of files) {
  for (const p of lintFile(f).sort((x, y) => x.line - y.line)) {
    console.log(`${f}:${p.line} [${p.level}] ${p.rule} — ${p.msg}`);
    p.level === "error" ? errors++ : warns++;
  }
}
console.log(`${files.length} file(s): ${errors} error(s), ${warns} warning(s)`);
if (errors) process.exitCode = 1;

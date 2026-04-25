# Anti-Pattern Allowlist

Detect a structural anti-pattern across a codebase while exempting the small set of files whose job is the pattern (entry points, anchors, registries). Exemptions live in a sidecar table — `(rule, glob, reason)` — so they are centralized, auditable, and resist silent growth. The rule's CLI surfaces suppressed entries via an audit flag, and new entries are forced to carry a `reason` so exemption pressure stays visible.

## Why this shape

Strict lints with no escape hatch break in real codebases — every project has a small set of files whose job is to do the thing the lint forbids. Plugin entry points anchor with `Path(__file__)`. Pytest fixtures sit at conftest. Test-fixture files contain anti-pattern source by design. Without exemptions, the lint becomes a friction tax users learn to bypass.

Per-line `# noqa: <rule>` works for sparse, scattered exemptions but fails at scale: entries get added inline without rationale, drift across files, and never get audited. A sidecar table groups exemptions by rule, makes review a one-file diff, and forces every entry to declare its reason.

## Pattern

```
1. {rule_id} = the anti-pattern's stable name (e.g., "Python - parent-walking")
2. {detector} = AST/regex/glob scan that returns Violations with `(rule, path, line, snippet)`

> The detector is rule-pure. It does not read or apply the allowlist.
> Filtering happens at the CLI/orchestrator layer so library callers
> can choose strict mode (raw violations) or filtered mode.

3. {allowlist_csv} = sidecar file next to the rule's implementation
    - Schema: `rule, pattern, reason`
    - `rule` matches Violation.rule exactly, OR `*` for cross-rule exemptions (e.g., test fixtures)
    - `pattern` is fnmatch glob against project-relative posix path
    - `reason` is prose; surfaced via --show-allowed; new entries must populate

4. {load} = parse {allowlist_csv} into AllowlistEntry list at CLI startup
5. {filter} = partition Violations into (kept, suppressed) by matching (rule, path) against entries
6. {report}:
    - Print kept violations with file:line:rule:snippet
    - If --show-allowed: print suppressed entries too, with `reason`
    - Exit 1 only when kept is non-empty (suppressed alone never blocks)

> Audit flag is the discipline. Without --show-allowed, the user can
> never tell a clean run from a heavily-allowlisted run. With it, the
> exemption set is visible on demand and reviewable on every PR.
```

## Sidecar table shape

```csv
rule,pattern,reason
Python - parent-walking,**/conftest.py,Pytest fixture anchor — legitimate base for test discovery
Python - parent-walking,plugins/*/run.py,Plugin CLI entry-point dispatcher; the blessed plugin-root anchor
*,**/fixture_*.*,Scanner test fixtures — files whose content is deliberate anti-pattern input across every dimension
```

The `*` wildcard in `rule` is the cross-dimension exemption — file-level exempt regardless of which rule fires. Use sparingly; reserved for content that is *inherently* exempt (test fixtures, generated code, vendored sources).

## When to use

- Structural lint with a small, named set of legitimate exceptions whose role is well-defined
- The exception class is *file-level*, not *line-level* (the file's job IS the pattern)
- The exception set is bounded and slow-changing (you can name the entries; they don't grow weekly)
- Entry rationale is non-obvious without context (`reason` carries real information, not just a marker)

## When NOT to use

- The exception class is fuzzy or unbounded — if every commit adds an exemption, the rule itself is the wrong rule
- Exceptions are line-level decisions inside otherwise-clean files — use `# noqa: <rule>` per line instead, or restructure the rule to be more precise
- The lint already has a precise scope that doesn't need exemptions (e.g., "no `eval` anywhere" is absolute)
- One rule has an order-of-magnitude more exemptions than violations — the rule isn't carrying weight, retire it

## Anti-patterns this prevents

- **Silent allowlist growth.** Per-line `# noqa: <rule>` accumulates without review. Sidecar table makes every addition a diff against one file with a `reason` column.
- **Detector + filter conflation.** A detector that knows about exemptions can't be tested for raw correctness — every test has to consider the live allowlist. Keeping the detector pure and filtering at the CLI layer keeps unit tests honest.
- **Hidden exemption count.** Without `--show-allowed`, a clean exit hides 50 suppressions just as easily as 0. The audit flag is non-optional infrastructure, not a debug feature.
- **Coupled rules.** A single allowlist file with `(rule, pattern, reason)` columns lets multiple rules coexist without naming-collision or per-rule sidecar fragmentation. New rules slot in with new rows.

## See also

- `logs/decision/check.md` — concrete application of this pattern to the parent-walking lint
- `plugins/ocd/systems/check/allowlist.csv` — the live exemption table
- `plugins/ocd/systems/check/_allowlist.py` — the loader/filter implementation

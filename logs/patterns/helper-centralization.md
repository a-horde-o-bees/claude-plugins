# Helper Centralization

When two or more systems duplicate orchestration logic, extract the orchestration into a shared `tools.*` helper that mirrors an existing helper pattern. The system shrinks to declaration; the helper owns resolution.

## When to use

The trigger is two or more systems' entry points sharing the same multi-step flow with only declarative differences (paths, names, schemas). Each new system arrival re-writes the same flow.

The shape that signals extraction is ready: existing helpers cover *primitives* (read this, compare those, write that) but not the *orchestration* of those primitives. Systems compose primitives directly, duplicating the orchestration.

## Process

1. **Identify the existing analog.** The codebase usually has a helper that solves the same shape in a different domain. For file-based systems the analog is `setup.deploy_files(src_dir, dst_dir, pattern, force, keep_orphans)` — system declares src+dst, helper resolves compare-before-write + orphan removal. The new helper should mirror this shape.
2. **Move orchestration into tools.\*; keep declaration in the system.** Each system passes a small bundle: location identifiers (paths) + behavioral hooks (callables that produce the canonical state). The helper takes `(where, what, force)` and returns the file-entries result.
3. **Cache deterministic computations at the helper layer.** If the helper repeatedly produces the same canonical artifact (e.g., a fresh empty DB to compare against), memoize via `@functools.cache` keyed on the schema-builder identity. Eliminates redundant work across calls within a process.
4. **Auto-init simplifies as a consequence.** When systems own their orchestration through the centralized helper, auto-init drops layered safety nets (e.g., pre-sync backup-restore) — the discipline lives in the helper, not in the orchestrator.

## Worked example

DB-backed systems went from ~30-line `_init.py` orchestration each (needs_map, navigator) to ~5 lines of declaration + helper composition. The orchestration now lives in `tools.db.rectify` and `tools.db.reset_db`. Auto-init dropped the project-level pre-sync mechanism — `scripts/auto_init.py` shed ~70 lines.

The path the session took:

1. Two systems duplicating orchestration was the trigger
2. User framed the convergence: "deploy_files() is a helper that each system can call — the system defines what needs to be deployed and where it belongs, the helper resolves filetype handling and clearing the destination directory on `--force`"
3. Mirror call shape: `rectify(db_path, schema_builder, rel_path, force)` ↔ `deploy_files(src_dir, dst_dir, pattern, force)`
4. Each system's init shrinks to declarative composition

## Pitfalls

- **Asymmetric primitives.** If existing helpers expose `compare()` but not `write_backup()`, the new helper's API will inherit the asymmetry. Audit the primitives before extracting orchestration; backfill missing primitives first so the helper signature stays clean.
- **Hidden coupling on caller invariants.** Each system's pre-extraction orchestration may rely on caller-side invariants (e.g., "we always re-scan after init"). Name those explicitly during extraction; either bake them into the helper or document them at call sites. Otherwise the helper looks complete but its contract is leaky.

## Anti-patterns

- **Speculative extraction.** Extracting orchestration *before* a second system needs it produces premature abstractions. Wait for the second instance — the YAGNI bar is three concrete cases for a generic, but two duplicating the same orchestration is enough to trigger this pattern.
- **Flag explosion at the helper.** When extending the helper to a third system tempts a new flag (`--special-mode-for-system-N`), step back: either the helper's contract has shifted (rename and migrate), or system N needs a sibling helper, not a flag.

## See also

- `logs/decision/database.md` *Schema-aware init contract via tools.db.rectify* — the decision that produced the worked example
- The base case: `setup.deploy_files` for file-deploying systems
- `plugins/ocd/systems/rules/templates/design-principles.md` *Borrow Before Build* — the umbrella principle; the case bullet "When two or more systems duplicate orchestration of existing primitives: extract the orchestration into a shared helper that mirrors the closest existing helper pattern" is the trigger form of this pattern's process

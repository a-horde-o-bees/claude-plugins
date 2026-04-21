# docs-plugin-dependencies

**URL**: https://code.claude.com/docs/en/plugin-dependencies
**Type**: Official Claude Code documentation
**Authority**: Official — authoritative for plugin-to-plugin dependency schema, version constraint syntax, and tag resolution convention.

**Version floor**: requires Claude Code v2.1.110 or later.

## Scope

Plugin-to-plugin dependency declarations: `dependencies` array in plugin.json, semver range syntax, cross-marketplace references, the `{plugin-name}--v{version}` git tag convention, and conflict resolution.

## Key prescriptions

### Dependency declaration

```json
{
  "name": "deploy-kit",
  "version": "3.1.0",
  "dependencies": [
    "audit-logger",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}
```

Entry forms:

- Bare string (`"audit-logger"`) — unversioned, tracks whatever the marketplace provides.
- Object with `name` (required), `version` (optional semver range), `marketplace` (optional, for cross-marketplace).

### Semver range syntax

Any node-semver expression: `~2.1.0`, `^2.0`, `>=1.4`, `=2.1.0`, pre-release `^2.0.0-0`.

Pre-release versions (e.g. `2.0.0-beta.1`) are **excluded unless the range opts in** with a pre-release suffix.

### Cross-marketplace dependencies

- `marketplace` field lets dependency resolve in a different marketplace.
- **Blocked by default** — the target marketplace must be allowlisted in the declaring marketplace's `marketplace.json`.

### Tag resolution convention

**Version resolution requires git tags formatted as `{plugin-name}--v{version}`** on the marketplace repository.

```bash
git tag secrets-vault--v2.1.0
git push origin secrets-vault--v2.1.0
```

- The plugin name prefix enables one marketplace to host multiple plugins with independent version lines.
- The `--v` separator is parsed as a prefix match — plugin names containing hyphens work.
- Claude Code lists all marketplace tags, filters by prefix, fetches highest satisfying tag.
- If no tag matches, dependent plugin is disabled with an error listing available versions.

### npm marketplace sources

For `npm` plugin source, tag-based resolution does not apply. The version constraint is still checked at load time; plugin is disabled with `dependency-version-unsatisfied` if installed version doesn't satisfy it.

### Constraint interaction

When multiple plugins constrain the same dependency, Claude Code intersects ranges and resolves to highest satisfying version.

Example outcomes:

| Plugin A requires | Plugin B requires | Result |
|---|---|---|
| `^2.0` | `>=2.1` | One install at highest `2.x` tag ≥ `2.1.0`. Both load. |
| `~2.1` | `~3.0` | Plugin B install fails with `range-conflict`. Plugin A and dependency unchanged. |
| `=2.1.0` | none | Dependency stays at `2.1.0`. Auto-update skips newer versions while Plugin A installed. |

### Error codes

- `range-conflict` — no version satisfies all ranges, invalid semver, or too complex to intersect.
- `dependency-version-unsatisfied` — installed version outside declared range.
- `no-matching-tag` — no `{name}--v*` tag satisfies range.

Surfaced in `claude plugin list`, `/plugin`, `/doctor`. Affected plugin disabled until resolved.

### Auto-update

Auto-update checks each constrained dependency against every installed plugin's range before applying. If marketplace moves a dependency outside any range, update is skipped and skip message names the constraining plugin.

When the last plugin constraining a dependency is uninstalled, the dependency resumes tracking its marketplace entry on the next update.

## Use for

- Resolving how a plugin declares cross-plugin dependencies.
- Verifying the `{plugin-name}--v{version}` tag format.
- Understanding version resolution when multiple plugins constrain the same dependency.
- Identifying the three error codes (`range-conflict`, `dependency-version-unsatisfied`, `no-matching-tag`) and their causes.
- Confirming the v2.1.110+ version floor.

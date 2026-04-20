# Claude Marketplace

Canonical shape for a Claude Code plugin marketplace repository. Use this pattern when starting any repo that publishes one or more Claude Code plugins — it captures the directory layout, versioning, branch model, release channels, CI, and release automation as a single coherent design. Aligned with the dominant conventions in well-maintained Claude plugin repos (superpowers-style single-author monorepo; Anthropic-style curated catalog is noted as an adaptation).

## When to use

- **This pattern** — a repository you own that publishes one or more Claude Code plugins you maintain. Marketplace is a thin wrapper that lets users subscribe and auto-update.
- **Adaptation: single-plugin repo** — drop the `plugins/` wrapper; the plugin lives at the repo root. See *Adaptations*.
- **Adaptation: curated third-party catalog** (like `anthropics/claude-plugins-official`) — plugin dirs hold only manifest metadata, actual plugin source is pinned to external repos via `github` / `url` / `git-subdir` sources with `ref` + `sha` pinning and scheduled auto-bump PRs. Different discipline (see *Adaptations*).
- **Not for MCP-only repos** — standalone MCP servers distribute via npm or PyPI, not through the plugin marketplace. If you wrap an MCP server in a plugin, the plugin repo follows this pattern and references the MCP package via `mcpServers` config.

## Repository structure

```text
my-marketplace/
├── .claude-plugin/
│   ├── marketplace.json              # Dev channel (plugin source → ref: main)
│   └── marketplace.stable.json       # Stable channel (plugin source → ref: vX.Y.Z)
├── plugins/
│   ├── <plugin-a>/                   # Plugin dir ships to user cache as-is
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json           # Plugin manifest — version authority
│   │   ├── skills/ commands/ agents/ hooks/ bin/
│   │   ├── .mcp.json .lsp.json       # If applicable
│   │   ├── requirements.txt          # Runtime deps (SessionStart hook reads)
│   │   ├── README.md LICENSE
│   │   └── architecture.md           # Plugin-level design (dev-facing; acceptable noise)
│   └── <plugin-b>/…
├── tests/                            # ALL tests — project + per-plugin — at repo root
│   ├── integration/                  # Marketplace-level integration
│   ├── unit/                         # Project-level unit tests
│   └── plugins/
│       ├── <plugin-a>/
│       │   ├── unit/
│       │   └── integration/
│       └── <plugin-b>/…
├── scripts/                          # Dev tooling
│   ├── test.sh                       # Delegates to the plugin framework's test runner
│   ├── release.sh                    # Cuts release branch + tag
│   └── validate.sh                   # Optional local validate before PR
├── .github/
│   └── workflows/
│       ├── validate.yml              # Marketplace + plugin manifests + frontmatter
│       └── test.yml                  # Full test suite
├── .gitignore                        # Excludes .venv/, __pycache__/, plugin data, etc.
├── .claude/                          # Dev-only agent config for working in this repo
│   ├── settings.json                 # Committed project settings
│   ├── settings.local.json           # gitignored — per-user overrides
│   ├── rules/ conventions/ patterns/ # Deployed copies — gitignored; regenerated
│   └── logs/                         # Committed decision / idea / problem / friction entries
├── README.md                         # User-facing: install commands for each channel
├── CHANGELOG.md                      # Updated on every release cut
├── architecture.md                   # Repo-level technical design
└── CLAUDE.md                         # Agent procedures for working in this repo
```

The core discipline: **plugin dirs contain only files that should ship to the user's cache**. Everything dev-side lives at the repo root. Tests, CI configs, project-wide scripts, dev docs, editor settings — none of these belong inside `plugins/<name>/`. This replaces the file-exclusion manifest that Claude Code does not provide.

## Versioning model

Every plugin declares its version in exactly one place: `plugins/<name>/.claude-plugin/plugin.json`. Never duplicate into marketplace entries. Claude Code's rule is "plugin manifest always wins silently" — duplicate values create drift that cannot be detected at runtime.

**Version space is split by branch:**

- `main` holds `0.0.z` — a monotonic dev build counter bumped automatically by a pre-commit hook on every commit. `main` is never released from directly. The counter exists because Claude Code uses `version` changes to detect that the plugin cache is stale; without it, users on the dev channel would not see updates.
- `release/x.y` branches own real semver (`x.y.z`). Cut from `main` at release time; `x.y.0` is the first release, `x.y.z` tracks patches on that minor line. Main continues its `0.0.z` incrementing unaffected by the release cut.

**Pre-release suffixes** (`-beta.1`, `-rc.1`) are legitimate but unusual in this ecosystem. Prefer a second experimental marketplace over pre-release tags when you need them.

## Branch model

- `main` — dev trunk. Install target for the dev channel. All feature merges land here first.
- `release/x.y` — cut per minor release. Holds the curated release content. Patch releases bump `x.y.z` on this branch.
- Topic branches — `feat/<topic>`, `fix/<topic>`, `<initials>/<topic>`. PR-merged into main. No long-lived `dev` integration branch needed.

Long-lived branches beyond `main` and `release/*` add overhead without benefit at this scale. If a feature needs a prolonged isolation (multiple sessions, crossing other changes), use a sandbox branch that merges back to main via a normal PR.

## Release channels

Two marketplaces, one repo. Users subscribe to whichever channel matches their risk tolerance.

### Dev channel

`.claude-plugin/marketplace.json`:

```json
{
  "name": "<owner>-dev",
  "owner": { "name": "<Owner Name>" },
  "plugins": [
    {
      "name": "<plugin-a>",
      "source": {
        "source": "github",
        "repo": "<owner>/<repo>",
        "ref": "main"
      }
    }
  ]
}
```

Users install via:

```
/plugin marketplace add <owner>/<repo>
/plugin install <plugin-a>@<owner>-dev
```

The `ref: "main"` is explicit — even when the repo's default branch is main, declaring it removes ambiguity and makes the dev/stable split visible at first read.

### Stable channel

`.claude-plugin/marketplace.stable.json`:

```json
{
  "name": "<owner>",
  "owner": { "name": "<Owner Name>" },
  "plugins": [
    {
      "name": "<plugin-a>",
      "source": {
        "source": "github",
        "repo": "<owner>/<repo>",
        "ref": "v1.2.0"
      }
    }
  ]
}
```

Users install via:

```
/plugin marketplace add <owner>/<repo>#.claude-plugin/marketplace.stable.json
/plugin install <plugin-a>@<owner>
```

The stable marketplace entry is updated on every release cut to point at the new tag. `ref: "<tag>"` can be replaced with explicit `sha:` pinning if you need commit-level precision.

### Naming

- Marketplace name (in manifest): the dev channel suffixes with `-dev`; the stable channel holds the unadorned owner name. Reasoning: stable is the default channel new users should land on, dev is the opt-in.
- Reserved marketplace names per Claude Code docs must be avoided: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`.

## Plugin dir discipline

What ships inside `plugins/<name>/` and what stays at repo root:

| File or directory                        | Ships to cache | Location                  |
| :--------------------------------------- | :------------- | :------------------------ |
| `.claude-plugin/plugin.json`             | yes            | plugin dir                |
| `skills/`, `commands/`, `agents/`        | yes            | plugin dir                |
| `hooks/hooks.json`, hook scripts         | yes            | plugin dir                |
| `.mcp.json`, `.lsp.json`                 | yes            | plugin dir                |
| `bin/`                                   | yes            | plugin dir                |
| `requirements.txt` (Python runtime deps) | yes            | plugin dir                |
| `package.json` (Node runtime deps)       | yes            | plugin dir                |
| `README.md`, `LICENSE`                   | yes            | plugin dir                |
| `architecture.md` (plugin-level)         | yes (small)    | plugin dir                |
| `CHANGELOG.md` (plugin-specific)         | yes (small)    | plugin dir (optional)     |
| `tests/`                                 | **no**         | repo root `tests/plugins/<name>/` |
| `conftest.py`, `pytest.ini`              | **no**         | repo root `tests/`        |
| CI workflows                             | **no**         | repo root `.github/`      |
| Dev-only scripts                         | **no**         | repo root `scripts/`      |
| `.claude/` (agent config)                | **no**         | repo root                 |

The cache is the directory name the plugin installs into — `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. Every file under the plugin dir at install time ends up there. Discipline on what belongs where is the entire dev-vs-prod separation mechanism; there is no `.claudeignore`.

## Test organization

All tests live at the repo root in a single `tests/` tree. Per-plugin tests nest under `tests/plugins/<name>/`. Project-wide tests live under `tests/integration/` or `tests/unit/` at the top level.

**Why at the root, not inside plugin dirs:** tests are dev artifacts that would otherwise ship to user caches. Keeping them at the root is the structural equivalent of excluding them from distribution.

**Per-plugin venv isolation:** each plugin's tests run under that plugin's own venv (`~/.claude/plugins/data/<plugin>-<namespace>/venv/`), which matches the runtime environment Claude Code uses in production. Project-level tests run under the project's `.venv/`. The test runner resolves these automatically.

**Agent-spawning tests:** tests that spawn real Claude subprocesses via `claude -p` (validating end-to-end integration with hooks, MCP servers, permissions) are marked `pytestmark = pytest.mark.agent` and gated behind an opt-in flag (`--run-agent` by convention). Agent tests cost tokens; they stay off by default and opt-in per run. See the testing convention for full discipline.

## CI validation

Two workflows at minimum:

### `.github/workflows/validate.yml`

Runs on every PR that touches `.claude-plugin/**`, `plugins/**/.claude-plugin/**`, or `plugins/**/skills/**`. Validates:

- Every `marketplace.json` parses and conforms to the marketplace schema.
- Every `plugin.json` parses and conforms to the plugin manifest schema.
- Every skill, agent, and command has well-formed frontmatter.
- Every `hooks/hooks.json` (if present) parses and matches the hook schema.

Claude Code ships a CLI validator that does most of this: `claude plugin validate .`. Workflow wraps it.

### `.github/workflows/test.yml`

Runs on every PR and on push to `main` / `release/*`:

- Sets up the project venv and each plugin's runtime venv.
- Runs `bash scripts/test.sh` (delegating to the plugin framework's test runner).
- Reports per-suite pass/fail.
- Optionally: gate merges on pass.

Agent tests (`pytest.mark.agent`) stay skipped in CI unless the workflow explicitly opts in with `--run-agent` — doing so requires `ANTHROPIC_API_KEY` as a secret and burns tokens. Consider a separate scheduled workflow for agent tests.

## Release pipeline

`scripts/release.sh x.y.z` cuts a release with one command. It should:

1. Verify working tree is clean and current branch is `main`.
2. Verify `main` is ahead of the most recent release tag (no-op releases get refused).
3. If the release is `x.y.0` (new minor line):
    1. Create branch `release/x.y` at current `main`.
    2. Bump `plugins/*/plugin.json` versions to `x.y.0`.
    3. Prepend an entry to `CHANGELOG.md`.
    4. Update `.claude-plugin/marketplace.stable.json` plugin sources to `ref: "vx.y.0"`.
    5. Commit ("release x.y.0"), tag `vx.y.0`, push branch + tag.
4. If the release is `x.y.z` where `z > 0` (patch on an existing release branch):
    1. Switch to `release/x.y`.
    2. Cherry-pick or merge the fix commits.
    3. Bump `plugin.json` to `x.y.z`, prepend CHANGELOG, tag `vx.y.z`, push.
5. Emit the install command users should run to pick up the release.

Automation beyond a shell script (release-please, changesets, semantic-release) is not standard in this ecosystem. Keep the pipeline legible — someone reading the script should understand the release process without external context.

## Documentation requirements

At the repo root:

- **`README.md`** — user-facing. Opens with install commands for both channels. Covers what each plugin does (one paragraph each), links to `plugins/<name>/README.md` for details, lists dependencies on global tools, and describes the release-channel distinction.
- **`CHANGELOG.md`** — release history. Keep-a-Changelog format. Updated on every release cut, not on every commit.
- **`architecture.md`** — developer-facing. Repo-level layers, how the plugins relate, shared infrastructure, release pipeline summary. References `plugins/<name>/architecture.md` for per-plugin internals without duplicating them.
- **`CLAUDE.md`** — agent procedures for working in this repo. Versioning discipline, branch model, release process, test invocation. Short and operational — architecture belongs in architecture.md.

Each plugin directory:

- **`plugins/<name>/README.md`** — user-facing, plugin-scoped.
- **`plugins/<name>/.claude-plugin/plugin.json`** — manifest.
- **`plugins/<name>/architecture.md`** — plugin-level technical design if non-trivial.
- Plugin-level `CLAUDE.md` only when the plugin has its own agent-facing operational procedures distinct from the repo-level ones.

## Adaptations

### Single-plugin repo

Drop the `plugins/` wrapper. The plugin manifest lives at `.claude-plugin/plugin.json` in the repo root. The marketplace.json plugin source uses `source: "./"` (the plugin is the whole repo).

```
my-plugin-repo/
├── .claude-plugin/
│   ├── plugin.json
│   ├── marketplace.json
│   └── marketplace.stable.json
├── skills/ commands/ agents/ hooks/
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/ .github/
├── requirements.txt
├── README.md CHANGELOG.md architecture.md CLAUDE.md LICENSE
└── …
```

Everything else in this pattern carries over unchanged — versioning, branches, release channels, test root, CI, release pipeline.

### Curated third-party catalog

When the marketplace publishes plugins you do not own (Anthropic's `claude-plugins-official` is the canonical example), plugin dirs hold only metadata and the plugin source fetches from the third-party repo:

```json
{
  "name": "<third-party-plugin>",
  "source": {
    "source": "github",
    "repo": "<third-party-owner>/<third-party-repo>",
    "ref": "<branch-or-tag>",
    "sha": "<40-char-commit-sha>"
  }
}
```

In this mode:

- No code lives under `plugins/<name>/` — it is a metadata-only directory or absent entirely, with the marketplace entry carrying the full definition (`strict: false`).
- A scheduled GitHub Actions workflow (weekly cron) opens a batched PR that bumps `sha` values to the upstream HEAD for each pinned source. Reviewer approves bumps after smoke-testing.
- No `release/*` branches; releases are the SHA-bump PRs themselves.

### MCP-only repo

Standalone MCP servers distribute via npm or PyPI, not through the plugin marketplace. If you also publish a Claude plugin that wraps the MCP server, that plugin is a separate repo using the main pattern; its `.mcp.json` references the MCP package by name:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"]
    }
  }
}
```

MCP server repos follow whatever release conventions are natural to their package ecosystem (npm changelogs, PyPI semver).

## Non-obvious gotchas

- **`version` in both `plugin.json` and marketplace entry**: plugin.json wins silently. Always declare in one place — `plugin.json` for non-relative-path plugins; marketplace entry for relative-path (plugin source `source: "./"` or `"./plugins/<name>"`).
- **Relative-path plugin sources require a git-based marketplace**: if users add the marketplace via a direct URL to `marketplace.json` (not a git clone), relative paths do not resolve. Prefer `github` / `url` / `git-subdir` sources with explicit `ref` pinning so both install paths work.
- **`additionalDirectories` in `permissions`**: accepts literal paths. Globs are not supported. `..` is portable because it resolves against the active project at runtime, so using `..` in either `.claude/settings.json` (project-scope) or `~/.claude/settings.json` (user-scope) is safe for enabling sibling-worktree operations.
- **Plugin cache carries everything in the plugin dir**: there is no server-side filtering, no build step, no `.claudeignore`. Discipline on plugin dir content is enforced only by repo convention.
- **Background auto-updates run without git credentials**: private-repo plugins need `GITHUB_TOKEN` / `GITLAB_TOKEN` / `BITBUCKET_TOKEN` exported in the user's shell for auto-update to succeed. Public repos avoid this entirely.
- **Marketplace state is per-user, not per-worktree**: `~/.claude/plugins/known_marketplaces.json` is global. Switching between worktrees does not isolate marketplace config.
- **Pre-commit version bump**: the `0.0.z` auto-bump on main is a commit hook, not a CI step — skipping hooks (`git commit --no-verify`) silently skips the bump and produces a dev commit Claude Code cannot distinguish from a prior one.

## Checklist for a new marketplace repo

1. Create `.claude-plugin/marketplace.json` with dev-channel manifest.
2. Create `.claude-plugin/marketplace.stable.json` with stable-channel manifest (points at `ref: v0.1.0` initially).
3. Create first plugin under `plugins/<plugin-a>/.claude-plugin/plugin.json`.
4. Initialize `tests/` at repo root with `integration/` and `plugins/<plugin-a>/` subdirs.
5. Add `scripts/test.sh` delegating to the plugin framework's test runner.
6. Add `scripts/release.sh` for release cuts.
7. Add `.github/workflows/validate.yml` and `.github/workflows/test.yml`.
8. Install pre-commit hook for `0.0.z` auto-bump on main.
9. Write `README.md` with dev-channel and stable-channel install commands.
10. Write `CHANGELOG.md` stub.
11. Write `architecture.md` and `CLAUDE.md`.
12. Tag the first stable release (`v0.1.0`), update `marketplace.stable.json` to pin it.
13. Verify: install from both channels on a clean machine; confirm plugin cache contains only intended files.

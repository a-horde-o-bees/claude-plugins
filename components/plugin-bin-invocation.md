# Plugin bin invocation

Each plugin ships a `plugins/<plugin>/bin/<plugin>-run` entry point (`ocd-run`, future `blueprint-run`, …). Two invocation forms coexist in the permission allowlist; pick the one matching what you need to verify.

## Bare name

```
ocd-run <verb>
```

Resolves via `$PATH` to the installed plugin cache (`~/.claude/plugins/cache/<author>/<plugin>/<version>/bin/`). This is whatever was synced at the last `/checkpoint`; edits in the working tree are invisible until the cache refreshes. Allow-listed in user settings (`Bash(<plugin>-run:*)`) because it's stable across sessions and projects.

## Full path

```
plugins/<plugin>/bin/<plugin>-run <verb>
```

Invokes the in-tree copy directly — no cache, edits take effect immediately. Allow-listed in this project's `.claude/settings.json` (`Bash(plugins/<plugin>/bin/<plugin>-run:*)`) because ad-hoc verification of plugin code in this repo must run against the working tree, not the last cached version.

## When to use which

Default to the **full-path form** when validating changes you haven't checkpointed yet. Use the **bare form** when you specifically want to exercise what downstream users have installed.

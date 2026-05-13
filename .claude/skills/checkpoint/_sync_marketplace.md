# Sync (Marketplace)

> Workflow component for `/checkpoint` when `sync_mode` is `marketplace`. Refreshes the project's marketplace cache and runs per-plugin updates for any plugins whose code changed in the commits being pushed.

> Recommends session restart when any plugin was updated — the plugin install is cached and only re-reads at session start.

### Variables

- {pending-paths} — file paths in the commits being pushed (output of `git diff --name-only origin/<branch>..HEAD`)

### Process

1. {changed-plugins}: unique plugin directory names extracted from {pending-paths} matching `^plugins/<name>/` — empty when no path under `plugins/` was touched
2. {marketplace-changed}: true if `.claude-plugin/marketplace.json` is in {pending-paths}; else false

3. If {changed-plugins} is empty AND {marketplace-changed} is false:
    1. Return to caller:
        - Mode: marketplace
        - Status: skipped — no plugin code or marketplace manifest in the push
        - Restart: not needed

4. {marketplace-name}: bash: `uv run python -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['name'])"`
5. Marketplace refresh — bash: `claude plugins marketplace update {marketplace-name}`
6. For each {plugin} in {changed-plugins}:
    1. Update plugin — bash: `claude plugins update {plugin}@{marketplace-name}`

7. Return to caller:
    - Mode: marketplace
    - Status: ran
    - Plugins updated: {changed-plugins}
    - Marketplace refresh trigger: {marketplace-changed} or plugin change in pending paths
    - Restart: recommended (`/exit` then `claude --continue`) — cached plugin install only re-reads at session start

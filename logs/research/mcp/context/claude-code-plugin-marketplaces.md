# Claude Code Plugin Marketplaces

## Identification
- url: https://code.claude.com/docs/en/plugin-marketplaces
- type: host integration docs
- author: Anthropic (Claude Code team)
- last-updated: active
- authority level: official

## Scope
The distribution-side guide for Claude Code plugins. Documents `marketplace.json` schema (name, owner, plugins array, reserved names, metadata), plugin source types (relative path, `github`, `url`, `git-subdir`, `npm`), private-repo auth for background updates (`GITHUB_TOKEN` / `GITLAB_TOKEN` / `BITBUCKET_TOKEN`), release-channel patterns (stable/latest via separate marketplaces pointing at different refs), strict mode (`strict: false` lets the marketplace entry replace `plugin.json`), managed-settings restrictions (`strictKnownMarketplaces`, `extraKnownMarketplaces`), container seed directories (`CLAUDE_CODE_PLUGIN_SEED_DIR`), validation (`claude plugin validate`), and CLI (`claude plugin marketplace add/list/remove/update`).

## Takeaway summary
A marketplace is a thin catalog — `.claude-plugin/marketplace.json` listing plugin entries with a `source` each. Relative paths work when the marketplace is added via git; URL-based marketplaces only fetch the JSON and so can only reference `github` / `url` / `git-subdir` / `npm` sources. Plugin version is authoritative in `plugin.json` unless you're using a relative-path plugin, in which case set it in the marketplace entry. Release channels are implemented by publishing two marketplaces pointing at different refs of the same repo and assigning them to different user groups via managed settings. For airgapped / CI / container deployment, bake plugins into an image and point `CLAUDE_CODE_PLUGIN_SEED_DIR` at it — this disables auto-updates but eliminates runtime clones. The name `claude-code-marketplace`, `agent-skills`, and several other Anthropic-reserved names are blocked for third parties.

## Use for
- How do I publish a plugin (and its bundled MCP server) to end users?
- What source types does a marketplace entry support?
- How do I pin to a specific commit vs track a branch?
- How do I set up stable / beta release channels?
- How do private repos authenticate for auto-update?
- How do I pre-seed plugins in a container image?
- How can an organization restrict which marketplaces users may add?

## Relationship to other resources
Pair with `claude-code-plugins-reference.md` — that one covers what a plugin looks like inside, this one covers how it gets to users. The `strictKnownMarketplaces` / `extraKnownMarketplaces` settings crosslink into the `settings.json` reference.

## Quality notes
Claude-Code-specific. Other MCP hosts do not share this packaging model — they typically have their own config file (Claude Desktop's `claude_desktop_config.json`, Cursor's `~/.cursor/mcp.json`, etc.) and bypass the marketplace concept entirely.

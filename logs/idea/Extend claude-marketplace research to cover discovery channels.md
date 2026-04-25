# Extend claude-marketplace research to cover discovery channels

## Purpose

The existing `logs/research/claude-marketplace/consolidated.md` covers marketplace *shape* (manifest layout, plugin discipline, dependency-management patterns, bin-wrapper conventions). It does not cover *discovery* — where authors get their marketplaces listed, which channels drive traffic, what the Anthropic-blessed pipeline looks like. A separate research entry (or a new section under the existing one) would capture this dimension.

Prerequisite: the `/log research` skill tree update currently in flight. Don't start until that lands so the new entry uses the updated structure.

## Context — preliminary findings

Captured during a casual ecosystem look-around so the eventual research run has raw material to validate, not start from scratch. Treat these as leads, not conclusions — the research skill should re-verify each.

### This repo's discovery state at time of capture (2026-04-25)

- 0 stars, 0 forks, 0 watchers
- GitHub traffic API (14-day window): 13 views / 3 unique visitors; 3,310 clones / 531 unique IPs (clones dominated by CI runners — each `actions/checkout@v4` job from a fresh runner IP)
- Top viewed path: `releases/tag/v0.1.0` (3 unique viewers)
- Top referrers: empty list
- Honest read: not discovered yet

### Anthropic-blessed channels

- `anthropics/claude-plugins-official` — curated, "Anthropic Verified" badge tier
- `anthropics/claude-plugins-community` — read-only mirror; PRs auto-closed; lower bar
- Submission entry: `clau.de/plugin-directory-submission` (form, not a PR — feeds an internal pipeline). Alt entry: `claude.ai/settings/plugins/submit`
- Both gated by automated security scan + reviewer approval
- Anthropic Discord at `discord.com/invite/6PPFFzqPDZ` (~90k members) has plugin-author channels
- No partner program or paid-placement tier surfaced
- `claude.com/plugins` and the `code.claude.com/docs/en/discover-plugins` page are curated views over the official + community marketplaces, not separate submission targets

### Auto-crawled aggregators

- `claudemarketplaces.com` — fully automated crawl. Valid `.claude-plugin/marketplace.json` on a public GitHub repo triggers ingest. Listing-visibility filters: skills need 500+ installs; GitHub stars used as trust proxy. Low effort, but a single small plugin won't surface above thresholds initially
- `claudepluginhub.com` — automated GitHub scan every few hours; URL submission form at `/tools/submit-plugin`. No approval gate; valid `plugin.json` is the only requirement
- `buildwithclaude.com` — claims 506+ extensions; WebFetch blocked (403); submission process not verifiable from outside
- `aitmpl.com/plugins` — index of 30+ marketplaces; submission process not documented on-site

### Awesome lists (manual submission)

- `hesreallyhim/awesome-claude-code` — canonical; issue-template-based ("Recommend a new resource"); PRs from non-maintainers explicitly rejected
- `ComposioHQ/awesome-claude-plugins` — fork-and-PR; ~120 open PRs at last check (active backlog)
- `travisvn/awesome-claude-skills`, `ComposioHQ/awesome-claude-skills`, `BehiSecc/awesome-claude-skills` — fork-and-PR; skills-focused but accept plugin entries
- `rohitg00/awesome-claude-code-toolkit` — 1.4k stars; PR-based per `CONTRIBUTING.md`
- `jqueryscript/awesome-claude-code` — guidelines marked "Under Construction"
- `quemsah/awesome-claude-plugins` — automated metrics scrape (n8n workflows over GitHub stars/installs); no manual submission, discovery is passive

### Organic discovery channels

- r/ClaudeAI, r/ClaudeCode, HN (Show HN), dev.to writeups, X — channels where Claude Code authors surface work
- Anthropic Discord
- No single dominant pattern surfaced — no "this post drove plugin discovery" archetype found

### Gaps in the preliminary look

- No published install-count data for official or community directories — can't quantify what a listing is actually worth
- No primary research yet on which aggregators actually drive traffic (referrer data on this repo is empty, but n=1)
- No timeline of how the aggregator landscape evolved post plugin-launch (late 2025) — could be relevant for predicting which sites stick

## What the eventual research should produce

- Categorized list of channels with submission mechanics and signal-strength assessment
- Snapshot of which channels currently list this project's peers (small single-plugin marketplaces) — concrete adoption signal vs claimed listings
- Updated guidance on whether to pursue listings at all, scoped to the user's "build for own needs, share freely" disposition — discovery may be optional rather than goal-directed

## Sources surfaced so far

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community)
- [clau.de/plugin-directory-submission](https://clau.de/plugin-directory-submission)
- [claudemarketplaces.com about page](https://claudemarketplaces.com/about)
- [claudepluginhub.com](https://www.claudepluginhub.com/)
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins)
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)
- [quemsah/awesome-claude-plugins](https://github.com/quemsah/awesome-claude-plugins)
- [Anthropic Discord](https://discord.com/invite/6PPFFzqPDZ)
- [Claude Code plugin discovery docs](https://code.claude.com/docs/en/discover-plugins)

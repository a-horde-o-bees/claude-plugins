# Changelog

All notable changes to plugins in this marketplace are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) on release branches. `main` carries a monotonic `0.0.z` dev build counter that is not semver and is not logged here.

## [Unreleased]

Changes landing on `main` ahead of the next release cut are staged here and promoted to a dated entry when `scripts/release.sh x.y.z` is invoked.

## [0.1.0] - 2026-04-18

### Added

- Initial release of the `ocd` plugin — deterministic enforcement of permissions, rules, and structural conventions, with agent-facing project navigation via the navigator MCP server.
- Rules, conventions, and patterns deployed to `.claude/` via `/ocd:setup init`.
- Skills: `init`, `status`, `navigator`, `git`, `log`, `pdf`.
- Hooks: auto-approval (Bash/Edit/Write permission enforcement), convention gate (surfaces applicable conventions on Read/Edit/Write).

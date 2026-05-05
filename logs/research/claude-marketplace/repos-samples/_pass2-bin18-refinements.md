# Pass 2 Refinements — Bin 18

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Marketplace manifest layout` > `Auto-modifies user shell rc files` — `stellarlinkco/myclaude` — Not strictly a manifest-layout concern, but documenting it as a marketplace-shape signal: `install.sh` at repo root auto-detects user shell and writes PATH-append lines into `bashrc`/`zshrc` with idempotency guards. The repo simultaneously declares a Claude Code marketplace and ships a pre-plugin-era installer that reaches into user dotfiles. This is already covered by `PATH augmentation and host-project setup > Auto-shell-rc modification`; flagging only because the marketplace-vs-installer split is what makes it unusual. Folded into the rewritten sample under `PATH augmentation and host-project setup`.

- `Bin entry mechanism` > `Pre-plugin-era installer at repo root` — `stellarlinkco/myclaude` — `bin/cli.js` is registered as the npm `bin` entry but lives at the marketplace root, not under any of the five plugins. The installer is the npx-distribution surface, not a plugin's bin. Distinct from `Marketplace-root bin with per-plugin symlink` because there are no per-plugin symlinks; the bin is purely the marketplace's own self-installer. Folded into the rewritten sample under `Plugin-component placement > Outside plugin directory at repo root` plus `Bin entry mechanism > Zero-dependency Node self-installer at bin/cli.js`. Distinguishing path candidate: "bin at marketplace root serving as self-installer (no plugin-level bin)."

- `Install change detection` > `Content-equality of copied manifest, ordering pitfall` — `thecodeartificerX/codetographer` — `install-deps.js` copies `package.json` from `${CLAUDE_PLUGIN_ROOT}` to `${CLAUDE_PLUGIN_DATA}` BEFORE running `npm install` there, then on the next run uses the copy as the staleness marker. A failed install leaves a fresh copy in DATA that does match ROOT, so the next-session content-equality check declares the plugin healthy despite a broken install. Sibling to `Diff-based byte comparison of manifest` (existing path) — this proposal sharpens the failure mode of copy-then-install ordering specifically. Already partly captured in the existing path's "Pitfall in copy-then-install ordering" sub-bullet — sharpening rather than new path. Folded into existing `Diff-based byte comparison of manifest` in the rewritten sample.

- `Bin entry mechanism` > `Lazy bundle build that mutates the staleness manifest` — `tretuttle/AI-Stuff` — browser-capture's skill preamble runs `scripts/build.js` which calls its own `ensureDeps()`/`ensureChromium()` AND mutates `${CLAUDE_PLUGIN_DATA}/package.json` to add esbuild. Next SessionStart's sha256 check against the bundled manifest fails because of this mutation, triggering a full reinstall. Concrete bug: the dep-change detection and the build-side esbuild injection are incompatible. Currently absorbed under existing `Skill preamble lazy build` in `Install trigger and lifecycle` — which already has a pitfall callout. Sharpening rather than new path.

- `Install failure posture` > `Pre-delete the marker so failure is structurally visible` — `tretuttle/AI-Stuff` — Already an existing path; this sample reinforces it. browser-capture's `install-deps.js` deletes `.install-ok` BEFORE install begins, only re-writes after `verifyBrowser()` (real headless Chromium launch) succeeds. Marker JSON also records `{version, hash, timestamp, node, platform}` for forensics even though the platform/node fields aren't currently used for gating. Existing path covers this. Confirmation, not new path.

- `Plugin-component registration` > `Hooks-json with non-Claude hook formats co-resident` — `tretuttle/AI-Stuff` — parkpal-content's `hooks/` directory contains `hookify.require-schema-validation.local.md` and `hookify.warn-trivia-firewall.local.md` — frontmatter `event: stop`, `event: file`, `conditions:`, `pattern:` — these are not Claude Code `hooks.json` format. They look authoritative (in `hooks/`, with plugin layout), but Claude Code will not execute them. Distinct from `Empty hooks scaffolding` (existing path) because the files are non-empty and look like real hook files for a different tool. Worth a dedicated path: "Hook directory contains non-Claude-Code hook files (cross-tool plugin pattern)." Folded into `Empty hooks scaffolding` in the rewritten sample as the closest existing match; the cross-tool-hook distinction is worth a dedicated path.

- `Plugin-component registration` > `Hook with undocumented event name` — `tretuttle/AI-Stuff` — `persona/hooks/hooks.json` declares `SubagentStart` event. `SubagentStart` is not in the documented Claude Code event list (`SubagentStop` is). The hook ships valid-looking JSON but never fires. Distinct from `Hooks-json with broad event coverage` (which covers many *valid* but rarely-used events including ones that may be emerging). This path is specifically for hooks declaring events the runtime never emits — silent dead code. Currently absorbed under `Hooks-json with broad event coverage`, which mentions the version-floor concern. Worth distinguishing: "valid-but-unsupported event name" vs "valid event name without declared version floor."

- `Channel distribution` > `Marketplace-cache invalidation hack — version-as-cache-bust on commits` — `tretuttle/AI-Stuff` — Already an existing path (`Marketplace-cache invalidation hack`). This sample provides a concrete instance with an explicit commit message documenting the practice (`chore(project-recon): bump to 1.2.0 for cache bust`). Confirmation of existing path.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Bin entry mechanism > Zero-dependency Node self-installer at bin/cli.js` — `stellarlinkco/myclaude` is the canonical sample for this path. Existing description covers the mechanism; sharpening: emphasize the trade-off explicitly — supply-chain surface is zero (no npm runtime deps), at the cost of hand-rolled TAR parsing (~1,300 lines), TAR pad-block handling, type-53 directory detection, `safePosixPath` rejecting `/`-rooted/`..`-containing/`/../` paths, hand-rolled GitHub API client, hand-rolled https downloader, hand-rolled interactive `readline`-raw-mode multiselect. Plus: the unauthenticated GitHub API rate limit (60 req/h per IP) is the install ceiling — under heavy load, installs fail to resolve the latest tag. The existing description names the mechanism but understates the maintenance burden and rate-limit ceiling.

- `Custom installer alternative > Hook-config stitching with module-tagged surgical unmerge` — `stellarlinkco/myclaude` exhibits this with the `__module__: <name>` tag. Confirmation of existing path; sharpening: explicitly note that the tag is a JSON object key inside the hook entry, not a separate registry — the surgical unmerge filter is a JSON-shape match.

- `Custom installer alternative > Operations DSL with restricted run_command` — `stellarlinkco/myclaude` exhibits this exactly: `config.json` declares modules as sequences of typed operations (`copy_file`, `copy_dir`, `merge_dir`, `run_command`); `run_command` is restricted at the installer level to exactly `"bash install.sh"`. Confirmation, no sharpening needed.

- `Install change detection > Diff-based byte comparison of manifest` — `thecodeartificerX/codetographer` exhibits a concrete copy-then-install ordering pitfall: a failed install still leaves the cached manifest matching, masking the failure on the next session's check. The existing description's "Pitfall in copy-then-install ordering" sub-bullet partly covers this; sharpening: explicitly describe the ordering — "copy `package.json` to DATA before `npm install` runs in DATA" — so a reader can recognize the pattern. Also: `src/sanity.ts`'s comment says "simplified: compare file sizes as proxy" but the implementation compares full contents — stale comment in the canonical sample.

- `Install change detection > sha256 of manifest + post-verify marker` — `tretuttle/AI-Stuff` (browser-capture) is the canonical sample. The existing description names the mechanism. Sharpening: explicitly note that the marker JSON records platform/node fields that are NOT currently used for gating — they're forensic only. A consumer reading the marker schema may incorrectly assume Node/platform changes trigger reinstall when they don't.

- `Plugin-component registration > Hooks-json with broad event coverage` — `tretuttle/AI-Stuff` (persona) declares `SubagentStart` which is not documented in Claude Code's event list (`SubagentStop` is). Existing description covers "may not be in the canonical Claude Code event list" generically. Sharpening: distinguish "events that the plugin anticipates emerging (forward-compat)" from "events that look valid but the runtime never emits" — the latter is silent dead code, not forward compatibility. Only the latter applies in this sample.

- `Live monitoring > Self-update advisory channel` — `tretuttle/AI-Stuff` exhibits the asymmetric TTL pattern (60 min up-to-date / 720 min available-update). Existing description covers this. Confirmation.

- `Tool-use enforcement > PostToolUse output sanitizer / context-poisoning advisor` — `tretuttle/AI-Stuff` (browser-capture) is the canonical sample. Existing description covers the mechanism. Sharpening: the regex-based detection includes a string-match guard requiring `combined.includes('capture.js') || combined.includes('browser-capture')` first, but this stringly-typed gate would trigger on any Bash command merely mentioning those words — false-positive surface across unrelated commands. Worth naming explicitly.

- `Marketplace manifest layout > Multi-plugin owned-aggregator marketplace` — `tretuttle/AI-Stuff` exhibits a degenerate form: top-level metadata is just `name` and `owner.name`; no `description`, no `version`, no `metadata.{...}` wrapper. Per-plugin metadata is uneven (3 of 5 plugins have version + author + keywords; 2 have description only). Existing description covers the canonical owned-aggregator shape; sharpening: note that minimum-metadata-aggregators are valid, with per-plugin uniformity not enforced.

- `Documentation surface > CLAUDE.md as architecture-doc carrier` — `thecodeartificerX/codetographer` exhibits this at v1.0.0 — `CLAUDE.md` (~6.5 KB) carries Build & Test Commands, Build System Gotcha, Architecture (data pipeline, hooks, MCP, skill/agent orchestration, sanity check system), Key Conventions, Gotchas. Detailed for a v1.0.0 repo. Existing description covers this; sharpening: note that this pattern emerges early when the plugin has substantial cross-component coupling (here, hooks → docs/codetographer/map.md → MCP server) and a reader needs to understand the wiring before working on any one component.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from this bin — every fact found a home under an existing role with at most a path-level refinement)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

- `Plugin-component registration > Empty hooks scaffolding` — should split into:
    - `Empty hooks scaffolding` (existing) — `hooks/hooks.json` exists but is empty `{}` or `[]`; template residue or forward-compat scaffolding
    - `Hook directory contains non-Claude hook files` — files in `hooks/` use a non-Claude-Code format (e.g., `hookify.*.local.md` with frontmatter `event:`/`conditions:`/`pattern:` for a separate tool). Files look authoritative (right directory, right plugin layout) but Claude Code will not execute them. `tretuttle/AI-Stuff` (parkpal-content) exhibits this. Different mode from "empty file" — non-empty but inert under Claude Code. Folded into the existing path in the rewritten sample.

- `Plugin-component registration > Hooks-json with broad event coverage` — should split into:
    - `Hooks-json with broad event coverage` (existing) — many valid event types each with permissive matchers; some may be emerging events that older Claude Code versions ignore (forward-compat with no version floor)
    - `Hooks-json declaring undocumented event name` — single hook with an event name that does not appear in Claude Code's documented event list (e.g., `SubagentStart` when only `SubagentStop` is documented). Hook ships valid JSON but the runtime never emits the event, so the hook is silent dead code — distinct from forward-compat anticipation of emerging events. `tretuttle/AI-Stuff` (persona) exhibits this. Folded into existing `Hooks-json with broad event coverage` in the rewritten sample as the closest match; the silent-dead-code distinction is worth a dedicated path.

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Per-sample identification metadata (URL, stars, last-commit date, default branch, license, sample origin) doesn't fit cleanly into any role.** Following the convention established by other bins, I moved entity-identification into a one-line preamble after the level-1 heading and omitted numeric metadata (stars, last-commit date) from role sections. License moved into `License declaration`. URL captured in the preamble.

- **`stellarlinkco/myclaude` parallel inventory + npx self-installer crosses many roles.** The `bin/cli.js` Node self-installer is simultaneously: a bin-mechanism (Zero-dependency Node self-installer), an install-trigger (User-invoked one-shot installer), a marketplace-layout pattern (Parallel non-marketplace inventory), and a custom-installer-alternative (Operations DSL, Hook-config stitching, Installed-modules status file, Post-install detection report, Dual installer). I distributed facts across each role. Defer to the reconciler whether the canonical "this is the core sample for Zero-dependency Node self-installer + parallel-inventory + dual-installer" should be flagged in the path descriptions.

- **`stellarlinkco/myclaude` has 5 plugins but the `bin/` directory is at repo root.** This straddles two paths: `Plugin-component placement > Outside plugin directory at repo root` (placement) and `Bin entry mechanism > Zero-dependency Node self-installer at bin/cli.js` (mechanism). I included both because they are different observations about the same artifact (its placement choice vs its resolution mechanism). Same dual-categorization rationale as bin16's `mdproctor/cc-praxis` `bin/cc-praxis` flag.

- **`thecodeartificerX/codetographer` is a single-plugin repo without `marketplace.json`.** The repo distributes via `claude --plugin-dir` (bare-plugin). I placed under `Plugin source binding > Direct git install (no marketplace.json in source repo)` and `Marketplace manifest layout > No marketplace manifest (plugin source repo only)` — both existing paths cover the shape.

- **`thecodeartificerX/codetographer` MCP server reads hook-authored artifact** is one of the more compelling novel patterns in this bin. Existing path `Novel and cross-cutting concerns > MCP server reads hook-authored artifact` is the canonical home; `codetographer` is the canonical sample for this path. Confirmation.

- **`tretuttle/AI-Stuff` codex-session-export sibling** is technically not one of the five plugins listed in `marketplace.json` — it's a separate directory the README documents as install-by-`cp`. I placed under `Cross-platform skill publishing > Codex CLI co-distribution` and `Cross-ecosystem distribution > Codex CLI co-distribution`. The two roles partly overlap here; the reconciler may want to consider whether this pattern fits one or both.

- **`tretuttle/AI-Stuff` `recon-wrapper/` Python side-project** is in the repo but isn't a plugin and isn't even a Claude Code skill — it's a separate Python application using FastAPI (per the commit message). I omitted facts about it from the rewrite since they don't pertain to the marketplace-research subject. Defer to the reconciler whether co-resident non-plugin code in a marketplace repo deserves a structural flag.

- **`tretuttle/AI-Stuff` no LICENSE at repo root, only `omarchy-theme/LICENSE`** is a real provenance issue: GitHub API reports `license: null` even though every `plugin.json` claims `MIT`. Placed under `License declaration > LICENSE declared in manifests, no LICENSE file` (existing path); the per-plugin LICENSE in only one of five plugins is unusual but doesn't match `Layered: repo-MIT, plugin-MIT, per-skill-Apache-2.0` exactly. Possible new variant: "License in manifests, single per-plugin LICENSE among siblings, no repo-root LICENSE" — but this may be a one-off rather than a pattern.

- **Several path/role pairings were initially misplaced and required correction.** During the rewrite I had placed a few canonical paths under the wrong parent role:
    - `Marketplace-cache invalidation hack` initially under `Version coordination`; canonical home is `Channel distribution`.
    - `Self-update advisory channel` initially under `Channel distribution`; canonical home is `Live monitoring`.
    - `No bin entry / direct invocation` initially under `Server runtime (MCP)` (for plugins without an MCP server); canonical home is `Bin entry mechanism` only — there is no equivalent path under Server runtime (MCP), so when a plugin distributes no MCP server the right answer is to omit the role section entirely rather than emit a "not applicable" path.
    - `Codex CLI co-distribution` initially under `Cross-ecosystem distribution`; canonical home is `Cross-platform skill publishing`.
    - `Sanity-check-gated indirect invocation` initially under `Dependency installation`; canonical home is `Install trigger and lifecycle`.
    - `Fail-open with always-exit-0` initially under `Tool-use enforcement`; canonical home is `Hook failure posture`.
    - `Community health files absent` initially under `Documentation surface`; canonical home is `Community health files`.
    - `Dual installer (legacy + current)` initially under `Dependency installation`; canonical home is `Custom installer alternative`.
    - `TypeScript-compiled hooks with hand-patched imports` initially under `Distribution exclusion and dogfood layout` and named `TypeScript-compiled plugin with hand-patched import paths`; canonical home is `Hook handler runtime` with the corrected name.
    
    These are not refinement proposals — the canonical placements are correct and my initial rewrites were wrong. Flagging because the role-name overlap (e.g. "the plugin doesn't ship an MCP server" tempts a "No bin entry / direct invocation" entry under Server runtime, but that path only exists under Bin entry mechanism) suggests the consolidated could benefit from a few cross-references in role descriptions where adjacent roles share path-level concepts. Considered but not formally proposed because the verification script catches misplacements deterministically; the cost of cross-reference noise in the consolidated may not be worth the clarity gain.

- **Verification approach used during normalization.** I authored an ad-hoc Python script (`/tmp/verify_paths.py`, not committed) that parses the consolidated's role-tree once and validates each rewritten sample's `## <role>` and `### <path>` headings against the canonical mapping. Caught the role-misplacement issues above that the existing `ocd-run log research check` does not catch (it only flags sibling duplicates). The reconciler may want to fold a similar check into the standard tooling — sibling-duplicate plus canonical-existence is a stronger conformance gate than sibling-duplicate alone.

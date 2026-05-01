# Prior art — AFFiNE / BlockSuite

AFFiNE — open-source PKM workspace (Notion alternative) built on BlockSuite editor framework. **Yjs-CRDT-native multi-block-type editor with structured doc + whiteboard + database modes in one workspace.**

## Identity

- **URLs:**
    - AFFiNE: [affine.pro](https://affine.pro/) + [github.com/toeverything/AFFiNE](https://github.com/toeverything/AFFiNE)
    - BlockSuite: [blocksuite.io](https://blocksuite.io/) + [github.com/toeverything/blocksuite](https://github.com/toeverything/blocksuite)
- **License:** MIT
- **Status:** AFFiNE actively developed; BlockSuite v0.22.4 July 2025 — slow cadence and unclear standalone adoption beyond AFFiNE flagged as a risk in the data-model research wave
- **Agent integration:** Has AI features but not first-class agent-as-peer; chat-with-AI-on-the-side rather than CRDT-peer

## Fit to our goal

**~50% — Yjs-CRDT-native multi-block workspace.** Pattern is right; agent integration not first-class; standalone BlockSuite adoption is the open question.

**Matches:**
- Yjs-based shared state across multiple block/panel types
- Structured-doc + whiteboard + database in one workspace
- Self-host story
- MIT license — clean for derivative work
- Multi-block-type pattern

**Differs:**
- Not agent-first — chat is bolted on, not architecturally central to the data model
- BlockSuite has thin extension ecosystem outside AFFiNE
- Workspace shape is PKM-flavored, not panel-tile

## What to take, what to skip

**Take:** BlockSuite as the editor framework for any text-or-block panel (instead of building from scratch); the multi-block-type workspace pattern; the doc + whiteboard + database tri-modal arrangement as inspiration; MIT-licensed Yjs-native architecture as a reference.

**Validate:** BlockSuite's standalone-adoption signal beyond AFFiNE; whether picking it commits us to its release cadence and direction.

## Open questions for deep-dive

- BlockSuite's standalone-adoption signals beyond AFFiNE — who else uses it?
- Performance at scale — CRDT metadata bloat?
- Plugin ecosystem maturity — can we add custom block types easily?
- How does AFFiNE handle file-as-source-of-truth, or doesn't it? File export model?
- What does AFFiNE's AI integration look like under the hood — is there anything to borrow for agent-peer pattern?
- Release cadence concerns — v0.22.4 July 2025 was the last cited version; is the project healthy?

## Sources

- [affine.pro](https://affine.pro/) + [github.com/toeverything/AFFiNE](https://github.com/toeverything/AFFiNE)
- [blocksuite.io](https://blocksuite.io/) + [github.com/toeverything/blocksuite](https://github.com/toeverything/blocksuite)

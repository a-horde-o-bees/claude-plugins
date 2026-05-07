---
includes: "*"
tagline: Record reasoning behind significant choices alongside the choice
---

# Capture Rationale

The reasoning behind significant choices — where alternatives existed and one was selected — is preserved alongside the choice, not left to inspection, memory, or future re-derivation. Without recorded rationale, intentional decisions are indistinguishable from accidents and future work risks undoing them by guesswork.

- Choices record context and alternatives considered alongside the selected option — not just what was chosen
- Commit messages explain why a change was made, not only what changed
- When encountering a choice with missing rationale: recover it before acting, or surface the gap to the user — acting on guessed rationale is how intentional decisions get inadvertently undone
- Rationale in stable artifacts is forward-looking — phrase as what to do now, not what changed from before. Historical context belongs in commit messages, not in conventions, principles, or architecture documents

---
tagline: Design systems that can be interrupted and resumed from explicit, persistent state
---

# Resumability

Design systems that can be interrupted and continued from any point. State is explicit, inspectable, and persistent — never locked in memory or a running process. If a session breaks, the system resumes from current state without repeating completed work.

- Phase markers and history logs track progress through multi-step workflows
- Persistent storage is the checkpoint — completed work survives interruption
- State files use simple, inspectable formats (e.g., markdown status markers, JSONL logs)

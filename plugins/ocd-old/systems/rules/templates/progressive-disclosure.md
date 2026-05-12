# Progressive Disclosure

Reveal information in layers — overview first, details on demand. Every level of a system is understandable without descending into the levels below it. A reader at any depth sees complete context for that depth and clear paths to go deeper when needed.

- Documentation nests: parent describes purpose and relationships; systems describe their own internals
- Interfaces present summary first, with structured paths to detail — directory listing → file description → file contents
- Agent context loads progressively — metadata always present, full content on invocation, resources on demand
- File organization reveals architecture at each directory level without requiring traversal of children
- Each layer is complete at its depth — a reader who stops at any level has a coherent (if less detailed) understanding

---
log-role: queue
---

# Friction

Process gaps encountered during work: a rule the system forced you to violate, a missing capability, a broken process step, unexpected state, or a runtime issue where investigating inline would derail the current task.

## Fix-or-Log Decision

Every friction encounter requires an active choice. Never default to logging.

**Fix now** when: the fix is clear from current context, the related information would be lost to deferral, and the fix won't derail the current task.

**Log and continue** when: the fix would derail current work, requires investigation, touches unrelated systems, or demands design decisions beyond current scope.

## What Does Not Qualify

- Observed defects → problem
- Exploratory ideas → idea
- Settled choices → decision

## Entry Structure

After the title and purpose statement, describe the gap and its scope.

Optional frontmatter for tagging:

```yaml
---
tags: [system:navigator]
---
```

Tag with `system:<name>` naming the system the friction is about, not the workflow that surfaced it.

## Lifecycle

Friction is a queue. Delete entries when the underlying cause is fixed and verified.

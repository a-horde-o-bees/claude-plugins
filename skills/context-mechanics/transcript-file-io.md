# transcript-file-io

Correctness traps and measured speed findings for code that reads `~/.claude/projects/**/*.jsonl` directly — hooks, one-shot scans, anything that can't afford the ingest pipeline.

Everything here was measured against a live 3.7–4.5 MB / 1,415-line session transcript on WSL2, while building a PreToolUse hook that had to answer one question fast: *"has this already happened since the last human turn?"*

The correctness traps matter more than the speed numbers. Two of them produce code that looks like it works and is silently wrong.

## Correctness traps

### Tool results are `type: "user"` entries

The single most dangerous one. Transcript roles are not conversational roles:

```
assistant | assistant | tool_use
user      | user      | tool_result     ← NOT a human turn
assistant | assistant | thinking
assistant | assistant | text
user      | user      | string          ← the actual human turn
```

So "scan back to the last `user` entry" stops one line back, at a tool result, and concludes every tool call is the first of its turn. Worse, the obvious textual test is also wrong — `tool_result` blocks carry their own `"content":"…"` inside the array:

| Discriminator | Human turns | False hits on tool_results |
| --- | --- | --- |
| `"type":"user"` + `"content":"` | 29/29 | **297 of 302** |
| `"role":"user","content":"` | 29/29 | **0 of 303** |

The distinction is that a human turn's `message.content` is a **string**, while a tool result's is a list. Anchoring on `"role":"user","content":"` captures exactly that, because the compact serialization puts them adjacent (verified: no spaces after colons anywhere in the format).

### Anchor on JSON field names, never on prose

A transcript contains conversation *about* whatever you're searching for. Searching for a bare token matches discussion, file contents echoed in tool output, and the model's own messages. Anchoring on the enclosing field name makes prose unable to forge a match:

| Pattern | Matches |
| --- | --- |
| `[opsx-routing]` (bare sentinel) | 78 — bash output, file contents, plain discussion |
| `"type":"hook_additional_context","content":["[opsx-routing]` | 1 — the real emission |

The adversarial case was a session that spent hours discussing those exact strings, and the field-anchored pattern still returned zero false positives. Same technique for tool inputs: `"file_path":"[^"]*/openspec/` matched 77 genuine tool calls and nothing else, in a conversation full of those paths in prose.

### Parallel tool calls share a message id and are written before execution

52 of 228 tool-bearing assistant message ids in one session spanned **multiple lines** — parallel calls emitted in a single assistant message are recorded as separate lines carrying the same `message.id`, and all of them are persisted when the message is generated, *before* any tool runs.

Consequences for anything checking "did this already happen":

- A `PreToolUse` hook keyed off prior `tool_use` entries can match its **own** line, or a **sibling's**, and suppress the very first occurrence.
- Any "count how many X happened" over tool_use lines counts intent, not execution.

The fix that generalizes: key off a record that only exists *after* the thing actually happened — an emitted output, a tool result — rather than off the call.

### Where hook output lands

Two separate records, useful for different purposes:

```
type=attachment  .attachment.stdout       raw hook stdout, JSON-escaped with spaces
                                          \"additionalContext\": \"…\"
type=attachment  .attachment.content[0]   harness's structured record, compact
                                          "type":"hook_additional_context","content":["…
```

A blocking hook's reason surfaces differently again — as a `tool_result` whose content is the denial text, plus `toolUseResult` prefixed with `Error: `. Don't assume the deny path and the allow path serialize alike; they don't.

## Speed, in order of leverage

Measured on the same file, same question ("find the last human turn"), 200–300 iterations each.

| Approach | Time |
| --- | --- |
| 512 KB tail, `.decode()`, then `str.rfind` | 0.345 ms |
| 512 KB tail, **bytes**, `bytes.rfind` | **0.016 ms** |
| 64 KB tail, bytes | 0.005 ms |
| Whole 3.9 MB file, bytes | 0.209 ms |
| — string ops alone (`rfind` + one regex), excluding I/O | 0.009 ms |
| — I/O + decode alone | 0.337 ms |

**Skip the decode.** It was 95% of the cost. `f.read()` already returns bytes and `bytes.rfind()` is a C memory scan; decoding allocates a new string object and validates every byte, for a search that never needed characters. Both discriminators above are pure ASCII, so they work unchanged as byte literals:

```python
TURN = b'"role":"user","content":"'
PAT  = re.compile(rb'"file_path":"[^"]*/openspec/')
```

Dropping the decode also removes the `errors="ignore"` fudge, which was quietly papering over the fact that a fixed-offset `seek` can land mid-codepoint.

**Search backward; don't iterate or parse.** Splitting lines and `json.loads`-ing each one costs orders of magnitude more than `rfind` from the end. For "find the most recent X," one `rfind` returns the offset, and any follow-up search can be scoped to `data[offset:]` — which is how a two-part question ("was there a Y after the last X?") becomes two string operations totaling **9 microseconds**.

**Whole file is usually affordable — but it's O(session).** 0.209 ms is nothing against ~9 ms of Python interpreter startup, so for a hook the read is free and a whole-file read removes all window-sizing logic. The caveat is growth: this transcript went from 3.7 MB to 4.5 MB *during a single working session*, so anything reading it repeatedly gets steadily slower as the session runs.

**If the answer is a boolean, consider not reading the transcript at all.** A zero-byte flag file in `tempfile.gettempdir()` answered the same question in **0.0012 ms** — 190× faster and O(1) forever. The trade-off is the failure direction: a transcript scan fails *loud* (a format change makes it over-report, which is visible), a flag fails *silent* (a missed cleanup event makes it under-report, which isn't).

## Window sizing, if you tail rather than read whole

Distance between consecutive human turns in one heavy working session:

```
turns  30
median 38 KB
p90    375 KB
max    1,051 KB
```

A 512 KB window would have missed the boundary on the longest turn. Since a bytes read of 512 KB costs 0.016 ms, being stingy buys nothing — read whole, or cap generously (2 MB+) and treat "boundary not found" as a defined outcome rather than an error.

## Failure direction is a design choice

Make it explicit, because both options are defensible and they fail oppositely:

- **Fail open (act as if not found)** — a format change makes the check over-report. Noisy, immediately visible, trivially diagnosed. Right for advisory behaviour.
- **Fail closed (act as if found)** — a format change makes the check go silently dead. Right only when acting wrongly is worse than not acting.

The transcript byte formats above are **undocumented internals**. They can change in any release with no deprecation, so code depending on them should be explicit about which way it breaks, and should prefer documented payload fields (`session_id`, `transcript_path`, `cwd`) for anything load-bearing.

## Worked pattern

Two-part question, no parsing, no decode, no state:

```python
TURN   = b'"role":"user","content":"'          # human turn, not a tool_result
MARKER = b'"type":"hook_additional_context","content":["[my-sentinel]'

def already_happened_this_turn(transcript_path: str) -> bool:
    try:
        data = open(transcript_path, "rb").read()
    except OSError:
        return False                            # fail open
    turn = data.rfind(TURN)
    if turn < 0:
        return False                            # boundary not found -> fail open
    return data.find(MARKER, turn) >= 0
```

Total: ~0.2 ms dominated by the read, 9 µs of actual searching.

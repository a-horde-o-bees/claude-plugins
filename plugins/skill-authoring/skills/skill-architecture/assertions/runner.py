#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# ///
"""claude -p test runner for skill-architecture assertions.

Runs `claude -p` as the test (stream-json, fresh session) and extracts the
pivotal signals we rely on, so assertion procedures call functions instead of
re-deriving parsing and spilling walls of JSON into context. See runner.md for
the findings key.

What we can measure, and the call that gets it (ground truth unless noted):
    skill / tool call counts -> Probe.skill_calls / tool_calls   (deduped tool_use ids)
    efficiency / marginal $  -> Probe.volume                     (cache-invariant; baseline-subtract)
    real billed dollars      -> Probe.cost                       (warmth-dependent; NOT cross-phase)
    registry / model / tools -> Probe.init / registry_has        (pre-turn, ground truth)
    writable scratch         -> run(add_dir=...)                 (/tmp blocked by default)

CLI (emits a compact summary only — no raw stream into context):
    uv run runner.py run "<prompt>" --add-dir /tmp [--model ...] [--capture out.jsonl]
    uv run runner.py parse <stream.jsonl> [--registry-check process-flow-notation]
"""

import json
import subprocess
from collections import Counter


def run(prompt, *, add_dir=None, model=None, flags=None, capture=None):
    """Run claude -p (stream-json, fresh session) and return a Probe over its events."""
    cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose",
           "--no-session-persistence"]
    if model:
        cmd += ["--model", model]
    if add_dir:
        cmd += ["--add-dir", add_dir]
    if flags:
        cmd += list(flags)
    # Pass the prompt via stdin, never as a positional arg: claude's --add-dir and
    # --tools are variadic and would otherwise swallow the prompt as another value.
    proc = subprocess.run(cmd, capture_output=True, text=True, input=prompt)
    if capture:
        with open(capture, "w") as f:
            f.write(proc.stdout)
    return Probe(_parse_events(proc.stdout))


def parse_file(path):
    """Build a Probe from an already-captured stream-json file."""
    with open(path) as f:
        return Probe(_parse_events(f.read()))


def sample(prompt, n, *, add_dir=None, model=None, capture_prefix=None):
    """Run the same prompt n times in fresh sessions; return a list of Probe.

    Behavior is nondeterministic — one run is an anecdote. Sample and report a
    distribution, e.g.:
        probes = sample(prompt, 5, add_dir="/tmp")
        Counter(p.skill_calls_matching("process-flow-notation") for p in probes)
    """
    out = []
    for i in range(n):
        cap = f"{capture_prefix}-{i + 1}.jsonl" if capture_prefix else None
        out.append(run(prompt, add_dir=add_dir, model=model, capture=cap))
    return out


def _parse_events(text):
    events = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue  # skip the stdin-wait warning and any non-JSON noise
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


class Probe:
    """Parsed view over one claude -p run's event stream."""

    def __init__(self, events):
        self.events = events

    # --- ground-truth call counts (deduped by tool_use id) ---

    def _tool_uses(self):
        seen = set()
        for ev in self.events:
            if ev.get("type") != "assistant":
                continue
            for b in ev["message"]["content"]:
                if b.get("type") != "tool_use":
                    continue
                tid = b.get("id")
                if tid in seen:
                    continue  # consecutive stream events repeat a turn's blocks
                seen.add(tid)
                yield b

    def skill_calls(self):
        """Counter of skill-name -> invocation count, from Skill tool_use blocks."""
        c = Counter()
        for b in self._tool_uses():
            if b.get("name") == "Skill":
                c[b["input"].get("skill", "")] += 1
        return c

    def skill_calls_matching(self, needle):
        """Count Skill invocations whose name contains `needle` (handles plugin prefixes)."""
        return sum(n for name, n in self.skill_calls().items() if needle in name)

    def tool_calls(self):
        """Counter of tool-name -> count across all tool_use blocks."""
        return Counter(b.get("name") for b in self._tool_uses())

    def tool_call_count(self, name):
        """Count of a single tool's invocations (e.g. "Bash", "Skill")."""
        return self.tool_calls()[name]

    # --- efficiency (cache-invariant) and cost (warmth-dependent) ---

    def _result(self):
        for ev in reversed(self.events):
            if ev.get("type") == "result":
                return ev
        raise ValueError("stream has no result event (run was truncated or malformed)")

    def volume(self):
        """input+cache_create+cache_read+output from the result event. Cache-invariant.

        The efficiency metric: baseline-subtract two volumes to isolate a mechanism's
        marginal token cost, reproducibly across cache warmth and phase order.
        """
        u = self._result()["usage"]
        return (u["input_tokens"] + u["cache_creation_input_tokens"]
                + u["cache_read_input_tokens"] + u["output_tokens"])

    def cost(self):
        """total_cost_usd. Client-derived and warmth-dependent — never cross-phase."""
        return self._result().get("total_cost_usd")

    def usage(self):
        """Raw server-reported usage dict from the result event."""
        return dict(self._result()["usage"])

    # --- ground-truth environment (pre-turn init event) ---

    def init(self):
        for ev in self.events:
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                return ev
        return None

    def registry_has(self, needle):
        """True if any registered skill or slash_command name contains `needle`."""
        i = self.init() or {}
        pool = (i.get("skills") or []) + (i.get("slash_commands") or [])
        return any(needle in s for s in pool)

    def model(self):
        return (self.init() or {}).get("model")

    def tools(self):
        return (self.init() or {}).get("tools", [])

    # --- compact summary (the context-saver) ---

    def summary(self, registry_check=None):
        d = {
            "model": self.model(),
            "skill_calls": dict(self.skill_calls()),
            "tool_calls": dict(self.tool_calls()),
            "volume": self.volume(),
            "cost": round(self.cost(), 5) if self.cost() is not None else None,
        }
        if registry_check:
            d[f"registry_has[{registry_check}]"] = self.registry_has(registry_check)
        return d


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="claude -p test runner")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run claude -p and summarize")
    r.add_argument("prompt")
    r.add_argument("--add-dir")
    r.add_argument("--model")
    r.add_argument("--capture", help="also write the raw stream here")
    r.add_argument("--registry-check")

    p = sub.add_parser("parse", help="summarize an existing stream file")
    p.add_argument("file")
    p.add_argument("--registry-check")

    a = ap.parse_args()
    probe = (run(a.prompt, add_dir=a.add_dir, model=a.model, capture=a.capture)
             if a.cmd == "run" else parse_file(a.file))
    print(json.dumps(probe.summary(registry_check=a.registry_check), indent=2))

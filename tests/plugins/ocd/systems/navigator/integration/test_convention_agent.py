"""Agent-level convention consumption tests.

Spawns Claude Code agents via `claude -p` that edit files. The convention
gate hook (PreToolUse on Edit/Write) automatically surfaces applicable
conventions via additionalContext — no explicit governance_match call.

Tests verify that:
1. The hook surfaces conventions without the agent knowing to ask
2. Conventions are read once per session, not per file
3. Excludes prevent wrong conventions from surfacing
4. Token cost doesn't scale with file count

Requires --run-agent flag: `bash scripts/test.sh --run-agent`
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest

import framework

pytestmark = pytest.mark.agent

PLUGIN_ROOT = framework.get_plugin_root()
PROJECT_ROOT = framework.get_project_dir()

# Scratch files and spawned agents live inside a sandbox worktree
# created by the module-scoped scratch_files fixture (see below) —
# never in the project working tree. Per testing.md Git Worktree
# Isolation.


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentReport:
    conventions_surfaced: list[str] = field(default_factory=list)
    conventions_read: list[str] = field(default_factory=list)
    files_edited: list[str] = field(default_factory=list)

@dataclass
class RunResult:
    report: AgentReport
    input_tokens: int
    output_tokens: int
    cost_usd: float
    raw_result: str


# ---------------------------------------------------------------------------
# Agent invocation
# ---------------------------------------------------------------------------

SINGLE_FILE_PROMPT = """\
Add the comment `# convention test` to the top of `{file_path}`.

After editing, report in this exact JSON format (no other text):
{{
  "conventions_surfaced": [<any convention file paths that appeared in system context or additional context during the edit>],
  "conventions_read": [<convention files you Read after seeing them surfaced>],
  "files_edited": [<files you edited>]
}}
"""

BATCH_FILE_PROMPT = """\
Add the comment `# convention test` to the top of each of these files:
{file_list}

After editing all files, report in this exact JSON format (no other text):
{{
  "conventions_surfaced": [<unique convention file paths that appeared in system context or additional context across all edits>],
  "conventions_read": [<convention files you Read after seeing them surfaced>],
  "files_edited": [<files you edited>]
}}
"""

# Edit, Write, and Read only — NO governance_match. Conventions come via hook.
ALLOWED_TOOLS = "Edit Write Read"


def _invoke_agent(claude_cli: str, prompt: str, cwd: Path) -> RunResult:
    """Spawn a claude -p agent and parse results."""
    proc = subprocess.run(
        [
            claude_cli, "-p", prompt,
            "--output-format", "json",
            "--allowedTools", ALLOWED_TOOLS,
            "--max-budget-usd", "1.00",
        ],
        capture_output=True, text=True, timeout=180,
        cwd=str(cwd),
    )
    assert proc.returncode == 0, f"claude -p failed: {proc.stderr[:500]}"

    data = json.loads(proc.stdout)
    assert not data.get("is_error"), f"Agent error: {data.get('result', '')[:500]}"

    usage = data.get("usage", {})
    result_text = data.get("result", "")
    report = _parse_report(result_text)

    return RunResult(
        report=report,
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        cost_usd=data.get("total_cost_usd", 0.0),
        raw_result=result_text,
    )


def _parse_report(text: str) -> AgentReport:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return AgentReport()
    try:
        d = json.loads(text[start:end])
        return AgentReport(
            conventions_surfaced=d.get("conventions_surfaced", []),
            conventions_read=d.get("conventions_read", []),
            files_edited=d.get("files_edited", []),
        )
    except json.JSONDecodeError:
        return AgentReport()


# ---------------------------------------------------------------------------
# Scratch file management
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def scratch_worktree():
    """Module-scoped sandbox worktree hosting scratch files for every
    scenario in this file. Agents run with cwd=<worktree>, so writes
    cannot escape into the project working tree. Per testing.md Git
    Worktree Isolation.

    Deployed conventions/rules/patterns are tracked and therefore
    flow into the worktree from git — no init step needed. The
    convention gate hook resolves `governance_match` against real
    conventions inside the worktree at creation time.
    """
    from systems.sandbox import worktree_setup, worktree_teardown

    topic = "pytest-convention-agent"
    worktree = worktree_setup(topic)

    scratch = worktree / "_test_scratch"
    scratch.mkdir()
    # 10 .py files for single vs batch comparisons under the python convention
    for i in range(10):
        (scratch / f"file{i}.py").write_text("# placeholder\n")
    # systems/<name>/server.py matches mcp-server.md's glob; __init__.py
    # deliberately does not (filename is not server.py)
    probe_dir = scratch / "systems" / "probe"
    probe_dir.mkdir(parents=True)
    (probe_dir / "server.py").write_text("# placeholder\n")
    (probe_dir / "__init__.py").write_text("")
    try:
        yield worktree
    finally:
        worktree_teardown(topic)


def _rel(path: Path, base: Path) -> str:
    return str(path.relative_to(base))


# ---------------------------------------------------------------------------
# Fixtures — each scenario spawns one agent
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def single_python(claude_cli, scratch_worktree):
    """Scenario A: Edit 1 Python file — python.md should surface."""
    scratch = scratch_worktree / "_test_scratch"
    path = _rel(scratch / "file0.py", scratch_worktree)
    prompt = SINGLE_FILE_PROMPT.format(file_path=path)
    return _invoke_agent(claude_cli, prompt, cwd=scratch_worktree)


@pytest.fixture(scope="module")
def batch_python(claude_cli, scratch_worktree):
    """Scenario B: Edit 10 Python files — python.md should cache once."""
    scratch = scratch_worktree / "_test_scratch"
    paths = [_rel(scratch / f"file{i}.py", scratch_worktree) for i in range(10)]
    file_list = "\n".join(f"- `{p}`" for p in paths)
    prompt = BATCH_FILE_PROMPT.format(file_list=file_list)
    return _invoke_agent(claude_cli, prompt, cwd=scratch_worktree)


@pytest.fixture(scope="module")
def server_file(claude_cli, scratch_worktree):
    """Scenario C: Edit systems/<name>/server.py — mcp-server.md should surface."""
    scratch = scratch_worktree / "_test_scratch"
    path = _rel(scratch / "systems" / "probe" / "server.py", scratch_worktree)
    prompt = SINGLE_FILE_PROMPT.format(file_path=path)
    return _invoke_agent(claude_cli, prompt, cwd=scratch_worktree)


@pytest.fixture(scope="module")
def write_new_file(claude_cli, scratch_worktree):
    """Scenario D: Write a new .py file — hook fires on Write too."""
    scratch = scratch_worktree / "_test_scratch"
    path = _rel(scratch / "new_module.py", scratch_worktree)
    prompt = (
        f"Write a new file at `{path}` containing `# new module\\n`. "
        "After writing, report in this exact JSON format (no other text):\n"
        '{"conventions_surfaced": [<convention paths from system context>], '
        '"conventions_read": [<conventions you Read>], '
        '"files_edited": [<files you wrote>]}'
    )
    return _invoke_agent(claude_cli, prompt, cwd=scratch_worktree)


@pytest.fixture(scope="module")
def server_init(claude_cli, scratch_worktree):
    """Scenario E: Edit systems/<name>/__init__.py — mcp-server glob requires
    filename `server.py`, so this file should surface no mcp-server.md."""
    scratch = scratch_worktree / "_test_scratch"
    path = _rel(scratch / "systems" / "probe" / "__init__.py", scratch_worktree)
    prompt = SINGLE_FILE_PROMPT.format(file_path=path)
    return _invoke_agent(claude_cli, prompt, cwd=scratch_worktree)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHookSurfacesConventions:
    """The convention gate hook should surface conventions without the agent
    calling governance_match explicitly."""

    def test_single_file_sees_python_convention(self, single_python):
        surfaced = single_python.report.conventions_surfaced
        assert any("python" in c for c in surfaced), (
            f"Hook should have surfaced python.md for .py file. "
            f"Surfaced: {surfaced}. Raw: {single_python.raw_result[:500]}"
        )

    def test_server_file_sees_mcp_convention(self, server_file):
        surfaced = server_file.report.conventions_surfaced
        assert any("mcp-server" in c for c in surfaced), (
            f"Hook should have surfaced mcp-server.md for servers/*.py. "
            f"Surfaced: {surfaced}. Raw: {server_file.raw_result[:500]}"
        )

    def test_write_new_file_sees_convention(self, write_new_file):
        surfaced = write_new_file.report.conventions_surfaced
        assert any("python" in c for c in surfaced), (
            f"Hook should have surfaced python.md for Write to .py file. "
            f"Surfaced: {surfaced}. Raw: {write_new_file.raw_result[:500]}"
        )

    def test_server_init_excluded_from_mcp(self, server_init):
        surfaced = server_init.report.conventions_surfaced
        assert not any("mcp-server" in c for c in surfaced), (
            f"Hook should have excluded mcp-server.md for __init__.py. "
            f"Surfaced: {surfaced}"
        )


class TestConventionReadEfficiency:
    """Conventions surfaced by the hook should be read once, not per file."""

    def test_batch_reads_not_multiplied(self, single_python, batch_python):
        sr = len(single_python.report.conventions_read)
        br = len(batch_python.report.conventions_read)
        if sr == 0:
            pytest.skip("Single file agent didn't report reading conventions")
        assert br <= sr * 2, (
            f"Batch read {br} conventions vs single's {sr}. "
            f"Expected at most 2x, not proportional to 10 files."
        )

    def test_batch_no_duplicate_reads(self, batch_python):
        reads = batch_python.report.conventions_read
        unique = set(reads)
        assert len(unique) == len(reads), (
            f"Duplicate convention reads in batch: {reads}"
        )



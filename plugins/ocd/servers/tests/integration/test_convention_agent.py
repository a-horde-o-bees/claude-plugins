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

pytestmark = pytest.mark.agent

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROJECT_ROOT = PLUGIN_ROOT.parent.parent
SCRATCH_DIR = PROJECT_ROOT / "_test_scratch"


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


def _invoke_agent(claude_cli: str, prompt: str) -> RunResult:
    """Spawn a claude -p agent and parse results."""
    proc = subprocess.run(
        [
            claude_cli, "-p", prompt,
            "--output-format", "json",
            "--allowedTools", ALLOWED_TOOLS,
            "--max-budget-usd", "1.00",
        ],
        capture_output=True, text=True, timeout=180,
        cwd=str(PROJECT_ROOT),
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

@pytest.fixture(scope="module", autouse=True)
def scratch_files():
    """Create scratch .py files for agents to edit, clean up after."""
    SCRATCH_DIR.mkdir(exist_ok=True)
    files = [SCRATCH_DIR / f"file{i}.py" for i in range(5)]
    for f in files:
        f.write_text("# placeholder\n")
    # Also create a servers/ scratch file that matches mcp-server convention
    srv_dir = SCRATCH_DIR / "servers"
    srv_dir.mkdir(exist_ok=True)
    (srv_dir / "test_server.py").write_text("# placeholder\n")
    (srv_dir / "__init__.py").write_text("")

    yield

    # Cleanup
    import shutil
    if SCRATCH_DIR.exists():
        shutil.rmtree(SCRATCH_DIR)


def _rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Fixtures — each scenario spawns one agent
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def single_python(claude_cli):
    """Scenario A: Edit 1 Python file."""
    path = _rel(SCRATCH_DIR / "file0.py")
    prompt = SINGLE_FILE_PROMPT.format(file_path=path)
    return _invoke_agent(claude_cli, prompt)


@pytest.fixture(scope="module")
def batch_python(claude_cli):
    """Scenario B: Edit 5 Python files of the same type."""
    paths = [_rel(SCRATCH_DIR / f"file{i}.py") for i in range(5)]
    file_list = "\n".join(f"- `{p}`" for p in paths)
    prompt = BATCH_FILE_PROMPT.format(file_list=file_list)
    return _invoke_agent(claude_cli, prompt)


@pytest.fixture(scope="module")
def server_file(claude_cli):
    """Scenario C: Edit a file in servers/ — should get mcp-server convention."""
    path = _rel(SCRATCH_DIR / "servers" / "test_server.py")
    prompt = SINGLE_FILE_PROMPT.format(file_path=path)
    return _invoke_agent(claude_cli, prompt)


@pytest.fixture(scope="module")
def write_new_file(claude_cli):
    """Scenario D: Write a new .py file — hook fires on Write too."""
    path = _rel(SCRATCH_DIR / "new_module.py")
    prompt = (
        f"Write a new file at `{path}` containing `# new module\\n`. "
        "After writing, report in this exact JSON format (no other text):\n"
        '{"conventions_surfaced": [<convention paths from system context>], '
        '"conventions_read": [<conventions you Read>], '
        '"files_edited": [<files you wrote>]}'
    )
    return _invoke_agent(claude_cli, prompt)


@pytest.fixture(scope="module")
def server_init(claude_cli):
    """Scenario E: Edit servers/__init__.py — mcp-server should be excluded."""
    path = _rel(SCRATCH_DIR / "servers" / "__init__.py")
    prompt = SINGLE_FILE_PROMPT.format(file_path=path)
    return _invoke_agent(claude_cli, prompt)


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
            f"Expected at most 2x, not proportional to 5 files."
        )

    def test_batch_no_duplicate_reads(self, batch_python):
        reads = batch_python.report.conventions_read
        unique = set(reads)
        assert len(unique) == len(reads), (
            f"Duplicate convention reads in batch: {reads}"
        )


class TestTokenEfficiency:
    """Batch editing should not cost proportionally more than single."""

    def test_batch_token_ratio(self, single_python, batch_python):
        if single_python.input_tokens == 0:
            pytest.skip("No token data")
        ratio = batch_python.input_tokens / single_python.input_tokens
        print(f"\n  Single: {single_python.input_tokens:,} input tokens, ${single_python.cost_usd:.4f}")
        print(f"  Batch:  {batch_python.input_tokens:,} input tokens, ${batch_python.cost_usd:.4f}")
        print(f"  Ratio:  {ratio:.2f}x")
        assert ratio < 3.0, (
            f"Batch used {ratio:.1f}x tokens vs single — possible convention re-consumption"
        )

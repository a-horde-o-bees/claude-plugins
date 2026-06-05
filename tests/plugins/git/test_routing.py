"""Local git-mechanics tests — no GitHub.

Exercises the pieces of the submodule-routing feature that can run against
`file://` remotes and local git: `_origin_slug` URL parsing and `detect.sh`'s
routing-gap detection. Branch protection and `gh pr` require real GitHub and
are validated in the deferred live e2e, not here.
"""

import subprocess
from pathlib import Path

import pr

ROOT = Path(__file__).resolve().parents[3]
DETECT = ROOT / "plugins/git/skills/git-doctor/scripts/detect.sh"


def _git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    _git(["init", "-q", "-b", "main"], path)
    _git(["config", "user.email", "t@example.com"], path)
    _git(["config", "user.name", "tester"], path)
    (path / "f.txt").write_text("x\n")
    _git(["add", "."], path)
    _git(["commit", "-qm", "init"], path)


def test_origin_slug_https(tmp_path, monkeypatch):
    _init_repo(tmp_path)
    _git(["remote", "add", "origin", "https://github.com/owner/repo.git"], tmp_path)
    monkeypatch.chdir(tmp_path)
    assert pr._origin_slug() == "owner/repo"


def test_origin_slug_ssh(tmp_path, monkeypatch):
    _init_repo(tmp_path)
    _git(["remote", "add", "origin", "git@github.com:owner/repo.git"], tmp_path)
    monkeypatch.chdir(tmp_path)
    assert pr._origin_slug() == "owner/repo"


def test_origin_slug_none_without_remote(tmp_path, monkeypatch):
    _init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert pr._origin_slug() is None


def test_detect_flags_and_clears_routing_gap(tmp_path):
    sub = tmp_path / "subrepo"
    _init_repo(sub)
    superp = tmp_path / "super"
    _init_repo(superp)
    _git(["-c", "protocol.file.allow=always", "submodule", "add", f"file://{sub}", "sub"], superp)
    _git(["commit", "-qm", "add sub"], superp)

    # No `branch =` declared → routing gap flagged.
    r = subprocess.run(["sh", str(DETECT)], cwd=superp, capture_output=True, text=True)
    assert "submodule-routing" in r.stdout
    assert "sub" in r.stdout

    # Declaring the native key clears the gap.
    _git(["config", "-f", ".gitmodules", "submodule.sub.branch", "main"], superp)
    r2 = subprocess.run(["sh", str(DETECT)], cwd=superp, capture_output=True, text=True)
    assert "submodule-routing" not in r2.stdout

"""Tests for the pure classifiers in git-pr-merge/scripts/pr.py.

Only the pure functions are exercised — the gh/git-touching subcommands
(`gate`, `protection`, `repo-route`) are integration-tested live, not here.
"""

import pr
import pytest


# --- classify_repo: per-repo routing decision -------------------------------

@pytest.mark.parametrize(
    "perm,is_fork,protected,update_mode,has_edits,xint,expected",
    [
        # owned (write/admin), unprotected working branch → direct push
        ("ADMIN", False, False, "", True, None,
         {"integration": "direct", "sync": "pin", "upstream": "none"}),
        ("WRITE", False, False, "", True, None,
         {"integration": "direct", "sync": "pin", "upstream": "none"}),
        # owned, protected working branch → recursive PR lifecycle
        ("ADMIN", False, True, "", True, None,
         {"integration": "pr", "sync": "pin", "upstream": "none"}),
        # owned fork, unprotected overlay branch → direct to our fork
        ("ADMIN", True, False, "", True, None,
         {"integration": "direct", "sync": "pin", "upstream": "fork"}),
        # vendored read-only → pin-only, never pushed
        ("READ", False, False, "", False, None,
         {"integration": "read-only", "sync": "pin", "upstream": "none"}),
        ("NONE", False, False, "", False, None,
         {"integration": "read-only", "sync": "pin", "upstream": "none"}),
        # track via native update= (rebase/merge) flips sync to track
        ("ADMIN", True, False, "rebase", True, None,
         {"integration": "direct", "sync": "track", "upstream": "fork"}),
        ("ADMIN", True, False, "merge", True, None,
         {"integration": "direct", "sync": "track", "upstream": "fork"}),
        # update=none / checkout / unset all mean pin
        ("ADMIN", False, False, "none", True, None,
         {"integration": "direct", "sync": "pin", "upstream": "none"}),
        ("ADMIN", False, False, "checkout", True, None,
         {"integration": "direct", "sync": "pin", "upstream": "none"}),
    ],
)
def test_classify_repo_axes(perm, is_fork, protected, update_mode, has_edits, xint, expected):
    got = pr.classify_repo(perm, is_fork, protected, update_mode, has_edits, xint)
    for k, v in expected.items():
        assert got[k] == v
    assert got["gaps"] == []


def test_classify_repo_x_integration_overrides_detection():
    # protected would detect 'pr'; explicit native override forces direct
    assert pr.classify_repo("ADMIN", False, True, "", True, "direct")["integration"] == "direct"
    # unprotected would detect 'direct'; override forces pr
    assert pr.classify_repo("ADMIN", False, False, "", True, "pr")["integration"] == "pr"
    # override read-only even when writable
    assert pr.classify_repo("ADMIN", False, False, "", True, "read-only")["integration"] == "read-only"


def test_classify_repo_gap_permission_undeterminable():
    for bad in (None, "", "WAT"):
        out = pr.classify_repo(bad, False, False, "", False)
        assert "permission-undeterminable" in out["gaps"]
        assert out["integration"] == "read-only"  # not writable ⇒ never push on unknown perm


def test_classify_repo_gap_edits_to_readonly():
    out = pr.classify_repo("READ", False, False, "", True)
    assert "edits-to-readonly" in out["gaps"]
    # no edits ⇒ pin-only is fine, no gap
    assert pr.classify_repo("READ", False, False, "", False)["gaps"] == []


def test_classify_repo_case_insensitive_perm_and_update():
    assert pr.classify_repo("admin", False, False, "REBASE", True)["sync"] == "track"
    assert pr.classify_repo("admin", False, False, "", True)["integration"] == "direct"


# --- reconcile_merge: pin-advance guard -------------------------------------

@pytest.mark.parametrize(
    "merge_sha,head,verdict",
    [
        ("abc123def456", "abc123def456", "ok"),     # exact
        ("abc123def456", "abc123", "ok"),           # head is short prefix
        ("abc123", "abc123def456", "ok"),           # merge is short prefix
        ("abc123def456", "deadbeef", "mismatch"),   # different shas
        ("", "abc123", "unknown"),                  # no merge commit
        ("abc123", "", "unknown"),                  # no local head
        ("  abc123  ", "abc123", "ok"),             # whitespace tolerant
    ],
)
def test_reconcile_merge(merge_sha, head, verdict):
    assert pr.reconcile_merge(merge_sha, head) == verdict


# --- classify_required / classify_gate: existing gate edges -----------------

def test_classify_required_protected_with_no_required_contexts_is_none():
    # A protected base whose protection lists no required checks must not
    # false-pass: status is 'none', not 'success'.
    status, adv = pr.classify_required(
        [{"name": "lint", "status": "COMPLETED", "conclusion": "FAILURE"}], [])
    assert status == "none"
    assert any(a["name"] == "lint" for a in adv)  # non-required failure → advisory


def test_classify_required_missing_required_run_is_pending():
    status, _ = pr.classify_required([], ["test"])
    assert status == "pending"  # required context with no run yet waits


def test_classify_required_nonrequired_never_gates():
    status, adv = pr.classify_required(
        [{"name": "markdown-lint", "status": "COMPLETED", "conclusion": "FAILURE"},
         {"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}],
        ["test"])
    assert status == "success"
    assert adv == [{"name": "markdown-lint", "state": "failing"}]


def test_classify_gate_review_required_only_blocks_when_protected():
    pr_obj = {"reviewDecision": "REVIEW_REQUIRED", "statusCheckRollup": []}
    gated = pr.classify_gate(pr_obj, 0, protection_enforced=True, required_contexts=[])
    assert any(b["dimension"] == "review" for b in gated["blockers"])
    solo = pr.classify_gate(pr_obj, 0, protection_enforced=False, required_contexts=[])
    assert not any(b["dimension"] == "review" for b in solo["blockers"])
    assert solo["merge_ready"] is True  # solo path, no hard blockers

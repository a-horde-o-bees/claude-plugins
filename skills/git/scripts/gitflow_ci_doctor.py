"""CI doctor: workflow hardening audit (pin/permissions/timeout/concurrency
findings, SHA resolution) and required-check reconciliation."""
import json
import re
from pathlib import Path

from gitflow_core import _default_branch, run

try:
    import yaml
except ImportError:  # structural workflow checks degrade to regex-only
    yaml = None

HIGH, MEDIUM, LOW = "high", "medium", "low"

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
# First-party actions GitHub owns; pinning still recommended but lower risk.
FIRST_PARTY = ("actions/", "github/")


def _ref_of(uses):
    """The ref after '@' in a `uses:` value, or None for a local/docker action."""
    if uses.startswith("./") or uses.startswith("docker://"):
        return None
    return uses.split("@", 1)[1] if "@" in uses else ""


def audit_uses(uses):
    """Return a pin finding for one `uses:` value, or None if acceptably pinned."""
    ref = _ref_of(uses)
    if ref is None:
        return None  # local or docker action — not a mutable upstream tag
    if SHA_RE.match(ref):
        return None  # immutable SHA pin — good
    action = uses.split("@", 1)[0]
    party = "first-party" if action.startswith(FIRST_PARTY) else "third-party"
    return {
        "check": "unpinned-action",
        "severity": HIGH,
        "action": action,
        "ref": ref,
        "detail": f"{action} pinned to mutable ref '{ref or '(none)'}' ({party})",
        "fix": f"pin to a full commit SHA: resolve `gh api repos/{action}/commits/{ref or 'TAG'} --jq .sha`, "
               f"then `uses: {action}@<sha> # {ref or 'vX.Y.Z'}`",
    }


def audit_workflow(text, data):
    """Findings for one workflow. `data` is the parsed YAML (or None if unparseable);
    `text` is the raw source (used for a regex fallback on `uses:` lines)."""
    findings = []

    # --- unpinned actions (parse-independent regex over uses: lines) ---
    for line in text.splitlines():
        m = USES_RE.match(line)
        if m:
            f = audit_uses(m.group(1).strip())
            if f:
                findings.append(f)

    if not isinstance(data, dict):
        findings.append({"check": "unparseable", "severity": HIGH,
                         "detail": "workflow YAML did not parse — structural checks skipped",
                         "fix": "run actionlint / yamllint to locate the syntax error"})
        return findings

    jobs = data.get("jobs") or {}
    top_perms = "permissions" in data
    # `on` may parse as the bareword key True in YAML 1.1 (on: → True:)
    on = data.get("on", data.get(True, {}))
    if not isinstance(on, dict):
        on = {k: None for k in (on if isinstance(on, list) else [on])}
    push_spec = on.get("push")
    # PR-feedback = superseded runs are possible: a pull_request trigger, or a
    # push that targets branches (not a tags-only release push).
    push_branches = "push" in on and not (
        isinstance(push_spec, dict) and "tags" in push_spec and "branches" not in push_spec
    )
    is_pr_feedback = "pull_request" in on or push_branches

    # --- least-privilege permissions ---
    if not top_perms:
        ungoverned = [j for j, spec in jobs.items()
                      if not (isinstance(spec, dict) and "permissions" in spec)]
        if ungoverned:
            findings.append({
                "check": "missing-permissions", "severity": HIGH,
                "detail": f"no top-level `permissions:` and {len(ungoverned)} job(s) without one "
                          f"({', '.join(sorted(ungoverned))}) — GITHUB_TOKEN defaults to broad write",
                "fix": "add top-level `permissions:\\n  contents: read`, escalate per-job only where a job writes",
            })

    # --- per-job: timeout (medium) ---
    for name, spec in jobs.items():
        if not isinstance(spec, dict):
            continue
        if "timeout-minutes" not in spec:
            findings.append({
                "check": "missing-timeout", "severity": MEDIUM, "job": name,
                "detail": f"job '{name}' has no `timeout-minutes` — a hung run burns to the 6h ceiling",
                "fix": f"add `timeout-minutes: <n>` to job '{name}' (~15 for typical CI)",
            })

    # --- concurrency on PR-feedback workflows (low) ---
    if is_pr_feedback and "concurrency" not in data:
        findings.append({
            "check": "missing-concurrency", "severity": LOW,
            "detail": "PR-feedback workflow with no `concurrency:` — superseded runs are not cancelled",
            "fix": "add `concurrency:\\n  group: ${{ github.workflow }}-${{ github.ref }}\\n  cancel-in-progress: true`",
        })

    return findings


def _resolve_pin(finding, cwd):
    """Fill an unpinned-action finding with its resolved SHA and replacement line."""
    action, ref = finding.get("action"), finding.get("ref")
    if not action or not ref:
        return
    rc, sha, _ = run(["gh", "api", f"repos/{action}/commits/{ref}", "--jq", ".sha"], cwd)
    if rc == 0 and SHA_RE.match(sha):
        finding["resolved_sha"] = sha
        finding["pinned_line"] = f"uses: {action}@{sha} # {ref}"


def cmd_ci_audit(a):
    wf_dir = Path(a.cwd) / a.dir
    files = sorted([*wf_dir.glob("*.yml"), *wf_dir.glob("*.yaml")]) if wf_dir.is_dir() else []
    results = []
    counts = {HIGH: 0, MEDIUM: 0, LOW: 0}
    for f in files:
        text = f.read_text()
        try:
            data = yaml.safe_load(text) if yaml else None
        except Exception:
            data = None
        findings = audit_workflow(text, data)
        for fi in findings:
            counts[fi["severity"]] = counts.get(fi["severity"], 0) + 1
            if a.resolve and fi["check"] == "unpinned-action":
                _resolve_pin(fi, a.cwd)
        results.append({"file": str(f), "findings": findings})
    print(json.dumps({
        "dir": str(wf_dir),
        "workflow_count": len(files),
        "yaml_available": yaml is not None,
        "clean": all(not r["findings"] for r in results),
        "severity_counts": counts,
        "results": results,
    }, indent=2))


def _job_names(wf_dir):
    names = set()
    if not (yaml and wf_dir.is_dir()):
        return names
    for f in [*wf_dir.glob("*.yml"), *wf_dir.glob("*.yaml")]:
        try:
            data = yaml.safe_load(f.read_text())
        except Exception:
            continue
        if isinstance(data, dict):
            for name, spec in (data.get("jobs") or {}).items():
                # the check name is the job's `name:` if set, else the job id
                names.add(spec["name"] if isinstance(spec, dict) and spec.get("name") else name)
    return names


def cmd_ci_reconcile(a):
    branch = a.branch or _default_branch(a.cwd)
    rc, out, _ = run(["gh", "api", f"repos/{{owner}}/{{repo}}/branches/{branch}/protection"], a.cwd)
    if rc != 0:
        print(json.dumps({"branch": branch, "protection": False,
                          "note": "no branch protection — nothing to reconcile"}))
        return
    data = json.loads(out)
    required = set((data.get("required_status_checks") or {}).get("contexts") or [])
    jobs = _job_names(Path(a.cwd) / a.dir)
    # A required context may name a job, or be an external check (CodeQL, a bot) — we
    # can only confirm the ones that should map to a local job. Flag required names
    # that match no job (likely stuck-pending) and local jobs not marked required.
    print(json.dumps({
        "branch": branch,
        "protection": True,
        "required_contexts": sorted(required),
        "job_names": sorted(jobs),
        "required_without_matching_job": sorted(required - jobs),
        "jobs_not_required": sorted(jobs - required),
        "note": "required_without_matching_job may hang as 'Expected — waiting' (or be an external check); "
                "jobs_not_required gate nothing until added to protection",
    }, indent=2))

"""Release flow (preflight, version validation, atomic cut) and the read-only
git passthrough for boxed repos."""
import json
import re
import subprocess
import sys
from pathlib import Path

from gitflow_core import _default_branch, die, run

SEMVERISH_TAG = re.compile(r"^v?[0-9]+\.[0-9]+\.[0-9]+$")


def _version_tuple(v):
    """Numeric tuple from a version string ('v1.2.3' → (1,2,3)), or None."""
    m = re.match(r"^v?(\d+(?:\.\d+)*)$", (v or "").strip())
    return tuple(int(p) for p in m.group(1).split(".")) if m else None


def cmd_release_preflight(a):
    """Release preconditions + the synthesis range. Judgment stays with the
    caller: the intent gate, methodology, synthesis, and review."""
    cwd = a.cwd
    default = _default_branch(cwd)
    _, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if branch != default:
        die(f"releases cut from the default branch ({default}); currently on {branch} — "
            f"switch or rebase the change onto it first")
    rc, _, _ = run(["git", "diff", "--quiet"], cwd)
    if rc != 0:
        die("working tree has unstaged changes — clean or commit before releasing")
    rc, _, _ = run(["git", "diff", "--cached", "--quiet"], cwd)
    if rc != 0:
        die("working tree has staged changes — commit or reset before releasing")
    run(["git", "fetch", "origin", default, "--quiet"], cwd, check=True)
    _, head, _ = run(["git", "rev-parse", "HEAD"], cwd, check=True)
    _, origin, _ = run(["git", "rev-parse", f"origin/{default}"], cwd, check=True)
    if head != origin:
        die(f"local {default} not aligned with origin/{default} — pull or push first")
    _, tags, _ = run(["git", "tag", "--sort=-version:refname"], cwd)
    last_tag = next((t for t in tags.splitlines() if SEMVERISH_TAG.match(t)), "")
    commit_range = f"{last_tag}..HEAD" if last_tag else "HEAD"
    _, count, _ = run(["git", "rev-list", "--count", commit_range], cwd, check=True)
    # Declared submodules, for the verb's opt-in recursion (--recurse-submodules);
    # emitted unconditionally — enumeration is cheap and the caller binds it only on opt-in.
    _, sub_out, _ = run(["git", "submodule", "status"], cwd)
    submodules = [line.split()[1] for line in sub_out.splitlines() if len(line.split()) >= 2]
    print(json.dumps({
        "default_branch": default, "head_sha": head, "last_tag": last_tag or None,
        "commit_range": commit_range, "commits_since": int(count or "0"),
        "submodules": submodules,
    }, indent=1))


def _release_validate(version, current, tag, cwd):
    fv, cv = _version_tuple(version), _version_tuple(current)
    if fv is None or cv is None:
        die(f"cannot compare versions {version!r} and {current!r} — not dotted-numeric")
    if fv <= cv:
        die(f"version {version} is not greater than current ({current}) — "
            f"pass a higher version or omit to use the recommendation")
    rc, _, _ = run(["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}"], cwd)
    if rc == 0:
        die(f"tag {tag} already exists — pass a different version, or delete the tag if made in error")


def cmd_release_validate(a):
    tag = a.tag or f"v{a.version}"
    _release_validate(a.version, a.current, tag, a.cwd)
    print(json.dumps({"version": a.version, "current": a.current, "tag": tag, "ok": True}))


def cmd_release_cut(a):
    """Stage the named manifests + CHANGELOG.md, commit, annotated-tag, and push
    branch + tag together. Progressive output so a mid-way failure names what
    completed. The caller has already applied the CHANGELOG/manifest edits."""
    cwd = a.cwd
    tag = a.tag or f"v{a.version}"
    _release_validate(a.version, a.current, tag, cwd)
    default = _default_branch(cwd)
    run(["git", "add", "--"] + a.manifest + ["CHANGELOG.md"], cwd, check=True)
    print(f"staged: {', '.join(a.manifest)} CHANGELOG.md")
    run(["git", "commit", "-m", f"release {tag}"], cwd, check=True)
    _, sha, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd)
    print(f"committed: {sha} release {tag}")
    run(["git", "tag", "-a", tag, "-m", f"release {tag}"], cwd, check=True)
    print(f"tagged: {tag} (annotated)")
    run(["git", "push", "origin", default, tag], cwd, check=True)
    print(f"pushed: {default} + {tag} to origin")


# Read-only git subcommands the boxed doorway may pass through — history and
# state inspection only; anything that can write refs, files, or config is out.
READ_OK = {"diff", "log", "show", "status", "describe", "shortlog", "rev-parse",
           "ls-files", "ls-tree", "ls-remote", "blame", "reflog", "grep", "tag"}
TAG_WRITE_FLAGS = {"-a", "-d", "-f", "-s", "-u", "-m", "-F", "--delete", "--force", "--annotate"}


def cmd_read(a):
    """Read-only git passthrough for judgment steps that inspect history (diff
    seeds, log synthesis) inside a boxed repo. Refuses write-capable forms."""
    args = a.git_args
    if args and args[0] == "--":
        args = args[1:]
    if not args or args[0] not in READ_OK:
        die(f"read passthrough allows only {', '.join(sorted(READ_OK))} — got {args[:1] or 'nothing'}")
    if args[0] == "tag" and (set(args) & TAG_WRITE_FLAGS or not all(x.startswith("-") for x in args[1:])):
        die("read passthrough allows only tag listing (flags like --sort/--list), not tag creation/deletion")
    p = subprocess.run(["git", *args], cwd=a.cwd, text=True)
    sys.exit(p.returncode)


MANIFEST_NAMES = ("plugin.json", "package.json", "Cargo.toml", "pyproject.toml")
SKIP_DIRS = {".git", ".venv", "node_modules"}


def cmd_release_bootstrap_detect(a):
    """Detection pass for the release-methodology bootstrap: existing manifests,
    CHANGELOG, tags, auto-bump hook, release workflow. Composing the methodology
    from these is the caller's judgment."""
    root = Path(a.cwd)
    manifests = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if len(rel.parts) > 4 or any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.is_file() and (p.name in MANIFEST_NAMES or p.name.endswith(".gemspec")):
            manifests.append(str(rel))
    _, tags_out, _ = run(["git", "tag", "--sort=-creatordate"], a.cwd)
    existing_tags = tags_out.splitlines()[:5]
    tag_format = "v<x.y.z>" if existing_tags and SEMVERISH_TAG.match(existing_tags[0]) else None
    hook = root / ".githooks" / "pre-commit"
    auto_bump_hook = bool(hook.is_file() and re.search(r"bump|version", hook.read_text(), re.I))
    print(json.dumps({
        "manifest_candidates": manifests,
        "has_changelog": (root / "CHANGELOG.md").is_file(),
        "existing_tags": existing_tags,
        "tag_format": tag_format,
        "auto_bump_hook": auto_bump_hook,
        "github_release_workflow": (root / ".github" / "workflows" / "release.yml").is_file(),
    }, indent=1))

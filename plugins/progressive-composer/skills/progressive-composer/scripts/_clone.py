"""Sparse-checkout and drift-detection primitives.

Replaces the prior full-clone + shared-cache model. Each composed or
installed skill embeds the upstream skill folder it depends on as a
sparse-checkout at a pinned commit, stored at
`<skill>/sources/<source-slug>/`. Drift detection uses `git ls-remote`
which is non-mutating — no local clone state is touched.
"""

import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def sparse_checkout_skill(
    url: str,
    skill_path: str,
    ref: str | None,
    dest: Path,
) -> str:
    """Clone just one skill folder from upstream into `dest`. Returns commit SHA.

    Uses `git clone --filter=blob:none --no-checkout` plus
    `git sparse-checkout set <skill_path>` and a checkout to fetch only
    the named subdirectory. After the operation, `dest` contains the
    contents of `<repo>/<skill_path>/` at the resolved commit (without
    the `.git` directory — we discard the partial clone since drift
    detection runs against upstream via `ls-remote`, not local refs).
    """
    dest = dest.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)

    # Clone into a temp directory adjacent to dest so we can move the
    # resolved sparse subtree into place atomically.
    with tempfile.TemporaryDirectory(prefix=".sparse-", dir=str(dest.parent)) as tmp:
        tmp_path = Path(tmp)
        clone_dir = tmp_path / "repo"

        clone_args = [
            "git",
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            "--depth",
            "1",
        ]
        if ref:
            clone_args.extend(["--branch", ref])
        clone_args.extend([url, str(clone_dir)])
        subprocess.run(clone_args, check=True, capture_output=True, text=True)

        subprocess.run(
            ["git", "-C", str(clone_dir), "sparse-checkout", "init", "--cone"],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(clone_dir), "sparse-checkout", "set", skill_path],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(clone_dir), "checkout"],
            check=True,
            capture_output=True,
            text=True,
        )

        commit = subprocess.run(
            ["git", "-C", str(clone_dir), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        skill_subdir = clone_dir / skill_path
        if not skill_subdir.is_dir():
            raise FileNotFoundError(
                f"skill path {skill_path!r} not found in {url}@{ref or 'default'}"
            )

        shutil.copytree(skill_subdir, dest)

    return commit


def ls_remote_head(url: str, ref: str) -> str:
    """Return the SHA at upstream's named ref via `git ls-remote`.

    Non-mutating — no local clone state is touched. The returned SHA is
    suitable for comparison against composition.md's pinned `commit`
    field for drift detection.

    `ref` is matched against branches first, then tags. Pass a fully
    qualified `refs/heads/<branch>` or `refs/tags/<tag>` to bypass the
    heuristic.
    """
    result = subprocess.run(
        ["git", "ls-remote", url, ref],
        capture_output=True,
        text=True,
        check=True,
    )
    line = result.stdout.strip().splitlines()
    if not line:
        # Try fully-qualified ref forms before giving up
        for candidate in (f"refs/heads/{ref}", f"refs/tags/{ref}"):
            qualified = subprocess.run(
                ["git", "ls-remote", url, candidate],
                capture_output=True,
                text=True,
                check=True,
            )
            qualified_lines = qualified.stdout.strip().splitlines()
            if qualified_lines:
                return qualified_lines[0].split("\t")[0]
        raise RuntimeError(f"ref {ref!r} not found at {url}")
    return line[0].split("\t")[0]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

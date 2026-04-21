#!/bin/bash
# Cut a release tag for this plugin marketplace.
#
# Usage: scripts/release.sh <x.y.z>
#
# Option E release flow:
#   - Tags live on main; no release branches.
#   - plugin.json auto-bumps z on every commit touching the plugin tree.
#     Release commits stage only plugin.json (+ optionally root CHANGELOG),
#     which the pre-commit hook recognizes as "no plugin code changes" and
#     skips the auto-bump.
#
# What this script does:
#   1. Precondition checks: on main, clean tree, aligned with origin/main,
#      version is semver, version > current, tag doesn't exist.
#   2. Bump plugins/*/.claude-plugin/plugin.json to the new version.
#   3. Leave staging + committing + tagging + pushing to the operator so
#      CHANGELOG curation and release-commit review happen with eyes on.
#
# Exits non-zero on any precondition failure. git state is touched only
# by the plugin.json bump (already written — discard with `git checkout
# -- plugins/*/.claude-plugin/plugin.json` to abort before committing).

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: scripts/release.sh <x.y.z>" >&2
    exit 64
fi

version="$1"
tag="v${version}"

if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Version must match x.y.z (got: $version)" >&2
    exit 64
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

# Precondition: on main
current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$current_branch" != "main" ]; then
    echo "Releases cut from main; currently on $current_branch" >&2
    exit 1
fi

# Precondition: working tree clean
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Working tree has uncommitted changes — stash or commit before releasing" >&2
    exit 1
fi

# Precondition: aligned with origin/main
git fetch origin main --quiet
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "Local main is not aligned with origin/main — pull or push before releasing" >&2
    exit 1
fi

# Precondition: tag doesn't exist
if git rev-parse --verify --quiet "refs/tags/$tag" >/dev/null; then
    echo "Tag $tag already exists" >&2
    exit 1
fi

# Bump each plugin's plugin.json (semver-ascending check included)
bumped=()
for manifest in plugins/*/.claude-plugin/plugin.json; do
    [ -f "$manifest" ] || continue
    current=$(python3 -c "import json; print(json.load(open('$manifest'))['version'])")
    if ! python3 - "$current" "$version" <<'PY'
import sys
def parse(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))
current, new = sys.argv[1], sys.argv[2]
sys.exit(0 if parse(new) > parse(current) else 1)
PY
    then
        echo "Error: $manifest version $current is not less than target $version" >&2
        exit 1
    fi
    python3 - "$manifest" "$version" <<'PY'
import json, sys
path, new_version = sys.argv[1], sys.argv[2]
with open(path) as f:
    data = json.load(f)
data["version"] = new_version
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
    bumped+=("$manifest: $current → $version")
done

if [ ${#bumped[@]} -eq 0 ]; then
    echo "No plugin manifests found under plugins/*/.claude-plugin/plugin.json" >&2
    exit 1
fi

echo "Bumped plugin manifests:"
for line in "${bumped[@]}"; do
    echo "  $line"
done

echo ""
echo "Next steps (operator review + curate CHANGELOG, then commit + tag + push):"
echo ""
echo "  1. Edit CHANGELOG.md — move the [Unreleased] contents into a new"
echo "     ## [$version] - \$(date -u +%Y-%m-%d) section, then reset [Unreleased]"
echo "     to the placeholder."
echo "  2. git add plugins/*/.claude-plugin/plugin.json CHANGELOG.md"
echo "  3. git commit -m 'release $tag'"
echo "     (pre-commit hook skips auto-bump because no plugins/<name>/ files"
echo "     other than plugin.json are staged)"
echo "  4. git tag -a '$tag' -m 'release $tag'"
echo "  5. git push origin main '$tag'"
echo ""
echo "release.yml fires on tag push: verifies tag format + plugin.json"
echo "version alignment, runs tests, creates GitHub release."
echo ""
echo "Users install via:"
echo "  /plugin marketplace add a-horde-o-bees/claude-plugins@$tag"

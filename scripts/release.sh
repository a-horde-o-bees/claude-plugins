#!/bin/bash
# Cut a release of one or more plugins in this marketplace.
#
# Usage: scripts/release.sh <x.y.z>
#
# For x.y.0 (new minor line):
#   - Creates release/x.y branch at current main
#   - Bumps every plugins/*/plugin.json version to x.y.0
#   - Prepends a release entry to CHANGELOG.md (operator fills in details)
#   - Updates .claude-plugin/marketplace.stable.json to pin ref:vx.y.0
#   - Commits "release x.y.0", tags vx.y.0, pushes branch + tag + main
#
# For x.y.z where z > 0 (patch on existing release branch):
#   - Requires checkout on release/x.y already
#   - Requires fix commits already in place on the branch
#   - Bumps plugin.json to x.y.z, prepends CHANGELOG, tags vx.y.z, pushes
#
# Exits non-zero on any precondition failure; git state is untouched.

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: scripts/release.sh <x.y.z>" >&2
    exit 64
fi

version="$1"

if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Version must match x.y.z (got: $version)" >&2
    exit 64
fi

major="${version%%.*}"
minor_patch="${version#*.}"
minor="${minor_patch%%.*}"
patch="${version##*.}"
release_branch="release/${major}.${minor}"
tag="v${version}"

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Working tree has uncommitted changes — stash or commit before releasing" >&2
    exit 1
fi

current_branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$patch" = "0" ]; then
    # Minor release — cut from main
    if [ "$current_branch" != "main" ]; then
        echo "Minor releases cut from main; currently on $current_branch" >&2
        exit 1
    fi
    if git show-ref --verify --quiet "refs/heads/$release_branch"; then
        echo "Branch $release_branch already exists locally — patch release?" >&2
        exit 1
    fi
    git checkout -b "$release_branch"
else
    # Patch release — must already be on the matching release branch
    if [ "$current_branch" != "$release_branch" ]; then
        echo "Patch releases cut from $release_branch; currently on $current_branch" >&2
        exit 1
    fi
fi

if git rev-parse --verify --quiet "refs/tags/$tag" >/dev/null; then
    echo "Tag $tag already exists" >&2
    exit 1
fi

# Bump plugin manifest versions (one authority — marketplace entries must not duplicate)
for manifest in plugins/*/.claude-plugin/plugin.json; do
    [ -f "$manifest" ] || continue
    python3 - <<PY "$manifest" "$version"
import json, sys
path, new_version = sys.argv[1], sys.argv[2]
data = json.loads(open(path).read())
data["version"] = new_version
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
    echo "Bumped $manifest to $version"
done

# Update stable marketplace pointer
stable_manifest=".claude-plugin/marketplace.stable.json"
if [ -f "$stable_manifest" ]; then
    python3 - <<PY "$stable_manifest" "$tag"
import json, sys
path, new_ref = sys.argv[1], sys.argv[2]
data = json.loads(open(path).read())
for plugin in data.get("plugins", []):
    source = plugin.get("source")
    if isinstance(source, dict) and "ref" in source:
        source["ref"] = new_ref
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
    echo "Pointed $stable_manifest at $tag"
fi

# Prepend a CHANGELOG entry stub (operator edits before commit)
if [ -f CHANGELOG.md ]; then
    date_stamp="$(date -u +%Y-%m-%d)"
    tmpfile="$(mktemp)"
    {
        echo "## [$version] - $date_stamp"
        echo ""
        echo "### Added"
        echo ""
        echo "### Changed"
        echo ""
        echo "### Fixed"
        echo ""
        cat CHANGELOG.md
    } > "$tmpfile"
    mv "$tmpfile" CHANGELOG.md
    echo "Prepended changelog stub for $version — fill in before committing"
fi

echo ""
echo "Staged changes:"
git status --short
echo ""
echo "Next steps:"
echo "  1. Edit CHANGELOG.md to describe what's in this release"
echo "  2. git add -u"
echo "  3. git commit -m 'release $version'"
echo "  4. git tag -a '$tag' -m 'release $version'"
echo "  5. git push origin $release_branch"
echo "  6. git push origin '$tag'"
echo ""
echo "Users install this release via the stable channel:"
echo "  /plugin marketplace add https://raw.githubusercontent.com/a-horde-o-bees/claude-plugins/main/.claude-plugin/marketplace.stable.json"

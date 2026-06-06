#!/usr/bin/env sh
# git-roots.sh — locate git roots for a (super)project, gating on submodule conformance.
# Mechanical helper: emits paths, never file dumps. POSIX sh, no bashisms — runs on stock
# macOS bash 3.2, Linux, WSL, git-bash.
#
# Modes (first arg, default `roots`):
#   self   -> print this script's own directory (canonical, cwd-independent); exit 0.
#             For a script to find its siblings at runtime. (SKILL.md files should use the
#             official ${CLAUDE_SKILL_DIR} substitution for bundled-file paths instead.)
#   root   -> print the superproject root, one line; exit 0. Answers even under drift —
#             the project root is knowable regardless of submodule conformance.
#   roots  -> every operable root, submodules first (deepest first), superproject last;
#             exit 0. Drift -> per-submodule state table on stderr, exit 1 (run git-doctor).
#   (any mode) not a git repo -> error on stderr, exit 2.
#
# Caller (roots): `for r in $(sh "$DIR"/git-roots.sh roots); do git -C "$r" …; done`
set -eu

mode=${1:-roots}

if [ "$mode" = self ]; then
  CDPATH= cd -- "$(dirname -- "$0")" && pwd
  exit 0
fi
case "$mode" in roots|root) ;; *)
  echo "usage: git-roots.sh [roots|root|self]" >&2; exit 2 ;;
esac

top=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "git-roots: not a git repository" >&2; exit 2; }

# Climb to the outermost superproject WITHOUT git's --show-superproject-working-tree:
# that keys off the gitlink, which a broken submodule lacks, so from inside an orphaned
# submodule git reports no parent and the breakage above goes unseen. Instead climb the
# filesystem, but only while a real submodule relationship holds — else an unrelated
# ancestor repo (e.g. ~/.claude) would be mistaken for the superproject. Relationship is
# proven, linkage-independent, by either signal:
#   (a) the child's .git is an absorbed gitdir FILE (monaco: `gitdir: ../.git/modules/…`), or
#   (b) the parent's .gitmodules declares the child's path.
# A parent satisfying neither is a genuine boundary — stop there.
sup=$top
while :; do
  parent=""
  d=$(dirname "$sup")
  while [ "$d" != "/" ]; do
    [ -e "$d/.git" ] && { parent=$d; break; }
    d=$(dirname "$d")
  done
  [ -z "$parent" ] && break
  rel=${sup#"$parent"/}
  is_sub=no
  # (a) certain test: sup's gitdir resolves under parent's .git/modules/ — git's own
  #     layout for an absorbed submodule. A worktree (.git/worktrees/) or unrelated
  #     redirected repo resolves elsewhere and is correctly rejected.
  if [ -f "$sup/.git" ]; then
    gd=$(sed -n 's/^gitdir: //p' "$sup/.git")
    abs=$(cd "$sup" 2>/dev/null && cd "$(dirname "$gd")" 2>/dev/null && pwd)/$(basename "$gd")
    if [ -d "$parent/.git" ]; then pgit=$(cd "$parent/.git" && pwd)
    else pgit=$(cd "$parent" 2>/dev/null && cd "$(dirname "$(sed -n 's/^gitdir: //p' "$parent/.git")")" 2>/dev/null && pwd)/$(basename "$(sed -n 's/^gitdir: //p' "$parent/.git")"); fi
    case "$abs" in "$pgit"/modules/*) is_sub=yes ;; esac
  fi
  # (b) certain test: parent's .gitmodules explicitly declares sup's path.
  if [ "$is_sub" = no ] && [ -f "$parent/.gitmodules" ]; then
    git config --file "$parent/.gitmodules" --get-regexp '\.path$' 2>/dev/null \
      | awk '{print $2}' | grep -qx "$rel" && is_sub=yes
  fi
  [ "$is_sub" = yes ] && sup=$parent || break
done

# `root`: the superproject path, in one call — determinable regardless of conformance.
if [ "$mode" = root ]; then printf '%s\n' "$sup"; exit 0; fi

# Three views of "what submodules exist", as newline-lists of paths relative to sup:
#   on_disk  — nested .git found by filesystem scan (catches UNDECLARED repos)
#   declared — .path entries in .gitmodules
#   linked   — staged gitlinks (mode 160000) in the superproject index
on_disk=$(cd "$sup" && find . -mindepth 2 \
            \( -name node_modules -o -name .venv -o -path '*/.git/*' \) -prune \
            -o -name .git -print 2>/dev/null | sed 's#^\./##; s#/\.git$##' | sort -u)
declared=$(git config --file "$sup/.gitmodules" --get-regexp '\.path$' 2>/dev/null \
            | awk '{print $2}' | sort -u)
linked=$(git -C "$sup" ls-files --stage 2>/dev/null \
            | awk '$1=="160000"{print $4}' | sort -u)

candidates=$(printf '%s\n%s\n' "$on_disk" "$declared" | grep -v '^$' | sort -u)

has() { printf '%s\n' "$2" | grep -qx "$1"; }

drift=0
report=""
for p in $candidates; do
  d=no; o=no; l=no
  has "$p" "$declared" && d=yes
  has "$p" "$on_disk"  && o=yes
  has "$p" "$linked"   && l=yes
  # Conformance per gitsubmodules(7): a conformant submodule needs BOTH a gitlink
  # (mode 160000) AND a matching .gitmodules declaration. Either alone is drift.
  if   [ "$l" = yes ] && [ "$o" = yes ] && [ "$d" = yes ]; then state=conforming
  elif [ "$l" = yes ] && [ "$d" = no ];                    then state=orphan-gitlink
  elif [ "$l" = yes ] && [ "$o" = no ]  && [ "$d" = yes ]; then state=not-checked-out
  elif [ "$l" = no ]  && [ "$o" = yes ] && [ "$d" = yes ]; then state=broken-link
  elif [ "$l" = no ]  && [ "$o" = yes ] && [ "$d" = no ];  then
    # Undeclared on-disk repo: gitignored by the parent = intentionally independent
    # (agent-os umbrella pattern), benign. Not ignored = forgotten/broken submodule, flag it.
    if git -C "$sup" check-ignore -q "$p" 2>/dev/null; then state=nested-independent
    else state=undeclared; fi
  elif [ "$l" = no ]  && [ "$o" = no ]  && [ "$d" = yes ]; then state=declared-only
  else state=anomaly; fi
  case "$state" in conforming|nested-independent) ;; *) drift=1 ;; esac
  staged=$(git -C "$sup" diff --cached --name-only -- "$p" 2>/dev/null | wc -l | tr -d ' ')
  history=$(git -C "$sup" log --all --oneline -- "$p" 2>/dev/null | wc -l | tr -d ' ')
  report=$(printf '%s\n  %-16s %s  staged=%s history=%s' \
             "$report" "$state" "$p" "$staged" "$history")
done

if [ "$drift" -eq 1 ]; then
  {
    echo "git-roots: submodule drift — run git-doctor"
    echo "  superproject: $sup"
    printf '%s\n' "$report" | sed '/^$/d'
  } >&2
  exit 1
fi

# Conforming: submodules first (reverse status order = deepest first), super last.
git -C "$sup" submodule status --recursive 2>/dev/null | awk '{print $2}' \
  | awk -v s="$sup" '{a[NR]=$0} END{for(i=NR;i>=1;i--) print s"/"a[i]}'
echo "$sup"

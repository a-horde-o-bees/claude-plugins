"""Compose verb — workflow-driven, self-contained skill folders.

    uv run -m scripts.compose new --scope <user|project>
    uv run -m scripts.compose refine <name> --scope <user|project>
    uv run -m scripts.compose build <name> --scope <user|project> [--force]
    uv run -m scripts.compose list [--scope <both|user|project>] [--drift]

Agent-internal sub-ops (called during compose workflows; not user-facing):

    uv run -m scripts.compose add-source <name> <url>:<skill>[@<ref>] --scope <user|project>
    uv run -m scripts.compose remove-source <name> <source-slug> --scope <user|project>
    uv run -m scripts.compose update-sources <name> [--source <slug>] --scope <user|project>
    uv run -m scripts.compose purge-sources <name> --scope <user|project>

Stdlib-only — no PEP 723 deps, runs uniformly under module-mode `uv run`.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts._clone import (
    ls_remote_head,
    sparse_checkout_skill,
)
from scripts._paths import (
    composition_path,
    compositions_in_scope,
    derive_source_slug,
    scope_skills_dir,
    skill_folder,
    skill_md_path,
    source_embed_path,
    sources_subdir,
)
from scripts._spec import (
    Source,
    add_source_to_spec,
    read as read_spec,
    remove_source_from_spec,
    write as write_spec,
)


SKILL_LAYOUTS = ("skills/{skill}", "{skill}")


def parse_source_arg(value: str) -> tuple[str, str, str | None]:
    """Parse `<url>:<skill>` or `<url>:<skill>@<ref>` into (url, skill, ref)."""
    ref: str | None = None
    if "@" in value:
        url_skill_part, _, candidate_ref = value.rpartition("@")
        if "/" not in candidate_ref or candidate_ref.startswith("refs/"):
            value = url_skill_part
            ref = candidate_ref
    if "://" in value:
        scheme, rest = value.split("://", 1)
        if ":" not in rest:
            raise argparse.ArgumentTypeError(
                f"expected `<url>:<skill>` form, got {value!r}"
            )
        path_part, _, skill = rest.rpartition(":")
        url = f"{scheme}://{path_part}"
    else:
        if value.count(":") < 1:
            raise argparse.ArgumentTypeError(
                f"expected `<url>:<skill>` form, got {value!r}"
            )
        url, _, skill = value.rpartition(":")
    if not url or not skill:
        raise argparse.ArgumentTypeError(
            f"expected `<url>:<skill>` form, got {value!r}"
        )
    return url, skill, ref


def find_skill_path_in_repo(url: str, ref: str | None, skill: str) -> str:
    """Probe upstream layout: `skills/<skill>` first, then `<skill>` at root.

    Performs a tiny clone into a temp dir to ls-tree and find where the
    requested skill folder lives. Returns the path relative to repo root.
    """
    with tempfile.TemporaryDirectory(prefix="probe-") as tmp:
        clone_dir = Path(tmp) / "probe"
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

        result = subprocess.run(
            ["git", "-C", str(clone_dir), "ls-tree", "-r", "--name-only", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        files = set(result.stdout.strip().splitlines())
        for layout in SKILL_LAYOUTS:
            candidate = layout.format(skill=skill)
            skill_md = f"{candidate}/SKILL.md"
            if skill_md in files:
                return candidate
        raise FileNotFoundError(
            f"skill {skill!r} not found at any known layout in {url}@{ref or 'default'}"
        )


COMPOSED_SKILL_TEMPLATE = """\
---
name: {name}
description: {description}
---

# {name}

<!--
Scaffolded by `compose build` from composition.md at:
{spec_path}

This is the initial materialization — `composition.md` captures design
intent and source provenance; this SKILL.md is the live implementation.
After scaffolding, refine here via dialogue with the user, flesh out
each Triggers entry, and create the `_<verb>.md` workflow files the
Triggers below reference. Embedded sources are at
{sources_path}/<source-slug>/.

Run `compose refine {name} --scope {scope}` periodically to detect
upstream drift in sources.
-->

## Triggers

<!--
Scaffolded from composition.md's `## Surface` section. Each cognitive
moment in Surface becomes a Triggers entry; each `Routes to: _<verb>.md`
line implies a `_<verb>.md` workflow file the agent will create.
-->
"""


# -----------------------------------------------------------------------------
# compose new — workflow entry (no disk ops)
# -----------------------------------------------------------------------------


def cmd_new(args: argparse.Namespace) -> int:
    target_dir = scope_skills_dir(args.scope)
    print(f"scope: {args.scope}")
    print(f"target: {target_dir}/<chosen-name>/composition.md")
    return 0


# -----------------------------------------------------------------------------
# compose refine — workflow re-entry (read spec, drift check, orchestrate)
# -----------------------------------------------------------------------------


def cmd_refine(args: argparse.Namespace) -> int:
    spec_path = composition_path(args.name, args.scope)
    if not spec_path.exists():
        print(
            f"no composition at {spec_path} — run `compose new --scope {args.scope}` to start a new one",
            file=sys.stderr,
        )
        return 2

    spec = read_spec(spec_path)
    skill_md = skill_md_path(args.name, args.scope)
    deployed = "yes" if skill_md.exists() else "no"

    print(f"spec: {spec_path}")
    print(f"deployed: {deployed}")

    drifted, in_sync, issues = _check_drift(spec)

    if drifted:
        print()
        print("drift detected:")
        for src, current_sha in drifted:
            print(f"  - {src.url}:{src.skill}@{src.ref} {src.commit[:8]} → {current_sha[:8]}")

    if in_sync:
        print()
        print("in sync:")
        for src in in_sync:
            print(f"  - {src.url}:{src.skill}@{src.ref} @ {src.commit[:8]}")

    if issues:
        print()
        print("issues:")
        for src, reason in issues:
            print(f"  - {src.url}:{src.skill}@{src.ref} — {reason}")
    return 0


def _check_drift(spec) -> tuple[list, list, list]:
    drifted = []
    in_sync = []
    issues = []
    for src in spec.sources:
        try:
            current_sha = ls_remote_head(src.url, src.ref)
        except Exception as exc:
            issues.append((src, f"ls-remote failed: {exc}"))
            continue
        if current_sha == src.commit:
            in_sync.append(src)
        else:
            drifted.append((src, current_sha))
    return drifted, in_sync, issues


# -----------------------------------------------------------------------------
# compose build — terminal materialize
# -----------------------------------------------------------------------------


def cmd_build(args: argparse.Namespace) -> int:
    spec_path = composition_path(args.name, args.scope)
    if not spec_path.exists():
        print(
            f"no composition at {spec_path} — run `compose new --scope {args.scope}` first",
            file=sys.stderr,
        )
        return 2

    spec = read_spec(spec_path)
    if not spec.description:
        print(
            "spec description is empty — set `description` in composition.md frontmatter "
            "before building (the deployed SKILL.md needs a discoverable description)",
            file=sys.stderr,
        )
        return 2
    if not spec.sources:
        print(
            "spec has no sources — add at least one via `compose add-source` before building",
            file=sys.stderr,
        )
        return 2

    skill_md = skill_md_path(args.name, args.scope)
    if skill_md.exists() and not args.force:
        print(
            f"deployed SKILL.md already exists at {skill_md} — pass --force to "
            "regenerate (this overwrites agent refinements)",
            file=sys.stderr,
        )
        return 2

    folder = skill_folder(args.name, args.scope)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "scripts").mkdir(exist_ok=True)
    init_py = folder / "scripts" / "__init__.py"
    if not init_py.exists():
        init_py.write_text("")

    skill_md.write_text(
        COMPOSED_SKILL_TEMPLATE.format(
            name=spec.name,
            description=spec.description,
            spec_path=spec_path,
            sources_path=sources_subdir(args.name, args.scope),
            scope=args.scope,
        )
    )

    print(f"built {spec.name} at {folder}")
    print(f"skill_md: {skill_md}")
    print("sources used:")
    for src in spec.sources:
        print(f"  - {src.url}:{src.skill}@{src.ref} @ {src.commit[:8]}")
    return 0


# -----------------------------------------------------------------------------
# compose list — overview
# -----------------------------------------------------------------------------


def cmd_list(args: argparse.Namespace) -> int:
    scopes = ("user", "project") if args.scope == "both" else (args.scope,)
    found_any = False

    for scope in scopes:
        try:
            entries = compositions_in_scope(scope)
        except RuntimeError:
            continue
        if not entries:
            continue

        print(f"{scope}-scope:")
        for spec_path in entries:
            try:
                spec = read_spec(spec_path)
            except Exception as exc:
                print(f"  - {spec_path.parent.name} (parse error: {exc})")
                found_any = True
                continue

            deployed = "deployed" if (spec_path.parent / "SKILL.md").exists() else "draft"
            source_word = "source" if len(spec.sources) == 1 else "sources"
            line = (
                f"  - {spec.name} ({len(spec.sources)} {source_word}, {deployed})"
            )
            print(line)

            if args.drift and spec.sources:
                drifted, _, issues = _check_drift(spec)
                for src, current_sha in drifted:
                    print(
                        f"      drift: {src.url}:{src.skill}@{src.ref} "
                        f"{src.commit[:8]} → {current_sha[:8]}"
                    )
                for src, reason in issues:
                    print(
                        f"      issue: {src.url}:{src.skill}@{src.ref} — {reason}"
                    )
            found_any = True

    if not found_any:
        print("no skills deployed by progressive-composer at the requested scope(s)")
    return 0


# -----------------------------------------------------------------------------
# compose add-source — agent sub-op
# -----------------------------------------------------------------------------


def cmd_add_source(args: argparse.Namespace) -> int:
    spec_path = composition_path(args.name, args.scope)
    if not spec_path.exists():
        print(
            f"no composition at {spec_path} — run `compose new --scope {args.scope}` first",
            file=sys.stderr,
        )
        return 2

    spec = read_spec(spec_path)

    url, skill, ref_from_arg = args.source
    ref = ref_from_arg or "main"
    source_slug = derive_source_slug(url, skill)

    try:
        skill_path = find_skill_path_in_repo(url, ref, skill)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    embed_path = source_embed_path(args.name, source_slug, args.scope)
    embed_path.parent.mkdir(parents=True, exist_ok=True)
    commit = sparse_checkout_skill(url, skill_path, ref, embed_path)

    source = Source(url=url, skill=skill, ref=ref, commit=commit)
    add_source_to_spec(spec, source)
    write_spec(spec_path, spec)

    print(f"added source {url}:{skill}@{ref}")
    print(f"  embedded at: {embed_path}")
    print(f"  pinned commit: {commit[:8]}")
    return 0


# -----------------------------------------------------------------------------
# compose remove-source — agent sub-op
# -----------------------------------------------------------------------------


def cmd_remove_source(args: argparse.Namespace) -> int:
    spec_path = composition_path(args.name, args.scope)
    if not spec_path.exists():
        print(
            f"no composition at {spec_path}", file=sys.stderr,
        )
        return 2

    spec = read_spec(spec_path)
    # Match by source-slug (since slug is what the user remembers from the embed dir)
    matches = [s for s in spec.sources if derive_source_slug(s.url, s.skill) == args.source_slug]
    if not matches:
        print(
            f"no source with slug {args.source_slug!r} in composition {args.name}",
            file=sys.stderr,
        )
        return 2

    for src in matches:
        remove_source_from_spec(spec, src.url, src.skill)

    embed_path = source_embed_path(args.name, args.source_slug, args.scope)
    if embed_path.exists():
        shutil.rmtree(embed_path)

    write_spec(spec_path, spec)

    print(f"removed source {args.source_slug} from {args.name}")
    return 0


# -----------------------------------------------------------------------------
# compose update-sources — agent sub-op
# -----------------------------------------------------------------------------


def cmd_update_sources(args: argparse.Namespace) -> int:
    spec_path = composition_path(args.name, args.scope)
    if not spec_path.exists():
        print(
            f"no composition at {spec_path}", file=sys.stderr,
        )
        return 2

    spec = read_spec(spec_path)
    targets = spec.sources
    if args.source:
        targets = [s for s in spec.sources if derive_source_slug(s.url, s.skill) == args.source]
        if not targets:
            print(
                f"no source with slug {args.source!r} in composition {args.name}",
                file=sys.stderr,
            )
            return 2

    for src in targets:
        try:
            skill_path = find_skill_path_in_repo(src.url, src.ref, src.skill)
        except FileNotFoundError as exc:
            print(f"skip {src.url}:{src.skill}@{src.ref} — {exc}", file=sys.stderr)
            continue

        slug = derive_source_slug(src.url, src.skill)
        embed_path = source_embed_path(args.name, slug, args.scope)
        embed_path.parent.mkdir(parents=True, exist_ok=True)
        old_commit = src.commit
        new_commit = sparse_checkout_skill(src.url, skill_path, src.ref, embed_path)
        src.commit = new_commit
        print(
            f"updated {src.url}:{src.skill}@{src.ref} "
            f"{old_commit[:8] if old_commit else 'unset'} → {new_commit[:8]}"
        )

    write_spec(spec_path, spec)
    return 0


# -----------------------------------------------------------------------------
# compose purge-sources — agent sub-op
# -----------------------------------------------------------------------------


def cmd_purge_sources(args: argparse.Namespace) -> int:
    spec_path = composition_path(args.name, args.scope)
    if not spec_path.exists():
        print(f"no composition at {spec_path}", file=sys.stderr)
        return 2

    sources_dir = sources_subdir(args.name, args.scope)
    if not sources_dir.exists():
        print(f"no sources/ subfolder at {sources_dir}; nothing to purge")
        return 0

    shutil.rmtree(sources_dir)
    print(f"purged {sources_dir}")
    print("composition.md commits remain pinned; future `compose refine` auto-rehydrates")
    return 0


# -----------------------------------------------------------------------------
# argparse wiring
# -----------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="compose",
        description="Workflow-driven, self-contained skill composition.",
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    # User-facing
    new = sub.add_parser("new", help="open a new-composition workflow")
    new.add_argument(
        "--scope",
        required=True,
        choices=("user", "project"),
        help="scope where the composition will live",
    )

    refine = sub.add_parser("refine", help="re-enter an existing composition with drift check")
    refine.add_argument("name", help="composition skill name")
    refine.add_argument("--scope", required=True, choices=("user", "project"))

    build = sub.add_parser("build", help="materialize composition.md into a deployed skill")
    build.add_argument("name", help="composition skill name")
    build.add_argument("--scope", required=True, choices=("user", "project"))
    build.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing deployed SKILL.md",
    )

    list_cmd = sub.add_parser("list", help="show all deployed skills and their status")
    list_cmd.add_argument(
        "--scope",
        choices=("user", "project", "both"),
        default="both",
    )
    list_cmd.add_argument(
        "--drift",
        action="store_true",
        help="run git ls-remote per source to detect upstream drift",
    )

    # Agent sub-ops
    add_src = sub.add_parser("add-source", help="(agent sub-op) add a source to a composition")
    add_src.add_argument("name", help="composition skill name")
    add_src.add_argument(
        "source",
        type=parse_source_arg,
        metavar="URL:SKILL[@REF]",
    )
    add_src.add_argument("--scope", required=True, choices=("user", "project"))

    rm_src = sub.add_parser("remove-source", help="(agent sub-op) remove a source from a composition")
    rm_src.add_argument("name", help="composition skill name")
    rm_src.add_argument("source_slug", help="source slug (derived from URL)")
    rm_src.add_argument("--scope", required=True, choices=("user", "project"))

    upd_src = sub.add_parser("update-sources", help="(agent sub-op) re-fetch source(s) at upstream HEAD")
    upd_src.add_argument("name", help="composition skill name")
    upd_src.add_argument(
        "--source",
        help="source slug to update (default: all sources)",
    )
    upd_src.add_argument("--scope", required=True, choices=("user", "project"))

    pg_src = sub.add_parser("purge-sources", help="(agent sub-op) delete the sources/ subfolder")
    pg_src.add_argument("name", help="composition skill name")
    pg_src.add_argument("--scope", required=True, choices=("user", "project"))

    args = parser.parse_args()

    dispatch = {
        "new": cmd_new,
        "refine": cmd_refine,
        "build": cmd_build,
        "list": cmd_list,
        "add-source": cmd_add_source,
        "remove-source": cmd_remove_source,
        "update-sources": cmd_update_sources,
        "purge-sources": cmd_purge_sources,
    }
    return dispatch[args.verb](args)


if __name__ == "__main__":
    raise SystemExit(main())

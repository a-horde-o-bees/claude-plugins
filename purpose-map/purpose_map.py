"""Purpose map for ground-up project evaluation.

Two entity types connected by four relationship types, plus location references:

  Needs       — problems to solve (the "why")
  Components  — structural units that address needs (the "how")

Entities use auto-generated short ids (c1, c2, ... for components; n1, n2, ...
for needs). The description is the load-bearing meaning. All displays render
entries as `[id] description` so the id is always paired with its purpose,
preventing reasoning from a name alone.

Edges:

  depends_on      — component depends on component (structural DAG)
  refines         — child need refines parent need (need decomposition DAG)
  owns            — component owns a need (single-owner allocation)
  addresses       — component addresses a need (capability; partial OK)
  component_paths — component → source-location reference (file path, optionally with #anchor)

Each relationship is an independent graph over the same entities. Paths are
non-authoritative location pointers — they record where the real artifact lived
when the entry was created so a future reader can find it (or retrace it after
a refactor).

Usage:
    python3 purpose-map/purpose_map.py <command> [args...]

Commands — components:
    add-component <description>            Add a component (id auto-assigned: c{n})
    set-component <id> <description>       Update description
    remove-component <id>                  Remove component and its edges

Commands — needs:
    add-need <description>                 Add a need (id auto-assigned: n{n})
    set-need <id> <description>            Update description
    remove-need <id>                       Remove need and its edges

Commands — edges:
    depend <component> <dependency>                    Component depends on another
    undepend <component> <dependency>                  Remove dependency
    refine <child-need> <parent-need> <rationale>      Child need refines parent need
    unrefine <child-need> <parent-need>                Remove refinement
    own <component> <need> <rationale>                 Component owns a need (single owner)
    disown <component> <need>                          Remove ownership
    address <component> <need> <rationale>             Component addresses a need
    unaddress <component> <need>                       Remove addressing edge
    set-rationale <type> <a> <b> <rationale>           Update rationale on an existing edge
                                                       (type: address | refine | own)
    add-path <component> <path>                        Record a source-location path
    remove-path <component> <path>                     Remove a recorded path

Rationales explain *why* an edge exists. They are required when creating
addresses/refines/owns edges so the reasoning survives session boundaries
and can be re-evaluated when descriptions change. Rationales are displayed
by `how`, `why`, and the `addresses` view.

Commands — lock:
    lock <id>                              Lock a component or need
    unlock <id>                            Unlock a component or need

Commands — analysis:
    dependencies [component-id] [--verify] Structural tree (with optional lock check)
    ownership [component-id]               Owned needs and how each is addressed
    addresses [id] [--gaps] [--orphans]    Addressing graph (entity, leaf gaps, or orphans)
    where <component-id>                   Recorded source-location paths for a component
    why <component-id>                     Upward trace: addresses → need → refines → owner
    how <need-id>                          Downward trace: direct addressers + refinements
    summary                                Counts, root needs, addressing status
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "purpose-map.db"


def _next_id(db, prefix, table):
    """Generate next sequential short id (e.g. c5, n3)."""
    rows = db.execute(
        f"SELECT id FROM {table} WHERE id LIKE ?", (f"{prefix}%",)
    ).fetchall()
    nums = []
    for (rid,) in rows:
        suffix = rid[len(prefix):]
        if suffix.isdigit():
            nums.append(int(suffix))
    return f"{prefix}{(max(nums) + 1) if nums else 1}"


def _comp_label(cid, description, locked):
    """Format a component as '◈ [id] description' with lock marker."""
    marker = "◈" if locked else "? ◈"
    return f"{marker} [{cid}] {description}"


def _need_label(nid, description, locked):
    """Format a need as '◇ [id] description' with lock marker."""
    marker = "◇" if locked else "? ◇"
    return f"{marker} [{nid}] {description}"


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS components (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            locked INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS needs (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            locked INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS depends_on (
            component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
            dependency_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
            PRIMARY KEY (component_id, dependency_id)
        );

        CREATE TABLE IF NOT EXISTS refines (
            need_id TEXT NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
            refined_need_id TEXT NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
            rationale TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (need_id, refined_need_id)
        );

        CREATE TABLE IF NOT EXISTS owns (
            component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
            need_id TEXT NOT NULL UNIQUE REFERENCES needs(id) ON DELETE CASCADE,
            rationale TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (component_id, need_id)
        );

        CREATE TABLE IF NOT EXISTS addresses (
            component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
            need_id TEXT NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
            rationale TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (component_id, need_id)
        );

        CREATE TABLE IF NOT EXISTS component_paths (
            component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
            path TEXT NOT NULL,
            PRIMARY KEY (component_id, path)
        );
    """)
    return db


# --- Component commands ---

def add_component(db, description):
    new_id = _next_id(db, "c", "components")
    db.execute("INSERT INTO components (id, description) VALUES (?, ?)",
                (new_id, description))
    db.commit()
    print(f"Added: [{new_id}] {description}")


def set_component(db, comp_id, description):
    cur = db.execute("UPDATE components SET description = ? WHERE id = ?",
                     (description, comp_id))
    if cur.rowcount == 0:
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)
    db.commit()
    print(f"Updated: [{comp_id}] {description}")


def remove_component(db, comp_id):
    cur = db.execute("DELETE FROM components WHERE id = ?", (comp_id,))
    if cur.rowcount == 0:
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)
    db.commit()
    print(f"Removed component: [{comp_id}]")


# --- Need commands ---

def add_need(db, description):
    new_id = _next_id(db, "n", "needs")
    db.execute("INSERT INTO needs (id, description) VALUES (?, ?)",
                (new_id, description))
    db.commit()
    print(f"Added: [{new_id}] {description}")


def set_need(db, need_id, description):
    cur = db.execute("UPDATE needs SET description = ? WHERE id = ?",
                     (description, need_id))
    if cur.rowcount == 0:
        print(f"Error: need '{need_id}' not found")
        sys.exit(1)
    db.commit()
    print(f"Updated: [{need_id}] {description}")


def remove_need(db, need_id):
    cur = db.execute("DELETE FROM needs WHERE id = ?", (need_id,))
    if cur.rowcount == 0:
        print(f"Error: need '{need_id}' not found")
        sys.exit(1)
    db.commit()
    print(f"Removed need: [{need_id}]")


# --- Dependency edge commands ---

def depend(db, comp_id, dep_id):
    _check_component(db, comp_id)
    _check_component(db, dep_id)
    if comp_id == dep_id:
        print("Error: a component cannot depend on itself")
        sys.exit(1)
    if _would_cycle(db, "depends_on", "component_id", "dependency_id", comp_id, dep_id):
        print(f"Error: {comp_id} → {dep_id} would create a dependency cycle")
        sys.exit(1)
    try:
        db.execute("INSERT INTO depends_on (component_id, dependency_id) VALUES (?, ?)",
                    (comp_id, dep_id))
        db.commit()
        print(f"Dependency: {comp_id} depends on {dep_id}")
    except sqlite3.IntegrityError:
        print("Error: dependency already exists")
        sys.exit(1)


def undepend(db, comp_id, dep_id):
    cur = db.execute("DELETE FROM depends_on WHERE component_id = ? AND dependency_id = ?",
                     (comp_id, dep_id))
    if cur.rowcount == 0:
        print("Error: dependency not found")
        sys.exit(1)
    db.commit()
    print(f"Removed: {comp_id} depends on {dep_id}")


# --- Refinement edge commands ---

def refine(db, child_id, parent_id, rationale):
    if not rationale or not rationale.strip():
        print("Error: refine requires a rationale explaining why this child refines the parent")
        sys.exit(1)
    _check_need(db, child_id)
    _check_need(db, parent_id)
    if child_id == parent_id:
        print("Error: a need cannot refine itself")
        sys.exit(1)
    if _would_cycle(db, "refines", "need_id", "refined_need_id", child_id, parent_id):
        print(f"Error: {child_id} → {parent_id} would create a refinement cycle")
        sys.exit(1)
    try:
        db.execute("INSERT INTO refines (need_id, refined_need_id, rationale) VALUES (?, ?, ?)",
                    (child_id, parent_id, rationale.strip()))
        db.commit()
        print(f"Refinement: {child_id} refines {parent_id}")
        print(f"  rationale: {rationale.strip()}")
    except sqlite3.IntegrityError:
        print("Error: refinement already exists")
        sys.exit(1)


def unrefine(db, child_id, parent_id):
    cur = db.execute("DELETE FROM refines WHERE need_id = ? AND refined_need_id = ?",
                     (child_id, parent_id))
    if cur.rowcount == 0:
        print("Error: refinement not found")
        sys.exit(1)
    db.commit()
    print(f"Removed: {child_id} refines {parent_id}")


# --- Ownership edge commands ---

def own(db, comp_id, need_id, rationale):
    if not rationale or not rationale.strip():
        print("Error: own requires a rationale explaining why this component owns the need")
        sys.exit(1)
    _check_component(db, comp_id)
    _check_need(db, need_id)
    existing = db.execute(
        "SELECT component_id FROM owns WHERE need_id = ?", (need_id,)
    ).fetchone()
    if existing:
        if existing[0] == comp_id:
            print("Error: ownership already exists")
        else:
            print(f"Error: '{need_id}' is already owned by '{existing[0]}'. "
                  f"Disown first, or refine the need to express a separate concern.")
        sys.exit(1)
    db.execute("INSERT INTO owns (component_id, need_id, rationale) VALUES (?, ?, ?)",
                (comp_id, need_id, rationale.strip()))
    db.commit()
    print(f"Ownership: {comp_id} owns {need_id}")
    print(f"  rationale: {rationale.strip()}")


def disown(db, comp_id, need_id):
    cur = db.execute("DELETE FROM owns WHERE component_id = ? AND need_id = ?",
                     (comp_id, need_id))
    if cur.rowcount == 0:
        print("Error: ownership not found")
        sys.exit(1)
    db.commit()
    print(f"Removed: {comp_id} owns {need_id}")


# --- Addressing edge commands ---

def address(db, comp_id, need_id, rationale):
    if not rationale or not rationale.strip():
        print("Error: address requires a rationale explaining why this component addresses the need")
        sys.exit(1)
    _check_component(db, comp_id)
    _check_need(db, need_id)
    try:
        db.execute("INSERT INTO addresses (component_id, need_id, rationale) VALUES (?, ?, ?)",
                    (comp_id, need_id, rationale.strip()))
        db.commit()
        print(f"Addresses: {comp_id} → {need_id}")
        print(f"  rationale: {rationale.strip()}")
    except sqlite3.IntegrityError:
        print("Error: addressing edge already exists")
        sys.exit(1)


def set_rationale(db, edge_type, a, b, rationale):
    """Update the rationale on an existing edge.

    edge_type: one of 'address', 'refine', 'own' (also accepts plural forms).
    """
    if not rationale or not rationale.strip():
        print("Error: rationale cannot be empty")
        sys.exit(1)

    table_map = {
        "address":   ("addresses", "component_id", "need_id"),
        "addresses": ("addresses", "component_id", "need_id"),
        "refine":    ("refines",   "need_id",      "refined_need_id"),
        "refines":   ("refines",   "need_id",      "refined_need_id"),
        "own":       ("owns",      "component_id", "need_id"),
        "owns":      ("owns",      "component_id", "need_id"),
    }
    if edge_type not in table_map:
        print(f"Error: unknown edge type '{edge_type}'. Use 'address', 'refine', or 'own'")
        sys.exit(1)

    table, col_a, col_b = table_map[edge_type]
    cur = db.execute(
        f"UPDATE {table} SET rationale = ? WHERE {col_a} = ? AND {col_b} = ?",
        (rationale.strip(), a, b)
    )
    if cur.rowcount == 0:
        print(f"Error: {edge_type} edge {a} → {b} not found")
        sys.exit(1)
    db.commit()
    print(f"Updated rationale: {edge_type} {a} → {b}")
    print(f"  rationale: {rationale.strip()}")


def unaddress(db, comp_id, need_id):
    cur = db.execute("DELETE FROM addresses WHERE component_id = ? AND need_id = ?",
                     (comp_id, need_id))
    if cur.rowcount == 0:
        print("Error: addressing edge not found")
        sys.exit(1)
    db.commit()
    print(f"Removed: {comp_id} → {need_id}")


# --- Path commands ---

def add_path(db, comp_id, path):
    _check_component(db, comp_id)
    try:
        db.execute("INSERT INTO component_paths (component_id, path) VALUES (?, ?)",
                    (comp_id, path))
        db.commit()
        print(f"Path: {comp_id} @ {path}")
    except sqlite3.IntegrityError:
        print("Error: path already recorded for this component")
        sys.exit(1)


def remove_path(db, comp_id, path):
    cur = db.execute("DELETE FROM component_paths WHERE component_id = ? AND path = ?",
                     (comp_id, path))
    if cur.rowcount == 0:
        print("Error: path not recorded for this component")
        sys.exit(1)
    db.commit()
    print(f"Removed: {comp_id} @ {path}")


# --- Lock commands ---

def lock(db, item_id):
    for table in ("components", "needs"):
        r = db.execute(f"UPDATE {table} SET locked = 1 WHERE id = ?", (item_id,))
        if r.rowcount:
            db.commit()
            print(f"Locked: {item_id}")
            return
    print(f"Error: '{item_id}' not found")
    sys.exit(1)


def unlock(db, item_id):
    for table in ("components", "needs"):
        r = db.execute(f"UPDATE {table} SET locked = 0 WHERE id = ?", (item_id,))
        if r.rowcount:
            db.commit()
            print(f"Unlocked: {item_id}")
            return
    print(f"Error: '{item_id}' not found")
    sys.exit(1)


# --- Analysis: dependencies ---

def dependencies(db, comp_id=None, verify=False):
    """Structural tree of components from depends_on edges only.

    With --verify, also reports unlocked dependency ancestors for each component.
    """
    if comp_id:
        comp = db.execute("SELECT description, locked FROM components WHERE id = ?",
                          (comp_id,)).fetchone()
        if not comp:
            print(f"Error: component '{comp_id}' not found")
            sys.exit(1)
        _dep_tree(db, comp_id, comp[0], comp[1])
        if verify:
            print()
            _verify_one(db, comp_id)
    else:
        roots = db.execute("""
            SELECT c.id, c.description, c.locked FROM components c
            WHERE NOT EXISTS (
                SELECT 1 FROM depends_on d WHERE d.component_id = c.id
            )
            ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
        """).fetchall()
        for cid, cdesc, clocked in roots:
            _dep_tree(db, cid, cdesc, clocked)

        if verify:
            print()
            verify_all(db)


def _dep_tree(db, comp_id, description, locked, header_prefix="", cont_prefix=""):
    """Print component and its dependent components."""
    print(f"{header_prefix}{_comp_label(comp_id, description, locked)}")

    dependents = db.execute("""
        SELECT c.id, c.description, c.locked FROM depends_on d
        JOIN components c ON c.id = d.component_id
        WHERE d.dependency_id = ? ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
    """, (comp_id,)).fetchall()

    for i, (cid, cdesc, clocked) in enumerate(dependents):
        is_last = i == len(dependents) - 1
        branch = "└── " if is_last else "├── "
        cont = "    " if is_last else "│   "
        _dep_tree(db, cid, cdesc, clocked,
                  cont_prefix + branch, cont_prefix + cont)


# --- Analysis: ownership ---

def ownership(db, comp_id=None):
    """For each owner, show owned needs and how each one is addressed.

    Coverage traverses refinements: a need is considered addressed if it has
    direct addressers OR all of its refinements are addressed.
    """
    if comp_id:
        _ownership_one(db, comp_id)
    else:
        owners = db.execute("""
            SELECT DISTINCT c.id FROM owns o
            JOIN components c ON c.id = o.component_id
            ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
        """).fetchall()
        for i, (oid,) in enumerate(owners):
            _ownership_one(db, oid)
            if i < len(owners) - 1:
                print()


def _ownership_one(db, comp_id):
    comp = db.execute("SELECT description, locked FROM components WHERE id = ?",
                      (comp_id,)).fetchone()
    if not comp:
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)

    owned = db.execute("""
        SELECT n.id, n.description, n.locked FROM owns o
        JOIN needs n ON n.id = o.need_id
        WHERE o.component_id = ? ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """, (comp_id,)).fetchall()

    print(_comp_label(comp_id, comp[0], comp[1]))
    if not owned:
        print("  (no owned needs)")
        return

    print(f"  owns {len(owned)} need(s):")
    addressed = 0
    for nid, ndesc, nlocked in owned:
        status, summary_text = _coverage(db, nid)
        marker = {"covered": "✓", "partial": "~", "gap": "✗"}[status]
        print(f"    {marker} {_need_label(nid, ndesc, nlocked)}")
        print(f"        {summary_text}")
        if status == "covered":
            addressed += 1

    pct = (addressed / len(owned) * 100) if owned else 0
    print(f"  [{addressed}/{len(owned)}] {pct:.0f}% fully addressed")


def _coverage(db, need_id, seen=None):
    """Return (status, summary) for a need.

    status: 'covered' (direct or all refinements covered),
            'partial' (some refinements covered),
            'gap'     (no direct addressers and no refinements, or all refinements gap)
    """
    seen = seen or set()
    if need_id in seen:
        return "gap", "(refinement cycle)"
    seen = seen | {need_id}

    direct = [r[0] for r in db.execute(
        "SELECT component_id FROM addresses WHERE need_id = ? ORDER BY CAST(SUBSTR(component_id, 2) AS INTEGER)",
        (need_id,)
    ).fetchall()]

    refinements = [r[0] for r in db.execute(
        "SELECT need_id FROM refines WHERE refined_need_id = ? ORDER BY CAST(SUBSTR(need_id, 2) AS INTEGER)",
        (need_id,)
    ).fetchall()]

    if direct and not refinements:
        return "covered", "addressed by " + ", ".join(direct)

    if not direct and not refinements:
        return "gap", "unaddressed (no addressers, no refinements)"

    # Refinements exist; recurse
    sub_results = [(r, _coverage(db, r, seen)) for r in refinements]
    covered_refs = [r for r, (s, _) in sub_results if s == "covered"]
    gap_refs = [r for r, (s, _) in sub_results if s == "gap"]

    parts = []
    if direct:
        parts.append("direct: " + ", ".join(direct))
    if covered_refs:
        parts.append(f"covered refinements: {', '.join(covered_refs)}")
    if gap_refs:
        parts.append(f"gap refinements: {', '.join(gap_refs)}")

    summary_text = "; ".join(parts)

    if direct or all(s == "covered" for _, (s, _) in sub_results):
        return "covered", summary_text
    if any(s == "covered" or s == "partial" for _, (s, _) in sub_results):
        return "partial", summary_text
    return "gap", summary_text


# --- Analysis: addresses ---

def addresses_view(db, entity_id=None, gaps=False, orphans=False):
    """Addressing graph: tree from a need or component, or specialty views."""
    if gaps:
        _show_leaf_gaps(db)
        return
    if orphans:
        _show_orphans(db)
        return

    if entity_id:
        # Need or component?
        if db.execute("SELECT 1 FROM needs WHERE id = ?", (entity_id,)).fetchone():
            _addresses_for_need(db, entity_id)
        elif db.execute("SELECT 1 FROM components WHERE id = ?", (entity_id,)).fetchone():
            _addresses_for_component(db, entity_id)
        else:
            print(f"Error: '{entity_id}' is not a known need or component")
            sys.exit(1)
    else:
        # All root needs (needs with no refined parents)
        roots = db.execute("""
            SELECT n.id FROM needs n
            WHERE NOT EXISTS (
                SELECT 1 FROM refines r WHERE r.need_id = n.id
            )
            ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
        """).fetchall()
        for i, (nid,) in enumerate(roots):
            _addresses_for_need(db, nid)
            if i < len(roots) - 1:
                print()


def _addresses_for_need(db, need_id, indent="", seen=None):
    """Tree of addressers for a need, with refinements expanded."""
    seen = seen or set()
    if need_id in seen:
        print(f"{indent}◇ [{need_id}] (refinement cycle)")
        return
    seen = seen | {need_id}

    need = db.execute("SELECT description, locked FROM needs WHERE id = ?",
                      (need_id,)).fetchone()
    print(f"{indent}{_need_label(need_id, need[0], need[1])}")

    direct = db.execute("""
        SELECT c.id, c.description, c.locked, a.rationale FROM addresses a
        JOIN components c ON c.id = a.component_id
        WHERE a.need_id = ? ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
    """, (need_id,)).fetchall()

    refinements = db.execute("""
        SELECT n.id, n.description, n.locked, r.rationale FROM refines r
        JOIN needs n ON n.id = r.need_id
        WHERE r.refined_need_id = ? ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """, (need_id,)).fetchall()

    if not direct and not refinements:
        print(f"{indent}  ✗ unaddressed (gap)")
        return

    for cid, cdesc, clocked, rationale in direct:
        print(f"{indent}  ↳ {_comp_label(cid, cdesc, clocked)}")
        if rationale:
            print(f"{indent}      rationale: {rationale}")

    if refinements:
        for nid, _, _, ref_rationale in refinements:
            _addresses_for_need(db, nid, indent + "    ", seen)
            if ref_rationale:
                print(f"{indent}      refinement rationale: {ref_rationale}")


def _addresses_for_component(db, comp_id):
    """What does this component address?"""
    comp = db.execute("SELECT description, locked FROM components WHERE id = ?",
                      (comp_id,)).fetchone()
    print(_comp_label(comp_id, comp[0], comp[1]))

    addrs = db.execute("""
        SELECT n.id, n.description, n.locked FROM addresses a
        JOIN needs n ON n.id = a.need_id
        WHERE a.component_id = ? ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """, (comp_id,)).fetchall()

    if not addrs:
        print("  (addresses nothing)")
        return

    for nid, ndesc, nlocked in addrs:
        print(f"  → {_need_label(nid, ndesc, nlocked)}")


def _show_leaf_gaps(db):
    """Needs with no refinements and no direct addressers — actionable gaps."""
    rows = db.execute("""
        SELECT n.id, n.description FROM needs n
        WHERE NOT EXISTS (SELECT 1 FROM refines r WHERE r.refined_need_id = n.id)
          AND NOT EXISTS (SELECT 1 FROM addresses a WHERE a.need_id = n.id)
        ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """).fetchall()
    if not rows:
        print("No leaf gaps — every leaf need has at least one addresser")
        return
    print(f"Leaf gaps ({len(rows)}) — needs with no refinements and no addressers:")
    for nid, desc in rows:
        owner = db.execute(
            "SELECT component_id FROM owns WHERE need_id = ?", (nid,)
        ).fetchone()
        owner_str = f"[{owner[0]}]" if owner else "unowned"
        print(f"  ✗ [{nid}] {desc}")
        print(f"      owned by: {owner_str}")


def _show_orphans(db):
    """Components that don't address anything."""
    rows = db.execute("""
        SELECT c.id, c.description, c.locked FROM components c
        WHERE NOT EXISTS (SELECT 1 FROM addresses a WHERE a.component_id = c.id)
        ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
    """).fetchall()
    if not rows:
        print("No orphans — every component addresses at least one need")
        return
    print(f"Orphan components ({len(rows)}):")
    for cid, desc, locked in rows:
        print(f"  {_comp_label(cid, desc, locked)}")


# --- Analysis: where, why, how ---

def where(db, comp_id):
    """Show recorded source-location paths for a component.

    Paths are non-authoritative pointers — true at creation, possibly stale
    after refactors. If they're broken, retrace by purpose using navigator
    or by content using grep, then update.
    """
    comp = db.execute("SELECT description, locked FROM components WHERE id = ?",
                      (comp_id,)).fetchone()
    if not comp:
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)

    print(_comp_label(comp_id, comp[0], comp[1]))

    paths = db.execute(
        "SELECT path FROM component_paths WHERE component_id = ? ORDER BY path",
        (comp_id,)
    ).fetchall()

    if not paths:
        print("  (no recorded paths)")
        return

    for (p,) in paths:
        print(f"  @ {p}")


def why(db, comp_id):
    """Upward trace: component → addresses → need → refines* → owner."""
    comp = db.execute("SELECT description, locked FROM components WHERE id = ?",
                      (comp_id,)).fetchone()
    if not comp:
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)

    print(_comp_label(comp_id, comp[0], comp[1]))

    addressed = db.execute("""
        SELECT n.id, n.description, n.locked, a.rationale FROM addresses a
        JOIN needs n ON n.id = a.need_id
        WHERE a.component_id = ? ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """, (comp_id,)).fetchall()

    if not addressed:
        print("  (addresses nothing)")
        return

    for nid, ndesc, nlocked, rationale in addressed:
        print(f"  ↑ addresses: {_need_label(nid, ndesc, nlocked)}")
        if rationale:
            print(f"      rationale: {rationale}")
        _trace_refines_up(db, nid, "      ")


def _trace_refines_up(db, need_id, indent, seen=None):
    """Walk up the refinement chain showing parents and ultimate owners."""
    seen = seen or set()
    if need_id in seen:
        return
    seen = seen | {need_id}

    owner = db.execute("""
        SELECT c.id, c.description, c.locked FROM owns o
        JOIN components c ON c.id = o.component_id
        WHERE o.need_id = ?
    """, (need_id,)).fetchone()
    if owner:
        print(f"{indent}owned by: {_comp_label(*owner)}")

    parents = db.execute("""
        SELECT n.id, n.description, n.locked FROM refines r
        JOIN needs n ON n.id = r.refined_need_id
        WHERE r.need_id = ? ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """, (need_id,)).fetchall()
    for pid, pdesc, plocked in parents:
        print(f"{indent}refines: {_need_label(pid, pdesc, plocked)}")
        _trace_refines_up(db, pid, indent + "  ", seen)


def how(db, need_id):
    """Downward trace: direct addressers + refinement subtree (recursively, with gaps)."""
    if not db.execute("SELECT 1 FROM needs WHERE id = ?", (need_id,)).fetchone():
        print(f"Error: need '{need_id}' not found")
        sys.exit(1)

    owner = db.execute("""
        SELECT c.id, c.description, c.locked FROM owns o
        JOIN components c ON c.id = o.component_id
        WHERE o.need_id = ?
    """, (need_id,)).fetchone()
    if owner:
        print(f"(owned by: {_comp_label(*owner)})")
    _addresses_for_need(db, need_id)


# --- Summary ---

def summary(db):
    """Counts, root needs, addressing status."""
    comp_count = db.execute("SELECT COUNT(*) FROM components").fetchone()[0]
    need_count = db.execute("SELECT COUNT(*) FROM needs").fetchone()[0]
    dep_count = db.execute("SELECT COUNT(*) FROM depends_on").fetchone()[0]
    ref_count = db.execute("SELECT COUNT(*) FROM refines").fetchone()[0]
    own_count = db.execute("SELECT COUNT(*) FROM owns").fetchone()[0]
    addr_count = db.execute("SELECT COUNT(*) FROM addresses").fetchone()[0]

    leaf_gaps = db.execute("""
        SELECT COUNT(*) FROM needs n
        WHERE NOT EXISTS (SELECT 1 FROM refines r WHERE r.refined_need_id = n.id)
          AND NOT EXISTS (SELECT 1 FROM addresses a WHERE a.need_id = n.id)
    """).fetchone()[0]

    locked_comps = db.execute(
        "SELECT COUNT(*) FROM components WHERE locked = 1"
    ).fetchone()[0]
    locked_needs = db.execute(
        "SELECT COUNT(*) FROM needs WHERE locked = 1"
    ).fetchone()[0]

    print(f"Components: {comp_count} ({locked_comps} locked)")
    print(f"Needs: {need_count} ({locked_needs} locked)")
    print(f"Dependencies: {dep_count} | Refinements: {ref_count} | "
          f"Ownership: {own_count} | Addresses: {addr_count}")
    print(f"Leaf gaps: {leaf_gaps}")

    roots = _root_needs(db)
    if roots:
        print(f"\nRoot needs ({len(roots)}):")
        for (nid,) in roots:
            row = db.execute(
                "SELECT description, locked FROM needs WHERE id = ?", (nid,)
            ).fetchone()
            status, _ = _coverage(db, nid)
            marker = {"covered": "✓", "partial": "~", "gap": "✗"}[status]
            print(f"  {marker} {_need_label(nid, row[0], row[1])}")


# --- Helpers ---

def verify_all(db):
    """Run lock-chain verify on every component."""
    all_comps = db.execute("SELECT id FROM components ORDER BY id").fetchall()
    any_unlocked = False
    for (cid,) in all_comps:
        if not _verify_one(db, cid, quiet=True):
            any_unlocked = True
    if not any_unlocked:
        print("✓ All dependency chains fully locked")


def _verify_one(db, comp_id, quiet=False):
    if not db.execute("SELECT id FROM components WHERE id = ?",
                      (comp_id,)).fetchone():
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)

    rows = db.execute("""
        WITH RECURSIVE ancestors(id, depth) AS (
            SELECT dependency_id, 1
            FROM depends_on WHERE component_id = ?
            UNION
            SELECT d.dependency_id, a.depth + 1
            FROM ancestors a
            JOIN depends_on d ON d.component_id = a.id
            WHERE a.depth < 50
        )
        SELECT DISTINCT c.id, c.description, c.locked
        FROM ancestors a
        JOIN components c ON c.id = a.id
    """, (comp_id,)).fetchall()

    if not rows:
        if not quiet:
            print(f"✓ {comp_id} has no dependency ancestors")
        return True

    unlocked = [(cid, desc) for cid, desc, locked in rows if not locked]
    all_locked = not unlocked

    if not quiet or not all_locked:
        if all_locked:
            print(f"✓ [{comp_id}] all dependencies locked")
        else:
            print(f"✗ [{comp_id}] unlocked dependencies:")
            for cid, desc in unlocked:
                print(f"    ✗ [{cid}] {desc}")

    return all_locked


def _root_needs(db):
    """Needs that no other need refines (top of refinement chains)."""
    return db.execute("""
        SELECT n.id FROM needs n
        WHERE NOT EXISTS (SELECT 1 FROM refines r WHERE r.need_id = n.id)
        ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """).fetchall()


def _would_cycle(db, table, from_col, to_col, new_from, new_to):
    """Check if inserting (new_from, new_to) into a DAG edge table would create a cycle.

    Generic walker: starting from new_to, walk forward through edges; if we reach new_from,
    a cycle would form.
    """
    rows = db.execute(f"""
        WITH RECURSIVE walk(id) AS (
            SELECT ? AS id
            UNION
            SELECT t.{to_col} FROM {table} t JOIN walk w ON t.{from_col} = w.id
        )
        SELECT 1 FROM walk WHERE id = ?
    """, (new_to, new_from)).fetchone()
    return bool(rows)


def _check_component(db, comp_id):
    if not db.execute("SELECT id FROM components WHERE id = ?",
                      (comp_id,)).fetchone():
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)


def _check_need(db, need_id):
    if not db.execute("SELECT id FROM needs WHERE id = ?",
                      (need_id,)).fetchone():
        print(f"Error: need '{need_id}' not found")
        sys.exit(1)


# --- Command dispatch ---

COMMANDS = {
    "add-component":    (add_component,    1, "<description>"),
    "set-component":    (set_component,    2, "<id> <description>"),
    "remove-component": (remove_component, 1, "<id>"),
    "add-need":         (add_need,         1, "<description>"),
    "set-need":         (set_need,         2, "<id> <description>"),
    "remove-need":      (remove_need,      1, "<id>"),
    "depend":           (depend,           2, "<component> <dependency>"),
    "undepend":         (undepend,         2, "<component> <dependency>"),
    "refine":           (refine,           3, "<child-need> <parent-need> <rationale>"),
    "unrefine":         (unrefine,         2, "<child-need> <parent-need>"),
    "own":              (own,              3, "<component> <need> <rationale>"),
    "disown":           (disown,           2, "<component> <need>"),
    "address":          (address,          3, "<component> <need> <rationale>"),
    "unaddress":        (unaddress,        2, "<component> <need>"),
    "set-rationale":    (set_rationale,    4, "<address|refine|own> <a> <b> <rationale>"),
    "add-path":         (add_path,         2, "<component> <path>"),
    "remove-path":      (remove_path,      2, "<component> <path>"),
    "lock":             (lock,             1, "<id>"),
    "unlock":           (unlock,           1, "<id>"),
    "dependencies":     (dependencies,     0, "[component-id] [--verify]"),
    "ownership":        (ownership,        0, "[component-id]"),
    "addresses":        (addresses_view,   0, "[id] [--gaps] [--orphans]"),
    "where":            (where,            1, "<component-id>"),
    "why":              (why,              1, "<component-id>"),
    "how":              (how,              1, "<need-id>"),
    "summary":          (summary,          0, ""),
}

OPTIONAL_ARG_COMMANDS = {"dependencies", "ownership", "addresses"}
RATIONALE_EDGE_COMMANDS = {"address", "refine", "own"}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        print("Commands:")
        for cmd, (_, _, usage) in sorted(COMMANDS.items()):
            print(f"  {cmd} {usage}")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Error: unknown command '{cmd}'")
        print("Run with --help for usage")
        sys.exit(1)

    func, argc, usage = COMMANDS[cmd]
    raw = sys.argv[2:]
    flags = {a for a in raw if a.startswith("--")}
    args = [a for a in raw if not a.startswith("--")]

    db = get_db()

    if cmd == "dependencies":
        func(db, args[0] if args else None, verify=("--verify" in flags))
    elif cmd == "addresses":
        func(db, args[0] if args else None,
             gaps=("--gaps" in flags), orphans=("--orphans" in flags))
    elif cmd in OPTIONAL_ARG_COMMANDS:
        func(db, args[0] if args else None)
    elif cmd in ("add-component", "add-need"):
        # Description-only commands: join all positional args into one description
        if not args:
            print(f"Usage: {cmd} {usage}")
            sys.exit(1)
        func(db, " ".join(args))
    elif cmd in ("set-component", "set-need"):
        # First arg is id, rest joined as description
        if len(args) < 2:
            print(f"Usage: {cmd} {usage}")
            sys.exit(1)
        func(db, args[0], " ".join(args[1:]))
    elif cmd in RATIONALE_EDGE_COMMANDS:
        # First two args are entity ids, rest joined as multi-word rationale
        if len(args) < 3:
            print(f"Usage: {cmd} {usage}")
            sys.exit(1)
        func(db, args[0], args[1], " ".join(args[2:]))
    elif cmd == "set-rationale":
        # First three args are edge_type + two entity ids, rest joined as rationale
        if len(args) < 4:
            print(f"Usage: {cmd} {usage}")
            sys.exit(1)
        func(db, args[0], args[1], args[2], " ".join(args[3:]))
    else:
        if len(args) < argc:
            print(f"Usage: {cmd} {usage}")
            sys.exit(1)
        func(db, *args[:argc])

    db.close()


if __name__ == "__main__":
    main()

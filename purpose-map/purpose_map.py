"""Purpose map for project evaluation.

Two entity types connected by two relationship types, plus location references:

  Needs       — concerns the project has (the "why")
  Components  — structural units that address needs (the "how")

Entities use auto-generated short ids (c1, c2, ... for components; n1, n2, ...
for needs). The description is the load-bearing meaning. All displays render
entries as `[id] description` so the id is always paired with its purpose,
preventing reasoning from a name alone.

Needs are project-implicit: the data structure lives within a project, so all
needs belong to the project by definition. There is no separate ownership
graph. Components are connected to needs only through the addressing graph,
where each addressing edge carries a rationale describing the specific
mechanism by which the component contributes.

Edges:

  depends_on      — component depends on component (structural DAG)
  addresses       — component addresses a need, with rationale (capability)
  component_paths — component → source-location reference (file path, optionally with #anchor)

Paths are non-authoritative location pointers — they record where the real
artifact lived when the entry was created so a future reader can find it
(or retrace it after a refactor).

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
    address <component> <need> <rationale>             Component addresses a need
    unaddress <component> <need>                       Remove addressing edge
    set-rationale <component> <need> <rationale>       Update rationale on an existing addressing edge
    add-path <component> <path>                        Record a source-location path
    remove-path <component> <path>                     Remove a recorded path

Rationales explain *why* an addressing edge exists. They are required when
creating addressing edges so the reasoning survives session boundaries and
can be re-evaluated when descriptions change. Rationales are displayed by
`how`, `why`, and the `addresses` view.

Commands — validation:
    validate <id>                          Validate a component or need (mark as confirmed)
    invalidate <id>                        Invalidate a component or need (remove validation)

Commands — analysis:
    dependencies [component-id] [--verify] Structural tree (with optional validation-chain check)
    addresses [id] [--gaps] [--orphans]    Addressing graph (entity, gaps, or orphans)
    where <component-id>                   Recorded source-location paths for a component
    why <component-id>                     What needs does this component address?
    how <need-id>                          What addresses this need? (with rationales)
    compare <component-a> <component-b>    Compare two components by addressing edges (common needs + each-only needs)
    summary                                Counts and per-need addressing status
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


def _comp_label(cid, description, validated):
    """Format a component as '◈ [id] description' with validation marker."""
    marker = "◈" if validated else "? ◈"
    return f"{marker} [{cid}] {description}"


def _need_label(nid, description, validated):
    """Format a need as '◇ [id] description' with validation marker."""
    marker = "◇" if validated else "? ◇"
    return f"{marker} [{nid}] {description}"


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS components (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            validated INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS needs (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            validated INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS depends_on (
            component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
            dependency_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
            PRIMARY KEY (component_id, dependency_id)
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


def set_rationale(db, a, b, rationale):
    """Update the rationale on an existing addressing edge."""
    if not rationale or not rationale.strip():
        print("Error: rationale cannot be empty")
        sys.exit(1)

    cur = db.execute(
        "UPDATE addresses SET rationale = ? WHERE component_id = ? AND need_id = ?",
        (rationale.strip(), a, b)
    )
    if cur.rowcount == 0:
        print(f"Error: addressing edge {a} → {b} not found")
        sys.exit(1)
    db.commit()
    print(f"Updated rationale: address {a} → {b}")
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


# --- Validation commands ---

def validate(db, item_id):
    for table in ("components", "needs"):
        r = db.execute(f"UPDATE {table} SET validated = 1 WHERE id = ?", (item_id,))
        if r.rowcount:
            db.commit()
            print(f"Validated: {item_id}")
            return
    print(f"Error: '{item_id}' not found")
    sys.exit(1)


def invalidate(db, item_id):
    for table in ("components", "needs"):
        r = db.execute(f"UPDATE {table} SET validated = 0 WHERE id = ?", (item_id,))
        if r.rowcount:
            db.commit()
            print(f"Invalidated: {item_id}")
            return
    print(f"Error: '{item_id}' not found")
    sys.exit(1)


# --- Analysis: dependencies ---

def dependencies(db, comp_id=None, verify=False):
    """Structural tree of components from depends_on edges only.

    With --verify, also reports unvalidated dependency ancestors for each component.
    """
    if comp_id:
        comp = db.execute("SELECT description, validated FROM components WHERE id = ?",
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
            SELECT c.id, c.description, c.validated FROM components c
            WHERE NOT EXISTS (
                SELECT 1 FROM depends_on d WHERE d.component_id = c.id
            )
            ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
        """).fetchall()
        for cid, cdesc, cvalidated in roots:
            _dep_tree(db, cid, cdesc, cvalidated)

        if verify:
            print()
            verify_all(db)


def _dep_tree(db, comp_id, description, validated, header_prefix="", cont_prefix=""):
    """Print component and its dependent components."""
    print(f"{header_prefix}{_comp_label(comp_id, description, validated)}")

    dependents = db.execute("""
        SELECT c.id, c.description, c.validated FROM depends_on d
        JOIN components c ON c.id = d.component_id
        WHERE d.dependency_id = ? ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
    """, (comp_id,)).fetchall()

    for i, (cid, cdesc, cvalidated) in enumerate(dependents):
        is_last = i == len(dependents) - 1
        branch = "└── " if is_last else "├── "
        cont = "    " if is_last else "│   "
        _dep_tree(db, cid, cdesc, cvalidated,
                  cont_prefix + branch, cont_prefix + cont)


def _coverage(db, need_id):
    """Return (status, summary) for a need: covered if any direct addressers, gap otherwise."""
    direct = [r[0] for r in db.execute(
        "SELECT component_id FROM addresses WHERE need_id = ? ORDER BY CAST(SUBSTR(component_id, 2) AS INTEGER)",
        (need_id,)
    ).fetchall()]

    if direct:
        return "covered", "addressed by " + ", ".join(direct)
    return "gap", "unaddressed"


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
        # All needs
        all_needs = db.execute("""
            SELECT id FROM needs
            ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)
        """).fetchall()
        for i, (nid,) in enumerate(all_needs):
            _addresses_for_need(db, nid)
            if i < len(all_needs) - 1:
                print()


def _addresses_for_need(db, need_id):
    """Show a need and its direct addressers with rationales."""
    need = db.execute("SELECT description, validated FROM needs WHERE id = ?",
                      (need_id,)).fetchone()
    print(_need_label(need_id, need[0], need[1]))

    direct = db.execute("""
        SELECT c.id, c.description, c.validated, a.rationale FROM addresses a
        JOIN components c ON c.id = a.component_id
        WHERE a.need_id = ? ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
    """, (need_id,)).fetchall()

    if not direct:
        print(f"  ✗ unaddressed (gap)")
        return

    for cid, cdesc, cvalidated, rationale in direct:
        print(f"  ↳ {_comp_label(cid, cdesc, cvalidated)}")
        if rationale:
            print(f"      rationale: {rationale}")


def _addresses_for_component(db, comp_id):
    """What does this component address?"""
    comp = db.execute("SELECT description, validated FROM components WHERE id = ?",
                      (comp_id,)).fetchone()
    print(_comp_label(comp_id, comp[0], comp[1]))

    addrs = db.execute("""
        SELECT n.id, n.description, n.validated FROM addresses a
        JOIN needs n ON n.id = a.need_id
        WHERE a.component_id = ? ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """, (comp_id,)).fetchall()

    if not addrs:
        print("  (addresses nothing)")
        return

    for nid, ndesc, nvalidated in addrs:
        print(f"  → {_need_label(nid, ndesc, nvalidated)}")


def _show_leaf_gaps(db):
    """Needs with no direct addressers — actionable gaps."""
    rows = db.execute("""
        SELECT n.id, n.description FROM needs n
        WHERE NOT EXISTS (SELECT 1 FROM addresses a WHERE a.need_id = n.id)
        ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """).fetchall()
    if not rows:
        print("No gaps — every need has at least one addresser")
        return
    print(f"Gaps ({len(rows)}) — needs with no addressers:")
    for nid, desc in rows:
        print(f"  ✗ [{nid}] {desc}")


def _show_orphans(db):
    """Components that don't address anything."""
    rows = db.execute("""
        SELECT c.id, c.description, c.validated FROM components c
        WHERE NOT EXISTS (SELECT 1 FROM addresses a WHERE a.component_id = c.id)
        ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
    """).fetchall()
    if not rows:
        print("No orphans — every component addresses at least one need")
        return
    print(f"Orphan components ({len(rows)}):")
    for cid, desc, validated in rows:
        print(f"  {_comp_label(cid, desc, validated)}")


# --- Analysis: where, why, how ---

def where(db, comp_id):
    """Show recorded source-location paths for a component.

    Paths are non-authoritative pointers — true at creation, possibly stale
    after refactors. If they're broken, retrace by purpose using navigator
    or by content using grep, then update.
    """
    comp = db.execute("SELECT description, validated FROM components WHERE id = ?",
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
    """Upward trace: what needs does this component address?"""
    comp = db.execute("SELECT description, validated FROM components WHERE id = ?",
                      (comp_id,)).fetchone()
    if not comp:
        print(f"Error: component '{comp_id}' not found")
        sys.exit(1)

    print(_comp_label(comp_id, comp[0], comp[1]))

    addressed = db.execute("""
        SELECT n.id, n.description, n.validated, a.rationale FROM addresses a
        JOIN needs n ON n.id = a.need_id
        WHERE a.component_id = ? ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
    """, (comp_id,)).fetchall()

    if not addressed:
        print("  (addresses nothing)")
        return

    for nid, ndesc, nvalidated, rationale in addressed:
        print(f"  ↑ addresses: {_need_label(nid, ndesc, nvalidated)}")
        if rationale:
            print(f"      rationale: {rationale}")


def how(db, need_id):
    """Show a need with all direct addressers and their rationales."""
    if not db.execute("SELECT 1 FROM needs WHERE id = ?", (need_id,)).fetchone():
        print(f"Error: need '{need_id}' not found")
        sys.exit(1)
    _addresses_for_need(db, need_id)


def compare(db, comp_a, comp_b):
    """Compare two components by their addressing edges. Shows common needs
    (both address) with each component's rationale side-by-side, and needs
    that only one addresses.

    Used to evaluate whether two components are doing the same thing through
    overlapping mechanisms (e.g., a rule and a hook that enforce the same
    constraint at different layers).
    """
    for cid in (comp_a, comp_b):
        if not db.execute("SELECT 1 FROM components WHERE id = ?", (cid,)).fetchone():
            print(f"Error: component '{cid}' not found")
            sys.exit(1)

    comp_a_data = db.execute(
        "SELECT description, validated FROM components WHERE id = ?", (comp_a,)
    ).fetchone()
    comp_b_data = db.execute(
        "SELECT description, validated FROM components WHERE id = ?", (comp_b,)
    ).fetchone()

    print(f"=== {comp_a} ===")
    print(_comp_label(comp_a, comp_a_data[0], comp_a_data[1]))
    print(f"\n=== {comp_b} ===")
    print(_comp_label(comp_b, comp_b_data[0], comp_b_data[1]))

    addr_a = {
        row[0]: row for row in db.execute("""
            SELECT n.id, n.description, n.validated, a.rationale
            FROM addresses a JOIN needs n ON n.id = a.need_id
            WHERE a.component_id = ?
            ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
        """, (comp_a,)).fetchall()
    }
    addr_b = {
        row[0]: row for row in db.execute("""
            SELECT n.id, n.description, n.validated, a.rationale
            FROM addresses a JOIN needs n ON n.id = a.need_id
            WHERE a.component_id = ?
            ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
        """, (comp_b,)).fetchall()
    }

    common = sorted(set(addr_a) & set(addr_b), key=lambda x: int(x[1:]))
    only_a = sorted(set(addr_a) - set(addr_b), key=lambda x: int(x[1:]))
    only_b = sorted(set(addr_b) - set(addr_a), key=lambda x: int(x[1:]))

    if common:
        print(f"\n=== COMMON NEEDS ({len(common)}) — both components address ===")
        for nid in common:
            row = addr_a[nid]
            print(_need_label(nid, row[1], row[2]))
            print(f"  {comp_a}: {row[3]}")
            print(f"  {comp_b}: {addr_b[nid][3]}")

    if only_a:
        print(f"\n=== {comp_a} ONLY ({len(only_a)}) ===")
        for nid in only_a:
            row = addr_a[nid]
            print(_need_label(nid, row[1], row[2]))
            if row[3]:
                print(f"  rationale: {row[3]}")

    if only_b:
        print(f"\n=== {comp_b} ONLY ({len(only_b)}) ===")
        for nid in only_b:
            row = addr_b[nid]
            print(_need_label(nid, row[1], row[2]))
            if row[3]:
                print(f"  rationale: {row[3]}")

    if not common and not only_a and not only_b:
        print(f"\n(neither component addresses any need)")


# --- Summary ---

def summary(db):
    """Counts and per-need addressing status."""
    comp_count = db.execute("SELECT COUNT(*) FROM components").fetchone()[0]
    need_count = db.execute("SELECT COUNT(*) FROM needs").fetchone()[0]
    dep_count = db.execute("SELECT COUNT(*) FROM depends_on").fetchone()[0]
    addr_count = db.execute("SELECT COUNT(*) FROM addresses").fetchone()[0]

    gaps = db.execute("""
        SELECT COUNT(*) FROM needs n
        WHERE NOT EXISTS (SELECT 1 FROM addresses a WHERE a.need_id = n.id)
    """).fetchone()[0]

    validated_comps = db.execute(
        "SELECT COUNT(*) FROM components WHERE validated = 1"
    ).fetchone()[0]
    validated_needs = db.execute(
        "SELECT COUNT(*) FROM needs WHERE validated = 1"
    ).fetchone()[0]

    print(f"Components: {comp_count} ({validated_comps} validated)")
    print(f"Needs: {need_count} ({validated_needs} validated)")
    print(f"Dependencies: {dep_count} | Addresses: {addr_count}")
    print(f"Gaps: {gaps}")

    all_needs = db.execute("""
        SELECT id, description, validated FROM needs
        ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)
    """).fetchall()
    if all_needs:
        print(f"\nNeeds ({len(all_needs)}):")
        for nid, desc, validated in all_needs:
            status, _ = _coverage(db, nid)
            marker = {"covered": "✓", "gap": "✗"}[status]
            print(f"  {marker} {_need_label(nid, desc, validated)}")


# --- Helpers ---

def verify_all(db):
    """Run validation-chain verify on every component."""
    all_comps = db.execute("SELECT id FROM components ORDER BY id").fetchall()
    any_unvalidated = False
    for (cid,) in all_comps:
        if not _verify_one(db, cid, quiet=True):
            any_unvalidated = True
    if not any_unvalidated:
        print("✓ All dependency chains fully validated")


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
        SELECT DISTINCT c.id, c.description, c.validated
        FROM ancestors a
        JOIN components c ON c.id = a.id
    """, (comp_id,)).fetchall()

    if not rows:
        if not quiet:
            print(f"✓ {comp_id} has no dependency ancestors")
        return True

    unvalidated = [(cid, desc) for cid, desc, validated in rows if not validated]
    all_validated = not unvalidated

    if not quiet or not all_validated:
        if all_validated:
            print(f"✓ [{comp_id}] all dependencies validated")
        else:
            print(f"✗ [{comp_id}] unvalidated dependencies:")
            for cid, desc in unvalidated:
                print(f"    ✗ [{cid}] {desc}")

    return all_validated


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
    "address":          (address,          3, "<component> <need> <rationale>"),
    "unaddress":        (unaddress,        2, "<component> <need>"),
    "set-rationale":    (set_rationale,    3, "<component> <need> <rationale>"),
    "add-path":         (add_path,         2, "<component> <path>"),
    "remove-path":      (remove_path,      2, "<component> <path>"),
    "validate":         (validate,         1, "<id>"),
    "invalidate":       (invalidate,       1, "<id>"),
    "dependencies":     (dependencies,     0, "[component-id] [--verify]"),
    "addresses":        (addresses_view,   0, "[id] [--gaps] [--orphans]"),
    "where":            (where,            1, "<component-id>"),
    "why":              (why,              1, "<component-id>"),
    "how":              (how,              1, "<need-id>"),
    "compare":          (compare,          2, "<component-a> <component-b>"),
    "summary":          (summary,          0, ""),
}

OPTIONAL_ARG_COMMANDS = {"dependencies", "addresses"}
RATIONALE_EDGE_COMMANDS = {"address", "set-rationale"}


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
    else:
        if len(args) < argc:
            print(f"Usage: {cmd} {usage}")
            sys.exit(1)
        func(db, *args[:argc])

    db.close()


if __name__ == "__main__":
    main()

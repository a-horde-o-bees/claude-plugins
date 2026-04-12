"""Coverage tools — domains, goals, junction links, and coverage/effectiveness metrics.

Domains categorize what criteria measure. Goals define success requirements.
Junction tables link goals to domains and domains to criteria.
"""

from __future__ import annotations

import sqlite3

from . import _helpers
from ._helpers import _check_db, _ok, _err

from skills.research._coverage import (
    register_domains as _register_domains,
    add_domain as _add_domain,
    remove_domain as _remove_domain,
    get_domains as _get_domains,
    register_goals as _register_goals,
    add_goal as _add_goal,
    remove_goal as _remove_goal,
    get_goals as _get_goals,
    link_goal_domain as _link_goal_domain,
    unlink_goal_domain as _unlink_goal_domain,
    link_domain_criterion as _link_domain_criterion,
    unlink_domain_criterion as _unlink_domain_criterion,
    get_coverage as _get_coverage,
)
from skills.research._effectiveness import (
    get_criteria_effectiveness as _get_criteria_effectiveness,
)


def set_domains(domains: list[dict]) -> str:
    """Replace ALL domain definitions. Cascades: removes old junction links.

    Args:
        domains: List of domain objects, each with name and optional description
    """
    if err := _check_db(): return err
    try:
        return _ok(_register_domains(_helpers.DB_PATH, domains))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def add_domain(name: str, description: str = "") -> str:
    """Add single domain definition.

    Args:
        name: Domain name
        description: What this domain covers
    """
    if err := _check_db(): return err
    try:
        return _ok(_add_domain(_helpers.DB_PATH, name, description))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def remove_domain(domain_id: str) -> str:
    """Remove domain and cascade-delete junction links.

    Args:
        domain_id: Domain ID (e.g., d1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_remove_domain(_helpers.DB_PATH, domain_id))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def get_domains() -> str:
    """List all domains with linked criteria counts."""
    if err := _check_db(): return err
    return _ok(_get_domains(_helpers.DB_PATH))


def link_domain_criterion(domain_id: str, criterion_id: str) -> str:
    """Link domain to criterion. Many-to-many: criterion can serve multiple domains.

    Args:
        domain_id: Domain ID (e.g., d1)
        criterion_id: Criterion ID (e.g., c1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_link_domain_criterion(_helpers.DB_PATH, domain_id, criterion_id))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def unlink_domain_criterion(domain_id: str, criterion_id: str) -> str:
    """Unlink domain from criterion.

    Args:
        domain_id: Domain ID (e.g., d1)
        criterion_id: Criterion ID (e.g., c1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_unlink_domain_criterion(_helpers.DB_PATH, domain_id, criterion_id))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def set_goals(goals: list[dict]) -> str:
    """Replace ALL goal definitions. Cascades: removes old junction links.

    Args:
        goals: List of goal objects, each with name and optional description
    """
    if err := _check_db(): return err
    try:
        return _ok(_register_goals(_helpers.DB_PATH, goals))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def add_goal(name: str, description: str = "") -> str:
    """Add single goal definition.

    Args:
        name: Goal name
        description: What this goal requires for success
    """
    if err := _check_db(): return err
    try:
        return _ok(_add_goal(_helpers.DB_PATH, name, description))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def remove_goal(goal_id: str) -> str:
    """Remove goal and cascade-delete junction links.

    Args:
        goal_id: Goal ID (e.g., g1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_remove_goal(_helpers.DB_PATH, goal_id))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def get_goals() -> str:
    """List all goals with linked domain counts."""
    if err := _check_db(): return err
    return _ok(_get_goals(_helpers.DB_PATH))


def link_goal_domain(goal_id: str, domain_id: str) -> str:
    """Link goal to domain. Many-to-many: domain can serve multiple goals.

    Args:
        goal_id: Goal ID (e.g., g1)
        domain_id: Domain ID (e.g., d1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_link_goal_domain(_helpers.DB_PATH, goal_id, domain_id))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def unlink_goal_domain(goal_id: str, domain_id: str) -> str:
    """Unlink goal from domain.

    Args:
        goal_id: Goal ID (e.g., g1)
        domain_id: Domain ID (e.g., d1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_unlink_goal_domain(_helpers.DB_PATH, goal_id, domain_id))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def get_coverage() -> str:
    """Compute coverage metrics per domain. Deterministic — all from database state.

    Returns per-domain: distinct researched entity count, criteria count,
    avg notes per entity. Plus entity pool trajectory.
    """
    if err := _check_db(): return err
    return _ok(_get_coverage(_helpers.DB_PATH))


def get_criteria_effectiveness() -> str:
    """Compute criteria effectiveness metrics. Deterministic — all from database state.

    Returns per-criterion: pass/fail/not-assessed counts, hit rate,
    discrimination, hardline rejection distribution, untriggered criteria.
    """
    if err := _check_db(): return err
    return _ok(_get_criteria_effectiveness(_helpers.DB_PATH))

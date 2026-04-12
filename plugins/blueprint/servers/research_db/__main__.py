"""MCP server entry point for blueprint research database.

Registers all domain tools on the FastMCP instance and runs the server
via stdio transport. Database path from DB_PATH env var.

Launched via run.py: python3 run.py servers.research_db
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

import servers.research_db as _srv

mcp = FastMCP("blueprint-research")

# ============================================================
# Registration
# ============================================================

mcp.tool()(_srv.register_entity)
mcp.tool()(_srv.register_entities)

# ============================================================
# Entity scalar properties
# ============================================================

mcp.tool()(_srv.set_name)
mcp.tool()(_srv.clear_name)
mcp.tool()(_srv.set_description)
mcp.tool()(_srv.clear_description)
mcp.tool()(_srv.set_purpose)
mcp.tool()(_srv.clear_purpose)
mcp.tool()(_srv.set_relevance)
mcp.tool()(_srv.clear_relevance)
mcp.tool()(_srv.set_stage)

# ============================================================
# Modes
# ============================================================

mcp.tool()(_srv.set_modes)
mcp.tool()(_srv.add_modes)
mcp.tool()(_srv.remove_modes)
mcp.tool()(_srv.clear_modes)

# ============================================================
# Notes
# ============================================================

mcp.tool()(_srv.add_notes)
mcp.tool()(_srv.set_note)
mcp.tool()(_srv.remove_notes)
mcp.tool()(_srv.clear_notes)

# ============================================================
# Measures
# ============================================================

mcp.tool()(_srv.set_measures)
mcp.tool()(_srv.clear_measures)
mcp.tool()(_srv.clear_all_measures)

# ============================================================
# URLs and Provenance
# ============================================================

mcp.tool()(_srv.add_url)
mcp.tool()(_srv.add_provenance)

# ============================================================
# Compound operations
# ============================================================

mcp.tool()(_srv.reject_entity)
mcp.tool()(_srv.merge_entities)

# ============================================================
# Queries
# ============================================================

mcp.tool()(_srv.get_entity)
mcp.tool()(_srv.list_entities)
mcp.tool()(_srv.get_research_queue)
mcp.tool()(_srv.get_unclassified)
mcp.tool()(_srv.find_duplicates)
mcp.tool()(_srv.get_dashboard)
mcp.tool()(_srv.get_measure_summary)

# ============================================================
# Criteria
# ============================================================

mcp.tool()(_srv.set_criteria)
mcp.tool()(_srv.add_criterion)
mcp.tool()(_srv.remove_criterion)
mcp.tool()(_srv.get_criteria)
mcp.tool()(_srv.link_criterion_note)
mcp.tool()(_srv.unlink_criterion_note)
mcp.tool()(_srv.clear_criterion_links)
mcp.tool()(_srv.get_assessment)
mcp.tool()(_srv.compute_relevance)

# ============================================================
# Infrastructure
# ============================================================

mcp.tool()(_srv.init_database)
mcp.tool()(_srv.describe_schema)

# ============================================================
# Domains
# ============================================================

mcp.tool()(_srv.set_domains)
mcp.tool()(_srv.add_domain)
mcp.tool()(_srv.remove_domain)
mcp.tool()(_srv.get_domains)
mcp.tool()(_srv.link_domain_criterion)
mcp.tool()(_srv.unlink_domain_criterion)

# ============================================================
# Goals
# ============================================================

mcp.tool()(_srv.set_goals)
mcp.tool()(_srv.add_goal)
mcp.tool()(_srv.remove_goal)
mcp.tool()(_srv.get_goals)
mcp.tool()(_srv.link_goal_domain)
mcp.tool()(_srv.unlink_goal_domain)

# ============================================================
# Coverage and effectiveness
# ============================================================

mcp.tool()(_srv.get_coverage)
mcp.tool()(_srv.get_criteria_effectiveness)

# --- Entry point ---

mcp.run()

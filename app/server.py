"""Real Estate Sustainability Analysis MCP - FastMCP Server with RefCache and Langfuse Tracing.

This module creates and configures the FastMCP server, wiring together
tools from the modular tools package.

Features:
- ESG assessment for existing buildings (Bestandsgebäude)
- Project store with SQLite persistence
- Data collection for energy and consumption metrics
- EU Taxonomy alignment checking
- Reference-based caching for large results
- Langfuse tracing integration for observability

Usage:
    # Run with typer CLI
    uvx real-estate-sustainability-mcp stdio           # Local CLI mode
    uvx real-estate-sustainability-mcp streamable-http # Remote/Docker mode

    # Or with uv
    uv run real-estate-sustainability-mcp stdio
"""

from __future__ import annotations

from fastmcp import FastMCP
from mcp_refcache import PreviewConfig, PreviewStrategy, RefCache
from mcp_refcache.fastmcp import cache_instructions

from app.prompts import langfuse_guide, template_guide
from app.tools import (
    # ESG tools - Data Collection
    add_consumption_data,
    add_energy_data,
    # ESG tools - Analysis
    calculate_carbon_footprint,
    calculate_energy_intensity,
    # ESG tools - Gap Analysis
    check_data_completeness,
    check_eu_taxonomy_alignment,
    # ESG tools - Project Store
    create_building_project,
    # Utilities
    create_get_cached_result,
    create_health_check,
    delete_building_project,
    get_building_project,
    get_project_data,
    list_building_projects,
    suggest_data_sources,
    update_building_project,
)
from app.tracing import TracedRefCache

# =============================================================================
# Initialize FastMCP Server
# =============================================================================

mcp = FastMCP(
    name="Real Estate Sustainability Analysis MCP",
    instructions=f"""MCP server for ESG assessment of existing commercial buildings (Bestandsgebäude).

Supports the sustainability assessment workflow:
1. Create building projects and collect data
2. Analyze data gaps and suggest sources
3. Calculate energy intensity and carbon footprint
4. Check EU Taxonomy alignment

All tool calls are traced to Langfuse with user/session attribution.


Available tools:

PROJECT STORE:
- create_building_project: Create a new building for ESG assessment
- get_building_project: Get project details with all related data
- update_building_project: Update building details
- list_building_projects: List all projects with pagination
- delete_building_project: Delete a project and all data

DATA COLLECTION:
- add_energy_data: Add annual energy consumption (electricity, gas, etc.)
- add_consumption_data: Add water, waste, and other consumption data
- get_project_data: Get all collected data for a project

GAP ANALYSIS:
- check_data_completeness: Check what data is missing
- suggest_data_sources: Get suggestions for data collection

ESG ANALYSIS:
- calculate_energy_intensity: Calculate kWh/m²/a with energy rating
- calculate_carbon_footprint: Calculate kgCO2/m²/a with emission breakdown
- check_eu_taxonomy_alignment: Check EU Taxonomy Activity 7.7 alignment

UTILITY:
- get_cached_result: Retrieve or paginate through cached results
- health_check: Check server health status


{cache_instructions()}
""",
)

# =============================================================================
# Initialize RefCache with Langfuse Tracing
# =============================================================================

# Create the base RefCache instance
_cache = RefCache(
    name="real-estate-sustainability-mcp",
    default_ttl=3600,  # 1 hour TTL
    preview_config=PreviewConfig(
        max_size=2048,  # Max 2048 tokens in previews
        default_strategy=PreviewStrategy.SAMPLE,  # Sample large collections
    ),
)

# Wrap with TracedRefCache for Langfuse observability
cache = TracedRefCache(_cache)

# =============================================================================
# Create Bound Tool Functions
# =============================================================================

# These are created with factory functions and bound to the cache instance.
get_cached_result = create_get_cached_result(cache)
health_check = create_health_check(_cache)

# =============================================================================
# Register Tools
# =============================================================================

# --- Project Store Tools ---
mcp.tool(create_building_project)
mcp.tool(get_building_project)
mcp.tool(update_building_project)
mcp.tool(list_building_projects)
mcp.tool(delete_building_project)

# --- Data Collection Tools ---
mcp.tool(add_energy_data)
mcp.tool(add_consumption_data)
mcp.tool(get_project_data)

# --- Gap Analysis Tools ---
mcp.tool(check_data_completeness)
mcp.tool(suggest_data_sources)

# --- ESG Analysis Tools ---
mcp.tool(calculate_energy_intensity)
mcp.tool(calculate_carbon_footprint)
mcp.tool(check_eu_taxonomy_alignment)

# --- Utility Tools ---
mcp.tool(get_cached_result)
mcp.tool(health_check)

# =============================================================================
# Register Prompts
# =============================================================================


@mcp.prompt
def _template_guide() -> str:
    """Guide for using this MCP server template."""
    return template_guide()


@mcp.prompt
def _langfuse_guide() -> str:
    """Guide for using Langfuse tracing with this server."""
    return langfuse_guide()

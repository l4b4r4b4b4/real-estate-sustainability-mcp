"""Tools module for Real Estate Sustainability MCP Server.

This module re-exports all tools from submodules for convenient access.

Tool Modules:
- esg: ESG assessment tools for building projects (Phase 1)
- cache: Cache query and retrieval
- health: Health check functionality
"""

from __future__ import annotations

from app.tools.cache import CacheQueryInput, create_get_cached_result
from app.tools.esg import (
    add_consumption_data,
    add_energy_data,
    calculate_carbon_footprint,
    calculate_energy_intensity,
    check_data_completeness,
    check_eu_taxonomy_alignment,
    create_building_project,
    delete_building_project,
    get_building_project,
    get_project_data,
    list_building_projects,
    suggest_data_sources,
    update_building_project,
)
from app.tools.health import create_health_check

__all__ = [
    # Utility tools
    "CacheQueryInput",
    # ESG tools - Data Collection
    "add_consumption_data",
    "add_energy_data",
    # ESG tools - Analysis
    "calculate_carbon_footprint",
    "calculate_energy_intensity",
    # ESG tools - Gap Analysis
    "check_data_completeness",
    "check_eu_taxonomy_alignment",
    # ESG tools - Project Store
    "create_building_project",
    "create_get_cached_result",
    "create_health_check",
    "delete_building_project",
    "get_building_project",
    "get_project_data",
    "list_building_projects",
    "suggest_data_sources",
    "update_building_project",
]

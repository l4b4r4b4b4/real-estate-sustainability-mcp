"""Data models for Real Estate Sustainability MCP Server.

This module re-exports all Pydantic models for convenient access.

Model Categories:
- Building: Core building project models
- Energy: Energy consumption data models
- Consumption: Non-energy consumption models
- Analysis: Result models for ESG analysis
"""

from __future__ import annotations

from app.models.building import (
    ANALYSIS_REQUIREMENTS,
    AnalysisType,
    BuildingProject,
    BuildingProjectCreate,
    BuildingProjectUpdate,
    BuildingType,
    CarbonFootprintResult,
    ConsumptionCategory,
    ConsumptionData,
    ConsumptionDataCreate,
    DataCompletenessResult,
    DataSource,
    EnergyData,
    EnergyDataCreate,
    EnergyIntensityResult,
    EnergyType,
    EUTaxonomyResult,
)

__all__ = [
    # Analysis requirements
    "ANALYSIS_REQUIREMENTS",
    "AnalysisType",
    # Building models
    "BuildingProject",
    "BuildingProjectCreate",
    "BuildingProjectUpdate",
    # Enums
    "BuildingType",
    # Analysis results
    "CarbonFootprintResult",
    "ConsumptionCategory",
    # Consumption models
    "ConsumptionData",
    "ConsumptionDataCreate",
    "DataCompletenessResult",
    "DataSource",
    "EUTaxonomyResult",
    # Energy models
    "EnergyData",
    "EnergyDataCreate",
    "EnergyIntensityResult",
    "EnergyType",
]

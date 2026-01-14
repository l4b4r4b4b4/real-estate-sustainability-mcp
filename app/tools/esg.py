"""ESG analysis tools for building projects.

This module provides tools for ESG assessment of existing commercial buildings
(Bestandsgebäude), including energy intensity calculation, carbon footprint,
EU Taxonomy alignment, and data completeness checking.

Tools follow the Phase 1 design from the project roadmap.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import Field

from app.models import (
    ANALYSIS_REQUIREMENTS,
    AnalysisType,
    BuildingProjectCreate,
    BuildingProjectUpdate,
    BuildingType,
    CarbonFootprintResult,
    ConsumptionCategory,
    ConsumptionDataCreate,
    DataCompletenessResult,
    DataSource,
    EnergyDataCreate,
    EnergyIntensityResult,
    EnergyType,
    EUTaxonomyResult,
)
from app.store import get_store
from app.tracing import traced_tool

# =============================================================================
# Constants: Emission Factors and Thresholds
# =============================================================================

# German grid emission factors (gCO2/kWh) - Source: Umweltbundesamt 2023
EMISSION_FACTORS: dict[EnergyType, float] = {
    EnergyType.ELECTRICITY: 380.0,  # German grid mix 2023
    EnergyType.GAS: 201.0,
    EnergyType.DISTRICT_HEATING: 240.0,  # Average, varies by provider
    EnergyType.DISTRICT_COOLING: 150.0,  # Estimate
    EnergyType.OIL: 266.0,
    EnergyType.BIOMASS: 23.0,  # Only direct emissions
    EnergyType.SOLAR_THERMAL: 0.0,
    EnergyType.OTHER: 250.0,  # Conservative estimate
}

# Primary energy factors (GEG 2024)
PRIMARY_ENERGY_FACTORS: dict[EnergyType, float] = {
    EnergyType.ELECTRICITY: 1.8,
    EnergyType.GAS: 1.1,
    EnergyType.DISTRICT_HEATING: 0.7,  # Varies by provider
    EnergyType.DISTRICT_COOLING: 1.0,
    EnergyType.OIL: 1.1,
    EnergyType.BIOMASS: 0.2,
    EnergyType.SOLAR_THERMAL: 0.0,
    EnergyType.OTHER: 1.5,
}

# EU Taxonomy thresholds (kWh/m²/a primary energy) by building type
# Source: EU Taxonomy Climate Delegated Act, Annex I, Section 7.7
EU_TAXONOMY_THRESHOLDS: dict[BuildingType, float] = {
    BuildingType.OFFICE: 100.0,
    BuildingType.RESIDENTIAL: 100.0,
    BuildingType.RETAIL: 120.0,
    BuildingType.MIXED: 110.0,
    BuildingType.INDUSTRIAL: 150.0,
    BuildingType.HOTEL: 120.0,
    BuildingType.LOGISTICS: 100.0,
    BuildingType.HEALTHCARE: 180.0,
    BuildingType.EDUCATION: 120.0,
}

# Energy rating thresholds (kWh/m²/year final energy)
ENERGY_RATING_THRESHOLDS = {
    "A+": 25,
    "A": 50,
    "B": 75,
    "C": 100,
    "D": 150,
    "E": 200,
    "F": 250,
    "G": float("inf"),
}


# =============================================================================
# Project Store Tools
# =============================================================================


@traced_tool("create_building_project")
def create_building_project(
    name: str = Field(..., description="Name or identifier for the building"),
    floor_area_sqm: float = Field(..., gt=0, description="Net floor area in m²"),
    construction_year: int = Field(..., ge=1800, le=2030, description="Year built"),
    building_type: str = Field(
        default="office",
        description="Building type: office, residential, retail, mixed, industrial, hotel, logistics, healthcare, education",
    ),
    address: str = Field(default="", description="Full address of the building"),
    city: str = Field(default="", description="City where building is located"),
    country: str = Field(default="DE", description="ISO country code (default: DE)"),
    renovation_year: int | None = Field(
        default=None, description="Year of last major renovation"
    ),
    epc_rating: str | None = Field(
        default=None, description="Energy Performance Certificate rating (A-G)"
    ),
    notes: str = Field(default="", description="Additional notes"),
) -> dict[str, Any]:
    """Create a new building project for ESG assessment.

    Creates a building project in the database that can be used to collect
    energy data, consumption data, and run sustainability analyses.

    Returns:
        Dictionary containing the created project details including the
        generated project_id for use in subsequent operations.

    Example:
        >>> result = create_building_project(
        ...     name="Klöpperhaus",
        ...     floor_area_sqm=5000,
        ...     construction_year=1985,
        ...     building_type="office",
        ...     city="Hamburg"
        ... )
        >>> project_id = result["project"]["project_id"]
    """
    store = get_store()

    # Parse building type
    try:
        bt = BuildingType(building_type.lower())
    except ValueError:
        bt = BuildingType.OFFICE

    project_data = BuildingProjectCreate(
        name=name,
        floor_area_sqm=floor_area_sqm,
        construction_year=construction_year,
        building_type=bt,
        address=address,
        city=city,
        country=country,
        renovation_year=renovation_year,
        epc_rating=epc_rating,
        notes=notes,
    )

    project = store.create_project(project_data)

    return {
        "status": "created",
        "project": project.model_dump(mode="json"),
        "message": f"Building project '{name}' created successfully",
        "next_steps": [
            f"Add energy data with add_energy_data(project_id='{project.project_id}', ...)",
            f"Check data completeness with check_data_completeness(project_id='{project.project_id}')",
        ],
    }


@traced_tool("get_building_project")
def get_building_project(
    project_id: str = Field(..., description="The project's unique identifier"),
) -> dict[str, Any]:
    """Get a building project by ID with all related data.

    Retrieves the building project details along with summary information
    about collected energy and consumption data.

    Returns:
        Dictionary with project details, energy data, and consumption data,
        or an error message if the project is not found.
    """
    store = get_store()
    summary = store.get_project_summary(project_id)

    if summary is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
            "suggestion": "Use list_building_projects() to see available projects",
        }

    return {
        "status": "found",
        **summary,
    }


@traced_tool("update_building_project")
def update_building_project(
    project_id: str = Field(..., description="The project's unique identifier"),
    name: str | None = Field(default=None, description="New name"),
    address: str | None = Field(default=None, description="New address"),
    city: str | None = Field(default=None, description="New city"),
    floor_area_sqm: float | None = Field(default=None, description="New floor area"),
    renovation_year: int | None = Field(default=None, description="Renovation year"),
    epc_rating: str | None = Field(default=None, description="New EPC rating"),
    notes: str | None = Field(default=None, description="New notes"),
) -> dict[str, Any]:
    """Update a building project's details.

    Only provided fields will be updated. Omit fields you don't want to change.

    Returns:
        Updated project details or error if not found.
    """
    store = get_store()

    update_data = BuildingProjectUpdate(
        name=name,
        address=address,
        city=city,
        floor_area_sqm=floor_area_sqm,
        renovation_year=renovation_year,
        epc_rating=epc_rating,
        notes=notes,
    )

    project = store.update_project(project_id, update_data)

    if project is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    return {
        "status": "updated",
        "project": project.model_dump(mode="json"),
    }


@traced_tool("list_building_projects")
def list_building_projects(
    limit: int = Field(default=20, ge=1, le=100, description="Max projects to return"),
    offset: int = Field(default=0, ge=0, description="Number of projects to skip"),
) -> dict[str, Any]:
    """List all building projects with pagination.

    Returns:
        Dictionary with list of projects and pagination info.
    """
    store = get_store()
    projects = store.list_projects(limit=limit, offset=offset)
    total = store.count_projects()

    return {
        "status": "success",
        "projects": [p.model_dump(mode="json") for p in projects],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(projects) < total,
        },
    }


@traced_tool("delete_building_project")
def delete_building_project(
    project_id: str = Field(..., description="The project's unique identifier"),
) -> dict[str, Any]:
    """Delete a building project and all related data.

    Warning: This action cannot be undone. All energy and consumption
    data associated with this project will also be deleted.

    Returns:
        Confirmation of deletion or error if not found.
    """
    store = get_store()
    deleted = store.delete_project(project_id)

    if not deleted:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    return {
        "status": "deleted",
        "message": f"Project '{project_id}' and all related data deleted",
    }


# =============================================================================
# Data Collection Tools
# =============================================================================


@traced_tool("add_energy_data")
def add_energy_data(
    project_id: str = Field(..., description="The project's unique identifier"),
    year: int = Field(..., ge=2000, le=2030, description="Year of consumption"),
    consumption_kwh: float = Field(..., ge=0, description="Annual consumption in kWh"),
    energy_type: str = Field(
        default="electricity",
        description="Energy type: electricity, gas, district_heating, district_cooling, oil, biomass, solar_thermal, other",
    ),
    source: str = Field(
        default="utility_bill",
        description="Data source: utility_bill, smart_meter, estimate, benchmark, energy_audit, bms, tenant_report, other",
    ),
    is_estimated: bool = Field(
        default=False, description="Whether this value is an estimate"
    ),
    notes: str = Field(default="", description="Additional notes"),
) -> dict[str, Any]:
    """Add annual energy consumption data to a building project.

    Use this to record energy consumption from utility bills, smart meters,
    or other sources. Multiple records per year are allowed for different
    energy types.

    Returns:
        The created energy data record or error if project not found.

    Example:
        >>> add_energy_data(
        ...     project_id="abc-123",
        ...     year=2023,
        ...     consumption_kwh=250000,
        ...     energy_type="electricity",
        ...     source="utility_bill"
        ... )
    """
    store = get_store()

    # Parse enums
    try:
        et = EnergyType(energy_type.lower())
    except ValueError:
        et = EnergyType.OTHER

    try:
        ds = DataSource(source.lower())
    except ValueError:
        ds = DataSource.OTHER

    energy_data = EnergyDataCreate(
        year=year,
        energy_type=et,
        consumption_kwh=consumption_kwh,
        source=ds,
        is_estimated=is_estimated,
        notes=notes,
    )

    result = store.add_energy_data(project_id, energy_data)

    if result is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    return {
        "status": "created",
        "energy_data": result.model_dump(mode="json"),
        "message": f"Added {consumption_kwh:,.0f} kWh of {energy_type} for year {year}",
    }


@traced_tool("add_consumption_data")
def add_consumption_data(
    project_id: str = Field(..., description="The project's unique identifier"),
    year: int = Field(..., ge=2000, le=2030, description="Year of consumption"),
    category: str = Field(
        ...,
        description="Category: water, waste_total, waste_recycled, tenant_electricity, common_area_electricity",
    ),
    value: float = Field(..., ge=0, description="Consumption value"),
    unit: str = Field(..., description="Unit of measurement (e.g., m3, kg, kWh)"),
    source: str = Field(default="utility_bill", description="Data source"),
    is_estimated: bool = Field(
        default=False, description="Whether this value is an estimate"
    ),
    notes: str = Field(default="", description="Additional notes"),
) -> dict[str, Any]:
    """Add non-energy consumption data (water, waste) to a building project.

    Returns:
        The created consumption data record or error if project not found.
    """
    from app.models import ConsumptionCategory

    store = get_store()

    # Parse enums
    try:
        cat = ConsumptionCategory(category.lower())
    except ValueError:
        return {
            "status": "error",
            "error": f"Invalid category '{category}'. Valid options: water, waste_total, waste_recycled, tenant_electricity, common_area_electricity",
        }

    try:
        ds = DataSource(source.lower())
    except ValueError:
        ds = DataSource.OTHER

    consumption_data = ConsumptionDataCreate(
        year=year,
        category=cat,
        value=value,
        unit=unit,
        source=ds,
        is_estimated=is_estimated,
        notes=notes,
    )

    result = store.add_consumption_data(project_id, consumption_data)

    if result is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    return {
        "status": "created",
        "consumption_data": result.model_dump(mode="json"),
        "message": f"Added {value:,.0f} {unit} of {category} for year {year}",
    }


@traced_tool("get_project_data")
def get_project_data(
    project_id: str = Field(..., description="The project's unique identifier"),
    year: int | None = Field(default=None, description="Filter by specific year"),
) -> dict[str, Any]:
    """Get all collected data for a building project.

    Retrieves energy data and consumption data, optionally filtered by year.

    Returns:
        Dictionary with all collected data for the project.
    """
    store = get_store()

    project = store.get_project(project_id)
    if project is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    energy_data = store.get_energy_data(project_id, year=year)
    consumption_data = store.get_consumption_data(project_id, year=year)

    return {
        "status": "success",
        "project_id": project_id,
        "project_name": project.name,
        "filter_year": year,
        "energy_data": [e.model_dump(mode="json") for e in energy_data],
        "consumption_data": [c.model_dump(mode="json") for c in consumption_data],
        "summary": {
            "energy_records": len(energy_data),
            "consumption_records": len(consumption_data),
            "years_with_data": sorted({e.year for e in energy_data}, reverse=True),
        },
    }


# =============================================================================
# Gap Analysis Tools
# =============================================================================


@traced_tool("check_data_completeness")
def check_data_completeness(
    project_id: str = Field(..., description="The project's unique identifier"),
    analysis_type: str | None = Field(
        default=None,
        description="Specific analysis to check requirements for: energy_intensity, carbon_footprint, eu_taxonomy, crrem, gresb. If not provided, checks general ESG readiness.",
    ),
) -> dict[str, Any]:
    """Check data completeness for a building project.

    Analyzes what data is available and identifies gaps that need to be
    filled for a complete ESG assessment. When an analysis_type is specified,
    returns requirements specific to that analysis.

    Args:
        project_id: The project's unique identifier
        analysis_type: Optional specific analysis type to check requirements for

    Returns:
        DataCompletenessResult with completeness score and missing data details.

    Example:
        >>> # General completeness check
        >>> check_data_completeness(project_id="abc-123")

        >>> # Check if ready for EU Taxonomy analysis
        >>> check_data_completeness(project_id="abc-123", analysis_type="eu_taxonomy")
    """
    store = get_store()

    project = store.get_project(project_id)
    if project is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    energy_data = store.get_energy_data(project_id)
    consumption_data = store.get_consumption_data(project_id)

    current_year = datetime.now(UTC).year
    energy_years = sorted({e.year for e in energy_data}, reverse=True)

    # Build availability map for all possible data points
    data_availability = _check_data_availability(
        project, energy_data, consumption_data, current_year
    )

    # Get requirements based on analysis type
    if analysis_type:
        try:
            analysis = AnalysisType(analysis_type.lower())
            requirements = ANALYSIS_REQUIREMENTS[analysis]
        except (ValueError, KeyError):
            valid_types = [t.value for t in AnalysisType]
            return {
                "status": "invalid_analysis_type",
                "error": f"Unknown analysis type: {analysis_type}",
                "valid_types": valid_types,
            }
    else:
        # Default: general ESG readiness (energy_intensity as baseline)
        analysis = None
        requirements = ANALYSIS_REQUIREMENTS[AnalysisType.ENERGY_INTENSITY]

    # Check requirements against availability
    missing_required = []
    missing_recommended = []
    suggestions = []

    for req in requirements.required:
        if not data_availability.get(req, False):
            missing_required.append(req)
            suggestion = _get_suggestion_for_requirement(req)
            if suggestion:
                suggestions.append(suggestion)

    for req in requirements.recommended:
        if not data_availability.get(req, False):
            missing_recommended.append(req)

    # Check data quality issues
    data_quality_issues = _check_data_quality(energy_data)

    # Calculate completeness score
    required_count = len(requirements.required)
    required_met = required_count - len(missing_required)
    recommended_count = len(requirements.recommended)
    recommended_met = recommended_count - len(missing_recommended)

    # Required worth 70%, recommended worth 30%
    required_score = required_met / required_count * 70 if required_count > 0 else 70.0

    if recommended_count > 0:
        recommended_score = (recommended_met / recommended_count) * 30
    else:
        recommended_score = 30.0

    completeness_score = round(required_score + recommended_score, 1)
    ready_for_analysis = len(missing_required) == 0

    result = DataCompletenessResult(
        project_id=project_id,
        project_name=project.name,
        analysis_type=analysis.value if analysis else None,
        completeness_score=completeness_score,
        ready_for_analysis=ready_for_analysis,
        has_basic_info=data_availability.get("floor_area", False),
        has_energy_data=data_availability.get("energy_data", False),
        has_recent_energy_data=data_availability.get("recent_energy_data", False),
        energy_years_available=energy_years,
        missing_required=missing_required,
        missing_recommended=missing_recommended,
        data_quality_issues=data_quality_issues,
        suggestions=suggestions,
    )

    response = {
        "status": "success",
        "result": result.model_dump(),
        "ready_for_analysis": ready_for_analysis,
    }

    if analysis:
        response["analysis_description"] = requirements.description

    return response


def _check_data_availability(
    project: Any,
    energy_data: list,
    consumption_data: list,
    current_year: int,
) -> dict[str, bool]:
    """Build a map of what data is available for the project."""
    energy_years = {e.year for e in energy_data}

    return {
        # Basic building info
        "floor_area": project.floor_area_sqm is not None and project.floor_area_sqm > 0,
        "building_type": project.building_type is not None,
        "location": bool(project.city) or bool(project.address),
        "address": bool(project.address),
        "city": bool(project.city),
        # Energy data
        "energy_data": len(energy_data) > 0,
        "recent_energy_data": any(y >= current_year - 2 for y in energy_years),
        "multi_year_energy_data": len(energy_years) >= 2,
        # Certifications and ratings
        "epc_rating": bool(project.epc_rating),
        "certifications": False,  # Not yet implemented
        # Consumption data
        "water_data": any(
            c.category == ConsumptionCategory.WATER for c in consumption_data
        ),
        "waste_data": any(
            c.category
            in (ConsumptionCategory.WASTE_TOTAL, ConsumptionCategory.WASTE_RECYCLED)
            for c in consumption_data
        ),
        # Future requirements (placeholders)
        "target_pathway": False,  # CRREM
        "tenant_engagement": False,  # GRESB
        "renewable_energy": False,  # GRESB
        "renovation_year": project.renovation_year is not None,
    }


def _get_suggestion_for_requirement(requirement: str) -> str | None:
    """Get a helpful suggestion for how to fulfill a requirement."""
    suggestions = {
        "floor_area": "Update project with floor_area_sqm using update_building_project()",
        "energy_data": "Add energy consumption data using add_energy_data()",
        "recent_energy_data": "Add energy data for the last 2 years using add_energy_data()",
        "multi_year_energy_data": "Add energy data for at least 2 different years for trend analysis",
        "building_type": "Specify building type when creating or updating the project",
        "location": "Add city or address to the building project",
        "epc_rating": "Add EPC rating (A-G) using update_building_project(epc_rating='C')",
        "water_data": "Add water consumption using add_consumption_data(category='water')",
        "waste_data": "Add waste data using add_consumption_data(category='waste_total')",
    }
    return suggestions.get(requirement)


def _check_data_quality(energy_data: list) -> list[str]:
    """Check for data quality issues in energy data."""
    issues = []

    estimated_count = sum(1 for e in energy_data if e.is_estimated)
    if estimated_count > 0:
        issues.append(
            f"{estimated_count} energy record(s) are estimates - consider replacing with actual data"
        )

    # Check for suspiciously high or low values (simple outlier detection)
    if energy_data:
        values = [e.consumption_kwh for e in energy_data]
        if len(values) > 1:
            avg = sum(values) / len(values)
            for energy_record in energy_data:
                if energy_record.consumption_kwh > avg * 3:
                    issues.append(
                        f"Unusually high consumption in {energy_record.year} "
                        f"({energy_record.energy_type.value}): {energy_record.consumption_kwh:,.0f} kWh"
                    )

    return issues


@traced_tool("suggest_data_sources")
def suggest_data_sources(
    project_id: str = Field(..., description="The project's unique identifier"),
) -> dict[str, Any]:
    """Suggest data sources for collecting missing information.

    Based on the project's current data gaps, suggests specific documents
    and sources that should be collected.

    Returns:
        List of suggested documents and data sources to collect.
    """
    store = get_store()

    project = store.get_project(project_id)
    if project is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    energy_data = store.get_energy_data(project_id)
    consumption_data = store.get_consumption_data(project_id)

    suggestions = []
    priority_documents = []
    optional_documents = []

    # Always useful documents
    priority_documents.extend(
        [
            {
                "document": "Utility Bills (Nebenkostenabrechnung)",
                "data_provides": ["Electricity", "Gas", "Water", "District heating"],
                "typical_source": "Property manager / Hausverwaltung",
            },
        ]
    )

    # Energy data suggestions
    if not energy_data:
        priority_documents.append(
            {
                "document": "Energy Performance Certificate (Energieausweis)",
                "data_provides": [
                    "Primary energy demand",
                    "Energy rating",
                    "Building envelope data",
                ],
                "typical_source": "Building owner or previous energy assessor",
            }
        )
        suggestions.append("Request utility bills from the last 2-3 years")

    # Check for tenant electricity (scope 3)
    has_tenant_electricity = any(
        c.category.value == "tenant_electricity" for c in consumption_data
    )
    if not has_tenant_electricity:
        optional_documents.append(
            {
                "document": "Tenant Electricity Bills",
                "data_provides": ["Tenant electricity consumption (Scope 3)"],
                "typical_source": "Request from tenants or estimate based on floor area",
                "note": "Often difficult to obtain - estimation methods available",
            }
        )

    # EPC suggestion
    if not project.epc_rating:
        priority_documents.append(
            {
                "document": "Energy Performance Certificate (Energieausweis)",
                "data_provides": ["EPC rating", "Primary energy demand"],
                "typical_source": "Required by law for sales/rentals - should exist",
            }
        )

    # Additional useful documents
    optional_documents.extend(
        [
            {
                "document": "Building Management System (BMS) Reports",
                "data_provides": ["Detailed consumption patterns", "HVAC efficiency"],
                "typical_source": "Facility manager",
            },
            {
                "document": "Waste Management Contract",
                "data_provides": ["Waste volumes", "Recycling rates"],
                "typical_source": "Waste disposal provider",
            },
            {
                "document": "Building Plans / Technical Documentation",
                "data_provides": [
                    "Floor areas",
                    "Building systems",
                    "Insulation details",
                ],
                "typical_source": "Building archive or property manager",
            },
        ]
    )

    return {
        "status": "success",
        "project_id": project_id,
        "project_name": project.name,
        "priority_documents": priority_documents,
        "optional_documents": optional_documents,
        "data_collection_tips": [
            "Start with utility bills - they provide the most important data",
            "Energy Performance Certificate (Energieausweis) is legally required and should exist",
            "Tenant consumption data can be estimated if not available",
            "Ask property manager (Hausverwaltung) for consolidated data",
        ],
    }


# =============================================================================
# ESG Analysis Tools
# =============================================================================


@traced_tool("calculate_energy_intensity")
def calculate_energy_intensity(
    project_id: str = Field(..., description="The project's unique identifier"),
    year: int | None = Field(
        default=None, description="Year to analyze (default: most recent)"
    ),
) -> dict[str, Any]:
    """Calculate energy intensity (kWh/m²/a) for a building.

    Calculates both final energy intensity and primary energy intensity
    using German primary energy factors (GEG 2024).

    Returns:
        EnergyIntensityResult with intensity values and energy rating.
    """
    store = get_store()

    project = store.get_project(project_id)
    if project is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    energy_data = store.get_energy_data(project_id)

    if not energy_data:
        return {
            "status": "no_data",
            "error": "No energy data available for this project",
            "suggestion": "Add energy data using add_energy_data()",
        }

    # Determine year to analyze
    available_years = sorted({e.year for e in energy_data}, reverse=True)
    analysis_year = year if year and year in available_years else available_years[0]

    # Filter to selected year
    year_data = [e for e in energy_data if e.year == analysis_year]

    # Calculate totals by energy type
    energy_breakdown = {}
    total_energy_kwh = 0.0
    total_primary_energy_kwh = 0.0
    has_estimates = False

    for record in year_data:
        energy_type = record.energy_type
        kwh = record.consumption_kwh
        energy_breakdown[energy_type.value] = (
            energy_breakdown.get(energy_type.value, 0) + kwh
        )
        total_energy_kwh += kwh

        # Apply primary energy factor
        pef = PRIMARY_ENERGY_FACTORS.get(energy_type, 1.0)
        total_primary_energy_kwh += kwh * pef

        if record.is_estimated:
            has_estimates = True

    # Calculate intensities
    floor_area = project.floor_area_sqm
    energy_intensity = total_energy_kwh / floor_area
    primary_energy_intensity = total_primary_energy_kwh / floor_area

    # Calculate weighted primary energy factor
    weighted_pef = (
        primary_energy_intensity / energy_intensity if energy_intensity > 0 else 1.0
    )

    # Determine energy rating
    rating = "G"
    for grade, threshold in ENERGY_RATING_THRESHOLDS.items():
        if energy_intensity < threshold:
            rating = grade
            break

    # Determine data quality
    if not has_estimates:
        data_quality = "measured"
    elif all(e.is_estimated for e in year_data):
        data_quality = "estimated"
    else:
        data_quality = "partially_estimated"

    result = EnergyIntensityResult(
        project_id=project_id,
        project_name=project.name,
        year=analysis_year,
        floor_area_sqm=floor_area,
        total_energy_kwh=round(total_energy_kwh, 2),
        energy_intensity_kwh_sqm=round(energy_intensity, 2),
        energy_breakdown=energy_breakdown,
        primary_energy_factor=round(weighted_pef, 2),
        primary_energy_intensity_kwh_sqm=round(primary_energy_intensity, 2),
        rating=rating,
        data_quality=data_quality,
    )

    return {
        "status": "success",
        "result": result.model_dump(),
        "interpretation": f"Energy intensity of {energy_intensity:.1f} kWh/m²/a corresponds to rating {rating}",
    }


@traced_tool("calculate_carbon_footprint")
def calculate_carbon_footprint(
    project_id: str = Field(..., description="The project's unique identifier"),
    year: int | None = Field(
        default=None, description="Year to analyze (default: most recent)"
    ),
) -> dict[str, Any]:
    """Calculate carbon footprint (kgCO2/m²/a) for a building.

    Uses German grid emission factors (Umweltbundesamt 2023) to calculate
    operational carbon emissions from energy consumption.

    Returns:
        CarbonFootprintResult with emissions breakdown by energy type.
    """
    store = get_store()

    project = store.get_project(project_id)
    if project is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    energy_data = store.get_energy_data(project_id)

    if not energy_data:
        return {
            "status": "no_data",
            "error": "No energy data available for this project",
            "suggestion": "Add energy data using add_energy_data()",
        }

    # Determine year to analyze
    available_years = sorted({e.year for e in energy_data}, reverse=True)
    analysis_year = year if year and year in available_years else available_years[0]

    # Filter to selected year
    year_data = [e for e in energy_data if e.year == analysis_year]

    # Calculate emissions by energy type
    emissions_breakdown = {}
    emission_factors_used = {}
    total_emissions_kg = 0.0
    has_estimates = False

    for record in year_data:
        energy_type = record.energy_type
        kwh = record.consumption_kwh

        # Get emission factor (gCO2/kWh) and convert to kgCO2
        ef = EMISSION_FACTORS.get(energy_type, 250.0)
        emissions_kg = kwh * ef / 1000  # Convert g to kg

        emissions_breakdown[energy_type.value] = (
            emissions_breakdown.get(energy_type.value, 0) + emissions_kg
        )
        emission_factors_used[energy_type.value] = ef
        total_emissions_kg += emissions_kg

        if record.is_estimated:
            has_estimates = True

    # Calculate intensity
    floor_area = project.floor_area_sqm
    carbon_intensity = total_emissions_kg / floor_area

    # Determine data quality
    if not has_estimates:
        data_quality = "measured"
    elif all(e.is_estimated for e in year_data):
        data_quality = "estimated"
    else:
        data_quality = "partially_estimated"

    result = CarbonFootprintResult(
        project_id=project_id,
        project_name=project.name,
        year=analysis_year,
        floor_area_sqm=floor_area,
        total_emissions_kg_co2=round(total_emissions_kg, 2),
        carbon_intensity_kg_co2_sqm=round(carbon_intensity, 2),
        emissions_breakdown={k: round(v, 2) for k, v in emissions_breakdown.items()},
        emission_factors_used=emission_factors_used,
        data_quality=data_quality,
    )

    return {
        "status": "success",
        "result": result.model_dump(),
        "interpretation": f"Carbon intensity of {carbon_intensity:.1f} kgCO2/m²/a ({total_emissions_kg:,.0f} kgCO2 total)",
        "notes": [
            "Emission factors: German grid mix 2023 (Umweltbundesamt)",
            "Scope: Operational emissions only (Scope 1 + Scope 2)",
        ],
    }


@traced_tool("check_eu_taxonomy_alignment")
def check_eu_taxonomy_alignment(
    project_id: str = Field(..., description="The project's unique identifier"),
    year: int | None = Field(
        default=None, description="Year to analyze (default: most recent)"
    ),
) -> dict[str, Any]:
    """Check EU Taxonomy alignment for a building.

    Evaluates whether the building meets EU Taxonomy criteria for
    "Climate Change Mitigation" under Activity 7.7 (Acquisition and
    ownership of buildings).

    Alignment pathways:
    1. EPC Class A
    2. Top 15% of national building stock (not implemented yet)
    3. Primary energy demand < threshold for building type

    Returns:
        EUTaxonomyResult with alignment status and recommendations.
    """
    store = get_store()

    project = store.get_project(project_id)
    if project is None:
        return {
            "status": "not_found",
            "error": f"Project with ID '{project_id}' not found",
        }

    # First calculate energy intensity
    intensity_result = calculate_energy_intensity(project_id, year)

    if intensity_result.get("status") != "success":
        return intensity_result

    intensity_data = intensity_result["result"]
    primary_energy_intensity = intensity_data["primary_energy_intensity_kwh_sqm"]
    analysis_year = intensity_data["year"]

    # Get threshold for building type
    threshold = EU_TAXONOMY_THRESHOLDS.get(project.building_type, 100.0)

    # Check alignment pathways
    is_aligned = False
    alignment_pathway = None
    recommendations = []
    data_quality_notes = []

    # Pathway 1: EPC Class A
    epc_aligned = None
    if project.epc_rating:
        epc_aligned = project.epc_rating.upper() in ["A+", "A"]
        if epc_aligned:
            is_aligned = True
            alignment_pathway = "epc_class_a"
    else:
        recommendations.append(
            "Add EPC rating - Class A buildings are automatically taxonomy-aligned"
        )

    # Pathway 3: Primary energy threshold
    if primary_energy_intensity < threshold:
        is_aligned = True
        if not alignment_pathway:
            alignment_pathway = "primary_energy_threshold"
    else:
        gap = primary_energy_intensity - threshold
        recommendations.append(
            f"Reduce primary energy demand by {gap:.1f} kWh/m²/a to meet threshold"
        )
        recommendations.append(
            "Consider energy efficiency measures: LED lighting, HVAC optimization, building envelope improvements"
        )

    # Calculate gap
    gap_kwh = primary_energy_intensity - threshold
    gap_percentage = (gap_kwh / threshold) * 100 if threshold > 0 else 0

    # Data quality notes
    if intensity_data["data_quality"] != "measured":
        data_quality_notes.append(
            f"Data quality: {intensity_data['data_quality']} - actual measurements may differ"
        )

    result = EUTaxonomyResult(
        project_id=project_id,
        project_name=project.name,
        building_type=project.building_type.value,
        year=analysis_year,
        is_aligned=is_aligned,
        alignment_pathway=alignment_pathway,
        primary_energy_intensity_kwh_sqm=primary_energy_intensity,
        threshold_kwh_sqm=threshold,
        gap_kwh_sqm=round(gap_kwh, 2),
        gap_percentage=round(gap_percentage, 1),
        epc_rating=project.epc_rating,
        epc_aligned=epc_aligned,
        dnsh_criteria_met=None,  # Not assessed yet
        recommendations=recommendations,
        data_quality_notes=data_quality_notes,
    )

    return {
        "status": "success",
        "result": result.model_dump(),
        "interpretation": (
            f"Building is {'✅ ALIGNED' if is_aligned else '❌ NOT ALIGNED'} "
            f"with EU Taxonomy (Activity 7.7)"
        ),
        "regulatory_notes": [
            "EU Taxonomy Regulation 2020/852",
            "Climate Delegated Act, Annex I, Section 7.7",
            "DNSH criteria not assessed in this version",
        ],
    }

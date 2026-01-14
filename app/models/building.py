"""Pydantic data models for building projects and ESG data.

This module defines the core data structures for ESG assessment of existing
commercial buildings (Bestandsgebäude), including building projects, energy
data, and consumption metrics.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, NamedTuple
from uuid import uuid4

from pydantic import BaseModel, Field


class BuildingType(str, Enum):
    """Building usage type classification."""

    OFFICE = "office"
    RESIDENTIAL = "residential"
    RETAIL = "retail"
    MIXED = "mixed"
    INDUSTRIAL = "industrial"
    HOTEL = "hotel"
    LOGISTICS = "logistics"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"


class EnergyType(str, Enum):
    """Energy source type for consumption tracking."""

    ELECTRICITY = "electricity"
    GAS = "gas"
    DISTRICT_HEATING = "district_heating"
    DISTRICT_COOLING = "district_cooling"
    OIL = "oil"
    BIOMASS = "biomass"
    SOLAR_THERMAL = "solar_thermal"
    OTHER = "other"


class DataSource(str, Enum):
    """Source of data for quality tracking."""

    UTILITY_BILL = "utility_bill"
    SMART_METER = "smart_meter"
    ESTIMATE = "estimate"
    BENCHMARK = "benchmark"
    ENERGY_AUDIT = "energy_audit"
    BUILDING_MANAGEMENT_SYSTEM = "bms"
    TENANT_REPORT = "tenant_report"
    OTHER = "other"


class ConsumptionCategory(str, Enum):
    """Categories of non-energy consumption."""

    WATER = "water"
    WASTE_TOTAL = "waste_total"
    WASTE_RECYCLED = "waste_recycled"
    TENANT_ELECTRICITY = "tenant_electricity"
    COMMON_AREA_ELECTRICITY = "common_area_electricity"


class AnalysisType(str, Enum):
    """Types of ESG analysis with different data requirements."""

    ENERGY_INTENSITY = "energy_intensity"
    CARBON_FOOTPRINT = "carbon_footprint"
    EU_TAXONOMY = "eu_taxonomy"
    # Future analysis types
    CRREM = "crrem"
    GRESB = "gresb"


class AnalysisRequirements(NamedTuple):
    """Data requirements for a specific analysis type."""

    required: tuple[str, ...]
    recommended: tuple[str, ...]
    description: str


# Analysis-specific data requirements
# Each key maps to what data is needed for that analysis
ANALYSIS_REQUIREMENTS: dict[AnalysisType, AnalysisRequirements] = {
    AnalysisType.ENERGY_INTENSITY: AnalysisRequirements(
        required=("floor_area", "energy_data"),
        recommended=("recent_energy_data",),
        description="Calculate energy consumption per square meter (kWh/m²/a)",
    ),
    AnalysisType.CARBON_FOOTPRINT: AnalysisRequirements(
        required=("floor_area", "energy_data"),
        recommended=("recent_energy_data",),
        description="Calculate carbon emissions per square meter (kgCO₂/m²/a)",
    ),
    AnalysisType.EU_TAXONOMY: AnalysisRequirements(
        required=("floor_area", "energy_data", "building_type"),
        recommended=("epc_rating", "recent_energy_data"),
        description="Check EU Taxonomy Activity 7.7 alignment for building acquisition",
    ),
    AnalysisType.CRREM: AnalysisRequirements(
        required=(
            "floor_area",
            "energy_data",
            "building_type",
            "location",
            "multi_year_energy_data",
        ),
        recommended=("renovation_year", "target_pathway"),
        description="Carbon Risk Real Estate Monitor pathway analysis",
    ),
    AnalysisType.GRESB: AnalysisRequirements(
        required=(
            "floor_area",
            "energy_data",
            "water_data",
            "waste_data",
            "building_type",
        ),
        recommended=(
            "certifications",
            "tenant_engagement",
            "renewable_energy",
        ),
        description="Global Real Estate Sustainability Benchmark assessment",
    ),
}


# =============================================================================
# Core Models
# =============================================================================


class BuildingProject(BaseModel):
    """A building project for ESG assessment.

    Represents an existing building (Bestandsgebäude) being assessed for
    sustainability performance, EU Taxonomy alignment, and improvement planning.
    """

    project_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the project",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name or identifier for the building",
    )
    address: str = Field(
        default="",
        max_length=500,
        description="Full address of the building",
    )
    city: str = Field(
        default="",
        max_length=100,
        description="City where the building is located",
    )
    country: str = Field(
        default="DE",
        max_length=2,
        description="ISO 3166-1 alpha-2 country code (default: DE for Germany)",
    )
    building_type: BuildingType = Field(
        default=BuildingType.OFFICE,
        description="Primary usage type of the building",
    )
    floor_area_sqm: float = Field(
        ...,
        gt=0,
        description="Net floor area in square meters (NRF/NGF)",
    )
    gross_floor_area_sqm: float | None = Field(
        default=None,
        gt=0,
        description="Gross floor area in square meters (BGF), if known",
    )
    construction_year: int = Field(
        ...,
        ge=1800,
        le=2030,
        description="Year the building was originally constructed",
    )
    renovation_year: int | None = Field(
        default=None,
        ge=1800,
        le=2030,
        description="Year of last major renovation, if any",
    )
    number_of_floors: int | None = Field(
        default=None,
        ge=1,
        le=200,
        description="Total number of floors (above and below ground)",
    )
    number_of_tenants: int | None = Field(
        default=None,
        ge=0,
        description="Number of tenants in the building",
    )
    occupancy_rate: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Current occupancy rate as percentage (0-100)",
    )
    epc_rating: str | None = Field(
        default=None,
        max_length=10,
        description="Energy Performance Certificate rating (e.g., 'A', 'B', 'C')",
    )
    notes: str = Field(
        default="",
        max_length=2000,
        description="Additional notes about the building",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the project was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the project was last updated",
    )


class BuildingProjectCreate(BaseModel):
    """Input model for creating a new building project."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name or identifier for the building",
    )
    address: str = Field(
        default="",
        max_length=500,
        description="Full address of the building",
    )
    city: str = Field(
        default="",
        max_length=100,
        description="City where the building is located",
    )
    country: str = Field(
        default="DE",
        max_length=2,
        description="ISO 3166-1 alpha-2 country code",
    )
    building_type: BuildingType = Field(
        default=BuildingType.OFFICE,
        description="Primary usage type of the building",
    )
    floor_area_sqm: float = Field(
        ...,
        gt=0,
        description="Net floor area in square meters (NRF/NGF)",
    )
    gross_floor_area_sqm: float | None = Field(
        default=None,
        gt=0,
        description="Gross floor area in square meters (BGF)",
    )
    construction_year: int = Field(
        ...,
        ge=1800,
        le=2030,
        description="Year the building was originally constructed",
    )
    renovation_year: int | None = Field(
        default=None,
        ge=1800,
        le=2030,
        description="Year of last major renovation",
    )
    number_of_floors: int | None = Field(
        default=None,
        ge=1,
        le=200,
        description="Total number of floors",
    )
    number_of_tenants: int | None = Field(
        default=None,
        ge=0,
        description="Number of tenants",
    )
    occupancy_rate: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Current occupancy rate as percentage",
    )
    epc_rating: str | None = Field(
        default=None,
        max_length=10,
        description="Energy Performance Certificate rating",
    )
    notes: str = Field(
        default="",
        max_length=2000,
        description="Additional notes",
    )


class BuildingProjectUpdate(BaseModel):
    """Input model for updating a building project (all fields optional)."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    address: str | None = Field(
        default=None,
        max_length=500,
    )
    city: str | None = Field(
        default=None,
        max_length=100,
    )
    country: str | None = Field(
        default=None,
        max_length=2,
    )
    building_type: BuildingType | None = None
    floor_area_sqm: float | None = Field(
        default=None,
        gt=0,
    )
    gross_floor_area_sqm: float | None = Field(
        default=None,
        gt=0,
    )
    construction_year: int | None = Field(
        default=None,
        ge=1800,
        le=2030,
    )
    renovation_year: int | None = Field(
        default=None,
        ge=1800,
        le=2030,
    )
    number_of_floors: int | None = Field(
        default=None,
        ge=1,
        le=200,
    )
    number_of_tenants: int | None = Field(
        default=None,
        ge=0,
    )
    occupancy_rate: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    epc_rating: str | None = Field(
        default=None,
        max_length=10,
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


# =============================================================================
# Energy and Consumption Data
# =============================================================================


class EnergyData(BaseModel):
    """Annual energy consumption data for a building.

    Tracks energy consumption by type (electricity, gas, etc.) for a specific year.
    Multiple records per year are allowed for different energy types.
    """

    energy_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this energy record",
    )
    project_id: str = Field(
        ...,
        description="Reference to the building project",
    )
    year: int = Field(
        ...,
        ge=2000,
        le=2030,
        description="Year of consumption data",
    )
    energy_type: EnergyType = Field(
        ...,
        description="Type of energy (electricity, gas, etc.)",
    )
    consumption_kwh: float = Field(
        ...,
        ge=0,
        description="Annual consumption in kWh",
    )
    source: DataSource = Field(
        default=DataSource.UTILITY_BILL,
        description="Source of the data for quality tracking",
    )
    is_estimated: bool = Field(
        default=False,
        description="Whether this value is an estimate",
    )
    notes: str = Field(
        default="",
        max_length=500,
        description="Additional notes about this data point",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the record was created",
    )


class EnergyDataCreate(BaseModel):
    """Input model for adding energy data."""

    year: int = Field(
        ...,
        ge=2000,
        le=2030,
        description="Year of consumption data",
    )
    energy_type: EnergyType = Field(
        ...,
        description="Type of energy",
    )
    consumption_kwh: float = Field(
        ...,
        ge=0,
        description="Annual consumption in kWh",
    )
    source: DataSource = Field(
        default=DataSource.UTILITY_BILL,
        description="Source of the data",
    )
    is_estimated: bool = Field(
        default=False,
        description="Whether this value is an estimate",
    )
    notes: str = Field(
        default="",
        max_length=500,
        description="Additional notes",
    )


class ConsumptionData(BaseModel):
    """Non-energy consumption data for a building.

    Tracks water usage, waste generation, and other environmental metrics.
    """

    consumption_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this consumption record",
    )
    project_id: str = Field(
        ...,
        description="Reference to the building project",
    )
    year: int = Field(
        ...,
        ge=2000,
        le=2030,
        description="Year of consumption data",
    )
    category: ConsumptionCategory = Field(
        ...,
        description="Category of consumption (water, waste, etc.)",
    )
    value: float = Field(
        ...,
        ge=0,
        description="Consumption value",
    )
    unit: str = Field(
        ...,
        max_length=20,
        description="Unit of measurement (e.g., 'm3', 'kg', 'kWh')",
    )
    source: DataSource = Field(
        default=DataSource.UTILITY_BILL,
        description="Source of the data",
    )
    is_estimated: bool = Field(
        default=False,
        description="Whether this value is an estimate",
    )
    notes: str = Field(
        default="",
        max_length=500,
        description="Additional notes",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the record was created",
    )


class ConsumptionDataCreate(BaseModel):
    """Input model for adding consumption data."""

    year: int = Field(
        ...,
        ge=2000,
        le=2030,
        description="Year of consumption data",
    )
    category: ConsumptionCategory = Field(
        ...,
        description="Category of consumption",
    )
    value: float = Field(
        ...,
        ge=0,
        description="Consumption value",
    )
    unit: str = Field(
        ...,
        max_length=20,
        description="Unit of measurement",
    )
    source: DataSource = Field(
        default=DataSource.UTILITY_BILL,
        description="Source of the data",
    )
    is_estimated: bool = Field(
        default=False,
        description="Whether this value is an estimate",
    )
    notes: str = Field(
        default="",
        max_length=500,
        description="Additional notes",
    )


# =============================================================================
# Analysis Results
# =============================================================================


class DataCompletenessResult(BaseModel):
    """Result of checking data completeness for a building project."""

    project_id: str
    project_name: str
    analysis_type: str | None = Field(
        default=None,
        description="Specific analysis type checked, or None for general completeness",
    )
    completeness_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall completeness as percentage (0-100)",
    )
    ready_for_analysis: bool = Field(
        default=False,
        description="Whether all required data is present for the analysis",
    )
    has_basic_info: bool
    has_energy_data: bool
    has_recent_energy_data: bool = Field(
        ...,
        description="Has energy data for the last 2 years",
    )
    energy_years_available: list[int] = Field(
        default_factory=list,
        description="Years with energy data",
    )
    missing_required: list[str] = Field(
        default_factory=list,
        description="List of missing required data fields",
    )
    missing_recommended: list[str] = Field(
        default_factory=list,
        description="List of missing recommended data fields",
    )
    data_quality_issues: list[str] = Field(
        default_factory=list,
        description="List of data quality concerns",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for improving data completeness",
    )


class EnergyIntensityResult(BaseModel):
    """Result of calculating energy intensity (kWh/m²/a)."""

    project_id: str
    project_name: str
    year: int
    floor_area_sqm: float
    total_energy_kwh: float
    energy_intensity_kwh_sqm: float = Field(
        ...,
        description="Energy intensity in kWh/m²/a",
    )
    energy_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Energy by type in kWh",
    )
    primary_energy_factor: float = Field(
        default=1.0,
        description="Weighted primary energy factor",
    )
    primary_energy_intensity_kwh_sqm: float = Field(
        ...,
        description="Primary energy intensity in kWh/m²/a",
    )
    rating: str = Field(
        ...,
        description="Energy rating (A+ to G)",
    )
    data_quality: Literal["measured", "partially_estimated", "estimated"]


class CarbonFootprintResult(BaseModel):
    """Result of calculating carbon footprint (kgCO2/m²/a)."""

    project_id: str
    project_name: str
    year: int
    floor_area_sqm: float
    total_emissions_kg_co2: float = Field(
        ...,
        description="Total CO2 emissions in kg",
    )
    carbon_intensity_kg_co2_sqm: float = Field(
        ...,
        description="Carbon intensity in kgCO2/m²/a",
    )
    emissions_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Emissions by energy type in kgCO2",
    )
    emission_factors_used: dict[str, float] = Field(
        default_factory=dict,
        description="Emission factors used (gCO2/kWh) by energy type",
    )
    data_quality: Literal["measured", "partially_estimated", "estimated"]


class EUTaxonomyResult(BaseModel):
    """Result of EU Taxonomy alignment check."""

    project_id: str
    project_name: str
    building_type: str
    year: int
    is_aligned: bool = Field(
        ...,
        description="Whether the building meets EU Taxonomy criteria",
    )
    alignment_pathway: str | None = Field(
        default=None,
        description="Which criterion was used (EPC, top_15_percent, primary_energy)",
    )
    primary_energy_intensity_kwh_sqm: float
    threshold_kwh_sqm: float = Field(
        ...,
        description="EU Taxonomy threshold for this building type",
    )
    gap_kwh_sqm: float = Field(
        ...,
        description="Gap to threshold (negative = below threshold = good)",
    )
    gap_percentage: float = Field(
        ...,
        description="Gap as percentage of threshold",
    )
    epc_rating: str | None = None
    epc_aligned: bool | None = None
    dnsh_criteria_met: bool | None = Field(
        default=None,
        description="Do No Significant Harm criteria assessment",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for achieving alignment",
    )
    data_quality_notes: list[str] = Field(
        default_factory=list,
        description="Notes about data quality affecting the assessment",
    )

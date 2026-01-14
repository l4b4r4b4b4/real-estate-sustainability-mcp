"""Tests for ESG assessment tools.

This module tests the ESG tools for building projects including:
- Project CRUD operations
- Energy and consumption data collection
- Data completeness checking with analysis-specific requirements
- Energy intensity and carbon footprint calculations
- EU Taxonomy alignment checking

Note: Since ESG tools use @traced_tool decorator and Field() defaults,
we test using the store directly and via helper wrappers.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import ValidationError

from app.models import (
    ANALYSIS_REQUIREMENTS,
    AnalysisType,
    BuildingProjectCreate,
    BuildingType,
    ConsumptionCategory,
    ConsumptionDataCreate,
    DataSource,
    EnergyDataCreate,
    EnergyType,
)
from app.store import get_store

if TYPE_CHECKING:
    from app.store.database import BuildingStore

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def store() -> BuildingStore:
    """Provide the building store."""
    return get_store()


@pytest.fixture
def clean_store(store: BuildingStore) -> BuildingStore:
    """Provide a clean store for each test."""
    # Get all projects and delete them
    projects = store.list_projects(limit=1000)
    for project in projects:
        store.delete_project(project.project_id)
    yield store
    # Cleanup after test
    projects = store.list_projects(limit=1000)
    for project in projects:
        store.delete_project(project.project_id)


@pytest.fixture
def sample_project(clean_store: BuildingStore):
    """Create a sample building project for testing."""
    project_data = BuildingProjectCreate(
        name="Test Building",
        floor_area_sqm=5000.0,
        construction_year=1990,
        building_type=BuildingType.OFFICE,
        address="Test Street 123",
        city="Berlin",
        country="DE",
        epc_rating="C",
    )
    return clean_store.create_project(project_data)


@pytest.fixture
def project_with_energy_data(sample_project, clean_store: BuildingStore):
    """Create a project with energy data."""
    project_id = sample_project.project_id

    # Add electricity data for 2023 and 2024
    clean_store.add_energy_data(
        project_id,
        EnergyDataCreate(
            year=2024,
            energy_type=EnergyType.ELECTRICITY,
            consumption_kwh=500000.0,
            source=DataSource.UTILITY_BILL,
        ),
    )
    clean_store.add_energy_data(
        project_id,
        EnergyDataCreate(
            year=2023,
            energy_type=EnergyType.ELECTRICITY,
            consumption_kwh=520000.0,
            source=DataSource.UTILITY_BILL,
        ),
    )

    # Add gas data
    clean_store.add_energy_data(
        project_id,
        EnergyDataCreate(
            year=2024,
            energy_type=EnergyType.GAS,
            consumption_kwh=200000.0,
            source=DataSource.UTILITY_BILL,
        ),
    )

    return sample_project


# =============================================================================
# Helper Functions for Tool Testing
# =============================================================================


def call_tool(tool_func, **kwargs) -> dict[str, Any]:
    """Call a tool function, handling the traced_tool wrapper."""
    # The traced_tool decorator wraps the function
    # We need to call it with keyword arguments
    fn = tool_func.fn if hasattr(tool_func, "fn") else tool_func
    return fn(**kwargs)


# =============================================================================
# Project Store Tests (Using Store Directly)
# =============================================================================


class TestBuildingStoreProject:
    """Tests for BuildingStore project operations."""

    def test_create_project_success(self, clean_store: BuildingStore):
        """Test successful project creation."""
        project_data = BuildingProjectCreate(
            name="Klöpperhaus",
            floor_area_sqm=15000.0,
            construction_year=1912,
            building_type=BuildingType.OFFICE,
            city="Hamburg",
        )
        project = clean_store.create_project(project_data)

        assert project.name == "Klöpperhaus"
        assert project.floor_area_sqm == 15000.0
        assert project.construction_year == 1912
        assert project.building_type == BuildingType.OFFICE
        assert project.city == "Hamburg"
        assert project.project_id is not None

    def test_create_project_with_all_fields(self, clean_store: BuildingStore):
        """Test project creation with all optional fields."""
        project_data = BuildingProjectCreate(
            name="Full Project",
            floor_area_sqm=10000.0,
            construction_year=1985,
            building_type=BuildingType.RETAIL,
            address="Main Street 1",
            city="Munich",
            country="DE",
            renovation_year=2020,
            epc_rating="B",
            notes="Test notes",
        )
        project = clean_store.create_project(project_data)

        assert project.renovation_year == 2020
        assert project.epc_rating == "B"
        assert project.notes == "Test notes"
        assert project.country == "DE"

    def test_get_project_success(self, sample_project, clean_store: BuildingStore):
        """Test successful project retrieval."""
        project = clean_store.get_project(sample_project.project_id)

        assert project is not None
        assert project.name == "Test Building"
        assert project.floor_area_sqm == 5000.0

    def test_get_project_not_found(self, clean_store: BuildingStore):
        """Test retrieval of non-existent project."""
        project = clean_store.get_project("nonexistent-id")
        assert project is None

    def test_list_projects_empty(self, clean_store: BuildingStore):
        """Test listing when no projects exist."""
        projects = clean_store.list_projects()
        assert projects == []

    def test_list_projects_with_data(self, clean_store: BuildingStore):
        """Test listing with multiple projects."""
        for i in range(3):
            project_data = BuildingProjectCreate(
                name=f"Project {i}",
                floor_area_sqm=1000.0 * (i + 1),
                construction_year=2000 + i,
            )
            clean_store.create_project(project_data)

        projects = clean_store.list_projects()
        assert len(projects) == 3

    def test_list_projects_pagination(self, clean_store: BuildingStore):
        """Test pagination of project listing."""
        for i in range(5):
            project_data = BuildingProjectCreate(
                name=f"Project {i}",
                floor_area_sqm=1000.0,
                construction_year=2000,
            )
            clean_store.create_project(project_data)

        # Get first 2
        projects = clean_store.list_projects(limit=2, offset=0)
        assert len(projects) == 2

        # Get next 2
        projects = clean_store.list_projects(limit=2, offset=2)
        assert len(projects) == 2

        # Get last 1
        projects = clean_store.list_projects(limit=2, offset=4)
        assert len(projects) == 1

    def test_delete_project_success(self, sample_project, clean_store: BuildingStore):
        """Test successful project deletion."""
        project_id = sample_project.project_id
        result = clean_store.delete_project(project_id)

        assert result is True

        # Verify it's gone
        project = clean_store.get_project(project_id)
        assert project is None

    def test_delete_project_not_found(self, clean_store: BuildingStore):
        """Test deleting non-existent project."""
        result = clean_store.delete_project("nonexistent-id")
        assert result is False


# =============================================================================
# Energy Data Tests
# =============================================================================


class TestBuildingStoreEnergyData:
    """Tests for BuildingStore energy data operations."""

    def test_add_energy_data_success(self, sample_project, clean_store: BuildingStore):
        """Test successful energy data addition."""
        project_id = sample_project.project_id
        energy_data = EnergyDataCreate(
            year=2024,
            energy_type=EnergyType.ELECTRICITY,
            consumption_kwh=500000.0,
            source=DataSource.UTILITY_BILL,
        )
        result = clean_store.add_energy_data(project_id, energy_data)

        assert result is not None
        assert result.consumption_kwh == 500000.0
        assert result.energy_type == EnergyType.ELECTRICITY
        assert result.year == 2024

    def test_add_energy_data_with_notes(
        self, sample_project, clean_store: BuildingStore
    ):
        """Test adding energy data with notes."""
        project_id = sample_project.project_id
        energy_data = EnergyDataCreate(
            year=2024,
            energy_type=EnergyType.GAS,
            consumption_kwh=100000.0,
            source=DataSource.SMART_METER,
            is_estimated=True,
            notes="Estimated based on partial data",
        )
        result = clean_store.add_energy_data(project_id, energy_data)

        assert result is not None
        assert result.is_estimated is True
        assert result.notes == "Estimated based on partial data"

    def test_add_energy_data_project_not_found(self, clean_store: BuildingStore):
        """Test adding energy data to non-existent project."""
        energy_data = EnergyDataCreate(
            year=2024,
            energy_type=EnergyType.ELECTRICITY,
            consumption_kwh=100000.0,
        )
        result = clean_store.add_energy_data("nonexistent-id", energy_data)
        assert result is None

    def test_get_energy_data(
        self, project_with_energy_data, clean_store: BuildingStore
    ):
        """Test getting energy data."""
        project_id = project_with_energy_data.project_id
        energy_data = clean_store.get_energy_data(project_id)

        assert len(energy_data) == 3  # 2 electricity + 1 gas

    def test_get_energy_data_by_year(
        self, project_with_energy_data, clean_store: BuildingStore
    ):
        """Test getting energy data filtered by year."""
        project_id = project_with_energy_data.project_id
        energy_data = clean_store.get_energy_data(project_id, year=2024)

        assert len(energy_data) == 2  # 1 electricity + 1 gas for 2024
        for record in energy_data:
            assert record.year == 2024


# =============================================================================
# Consumption Data Tests
# =============================================================================


class TestBuildingStoreConsumptionData:
    """Tests for BuildingStore consumption data operations."""

    def test_add_water_consumption(self, sample_project, clean_store: BuildingStore):
        """Test adding water consumption data."""
        project_id = sample_project.project_id
        consumption_data = ConsumptionDataCreate(
            year=2024,
            category=ConsumptionCategory.WATER,
            value=5000.0,
            unit="m3",
        )
        result = clean_store.add_consumption_data(project_id, consumption_data)

        assert result is not None
        assert result.category == ConsumptionCategory.WATER
        assert result.value == 5000.0
        assert result.unit == "m3"

    def test_add_waste_data(self, sample_project, clean_store: BuildingStore):
        """Test adding waste data."""
        project_id = sample_project.project_id
        consumption_data = ConsumptionDataCreate(
            year=2024,
            category=ConsumptionCategory.WASTE_TOTAL,
            value=25000.0,
            unit="kg",
        )
        result = clean_store.add_consumption_data(project_id, consumption_data)

        assert result is not None
        assert result.category == ConsumptionCategory.WASTE_TOTAL

    def test_add_consumption_data_project_not_found(self, clean_store: BuildingStore):
        """Test adding consumption data to non-existent project."""
        consumption_data = ConsumptionDataCreate(
            year=2024,
            category=ConsumptionCategory.WATER,
            value=1000.0,
            unit="m3",
        )
        result = clean_store.add_consumption_data("nonexistent-id", consumption_data)
        assert result is None


# =============================================================================
# Analysis Requirements Tests
# =============================================================================


class TestAnalysisRequirements:
    """Tests for analysis requirements configuration."""

    def test_all_analysis_types_have_requirements(self):
        """Test that all analysis types have defined requirements."""
        for analysis_type in AnalysisType:
            assert analysis_type in ANALYSIS_REQUIREMENTS
            requirements = ANALYSIS_REQUIREMENTS[analysis_type]
            assert len(requirements.required) > 0
            assert requirements.description

    def test_energy_intensity_requirements(self):
        """Test energy intensity requirements."""
        requirements = ANALYSIS_REQUIREMENTS[AnalysisType.ENERGY_INTENSITY]
        assert "floor_area" in requirements.required
        assert "energy_data" in requirements.required

    def test_eu_taxonomy_requirements(self):
        """Test EU Taxonomy requirements."""
        requirements = ANALYSIS_REQUIREMENTS[AnalysisType.EU_TAXONOMY]
        assert "floor_area" in requirements.required
        assert "energy_data" in requirements.required
        assert "building_type" in requirements.required
        assert "epc_rating" in requirements.recommended

    def test_crrem_requirements(self):
        """Test CRREM requirements."""
        requirements = ANALYSIS_REQUIREMENTS[AnalysisType.CRREM]
        assert "floor_area" in requirements.required
        assert "energy_data" in requirements.required
        assert "multi_year_energy_data" in requirements.required
        assert "location" in requirements.required

    def test_gresb_requirements(self):
        """Test GRESB requirements."""
        requirements = ANALYSIS_REQUIREMENTS[AnalysisType.GRESB]
        assert "water_data" in requirements.required
        assert "waste_data" in requirements.required
        assert "energy_data" in requirements.required


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    """Tests for model enums."""

    def test_building_types(self):
        """Test building type enum values."""
        assert BuildingType.OFFICE.value == "office"
        assert BuildingType.RESIDENTIAL.value == "residential"
        assert BuildingType.RETAIL.value == "retail"

    def test_energy_types(self):
        """Test energy type enum values."""
        assert EnergyType.ELECTRICITY.value == "electricity"
        assert EnergyType.GAS.value == "gas"
        assert EnergyType.DISTRICT_HEATING.value == "district_heating"

    def test_consumption_categories(self):
        """Test consumption category enum values."""
        assert ConsumptionCategory.WATER.value == "water"
        assert ConsumptionCategory.WASTE_TOTAL.value == "waste_total"

    def test_data_sources(self):
        """Test data source enum values."""
        assert DataSource.UTILITY_BILL.value == "utility_bill"
        assert DataSource.SMART_METER.value == "smart_meter"
        assert DataSource.ESTIMATE.value == "estimate"

    def test_analysis_types(self):
        """Test analysis type enum values."""
        assert AnalysisType.ENERGY_INTENSITY.value == "energy_intensity"
        assert AnalysisType.CARBON_FOOTPRINT.value == "carbon_footprint"
        assert AnalysisType.EU_TAXONOMY.value == "eu_taxonomy"
        assert AnalysisType.CRREM.value == "crrem"
        assert AnalysisType.GRESB.value == "gresb"


# =============================================================================
# Tool Tests (Using Imported Tool Internals)
# =============================================================================


class TestDataAvailabilityCheck:
    """Tests for _check_data_availability helper."""

    def test_data_availability_empty_project(
        self, sample_project, clean_store: BuildingStore
    ):
        """Test data availability check for project with no data."""
        from app.tools.esg import _check_data_availability

        energy_data = clean_store.get_energy_data(sample_project.project_id)
        consumption_data = clean_store.get_consumption_data(sample_project.project_id)
        current_year = datetime.now(UTC).year

        availability = _check_data_availability(
            sample_project, energy_data, consumption_data, current_year
        )

        assert availability["floor_area"] is True
        assert availability["building_type"] is True
        assert availability["energy_data"] is False
        assert availability["recent_energy_data"] is False
        assert availability["water_data"] is False
        assert availability["waste_data"] is False

    def test_data_availability_with_energy(
        self, project_with_energy_data, clean_store: BuildingStore
    ):
        """Test data availability check for project with energy data."""
        from app.tools.esg import _check_data_availability

        energy_data = clean_store.get_energy_data(project_with_energy_data.project_id)
        consumption_data = clean_store.get_consumption_data(
            project_with_energy_data.project_id
        )
        current_year = datetime.now(UTC).year

        availability = _check_data_availability(
            project_with_energy_data, energy_data, consumption_data, current_year
        )

        assert availability["floor_area"] is True
        assert availability["energy_data"] is True
        assert availability["recent_energy_data"] is True
        assert availability["multi_year_energy_data"] is True


class TestDataQualityCheck:
    """Tests for _check_data_quality helper."""

    def test_data_quality_no_issues(
        self, project_with_energy_data, clean_store: BuildingStore
    ):
        """Test data quality check with no issues."""
        from app.tools.esg import _check_data_quality

        energy_data = clean_store.get_energy_data(project_with_energy_data.project_id)
        issues = _check_data_quality(energy_data)

        # No estimated data, so no issues about estimates
        estimate_issues = [i for i in issues if "estimate" in i.lower()]
        assert len(estimate_issues) == 0

    def test_data_quality_with_estimates(
        self, sample_project, clean_store: BuildingStore
    ):
        """Test data quality check with estimated data."""
        from app.tools.esg import _check_data_quality

        project_id = sample_project.project_id
        energy_data = EnergyDataCreate(
            year=2024,
            energy_type=EnergyType.ELECTRICITY,
            consumption_kwh=100000.0,
            is_estimated=True,
        )
        clean_store.add_energy_data(project_id, energy_data)

        all_energy = clean_store.get_energy_data(project_id)
        issues = _check_data_quality(all_energy)

        # Should have issue about estimated data
        estimate_issues = [i for i in issues if "estimate" in i.lower()]
        assert len(estimate_issues) == 1


class TestSuggestionHelper:
    """Tests for _get_suggestion_for_requirement helper."""

    def test_suggestions_exist_for_common_requirements(self):
        """Test that suggestions exist for common requirements."""
        from app.tools.esg import _get_suggestion_for_requirement

        assert _get_suggestion_for_requirement("floor_area") is not None
        assert _get_suggestion_for_requirement("energy_data") is not None
        assert _get_suggestion_for_requirement("water_data") is not None
        assert _get_suggestion_for_requirement("epc_rating") is not None

    def test_suggestion_returns_none_for_unknown(self):
        """Test that unknown requirements return None."""
        from app.tools.esg import _get_suggestion_for_requirement

        assert _get_suggestion_for_requirement("unknown_requirement") is None


# =============================================================================
# ESG Analysis Calculation Tests
# =============================================================================


class TestEnergyIntensityCalculation:
    """Tests for energy intensity calculation logic."""

    def test_energy_intensity_calculation(
        self, project_with_energy_data, clean_store: BuildingStore
    ):
        """Test energy intensity calculation."""
        # Get data
        project = project_with_energy_data
        energy_data = clean_store.get_energy_data(project.project_id, year=2024)

        # Calculate manually
        total_energy = sum(e.consumption_kwh for e in energy_data)
        floor_area = project.floor_area_sqm
        expected_intensity = total_energy / floor_area

        # 500000 electricity + 200000 gas = 700000 kWh
        # 700000 / 5000 = 140 kWh/m²/a
        assert total_energy == 700000.0
        assert expected_intensity == 140.0


class TestCarbonFootprintCalculation:
    """Tests for carbon footprint calculation logic."""

    def test_emission_factors_defined(self):
        """Test that emission factors are defined for all energy types."""
        from app.tools.esg import EMISSION_FACTORS

        assert EnergyType.ELECTRICITY in EMISSION_FACTORS
        assert EnergyType.GAS in EMISSION_FACTORS
        assert EnergyType.DISTRICT_HEATING in EMISSION_FACTORS
        assert EnergyType.OIL in EMISSION_FACTORS

    def test_primary_energy_factors_defined(self):
        """Test that primary energy factors are defined."""
        from app.tools.esg import PRIMARY_ENERGY_FACTORS

        assert EnergyType.ELECTRICITY in PRIMARY_ENERGY_FACTORS
        assert EnergyType.GAS in PRIMARY_ENERGY_FACTORS

    def test_carbon_calculation(
        self, project_with_energy_data, clean_store: BuildingStore
    ):
        """Test carbon emission calculation."""
        from app.tools.esg import EMISSION_FACTORS

        # Get data
        project = project_with_energy_data
        energy_data = clean_store.get_energy_data(project.project_id, year=2024)

        # Calculate manually
        total_emissions = 0.0
        for record in energy_data:
            factor = EMISSION_FACTORS.get(record.energy_type, 0)
            total_emissions += record.consumption_kwh * factor / 1000  # Convert to kg

        # 500000 * 380 / 1000 = 190000 kg (electricity)
        # 200000 * 201 / 1000 = 40200 kg (gas)
        # Total = 230200 kg
        assert total_emissions == pytest.approx(230200.0, rel=0.01)


class TestEUTaxonomyThresholds:
    """Tests for EU Taxonomy threshold configuration."""

    def test_thresholds_defined(self):
        """Test that thresholds are defined for building types."""
        from app.tools.esg import EU_TAXONOMY_THRESHOLDS

        assert BuildingType.OFFICE in EU_TAXONOMY_THRESHOLDS
        assert BuildingType.RESIDENTIAL in EU_TAXONOMY_THRESHOLDS
        assert BuildingType.RETAIL in EU_TAXONOMY_THRESHOLDS

    def test_office_threshold(self):
        """Test office building threshold."""
        from app.tools.esg import EU_TAXONOMY_THRESHOLDS

        # EU Taxonomy requires < 100 kWh/m²/a for offices
        assert EU_TAXONOMY_THRESHOLDS[BuildingType.OFFICE] == 100.0


class TestEnergyRating:
    """Tests for energy rating assignment."""

    def test_rating_thresholds_defined(self):
        """Test that rating thresholds are defined."""
        from app.tools.esg import ENERGY_RATING_THRESHOLDS

        assert "A" in ENERGY_RATING_THRESHOLDS
        assert "B" in ENERGY_RATING_THRESHOLDS
        assert "C" in ENERGY_RATING_THRESHOLDS
        assert "G" in ENERGY_RATING_THRESHOLDS

    def test_rating_assignment(self):
        """Test rating is assigned based on intensity."""
        from app.tools.esg import ENERGY_RATING_THRESHOLDS

        # Lower intensity = better rating
        # A should be the lowest threshold
        a_threshold = ENERGY_RATING_THRESHOLDS["A"]
        g_threshold = ENERGY_RATING_THRESHOLDS["G"]

        assert a_threshold < g_threshold


# =============================================================================
# Integration Tests
# =============================================================================


class TestFullWorkflow:
    """Integration tests for complete ESG assessment workflow."""

    def test_complete_data_collection_workflow(self, clean_store: BuildingStore):
        """Test a complete data collection workflow."""
        # Step 1: Create project
        project_data = BuildingProjectCreate(
            name="Integration Test Building",
            floor_area_sqm=10000.0,
            construction_year=1995,
            building_type=BuildingType.OFFICE,
            city="Frankfurt",
            epc_rating="D",
        )
        project = clean_store.create_project(project_data)
        project_id = project.project_id

        # Step 2: Verify no energy data initially
        energy_data = clean_store.get_energy_data(project_id)
        assert len(energy_data) == 0

        # Step 3: Add energy data
        clean_store.add_energy_data(
            project_id,
            EnergyDataCreate(
                year=2024,
                energy_type=EnergyType.ELECTRICITY,
                consumption_kwh=800000.0,
            ),
        )
        clean_store.add_energy_data(
            project_id,
            EnergyDataCreate(
                year=2024,
                energy_type=EnergyType.GAS,
                consumption_kwh=400000.0,
            ),
        )

        # Step 4: Verify energy data
        energy_data = clean_store.get_energy_data(project_id)
        assert len(energy_data) == 2

        total_energy = sum(e.consumption_kwh for e in energy_data)
        assert total_energy == 1200000.0

        # Step 5: Calculate intensity
        intensity = total_energy / project.floor_area_sqm
        assert intensity == 120.0  # 1.2M / 10000

        # Step 6: Clean up
        result = clean_store.delete_project(project_id)
        assert result is True

    def test_gresb_data_collection_workflow(self, clean_store: BuildingStore):
        """Test workflow to collect GRESB-required data."""
        # Create project
        project_data = BuildingProjectCreate(
            name="GRESB Ready Building",
            floor_area_sqm=5000.0,
            construction_year=2010,
            building_type=BuildingType.OFFICE,
            city="Berlin",
        )
        project = clean_store.create_project(project_data)
        project_id = project.project_id

        # Add energy data
        clean_store.add_energy_data(
            project_id,
            EnergyDataCreate(
                year=2024,
                energy_type=EnergyType.ELECTRICITY,
                consumption_kwh=300000.0,
            ),
        )

        # Add water data (required for GRESB)
        clean_store.add_consumption_data(
            project_id,
            ConsumptionDataCreate(
                year=2024,
                category=ConsumptionCategory.WATER,
                value=2500.0,
                unit="m3",
            ),
        )

        # Add waste data (required for GRESB)
        clean_store.add_consumption_data(
            project_id,
            ConsumptionDataCreate(
                year=2024,
                category=ConsumptionCategory.WASTE_TOTAL,
                value=15000.0,
                unit="kg",
            ),
        )

        # Verify all data collected
        energy = clean_store.get_energy_data(project_id)
        consumption = clean_store.get_consumption_data(project_id)

        assert len(energy) == 1
        assert len(consumption) == 2

        # Verify water and waste present
        categories = {c.category for c in consumption}
        assert ConsumptionCategory.WATER in categories
        assert ConsumptionCategory.WASTE_TOTAL in categories

        # Clean up
        clean_store.delete_project(project_id)

    def test_multi_year_data_for_crrem(self, clean_store: BuildingStore):
        """Test collecting multi-year data for CRREM analysis."""
        # Create project
        project_data = BuildingProjectCreate(
            name="CRREM Analysis Building",
            floor_area_sqm=8000.0,
            construction_year=1980,
            building_type=BuildingType.OFFICE,
            city="Munich",
        )
        project = clean_store.create_project(project_data)
        project_id = project.project_id

        # Add multi-year energy data (required for CRREM)
        for year in [2022, 2023, 2024]:
            # Simulate decreasing consumption (improvement trend)
            consumption = 1000000 - (year - 2022) * 50000
            clean_store.add_energy_data(
                project_id,
                EnergyDataCreate(
                    year=year,
                    energy_type=EnergyType.ELECTRICITY,
                    consumption_kwh=float(consumption),
                ),
            )

        # Verify multi-year data
        energy = clean_store.get_energy_data(project_id)
        years = {e.year for e in energy}

        assert len(years) >= 2  # CRREM requires multi-year
        assert 2022 in years
        assert 2023 in years
        assert 2024 in years

        # Verify trend (consumption decreasing)
        sorted_data = sorted(energy, key=lambda e: e.year)
        assert sorted_data[0].consumption_kwh > sorted_data[-1].consumption_kwh

        # Clean up
        clean_store.delete_project(project_id)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_zero_floor_area_handling(self, clean_store: BuildingStore):
        """Test that zero floor area is rejected."""
        with pytest.raises(ValidationError, match="floor_area_sqm"):
            BuildingProjectCreate(
                name="Zero Area",
                floor_area_sqm=0.0,
                construction_year=2000,
            )

    def test_negative_consumption_handling(self):
        """Test that negative consumption is rejected."""
        with pytest.raises(ValidationError, match="consumption_kwh"):
            EnergyDataCreate(
                year=2024,
                energy_type=EnergyType.ELECTRICITY,
                consumption_kwh=-100.0,
            )

    def test_future_year_handling(self):
        """Test that future year beyond limit is rejected."""
        with pytest.raises(ValidationError, match="year"):
            EnergyDataCreate(
                year=2050,  # Beyond 2030 limit
                energy_type=EnergyType.ELECTRICITY,
                consumption_kwh=100000.0,
            )

    def test_very_old_construction_year(self, clean_store: BuildingStore):
        """Test that very old construction year is rejected."""
        with pytest.raises(ValidationError, match="construction_year"):
            BuildingProjectCreate(
                name="Ancient Building",
                floor_area_sqm=1000.0,
                construction_year=1700,  # Before 1800 limit
            )

    def test_empty_energy_data_list(self, sample_project, clean_store: BuildingStore):
        """Test handling of empty energy data list."""
        energy = clean_store.get_energy_data(sample_project.project_id)
        assert energy == []

    def test_project_summary_with_no_data(
        self, sample_project, clean_store: BuildingStore
    ):
        """Test project summary with no energy/consumption data."""
        summary = clean_store.get_project_summary(sample_project.project_id)

        assert summary is not None
        assert summary["project"]["name"] == "Test Building"
        assert len(summary["energy_data"]) == 0
        assert len(summary["consumption_data"]) == 0

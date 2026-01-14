"""Sustainability analysis tools for Real Estate Sustainability MCP Server.

This module provides tools for analyzing building sustainability metrics,
calculating carbon footprints, generating sustainability scores, and
suggesting improvements.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.tracing import traced_tool


class BuildingData(BaseModel):
    """Input model for building sustainability data."""

    name: str = Field(
        default="Building",
        description="Name or identifier for the building",
    )
    energy_kwh_per_year: float = Field(
        ...,
        ge=0,
        description="Annual energy consumption in kWh",
    )
    floor_area_sqm: float = Field(
        ...,
        gt=0,
        description="Total floor area in square meters",
    )
    water_liters_per_year: float = Field(
        default=0,
        ge=0,
        description="Annual water consumption in liters",
    )
    waste_kg_per_year: float = Field(
        default=0,
        ge=0,
        description="Annual waste generated in kg",
    )
    recycling_percentage: float = Field(
        default=0,
        ge=0,
        le=100,
        description="Percentage of waste that is recycled (0-100)",
    )
    renewable_energy_percentage: float = Field(
        default=0,
        ge=0,
        le=100,
        description="Percentage of energy from renewable sources (0-100)",
    )
    building_year: int = Field(
        default=2000,
        ge=1800,
        le=2030,
        description="Year the building was constructed",
    )
    has_green_certification: bool = Field(
        default=False,
        description="Whether the building has any green certification (LEED, BREEAM, etc.)",
    )


# Energy rating thresholds (kWh/m²/year) based on EU Energy Performance standards
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

# Average CO2 emissions per kWh (kg CO2/kWh) - EU average grid mix
CO2_PER_KWH = 0.233

# Water usage benchmark (liters/m²/year) for commercial buildings
WATER_BENCHMARK = 500

# Waste benchmark (kg/m²/year) for commercial buildings
WASTE_BENCHMARK = 50


@traced_tool("calculate_energy_rating")
def calculate_energy_rating(
    energy_kwh_per_year: float,
    floor_area_sqm: float,
) -> dict[str, Any]:
    """Calculate the energy efficiency rating for a building.

    Returns an energy rating from A+ to G based on energy consumption
    per square meter, following EU Energy Performance Certificate standards.

    Args:
        energy_kwh_per_year: Annual energy consumption in kWh.
        floor_area_sqm: Total floor area in square meters.

    Returns:
        Energy rating with breakdown and comparison to benchmarks.
    """
    energy_per_sqm = energy_kwh_per_year / floor_area_sqm

    rating = "G"
    for grade, threshold in ENERGY_RATING_THRESHOLDS.items():
        if energy_per_sqm <= threshold:
            rating = grade
            break

    # Calculate percentile (how it compares to average)
    average_consumption = 125  # kWh/m²/year EU average for commercial
    efficiency_vs_average = (
        (average_consumption - energy_per_sqm) / average_consumption
    ) * 100

    return {
        "rating": rating,
        "energy_per_sqm": round(energy_per_sqm, 2),
        "unit": "kWh/m²/year",
        "thresholds": ENERGY_RATING_THRESHOLDS,
        "comparison": {
            "eu_average": average_consumption,
            "efficiency_vs_average_percent": round(efficiency_vs_average, 1),
            "better_than_average": energy_per_sqm < average_consumption,
        },
        "interpretation": _get_rating_interpretation(rating),
    }


def _get_rating_interpretation(rating: str) -> str:
    """Get human-readable interpretation of energy rating."""
    interpretations = {
        "A+": "Exceptional - Near zero energy building, highest efficiency",
        "A": "Excellent - Very low energy consumption, highly efficient",
        "B": "Good - Low energy consumption, above average efficiency",
        "C": "Average - Typical energy consumption for modern buildings",
        "D": "Below Average - Higher than typical energy consumption",
        "E": "Poor - Significant energy inefficiency, improvements recommended",
        "F": "Very Poor - Major energy inefficiency, urgent improvements needed",
        "G": "Critical - Extremely inefficient, immediate action required",
    }
    return interpretations.get(rating, "Unknown rating")


@traced_tool("calculate_carbon_footprint")
def calculate_carbon_footprint(
    energy_kwh_per_year: float,
    floor_area_sqm: float,
    renewable_energy_percentage: float = 0,
) -> dict[str, Any]:
    """Calculate the carbon footprint of a building.

    Estimates annual CO2 emissions based on energy consumption,
    accounting for renewable energy usage.

    Args:
        energy_kwh_per_year: Annual energy consumption in kWh.
        floor_area_sqm: Total floor area in square meters.
        renewable_energy_percentage: Percentage of energy from renewables (0-100).

    Returns:
        Carbon footprint analysis with emissions and equivalents.
    """
    # Adjust for renewable energy (assumes zero emissions from renewables)
    non_renewable_fraction = (100 - renewable_energy_percentage) / 100
    effective_energy = energy_kwh_per_year * non_renewable_fraction

    # Calculate CO2 emissions
    total_co2_kg = effective_energy * CO2_PER_KWH
    co2_per_sqm = total_co2_kg / floor_area_sqm

    # Fun equivalents for context
    trees_needed = total_co2_kg / 21  # Average tree absorbs ~21kg CO2/year
    car_km_equivalent = total_co2_kg / 0.12  # Average car: 120g CO2/km
    flights_equivalent = total_co2_kg / 250  # Short-haul flight: ~250kg CO2

    return {
        "total_co2_kg_per_year": round(total_co2_kg, 2),
        "co2_per_sqm": round(co2_per_sqm, 2),
        "unit": "kg CO2/year",
        "renewable_offset_percent": renewable_energy_percentage,
        "emissions_factor_used": CO2_PER_KWH,
        "equivalents": {
            "trees_to_offset": round(trees_needed, 1),
            "car_kilometers": round(car_km_equivalent, 0),
            "short_flights": round(flights_equivalent, 1),
        },
        "reduction_potential": {
            "with_50_percent_renewable": round(total_co2_kg * 0.5, 2),
            "with_100_percent_renewable": 0,
        },
    }


@traced_tool("sustainability_score")
def sustainability_score(
    energy_kwh_per_year: float,
    floor_area_sqm: float,
    water_liters_per_year: float = 0,
    waste_kg_per_year: float = 0,
    recycling_percentage: float = 0,
    renewable_energy_percentage: float = 0,
    has_green_certification: bool = False,
) -> dict[str, Any]:
    """Calculate an overall sustainability score for a building.

    Generates a comprehensive score from 0-100 based on multiple
    sustainability factors including energy, water, waste, and certifications.

    Args:
        energy_kwh_per_year: Annual energy consumption in kWh.
        floor_area_sqm: Total floor area in square meters.
        water_liters_per_year: Annual water consumption in liters.
        waste_kg_per_year: Annual waste generated in kg.
        recycling_percentage: Percentage of waste recycled (0-100).
        renewable_energy_percentage: Percentage of renewable energy (0-100).
        has_green_certification: Whether building has green certification.

    Returns:
        Overall sustainability score with category breakdown.
    """
    scores = {}

    # Energy score (40% weight)
    energy_per_sqm = energy_kwh_per_year / floor_area_sqm
    if energy_per_sqm <= 50:
        energy_score = 100
    elif energy_per_sqm <= 100:
        energy_score = 80 - ((energy_per_sqm - 50) / 50) * 20
    elif energy_per_sqm <= 200:
        energy_score = 60 - ((energy_per_sqm - 100) / 100) * 30
    else:
        energy_score = max(0, 30 - ((energy_per_sqm - 200) / 100) * 30)
    scores["energy"] = {"score": round(energy_score, 1), "weight": 0.4}

    # Renewable energy bonus (15% weight)
    renewable_score = renewable_energy_percentage
    scores["renewable"] = {"score": round(renewable_score, 1), "weight": 0.15}

    # Water score (15% weight)
    if water_liters_per_year > 0:
        water_per_sqm = water_liters_per_year / floor_area_sqm
        if water_per_sqm <= WATER_BENCHMARK * 0.5:
            water_score = 100
        elif water_per_sqm <= WATER_BENCHMARK:
            water_score = 70 + (1 - water_per_sqm / WATER_BENCHMARK) * 30
        else:
            water_score = max(
                0, 70 - ((water_per_sqm - WATER_BENCHMARK) / WATER_BENCHMARK) * 70
            )
    else:
        water_score = 50  # No data, assume average
    scores["water"] = {"score": round(water_score, 1), "weight": 0.15}

    # Waste score (15% weight)
    if waste_kg_per_year > 0:
        waste_per_sqm = waste_kg_per_year / floor_area_sqm
        waste_base = (
            50
            if waste_per_sqm <= WASTE_BENCHMARK
            else max(0, 50 - ((waste_per_sqm - WASTE_BENCHMARK) / WASTE_BENCHMARK) * 50)
        )
        recycling_bonus = recycling_percentage * 0.5
        waste_score = min(100, waste_base + recycling_bonus)
    else:
        waste_score = 50 + recycling_percentage * 0.5
    scores["waste"] = {"score": round(waste_score, 1), "weight": 0.15}

    # Certification bonus (15% weight)
    cert_score = 100 if has_green_certification else 0
    scores["certification"] = {"score": cert_score, "weight": 0.15}

    # Calculate weighted total
    total_score = sum(s["score"] * s["weight"] for s in scores.values())

    # Determine grade
    if total_score >= 90:
        grade = "A+"
    elif total_score >= 80:
        grade = "A"
    elif total_score >= 70:
        grade = "B"
    elif total_score >= 60:
        grade = "C"
    elif total_score >= 50:
        grade = "D"
    elif total_score >= 40:
        grade = "E"
    else:
        grade = "F"

    return {
        "total_score": round(total_score, 1),
        "grade": grade,
        "category_scores": scores,
        "interpretation": _get_score_interpretation(total_score),
        "top_improvement_area": min(scores.items(), key=lambda x: x[1]["score"])[0],
    }


def _get_score_interpretation(score: float) -> str:
    """Get interpretation of sustainability score."""
    if score >= 90:
        return "Exceptional sustainability performance - industry leader"
    elif score >= 80:
        return "Excellent sustainability - well above average"
    elif score >= 70:
        return "Good sustainability - above average performance"
    elif score >= 60:
        return "Average sustainability - meets basic standards"
    elif score >= 50:
        return "Below average - improvement opportunities exist"
    elif score >= 40:
        return "Poor sustainability - significant improvements needed"
    else:
        return "Critical - urgent sustainability improvements required"


@traced_tool("suggest_improvements")
def suggest_improvements(
    energy_kwh_per_year: float,
    floor_area_sqm: float,
    building_year: int = 2000,
    renewable_energy_percentage: float = 0,
    recycling_percentage: float = 0,
    has_green_certification: bool = False,
) -> dict[str, Any]:
    """Suggest sustainability improvements for a building.

    Analyzes current building metrics and provides prioritized
    recommendations for improving sustainability performance.

    Args:
        energy_kwh_per_year: Annual energy consumption in kWh.
        floor_area_sqm: Total floor area in square meters.
        building_year: Year the building was constructed.
        renewable_energy_percentage: Current percentage of renewable energy.
        recycling_percentage: Current recycling rate.
        has_green_certification: Whether building has certification.

    Returns:
        Prioritized list of improvement suggestions with estimated impact.
    """
    suggestions = []
    energy_per_sqm = energy_kwh_per_year / floor_area_sqm

    # Energy efficiency improvements
    if energy_per_sqm > 100:
        priority = "high" if energy_per_sqm > 150 else "medium"
        potential_savings = (energy_per_sqm - 75) * floor_area_sqm * 0.15  # €0.15/kWh
        suggestions.append(
            {
                "category": "energy_efficiency",
                "title": "Improve Building Insulation",
                "description": "Upgrade wall, roof, and window insulation to reduce heat loss",
                "priority": priority,
                "estimated_energy_reduction_percent": 20,
                "estimated_annual_savings_eur": round(potential_savings * 0.2, 0),
                "implementation_cost": "medium",
                "payback_years": 5,
            }
        )

    if energy_per_sqm > 75:
        suggestions.append(
            {
                "category": "energy_efficiency",
                "title": "LED Lighting Upgrade",
                "description": "Replace all lighting with LED fixtures and add motion sensors",
                "priority": "medium",
                "estimated_energy_reduction_percent": 10,
                "estimated_annual_savings_eur": round(
                    energy_kwh_per_year * 0.1 * 0.15, 0
                ),
                "implementation_cost": "low",
                "payback_years": 2,
            }
        )

    # Renewable energy
    if renewable_energy_percentage < 50:
        suggestions.append(
            {
                "category": "renewable_energy",
                "title": "Install Solar Panels",
                "description": "Add rooftop solar PV system to generate clean electricity",
                "priority": "high" if renewable_energy_percentage < 20 else "medium",
                "estimated_energy_reduction_percent": 30,
                "estimated_co2_reduction_kg": round(
                    energy_kwh_per_year * 0.3 * CO2_PER_KWH, 0
                ),
                "implementation_cost": "high",
                "payback_years": 8,
            }
        )

    if renewable_energy_percentage < 100:
        suggestions.append(
            {
                "category": "renewable_energy",
                "title": "Switch to Green Energy Supplier",
                "description": "Purchase 100% renewable electricity from your energy provider",
                "priority": "low",
                "estimated_energy_reduction_percent": 0,
                "estimated_co2_reduction_kg": round(
                    energy_kwh_per_year
                    * (1 - renewable_energy_percentage / 100)
                    * CO2_PER_KWH,
                    0,
                ),
                "implementation_cost": "none",
                "payback_years": 0,
            }
        )

    # HVAC improvements for older buildings
    if building_year < 2010:
        suggestions.append(
            {
                "category": "hvac",
                "title": "HVAC System Upgrade",
                "description": "Replace aging heating/cooling with modern heat pump system",
                "priority": "high" if building_year < 2000 else "medium",
                "estimated_energy_reduction_percent": 25,
                "estimated_annual_savings_eur": round(
                    energy_kwh_per_year * 0.25 * 0.15, 0
                ),
                "implementation_cost": "high",
                "payback_years": 7,
            }
        )

    # Waste management
    if recycling_percentage < 50:
        suggestions.append(
            {
                "category": "waste",
                "title": "Implement Recycling Program",
                "description": "Set up comprehensive recycling with clear signage and training",
                "priority": "medium",
                "estimated_recycling_increase_percent": 30,
                "implementation_cost": "low",
                "payback_years": 1,
            }
        )

    # Certification
    if not has_green_certification:
        suggestions.append(
            {
                "category": "certification",
                "title": "Pursue Green Building Certification",
                "description": "Apply for LEED, BREEAM, or DGNB certification to validate efforts",
                "priority": "low",
                "benefits": [
                    "Market differentiation",
                    "Higher property value",
                    "Tenant attraction",
                    "Regulatory compliance",
                ],
                "implementation_cost": "medium",
            }
        )

    # Smart building
    suggestions.append(
        {
            "category": "smart_building",
            "title": "Install Building Management System",
            "description": "Deploy IoT sensors and BMS for real-time energy monitoring and optimization",
            "priority": "medium",
            "estimated_energy_reduction_percent": 15,
            "implementation_cost": "medium",
            "payback_years": 4,
        }
    )

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    return {
        "building_analysis": {
            "energy_per_sqm": round(energy_per_sqm, 2),
            "building_age_years": 2025 - building_year,
            "current_renewable_percent": renewable_energy_percentage,
            "current_recycling_percent": recycling_percentage,
        },
        "total_suggestions": len(suggestions),
        "suggestions": suggestions,
        "quick_wins": [
            s for s in suggestions if s.get("implementation_cost") in ("none", "low")
        ],
        "high_impact": [s for s in suggestions if s.get("priority") == "high"],
    }


@traced_tool("compare_buildings")
def compare_buildings(
    buildings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare sustainability metrics across multiple buildings.

    Analyzes and ranks buildings by various sustainability criteria,
    identifying best performers and areas for improvement.

    Args:
        buildings: List of building data dictionaries, each containing:
            - name: Building identifier
            - energy_kwh_per_year: Annual energy consumption
            - floor_area_sqm: Floor area in square meters
            - (optional) water_liters_per_year, waste_kg_per_year, etc.

    Returns:
        Comparison analysis with rankings and insights.
    """
    if not buildings:
        return {"error": "No buildings provided for comparison"}

    if len(buildings) < 2:
        return {"error": "At least 2 buildings required for comparison"}

    results = []
    for building in buildings:
        name = building.get("name", f"Building {len(results) + 1}")
        energy = building.get("energy_kwh_per_year", 0)
        area = building.get("floor_area_sqm", 1)
        renewable = building.get("renewable_energy_percentage", 0)

        energy_per_sqm = energy / area if area > 0 else 0
        co2_kg = energy * (1 - renewable / 100) * CO2_PER_KWH

        # Get energy rating
        rating_result = calculate_energy_rating(energy, area)

        results.append(
            {
                "name": name,
                "energy_per_sqm": round(energy_per_sqm, 2),
                "energy_rating": rating_result["rating"],
                "co2_kg_per_year": round(co2_kg, 2),
                "renewable_percent": renewable,
                "floor_area_sqm": area,
            }
        )

    # Sort by energy efficiency
    results.sort(key=lambda x: x["energy_per_sqm"])

    # Calculate averages
    avg_energy = sum(r["energy_per_sqm"] for r in results) / len(results)
    avg_co2 = sum(r["co2_kg_per_year"] for r in results) / len(results)

    # Find best and worst
    best_energy = results[0]
    worst_energy = results[-1]

    return {
        "building_count": len(results),
        "rankings": results,
        "best_performer": {
            "name": best_energy["name"],
            "energy_per_sqm": best_energy["energy_per_sqm"],
            "rating": best_energy["energy_rating"],
        },
        "needs_improvement": {
            "name": worst_energy["name"],
            "energy_per_sqm": worst_energy["energy_per_sqm"],
            "rating": worst_energy["energy_rating"],
        },
        "portfolio_averages": {
            "avg_energy_per_sqm": round(avg_energy, 2),
            "avg_co2_kg_per_year": round(avg_co2, 2),
        },
        "potential_savings": {
            "if_all_matched_best_kwh": round(
                sum(
                    (r["energy_per_sqm"] - best_energy["energy_per_sqm"])
                    * r["floor_area_sqm"]
                    for r in results
                ),
                0,
            ),
            "if_all_matched_best_co2_kg": round(
                sum(
                    (r["co2_kg_per_year"] - best_energy["co2_kg_per_year"])
                    for r in results
                ),
                0,
            ),
        },
    }


__all__ = [
    "BuildingData",
    "calculate_carbon_footprint",
    "calculate_energy_rating",
    "compare_buildings",
    "suggest_improvements",
    "sustainability_score",
]

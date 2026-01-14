"""SQLite database store for building projects and ESG data.

This module provides persistence for building projects, energy data, and
consumption data using SQLite. The store is designed to work with RefCache
for cross-tool reference support.

Features:
- CRUD operations for building projects
- Energy and consumption data management
- Automatic database initialization
- Thread-safe operations
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

    from app.models import (
        BuildingProject,
        BuildingProjectCreate,
        BuildingProjectUpdate,
        ConsumptionData,
        ConsumptionDataCreate,
        EnergyData,
        EnergyDataCreate,
    )

# Default database location
DEFAULT_DB_PATH = Path.home() / ".real-estate-sustainability-mcp" / "data.db"


def get_db_path() -> Path:
    """Get the database path from environment or use default."""
    env_path = os.environ.get("DATABASE_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


class BuildingStore:
    """SQLite-based store for building projects and related data.

    This class manages all database operations for the ESG assessment system.
    It automatically creates the database and tables on first use.

    Usage:
        store = BuildingStore()
        project = store.create_project(BuildingProjectCreate(...))
        all_projects = store.list_projects()
    """

    def __init__(self, db_path: Path | None = None) -> None:
        """Initialize the store with the given database path.

        Args:
            db_path: Path to the SQLite database file. If None, uses the
                     DATABASE_PATH environment variable or default location.
        """
        self.db_path = db_path or get_db_path()
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure the database directory and tables exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            self._create_tables(conn)

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _create_tables(self, conn: sqlite3.Connection) -> None:
        """Create database tables if they don't exist."""
        cursor = conn.cursor()

        # Building projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS building_projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT DEFAULT '',
                city TEXT DEFAULT '',
                country TEXT DEFAULT 'DE',
                building_type TEXT DEFAULT 'office',
                floor_area_sqm REAL NOT NULL,
                gross_floor_area_sqm REAL,
                construction_year INTEGER NOT NULL,
                renovation_year INTEGER,
                number_of_floors INTEGER,
                number_of_tenants INTEGER,
                occupancy_rate REAL,
                epc_rating TEXT,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Energy data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_data (
                energy_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                year INTEGER NOT NULL,
                energy_type TEXT NOT NULL,
                consumption_kwh REAL NOT NULL,
                source TEXT DEFAULT 'utility_bill',
                is_estimated INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES building_projects(project_id)
                    ON DELETE CASCADE
            )
        """)

        # Consumption data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumption_data (
                consumption_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                year INTEGER NOT NULL,
                category TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                source TEXT DEFAULT 'utility_bill',
                is_estimated INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES building_projects(project_id)
                    ON DELETE CASCADE
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_energy_project_year
            ON energy_data(project_id, year)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consumption_project_year
            ON consumption_data(project_id, year)
        """)

    # =========================================================================
    # Building Project CRUD
    # =========================================================================

    def create_project(self, data: BuildingProjectCreate) -> BuildingProject:
        """Create a new building project.

        Args:
            data: Project creation data.

        Returns:
            The created BuildingProject with generated ID and timestamps.
        """
        from uuid import uuid4

        from app.models import BuildingProject

        now = datetime.now(UTC).isoformat()
        project_id = str(uuid4())

        project = BuildingProject(
            project_id=project_id,
            name=data.name,
            address=data.address,
            city=data.city,
            country=data.country,
            building_type=data.building_type,
            floor_area_sqm=data.floor_area_sqm,
            gross_floor_area_sqm=data.gross_floor_area_sqm,
            construction_year=data.construction_year,
            renovation_year=data.renovation_year,
            number_of_floors=data.number_of_floors,
            number_of_tenants=data.number_of_tenants,
            occupancy_rate=data.occupancy_rate,
            epc_rating=data.epc_rating,
            notes=data.notes,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO building_projects (
                    project_id, name, address, city, country, building_type,
                    floor_area_sqm, gross_floor_area_sqm, construction_year,
                    renovation_year, number_of_floors, number_of_tenants,
                    occupancy_rate, epc_rating, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.project_id,
                    project.name,
                    project.address,
                    project.city,
                    project.country,
                    project.building_type.value,
                    project.floor_area_sqm,
                    project.gross_floor_area_sqm,
                    project.construction_year,
                    project.renovation_year,
                    project.number_of_floors,
                    project.number_of_tenants,
                    project.occupancy_rate,
                    project.epc_rating,
                    project.notes,
                    now,
                    now,
                ),
            )

        return project

    def get_project(self, project_id: str) -> BuildingProject | None:
        """Get a building project by ID.

        Args:
            project_id: The project's unique identifier.

        Returns:
            The BuildingProject if found, None otherwise.
        """
        from app.models import BuildingProject, BuildingType

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM building_projects WHERE project_id = ?",
                (project_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return BuildingProject(
            project_id=row["project_id"],
            name=row["name"],
            address=row["address"],
            city=row["city"],
            country=row["country"],
            building_type=BuildingType(row["building_type"]),
            floor_area_sqm=row["floor_area_sqm"],
            gross_floor_area_sqm=row["gross_floor_area_sqm"],
            construction_year=row["construction_year"],
            renovation_year=row["renovation_year"],
            number_of_floors=row["number_of_floors"],
            number_of_tenants=row["number_of_tenants"],
            occupancy_rate=row["occupancy_rate"],
            epc_rating=row["epc_rating"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def update_project(
        self, project_id: str, data: BuildingProjectUpdate
    ) -> BuildingProject | None:
        """Update a building project.

        Args:
            project_id: The project's unique identifier.
            data: Fields to update (only non-None fields are updated).

        Returns:
            The updated BuildingProject if found, None otherwise.
        """
        # Get existing project
        existing = self.get_project(project_id)
        if existing is None:
            return None

        # Build update query dynamically based on provided fields
        updates = []
        values = []
        update_dict = data.model_dump(exclude_none=True)

        for field, value in update_dict.items():
            if hasattr(value, "value"):  # Handle enums
                value = value.value
            updates.append(f"{field} = ?")
            values.append(value)

        if not updates:
            return existing

        # Add updated_at
        now = datetime.now(UTC).isoformat()
        updates.append("updated_at = ?")
        values.append(now)
        values.append(project_id)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE building_projects SET {', '.join(updates)} WHERE project_id = ?",
                values,
            )

        return self.get_project(project_id)

    def delete_project(self, project_id: str) -> bool:
        """Delete a building project and all related data.

        Args:
            project_id: The project's unique identifier.

        Returns:
            True if the project was deleted, False if not found.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Delete related data first (foreign key cascades should handle this,
            # but we're explicit for clarity)
            cursor.execute(
                "DELETE FROM energy_data WHERE project_id = ?", (project_id,)
            )
            cursor.execute(
                "DELETE FROM consumption_data WHERE project_id = ?", (project_id,)
            )
            cursor.execute(
                "DELETE FROM building_projects WHERE project_id = ?", (project_id,)
            )
            return cursor.rowcount > 0

    def list_projects(self, limit: int = 100, offset: int = 0) -> list[BuildingProject]:
        """List all building projects with pagination.

        Args:
            limit: Maximum number of projects to return.
            offset: Number of projects to skip.

        Returns:
            List of BuildingProject objects.
        """
        from app.models import BuildingProject, BuildingType

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM building_projects
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = cursor.fetchall()

        projects = []
        for row in rows:
            projects.append(
                BuildingProject(
                    project_id=row["project_id"],
                    name=row["name"],
                    address=row["address"],
                    city=row["city"],
                    country=row["country"],
                    building_type=BuildingType(row["building_type"]),
                    floor_area_sqm=row["floor_area_sqm"],
                    gross_floor_area_sqm=row["gross_floor_area_sqm"],
                    construction_year=row["construction_year"],
                    renovation_year=row["renovation_year"],
                    number_of_floors=row["number_of_floors"],
                    number_of_tenants=row["number_of_tenants"],
                    occupancy_rate=row["occupancy_rate"],
                    epc_rating=row["epc_rating"],
                    notes=row["notes"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
            )
        return projects

    def count_projects(self) -> int:
        """Count total number of building projects.

        Returns:
            Total number of projects in the database.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM building_projects")
            result = cursor.fetchone()
            return result[0] if result else 0

    # =========================================================================
    # Energy Data CRUD
    # =========================================================================

    def add_energy_data(
        self, project_id: str, data: EnergyDataCreate
    ) -> EnergyData | None:
        """Add energy consumption data to a project.

        Args:
            project_id: The project's unique identifier.
            data: Energy data to add.

        Returns:
            The created EnergyData if project exists, None otherwise.
        """
        from uuid import uuid4

        from app.models import EnergyData

        # Verify project exists
        if self.get_project(project_id) is None:
            return None

        now = datetime.now(UTC).isoformat()
        energy_id = str(uuid4())

        energy = EnergyData(
            energy_id=energy_id,
            project_id=project_id,
            year=data.year,
            energy_type=data.energy_type,
            consumption_kwh=data.consumption_kwh,
            source=data.source,
            is_estimated=data.is_estimated,
            notes=data.notes,
            created_at=datetime.fromisoformat(now),
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO energy_data (
                    energy_id, project_id, year, energy_type, consumption_kwh,
                    source, is_estimated, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    energy.energy_id,
                    energy.project_id,
                    energy.year,
                    energy.energy_type.value,
                    energy.consumption_kwh,
                    energy.source.value,
                    1 if energy.is_estimated else 0,
                    energy.notes,
                    now,
                ),
            )

        return energy

    def get_energy_data(
        self, project_id: str, year: int | None = None
    ) -> list[EnergyData]:
        """Get energy data for a project.

        Args:
            project_id: The project's unique identifier.
            year: Optional year filter.

        Returns:
            List of EnergyData records.
        """
        from app.models import DataSource, EnergyData, EnergyType

        with self._get_connection() as conn:
            cursor = conn.cursor()
            if year is not None:
                cursor.execute(
                    """
                    SELECT * FROM energy_data
                    WHERE project_id = ? AND year = ?
                    ORDER BY year DESC, energy_type
                    """,
                    (project_id, year),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM energy_data
                    WHERE project_id = ?
                    ORDER BY year DESC, energy_type
                    """,
                    (project_id,),
                )
            rows = cursor.fetchall()

        return [
            EnergyData(
                energy_id=row["energy_id"],
                project_id=row["project_id"],
                year=row["year"],
                energy_type=EnergyType(row["energy_type"]),
                consumption_kwh=row["consumption_kwh"],
                source=DataSource(row["source"]),
                is_estimated=bool(row["is_estimated"]),
                notes=row["notes"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def delete_energy_data(self, energy_id: str) -> bool:
        """Delete a specific energy data record.

        Args:
            energy_id: The energy record's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM energy_data WHERE energy_id = ?", (energy_id,))
            return cursor.rowcount > 0

    # =========================================================================
    # Consumption Data CRUD
    # =========================================================================

    def add_consumption_data(
        self, project_id: str, data: ConsumptionDataCreate
    ) -> ConsumptionData | None:
        """Add consumption data to a project.

        Args:
            project_id: The project's unique identifier.
            data: Consumption data to add.

        Returns:
            The created ConsumptionData if project exists, None otherwise.
        """
        from uuid import uuid4

        from app.models import ConsumptionData

        # Verify project exists
        if self.get_project(project_id) is None:
            return None

        now = datetime.now(UTC).isoformat()
        consumption_id = str(uuid4())

        consumption = ConsumptionData(
            consumption_id=consumption_id,
            project_id=project_id,
            year=data.year,
            category=data.category,
            value=data.value,
            unit=data.unit,
            source=data.source,
            is_estimated=data.is_estimated,
            notes=data.notes,
            created_at=datetime.fromisoformat(now),
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO consumption_data (
                    consumption_id, project_id, year, category, value,
                    unit, source, is_estimated, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    consumption.consumption_id,
                    consumption.project_id,
                    consumption.year,
                    consumption.category.value,
                    consumption.value,
                    consumption.unit,
                    consumption.source.value,
                    1 if consumption.is_estimated else 0,
                    consumption.notes,
                    now,
                ),
            )

        return consumption

    def get_consumption_data(
        self, project_id: str, year: int | None = None
    ) -> list[ConsumptionData]:
        """Get consumption data for a project.

        Args:
            project_id: The project's unique identifier.
            year: Optional year filter.

        Returns:
            List of ConsumptionData records.
        """
        from app.models import ConsumptionCategory, ConsumptionData, DataSource

        with self._get_connection() as conn:
            cursor = conn.cursor()
            if year is not None:
                cursor.execute(
                    """
                    SELECT * FROM consumption_data
                    WHERE project_id = ? AND year = ?
                    ORDER BY year DESC, category
                    """,
                    (project_id, year),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM consumption_data
                    WHERE project_id = ?
                    ORDER BY year DESC, category
                    """,
                    (project_id,),
                )
            rows = cursor.fetchall()

        return [
            ConsumptionData(
                consumption_id=row["consumption_id"],
                project_id=row["project_id"],
                year=row["year"],
                category=ConsumptionCategory(row["category"]),
                value=row["value"],
                unit=row["unit"],
                source=DataSource(row["source"]),
                is_estimated=bool(row["is_estimated"]),
                notes=row["notes"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def delete_consumption_data(self, consumption_id: str) -> bool:
        """Delete a specific consumption data record.

        Args:
            consumption_id: The consumption record's unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM consumption_data WHERE consumption_id = ?",
                (consumption_id,),
            )
            return cursor.rowcount > 0

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_project_summary(self, project_id: str) -> dict | None:
        """Get a summary of a project with all related data.

        Args:
            project_id: The project's unique identifier.

        Returns:
            Dictionary with project data and related records, or None if not found.
        """
        project = self.get_project(project_id)
        if project is None:
            return None

        energy_data = self.get_energy_data(project_id)
        consumption_data = self.get_consumption_data(project_id)

        return {
            "project": project.model_dump(),
            "energy_data": [e.model_dump() for e in energy_data],
            "consumption_data": [c.model_dump() for c in consumption_data],
            "energy_years": sorted({e.year for e in energy_data}, reverse=True),
            "has_recent_data": any(
                e.year >= datetime.now(UTC).year - 1 for e in energy_data
            ),
        }

    def clear_database(self) -> None:
        """Clear all data from the database. Use with caution!"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM consumption_data")
            cursor.execute("DELETE FROM energy_data")
            cursor.execute("DELETE FROM building_projects")


# Global store instance (lazy initialization)
_store: BuildingStore | None = None


def get_store() -> BuildingStore:
    """Get the global BuildingStore instance.

    Creates the store on first access with default settings.

    Returns:
        The global BuildingStore instance.
    """
    global _store
    if _store is None:
        _store = BuildingStore()
    return _store


def reset_store() -> None:
    """Reset the global store instance. Used for testing."""
    global _store
    _store = None

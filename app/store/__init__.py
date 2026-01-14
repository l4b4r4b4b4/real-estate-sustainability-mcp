"""Store module for Real Estate Sustainability MCP Server.

This module provides persistence for building projects and ESG data
using SQLite.

Components:
- BuildingStore: Main database interface
- get_store: Global store accessor
"""

from __future__ import annotations

from app.store.database import BuildingStore, get_store, reset_store

__all__ = [
    "BuildingStore",
    "get_store",
    "reset_store",
]

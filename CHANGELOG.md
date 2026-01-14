# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Phase 2: CRREM pathway integration
- Phase 3: Measure planning & optimization
- Phase 4: Reporting & export (S3 asset storage)
- Excel spreadsheet analysis for sustainability data
- PDF parsing for building reports and certifications

## [0.0.2] - 2026-01-14

### Added

- **Phase 1 ESG Assessment Tools** - Complete workflow for existing buildings (Bestandsgebäude)
- Building project CRUD tools:
  - `create_building_project` - Create new building for assessment
  - `get_building_project` - Retrieve project with related data
  - `update_building_project` - Update project details
  - `list_building_projects` - List all projects with pagination
  - `delete_building_project` - Remove project and all related data
- Data collection tools:
  - `add_energy_data` - Record annual energy consumption (electricity, gas, etc.)
  - `add_consumption_data` - Record water and waste data
  - `get_project_data` - Retrieve all collected data for a project
- Gap analysis tools:
  - `check_data_completeness` - Analyze data gaps with analysis-specific requirements
  - `suggest_data_sources` - Recommend documents to collect missing data
- ESG analysis tools:
  - `calculate_energy_intensity` - Calculate kWh/m²/a with energy rating
  - `calculate_carbon_footprint` - Calculate kgCO₂/m²/a emissions
  - `check_eu_taxonomy_alignment` - Evaluate EU Taxonomy criteria
- Data models with Pydantic validation (BuildingProject, EnergyData, ConsumptionData)
- SQLite persistence layer for project data
- Analysis-specific requirements system (`AnalysisType` enum, `ANALYSIS_REQUIREMENTS`)
- Support for EU Taxonomy, CRREM, and GRESB requirement profiles
- German emission factors (Umweltbundesamt 2023)
- GEG 2024 primary energy factors
- 50 new ESG tests (124 total)

### Changed

- Removed demo/admin tools from template (26 → 15 tools)
- Server now exposes only essential tools: 13 ESG + `health_check` + `get_cached_result`
- "Recent data" check now accepts data from last 2 years (was 1 year)

### Fixed

- Fixed `datetime.utcnow()` deprecation warnings - now uses `datetime.now(timezone.utc)`

## [0.0.1] - 2026-01-14

### Fixed

- Replace remaining `fastmcp-template` references with correct project name
- Update CLI app name and help text
- Update SQLite cache path in config
- Update test docstrings

## [0.0.0] - 2026-01-14

### Added

- **Initial release** of Real Estate Sustainability MCP Server
- Core server implementation with FastMCP and mcp-refcache integration
- Langfuse tracing for observability with user/session attribution
- Core tools:
  - `health_check` - Server health status and cache info
  - `store_secret` - Store secrets with EXECUTE-only agent permissions
  - `compute_with_secret` - Private computation without revealing values
  - `get_cached_result` - Paginate through cached results
- Context management tools for Langfuse testing:
  - `enable_test_context` - Enable/disable test context mode
  - `set_test_context` - Set user/session context for tracing
  - `reset_test_context` - Reset to default context values
  - `get_trace_info` - Get current Langfuse tracing status
- Admin tools (permission-gated) for cache management
- Sustainability guide and Langfuse guide prompts
- CLI with multiple transport options:
  - `stdio` - Local CLI mode
  - `sse` - Server-Sent Events transport
  - `streamable-http` - Recommended for remote/Docker deployment
- Docker support with multi-stage builds
- GitHub Actions workflows:
  - CI pipeline with Python 3.12/3.13 matrix
  - Release workflow for GHCR image publishing
  - Publish workflow for PyPI releases
- Full test suite (92 tests passing)

### Notes

This is the first experimental release. The package structure and release
workflow are validated, but domain-specific sustainability tools are not
yet implemented. See "Planned" section for upcoming features.

[Unreleased]: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp/compare/v0.0.0...v0.0.1
[0.0.0]: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp/releases/tag/v0.0.0
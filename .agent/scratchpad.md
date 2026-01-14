# Real Estate Sustainability MCP - Agent Scratchpad

## Current Status: 🟢 Phase 1 Complete - Schema Polish Done

**Last Updated**: 2026-01-15 (Session 6)

## Project Overview

**Purpose**: MCP server for ESG assessment of existing commercial buildings (Bestandsgebäude). Focused on practical agent-driven workflows for asset managers: data collection, gap analysis, EU Taxonomy alignment, and carbon footprint calculation.

**Stack**:
- Python 3.12+
- FastMCP framework
- mcp-refcache for reference-based caching
- Langfuse for tracing/observability
- UV for dependency management

**Key URLs**:
- PyPI: `real-estate-sustainability-mcp` (not yet published)
- Port: 8001 (for Flowise integration)
- Protocol: Streamable HTTP

## Current Status

### Project State: 🟡 Phase 1 Testing in Progress

- ✅ Published to PyPI: v0.0.0 and v0.0.1
- ✅ GitHub repo: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp
- ✅ Self-hosted GitHub Actions runner configured (Threadripper 64-core)
- ✅ 124 tests passing, all linting clean (50 new ESG tests added)
- ✅ Server runs on port 8001 with streamable-http transport
- ✅ Phase 1 ESG tools implemented:
  - ✅ Data models (BuildingProject, EnergyData, ConsumptionData)
  - ✅ SQLite store with persistence
  - ✅ Project CRUD tools (create/get/update/list/delete)
  - ✅ Data collection tools (add_energy_data, add_consumption_data)
  - ✅ Gap analysis tools (check_data_completeness, suggest_data_sources)
  - ✅ ESG analysis tools (energy_intensity, carbon_footprint, eu_taxonomy)
- ✅ Tool cleanup: removed demo/admin tools (26 → 15 tools)
- ✅ Analysis-specific requirements system implemented
- ✅ Interactive testing of ESG tools completed
- ✅ Comprehensive test suite for ESG tools (tests/test_esg.py)
- ✅ Published v0.0.2 to PyPI
- ✅ CI fixed for NixOS self-hosted runner
- ✅ Pre-commit hooks auto-install in flake.nix
- ✅ Goal 05: Schema investigation complete - schemas already correct!
- ✅ Added 8 schema validation tests (132 tests total)
- ✅ Fixed `get_cached_result` missing descriptions
- ✅ Created `scripts/inspect_schemas.py` for debugging
- 🟡 Flowise integration - needs testing (issue may be Flowise-side)

### Test Status

```
132 passed in 3.05s
```

### Session 4 Testing Results (Klöpperhaus)

| Metric | Value | Status |
|--------|-------|--------|
| Energy Intensity | 168.0 kWh/m²/a | Rating E |
| Primary Energy | 249.6 kWh/m²/a | - |
| Carbon Footprint | 57.12 kgCO₂/m²/a | - |
| Data Completeness | 90% | ✅ Ready |
| EU Taxonomy | NOT aligned | Gap: 149.6 kWh/m²/a |

### Integration Target

**Flowise Agent**: `59b141da-70af-4906-976a-982ad1701526`
- Configured to connect to `http://localhost:8001/mcp`
- ReACT-MCP Agent v3.2 ready
- **BLOCKED**: Flowise runs in Docker, can't reach host localhost:8001
- **SOLUTION**: Add MCP server to same Docker Compose network

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Flowise (localhost:3001)                               │
│  └── ReACT-MCP Agent (agentflow)                        │
│       └── MCP Tool → http://localhost:8001/mcp          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  real-estate-sustainability-mcp (localhost:8001)        │
│  ├── Tools:                                             │
│  │   ├── Excel Analysis (planned)                       │
│  │   ├── PDF Parsing (planned)                          │
│  │   ├── Sustainability Frameworks (planned)            │
│  │   └── IFC Integration (planned)                      │
│  ├── RefCache (reference-based caching)                 │
│  └── Langfuse (tracing/observability)                   │
└─────────────────────────────────────────────────────────┘
```

## Implementation Roadmap

See `.agent/goals/04-Certification-System-Implementation/scratchpad.md` for full details.

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1** | Simple ESG Status + EU Taxonomy | 🟡 In Design |
| **Phase 2** | CRREM Pathway Integration | ⚪ Planned |
| **Phase 3** | Measure Planning & Optimization | ⚪ Planned |
| **Phase 4** | Reporting & Export | ⚪ Planned |

### Phase 1 Tools (Implemented ✅)

| Category | Tools | Status |
|----------|-------|--------|
| **Project Store** | create/get/update/list/delete_building_project | ✅ |
| **Data Collection** | add_energy_data, add_consumption_data, get_project_data | ✅ |
| **Gap Analysis** | check_data_completeness, suggest_data_sources | ✅ |
| **ESG Analysis** | calculate_energy_intensity, calculate_carbon_footprint, check_eu_taxonomy_alignment | ✅ |

## Goals Index

| Goal | Title | Status | Priority |
|------|-------|--------|----------|
| 01 | Clean Up Template Demo Tools | 🟢 Complete | P0 |
| 02 | Minimal Working Server | 🟢 Complete | P0 |
| 03 | Publish v0.0.0 to PyPI | 🟢 Complete | P0 |
| 04 | ESG Assessment for Bestandsgebäude | 🟡 Phase 1 Complete, v0.0.2 Published | P1 |
| 05 | Tool Schema Polish for MCP/LLM | 🟢 Complete | P0 |

### Status Indicators
- 🟢 Complete
- 🟡 In Progress
- 🔴 Blocked
- ⚪ Not Started

### Architecture Decisions (Session 2-4)
- **ESG focus for Bestandsgebäude**: Not formal DGNB/BREEAM certification
- **EU Taxonomy alignment**: Primary regulatory framework
- **CRREM for Phase 2**: Industry-standard carbon benchmarking (deferred)
- **SQLite + RefCache**: Persistence with cross-tool reference support
- **Don't implement PDF/Excel tools**: Use dedicated MCP servers for those
- **Phased roadmap**: Phase 1 (basics) → Phase 2 (CRREM) → Phase 3 (measures) → Phase 4 (reports)
- **Analysis-specific requirements** (Session 4): Each analysis type defines its own required/recommended data
- **Tool cleanup** (Session 4): Removed demo/admin tools, keep server focused (15 tools)
- **S3 storage for Phase 4+**: Generated assets (reports, exports) to S3 with RefCache permission integration

## Session Log

### Session 6 - Schema Investigation (2026-01-15)

**Objective**: Fix tool schemas to enable Flowise LLM integration

**Investigation Results**:
1. **Original hypothesis was WRONG** - Schemas already have `required` arrays
2. Verified via Python inspection that FastMCP generates correct JSON schemas:
   - All tools have `required` arrays
   - All properties have `description` fields
   - All properties have `type` declarations
3. The Flowise error is likely caused by:
   - Flowise caching old schemas
   - LLM model not interpreting `required` arrays correctly
   - Flowise MCP connector bug

**Fixes Applied**:
1. ✅ Added `Field()` annotations with descriptions to `get_cached_result`
2. ✅ Added 8 schema validation tests in `TestToolSchemas`
3. ✅ Created `scripts/inspect_schemas.py` for debugging

**Test Results**:
- 132 tests passing (124 original + 8 new schema tests)
- All linting clean

**Files Modified**:
- `app/tools/cache.py` - Added Field() descriptions to get_cached_result
- `tests/test_server.py` - Added TestToolSchemas class (8 tests)
- `scripts/inspect_schemas.py` - NEW: Schema inspection script
- `.agent/goals/05-Tool-Schema-Polish/scratchpad.md` - Documented findings

**Next Steps**:
- Test with Flowise (restart to clear cached schemas)
- If issue persists, check Flowise MCP connector logs
- Release v0.0.3 if needed

---

### Session 4 - Testing & Architecture (2026-01-14)

**Objective**: Test ESG tools, clean up server, add analysis-specific requirements

**Completed**:
1. ✅ Tested full ESG workflow with "Klöpperhaus" building
2. ✅ Fixed bug: "recent data" check too strict (now accepts 2 years)
3. ✅ Tool cleanup: removed 11 demo/admin tools (26 → 15 tools)
4. ✅ Added `AnalysisType` enum and `ANALYSIS_REQUIREMENTS` mapping
5. ✅ Updated `check_data_completeness` to accept optional `analysis_type`
6. ✅ `ready_for_analysis` now means "all required data present"
7. ✅ Documented S3 storage plans for Phase 4+

**Key Decisions**:
- Analysis-specific requirements for extensibility (CRREM, GRESB, etc.)
- S3 storage with mcp-refcache permission integration (future)
- Keep only essential utility tools: `health_check`, `get_cached_result`

**Files Modified**:
- `app/server.py` - Removed demo/admin tool registration
- `app/tools/__init__.py` - Cleaned up exports
- `app/tools/esg.py` - Added analysis-specific completeness check
- `app/models/building.py` - Added AnalysisType, ANALYSIS_REQUIREMENTS
- `tests/test_server.py` - Removed tests for deleted tools

**Next Steps**:
- Publish v0.0.2 to PyPI
- Test with Flowise agents

---

### Session 3 - Phase 1 Implementation (2026-01-14)

**Objective**: Design and implement Phase 1 ESG tools

**Completed**:
1. ✅ Analyzed workflow JSON (general-substainability-workflow-and-screens.json)
2. ✅ Decided: ESG for Bestandsgebäude (not formal DGNB/BREEAM)
3. ✅ Researched EU Taxonomy, CRREM
4. ✅ Designed 4-phase roadmap
5. ✅ Documented Phase 1 data model and tools
6. ✅ Updated Goal 04 scratchpad with full roadmap
7. ✅ **Implemented Phase 1:**
   - Created `app/models/building.py` - Pydantic data models
   - Created `app/store/database.py` - SQLite persistence layer
   - Created `app/tools/esg.py` - 13 ESG tools
   - Updated `app/server.py` - Registered new tools
   - Removed old placeholder sustainability tools
8. ✅ All 92 tests passing, linting clean

**Key Decisions**:
- ESG + EU Taxonomy alignment (not formal certification)
- CRREM pathways deferred to Phase 2
- SQLite for persistence (~/.real-estate-sustainability-mcp/data.db)
- German emission factors (Umweltbundesamt 2023)
- GEG 2024 primary energy factors

**New Files Created**:
- `app/models/__init__.py` - Models package
- `app/models/building.py` - BuildingProject, EnergyData, ConsumptionData, result models
- `app/store/__init__.py` - Store package
- `app/store/database.py` - BuildingStore with SQLite
- `app/tools/esg.py` - 13 ESG assessment tools

**Next Steps**:
- Test tools interactively via MCP (real-estate-sustainability-mcp-dev)
- Write tests for new ESG tools
- Publish v0.0.2 to PyPI

---

### Session 2 - Publishing & Certification Planning (2026-01-14)

**Objective**: Publish to PyPI, set up runner, plan certification tools

**Completed**:
1. ✅ Cleaned up template demo tools (deleted `app/tools/demo.py`)
2. ✅ Fixed all test failures (92 passing)
3. ✅ Published v0.0.0 and v0.0.1 to PyPI
4. ✅ Created GitHub repo with proper CI/CD
5. ✅ Set up self-hosted GitHub Actions runner (Threadripper)
6. ✅ Added generic sustainability tools (placeholder)
7. ✅ Researched DGNB, BREEAM, ESG certification systems

**Discovered**:
- Flowise Docker networking issue (can't reach host localhost)
- Generic tools are NOT German-regulation-compliant
- Need project store for iterative data collection
- Should focus on ONE certification system first

---

### Session 1 - Project Investigation

**Date**: 2026-01-14

**Objective**: Investigate repo state and create goals

**Findings**:
- Project generated from fastmcp-template
- 8 failing tests (demo tools not registered)
- Flowise configured but can't connect (server not running)

---

## Quick Reference

### Commands

```bash
# Install from PyPI
uvx real-estate-sustainability-mcp --version

# Run server (stdio mode)
uv run real-estate-sustainability-mcp stdio

# Run server (HTTP mode for Flowise)
uv run real-estate-sustainability-mcp streamable-http --port 8001

# Run tests
uv run pytest

# Lint
uv run ruff check . --fix && uv run ruff format .

# Build and publish (via GitHub Actions on tag push)
git tag v0.0.2 && git push origin v0.0.2
```

### Key Files

| File | Purpose |
|------|---------|
| `app/server.py` | Main FastMCP server, tool registration |
| `app/tools/sustainability.py` | Sustainability tools (to be replaced) |
| `app/tools/` | Tool modules |
| `pyproject.toml` | Project config, dependencies |
| `tests/test_server.py` | Test suite |
| `.agent/goals/` | Goal tracking |

### Key URLs

| Resource | URL |
|----------|-----|
| PyPI | https://pypi.org/project/real-estate-sustainability-mcp/ |
| GitHub | https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp |
| Flowise Flow | http://localhost:3001/v2/agentcanvas/59b141da-70af-4906-976a-982ad1701526 |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse tracing |
| `LANGFUSE_SECRET_KEY` | Langfuse tracing |
| `LANGFUSE_HOST` | Langfuse host URL |
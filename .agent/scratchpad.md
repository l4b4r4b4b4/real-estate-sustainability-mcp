# Real Estate Sustainability MCP - Agent Scratchpad

## Project Overview

**Purpose**: MCP server for analyzing building sustainability metrics through Excel, PDF, and standardized frameworks (ESG, LEED, BREEAM, DGNB) with IFC integration.

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

### Project State: 🟡 Template Generated, Tools Not Implemented

The project was generated from `fastmcp-template` and contains:
- ✅ Basic FastMCP server structure
- ✅ RefCache integration with Langfuse tracing
- ✅ Demo tools (hello, generate_items, secrets)
- ✅ Test infrastructure (93 passing, 8 failing)
- ✅ Docker configuration
- ✅ GitHub Actions CI/CD
- ❌ **No domain-specific tools implemented yet**

### Test Status

```
8 failed, 93 passed in 3.31s
```

**Failing tests** reference tools not registered in `server.py`:
- `generate_items` - not registered
- `hello` - not registered
- Cache name mismatch in health check

### Integration Target

**Flowise Agent**: `59b141da-70af-4906-976a-982ad1701526`
- Configured to connect to `http://localhost:8001/mcp`
- ReACT-MCP Agent v3.2 ready and waiting

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

## Planned Tool Categories

From README and project description:

| Category | Tools | Priority |
|----------|-------|----------|
| **Core** | health_check, echo/ping | P0 |
| **Excel** | read_excel, analyze_spreadsheet | P1 |
| **PDF** | extract_pdf_text, analyze_pdf | P1 |
| **Frameworks** | check_esg, check_leed, check_breeam, check_dgnb | P2 |
| **IFC** | parse_ifc, extract_building_data | P3 |

## MVP Goals Index

| Goal | Title | Status | Priority |
|------|-------|--------|----------|
| 01 | Fix Existing Tests & Register Demo Tools | ⚪ Not Started | P0 |
| 02 | Minimal Working Server (Health + Echo) | ⚪ Not Started | P0 |
| 03 | Publish v0.0.0 to PyPI | ⚪ Not Started | P0 |
| 04 | Flowise Integration Test | ⚪ Not Started | P1 |
| 05 | Excel Analysis Tools | ⚪ Not Started | P1 |
| 06 | PDF Analysis Tools | ⚪ Not Started | P1 |
| 07 | Sustainability Framework Tools | ⚪ Not Started | P2 |

### Status Indicators
- 🟢 Complete
- 🟡 In Progress
- 🔴 Blocked
- ⚪ Not Started

## Session Log

### Session 1 - Project Investigation

**Date**: Current session

**Objective**: Investigate repo state and create goals

**Findings**:

1. **Project generated from fastmcp-template**
   - Contains full project structure
   - Demo tools exist but not all registered in server.py
   - Tests reference unregistered tools → 8 failures

2. **Server.py analysis**:
   - Registers: context tools, secret tools, cache tools, health_check
   - Missing: `hello`, `generate_items` (exist in tools/ but not registered)
   - Cache name: "real-estate-sustainability-mcp"

3. **Flowise integration ready**:
   - Flow ID: `59b141da-70af-4906-976a-982ad1701526`
   - MCP endpoint configured: `http://localhost:8001/mcp`
   - Tested: Connection refused (server not running)

4. **Version**: 0.0.0 (ready for first release per .rules)

**Next Steps**:
1. Fix failing tests (register missing tools OR update tests)
2. Ensure server runs on port 8001
3. Test with Flowise
4. Publish v0.0.0 to PyPI

---

## Quick Reference

### Commands

```bash
# Run server (stdio mode)
uv run real-estate-sustainability-mcp stdio

# Run server (HTTP mode for Flowise)
uv run real-estate-sustainability-mcp streamable-http --port 8001

# Run tests
uv run pytest

# Lint
uv run ruff check . --fix && uv run ruff format .
```

### Key Files

| File | Purpose |
|------|---------|
| `app/server.py` | Main FastMCP server, tool registration |
| `app/tools/` | Tool modules |
| `pyproject.toml` | Project config, dependencies |
| `tests/test_server.py` | Test suite |
| `.agent/goals/` | Goal tracking |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse tracing |
| `LANGFUSE_SECRET_KEY` | Langfuse tracing |
| `LANGFUSE_HOST` | Langfuse host URL |
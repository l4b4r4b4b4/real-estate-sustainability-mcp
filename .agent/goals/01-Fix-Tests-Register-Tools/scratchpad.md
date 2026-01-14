# Goal 01: Clean Up Template Demo Tools

> **Status**: 🟢 Complete
> **Priority**: P0 (Critical)
> **Created**: 2026-01-14
> **Updated**: 2026-01-14
> **Completed**: 2026-01-14

## Overview

Clean up demo tools (`hello`, `generate_items`) inherited from fastmcp-template. These template-specific tools are not needed for a sustainability analysis server and their presence causes 8 test failures.

## Success Criteria

- [x] All tests pass (92 pass after removing demo tests)
- [x] `uv run pytest` exits with code 0
- [x] Server starts without errors
- [x] Coverage remains ≥73%
- [x] No references to template demo tools remain

## Context & Background

The project was generated from `fastmcp-template`. The template includes demo tools in `app/tools/demo.py` but they are not registered in `app/server.py`. Tests expect these tools to exist, causing failures.

**Failing Tests (8)**:
1. `TestServerInitialization::test_mcp_instance_exists` - expects "FastMCP Template" but is "Real Estate Sustainability Analysis MCP"
2. `TestServerInitialization::test_cache_instance_exists` - expects "fastmcp-template" but is "real-estate-sustainability-mcp"
3. `TestHelloTool::test_hello_default` - hello not registered in server
4. `TestHelloTool::test_hello_custom_name` - hello not registered in server
5. `TestHealthCheck::test_health_check_returns_cache_name` - expects "fastmcp-template"
6. `TestGenerateItems::test_generate_items_default` - generate_items not registered
7. `TestGenerateItems::test_generate_items_custom_params` - generate_items not registered
8. `TestGenerateItems::test_generate_items_large_count` - generate_items not registered

**Root Cause**: Template artifacts that don't match the renamed project.

## Approach

**Option chosen: Clean up template artifacts entirely**

Rather than registering demo tools we don't need, remove them completely:

1. Delete `app/tools/demo.py` (template demo file)
2. Update `app/tools/__init__.py` to remove demo imports
3. Update `app/prompts/__init__.py` to be sustainability-focused
4. Update tests to:
   - Remove `TestHelloTool` class
   - Remove `TestGenerateItems` class
   - Fix name expectations to match actual project names
   - Update prompt tests to not check for hello/generate_items

## Tasks

| Task ID | Description | Status | Depends On |
|---------|-------------|--------|------------|
| Task-01 | Delete `app/tools/demo.py` | 🟢 | - |
| Task-02 | Update `app/tools/__init__.py` (remove demo imports) | 🟢 | Task-01 |
| Task-03 | Update `app/prompts/__init__.py` (sustainability focus) | 🟢 | - |
| Task-04 | Update `tests/test_server.py` (remove demo tests, fix names) | 🟢 | Task-01, Task-02, Task-03 |
| Task-05 | Run full test suite, verify all pass | 🟢 | Task-04 |
| Task-06 | Run linter/formatter | 🟢 | Task-05 |

## Files to Modify

| File | Changes |
|------|---------|
| `app/tools/demo.py` | DELETE |
| `app/tools/__init__.py` | Remove `hello`, `generate_items`, `ItemGenerationInput` |
| `app/prompts/__init__.py` | Remove hello/generate_items references, rename to sustainability guide |
| `tests/test_server.py` | Remove TestHelloTool, TestGenerateItems; fix name expectations |

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing tools | High | Low | Only touching demo tools, not cache/secret tools |
| Missing imports | Medium | Medium | Run tests after each file change |

## Notes & Decisions

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-14 | Remove demo tools instead of registering | Cleaner codebase, no unused code |
| 2026-01-14 | Rename prompts to sustainability focus | Project-specific branding |

### Open Questions

- [x] Should demo tools remain? **No - remove them**

## Completion Summary

**Date**: 2026-01-14

**What was done**:
1. Deleted `app/tools/demo.py` (hello, generate_items)
2. Updated `app/tools/__init__.py` to remove demo imports
3. Updated `app/prompts/__init__.py` with sustainability-focused content
4. Updated `app/tools/health.py` to use correct server name
5. Updated `tests/test_server.py`:
   - Removed `TestHelloTool` class
   - Removed `TestGenerateItems` class
   - Removed `ItemGenerationInput` Pydantic tests
   - Fixed name expectations to "Real Estate Sustainability Analysis MCP"
   - Fixed cache name to "real-estate-sustainability-mcp"
   - Renamed `TestTemplateGuidePrompt` to `TestSustainabilityGuidePrompt`
6. Ran linter and formatter

**Results**:
- 92 tests passing (was 93 pass + 8 fail = 101 total, now 92 pass after removing 9 demo-related tests)
- All linting passes
- Clean codebase with no template artifacts

## References

- `app/tools/demo.py` - Demo tool implementations (to delete)
- `app/server.py` - Current tool registration
- `tests/test_server.py` - Failing tests
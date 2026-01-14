# Goal 05: Tool Schema Polish for MCP/LLM Compatibility

> **Status**: 🟢 Complete (investigation done, fixes applied)
> **Priority**: P0 (Blocking Flowise integration)
> **Created**: 2026-01-14
> **Updated**: 2026-01-15

## Problem Statement

~~The ESG tools are missing proper JSON schema annotations that LLMs need to call them correctly.~~

**UPDATE (Session 6):** Investigation revealed the schemas are **already correct**. The MCP server generates proper JSON schemas with all required fields, descriptions, and types.

### Original Hypothesis (DISPROVEN)
~~1. Missing `required` fields - LLMs don't know which parameters are mandatory~~
~~2. Missing property descriptions - LLMs can't understand what each field means~~
~~3. Inconsistent type annotations - Some fields lack explicit types~~

### Actual Finding
The MCP server generates correct schemas. Example for `create_building_project`:
```json
{
  "inputSchema": {
    "properties": {
      "name": { "description": "Name or identifier for the building", "type": "string" },
      "floor_area_sqm": { "description": "Net floor area in m²", "exclusiveMinimum": 0, "type": "number" },
      "construction_year": { "description": "Year built", "minimum": 1800, "maximum": 2030, "type": "integer" },
      ...
    },
    "required": ["name", "floor_area_sqm", "construction_year"],
    "type": "object"
  }
}
```

### Revised Problem Statement
The Flowise agent error:
```
1 validation error for call[create_building_project]
construction_year
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
```

Possible causes (need investigation):
1. **Flowise schema caching** - May have cached an older schema before Field() annotations existed
2. **LLM model issue** - Some models don't properly interpret JSON Schema `required` arrays
3. **Flowise MCP integration bug** - May not be passing schemas correctly to the LLM
4. **Version mismatch** - Flowise may be connecting to wrong server instance

## Success Criteria

- [x] All tools have explicit `required` arrays in their JSON schemas ✅ (already done)
- [x] All properties have `description` fields ✅ (fixed `get_cached_result`)
- [x] All properties have explicit `type` declarations ✅ (already done)
- [x] Fix `get_cached_result` missing descriptions ✅
- [x] Add schema validation tests ✅ (8 new tests)
- [x] Create debug/inspection script ✅ (`scripts/inspect_schemas.py`)
- [ ] Diagnose Flowise integration issue (needs Flowise testing)
- [ ] Flowise agent can successfully call all ESG tools (needs user verification)
- [ ] v0.0.3 published to PyPI (optional, depends on Flowise testing)

## Schema Audit Results (Session 6)

All ESG tools already have correct schemas. Verified via Python inspection:

```
Tool Schema Summary:
============================================================
create_building_project:     required: [name, floor_area_sqm, construction_year] ✅
add_energy_data:             required: [project_id, year, consumption_kwh] ✅
add_consumption_data:        required: [project_id, year, category, value, unit] ✅
calculate_energy_intensity:  required: [project_id] ✅
calculate_carbon_footprint:  required: [project_id] ✅
check_eu_taxonomy_alignment: required: [project_id] ✅
check_data_completeness:     required: [project_id] ✅
suggest_data_sources:        required: [project_id] ✅
get_building_project:        required: [project_id] ✅
update_building_project:     required: [project_id] ✅
delete_building_project:     required: [project_id] ✅
get_project_data:            required: [project_id] ✅
list_building_projects:      required: [none] ✅
health_check:                required: [none] ✅
get_cached_result:           required: [ref_id] ✅ (but missing descriptions ⚠️)
```

### Only Issue Found
`get_cached_result` is missing `description` fields for its parameters:
- `ref_id` - no description
- `page` - no description
- `page_size` - no description
- `max_size` - no description

## Technical Approach

### Option A: Pydantic Field() with json_schema_extra
```python
from pydantic import Field

def create_building_project(
    name: str = Field(..., description="Name of the building project"),
    floor_area_sqm: float = Field(..., gt=0, description="Net floor area in m²"),
    construction_year: int = Field(..., ge=1800, le=2030, description="Year built"),
    building_type: str = Field(default="office", description="Building type"),
) -> dict[str, Any]:
    ...
```

### Option B: Custom schema override in FastMCP
Check if FastMCP/mcp-refcache supports schema customization.

### Option C: Wrapper models with explicit schema
Create Pydantic input models with proper schema generation.

## Implementation Plan

### Task 1: Audit Current Schemas
- [ ] Export current tool schemas from MCP server
- [ ] Document which fields are missing required/descriptions
- [ ] Map Pydantic model fields to tool parameters

### Task 2: Update Tool Definitions
- [ ] Update `app/tools/esg.py` with proper Field() annotations
- [ ] Update `app/models/building.py` if needed
- [ ] Ensure all required fields use `...` (Ellipsis) as default

### Task 3: Test Schema Generation
- [ ] Write test to verify JSON schema output
- [ ] Test with MCP inspector or Flowise
- [ ] Verify LLM can call tools without errors

### Task 4: Release v0.0.3
- [ ] Update CHANGELOG.md
- [ ] Bump version to 0.0.3
- [ ] Create PR, merge, tag, release

## Files to Modify

| File | Changes |
|------|---------|
| `app/tools/esg.py` | Add Field() with descriptions to all tool parameters |
| `app/models/building.py` | Verify Create models have proper Field() annotations |
| `tests/test_esg.py` | Add schema validation tests |
| `pyproject.toml` | Bump version |
| `CHANGELOG.md` | Document changes |

## Research Notes

### FastMCP Schema Generation
Need to check how FastMCP generates JSON schemas from function signatures:
- Does it respect Pydantic Field() metadata?
- Does it auto-generate `required` from parameters without defaults?
- Can we override the schema manually?

### MCP Protocol Schema Requirements
From MCP spec, tool schemas should include:
- `name`: Tool name
- `description`: What the tool does
- `inputSchema`: JSON Schema object with:
  - `type`: "object"
  - `properties`: Field definitions with type/description
  - `required`: Array of required field names

## Session Log

### Session 6 (2026-01-15)
**Investigation Results:**

1. **Audited tool schemas** - All ESG tools have correct `required` arrays and descriptions
2. **Verified MCP protocol output** - `to_mcp_tool()` returns complete JSON schemas
3. **Found one issue** - `get_cached_result` missing descriptions (minor)
4. **Disproven original hypothesis** - Schema generation is NOT the problem

**Fixes Applied:**

1. ✅ Added `Field()` annotations with descriptions to `get_cached_result` in `app/tools/cache.py`
2. ✅ Added 8 schema validation tests in `tests/test_server.py::TestToolSchemas`:
   - `test_create_building_project_has_required`
   - `test_add_energy_data_has_required`
   - `test_add_consumption_data_has_required`
   - `test_analysis_tools_have_required_project_id`
   - `test_all_properties_have_descriptions`
   - `test_all_properties_have_types`
   - `test_get_cached_result_has_required`
   - `test_mcp_tool_output_has_input_schema`
3. ✅ Created `scripts/inspect_schemas.py` for debugging:
   - `uv run python scripts/inspect_schemas.py --summary` - Shows all tool schemas
   - `uv run python scripts/inspect_schemas.py --tool create_building_project` - Single tool
   - `uv run python scripts/inspect_schemas.py --all` - Full JSON output

**Test Results:**
- 132 tests passing (124 original + 8 new schema tests)
- All linting passes

**Remaining Work (needs user testing):**
1. Test with Flowise to verify the issue is resolved
2. If issue persists, try:
   - Restart Flowise to clear cached schemas
   - Check Flowise MCP connector logs
   - Try different LLM model in Flowise
3. Release v0.0.3 if Flowise testing confirms fix

---

## Related

- Goal 04: ESG Assessment Implementation (Phase 1 complete)
- Issue: Flowise agent can't call tools correctly
- v0.0.2: Published but has schema issues
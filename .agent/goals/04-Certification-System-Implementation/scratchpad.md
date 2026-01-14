# Goal 04: ESG Assessment for Bestandsgebäude (Existing Buildings)

> **Status**: 🟡 Phase 1 Complete - Testing in Progress
> **Priority**: P1 (High)
> **Created**: 2026-01-14
> **Updated**: 2026-01-14 (Session 4)

## Overview

Implement ESG assessment tooling for existing commercial real estate buildings (Bestandsgebäude). Focus on practical, agent-driven workflows for asset managers to assess sustainability status, identify data gaps, plan measures, and compare against benchmarks.

Based on the 9-step storyboard workflow from `general-substainability-workflow-and-screens.json`.

## Success Criteria

- [x] Project store with SQLite persistence (RefCache-backed)
- [x] Data collection tools for building information
- [x] Data gap analysis (what documents/data are missing?)
- [x] EU Taxonomy alignment check for buildings
- [x] Simple carbon footprint calculation
- [x] Analysis-specific requirements system (Session 4)
- [x] Tool cleanup - removed demo/admin tools (Session 4)
- [x] Interactive testing of ESG tools (Session 4)
- [ ] Integration tested with Flowise agent
- [ ] Tests written for new ESG tools

## Phased Implementation Roadmap

### Phase 1: Simple ESG Status ✅ IMPLEMENTED

**Goal:** Get a working prototype that can be used in Flowise agents

**Scope:**
1. **Project Store** (SQLite + RefCache)
   - `create_building_project(name, address, building_type, floor_area, construction_year)`
   - `get_building_project(project_id)`
   - `update_building_project(project_id, **updates)`
   - `list_building_projects()`
   - `delete_building_project(project_id)`

2. **Data Collection Tools**
   - `add_energy_data(project_id, year, consumption_kwh, source)`
   - `add_consumption_data(project_id, category, value, unit, year)`
   - `get_project_data(project_id)` → all collected data

3. **Gap Analysis**
   - `check_data_completeness(project_id)` → missing required data, quality issues
   - `suggest_data_sources(project_id)` → what documents to collect

4. **Simple ESG Analysis**
   - `calculate_energy_intensity(project_id)` → kWh/m²/a
   - `calculate_carbon_footprint(project_id)` → kgCO2/m²/a
   - `check_eu_taxonomy_alignment(project_id)` → is building below threshold?

**EU Taxonomy Thresholds (Climate Mitigation - Existing Buildings):**
- Office: < 100 kWh/m²/a primary energy OR top 15% of national stock
- Residential: < 100 kWh/m²/a primary energy OR EPC class A
- Retail: varies by climate zone

**Data Model (Phase 1):**
```python
class BuildingProject:
    project_id: str  # UUID
    name: str
    address: str
    building_type: Literal["office", "residential", "retail", "mixed", "industrial"]
    floor_area_sqm: float  # NRF/NGF
    construction_year: int
    renovation_year: Optional[int]
    created_at: datetime
    updated_at: datetime

class EnergyData:
    project_id: str
    year: int
    consumption_kwh: float
    source: Literal["utility_bill", "smart_meter", "estimate", "benchmark"]
    energy_type: Literal["electricity", "gas", "district_heating", "oil", "other"]

class ConsumptionData:
    project_id: str
    category: Literal["water", "waste", "tenant_electricity"]
    value: float
    unit: str
    year: int
    source: str
```

---

### Phase 2: CRREM Pathway Integration (Future)

**Goal:** Add industry-standard carbon trajectory benchmarking

**Scope:**
1. **CRREM Pathways**
   - `get_crrem_pathway(country, building_type, scenario)` → pathway data
   - `calculate_stranding_year(project_id, scenario)` → when does building strand?
   - `compare_to_crrem(project_id)` → current position vs 1.5°C and 2°C pathways

2. **Scenario Modeling**
   - `create_scenario(project_id, name, measures[])`
   - `evaluate_scenario(project_id, scenario_id)` → impact on trajectory
   - `compare_scenarios(project_id, scenario_ids[])`

3. **Visualization Data**
   - `get_trajectory_chart_data(project_id)` → data for CRREM-style charts

**CRREM Data Required:**
- Country-specific pathways (Germany, EU, etc.)
- Building type categories (Office, Retail, Hotel, Residential, Industrial, etc.)
- 1.5°C and 2°C scenarios
- kgCO2/m²/a thresholds by year (2020-2050)

**Sources:**
- CRREM publishes Excel-based pathways: https://www.crrem.eu/
- CRREM Risk Assessment Tool (reference)

---

### Phase 3: Measure Planning & Optimization (Future)

**Goal:** Help asset managers prioritize sustainability measures

**Scope:**
1. **Measure Library**
   - `list_available_measures(building_type)` → common measures
   - `get_measure_details(measure_id)` → costs, savings, CO2 reduction

2. **Measure Evaluation**
   - `estimate_measure_impact(project_id, measure_id)` → ROI, payback, CO2 savings
   - `add_planned_measure(project_id, measure_id, year, budget)`

3. **Optimization**
   - `suggest_measures(project_id, budget, target_year)` → recommended measures
   - `generate_renovation_roadmap(project_id)` → phased implementation plan

**Common Measures Database:**
- LED lighting upgrade
- HVAC optimization/replacement
- Building envelope (windows, insulation)
- Solar PV installation
- Heat pump conversion
- Smart building controls
- Green roof/facade

---

### Phase 4: Reporting & Export (Future)

**Goal:** Generate outputs for stakeholders

**Scope:**
1. **ESG Summary Reports**
   - `generate_esg_summary(project_id, audience)` → for investors, management, tenants
   - `export_report(project_id, format)` → PDF, Excel, JSON

2. **Regulatory Reporting**
   - `generate_taxonomy_disclosure(project_id)` → EU Taxonomy Article 8 data
   - `generate_sfdr_data(project_id)` → SFDR PAI indicators

3. **Portfolio Features**
   - `aggregate_portfolio(project_ids[])` → portfolio-level metrics
   - `compare_buildings(project_ids[])` → side-by-side comparison

---

## Workflow Alignment (9-Step Storyboard)

| Step | Workflow Stage | Phase 1 Tools |
|------|----------------|---------------|
| 1-3 | Opening, Overview, Intent | `create_building_project`, `get_building_project` |
| 4 | Document Intake & Gaps | `check_data_completeness`, `suggest_data_sources` |
| 5 | ESG Status & Validation | `calculate_energy_intensity`, `calculate_carbon_footprint`, `check_eu_taxonomy_alignment` |
| 6 | Measures Identification | (Phase 3) |
| 7 | Strategy & Benchmarking | (Phase 2: CRREM) |
| 8-9 | Results & Feedback | (Phase 4: Reports) |

---

## Technical Decisions

### Storage: SQLite + RefCache

**Why SQLite:**
- Persistence beyond session
- Simple, no external dependencies
- Easy to migrate to Redis later
- Good for demo/prototype

**RefCache Integration:**
- Project IDs are RefCache references
- Large results paginated via RefCache
- Cross-tool references possible (future: other MCP servers)

**Database Location:**
- Default: `~/.real-estate-sustainability-mcp/data.db`
- Configurable via `DATABASE_PATH` env var

### Emission Factors

**German Grid Mix (2023):**
- Electricity: 380 gCO2/kWh (Umweltbundesamt)
- Gas: 201 gCO2/kWh
- District heating: varies by provider (~200-300 gCO2/kWh)
- Oil: 266 gCO2/kWh

**Primary Energy Factors (GEG 2024):**
- Electricity (grid): 1.8
- Gas: 1.1
- District heating: 0.7 (varies)
- Oil: 1.1

### EU Taxonomy Technical Criteria

**Activity 7.7: Acquisition and ownership of buildings**

For existing buildings to be taxonomy-aligned (climate mitigation):

1. **Energy Performance Certificate (EPC) Class A**, OR
2. **Top 15% of national building stock** in terms of primary energy demand, OR
3. **Primary energy demand < 100 kWh/m²/a** (for non-residential)

Plus: Do No Significant Harm (DNSH) criteria for other objectives.

---

## Dependencies

- **Upstream**: 
  - Goal 01-03 complete ✅
  - Server published to PyPI ✅
  
- **External (not needed for Phase 1)**:
  - PDF MCP - for document parsing
  - Excel MCP - for spreadsheet data
  - IFC MCP - for BIM data

---

## Tasks (Phase 1)

| Task ID | Description | Status | Depends On |
|---------|-------------|--------|------------|
| Task-01 | Design data model (Pydantic) | ✅ Complete | - |
| Task-02 | Implement SQLite store | ✅ Complete | Task-01 |
| Task-03 | Implement project CRUD tools | ✅ Complete | Task-02 |
| Task-04 | Implement data collection tools | ✅ Complete | Task-03 |
| Task-05 | Implement gap analysis | ✅ Complete | Task-04 |
| Task-06 | Implement ESG analysis tools | ✅ Complete | Task-04 |
| Task-07 | Write tests | ⚪ Next | Task-03-06 |
| Task-08 | Test with Flowise | 🟡 In Progress | Task-07 |

### Files Implemented (Session 3)

| File | Purpose |
|------|---------|
| `app/models/__init__.py` | Models package exports |
| `app/models/building.py` | Pydantic models: BuildingProject, EnergyData, ConsumptionData, result types |
| `app/store/__init__.py` | Store package exports |
| `app/store/database.py` | SQLite BuildingStore with CRUD operations |
| `app/tools/esg.py` | 13 ESG assessment tools |

### Tools Implemented

| Tool | Category | Description |
|------|----------|-------------|
| `create_building_project` | Project Store | Create new building for ESG assessment |
| `get_building_project` | Project Store | Get project with all related data |
| `update_building_project` | Project Store | Update building details |
| `list_building_projects` | Project Store | List all projects with pagination |
| `delete_building_project` | Project Store | Delete project and all data |
| `add_energy_data` | Data Collection | Add annual energy consumption |
| `add_consumption_data` | Data Collection | Add water, waste, etc. |
| `get_project_data` | Data Collection | Get all collected data |
| `check_data_completeness` | Gap Analysis | Check what data is missing |
| `suggest_data_sources` | Gap Analysis | Suggest documents to collect |
| `calculate_energy_intensity` | ESG Analysis | Calculate kWh/m²/a + rating |
| `calculate_carbon_footprint` | ESG Analysis | Calculate kgCO2/m²/a |
| `check_eu_taxonomy_alignment` | ESG Analysis | Check Activity 7.7 alignment |

---

## Session 4 Progress (2026-01-14)

### Tool Cleanup ✅

Removed 11 demo/admin tools inherited from mcp-refcache template:
- `store_secret`, `compute_with_secret` (demo tools)
- `enable_test_context`, `set_test_context`, `reset_test_context`, `get_trace_info` (context management)
- 5 `admin_*` tools (cache administration)

**Kept**: `health_check`, `get_cached_result` (essential utilities)

**Result**: 26 tools → 15 tools (13 ESG + 2 utility)

### Analysis-Specific Requirements ✅

Added framework for analysis-specific data validation:

```python
class AnalysisType(Enum):
    ENERGY_INTENSITY = "energy_intensity"
    CARBON_FOOTPRINT = "carbon_footprint"
    EU_TAXONOMY = "eu_taxonomy"
    CRREM = "crrem"  # Future
    GRESB = "gresb"  # Future

ANALYSIS_REQUIREMENTS = {
    AnalysisType.ENERGY_INTENSITY: AnalysisRequirements(
        required=("floor_area", "energy_data"),
        recommended=("recent_energy_data",),
    ),
    AnalysisType.EU_TAXONOMY: AnalysisRequirements(
        required=("floor_area", "energy_data", "building_type"),
        recommended=("epc_rating", "recent_energy_data"),
    ),
    # ... more analysis types
}
```

**Updated `check_data_completeness`**:
- Now accepts optional `analysis_type` parameter
- Returns requirements specific to that analysis
- `ready_for_analysis` = all required data present (not just score >= X%)
- Easy to extend for CRREM, GRESB, etc.

### Interactive Testing ✅

Tested full ESG workflow:
1. Created "Klöpperhaus" project (Hamburg office, 15,000 m²)
2. Added energy data (electricity + district heating for 2023/2024)
3. Check data completeness → 90% ✅
4. Energy intensity → 168 kWh/m²/a (Rating E)
5. Carbon footprint → 57.12 kgCO₂/m²/a
6. EU Taxonomy → NOT aligned (gap: 149.6 kWh/m²/a)

**Bug Fixed**: "Recent data" check was too strict (expected 2025/2026, but 2024 is reasonable). Changed to accept data from last 2 years.

---

## Future: S3 Storage for Generated Assets

### Concept

Generated assets (reports, presentations, exports) should be stored persistently in S3-compatible storage, not just returned as tool results.

### S3 Integration Design (Future Phase 4+)

**Storage Concepts**:
- **Bucket**: Top-level container (e.g., `esg-reports-prod`)
- **Prefix/Namespace**: Logical grouping within bucket (e.g., `projects/{project_id}/reports/`)
- **Object Key**: Full path to file (e.g., `projects/abc-123/reports/2024-taxonomy-disclosure.pdf`)

**Proposed Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│  MCP Tool: generate_esg_report()                        │
│  └── Returns: S3 URL + RefCache reference               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  S3 Storage (MinIO / AWS S3 / Cloudflare R2)            │
│  ├── Bucket: esg-reports                                │
│  │   ├── projects/{project_id}/reports/                 │
│  │   ├── projects/{project_id}/exports/                 │
│  │   └── portfolios/{portfolio_id}/                     │
│  └── Access via presigned URLs                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  RefCache Permission Integration                         │
│  ├── S3 object reference stored in RefCache             │
│  ├── Permissions: READ, DOWNLOAD, SHARE                 │
│  └── User/Org scoping via namespace                     │
└─────────────────────────────────────────────────────────┘
```

**Permission Model**:
- Integrate with mcp-refcache `AccessPolicy` system
- User-scoped: `user:{user_id}:reports`
- Org-scoped: `org:{org_id}:projects:{project_id}`
- Time-limited presigned URLs for downloads

**Asset Types**:
| Asset Type | Format | Storage Path |
|------------|--------|--------------|
| ESG Summary Report | PDF | `projects/{id}/reports/esg-summary-{date}.pdf` |
| EU Taxonomy Disclosure | PDF/JSON | `projects/{id}/reports/taxonomy-{year}.pdf` |
| CRREM Chart | PNG/SVG | `projects/{id}/charts/crrem-pathway.png` |
| Data Export | Excel/CSV | `projects/{id}/exports/energy-data-{date}.xlsx` |
| Portfolio Report | PDF | `portfolios/{id}/reports/annual-{year}.pdf` |

**Implementation Notes**:
- Use `boto3` or `aioboto3` for S3 operations
- Support multiple backends: AWS S3, MinIO (self-hosted), Cloudflare R2
- Environment config: `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- Generate presigned URLs with configurable expiry (default: 1 hour)

---

## Notes & Decisions

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-14 | Focus on ESG for Bestandsgebäude, not formal certification | Matches workflow JSON, simpler to implement |
| 2026-01-14 | Use SQLite for persistence | Simple, no dependencies, easy migration |
| 2026-01-14 | EU Taxonomy as primary regulatory framework | Most relevant for ESG/investor reporting |
| 2026-01-14 | CRREM deferred to Phase 2 | Get basics working first |
| 2026-01-14 | Phased roadmap approved | Phase 1 → 2 → 3 → 4 |
| 2026-01-14 | German emission factors (Umweltbundesamt 2023) | Most accurate for German market |
| 2026-01-14 | GEG 2024 primary energy factors | Current German regulation |
| 2026-01-14 | Removed old placeholder sustainability tools | Replaced with proper ESG implementation |
| 2026-01-14 | Analysis-specific requirements system | Each analysis type defines its own required/recommended data |
| 2026-01-14 | Removed demo/admin tools from server | Keep server focused on ESG, 15 tools total |
| 2026-01-14 | S3 storage planned for Phase 4+ | Generated assets need persistent storage with permissions |

### Open Questions

- [x] Which certification system? → ESG + EU Taxonomy (not DGNB/BREEAM)
- [x] CRREM needed? → Yes, but Phase 2
- [x] Analysis-specific requirements? → AnalysisType enum + ANALYSIS_REQUIREMENTS mapping
- [ ] Specific emission factors source? (Umweltbundesamt vs GEMIS vs custom)
- [ ] Multi-tenant data handling? (scope 3 tenant emissions)
- [ ] S3 backend choice? (AWS S3 vs MinIO vs Cloudflare R2)
- [ ] Permission model for shared assets across organizations?

---

## References

- EU Taxonomy Navigator: https://ec.europa.eu/sustainable-finance-taxonomy/
- EU Taxonomy Regulation: https://eur-lex.europa.eu/eli/reg/2020/852/oj
- CRREM Project: https://www.crrem.eu/
- GEG (Gebäudeenergiegesetz): https://www.gesetze-im-internet.de/geg/
- Umweltbundesamt CO2 Emissionsfaktoren: https://www.umweltbundesamt.de/
- GRESB: https://www.gresb.com/
- SFDR: https://finance.ec.europa.eu/sustainable-finance/disclosures_en
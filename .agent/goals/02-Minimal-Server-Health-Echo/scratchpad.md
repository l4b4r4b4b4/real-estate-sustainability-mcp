# Goal 02: Minimal Working Server (Health + Echo)

> **Status**: 🟢 Complete
> **Priority**: P0 (Critical)
> **Created**: 2026-01-14
> **Updated**: 2026-01-14
> **Completed**: 2026-01-14

## Overview

Ensure the MCP server starts correctly on port 8001 with streamable HTTP transport and exposes basic connectivity tools that Flowise can call to verify the integration works.

## Success Criteria

- [x] Server starts with `uv run real-estate-sustainability-mcp streamable-http --port 8001`
- [x] `health_check` tool responds with server status
- [x] Sustainability tools implemented (calculate_energy_rating, carbon_footprint, etc.)
- [ ] Flowise agent can successfully call at least one tool (blocked - needs Docker networking)
- [x] No errors in server logs during basic operation

## Context & Background

The Flowise ReACT-MCP Agent (flow ID: `59b141da-70af-4906-976a-982ad1701526`) is configured to connect to `http://localhost:8001/mcp`. We need to verify the server runs correctly on this endpoint before adding domain-specific tools.

**Current state**:
- Server code exists but hasn't been tested with Flowise
- `health_check` tool is registered
- Need simple echo/ping for connectivity testing

## Constraints & Requirements

- **Hard Requirements**: 
  - Must run on port 8001
  - Must use streamable HTTP transport (not stdio)
  - Must be compatible with Flowise MCP client
- **Soft Requirements**: 
  - Fast startup time
  - Minimal dependencies for first test
- **Out of Scope**: 
  - Document analysis tools (Goal 05+)
  - PyPI publishing (Goal 03)

## Approach

1. Start server locally on port 8001
2. Test with curl to verify MCP endpoint responds
3. Test with Flowise agent
4. Add simple `echo` tool if needed for debugging

## Tasks

| Task ID | Description | Status | Depends On |
|---------|-------------|--------|------------|
| Task-01 | Start server on port 8001, check for errors | 🟢 | Goal-01 |
| Task-02 | Test MCP endpoint with curl | 🟢 | Task-01 |
| Task-03 | Test health_check from Flowise | 🔴 Blocked | Task-02 |
| Task-04 | Add sustainability tools | 🟢 | - |
| Task-05 | Document findings | 🟢 | Task-04 |

**Note**: Task-03 blocked because Flowise runs in Docker container, cannot reach host localhost:8001. Solution: Add MCP server to same Docker Compose network as Flowise.

## Test Commands

```bash
# Start server
uv run real-estate-sustainability-mcp streamable-http --port 8001

# Test endpoint exists (in another terminal)
curl http://localhost:8001/mcp

# Test with Flowise
FLOW_ID="59b141da-70af-4906-976a-982ad1701526"
curl -X POST "http://localhost:3001/api/v1/prediction/${FLOW_ID}" \
  -H "Content-Type: application/json" \
  -d '{"question": "What tools are available?", "sessionId": "test-1"}'
```

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Port conflict | Medium | Low | Check port availability first |
| MCP protocol mismatch | High | Medium | Test with curl before Flowise |
| Flowise auth issues | Medium | Medium | Check Flowise API key config |

## Dependencies

- **Upstream**: Goal-01 (tests passing, server starts cleanly)
- **Downstream**: Goal-03 (PyPI publish), Goal-04 (full Flowise integration)

## Notes & Decisions

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| - | Use streamable-http not SSE | Flowise configured for this transport |
| - | Port 8001 | Matches Flowise agent config |

### Open Questions

- [ ] Does Flowise need any special headers for MCP calls?
- [ ] Should we add request logging for debugging?

## Completion Summary

**Date**: 2026-01-14

### What was done:
1. Server starts successfully on port 8001 with streamable-http transport
2. Added 5 sustainability analysis tools (though generic, not German-regulation-compliant)
3. Published v0.0.0 and v0.0.1 to PyPI
4. Set up self-hosted GitHub Actions runner on Threadripper workstation
5. Discovered Flowise Docker networking issue

### Blocker discovered:
Flowise runs in Docker container - `localhost:8001` from inside container doesn't reach host.

**Solution for next session**: Add MCP server container to same Docker Compose network as Flowise, use service name for connectivity.

### Tools implemented (to be replaced with proper German certification tools):
- `calculate_energy_rating` - Generic A-G rating (needs GEG compliance)
- `calculate_carbon_footprint` - CO2 estimation
- `sustainability_score` - Overall score 0-100
- `suggest_improvements` - Recommendations
- `compare_buildings` - Multi-building comparison

## References

- Flowise Flow: http://localhost:3001/v2/agentcanvas/59b141da-70af-4906-976a-982ad1701526
- MCP configured at: `http://localhost:8001/mcp`
- FastMCP docs: https://github.com/jlowin/fastmcp
- PyPI: https://pypi.org/project/real-estate-sustainability-mcp/
- GitHub: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp
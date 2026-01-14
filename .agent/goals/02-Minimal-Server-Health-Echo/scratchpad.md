# Goal 02: Minimal Working Server (Health + Echo)

> **Status**: 🟡 In Progress
> **Priority**: P0 (Critical)
> **Created**: 2026-01-14
> **Updated**: 2026-01-14

## Overview

Ensure the MCP server starts correctly on port 8001 with streamable HTTP transport and exposes basic connectivity tools that Flowise can call to verify the integration works.

## Success Criteria

- [ ] Server starts with `uv run real-estate-sustainability-mcp streamable-http --port 8001`
- [ ] `health_check` tool responds with server status
- [ ] `echo` or `ping` tool responds to verify MCP protocol works
- [ ] Flowise agent can successfully call at least one tool
- [ ] No errors in server logs during basic operation

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
| Task-01 | Start server on port 8001, check for errors | ⚪ | Goal-01 |
| Task-02 | Test MCP endpoint with curl | ⚪ | Task-01 |
| Task-03 | Test health_check from Flowise | ⚪ | Task-02 |
| Task-04 | Add echo/ping tool if needed | ⚪ | Task-03 |
| Task-05 | Document successful connection | ⚪ | Task-03 |

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

## References

- Flowise Flow: http://localhost:3001/v2/agentcanvas/59b141da-70af-4906-976a-982ad1701526
- MCP configured at: `http://localhost:8001/mcp`
- FastMCP docs: https://github.com/jlowin/fastmcp
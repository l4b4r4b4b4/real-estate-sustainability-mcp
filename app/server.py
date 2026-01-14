"""Real Estate Sustainability Analysis MCP - FastMCP Server with RefCache and Langfuse Tracing.

This module creates and configures the FastMCP server, wiring together
tools from the modular tools package.

Features:
- Reference-based caching for large results
- Preview generation (sample, truncate, paginate strategies)
- Pagination for accessing large datasets
- Access control (user vs agent permissions)
- Private computation (EXECUTE without READ)

- Langfuse tracing integration for observability


Usage:
    # Run with typer CLI
    uvx real-estate-sustainability-mcp stdio           # Local CLI mode
    uvx real-estate-sustainability-mcp streamable-http # Remote/Docker mode

    # Or with uv
    uv run real-estate-sustainability-mcp stdio
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from mcp_refcache import PreviewConfig, PreviewStrategy, RefCache
from mcp_refcache.fastmcp import cache_instructions, register_admin_tools

from app.prompts import langfuse_guide, template_guide
from app.tools import (
    create_compute_with_secret,
    create_get_cached_result,
    create_health_check,
    create_store_secret,
    enable_test_context,
    get_trace_info,
    reset_test_context,
    set_test_context,
)
from app.tracing import TracedRefCache

# =============================================================================
# Initialize FastMCP Server
# =============================================================================

mcp = FastMCP(
    name="Real Estate Sustainability Analysis MCP",
    instructions=f"""MCP server for analyzing building sustainability metrics through Excel, PDF, and standardized frameworks (ESG, LEED, BREEAM, DGNB) with IFC integration


All tool calls are traced to Langfuse with:
- User ID and Session ID from context (for filtering/aggregation)
- Full context metadata (org_id, agent_id, cache_namespace)
- Cache operation spans with hit/miss tracking

Enable test mode with enable_test_context() to simulate different users.


Available tools:

- store_secret: Store a secret value for private computation
- compute_with_secret: Use a secret in computation without revealing it
- get_cached_result: Retrieve or paginate through cached results

- enable_test_context: Enable/disable test context for Langfuse demos
- set_test_context: Set test context values for user attribution
- reset_test_context: Reset test context to defaults
- get_trace_info: Get current Langfuse tracing status


{cache_instructions()}
""",
)

# =============================================================================
# Initialize RefCache with Langfuse Tracing

# =============================================================================

# Create the base RefCache instance
_cache = RefCache(
    name="real-estate-sustainability-mcp",
    default_ttl=3600,  # 1 hour TTL
    preview_config=PreviewConfig(
        max_size=2048,  # Max 2048 tokens in previews
        default_strategy=PreviewStrategy.SAMPLE,  # Sample large collections
    ),
)


# Wrap with TracedRefCache for Langfuse observability
cache = TracedRefCache(_cache)


# =============================================================================
# Create Bound Tool Functions
# =============================================================================

# These are created with factory functions and bound to the cache instance.
# We keep references for testing and re-export them as module attributes.
store_secret = create_store_secret(cache)
compute_with_secret = create_compute_with_secret(cache)
get_cached_result = create_get_cached_result(cache)
health_check = create_health_check(_cache)

# =============================================================================
# Register Tools
# =============================================================================


# Context management tools
mcp.tool(enable_test_context)
mcp.tool(set_test_context)
mcp.tool(reset_test_context)
mcp.tool(get_trace_info)


# Cache-bound tools (using pre-created module-level functions)
mcp.tool(store_secret)
mcp.tool(compute_with_secret)
mcp.tool(get_cached_result)
mcp.tool(health_check)

# =============================================================================
# Admin Tools (Permission-Gated)
# =============================================================================


async def is_admin(ctx: Any) -> bool:
    """Check if the current context has admin privileges.

    Override this in your own server with proper auth logic.
    """
    # Demo: No admin access by default
    return False


# Register admin tools with the underlying cache (not the traced wrapper)
_admin_tools = register_admin_tools(
    mcp,
    _cache,
    admin_check=is_admin,
    prefix="admin_",
    include_dangerous=False,
)

# =============================================================================
# Register Prompts
# =============================================================================


@mcp.prompt
def _template_guide() -> str:
    """Guide for using this MCP server template."""
    return template_guide()


@mcp.prompt
def _langfuse_guide() -> str:
    """Guide for using Langfuse tracing with this server."""
    return langfuse_guide()

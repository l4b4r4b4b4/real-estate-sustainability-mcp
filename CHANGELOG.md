# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Excel spreadsheet analysis for sustainability data
- PDF parsing for building reports and certifications
- ESG (Environmental, Social, Governance) scoring tools
- LEED certification analysis
- BREEAM assessment tools
- DGNB evaluation tools
- IFC file parsing for building information modeling

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

[Unreleased]: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp/compare/v0.0.0...HEAD
[0.0.0]: https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp/releases/tag/v0.0.0
# Real Estate Sustainability Analysis MCP

MCP server for analyzing building sustainability metrics through Excel, PDF, and standardized frameworks (ESG, LEED, BREEAM, DGNB) with IFC integration

Built with [FastMCP](https://github.com/jlowin/fastmcp) and [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) for efficient handling of large data in AI agent tools.

## Features

- ✅ **Reference-Based Caching** - Return references instead of large data, reducing context window usage
- ✅ **Preview Generation** - Automatic previews for large results (sample, truncate, paginate strategies)
- ✅ **Pagination** - Navigate large datasets without loading everything at once
- ✅ **Access Control** - Separate user and agent permissions for sensitive data
- ✅ **Private Computation** - Let agents compute with values they cannot see
- ✅ **Docker Ready** - Production-ready containers with Python slim base image
- ✅ **GitHub Actions** - CI/CD with PyPI publishing and GHCR containers

- ✅ **Langfuse Tracing** - Built-in observability integration

- ✅ **Type-Safe** - Full type hints with Pydantic models
- ✅ **Testing Ready** - pytest with 73% coverage requirement
- ✅ **Pre-commit Hooks** - Ruff formatting and linting

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/l4b4r4b4b4/real-estate-sustainability-mcp
cd real-estate-sustainability-mcp

# Install dependencies
uv sync

# Run the server (stdio mode for Claude Desktop)
uv run real-estate-sustainability-mcp

# Run the server (SSE/HTTP mode for deployment)
uv run real-estate-sustainability-mcp --transport sse --port 8000
```

### Install from PyPI

```bash
# Run directly with uvx (no install needed)
uvx real-estate-sustainability-mcp stdio

# Or install globally
uv tool install real-estate-sustainability-mcp
real-estate-sustainability-mcp --help
```

### Docker Deployment

```bash
# Pull and run from GHCR
docker pull ghcr.io/l4b4r4b4b4/real-estate-sustainability-mcp:latest
docker run -p 8000:8000 ghcr.io/l4b4r4b4b4/real-estate-sustainability-mcp:latest

# Or build locally with Docker Compose
docker compose up

# Build images manually
docker compose --profile build build base
docker compose build
```

### Using with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "real-estate-sustainability-mcp": {
      "command": "uv",
      "args": ["run", "real-estate-sustainability-mcp"],
      "cwd": "/path/to/real-estate-sustainability-mcp"
    }
  }
}
```

### Using with Zed

The project includes `.zed/settings.json` pre-configured for MCP context servers.


## Project Structure

```
real-estate-sustainability-mcp/
├── app/                     # Application code
│   ├── __init__.py          # Version export
│   ├── server.py            # Main server with tools
│   ├── tools/               # Tool modules
│   └── __main__.py          # CLI entry point
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   └── test_server.py       # Server tests
├── docker/
│   ├── Dockerfile.base      # Python slim base image with dependencies
│   ├── Dockerfile           # Production image (extends base)
│   └── Dockerfile.dev       # Development with hot reload
├── .github/
│   └── workflows/
│       ├── ci.yml           # CI pipeline (lint, test, security)
│       ├── publish.yml      # PyPI trusted publisher
│       └── release.yml      # Docker build & publish to GHCR
├── .agent/                  # AI assistant workspace
│   └── goals/
│       └── 00-Template-Goal/  # Goal tracking template
├── pyproject.toml           # Project config
├── docker-compose.yml       # Local development & production
├── flake.nix                # Nix dev shell
└── .rules                   # AI assistant guidelines
```

## Development

### Setup

```bash
# Install dependencies
uv sync

# Install pre-commit and pre-push hooks
uv run pre-commit install --install-hooks
uv run pre-commit install --hook-type pre-push
```

### Running Tests

```bash
uv run pytest
uv run pytest --cov  # With coverage
```

### Linting and Formatting

```bash
uv run ruff check . --fix
uv run ruff format .
```

### Type Checking

```bash
uv run mypy app/
```

### Docker Development

```bash
# Run development container with hot reload
docker compose --profile dev up

# Build base image (for publishing)
docker compose --profile build build base

# Build all images
docker compose build
```

### Using Nix (Optional)

```bash
nix develop  # Enter dev shell with all tools
```

## Configuration


### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | - |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | - |
| `LANGFUSE_HOST` | Langfuse host URL | `https://cloud.langfuse.com` |


### CLI Commands

```bash
uvx real-estate-sustainability-mcp --help

Commands:
  stdio             Start server in stdio mode (for Claude Desktop and local CLI)
  sse               Start server in SSE mode (Server-Sent Events)
  streamable-http   Start server in streamable HTTP mode (recommended for remote/Docker)

# Examples:
uvx real-estate-sustainability-mcp stdio                          # Local CLI mode
uvx real-estate-sustainability-mcp sse --port 8000                # SSE on port 8000
uvx real-estate-sustainability-mcp streamable-http --host 0.0.0.0 # Docker/remote mode
```

## Publishing

### PyPI

Configure trusted publisher at [PyPI](https://pypi.org/manage/account/publishing/):
- Project name: `real-estate-sustainability-mcp`
- Owner: `l4b4r4b4b4`
- Repository: `real-estate-sustainability-mcp`
- Workflow: `publish.yml`
- Environment: `pypi`

### Docker Images

Images are automatically published to GHCR on:
- Push to `main` branch → `latest` tag
- Version tags (`v*.*.*`) → `latest`, `v0.0.1`, `0.0.1`, `0.0` tags

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Related Projects

- [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) - Reference-based caching for MCP servers
- [FastMCP](https://github.com/jlowin/fastmcp) - High-performance MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - The underlying protocol specification

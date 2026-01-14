#!/usr/bin/env python3
"""Inspect MCP tool schemas for debugging LLM integration issues.

This script outputs the full JSON schema for all registered MCP tools,
helping diagnose issues where LLMs don't call tools correctly.

Usage:
    uv run python scripts/inspect_schemas.py
    uv run python scripts/inspect_schemas.py --tool create_building_project
    uv run python scripts/inspect_schemas.py --summary
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any


def get_tools() -> dict[str, Any]:
    """Get all registered tools from the MCP server."""
    from app.server import mcp

    async def _get_tools() -> dict[str, Any]:
        return await mcp._tool_manager.get_tools()

    return asyncio.run(_get_tools())


def print_tool_schema(tool_name: str, tool: Any) -> None:
    """Print the full schema for a single tool."""
    mcp_tool = tool.to_mcp_tool()
    output = {
        "name": mcp_tool.name,
        "description": mcp_tool.description,
        "inputSchema": mcp_tool.inputSchema,
    }
    print(json.dumps(output, indent=2))


def print_summary(tools: dict) -> None:
    """Print a summary of all tool schemas."""
    print("=" * 70)
    print("MCP Tool Schema Summary")
    print("=" * 70)
    print()

    for name in sorted(tools.keys()):
        tool = tools[name]
        params = getattr(tool, "parameters", {})
        required = params.get("required", [])
        properties = params.get("properties", {})

        # Check for missing descriptions
        missing_desc = [p for p, v in properties.items() if "description" not in v]

        # Check for missing types
        missing_type = [
            p for p, v in properties.items() if "type" not in v and "anyOf" not in v
        ]

        print(f"📦 {name}")
        print(f"   Required: [{', '.join(required) or 'none'}]")
        print(f"   Properties: {len(properties)}")

        if missing_desc:
            print(f"   ⚠️  Missing descriptions: {missing_desc}")
        if missing_type:
            print(f"   ⚠️  Missing types: {missing_type}")

        # Show descriptions for required fields
        for prop_name in required:
            prop_schema = properties.get(prop_name, {})
            desc = prop_schema.get("description", "NO DESCRIPTION")
            prop_type = prop_schema.get("type", "union")
            print(f"      • {prop_name} ({prop_type}): {desc}")

        print()

    print("=" * 70)
    print("Summary: All tools should have 'required' arrays and descriptions.")
    print("If Flowise still has issues, try:")
    print("  1. Restart Flowise to clear cached schemas")
    print("  2. Check Flowise MCP connector logs for actual schema received")
    print("  3. Try a different LLM model (some handle schemas better)")
    print("=" * 70)


def print_all_schemas(tools: dict) -> None:
    """Print full schemas for all tools."""
    all_schemas = []
    for name in sorted(tools.keys()):
        tool = tools[name]
        mcp_tool = tool.to_mcp_tool()
        all_schemas.append(
            {
                "name": mcp_tool.name,
                "description": mcp_tool.description[:200] + "..."
                if len(mcp_tool.description or "") > 200
                else mcp_tool.description,
                "inputSchema": mcp_tool.inputSchema,
            }
        )
    print(json.dumps(all_schemas, indent=2))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Inspect MCP tool schemas for debugging"
    )
    parser.add_argument(
        "--tool",
        "-t",
        help="Show schema for a specific tool",
    )
    parser.add_argument(
        "--summary",
        "-s",
        action="store_true",
        help="Show summary of all tools",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Output full JSON schemas for all tools",
    )

    args = parser.parse_args()

    tools = get_tools()

    if args.tool:
        if args.tool not in tools:
            print(f"Error: Tool '{args.tool}' not found.", file=sys.stderr)
            print(
                f"Available tools: {', '.join(sorted(tools.keys()))}", file=sys.stderr
            )
            sys.exit(1)
        print_tool_schema(args.tool, tools[args.tool])
    elif args.summary:
        print_summary(tools)
    elif args.all:
        print_all_schemas(tools)
    else:
        # Default: show summary
        print_summary(tools)


if __name__ == "__main__":
    main()

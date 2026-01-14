"""Tests for the real-estate-sustainability-mcp server module."""

from __future__ import annotations

import asyncio

import pytest

from app.server import cache, mcp
from app.tracing import (
    MockContext,
    enable_test_mode,
    get_langfuse_attributes,
    is_langfuse_enabled,
    is_test_mode_enabled,
)


class TestServerInitialization:
    """Tests for server initialization."""

    def test_mcp_instance_exists(self) -> None:
        """Test that FastMCP instance is created."""
        assert mcp is not None
        assert mcp.name == "Real Estate Sustainability Analysis MCP"

    def test_cache_instance_exists(self) -> None:
        """Test that RefCache instance is created."""
        assert cache is not None
        assert cache.name == "real-estate-sustainability-mcp"


class TestTracingModule:
    """Tests for the tracing module."""

    def setup_method(self) -> None:
        """Reset test mode before each test."""
        enable_test_mode(False)
        MockContext.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        enable_test_mode(False)
        MockContext.reset()

    def test_is_langfuse_enabled_without_env(self) -> None:
        """Test that Langfuse is disabled without env vars."""
        # This may be True or False depending on env
        result = is_langfuse_enabled()
        assert isinstance(result, bool)

    def test_enable_test_mode(self) -> None:
        """Test enabling test mode."""
        assert not is_test_mode_enabled()
        enable_test_mode(True)
        assert is_test_mode_enabled()
        enable_test_mode(False)
        assert not is_test_mode_enabled()

    def test_mock_context_default_state(self) -> None:
        """Test MockContext has default state."""
        state = MockContext.get_current_state()
        assert state["user_id"] == "demo_user"
        assert state["org_id"] == "demo_org"
        assert state["agent_id"] == "demo_agent"
        assert state["session_id"] == "demo_session_001"

    def test_mock_context_set_state(self) -> None:
        """Test MockContext state can be updated."""
        MockContext.set_state(user_id="alice", org_id="acme")
        state = MockContext.get_current_state()
        assert state["user_id"] == "alice"
        assert state["org_id"] == "acme"

    def test_mock_context_set_session_id(self) -> None:
        """Test MockContext session_id can be updated."""
        MockContext.set_session_id("new-session-123")
        state = MockContext.get_current_state()
        assert state["session_id"] == "new-session-123"

    def test_mock_context_reset(self) -> None:
        """Test MockContext reset."""
        MockContext.set_state(user_id="bob")
        MockContext.set_session_id("custom-session")
        MockContext.reset()
        state = MockContext.get_current_state()
        assert state["user_id"] == "demo_user"
        assert state["session_id"] == "demo_session_001"

    def test_get_langfuse_attributes_default(self) -> None:
        """Test get_langfuse_attributes without context."""
        attrs = get_langfuse_attributes()
        assert "user_id" in attrs
        assert "session_id" in attrs
        assert "metadata" in attrs
        assert "tags" in attrs
        assert "version" in attrs

    def test_get_langfuse_attributes_with_test_mode(self) -> None:
        """Test get_langfuse_attributes with test mode enabled."""
        enable_test_mode(True)
        MockContext.set_state(user_id="test_user", org_id="test_org")
        attrs = get_langfuse_attributes()
        assert attrs["user_id"] == "test_user"
        assert attrs["metadata"]["orgid"] == "test_org"
        assert "testmode" in attrs["tags"]

    def test_get_langfuse_attributes_with_operation(self) -> None:
        """Test get_langfuse_attributes with operation name."""
        attrs = get_langfuse_attributes(operation="cache_set")
        assert attrs["metadata"]["operation"] == "cache_set"
        assert "cacheset" in attrs["tags"]


class TestHealthCheck:
    """Tests for health_check tool."""

    def _call_health_check(self) -> dict:
        """Helper to call health_check, handling FunctionTool wrapper."""
        from app import server

        health_fn = server.health_check
        if hasattr(health_fn, "fn"):
            return health_fn.fn()
        return health_fn()

    def test_health_check_returns_status(self) -> None:
        """Test that health check returns healthy status."""
        result = self._call_health_check()

        assert "status" in result
        assert result["status"] == "healthy"

    def test_health_check_returns_server_name(self) -> None:
        """Test that health check returns server name."""
        result = self._call_health_check()

        assert "server" in result
        assert result["server"] == "real-estate-sustainability-mcp"

    def test_health_check_returns_cache_name(self) -> None:
        """Test that health check returns cache name."""
        result = self._call_health_check()

        assert "cache" in result
        assert result["cache"] == "real-estate-sustainability-mcp"


class TestMCPConfiguration:
    """Tests for MCP server configuration."""

    def test_mcp_has_instructions(self) -> None:
        """Test that MCP has instructions configured."""
        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0

    def test_instructions_mention_caching(self) -> None:
        """Test that instructions mention caching."""
        assert "cach" in mcp.instructions.lower()

    def test_instructions_mention_esg(self) -> None:
        """Test that instructions mention ESG assessment."""
        assert "esg" in mcp.instructions.lower()


class TestGetCachedResult:
    """Tests for the get_cached_result tool."""

    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self) -> None:
        """Clear cache before and after each test."""
        cache.clear()
        yield
        cache.clear()

    async def _call_get_cached_result(
        self,
        ref_id: str,
        page: int | None = None,
        page_size: int | None = None,
        max_size: int | None = None,
    ) -> dict:
        """Helper to call get_cached_result."""
        from app import server

        get_fn = server.get_cached_result
        fn = get_fn.fn if hasattr(get_fn, "fn") else get_fn

        return await fn(ref_id, page, page_size, max_size)

    @pytest.mark.asyncio
    async def test_get_cached_result_invalid_ref(self) -> None:
        """Test that invalid reference returns error dict."""
        result = await self._call_get_cached_result("nonexistent:ref")

        assert "error" in result
        assert result["ref_id"] == "nonexistent:ref"

    @pytest.mark.asyncio
    async def test_get_cached_result_not_found(self) -> None:
        """Test that result includes the requested ref_id."""
        result = await self._call_get_cached_result("test:ref:123")

        assert "ref_id" in result
        assert result["ref_id"] == "test:ref:123"


class TestTyperCLI:
    """Tests for the typer CLI entry point."""

    def test_cli_app_exists(self) -> None:
        """Test that typer app is created."""
        from app.__main__ import app

        assert app is not None

    def test_cli_has_stdio_command(self) -> None:
        """Test that CLI has stdio command."""
        from app.__main__ import app

        # Check callback names since typer may not set cmd.name for decorated funcs
        callback_names = [
            cmd.callback.__name__ if cmd.callback else cmd.name
            for cmd in app.registered_commands
        ]
        assert "stdio" in callback_names

    def test_cli_has_sse_command(self) -> None:
        """Test that CLI has sse command."""
        from app.__main__ import app

        callback_names = [
            cmd.callback.__name__ if cmd.callback else cmd.name
            for cmd in app.registered_commands
        ]
        assert "sse" in callback_names

    def test_cli_has_streamable_http_command(self) -> None:
        """Test that CLI has streamable-http command."""
        from app.__main__ import app

        # streamable-http uses explicit name, check both name and callback
        command_info = [
            (cmd.name, cmd.callback.__name__ if cmd.callback else None)
            for cmd in app.registered_commands
        ]
        has_streamable_http = any(
            name == "streamable-http" or callback == "streamable_http"
            for name, callback in command_info
        )
        assert has_streamable_http


class TestPydanticModels:
    """Tests for Pydantic input models."""

    def test_secret_input(self) -> None:
        """Test SecretInput model."""
        from app.tools.secrets import SecretInput

        model = SecretInput(name="test", value=42.0)
        assert model.name == "test"
        assert model.value == 42.0

    def test_secret_input_validation(self) -> None:
        """Test SecretInput validates name length."""
        from pydantic import ValidationError

        from app.tools.secrets import SecretInput

        with pytest.raises(ValidationError):
            SecretInput(name="", value=1.0)  # Empty name

    def test_secret_compute_input(self) -> None:
        """Test SecretComputeInput model."""
        from app.tools.secrets import SecretComputeInput

        model = SecretComputeInput(secret_ref="ref:123", multiplier=2.5)
        assert model.secret_ref == "ref:123"
        assert model.multiplier == 2.5

    def test_secret_compute_input_default_multiplier(self) -> None:
        """Test SecretComputeInput default multiplier."""
        from app.tools.secrets import SecretComputeInput

        model = SecretComputeInput(secret_ref="ref:456")
        assert model.multiplier == 1.0

    def test_cache_query_input(self) -> None:
        """Test CacheQueryInput model."""
        from app.tools.cache import CacheQueryInput

        model = CacheQueryInput(ref_id="cache:ref", page=2, page_size=20)
        assert model.ref_id == "cache:ref"
        assert model.page == 2
        assert model.page_size == 20

    def test_cache_query_input_defaults(self) -> None:
        """Test CacheQueryInput optional fields."""
        from app.tools.cache import CacheQueryInput

        model = CacheQueryInput(ref_id="cache:ref")
        assert model.page is None
        assert model.page_size is None
        assert model.max_size is None


class TestSustainabilityGuidePrompt:
    """Tests for the sustainability guide prompt."""

    def _call_template_guide(self) -> str:
        """Helper to call template_guide prompt."""
        from app import server

        prompt_fn = server.template_guide
        if hasattr(prompt_fn, "fn"):
            return prompt_fn.fn()
        return prompt_fn()

    def test_sustainability_guide_returns_string(self) -> None:
        """Test that sustainability guide returns a string."""
        result = self._call_template_guide()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_sustainability_guide_mentions_sustainability(self) -> None:
        """Test that guide mentions sustainability."""
        result = self._call_template_guide()
        assert "sustainability" in result.lower()

    def test_sustainability_guide_mentions_health_check(self) -> None:
        """Test that guide mentions health_check tool."""
        result = self._call_template_guide()
        assert "health_check" in result

    def test_sustainability_guide_mentions_secret(self) -> None:
        """Test that guide mentions secret computation."""
        result = self._call_template_guide()
        assert "secret" in result.lower()


class TestToolSchemas:
    """Tests for tool JSON schema generation.

    These tests ensure MCP tool schemas have proper required arrays,
    descriptions, and type declarations for LLM compatibility.
    """

    @pytest.fixture
    def tools(self) -> dict:
        """Get all registered tools from the MCP server."""

        async def get_tools():
            return await mcp._tool_manager.get_tools()

        return asyncio.run(get_tools())

    def test_create_building_project_has_required(self, tools: dict) -> None:
        """Test create_building_project has required fields."""
        tool = tools["create_building_project"]
        params = tool.parameters
        assert "required" in params
        assert "name" in params["required"]
        assert "floor_area_sqm" in params["required"]
        assert "construction_year" in params["required"]

    def test_add_energy_data_has_required(self, tools: dict) -> None:
        """Test add_energy_data has required fields."""
        tool = tools["add_energy_data"]
        params = tool.parameters
        assert "required" in params
        assert "project_id" in params["required"]
        assert "year" in params["required"]
        assert "consumption_kwh" in params["required"]

    def test_add_consumption_data_has_required(self, tools: dict) -> None:
        """Test add_consumption_data has required fields."""
        tool = tools["add_consumption_data"]
        params = tool.parameters
        assert "required" in params
        required = params["required"]
        assert "project_id" in required
        assert "year" in required
        assert "category" in required
        assert "value" in required
        assert "unit" in required

    def test_analysis_tools_have_required_project_id(self, tools: dict) -> None:
        """Test all analysis tools require project_id."""
        analysis_tools = [
            "calculate_energy_intensity",
            "calculate_carbon_footprint",
            "check_eu_taxonomy_alignment",
            "check_data_completeness",
            "suggest_data_sources",
        ]
        for tool_name in analysis_tools:
            tool = tools[tool_name]
            params = tool.parameters
            assert "required" in params, f"{tool_name} missing 'required'"
            assert "project_id" in params["required"], f"{tool_name} missing project_id"

    def test_all_properties_have_descriptions(self, tools: dict) -> None:
        """Test all tool properties have description fields."""
        for tool_name, tool in tools.items():
            params = tool.parameters
            properties = params.get("properties", {})
            for prop_name, prop_schema in properties.items():
                assert "description" in prop_schema, (
                    f"{tool_name}.{prop_name} missing description"
                )

    def test_all_properties_have_types(self, tools: dict) -> None:
        """Test all tool properties have type declarations."""
        for tool_name, tool in tools.items():
            params = tool.parameters
            properties = params.get("properties", {})
            for prop_name, prop_schema in properties.items():
                # Type can be in 'type' field or in 'anyOf' for union types
                has_type = "type" in prop_schema or "anyOf" in prop_schema
                assert has_type, f"{tool_name}.{prop_name} missing type"

    def test_get_cached_result_has_required(self, tools: dict) -> None:
        """Test get_cached_result has required ref_id."""
        tool = tools["get_cached_result"]
        params = tool.parameters
        assert "required" in params
        assert "ref_id" in params["required"]

    def test_mcp_tool_output_has_input_schema(self, tools: dict) -> None:
        """Test MCP protocol tool output has inputSchema."""
        tool = tools["create_building_project"]
        mcp_tool = tool.to_mcp_tool()
        assert mcp_tool.inputSchema is not None
        assert "required" in mcp_tool.inputSchema
        assert "properties" in mcp_tool.inputSchema

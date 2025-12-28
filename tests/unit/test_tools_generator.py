"""Unit tests for Claude tool definition generator."""

import json
import tempfile
from pathlib import Path

import pytest

from honeycomb.tools.descriptions import validate_description
from honeycomb.tools.generator import (
    create_tool_definition,
    export_tools_json,
    export_tools_python,
    generate_all_tools,
    generate_create_burn_alert_tool,
    generate_create_slo_tool,
    generate_create_trigger_tool,
    generate_list_triggers_tool,
    generate_tools_for_resource,
)
from honeycomb.tools.schemas import validate_schema, validate_tool_name


class TestToolNameValidation:
    """Test tool name validation."""

    def test_valid_names(self):
        """Valid tool names should pass validation."""
        valid_names = [
            "honeycomb_create_trigger",
            "honeycomb-list-slos",
            "honeycomb_get_burn_alert",
            "a",  # Single char valid
            "a" * 64,  # Max length
        ]

        for name in valid_names:
            validate_tool_name(name)  # Should not raise

    def test_invalid_names(self):
        """Invalid tool names should raise ValueError."""
        invalid_names = [
            "",  # Empty
            "a" * 65,  # Too long
            "honeycomb.create",  # Dot not allowed
            "honeycomb create",  # Space not allowed
            "honeycomb@create",  # @ not allowed
        ]

        for name in invalid_names:
            with pytest.raises(ValueError, match="must match pattern"):
                validate_tool_name(name)


class TestDescriptionValidation:
    """Test description validation."""

    def test_valid_descriptions(self):
        """Valid descriptions should pass validation."""
        valid_desc = "A" * 50  # Minimum length
        validate_description(valid_desc)

        long_desc = "Creates a new trigger that fires when query results cross a threshold."
        validate_description(long_desc)

    def test_description_too_short(self):
        """Descriptions < 50 chars should fail."""
        with pytest.raises(ValueError, match="at least 50 characters"):
            validate_description("Too short")

    def test_description_with_placeholders(self):
        """Descriptions with placeholder text should fail."""
        placeholders = ["TODO", "TBD", "FIXME", "XXX"]

        for placeholder in placeholders:
            desc = f"This is a {placeholder} description that is long enough to pass length check"
            with pytest.raises(ValueError, match="placeholder text"):
                validate_description(desc)


class TestSchemaValidation:
    """Test schema validation."""

    def test_valid_schema(self):
        """Valid schemas should pass validation."""
        schema = {
            "type": "object",
            "properties": {
                "dataset": {"type": "string", "description": "Dataset slug"},
                "name": {"type": "string", "description": "Trigger name"},
            },
            "required": ["dataset", "name"],
        }
        validate_schema(schema)

    def test_schema_missing_properties(self):
        """Schema without properties should fail."""
        with pytest.raises(ValueError, match="must have 'properties' field"):
            validate_schema({"type": "object"})

    def test_required_field_not_in_properties(self):
        """Required fields not in properties should fail."""
        schema = {
            "type": "object",
            "properties": {"dataset": {"type": "string", "description": "Dataset"}},
            "required": ["dataset", "missing_field"],
        }
        with pytest.raises(ValueError, match="Required field 'missing_field' not found"):
            validate_schema(schema)

    def test_property_missing_description(self):
        """Properties without descriptions should fail."""
        schema = {
            "type": "object",
            "properties": {
                "dataset": {"type": "string"},  # Missing description
            },
        }
        with pytest.raises(ValueError, match="missing description"):
            validate_schema(schema)


class TestToolDefinitionCreation:
    """Test tool definition creation."""

    def test_create_minimal_tool(self):
        """Can create tool with minimal parameters."""
        tool = create_tool_definition(
            name="test_tool",
            description="A" * 50,
            input_schema={
                "type": "object",
                "properties": {"param": {"type": "string", "description": "A parameter"}},
            },
        )

        assert tool["name"] == "test_tool"
        assert len(tool["description"]) >= 50
        assert tool["input_schema"]["type"] == "object"
        assert "input_examples" not in tool

    def test_create_tool_with_examples(self):
        """Can create tool with examples."""
        examples = [{"param": "value1"}, {"param": "value2"}]

        tool = create_tool_definition(
            name="test_tool",
            description="A" * 50,
            input_schema={
                "type": "object",
                "properties": {"param": {"type": "string", "description": "A parameter"}},
            },
            input_examples=examples,
        )

        assert tool["input_examples"] == examples

    def test_invalid_tool_name_raises(self):
        """Invalid tool name should raise ValueError."""
        with pytest.raises(ValueError):
            create_tool_definition(
                name="invalid.name",
                description="A" * 50,
                input_schema={
                    "type": "object",
                    "properties": {"param": {"type": "string", "description": "A parameter"}},
                },
            )


class TestGenerateAllTools:
    """Test generating all tool definitions."""

    def test_generates_15_tools(self):
        """Should generate exactly 36 tools (Priority 1 + Batch 1 + Batch 2)."""
        tools = generate_all_tools()
        assert len(tools) == 36  # 15 Priority 1 + 10 Batch 1 + 11 Batch 2

    def test_all_tools_have_required_fields(self):
        """All tools must have name, description, and input_schema."""
        tools = generate_all_tools()

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

            # Validate each field
            validate_tool_name(tool["name"])
            validate_description(tool["description"])
            validate_schema(tool["input_schema"])

    def test_tool_names_are_unique(self):
        """All tool names must be unique."""
        tools = generate_all_tools()
        names = [t["name"] for t in tools]
        assert len(names) == len(set(names)), "Duplicate tool names found"

    def test_all_tools_start_with_honeycomb(self):
        """All tools should have 'honeycomb_' prefix."""
        tools = generate_all_tools()

        for tool in tools:
            assert tool["name"].startswith("honeycomb_"), f"Tool {tool['name']} missing prefix"


class TestGenerateResourceTools:
    """Test generating tools for specific resources."""

    def test_generate_triggers_only(self):
        """Can generate triggers tools only."""
        tools = generate_tools_for_resource("triggers")
        assert len(tools) == 5
        for tool in tools:
            assert "trigger" in tool["name"]

    def test_generate_slos_only(self):
        """Can generate SLO tools only."""
        tools = generate_tools_for_resource("slos")
        assert len(tools) == 5
        for tool in tools:
            assert "slo" in tool["name"]

    def test_generate_burn_alerts_only(self):
        """Can generate burn alert tools only."""
        tools = generate_tools_for_resource("burn_alerts")
        assert len(tools) == 5
        for tool in tools:
            assert "burn_alert" in tool["name"]

    def test_invalid_resource_raises(self):
        """Invalid resource name should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid resource"):
            generate_tools_for_resource("invalid_resource")


class TestExportFunctions:
    """Test exporting tool definitions."""

    def test_export_tools_json(self):
        """Can export tools to JSON file."""
        tools = generate_all_tools()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            export_tools_json(tools, output_path)

            # Verify file exists and is valid JSON
            with open(output_path) as f:
                data = json.load(f)

            assert "tools" in data
            assert "version" in data
            assert "generated_at" in data
            assert "count" in data
            assert data["count"] == 36
            assert len(data["tools"]) == 36
        finally:
            Path(output_path).unlink()

    def test_export_tools_python(self):
        """Can export tools to Python module."""
        tools = generate_all_tools()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            output_path = f.name

        try:
            export_tools_python(tools, output_path)

            # Verify file exists and is valid Python
            with open(output_path) as f:
                content = f.read()

            assert "HONEYCOMB_TOOLS" in content
            assert "def get_tool" in content
            assert "def get_all_tools" in content
            assert "def list_tool_names" in content
        finally:
            Path(output_path).unlink()


class TestSpecificToolGenerators:
    """Test individual tool generators produce valid output."""

    def test_list_triggers_tool(self):
        """list_triggers tool should be valid."""
        tool = generate_list_triggers_tool()

        assert tool["name"] == "honeycomb_list_triggers"
        assert len(tool["description"]) >= 50
        assert "dataset" in tool["input_schema"]["properties"]
        assert tool["input_schema"]["required"] == ["dataset"]
        assert len(tool["input_examples"]) >= 2

    def test_create_trigger_tool(self):
        """create_trigger tool should be valid."""
        tool = generate_create_trigger_tool()

        assert tool["name"] == "honeycomb_create_trigger"
        assert len(tool["description"]) >= 50

        # Check required fields
        required = tool["input_schema"]["required"]
        assert "dataset" in required
        assert "name" in required
        assert "threshold" in required

        # Check examples
        examples = tool["input_examples"]
        assert len(examples) >= 3  # Should have multiple examples showcasing features

        # Verify at least one example shows inline query
        has_inline_query = any("query" in ex for ex in examples)
        assert has_inline_query, "Should have example with inline query"

    def test_create_slo_tool(self):
        """create_slo tool should be valid."""
        tool = generate_create_slo_tool()

        assert tool["name"] == "honeycomb_create_slo"
        assert len(tool["description"]) >= 50

        # Check examples
        examples = tool["input_examples"]
        assert len(examples) >= 3

        # Should have example with new derived column
        has_new_dc = any("expression" in ex.get("sli", {}) for ex in examples)
        assert has_new_dc, "Should have example creating new derived column"

        # Should have example with burn alerts
        has_burn_alerts = any("burn_alerts" in ex for ex in examples)
        assert has_burn_alerts, "Should have example with burn alerts"

    def test_create_burn_alert_tool(self):
        """create_burn_alert tool should be valid."""
        tool = generate_create_burn_alert_tool()

        assert tool["name"] == "honeycomb_create_burn_alert"
        assert len(tool["description"]) >= 50

        # Check examples
        examples = tool["input_examples"]
        assert len(examples) >= 2

        # Should show both alert types
        alert_types = {ex.get("alert_type") for ex in examples}
        assert "exhaustion_time" in alert_types
        assert "budget_rate" in alert_types


class TestToolExamplesValidation:
    """Test that tool examples are valid against their schemas."""

    def test_all_examples_validate_against_schema(self):
        """Every example should validate against its tool's schema."""
        tools = generate_all_tools()

        for tool in tools:
            tool_name = tool["name"]
            schema = tool["input_schema"]
            examples = tool.get("input_examples", [])

            for i, example in enumerate(examples):
                # Check all required fields are present
                required_fields = schema.get("required", [])
                for field in required_fields:
                    assert field in example, (
                        f"{tool_name} example {i}: missing required field '{field}'"
                    )

                # Check no extra unknown fields (unless schema allows additionalProperties)
                if schema.get("additionalProperties") is False:
                    for field in example:
                        assert field in schema["properties"], (
                            f"{tool_name} example {i}: unknown field '{field}'"
                        )

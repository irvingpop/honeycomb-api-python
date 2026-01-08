"""Datasets tool definitions for Claude API.

This module provides tool generators and descriptions for
datasets resources.
"""

from typing import Any

from honeycomb.models import DatasetCreate, DatasetUpdate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Datasets Descriptions
# ==============================================================================

DATASET_DESCRIPTIONS = {
    "honeycomb_list_datasets": (
        "Lists all datasets in your Honeycomb environment (no parameters required). "
        "Use this to discover existing datasets before creating new ones, when setting up observability for a new service, or when migrating data from another platform. "
        "This operation requires no parameters - it automatically lists all datasets you have access to. "
        "Returns a list of dataset objects including their slugs, names, descriptions, and metadata like creation timestamps and column counts."
    ),
    "honeycomb_get_dataset": (
        "Retrieves detailed information about a specific dataset by its slug. "
        "Use this to inspect a dataset's configuration including its name, description, JSON expansion settings, and usage statistics. "
        "Requires the dataset slug parameter. "
        "Returns the complete dataset configuration including creation timestamp, last written timestamp, and regular columns count."
    ),
    "honeycomb_create_dataset": (
        "Creates a new dataset to store telemetry data in Honeycomb. "
        "Use this when setting up observability for a new service, creating test environments, or segmenting data by application or team. "
        "Requires a name parameter which will be converted to a URL-safe slug. "
        "Optional parameters include description for documentation and expand_json_depth (0-10) to automatically expand nested JSON fields into separate columns. "
        "The dataset slug will be automatically generated from the name and used for API operations."
    ),
    "honeycomb_update_dataset": (
        "Updates an existing dataset's name, description, JSON expansion settings, or delete protection. "
        "Use this to correct dataset metadata, add documentation, adjust JSON parsing behavior, or toggle delete protection. "
        "Requires the dataset slug. All other fields are optional - only provided fields will be updated. "
        "Set delete_protected=true to prevent accidental deletion, or delete_protected=false to allow deletion. "
        "Note: The slug itself cannot be changed. Changing expand_json_depth only affects new events, not existing data."
    ),
    "honeycomb_delete_dataset": (
        "Permanently deletes a dataset and all its data from Honeycomb. "
        "Use this when decommissioning services, cleaning up test datasets, or consolidating data storage. "
        "Requires the dataset slug parameter. "
        "Warning: This action cannot be undone. All events, columns, queries, triggers, and SLOs in this dataset will be permanently deleted. "
        "Note: Datasets with delete protection enabled cannot be deleted. Use honeycomb_update_dataset to disable delete_protected first."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return DATASET_DESCRIPTIONS[tool_name]


def create_tool_definition(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    input_examples: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a Claude tool definition."""
    from honeycomb.tools.descriptions import validate_description
    from honeycomb.tools.schemas import add_metadata_fields, validate_schema, validate_tool_name

    validate_tool_name(name)
    validate_description(description)
    validate_schema(input_schema)
    add_metadata_fields(input_schema)

    definition: dict[str, Any] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
    }

    if input_examples:
        definition["input_examples"] = input_examples

    return definition


# ==============================================================================
# Datasets Tool Definitions
# ==============================================================================


def generate_list_datasets_tool() -> dict[str, Any]:
    """Generate honeycomb_list_datasets tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    examples: list[dict[str, Any]] = [
        {},  # List all datasets
    ]

    return create_tool_definition(
        name="honeycomb_list_datasets",
        description=get_description("honeycomb_list_datasets"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_get_dataset tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["slug"]}

    add_parameter(schema, "slug", "string", "The dataset slug to retrieve", required=True)

    examples: list[dict[str, Any]] = [
        {"slug": "api-logs"},
        {"slug": "production"},
    ]

    return create_tool_definition(
        name="honeycomb_get_dataset",
        description=get_description("honeycomb_get_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_create_dataset tool definition."""
    # Start with DatasetCreate schema
    base_schema = generate_schema_from_model(
        DatasetCreate,
        exclude_fields={"created_at", "last_written_at", "slug", "regular_columns_count"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        # Minimal example
        {"name": "api-logs"},
        # With description
        {
            "name": "production-logs",
            "description": "Production API logs from main services",
        },
        # With JSON expansion
        {
            "name": "trace-data",
            "description": "Distributed traces with nested JSON",
            "expand_json_depth": 3,
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_dataset",
        description=get_description("honeycomb_create_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_update_dataset tool definition."""
    # Use DatasetUpdate which supports partial updates and delete_protected
    base_schema = generate_schema_from_model(DatasetUpdate)

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["slug"]}
    add_parameter(schema, "slug", "string", "The dataset slug to update", required=True)

    # Add properties from DatasetUpdate (all optional)
    schema["properties"].update(base_schema["properties"])
    # Don't extend required - DatasetUpdate fields are all optional

    examples: list[dict[str, Any]] = [
        {"slug": "api-logs", "name": "API Logs", "description": "Updated description"},
        {"slug": "production", "expand_json_depth": 5},
        {"slug": "critical-data", "delete_protected": True},
        {"slug": "test-dataset", "delete_protected": False},
    ]

    return create_tool_definition(
        name="honeycomb_update_dataset",
        description=get_description("honeycomb_update_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_dataset tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["slug"]}

    add_parameter(schema, "slug", "string", "The dataset slug to delete", required=True)

    examples: list[dict[str, Any]] = [
        {"slug": "test-dataset"},
        {"slug": "old-logs"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_dataset",
        description=get_description("honeycomb_delete_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all datasets tool definitions."""
    return [
        generate_list_datasets_tool(),
        generate_get_dataset_tool(),
        generate_create_dataset_tool(),
        generate_update_dataset_tool(),
        generate_delete_dataset_tool(),
    ]

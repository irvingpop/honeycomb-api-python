"""Schema generation utilities for Claude tool definitions.

This module provides utilities to generate JSON Schema definitions from Pydantic models,
suitable for Claude's tool calling API.
"""

import re
from typing import Any

from pydantic import BaseModel

# ==============================================================================
# Metadata Field Schemas (for Claude reasoning - stripped before API execution)
# ==============================================================================

CONFIDENCE_SCHEMA: dict[str, Any] = {
    "type": "string",
    "enum": ["high", "medium", "low", "none"],
    "description": (
        "Claude's confidence level in this tool call. "
        "'high' = certain this matches user intent and will succeed, "
        "'medium' = likely correct but some uncertainty, "
        "'low' = uncertain but best available option, "
        "'none' = guessing or placeholder value."
    ),
}

NOTES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Structured reasoning notes explaining Claude's decision-making process. "
        "All categories are optional arrays of single-sentence strings."
    ),
    "properties": {
        "decisions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key decisions made (e.g., 'Chose COUNT over AVG for error rate')",
        },
        "concerns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Potential issues or risks (e.g., 'Time range may be too short')",
        },
        "assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Assumptions being made (e.g., 'Assuming status_code column exists')",
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Clarifying questions for increased confidence "
                "(e.g., 'I would be more confident if I knew the expected error baseline')"
            ),
        },
    },
    "additionalProperties": False,
}

# Fields that are metadata for downstream applications, not sent to Honeycomb API
METADATA_FIELDS: set[str] = {"confidence", "notes"}


def add_metadata_fields(schema: dict[str, Any]) -> None:
    """Add confidence and notes metadata fields to a tool schema.

    These fields are for Claude's reasoning and are NOT sent to the Honeycomb API.
    They are stripped by the executor before API calls.

    Both fields are optional - they are not added to the required list.

    Args:
        schema: The tool input schema to modify (mutated in place)

    Example:
        >>> schema = {"type": "object", "properties": {}, "required": ["dataset"]}
        >>> add_metadata_fields(schema)
        >>> "confidence" in schema["properties"]
        True
        >>> "notes" in schema["properties"]
        True
        >>> "confidence" in schema.get("required", [])
        False
    """
    import copy

    schema["properties"]["confidence"] = copy.deepcopy(CONFIDENCE_SCHEMA)
    schema["properties"]["notes"] = copy.deepcopy(NOTES_SCHEMA)
    # Note: Both fields are OPTIONAL - not added to required list


def validate_tool_name(name: str) -> None:
    """Validate tool name follows Claude's naming constraints.

    Args:
        name: The tool name to validate

    Raises:
        ValueError: If name doesn't match pattern ^[a-zA-Z0-9_-]{1,64}$
    """
    pattern = r"^[a-zA-Z0-9_-]{1,64}$"
    if not re.match(pattern, name):
        raise ValueError(
            f"Tool name '{name}' must match pattern {pattern}. "
            "Only letters, numbers, underscores, and hyphens allowed, 1-64 characters."
        )


def generate_schema_from_model(
    model: type[BaseModel], exclude_fields: set[str] | None = None
) -> dict[str, Any]:
    """Generate JSON Schema from a Pydantic model.

    Args:
        model: The Pydantic model class to generate schema from
        exclude_fields: Optional set of field names to exclude from schema

    Returns:
        JSON Schema dict suitable for Claude tool definitions
    """
    exclude_fields = exclude_fields or set()

    # Get the full JSON schema from Pydantic
    full_schema = model.model_json_schema()

    # Extract properties and required fields
    properties = {
        k: v for k, v in full_schema.get("properties", {}).items() if k not in exclude_fields
    }
    required = [f for f in full_schema.get("required", []) if f not in exclude_fields]

    # Build the schema
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }

    if required:
        schema["required"] = required

    # Handle definitions/defs for nested models
    if "$defs" in full_schema:
        schema["$defs"] = full_schema["$defs"]
    elif "definitions" in full_schema:
        schema["definitions"] = full_schema["definitions"]

    return schema


def merge_schemas(*schemas: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple JSON schemas into one.

    Useful for combining schemas from multiple models (e.g., dataset + model-specific params).

    Args:
        *schemas: Variable number of schema dicts to merge

    Returns:
        Merged schema dict
    """
    merged: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    all_defs: dict[str, Any] = {}

    for schema in schemas:
        # Merge properties
        merged["properties"].update(schema.get("properties", {}))

        # Merge required fields
        required = schema.get("required", [])
        if required:
            merged["required"].extend(required)

        # Merge definitions
        if "$defs" in schema:
            all_defs.update(schema["$defs"])
        elif "definitions" in schema:
            all_defs.update(schema["definitions"])

    # Deduplicate required fields
    if merged["required"]:
        merged["required"] = list(dict.fromkeys(merged["required"]))
    else:
        del merged["required"]

    # Add definitions if any
    if all_defs:
        merged["$defs"] = all_defs

    return merged


def add_parameter(
    schema: dict[str, Any],
    name: str,
    param_type: str,
    description: str,
    required: bool = True,
    **kwargs: Any,
) -> None:
    """Add a parameter to an existing schema.

    Args:
        schema: The schema dict to modify
        name: Parameter name
        param_type: JSON Schema type (string, integer, object, array, etc.)
        description: Parameter description
        required: Whether parameter is required
        **kwargs: Additional schema properties (enum, items, etc.)
    """
    schema["properties"][name] = {
        "type": param_type,
        "description": description,
        **kwargs,
    }

    if required:
        if "required" not in schema:
            schema["required"] = []
        if name not in schema["required"]:
            schema["required"].append(name)


def validate_schema(schema: dict[str, Any]) -> None:
    """Validate a JSON Schema is well-formed.

    Args:
        schema: The schema dict to validate

    Raises:
        ValueError: If schema is invalid
    """
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary")

    if schema.get("type") != "object":
        raise ValueError("Schema type must be 'object'")

    if "properties" not in schema:
        raise ValueError("Schema must have 'properties' field")

    if not isinstance(schema["properties"], dict):
        raise ValueError("Schema properties must be a dictionary")

    # Check all required fields exist in properties
    required = schema.get("required", [])
    properties = schema["properties"]

    for field in required:
        if field not in properties:
            raise ValueError(f"Required field '{field}' not found in properties")

    # Check all properties have descriptions
    for field_name, field_schema in properties.items():
        if "description" not in field_schema and "$ref" not in field_schema:
            raise ValueError(
                f"Field '{field_name}' missing description. "
                "All fields must have descriptions for Claude tool definitions."
            )

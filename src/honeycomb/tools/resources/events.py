"""Events tool definitions for Claude API.

This module provides tool generators and descriptions for
events resources.
"""

from typing import Any

from honeycomb.tools.schemas import add_parameter

# ==============================================================================
# Events Descriptions
# ==============================================================================

EVENT_DESCRIPTIONS = {
    "honeycomb_send_event": (
        "Sends a SINGLE telemetry event to a Honeycomb dataset. Use ONLY for one-off events or testing. "
        "STRUCTURE: Flat - parameters are 'dataset' (string) and 'data' (object with key-value pairs) provided directly at top level. "
        "Example: {dataset: 'api-logs', data: {status_code: 200, endpoint: '/api/users'}}. "
        "For 2+ events, you MUST use honeycomb_send_batch_events instead. "
        "Optional parameters: timestamp (Unix seconds), samplerate (integer). "
        "IMPORTANT: This is for SINGLE events only - batch tool is required for multiple events."
    ),
    "honeycomb_send_batch_events": (
        "Sends MULTIPLE telemetry events to a Honeycomb dataset in a single API call (preferred for 2+ events). "
        "STRUCTURE: Nested - requires 'dataset' (string) and 'events' (array) where EACH event object has a 'data' field. "
        "Example: {dataset: 'api-logs', events: [{data: {status_code: 200}}, {data: {status_code: 201}}]}. "
        "CRITICAL: The 'events' parameter is REQUIRED and must be an ARRAY of event objects. Each event MUST have a 'data' field containing key-value pairs. "
        "Per-event optional fields: 'time' (ISO8601 string like '2024-01-15T10:30:00Z'), 'samplerate' (integer). "
        "Use this for efficient bulk data ingestion, application logs, traces, or metrics. "
        "Returns status for each event, allowing identification and retry of failed events."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return EVENT_DESCRIPTIONS[tool_name]


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
# Events Tool Definitions
# ==============================================================================


def generate_send_event_tool() -> dict[str, Any]:
    """Generate honeycomb_send_event tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "data"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "data", "object", "Event data as key-value pairs", required=True)
    add_parameter(schema, "timestamp", "integer", "Unix timestamp for the event", required=False)
    add_parameter(schema, "samplerate", "integer", "Sample rate (default: 1)", required=False)

    examples: list[dict[str, Any]] = [
        {
            "dataset": "api-logs",
            "data": {"endpoint": "/api/users", "duration_ms": 42, "status_code": 200},
        },
        {
            "dataset": "production",
            "data": {"service": "auth", "latency": 15},
            "timestamp": 1640000000,
        },
    ]

    return create_tool_definition(
        name="honeycomb_send_event",
        description=get_description("honeycomb_send_event"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_send_batch_events_tool() -> dict[str, Any]:
    """Generate honeycomb_send_batch_events tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "events"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)

    schema["properties"]["events"] = {
        "type": "array",
        "description": "Array of event objects. Each event must have a 'data' field with event payload.",
        "items": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Event payload as key-value pairs (required for each event)",
                },
                "time": {
                    "type": "string",
                    "description": "Event timestamp in ISO8601 format (e.g., '2024-01-15T10:30:00Z'). Optional, defaults to server time.",
                },
                "samplerate": {
                    "type": "integer",
                    "description": "Sample rate for this event (optional, defaults to 1)",
                },
            },
            "required": ["data"],
        },
    }

    examples: list[dict[str, Any]] = [
        {
            "dataset": "api-logs",
            "events": [
                {
                    "data": {"endpoint": "/api/users", "duration_ms": 42, "status_code": 200},
                    "time": "2024-01-15T10:30:00Z",
                },
                {
                    "data": {"endpoint": "/api/posts", "duration_ms": 18, "status_code": 201},
                    "time": "2024-01-15T10:30:15Z",
                },
            ],
        },
    ]

    return create_tool_definition(
        name="honeycomb_send_batch_events",
        description=get_description("honeycomb_send_batch_events"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all events tool definitions."""
    return [
        generate_send_event_tool(),
        generate_send_batch_events_tool(),
    ]

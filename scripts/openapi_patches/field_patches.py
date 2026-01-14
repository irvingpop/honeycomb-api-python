"""Patches that modify field requirements, patterns, and defaults.

These patches fix issues in the OpenAPI spec where the schema doesn't
match actual API behavior or our SDK's needs.
"""

from typing import Any

from .base import BasePatch, get_schemas


class DatasetUpdatePayloadOptionalPatch(BasePatch):
    """Make DatasetUpdatePayload fields optional for partial updates.

    The spec marks fields as required, but UPDATE operations should
    allow partial updates.
    """

    name = "DatasetUpdatePayload optional fields"
    description = "Removes 'required' constraint from DatasetUpdatePayload"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        return "DatasetUpdatePayload" in schemas and "required" in schemas["DatasetUpdatePayload"]

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        del schemas["DatasetUpdatePayload"]["required"]
        print(f"  [check] DatasetUpdatePayload: removed 'required' (UPDATE should be partial)")
        return 1


class BatchEventDataRequiredPatch(BasePatch):
    """Make BatchEvent.data required.

    You can't send an event without data, so this should be required.
    """

    name = "BatchEvent.data required"
    description = "Adds 'data' to BatchEvent required fields"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "BatchEvent" not in schemas:
            return False
        required = schemas["BatchEvent"].get("required", [])
        return "data" not in required

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        schemas["BatchEvent"].setdefault("required", [])
        schemas["BatchEvent"]["required"].append("data")
        print(f"  [check] BatchEvent: added 'data' to required fields")
        return 1


class BurnAlertRecipientsOptionalPatch(BasePatch):
    """Make burn alert recipients optional.

    Useful for testing and builders where you might not want to
    specify recipients initially.
    """

    name = "Burn alert recipients optional"
    description = "Removes 'recipients' from required in create burn alert requests"

    BURN_ALERT_SCHEMAS = [
        "CreateExhaustionTimeBurnAlertRequest",
        "CreateBudgetRateBurnAlertRequest",
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        for schema_name in self.BURN_ALERT_SCHEMAS:
            if schema_name in schemas:
                return True
        return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0

        for schema_name in self.BURN_ALERT_SCHEMAS:
            if schema_name not in schemas:
                continue

            all_of = schemas[schema_name].get("allOf", [])
            for item in all_of:
                if isinstance(item, dict) and "required" in item:
                    if "recipients" in item["required"]:
                        item["required"].remove("recipients")
                        patches += 1
                        print(f"  [check] {schema_name}: removed 'recipients' from required")

        return patches


class QueryDefaultsPatch(BasePatch):
    """Remove/override problematic defaults from Query schema.

    The spec has example values and API defaults that don't match our usage.
    """

    name = "Query schema defaults"
    description = "Removes bogus timestamp defaults, overrides breakdowns/limit defaults"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        return "Query" in schemas

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        props = schemas["Query"].get("properties", {})
        patches = 0

        # Remove bogus timestamp defaults (these are example values, not real defaults)
        if "start_time" in props and "default" in props["start_time"]:
            del props["start_time"]["default"]
            patches += 1
            print(f"  [check] Query.start_time: removed bogus default timestamp")

        if "end_time" in props and "default" in props["end_time"]:
            del props["end_time"]["default"]
            patches += 1
            print(f"  [check] Query.end_time: removed bogus default timestamp")

        # Override breakdowns default (spec has ["user_agent"], we want None)
        if "breakdowns" in props and props["breakdowns"].get("default"):
            props["breakdowns"]["default"] = None
            patches += 1
            print(f"  [check] Query.breakdowns: changed default from ['user_agent'] to None")

        # Override limit default (spec has 100, we want None for more flexibility)
        if "limit" in props and props["limit"].get("default"):
            props["limit"]["default"] = None
            patches += 1
            print(f"  [check] Query.limit: changed default from 100 to None")

        return patches


class ApiKeyIdPatternsPatch(BasePatch):
    """Fix API key ID validation patterns.

    The spec uses hcxik_ and hcxlk_ but actual API uses hcaik_ and hcalk_.
    This causes validation errors when trying to update keys.
    """

    name = "API key ID patterns"
    description = "Fixes API key ID regex patterns (hcxik_ -> hc[a-z]ik_, etc.)"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        # Check if any schema has the old patterns
        for schema in schemas.values():
            if isinstance(schema, dict) and "properties" in schema:
                props = schema["properties"]
                if "id" in props and isinstance(props["id"], dict):
                    pattern = props["id"].get("pattern", "")
                    if pattern in ["^hcxik_[a-zA-Z0-9]{26}$", "^hcxlk_[a-zA-Z0-9]{26}$"]:
                        return True
        return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0

        for schema_name, schema in list(schemas.items()):
            if not isinstance(schema, dict) or "properties" not in schema:
                continue

            props = schema["properties"]
            if "id" not in props or not isinstance(props["id"], dict):
                continue

            pattern = props["id"].get("pattern", "")

            # Fix ingest key pattern
            if pattern == "^hcxik_[a-zA-Z0-9]{26}$":
                props["id"]["pattern"] = "^hc[a-z]ik_[a-zA-Z0-9]{26}$"
                patches += 1
                print(f"  [check] {schema_name}.id: fixed ingest key pattern (hcxik_ -> hc[a-z]ik_)")

            # Fix configuration key pattern
            elif pattern == "^hcxlk_[a-zA-Z0-9]{26}$":
                props["id"]["pattern"] = "^hc[a-z]lk_[a-zA-Z0-9]{26}$"
                patches += 1
                print(f"  [check] {schema_name}.id: fixed configuration key pattern (hcxlk_ -> hc[a-z]lk_)")

        return patches


# Export all field patches
FIELD_PATCHES = [
    DatasetUpdatePayloadOptionalPatch(),
    BatchEventDataRequiredPatch(),
    BurnAlertRecipientsOptionalPatch(),
    QueryDefaultsPatch(),
    ApiKeyIdPatternsPatch(),
]

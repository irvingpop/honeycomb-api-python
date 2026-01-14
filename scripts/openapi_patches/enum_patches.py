"""Patches that add x-enum-varnames for readable enum member names.

Without these patches, datamodel-codegen generates unusable enum names
like field_ for "=" and field__ for "!=" operators.
"""

from typing import Any

from .base import BasePatch, get_schemas


class FilterOpEnumPatch(BasePatch):
    """Add x-enum-varnames to FilterOp for usable operator names."""

    name = "FilterOp enum varnames"
    description = "Adds readable names (EQUALS, NOT_EQUALS, etc.) to FilterOp enum"

    VARNAMES = [
        "EQUALS",  # "="
        "NOT_EQUALS",  # "!="
        "GREATER_THAN",  # ">"
        "GREATER_THAN_OR_EQUAL",  # ">="
        "LESS_THAN",  # "<"
        "LESS_THAN_OR_EQUAL",  # "<="
        "STARTS_WITH",  # "starts-with"
        "DOES_NOT_START_WITH",  # "does-not-start-with"
        "ENDS_WITH",  # "ends-with"
        "DOES_NOT_END_WITH",  # "does-not-end-with"
        "EXISTS",  # "exists"
        "DOES_NOT_EXIST",  # "does-not-exist"
        "CONTAINS",  # "contains"
        "DOES_NOT_CONTAIN",  # "does-not-contain"
        "IN",  # "in"
        "NOT_IN",  # "not-in"
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        return "FilterOp" in schemas and "x-enum-varnames" not in schemas.get("FilterOp", {})

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        schemas["FilterOp"]["x-enum-varnames"] = self.VARNAMES
        print(f"  [check] FilterOp: added x-enum-varnames for usable enum names")
        return 1


class HavingOpEnumPatch(BasePatch):
    """Add x-enum-varnames to HavingOp (subset of FilterOp)."""

    name = "HavingOp enum varnames"
    description = "Adds readable names to HavingOp comparison operators"

    VARNAMES = [
        "EQUALS",  # "="
        "NOT_EQUALS",  # "!="
        "GREATER_THAN",  # ">"
        "GREATER_THAN_OR_EQUAL",  # ">="
        "LESS_THAN",  # "<"
        "LESS_THAN_OR_EQUAL",  # "<="
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        return "HavingOp" in schemas and "x-enum-varnames" not in schemas.get("HavingOp", {})

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        schemas["HavingOp"]["x-enum-varnames"] = self.VARNAMES
        print(f"  [check] HavingOp: added x-enum-varnames for usable enum names")
        return 1


class TriggerThresholdOpEnumPatch(BasePatch):
    """Add x-enum-varnames to BaseTriggerThreshold.op."""

    name = "BaseTriggerThreshold.op enum varnames"
    description = "Adds readable names to trigger threshold comparison operators"

    VARNAMES = [
        "GREATER_THAN",  # ">"
        "GREATER_THAN_OR_EQUAL",  # ">="
        "LESS_THAN",  # "<"
        "LESS_THAN_OR_EQUAL",  # "<="
    ]

    EXPECTED_ENUM = [">", ">=", "<", "<="]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "BaseTrigger" not in schemas:
            return False

        threshold = schemas["BaseTrigger"].get("properties", {}).get("threshold", {})
        if not threshold:
            return False

        # Handle $ref to threshold schema
        if "$ref" in threshold:
            ref = threshold["$ref"]
            threshold_schema_name = ref.split("/")[-1]
            threshold_schema = schemas.get(threshold_schema_name, {})
        else:
            threshold_schema = threshold

        op = threshold_schema.get("properties", {}).get("op", {})
        return op.get("enum") == self.EXPECTED_ENUM and "x-enum-varnames" not in op

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        threshold = schemas["BaseTrigger"]["properties"]["threshold"]

        if "$ref" in threshold:
            ref = threshold["$ref"]
            threshold_schema_name = ref.split("/")[-1]
            threshold_schema = schemas[threshold_schema_name]
        else:
            threshold_schema = threshold

        op = threshold_schema["properties"]["op"]
        op["x-enum-varnames"] = self.VARNAMES
        print(f"  [check] BaseTriggerThreshold.op: added x-enum-varnames for usable enum names")
        return 1


class BoardViewFilterOperationEnumPatch(BasePatch):
    """Add x-enum-varnames to BoardViewFilter.operation."""

    name = "BoardViewFilter.operation enum varnames"
    description = "Adds readable names to board view filter operations"

    VARNAMES = [
        "EQUALS",  # "="
        "NOT_EQUALS",  # "!="
        "GREATER_THAN",  # ">"
        "GREATER_THAN_OR_EQUAL",  # ">="
        "LESS_THAN",  # "<"
        "LESS_THAN_OR_EQUAL",  # "<="
        "STARTS_WITH",  # "starts-with"
        "DOES_NOT_START_WITH",  # "does-not-start-with"
        "ENDS_WITH",  # "ends-with"
        "DOES_NOT_END_WITH",  # "does-not-end-with"
        "EXISTS",  # "exists"
        "DOES_NOT_EXIST",  # "does-not-exist"
        "CONTAINS",  # "contains"
        "DOES_NOT_CONTAIN",  # "does-not-contain"
        "IN",  # "in"
        "NOT_IN",  # "not-in"
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "BoardViewFilter" not in schemas:
            return False
        operation = schemas["BoardViewFilter"].get("properties", {}).get("operation", {})
        return operation and "enum" in operation and "x-enum-varnames" not in operation

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        operation = schemas["BoardViewFilter"]["properties"]["operation"]
        operation["x-enum-varnames"] = self.VARNAMES
        print(f"  [check] BoardViewFilter.operation: added x-enum-varnames for usable enum names")
        return 1


# Export all enum patches
ENUM_PATCHES = [
    FilterOpEnumPatch(),
    HavingOpEnumPatch(),
    TriggerThresholdOpEnumPatch(),
    BoardViewFilterOperationEnumPatch(),
]

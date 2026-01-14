"""Patches that restructure discriminated unions to avoid nested allOf patterns.

These patches address the fundamental spec design issue where allOf wraps oneOf
discriminated unions. This causes datamodel-codegen to generate numbered classes
even when the component schemas have proper names.

The solution is to create explicit variant schemas and replace the nested pattern
with a clean oneOf discriminator.
"""

from typing import Any

from .base import BasePatch, get_schemas


class ApiKeyCreateAttributesRestructuringPatch(BasePatch):
    """Restructure ApiKeyCreateResponse to avoid nested allOf(oneOf).

    BEFORE (problematic):
    ApiKeyCreateResponse.data.attributes:
      allOf:
        - $ref: ApiKeyAttributes  # oneOf discriminated union!
        - $ref: ApiKeySecret

    This generates:
    - AttributesAttributes(IngestKey, ApiKeySecret)
    - AttributesAttributes1(ConfigurationKey, ApiKeySecret)

    AFTER (clean):
    ApiKeyCreateResponse.data.attributes:
      oneOf:
        - $ref: IngestKeyCreateAttributes
        - $ref: ConfigurationKeyCreateAttributes
      discriminator:
        propertyName: key_type

    IngestKeyCreateAttributes:
      allOf:
        - $ref: IngestKeyAttributes
        - $ref: ApiKeySecret

    ConfigurationKeyCreateAttributes:
      allOf:
        - $ref: ConfigurationKeyAttributes
        - $ref: ApiKeySecret

    This generates clean class names with no numbered variants.
    """

    name = "Restructure ApiKeyCreateResponse discriminated union"
    description = "Creates explicit IngestKeyCreateAttributes and ConfigurationKeyCreateAttributes schemas"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "ApiKeyCreateResponse" not in schemas:
            return False

        # Check if already restructured
        if "IngestKeyCreateAttributes" in schemas or "ConfigurationKeyCreateAttributes" in schemas:
            return False

        # Check if the nested allOf(oneOf) pattern exists
        try:
            data_props = schemas["ApiKeyCreateResponse"]["properties"]["data"]["properties"]
            attributes = data_props.get("attributes", {})
            all_of = attributes.get("allOf", [])

            # Should have both ApiKeyAttributes ref and ApiKeySecret ref
            has_api_key_ref = any(
                isinstance(item, dict) and item.get("$ref") == "#/components/schemas/ApiKeyAttributes"
                for item in all_of
            )
            has_secret_ref = any(
                isinstance(item, dict) and item.get("$ref") == "#/components/schemas/ApiKeySecret"
                for item in all_of
            )

            return has_api_key_ref and has_secret_ref
        except (KeyError, TypeError):
            return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0

        # 1. Create IngestKeyCreateAttributes
        schemas["IngestKeyCreateAttributes"] = {
            "title": "Ingest Key Create Attributes",
            "allOf": [
                {"$ref": "#/components/schemas/IngestKeyAttributes"},
                {"$ref": "#/components/schemas/ApiKeySecret"},
            ],
        }
        patches += 1
        print(f"  [check] Created IngestKeyCreateAttributes schema")

        # 2. Create ConfigurationKeyCreateAttributes
        schemas["ConfigurationKeyCreateAttributes"] = {
            "title": "Configuration Key Create Attributes",
            "allOf": [
                {"$ref": "#/components/schemas/ConfigurationKeyAttributes"},
                {"$ref": "#/components/schemas/ApiKeySecret"},
            ],
        }
        patches += 1
        print(f"  [check] Created ConfigurationKeyCreateAttributes schema")

        # 3. Replace the nested allOf with a clean oneOf discriminator
        data_props = schemas["ApiKeyCreateResponse"]["properties"]["data"]["properties"]
        data_props["attributes"] = {
            "oneOf": [
                {"$ref": "#/components/schemas/IngestKeyCreateAttributes"},
                {"$ref": "#/components/schemas/ConfigurationKeyCreateAttributes"},
            ],
            "discriminator": {
                "propertyName": "key_type",
                "mapping": {
                    "ingest": "#/components/schemas/IngestKeyCreateAttributes",
                    "configuration": "#/components/schemas/ConfigurationKeyCreateAttributes",
                },
            },
        }
        patches += 1
        print(f"  [check] ApiKeyCreateResponse.data.attributes: replaced allOf(oneOf) with oneOf discriminator")

        return patches


# Export all discriminator restructuring patches
DISCRIMINATOR_RESTRUCTURING_PATCHES = [
    ApiKeyCreateAttributesRestructuringPatch(),
]

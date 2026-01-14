"""Patches that extract inline schemas to named schemas.

These patches address the root cause of numbered class names (AttributesAttributes1,
BudgetRate1, etc.) by extracting inline schemas from allOf patterns into properly
named schemas in components/schemas.

Without these patches, datamodel-codegen generates numbered classes because inline
objects in allOf don't have names.
"""

from typing import Any

from .base import BasePatch, get_schemas


class ApiKeySecretExtractionPatch(BasePatch):
    """Extract ApiKeySecret schema from ApiKeyCreateResponse.

    The API key create response uses allOf to combine ApiKeyAttributes with
    an inline object containing the secret field. This generates:
    - AttributesAttributes (base with secret)
    - AttributesAttributes1 (IngestKey + secret)
    - AttributesAttributes2 (ConfigurationKey + secret)

    This patch extracts the inline object to a named ApiKeySecret schema,
    resulting in cleaner class names.
    """

    name = "Extract ApiKeySecret schema"
    description = "Extracts inline secret object from ApiKeyCreateResponse to named schema"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "ApiKeyCreateResponse" not in schemas:
            return False

        # Check if the inline object exists (hasn't been extracted yet)
        try:
            data_props = schemas["ApiKeyCreateResponse"]["properties"]["data"]["properties"]
            attributes = data_props.get("attributes", {})
            all_of = attributes.get("allOf", [])

            # Look for inline object (not a $ref)
            for item in all_of:
                if isinstance(item, dict) and "$ref" not in item and "properties" in item:
                    if "secret" in item.get("properties", {}):
                        return True
        except (KeyError, TypeError):
            pass

        return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0

        # 1. Find and extract the inline secret object
        data_props = schemas["ApiKeyCreateResponse"]["properties"]["data"]["properties"]
        attributes = data_props["attributes"]
        all_of = attributes["allOf"]

        inline_secret = None
        api_key_ref = None

        for item in all_of:
            if isinstance(item, dict):
                if "$ref" in item:
                    api_key_ref = item
                elif "properties" in item and "secret" in item.get("properties", {}):
                    inline_secret = item

        if inline_secret is None:
            return 0

        # 2. Create the named ApiKeySecret schema
        schemas["ApiKeySecret"] = {
            "type": "object",
            "required": inline_secret.get("required", []),
            "properties": inline_secret["properties"],
        }
        patches += 1
        print(f"  [check] Created ApiKeySecret schema from inline object")

        # 3. Replace the inline object with a $ref
        attributes["allOf"] = [
            api_key_ref,
            {"$ref": "#/components/schemas/ApiKeySecret"},
        ]
        patches += 1
        print(f"  [check] ApiKeyCreateResponse.data.attributes: replaced inline with $ref")

        return patches


class BurnAlertDetailRecipientsExtractionPatch(BasePatch):
    """Extract BurnAlertDetailRecipients schema from burn alert detail responses.

    Both ExhaustionTimeBurnAlertDetailResponse and BudgetRateBurnAlertDetailResponse
    use allOf with an inline recipients object. This generates:
    - ExhaustionTime1
    - BudgetRate1

    This patch extracts the inline object to a shared BurnAlertDetailRecipients schema.
    """

    name = "Extract BurnAlertDetailRecipients schema"
    description = "Extracts inline recipients object from burn alert detail responses"

    DETAIL_RESPONSE_SCHEMAS = [
        "ExhaustionTimeBurnAlertDetailResponse",
        "BudgetRateBurnAlertDetailResponse",
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)

        for schema_name in self.DETAIL_RESPONSE_SCHEMAS:
            if schema_name not in schemas:
                continue

            all_of = schemas[schema_name].get("allOf", [])
            for item in all_of:
                if isinstance(item, dict) and "$ref" not in item:
                    props = item.get("properties", {})
                    if "recipients" in props:
                        return True

        return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0
        recipients_schema_created = False

        for schema_name in self.DETAIL_RESPONSE_SCHEMAS:
            if schema_name not in schemas:
                continue

            schema = schemas[schema_name]
            all_of = schema.get("allOf", [])

            base_ref = None
            inline_recipients = None

            for item in all_of:
                if isinstance(item, dict):
                    if "$ref" in item:
                        base_ref = item
                    elif "properties" in item and "recipients" in item.get("properties", {}):
                        inline_recipients = item

            if inline_recipients is None or base_ref is None:
                continue

            # Create the shared schema once
            if not recipients_schema_created:
                schemas["BurnAlertDetailRecipients"] = {
                    "type": "object",
                    "properties": inline_recipients["properties"],
                }
                recipients_schema_created = True
                patches += 1
                print(f"  [check] Created BurnAlertDetailRecipients schema from inline object")

            # Replace inline with $ref
            schema["allOf"] = [
                base_ref,
                {"$ref": "#/components/schemas/BurnAlertDetailRecipients"},
            ]
            patches += 1
            print(f"  [check] {schema_name}: replaced inline recipients with $ref")

        return patches


class BurnAlertListSloExtractionPatch(BasePatch):
    """Extract BurnAlertListSlo schema from burn alert list responses.

    Both ExhaustionTimeBurnAlertListResponse and BudgetRateBurnAlertListResponse
    use allOf with an inline slo object. This generates numbered variants like:
    - BudgetRate1

    This patch extracts the inline object to a shared BurnAlertListSlo schema.
    """

    name = "Extract BurnAlertListSlo schema"
    description = "Extracts inline slo object from burn alert list responses"

    LIST_RESPONSE_SCHEMAS = [
        "ExhaustionTimeBurnAlertListResponse",
        "BudgetRateBurnAlertListResponse",
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)

        for schema_name in self.LIST_RESPONSE_SCHEMAS:
            if schema_name not in schemas:
                continue

            all_of = schemas[schema_name].get("allOf", [])
            for item in all_of:
                if isinstance(item, dict) and "$ref" not in item:
                    props = item.get("properties", {})
                    if "slo" in props:
                        return True

        return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0
        slo_schema_created = False

        for schema_name in self.LIST_RESPONSE_SCHEMAS:
            if schema_name not in schemas:
                continue

            schema = schemas[schema_name]
            all_of = schema.get("allOf", [])

            base_ref = None
            inline_slo = None

            for item in all_of:
                if isinstance(item, dict):
                    if "$ref" in item:
                        base_ref = item
                    elif "properties" in item and "slo" in item.get("properties", {}):
                        inline_slo = item

            if inline_slo is None or base_ref is None:
                continue

            # Create the shared schema once
            if not slo_schema_created:
                schemas["BurnAlertListSlo"] = {
                    "type": "object",
                    "properties": inline_slo["properties"],
                }
                slo_schema_created = True
                patches += 1
                print(f"  [check] Created BurnAlertListSlo schema from inline object")

            # Replace inline with $ref
            schema["allOf"] = [
                base_ref,
                {"$ref": "#/components/schemas/BurnAlertListSlo"},
            ]
            patches += 1
            print(f"  [check] {schema_name}: replaced inline slo with $ref")

        return patches


# Export all schema extraction patches
SCHEMA_EXTRACTION_PATCHES = [
    ApiKeySecretExtractionPatch(),
    BurnAlertListSloExtractionPatch(),  # List responses before detail (order matters)
    BurnAlertDetailRecipientsExtractionPatch(),
]

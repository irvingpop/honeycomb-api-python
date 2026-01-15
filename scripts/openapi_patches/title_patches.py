"""Patches that add or fix titles on inline schemas.

These patches ensure datamodel-codegen generates semantic class names
instead of auto-numbered names (Type1, Details1, etc.) when using
--use-title-as-name.
"""

from typing import Any

from .base import BasePatch, get_schemas, logger


class CreateColumnTypeTitlePatch(BasePatch):
    """Add title to CreateColumn.type enum for clean enum naming."""

    name = "CreateColumn.type title"
    description = "Adds title 'ColumnType' to CreateColumn.type enum"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "CreateColumn" not in schemas:
            return False
        props = schemas["CreateColumn"].get("properties", {})
        return "type" in props and "title" not in props["type"]

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        schemas["CreateColumn"]["properties"]["type"]["title"] = "ColumnType"
        logger.info("CreateColumn.type -> ColumnType")
        return 1


class RecipientDetailsTitlePatch(BasePatch):
    """Add titles to recipient details objects for clean class naming."""

    name = "Recipient details titles"
    description = "Adds {Type}RecipientDetails titles to inline recipient detail schemas"

    RECIPIENT_TYPES = [
        "PagerDuty",
        "Email",
        "Slack",
        "Webhook",
        "MSTeams",
        "MSTeamsWorkflow",
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        for recipient_type in self.RECIPIENT_TYPES:
            schema_name = f"{recipient_type}Recipient"
            if schema_name in schemas:
                return True
        return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0

        for recipient_type in self.RECIPIENT_TYPES:
            schema_name = f"{recipient_type}Recipient"
            if schema_name not in schemas:
                continue

            all_of = schemas[schema_name].get("allOf", [])
            for item in all_of:
                if not isinstance(item, dict):
                    continue
                if "properties" not in item:
                    continue
                if "details" not in item["properties"]:
                    continue

                details = item["properties"]["details"]
                if "title" not in details:
                    details["title"] = f"{recipient_type}RecipientDetails"
                    patches += 1
                    logger.info(f"{schema_name}.details -> {recipient_type}RecipientDetails")

        return patches


class RecipientDetailsAdditionalPropertiesPatch(BasePatch):
    """Add additionalProperties: false to recipient details for strict validation.

    This prevents LLMs from hallucinating extra fields when generating recipient data.
    """

    name = "Recipient details additionalProperties"
    description = "Adds additionalProperties=false to recipient detail schemas"

    RECIPIENT_TYPES = [
        "PagerDuty",
        "Email",
        "Slack",
        "Webhook",
        "MSTeams",
        "MSTeamsWorkflow",
    ]

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        for recipient_type in self.RECIPIENT_TYPES:
            schema_name = f"{recipient_type}Recipient"
            if schema_name in schemas:
                return True
        return False

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0

        for recipient_type in self.RECIPIENT_TYPES:
            schema_name = f"{recipient_type}Recipient"
            if schema_name not in schemas:
                continue

            all_of = schemas[schema_name].get("allOf", [])
            for item in all_of:
                if not isinstance(item, dict):
                    continue
                if "properties" not in item:
                    continue
                if "details" not in item["properties"]:
                    continue

                details = item["properties"]["details"]
                if "additionalProperties" not in details:
                    details["additionalProperties"] = False
                    patches += 1
                    logger.info(f"{schema_name}.details: added additionalProperties=false")

        return patches


class UpdateBudgetRateBurnAlertTitlePatch(BasePatch):
    """Fix UpdateBudgetRateBurnAlertRequest title to avoid conflict."""

    name = "UpdateBudgetRateBurnAlertRequest title"
    description = "Changes title from 'Budget Rate' to 'UpdateBudgetRateBurnAlert'"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "UpdateBudgetRateBurnAlertRequest" not in schemas:
            return False
        return schemas["UpdateBudgetRateBurnAlertRequest"].get("title") == "Budget Rate"

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        schemas["UpdateBudgetRateBurnAlertRequest"]["title"] = "UpdateBudgetRateBurnAlert"
        logger.info("UpdateBudgetRateBurnAlertRequest: changed title to 'UpdateBudgetRateBurnAlert'")
        return 1


class BudgetRateBurnAlertListResponseTitlePatch(BasePatch):
    """Fix BudgetRateBurnAlertListResponse title to avoid conflict with BudgetRateBurnAlert.

    BudgetRateBurnAlert has title "Budget Rate" which generates the BudgetRate class.
    BudgetRateBurnAlertListResponse also has title "Budget Rate", causing a conflict
    that results in BudgetRate1.
    """

    name = "BudgetRateBurnAlertListResponse title"
    description = "Changes title from 'Budget Rate' to 'Budget Rate List Response'"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "BudgetRateBurnAlertListResponse" not in schemas:
            return False
        return schemas["BudgetRateBurnAlertListResponse"].get("title") == "Budget Rate"

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        schemas["BudgetRateBurnAlertListResponse"]["title"] = "Budget Rate List Response"
        logger.info("BudgetRateBurnAlertListResponse: changed title to 'Budget Rate List Response'")
        return 1


class ExhaustionTimeBurnAlertDetailResponseTitlePatch(BasePatch):
    """Fix ExhaustionTimeBurnAlertDetailResponse title to avoid conflict.

    ExhaustionTimeBurnAlert has title "Exhaustion Time" which generates the ExhaustionTime class.
    ExhaustionTimeBurnAlertDetailResponse also has title "Exhaustion Time", causing a conflict
    that results in ExhaustionTime1.
    """

    name = "ExhaustionTimeBurnAlertDetailResponse title"
    description = "Changes title from 'Exhaustion Time' to 'Exhaustion Time Detail Response'"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "ExhaustionTimeBurnAlertDetailResponse" not in schemas:
            return False
        return schemas["ExhaustionTimeBurnAlertDetailResponse"].get("title") == "Exhaustion Time"

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        schemas["ExhaustionTimeBurnAlertDetailResponse"]["title"] = "Exhaustion Time Detail Response"
        print(
            f"  [check] ExhaustionTimeBurnAlertDetailResponse: changed title to 'Exhaustion Time Detail Response'"
        )
        return 1


class BoardViewFilterOperationTitlePatch(BasePatch):
    """Add title to BoardViewFilter.operation for clean enum naming."""

    name = "BoardViewFilter.operation title"
    description = "Adds title 'BoardViewFilterOperation' to the operation enum"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        if "BoardViewFilter" not in schemas:
            return False
        operation = schemas["BoardViewFilter"].get("properties", {}).get("operation", {})
        return operation and "enum" in operation and "title" not in operation

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        operation = schemas["BoardViewFilter"]["properties"]["operation"]
        operation["title"] = "BoardViewFilterOperation"
        logger.info("BoardViewFilter.operation: added title 'BoardViewFilterOperation'")
        return 1


class ApiKeyRequestTitlesPatch(BasePatch):
    """Fix titles on IngestKeyRequest and ConfigurationKeyRequest.

    DMCG generates IngestKey1/ConfigurationKey1 because the default titles
    conflict with IngestKey/ConfigurationKey. Change titles to unique names.
    """

    name = "API key request titles"
    description = "Changes IngestKeyRequest/ConfigurationKeyRequest titles to *Update variants"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        schemas = get_schemas(spec)
        return "IngestKeyRequest" in schemas or "ConfigurationKeyRequest" in schemas

    def apply(self, spec: dict[str, Any]) -> int:
        schemas = get_schemas(spec)
        patches = 0

        if "IngestKeyRequest" in schemas:
            schemas["IngestKeyRequest"]["title"] = "IngestKeyUpdate"
            patches += 1
            logger.info("IngestKeyRequest: changed title to 'IngestKeyUpdate'")

        if "ConfigurationKeyRequest" in schemas:
            schemas["ConfigurationKeyRequest"]["title"] = "ConfigurationKeyUpdate"
            patches += 1
            logger.info("ConfigurationKeyRequest: changed title to 'ConfigurationKeyUpdate'")

        return patches


# Export all title patches
TITLE_PATCHES = [
    CreateColumnTypeTitlePatch(),
    RecipientDetailsTitlePatch(),
    RecipientDetailsAdditionalPropertiesPatch(),
    UpdateBudgetRateBurnAlertTitlePatch(),
    BudgetRateBurnAlertListResponseTitlePatch(),
    ExhaustionTimeBurnAlertDetailResponseTitlePatch(),
    BoardViewFilterOperationTitlePatch(),
    ApiKeyRequestTitlesPatch(),
]

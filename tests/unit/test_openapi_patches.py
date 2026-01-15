"""Unit tests for OpenAPI spec patches.

These tests verify that each patch correctly modifies the spec structure
without requiring the full spec file.
"""

import copy
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from openapi_patches import ALL_PATCHES, get_schemas
from openapi_patches.base import logger as patch_logger
from openapi_patches.discriminator_restructuring import (
    ApiKeyCreateAttributesRestructuringPatch,
)
from openapi_patches.enum_patches import (
    FilterOpEnumPatch,
    HavingOpEnumPatch,
    TriggerThresholdOpEnumPatch,
)
from openapi_patches.field_patches import (
    ApiKeyIdPatternsPatch,
    BatchEventDataRequiredPatch,
    DatasetUpdatePayloadOptionalPatch,
)
from openapi_patches.schema_extraction import (
    ApiKeySecretExtractionPatch,
    BurnAlertDetailRecipientsExtractionPatch,
    BurnAlertListSloExtractionPatch,
)
from openapi_patches.title_patches import (
    ApiKeyRequestTitlesPatch,
    CreateColumnTypeTitlePatch,
    RecipientDetailsTitlePatch,
)


@pytest.fixture(autouse=True)
def suppress_patch_logging():
    """Suppress patch logger output during tests."""
    patch_logger.disabled = True
    yield
    patch_logger.disabled = False


class TestBasePatch:
    """Test base patch functionality."""

    def test_get_schemas_creates_structure(self):
        """get_schemas should create components/schemas if missing."""
        spec = {}
        schemas = get_schemas(spec)
        assert schemas == {}
        assert spec == {"components": {"schemas": {}}}

    def test_get_schemas_returns_existing(self):
        """get_schemas should return existing schemas dict."""
        spec = {"components": {"schemas": {"Foo": {"type": "object"}}}}
        schemas = get_schemas(spec)
        assert "Foo" in schemas


class TestTitlePatches:
    """Test title patches."""

    def test_create_column_type_title(self):
        """CreateColumnTypeTitlePatch adds title to CreateColumn.type."""
        spec = {
            "components": {
                "schemas": {
                    "CreateColumn": {"properties": {"type": {"enum": ["string", "integer"]}}}
                }
            }
        }
        patch = CreateColumnTypeTitlePatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1
        assert (
            spec["components"]["schemas"]["CreateColumn"]["properties"]["type"]["title"]
            == "ColumnType"
        )

    def test_create_column_type_title_already_present(self):
        """CreateColumnTypeTitlePatch skips if title already present."""
        spec = {
            "components": {
                "schemas": {"CreateColumn": {"properties": {"type": {"title": "ExistingTitle"}}}}
            }
        }
        patch = CreateColumnTypeTitlePatch()
        assert not patch.applies_to(spec)

    def test_recipient_details_title(self):
        """RecipientDetailsTitlePatch adds titles to recipient details."""
        spec = {
            "components": {
                "schemas": {
                    "EmailRecipient": {
                        "allOf": [
                            {"$ref": "#/components/schemas/BaseRecipient"},
                            {"properties": {"details": {"type": "object"}}},
                        ]
                    }
                }
            }
        }
        patch = RecipientDetailsTitlePatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1
        details = spec["components"]["schemas"]["EmailRecipient"]["allOf"][1]["properties"][
            "details"
        ]
        assert details["title"] == "EmailRecipientDetails"

    def test_api_key_request_titles(self):
        """ApiKeyRequestTitlesPatch changes request titles to *Update."""
        spec = {
            "components": {
                "schemas": {
                    "IngestKeyRequest": {"type": "object"},
                    "ConfigurationKeyRequest": {"type": "object"},
                }
            }
        }
        patch = ApiKeyRequestTitlesPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 2
        assert spec["components"]["schemas"]["IngestKeyRequest"]["title"] == "IngestKeyUpdate"
        assert (
            spec["components"]["schemas"]["ConfigurationKeyRequest"]["title"]
            == "ConfigurationKeyUpdate"
        )


class TestEnumPatches:
    """Test enum patches."""

    def test_filter_op_enum(self):
        """FilterOpEnumPatch adds x-enum-varnames."""
        spec = {"components": {"schemas": {"FilterOp": {"enum": ["=", "!="]}}}}
        patch = FilterOpEnumPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1
        assert "x-enum-varnames" in spec["components"]["schemas"]["FilterOp"]

    def test_having_op_enum(self):
        """HavingOpEnumPatch adds x-enum-varnames."""
        spec = {"components": {"schemas": {"HavingOp": {"enum": ["=", "!="]}}}}
        patch = HavingOpEnumPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1
        assert "x-enum-varnames" in spec["components"]["schemas"]["HavingOp"]

    def test_trigger_threshold_op_enum(self):
        """TriggerThresholdOpEnumPatch adds x-enum-varnames."""
        spec = {
            "components": {
                "schemas": {
                    "BaseTrigger": {
                        "properties": {
                            "threshold": {"properties": {"op": {"enum": [">", ">=", "<", "<="]}}}
                        }
                    }
                }
            }
        }
        patch = TriggerThresholdOpEnumPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1


class TestFieldPatches:
    """Test field patches."""

    def test_dataset_update_optional(self):
        """DatasetUpdatePayloadOptionalPatch removes required."""
        spec = {"components": {"schemas": {"DatasetUpdatePayload": {"required": ["name"]}}}}
        patch = DatasetUpdatePayloadOptionalPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1
        assert "required" not in spec["components"]["schemas"]["DatasetUpdatePayload"]

    def test_batch_event_data_required(self):
        """BatchEventDataRequiredPatch adds data to required."""
        spec = {"components": {"schemas": {"BatchEvent": {"type": "object"}}}}
        patch = BatchEventDataRequiredPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1
        assert "data" in spec["components"]["schemas"]["BatchEvent"]["required"]

    def test_api_key_id_patterns(self):
        """ApiKeyIdPatternsPatch fixes ID patterns."""
        spec = {
            "components": {
                "schemas": {
                    "IngestKeyRequest": {
                        "properties": {"id": {"pattern": "^hcxik_[a-zA-Z0-9]{26}$"}}
                    }
                }
            }
        }
        patch = ApiKeyIdPatternsPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 1
        assert (
            spec["components"]["schemas"]["IngestKeyRequest"]["properties"]["id"]["pattern"]
            == "^hc[a-z]ik_[a-zA-Z0-9]{26}$"
        )


class TestSchemaExtractionPatches:
    """Test schema extraction patches."""

    def test_api_key_secret_extraction(self):
        """ApiKeySecretExtractionPatch extracts secret to named schema."""
        spec = {
            "components": {
                "schemas": {
                    "ApiKeyCreateResponse": {
                        "properties": {
                            "data": {
                                "properties": {
                                    "attributes": {
                                        "allOf": [
                                            {"$ref": "#/components/schemas/ApiKeyAttributes"},
                                            {
                                                "type": "object",
                                                "required": ["secret"],
                                                "properties": {"secret": {"type": "string"}},
                                            },
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        patch = ApiKeySecretExtractionPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 2  # Create schema + replace inline

        schemas = spec["components"]["schemas"]
        assert "ApiKeySecret" in schemas
        assert schemas["ApiKeySecret"]["properties"]["secret"]["type"] == "string"

        attributes = schemas["ApiKeyCreateResponse"]["properties"]["data"]["properties"][
            "attributes"
        ]
        assert len(attributes["allOf"]) == 2
        assert attributes["allOf"][1] == {"$ref": "#/components/schemas/ApiKeySecret"}

    def test_api_key_secret_already_extracted(self):
        """ApiKeySecretExtractionPatch skips if already extracted."""
        spec = {
            "components": {
                "schemas": {
                    "ApiKeyCreateResponse": {
                        "properties": {
                            "data": {
                                "properties": {
                                    "attributes": {
                                        "allOf": [
                                            {"$ref": "#/components/schemas/ApiKeyAttributes"},
                                            {"$ref": "#/components/schemas/ApiKeySecret"},
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    "ApiKeySecret": {"type": "object"},
                }
            }
        }
        patch = ApiKeySecretExtractionPatch()
        assert not patch.applies_to(spec)

    def test_burn_alert_list_slo_extraction(self):
        """BurnAlertListSloExtractionPatch extracts slo to named schema."""
        spec = {
            "components": {
                "schemas": {
                    "ExhaustionTimeBurnAlertListResponse": {
                        "allOf": [
                            {"$ref": "#/components/schemas/ExhaustionTimeBurnAlert"},
                            {
                                "properties": {
                                    "slo": {
                                        "type": "object",
                                        "properties": {"id": {"type": "string"}},
                                    }
                                }
                            },
                        ]
                    },
                    "BudgetRateBurnAlertListResponse": {
                        "allOf": [
                            {"$ref": "#/components/schemas/BudgetRateBurnAlert"},
                            {
                                "properties": {
                                    "slo": {
                                        "type": "object",
                                        "properties": {"id": {"type": "string"}},
                                    }
                                }
                            },
                        ]
                    },
                }
            }
        }
        patch = BurnAlertListSloExtractionPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 3  # Create schema + replace 2 inline

        schemas = spec["components"]["schemas"]
        assert "BurnAlertListSlo" in schemas
        assert schemas["ExhaustionTimeBurnAlertListResponse"]["allOf"][1] == {
            "$ref": "#/components/schemas/BurnAlertListSlo"
        }
        assert schemas["BudgetRateBurnAlertListResponse"]["allOf"][1] == {
            "$ref": "#/components/schemas/BurnAlertListSlo"
        }

    def test_burn_alert_detail_recipients_extraction(self):
        """BurnAlertDetailRecipientsExtractionPatch extracts recipients to named schema."""
        spec = {
            "components": {
                "schemas": {
                    "ExhaustionTimeBurnAlertDetailResponse": {
                        "allOf": [
                            {"$ref": "#/components/schemas/ExhaustionTimeBurnAlertListResponse"},
                            {"properties": {"recipients": {"type": "array"}}},
                        ]
                    },
                    "BudgetRateBurnAlertDetailResponse": {
                        "allOf": [
                            {"$ref": "#/components/schemas/BudgetRateBurnAlertListResponse"},
                            {"properties": {"recipients": {"type": "array"}}},
                        ]
                    },
                }
            }
        }
        patch = BurnAlertDetailRecipientsExtractionPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 3  # Create schema + replace 2 inline

        schemas = spec["components"]["schemas"]
        assert "BurnAlertDetailRecipients" in schemas


class TestDiscriminatorRestructuringPatches:
    """Test discriminator restructuring patches."""

    def test_api_key_create_attributes_restructuring(self):
        """ApiKeyCreateAttributesRestructuringPatch eliminates numbered classes."""
        spec = {
            "components": {
                "schemas": {
                    "ApiKeySecret": {
                        "type": "object",
                        "properties": {"secret": {"type": "string"}},
                    },
                    "IngestKeyAttributes": {"type": "object"},
                    "ConfigurationKeyAttributes": {"type": "object"},
                    "ApiKeyCreateResponse": {
                        "properties": {
                            "data": {
                                "properties": {
                                    "attributes": {
                                        "allOf": [
                                            {"$ref": "#/components/schemas/ApiKeyAttributes"},
                                            {"$ref": "#/components/schemas/ApiKeySecret"},
                                        ]
                                    }
                                }
                            }
                        }
                    },
                }
            }
        }
        patch = ApiKeyCreateAttributesRestructuringPatch()
        assert patch.applies_to(spec)
        changes = patch.apply(spec)
        assert changes == 3  # Create 2 schemas + restructure

        schemas = spec["components"]["schemas"]
        assert "IngestKeyCreateAttributes" in schemas
        assert "ConfigurationKeyCreateAttributes" in schemas

        # Should be oneOf, not allOf
        attributes = schemas["ApiKeyCreateResponse"]["properties"]["data"]["properties"][
            "attributes"
        ]
        assert "oneOf" in attributes
        assert "discriminator" in attributes
        assert attributes["discriminator"]["propertyName"] == "key_type"

    def test_api_key_create_already_restructured(self):
        """ApiKeyCreateAttributesRestructuringPatch skips if already restructured."""
        spec = {
            "components": {
                "schemas": {
                    "IngestKeyCreateAttributes": {"type": "object"},
                    "ApiKeyCreateResponse": {"type": "object"},
                }
            }
        }
        patch = ApiKeyCreateAttributesRestructuringPatch()
        assert not patch.applies_to(spec)


class TestAllPatches:
    """Integration tests for all patches together."""

    def test_patches_are_idempotent(self):
        """Patches should not break if applied twice."""
        spec = {
            "components": {
                "schemas": {
                    "FilterOp": {"enum": ["=", "!="]},
                }
            }
        }

        # Apply all patches twice
        for patch in ALL_PATCHES:
            patch(spec)
        first_result = copy.deepcopy(spec)

        for patch in ALL_PATCHES:
            patch(spec)
        second_result = spec

        # Results should be the same (idempotent)
        assert first_result == second_result

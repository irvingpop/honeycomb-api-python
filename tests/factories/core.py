"""Factories for core Honeycomb models (Environment, Dataset, ApiKey)."""

from honeycomb._generated_models import (
    ApiKeyObjectType,
    ConfigurationKey,
    ConfigurationKeyPermissions,
    CreateEnvironmentRequest,
    CreateEnvironmentRequestData,
    CreateEnvironmentRequestDataAttributes,
    DatasetSettings,
    EnvironmentAttributes,
    EnvironmentAttributesSettings,
    EnvironmentColor,
    EnvironmentLinks,
    EnvironmentRelationshipDataType,
    IngestKey,
    Permissions,
)
from honeycomb.models import ApiKeyObject, Dataset, DatasetCreate, DatasetUpdate, Environment

from .base import HoneycombFactory

# =============================================================================
# Dataset Factories
# =============================================================================


class DatasetSettingsFactory(HoneycombFactory):
    """Factory for DatasetSettings."""

    __model__ = DatasetSettings


class DatasetFactory(HoneycombFactory):
    """Factory for Dataset response model.

    Example:
        dataset = DatasetFactory.build(name="my-dataset")
        datasets = DatasetFactory.batch(5)
    """

    __model__ = Dataset

    name = lambda: f"test-dataset-{HoneycombFactory._honeycomb_id()}"
    slug = lambda: f"test-dataset-{HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test dataset"


class DatasetCreateFactory(HoneycombFactory):
    """Factory for DatasetCreate request model."""

    __model__ = DatasetCreate

    name = lambda: f"test-dataset-{HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test dataset"


class DatasetUpdateFactory(HoneycombFactory):
    """Factory for DatasetUpdate request model."""

    __model__ = DatasetUpdate

    description = lambda: "Updated description"


# =============================================================================
# Environment Factories (JSON:API structure)
# =============================================================================


class EnvironmentAttributesSettingsFactory(HoneycombFactory):
    """Factory for EnvironmentAttributesSettings."""

    __model__ = EnvironmentAttributesSettings

    delete_protected = False


class EnvironmentLinksFactory(HoneycombFactory):
    """Factory for EnvironmentLinks."""

    __model__ = EnvironmentLinks

    @classmethod
    def build(cls, **kwargs):
        env_id = kwargs.get("env_id", HoneycombFactory._honeycomb_id())
        return super().build(
            self=f"https://api.honeycomb.io/1/environments/{env_id}",
            **{k: v for k, v in kwargs.items() if k != "env_id"},
        )


class EnvironmentAttributesFactory(HoneycombFactory):
    """Factory for EnvironmentAttributes."""

    __model__ = EnvironmentAttributes

    name = lambda: f"Test Environment {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test environment"
    color = lambda: HoneycombFactory.__random__.choice(list(EnvironmentColor))
    slug = lambda: f"test-env-{HoneycombFactory._honeycomb_id()}"


class EnvironmentFactory(HoneycombFactory):
    """Factory for Environment response model (JSON:API structure).

    Example:
        env = EnvironmentFactory.build()
        envs = EnvironmentFactory.batch(3)
    """

    __model__ = Environment

    id = lambda: f"hxenv_{HoneycombFactory._honeycomb_id()}"
    type = EnvironmentRelationshipDataType.environments


class CreateEnvironmentRequestDataAttributesFactory(HoneycombFactory):
    """Factory for CreateEnvironmentRequestDataAttributes."""

    __model__ = CreateEnvironmentRequestDataAttributes

    name = lambda: f"Test Environment {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test environment"
    color = lambda: HoneycombFactory.__random__.choice(list(EnvironmentColor))


class CreateEnvironmentRequestDataFactory(HoneycombFactory):
    """Factory for CreateEnvironmentRequestData."""

    __model__ = CreateEnvironmentRequestData

    type = EnvironmentRelationshipDataType.environments


class EnvironmentCreateFactory(HoneycombFactory):
    """Factory for CreateEnvironmentRequest (environment creation).

    Example:
        create_req = EnvironmentCreateFactory.build()
    """

    __model__ = CreateEnvironmentRequest


# =============================================================================
# API Key Factories
# =============================================================================


class IngestKeyPermissionsFactory(HoneycombFactory):
    """Factory for Ingest Key Permissions."""

    __model__ = Permissions


class ConfigurationKeyPermissionsFactory(HoneycombFactory):
    """Factory for Configuration Key Permissions."""

    __model__ = ConfigurationKeyPermissions


class IngestKeyFactory(HoneycombFactory):
    """Factory for IngestKey attributes."""

    __model__ = IngestKey

    name = lambda: f"Test Ingest Key {HoneycombFactory._honeycomb_id()}"
    disabled = False


class ConfigurationKeyFactory(HoneycombFactory):
    """Factory for ConfigurationKey attributes."""

    __model__ = ConfigurationKey

    name = lambda: f"Test Config Key {HoneycombFactory._honeycomb_id()}"
    disabled = False


class ApiKeyObjectFactory(HoneycombFactory):
    """Factory for ApiKeyObject response model.

    Example:
        api_key = ApiKeyObjectFactory.build()
        # For ingest key specifically:
        ingest_key = ApiKeyObjectFactory.build(
            id="hcxik_123",
            attributes=IngestKeyFactory.build()
        )
    """

    __model__ = ApiKeyObject

    id = lambda: f"hcxik_{HoneycombFactory._honeycomb_id()}"
    type = ApiKeyObjectType.api_keys

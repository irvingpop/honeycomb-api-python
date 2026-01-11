"""Pydantic models for Honeycomb Datasets."""

from __future__ import annotations

from pydantic import Field

from honeycomb._generated_models import Dataset as _DatasetGenerated
from honeycomb._generated_models import DatasetCreationPayload as _DatasetCreationPayloadGenerated
from honeycomb._generated_models import DatasetUpdatePayload as _DatasetUpdatePayloadGenerated
from honeycomb._generated_models import DatasetUpdatePayloadSettings


class DatasetCreate(_DatasetCreationPayloadGenerated):
    """Model for creating a new dataset (extends generated DatasetCreationPayload)."""

    pass


class DatasetUpdate(_DatasetUpdatePayloadGenerated):
    """Model for updating an existing dataset (extends generated DatasetUpdatePayload).

    Note: The API expects delete_protected nested in 'settings':
        DatasetUpdate(settings=DatasetUpdatePayloadSettings(delete_protected=True))
    """

    # Override to add description (required for Claude tool schema generation)
    settings: DatasetUpdatePayloadSettings | None = Field(
        default=None, description="Dataset settings (e.g., delete_protected)"
    )


class Dataset(_DatasetGenerated):
    """A Honeycomb dataset (response model, extends generated Dataset)."""

    pass

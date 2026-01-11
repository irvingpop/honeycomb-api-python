"""Pydantic models for Honeycomb Markers."""

from __future__ import annotations

from honeycomb._generated_models import Marker as _MarkerGenerated
from honeycomb._generated_models import MarkerSetting as _MarkerSettingGenerated


class MarkerCreate(_MarkerGenerated):
    """Model for creating a new marker (extends generated Marker).

    Note: The API uses the same flat structure for both create and response.
    """

    pass


class Marker(_MarkerGenerated):
    """A Honeycomb marker (response model, extends generated Marker)."""

    pass


class MarkerSettingCreate(_MarkerSettingGenerated):
    """Model for creating a new marker setting (extends generated MarkerSetting).

    Note: The API uses the same structure for both create and response.
    """

    pass


class MarkerSetting(_MarkerSettingGenerated):
    """A Honeycomb marker setting (response model, extends generated MarkerSetting)."""

    pass

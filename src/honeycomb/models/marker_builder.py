"""Marker Builder - Fluent interface for creating markers."""

from __future__ import annotations

import time

from honeycomb.models.markers import MarkerCreate, MarkerSettingCreate


class MarkerBuilder:
    """Fluent builder for markers.

    Example - Point marker:
        marker = (
            MarkerBuilder("Deployed v1.2.3")
            .type("deploy")
            .url("https://github.com/org/repo/releases/v1.2.3")
            .build()
        )

    Example - Duration marker:
        marker = (
            MarkerBuilder("Maintenance window")
            .type("maintenance")
            .start_time(1703980800)
            .end_time(1703984400)
            .build()
        )

    Example - Duration from now:
        marker = (
            MarkerBuilder("Load test in progress")
            .type("test")
            .duration_minutes(30)
            .build()
        )
    """

    def __init__(self, message: str):
        self._message = message
        self._type: str | None = None
        self._start_time: int | None = None
        self._end_time: int | None = None
        self._url: str | None = None

    def type(self, marker_type: str) -> MarkerBuilder:
        """Set marker type (groups similar markers).

        Args:
            marker_type: Type identifier (e.g., "deploy", "maintenance", "incident")
        """
        self._type = marker_type
        return self

    def url(self, url: str) -> MarkerBuilder:
        """Set target URL for the marker.

        Args:
            url: URL to link to (e.g., deployment, incident, PR)
        """
        self._url = url
        return self

    def start_time(self, timestamp: int) -> MarkerBuilder:
        """Set start time as Unix timestamp.

        Args:
            timestamp: Unix timestamp in seconds
        """
        self._start_time = timestamp
        return self

    def end_time(self, timestamp: int) -> MarkerBuilder:
        """Set end time as Unix timestamp (for duration markers).

        Args:
            timestamp: Unix timestamp in seconds
        """
        self._end_time = timestamp
        return self

    def duration_minutes(self, minutes: int) -> MarkerBuilder:
        """Set duration from now.

        Args:
            minutes: Duration in minutes from current time
        """
        now = int(time.time())
        self._start_time = now
        self._end_time = now + (minutes * 60)
        return self

    def duration_hours(self, hours: int) -> MarkerBuilder:
        """Set duration from now in hours.

        Args:
            hours: Duration in hours from current time
        """
        return self.duration_minutes(hours * 60)

    @staticmethod
    def setting(marker_type: str, color: str) -> MarkerSettingCreate:
        """Create a marker setting (color configuration).

        Args:
            marker_type: Type of marker to configure
            color: Hex color code (e.g., '#F96E11')

        Returns:
            MarkerSettingCreate object

        Example:
            >>> setting = MarkerBuilder.setting("deploy", "#00FF00")
            >>> await client.markers.create_setting_async(setting)
        """
        return MarkerSettingCreate(type=marker_type, color=color)

    def build(self) -> MarkerCreate:
        """Build MarkerCreate with validation.

        Returns:
            MarkerCreate object ready to be sent to the API

        Raises:
            ValueError: If marker type is missing
        """
        if not self._type:
            raise ValueError("Marker type is required. Use type().")

        return MarkerCreate(
            message=self._message,
            type=self._type,
            start_time=self._start_time,
            end_time=self._end_time,
            url=self._url,
        )

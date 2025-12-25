"""Pydantic models for Honeycomb Events (data ingestion)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BatchEvent(BaseModel):
    """Model for a batch event."""

    data: dict[str, Any] = Field(description="Event payload (key-value pairs)")
    time: str | None = Field(
        default=None, description="Event timestamp (ISO8601 format). Defaults to server time."
    )
    samplerate: int | None = Field(default=None, description="Sample rate. Defaults to 1.")

    def model_dump_for_api(self) -> dict:
        """Serialize for API request."""
        result: dict[str, Any] = {"data": self.data}
        if self.time:
            result["time"] = self.time
        if self.samplerate:
            result["samplerate"] = self.samplerate
        return result


class BatchEventResult(BaseModel):
    """Result for a single event in a batch."""

    status: int = Field(description="HTTP status code for this event")
    error: str | None = Field(default=None, description="Error message if status != 202")

    model_config = {"extra": "allow"}

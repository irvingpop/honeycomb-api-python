"""Pydantic models for Honeycomb Events (data ingestion)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from honeycomb._generated_models import BatchEvent as _BatchEventGenerated


class BatchEvent(_BatchEventGenerated):
    """Model for a batch event.

    Extends generated BatchEvent model with no modifications.
    The spec was patched to make data field required.
    """

    pass


class BatchEventResult(BaseModel):
    """Result for a single event in a batch."""

    status: int = Field(description="HTTP status code for this event")
    error: str | None = Field(default=None, description="Error message if status != 202")

    model_config = {"extra": "allow"}

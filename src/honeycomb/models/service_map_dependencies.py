"""Pydantic models for Honeycomb Service Map Dependencies."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ServiceMapNodeType(str, Enum):
    """Type of node in the service map."""

    SERVICE = "service"


class ServiceMapNode(BaseModel):
    """A node in the service map (typically a service).

    Attributes:
        name: Name of the service or node.
        type: Type of the node. Currently only 'service' is supported.
    """

    name: str = Field(..., description="Name of the service or node")
    type: ServiceMapNodeType = Field(
        default=ServiceMapNodeType.SERVICE,
        description="Type of the node. Currently only 'service' is supported.",
    )


class ServiceMapDependency(BaseModel):
    """A dependency relationship between two services.

    Attributes:
        parent_node: The upstream service (caller).
        child_node: The downstream service (callee).
        call_count: Number of calls between the parent and child services.
    """

    parent_node: ServiceMapNode = Field(..., description="The upstream service (caller)")
    child_node: ServiceMapNode = Field(..., description="The downstream service (callee)")
    call_count: int = Field(..., description="Number of calls between services")


class ServiceMapDependencyRequestStatus(str, Enum):
    """Status of a Service Map Dependencies request."""

    PENDING = "pending"
    READY = "ready"
    ERROR = "error"


class ServiceMapDependencyRequestCreate(BaseModel):
    """Request to create a Service Map Dependencies query.

    Time range can be specified in several ways:
    - time_range only: Seconds before now
    - start_time + time_range: Seconds after start_time
    - end_time + time_range: Seconds before end_time
    - start_time + end_time: Explicit time range

    Attributes:
        start_time: Absolute start time in seconds since UNIX epoch.
        end_time: Absolute end time in seconds since UNIX epoch.
        time_range: Time range in seconds (default: 7200 = 2 hours).
        filters: Optional list of service nodes to filter by.
    """

    start_time: int | None = Field(
        default=None,
        description="Absolute start time in seconds since UNIX epoch",
    )
    end_time: int | None = Field(
        default=None,
        description="Absolute end time in seconds since UNIX epoch",
    )
    time_range: int = Field(
        default=7200,
        ge=1,
        description="Time range in seconds (default: 7200 = 2 hours)",
    )
    filters: list[ServiceMapNode] | None = Field(
        default=None,
        description="Optional list of service nodes to filter dependencies by",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request, excluding None values."""
        data: dict[str, Any] = {"time_range": self.time_range}
        if self.start_time is not None:
            data["start_time"] = self.start_time
        if self.end_time is not None:
            data["end_time"] = self.end_time
        if self.filters:
            data["filters"] = [f.model_dump() for f in self.filters]
        return data


class ServiceMapDependencyRequest(BaseModel):
    """Response from creating a Service Map Dependencies request.

    Attributes:
        request_id: Unique identifier for the request.
        status: Status of the request (pending, ready, error).
    """

    request_id: str = Field(..., description="Unique identifier for the request")
    status: ServiceMapDependencyRequestStatus = Field(..., description="Status of the request")


class ServiceMapDependencyResult(BaseModel):
    """Result of a Service Map Dependencies query.

    Attributes:
        request_id: Unique identifier for the request.
        status: Status of the request (pending, ready, error).
        dependencies: List of service dependencies (None if pending/error).
    """

    request_id: str = Field(..., description="Unique identifier for the request")
    status: ServiceMapDependencyRequestStatus = Field(..., description="Status of the request")
    dependencies: list[ServiceMapDependency] | None = Field(
        default=None,
        description="List of service dependencies (None if pending/error)",
    )

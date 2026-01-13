"""Pydantic models for Honeycomb Service Map Dependencies.

Re-exports generated models with backward-compatible names.
"""

from honeycomb._generated_models import (
    CreateMapDependenciesRequest as _CreateMapDependenciesRequestGenerated,
)
from honeycomb._generated_models import (
    CreateMapDependenciesResponse as _CreateMapDependenciesResponseGenerated,
)
from honeycomb._generated_models import (
    CreateMapDependenciesResponseStatus,
    MapNodeType,
)
from honeycomb._generated_models import (
    GetMapDependenciesResponse as _GetMapDependenciesResponseGenerated,
)
from honeycomb._generated_models import (
    MapDependency as _MapDependencyGenerated,
)
from honeycomb._generated_models import (
    MapNode as _MapNodeGenerated,
)

# Re-export enums with backward-compatible names
ServiceMapNodeType = MapNodeType
ServiceMapDependencyRequestStatus = CreateMapDependenciesResponseStatus


class ServiceMapNode(_MapNodeGenerated):
    """A node in the service map (extends generated MapNode).

    Attributes:
        name: Name of the service or node.
        type: Type of the node. Currently only 'service' is supported.
    """

    pass


class ServiceMapDependency(_MapDependencyGenerated):
    """A dependency relationship between two services (extends generated).

    Attributes:
        parent_node: The upstream service (caller).
        child_node: The downstream service (callee).
        call_count: Number of calls between the parent and child services.
    """

    pass


class ServiceMapDependencyRequestCreate(_CreateMapDependenciesRequestGenerated):
    """Request to create a Service Map Dependencies query (extends generated).

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

    pass


class ServiceMapDependencyRequest(_CreateMapDependenciesResponseGenerated):
    """Response from creating a Service Map Dependencies request (extends generated).

    Attributes:
        request_id: Unique identifier for the request.
        status: Status of the request (pending, ready, error).
    """

    pass


class ServiceMapDependencyResult(_GetMapDependenciesResponseGenerated):
    """Result of a Service Map Dependencies query (extends generated).

    Attributes:
        request_id: Unique identifier for the request.
        status: Status of the request (pending, ready, error).
        dependencies: List of service dependencies (None if pending/error).
    """

    pass


__all__ = [
    "ServiceMapDependency",
    "ServiceMapDependencyRequest",
    "ServiceMapDependencyRequestCreate",
    "ServiceMapDependencyRequestStatus",
    "ServiceMapDependencyResult",
    "ServiceMapNode",
    "ServiceMapNodeType",
]

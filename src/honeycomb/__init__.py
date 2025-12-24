"""Honeycomb API client for Python."""

__version__ = "0.1.0"

from .auth import APIKeyAuth, AuthStrategy, ManagementKeyAuth, create_auth
from .client import HoneycombClient, RateLimitInfo, RetryConfig
from .exceptions import (
    HoneycombAPIError,
    HoneycombAuthError,
    HoneycombConnectionError,
    HoneycombForbiddenError,
    HoneycombNotFoundError,
    HoneycombRateLimitError,
    HoneycombServerError,
    HoneycombTimeoutError,
    HoneycombValidationError,
)
from .models import (
    SLI,
    SLO,
    Board,
    BoardCreate,
    Dataset,
    DatasetCreate,
    Query,
    QueryCalculation,
    QueryFilter,
    QueryResult,
    QuerySpec,
    SLOCreate,
    Trigger,
    TriggerAlertType,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)

__all__ = [
    "__version__",
    # Client
    "HoneycombClient",
    "RetryConfig",
    "RateLimitInfo",
    # Auth
    "AuthStrategy",
    "APIKeyAuth",
    "ManagementKeyAuth",
    "create_auth",
    # Exceptions
    "HoneycombAPIError",
    "HoneycombAuthError",
    "HoneycombForbiddenError",
    "HoneycombNotFoundError",
    "HoneycombValidationError",
    "HoneycombRateLimitError",
    "HoneycombServerError",
    "HoneycombTimeoutError",
    "HoneycombConnectionError",
    # Models - Triggers
    "Trigger",
    "TriggerCreate",
    "TriggerThreshold",
    "TriggerThresholdOp",
    "TriggerAlertType",
    "TriggerQuery",
    "QueryCalculation",
    "QueryFilter",
    # Models - SLOs
    "SLO",
    "SLOCreate",
    "SLI",
    # Models - Datasets
    "Dataset",
    "DatasetCreate",
    # Models - Boards
    "Board",
    "BoardCreate",
    # Models - Queries
    "Query",
    "QuerySpec",
    "QueryResult",
]

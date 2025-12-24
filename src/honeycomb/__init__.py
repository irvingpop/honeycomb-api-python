"""Honeycomb API client for Python."""

__version__ = "0.1.0"

from .auth import APIKeyAuth, AuthStrategy, ManagementKeyAuth, create_auth
from .client import HoneycombClient
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
    Dataset,
    DatasetCreate,
    QueryCalculation,
    QueryFilter,
    SLOCreate,
    Trigger,
    TriggerAlertType,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)
from .resources import Board, BoardCreate

__all__ = [
    "__version__",
    # Client
    "HoneycombClient",
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
]

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
    ApiKey,
    ApiKeyCreate,
    ApiKeyType,
    BatchEvent,
    BatchEventResult,
    Board,
    BoardCreate,
    BurnAlert,
    BurnAlertCreate,
    BurnAlertType,
    CalcOp,
    Calculation,
    Column,
    ColumnCreate,
    ColumnType,
    Dataset,
    DatasetCreate,
    Environment,
    EnvironmentColor,
    EnvironmentCreate,
    EnvironmentUpdate,
    Filter,
    FilterCombination,
    FilterOp,
    Having,
    Marker,
    MarkerCreate,
    MarkerSetting,
    MarkerSettingCreate,
    Order,
    OrderDirection,
    Query,
    QueryBuilder,
    QueryResult,
    QuerySpec,
    Recipient,
    RecipientCreate,
    RecipientType,
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
    # Models - Query Builder (enums and typed models)
    "CalcOp",
    "FilterOp",
    "OrderDirection",
    "FilterCombination",
    "Calculation",
    "Filter",
    "Order",
    "Having",
    "QueryBuilder",
    # Models - Triggers
    "Trigger",
    "TriggerCreate",
    "TriggerThreshold",
    "TriggerThresholdOp",
    "TriggerAlertType",
    "TriggerQuery",
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
    # Models - Columns
    "Column",
    "ColumnCreate",
    "ColumnType",
    # Models - Markers
    "Marker",
    "MarkerCreate",
    "MarkerSetting",
    "MarkerSettingCreate",
    # Models - Recipients
    "Recipient",
    "RecipientCreate",
    "RecipientType",
    # Models - Burn Alerts
    "BurnAlert",
    "BurnAlertCreate",
    "BurnAlertType",
    # Models - Events
    "BatchEvent",
    "BatchEventResult",
    # Models - API Keys (v2)
    "ApiKey",
    "ApiKeyCreate",
    "ApiKeyType",
    # Models - Environments (v2)
    "Environment",
    "EnvironmentCreate",
    "EnvironmentUpdate",
    "EnvironmentColor",
]

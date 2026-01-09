"""Honeycomb API client for Python."""

import sys


# Handle Ctrl-C gracefully without traceback (including during slow imports)
# This MUST be installed before any other imports to catch KeyboardInterrupt during module loading
def _keyboard_interrupt_handler(exc_type, exc_value, exc_traceback):  # type: ignore[no-untyped-def]
    if issubclass(exc_type, KeyboardInterrupt):
        sys.exit(130)  # Standard exit code for SIGINT
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = _keyboard_interrupt_handler

# Now safe to import other modules
# ruff: noqa: E402 - imports must come after excepthook installation
from importlib.metadata import version

__version__ = version("honeycomb-api")

# Note: tools module is imported lazily via __getattr__ below to speed up CLI startup
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
    ApiKeyUpdate,
    AuthInfo,
    AuthInfoV2,
    BatchEvent,
    BatchEventResult,
    Board,
    BoardBuilder,
    BoardBundle,
    BoardCreate,
    BurnAlert,
    BurnAlertBuilder,
    BurnAlertCreate,
    BurnAlertDefinition,
    BurnAlertRecipient,
    BurnAlertType,
    CalcOp,
    Calculation,
    Column,
    ColumnCreate,
    ColumnType,
    Dataset,
    DatasetCreate,
    DatasetUpdate,
    DerivedColumn,
    DerivedColumnBuilder,
    DerivedColumnCreate,
    Environment,
    EnvironmentColor,
    EnvironmentCreate,
    EnvironmentUpdate,
    Filter,
    FilterCombination,
    FilterOp,
    Having,
    Marker,
    MarkerBuilder,
    MarkerCreate,
    MarkerSetting,
    MarkerSettingCreate,
    Order,
    OrderDirection,
    Query,
    QueryAnnotation,
    QueryAnnotationCreate,
    QueryAnnotationSource,
    QueryBuilder,
    QueryResult,
    QuerySpec,
    Recipient,
    RecipientBuilder,
    RecipientCreate,
    RecipientMixin,
    RecipientType,
    ServiceMapDependency,
    ServiceMapDependencyRequest,
    ServiceMapDependencyRequestCreate,
    ServiceMapDependencyRequestStatus,
    ServiceMapDependencyResult,
    ServiceMapNode,
    ServiceMapNodeType,
    SLIDefinition,
    SLOBuilder,
    SLOBundle,
    SLOCreate,
    TagsMixin,
    Trigger,
    TriggerAlertType,
    TriggerBuilder,
    TriggerBundle,
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
    # Tools (Claude API) - lazily imported
    "tools",
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
    "TriggerBuilder",
    "TriggerBundle",
    # Models - SLOs
    "SLO",
    "SLOCreate",
    "SLI",
    "SLOBuilder",
    "SLOBundle",
    "SLIDefinition",
    # Models - Datasets
    "Dataset",
    "DatasetCreate",
    "DatasetUpdate",
    # Models - Boards
    "Board",
    "BoardBuilder",
    "BoardBundle",
    "BoardCreate",
    "ExistingQueryPanel",
    "ExistingSLOPanel",
    "QueryBuilderPanel",
    "SLOBuilderPanel",
    "TextPanel",
    # Models - Queries
    "Query",
    "QuerySpec",
    "QueryResult",
    # Models - Query Annotations
    "QueryAnnotation",
    "QueryAnnotationCreate",
    "QueryAnnotationSource",
    # Models - Columns
    "Column",
    "ColumnCreate",
    "ColumnType",
    # Models - Derived Columns (Calculated Fields)
    "DerivedColumn",
    "DerivedColumnCreate",
    "DerivedColumnBuilder",
    # Models - Markers
    "Marker",
    "MarkerBuilder",
    "MarkerCreate",
    "MarkerSetting",
    "MarkerSettingCreate",
    # Models - Recipients
    "Recipient",
    "RecipientCreate",
    "RecipientType",
    "RecipientBuilder",
    "RecipientMixin",
    # Models - Tags
    "TagsMixin",
    # Models - Burn Alerts
    "BurnAlert",
    "BurnAlertBuilder",
    "BurnAlertCreate",
    "BurnAlertDefinition",
    "BurnAlertRecipient",
    "BurnAlertType",
    # Models - Events
    "BatchEvent",
    "BatchEventResult",
    # Models - API Keys (v2)
    "ApiKey",
    "ApiKeyCreate",
    "ApiKeyType",
    "ApiKeyUpdate",
    # Models - Auth
    "AuthInfo",
    "AuthInfoV2",
    # Models - Environments (v2)
    "Environment",
    "EnvironmentCreate",
    "EnvironmentUpdate",
    "EnvironmentColor",
    # Models - Service Map Dependencies
    "ServiceMapDependency",
    "ServiceMapDependencyRequest",
    "ServiceMapDependencyRequestCreate",
    "ServiceMapDependencyRequestStatus",
    "ServiceMapDependencyResult",
    "ServiceMapNode",
    "ServiceMapNodeType",
]


# Lazy import mechanism for tools module to speed up CLI startup
def __getattr__(name: str):  # type: ignore[no-untyped-def]
    """Lazily import the tools module when accessed."""
    if name == "tools":
        import importlib

        # Use importlib to avoid triggering __getattr__ recursively
        tools_module = importlib.import_module("honeycomb.tools")
        # Cache in globals to avoid re-importing
        globals()[name] = tools_module
        return tools_module
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

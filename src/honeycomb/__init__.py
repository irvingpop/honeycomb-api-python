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
    SLO,
    AlertType,
    ApiKey,
    ApiKeyCreate,
    ApiKeyCreateRequest,
    ApiKeyListResponse,
    ApiKeyObject,
    ApiKeyObjectType,
    ApiKeyResponse,
    ApiKeyType,
    ApiKeyUpdate,
    ApiKeyUpdateRequest,
    Auth,
    AuthV2Response,
    BatchEvent,
    BatchEventResult,
    Board,
    BoardBuilder,
    BoardBundle,
    BoardCreate,
    BudgetRateBurnAlertDetailResponse,
    BurnAlert,
    BurnAlertBuilder,
    BurnAlertCreate,
    BurnAlertDefinition,
    BurnAlertDetailResponse,
    BurnAlertListResponse,
    BurnAlertRecipient,
    BurnAlertType,
    CalcOp,
    Calculation,
    Column,
    ColumnCreate,
    ColumnType,
    ConfigurationKey,
    CreateBudgetRateBurnAlertRequest,
    CreateBudgetRateBurnAlertRequestSlo,
    CreateBurnAlertRequest,
    CreateEnvironmentRequest,
    CreateExhaustionTimeBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequestSlo,
    Dataset,
    DatasetCreate,
    DatasetUpdate,
    DerivedColumn,
    DerivedColumnBuilder,
    DerivedColumnCreate,
    EmailRecipient,
    EmailRecipientDetails,
    Environment,
    EnvironmentColor,
    EnvironmentCreate,
    EnvironmentListResponse,
    EnvironmentResponse,
    EnvironmentUpdate,
    ExhaustionTimeDetailResponse,
    Filter,
    FilterCombination,
    FilterOp,
    Having,
    IngestKey,
    Marker,
    MarkerBuilder,
    MarkerCreate,
    MarkerSetting,
    MarkerSettingCreate,
    MSTeamsRecipient,
    MSTeamsRecipientDetails,
    MSTeamsWorkflowRecipient,
    MSTeamsWorkflowRecipientDetails,
    NotificationRecipient,
    Order,
    OrderDirection,
    PagerDutyRecipient,
    PagerDutyRecipientDetails,
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
    SlackRecipient,
    SlackRecipientDetails,
    SLIDefinition,
    SLOBuilder,
    SLOBundle,
    SLOCreate,
    SLOCreateSli,
    TagsMixin,
    Trigger,
    TriggerAlertType,
    TriggerBuilder,
    TriggerBundle,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
    TriggerWithInlineQuery,
    TriggerWithQueryReference,
    UpdateBurnAlertRequest,
    UpdateEnvironmentRequest,
    WebhookHeader,
    WebhookPayloads,
    WebhookPayloadTemplate,
    WebhookRecipient,
    WebhookRecipientDetails,
    WebhookTemplateVariable,
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
    "TriggerCreate",  # Union type for compatibility
    "TriggerWithInlineQuery",  # Specific type for inline queries
    "TriggerWithQueryReference",  # Specific type for query references
    "TriggerThreshold",
    "TriggerThresholdOp",
    "TriggerAlertType",
    "TriggerBuilder",
    "TriggerBundle",
    # Models - SLOs
    "SLO",
    "SLOCreate",
    "SLOCreateSli",
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
    "EmailRecipient",
    "EmailRecipientDetails",
    "SlackRecipient",
    "SlackRecipientDetails",
    "PagerDutyRecipient",
    "PagerDutyRecipientDetails",
    "WebhookRecipient",
    "WebhookRecipientDetails",
    "WebhookHeader",
    "WebhookPayloads",
    "WebhookPayloadTemplate",
    "WebhookTemplateVariable",
    "MSTeamsRecipient",
    "MSTeamsRecipientDetails",
    "MSTeamsWorkflowRecipient",
    "MSTeamsWorkflowRecipientDetails",
    # Models - Tags
    "TagsMixin",
    # Models - Burn Alerts
    "AlertType",
    "BudgetRateBurnAlertDetailResponse",
    "BurnAlert",
    "BurnAlertBuilder",
    "BurnAlertCreate",
    "BurnAlertDefinition",
    "BurnAlertDetailResponse",
    "BurnAlertListResponse",
    "BurnAlertRecipient",
    "BurnAlertType",
    "CreateBudgetRateBurnAlertRequest",
    "CreateBudgetRateBurnAlertRequestSlo",
    "CreateBurnAlertRequest",
    "CreateExhaustionTimeBurnAlertRequest",
    "CreateExhaustionTimeBurnAlertRequestSlo",
    "ExhaustionTimeDetailResponse",
    "NotificationRecipient",
    "UpdateBudgetRateBurnAlert",
    "UpdateBurnAlertRequest",
    "UpdateExhaustionTimeBurnAlertRequest",
    # Models - Events
    "BatchEvent",
    "BatchEventResult",
    # Models - API Keys (v2)
    "ApiKey",
    "ApiKeyCreate",
    "ApiKeyCreateRequest",
    "ApiKeyListResponse",
    "ApiKeyObject",
    "ApiKeyObjectType",
    "ApiKeyResponse",
    "ApiKeyType",
    "ApiKeyUpdate",
    "ApiKeyUpdateRequest",
    "ConfigurationKey",
    "IngestKey",
    # Models - Auth
    "Auth",
    "AuthV2Response",
    # Models - Environments (v2)
    "CreateEnvironmentRequest",
    "Environment",
    "EnvironmentColor",
    "EnvironmentCreate",
    "EnvironmentListResponse",
    "EnvironmentResponse",
    "EnvironmentUpdate",
    "UpdateEnvironmentRequest",
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

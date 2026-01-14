"""Pydantic models for Honeycomb API resources."""

# Import specific trigger types for advanced usage
from honeycomb._generated_models import TriggerWithInlineQuery, TriggerWithQueryReference

from .api_keys import (
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
    ConfigurationKey,
    IngestKey,
)
from .auth import Auth, AuthV2Response
from .board_builder import (
    BoardBuilder,
    BoardBundle,
    ExistingQueryPanel,
    ExistingSLOPanel,
    QueryBuilderPanel,
    SLOBuilderPanel,
    TextPanel,
)
from .boards import (
    Board,
    BoardCreate,
    BoardView,
    BoardViewCreate,
    BoardViewFilter,
)
from .burn_alerts import (
    AlertType,
    BudgetRateBurnAlertDetailResponse,
    BurnAlert,
    BurnAlertCreate,
    BurnAlertDetailResponse,
    BurnAlertListResponse,
    BurnAlertRecipient,
    BurnAlertType,
    CreateBudgetRateBurnAlertRequest,
    CreateBudgetRateBurnAlertRequestSlo,
    CreateBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequestSlo,
    ExhaustionTimeDetailResponse,
    NotificationRecipient,
    UpdateBudgetRateBurnAlert,
    UpdateBurnAlertRequest,
    UpdateExhaustionTimeBurnAlertRequest,
)
from .columns import Column, ColumnCreate, ColumnType
from .datasets import Dataset, DatasetCreate, DatasetUpdate
from .derived_columns import DerivedColumn, DerivedColumnBuilder, DerivedColumnCreate
from .environments import (
    CreateEnvironmentRequest,
    Environment,
    EnvironmentColor,
    EnvironmentCreate,
    EnvironmentListResponse,
    EnvironmentResponse,
    EnvironmentUpdate,
    UpdateEnvironmentRequest,
)
from .events import BatchEvent, BatchEventResult
from .marker_builder import MarkerBuilder
from .markers import Marker, MarkerCreate, MarkerSetting, MarkerSettingCreate
from .queries import Query, QueryResult, QueryResultData, QuerySpec
from .query_annotations import QueryAnnotation, QueryAnnotationCreate, QueryAnnotationSource
from .query_builder import (
    CalcOp,
    Calculation,
    Filter,
    FilterCombination,
    FilterOp,
    Having,
    Order,
    OrderDirection,
    QueryBuilder,
)
from .recipient_builder import RecipientBuilder, RecipientMixin
from .recipients import (
    EmailRecipient,
    EmailRecipientDetails,
    MSTeamsRecipient,
    MSTeamsRecipientDetails,
    MSTeamsWorkflowRecipient,
    MSTeamsWorkflowRecipientDetails,
    PagerDutyRecipient,
    PagerDutyRecipientDetails,
    Recipient,
    RecipientCreate,
    RecipientType,
    SlackRecipient,
    SlackRecipientDetails,
    WebhookHeader,
    WebhookPayloads,
    WebhookPayloadTemplate,
    WebhookRecipient,
    WebhookRecipientDetails,
    WebhookTemplateVariable,
    get_recipient_class,
)
from .service_map_dependencies import (
    ServiceMapDependency,
    ServiceMapDependencyRequest,
    ServiceMapDependencyRequestCreate,
    ServiceMapDependencyRequestStatus,
    ServiceMapDependencyResult,
    ServiceMapNode,
    ServiceMapNodeType,
)
from .slo_builder import BurnAlertBuilder, BurnAlertDefinition, SLIDefinition, SLOBuilder, SLOBundle
from .slos import SLO, SLOCreate, SLOCreateSli
from .tags_mixin import TagsMixin
from .tool_inputs import TriggerToolInput
from .trigger_builder import TriggerBuilder, TriggerBundle
from .triggers import (
    Trigger,
    TriggerAlertType,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
)

__all__ = [
    # Query Builder (enums and typed models)
    "CalcOp",
    "FilterOp",
    "OrderDirection",
    "FilterCombination",
    "Calculation",
    "Filter",
    "Order",
    "Having",
    "QueryBuilder",
    # Triggers
    "Trigger",
    "TriggerCreate",  # Union type: TriggerWithInlineQuery | TriggerWithQueryReference
    "TriggerWithInlineQuery",  # Specific type for inline queries (from builder)
    "TriggerWithQueryReference",  # Specific type for query references
    "TriggerThreshold",
    "TriggerThresholdOp",
    "TriggerAlertType",
    "TriggerToolInput",  # Tool input model with proper validation
    "TriggerBuilder",
    "TriggerBundle",
    # SLOs
    "SLO",
    "SLOCreate",
    "SLOCreateSli",
    "SLOBuilder",
    "SLOBundle",
    "SLIDefinition",
    "BurnAlertBuilder",
    "BurnAlertDefinition",
    # Datasets
    "Dataset",
    "DatasetCreate",
    "DatasetUpdate",
    # Boards
    "Board",
    "BoardBuilder",
    "BoardBundle",
    "BoardCreate",
    "BoardView",
    "BoardViewCreate",
    "BoardViewFilter",
    "ExistingQueryPanel",
    "ExistingSLOPanel",
    "QueryBuilderPanel",
    "SLOBuilderPanel",
    "TextPanel",
    # Queries
    "Query",
    "QuerySpec",
    "QueryResult",
    "QueryResultData",
    # Query Annotations
    "QueryAnnotation",
    "QueryAnnotationCreate",
    "QueryAnnotationSource",
    # Columns
    "Column",
    "ColumnCreate",
    "ColumnType",
    # Derived Columns (Calculated Fields)
    "DerivedColumn",
    "DerivedColumnCreate",
    "DerivedColumnBuilder",
    # Markers
    "Marker",
    "MarkerBuilder",
    "MarkerCreate",
    "MarkerSetting",
    "MarkerSettingCreate",
    # Recipients
    "Recipient",
    "RecipientCreate",
    "RecipientType",
    "RecipientBuilder",
    "RecipientMixin",
    "get_recipient_class",
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
    # Tags
    "TagsMixin",
    # Burn Alerts
    "AlertType",
    "BudgetRateBurnAlertDetailResponse",
    "BurnAlert",
    "BurnAlertCreate",
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
    # Events
    "BatchEvent",
    "BatchEventResult",
    # API Keys (v2)
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
    # Auth
    "Auth",
    "AuthV2Response",
    # Environments (v2)
    "CreateEnvironmentRequest",
    "Environment",
    "EnvironmentColor",
    "EnvironmentCreate",
    "EnvironmentUpdate",
    "EnvironmentListResponse",
    "EnvironmentResponse",
    "UpdateEnvironmentRequest",
    # Service Map Dependencies
    "ServiceMapDependency",
    "ServiceMapDependencyRequest",
    "ServiceMapDependencyRequestCreate",
    "ServiceMapDependencyRequestStatus",
    "ServiceMapDependencyResult",
    "ServiceMapNode",
    "ServiceMapNodeType",
]

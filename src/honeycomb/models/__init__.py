"""Pydantic models for Honeycomb API resources."""

from .api_keys import ApiKey, ApiKeyCreate, ApiKeyType
from .auth import AuthInfo, AuthInfoV2
from .board_builder import (
    BoardBuilder,
    BoardBundle,
    ExistingQueryPanel,
    ExistingSLOPanel,
    QueryBuilderPanel,
    SLOBuilderPanel,
    TextPanel,
)
from .boards import Board, BoardCreate
from .burn_alerts import BurnAlert, BurnAlertCreate, BurnAlertRecipient, BurnAlertType
from .columns import Column, ColumnCreate, ColumnType
from .datasets import Dataset, DatasetCreate
from .derived_columns import DerivedColumn, DerivedColumnBuilder, DerivedColumnCreate
from .environments import Environment, EnvironmentColor, EnvironmentCreate, EnvironmentUpdate
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
from .recipients import Recipient, RecipientCreate, RecipientType
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
from .slos import SLI, SLO, SLOCreate
from .tags_mixin import TagsMixin
from .trigger_builder import TriggerBuilder, TriggerBundle
from .triggers import (
    Trigger,
    TriggerAlertType,
    TriggerCreate,
    TriggerQuery,
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
    "TriggerCreate",
    "TriggerThreshold",
    "TriggerThresholdOp",
    "TriggerAlertType",
    "TriggerQuery",
    "TriggerBuilder",
    "TriggerBundle",
    # SLOs
    "SLO",
    "SLOCreate",
    "SLI",
    "SLOBuilder",
    "SLOBundle",
    "SLIDefinition",
    "BurnAlertBuilder",
    "BurnAlertDefinition",
    # Datasets
    "Dataset",
    "DatasetCreate",
    # Boards
    "Board",
    "BoardBuilder",
    "BoardBundle",
    "BoardCreate",
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
    # Tags
    "TagsMixin",
    # Burn Alerts
    "BurnAlert",
    "BurnAlertCreate",
    "BurnAlertRecipient",
    "BurnAlertType",
    # Events
    "BatchEvent",
    "BatchEventResult",
    # API Keys (v2)
    "ApiKey",
    "ApiKeyCreate",
    "ApiKeyType",
    # Auth
    "AuthInfo",
    "AuthInfoV2",
    # Environments (v2)
    "Environment",
    "EnvironmentCreate",
    "EnvironmentUpdate",
    "EnvironmentColor",
    # Service Map Dependencies
    "ServiceMapDependency",
    "ServiceMapDependencyRequest",
    "ServiceMapDependencyRequestCreate",
    "ServiceMapDependencyRequestStatus",
    "ServiceMapDependencyResult",
    "ServiceMapNode",
    "ServiceMapNodeType",
]

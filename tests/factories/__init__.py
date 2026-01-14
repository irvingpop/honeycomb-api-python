"""Polyfactory-based test data factories for Honeycomb models.

This package provides factories for generating realistic test data that matches
the Pydantic models used by the Honeycomb API client. Use these factories with
respx mocks to create schema-valid mock responses.

Basic usage:
    from tests.factories import SLOFactory, mock_response, mock_list_response

    # Generate a single mock response
    respx_mock.get("https://api.honeycomb.io/1/slos/dataset/slo-1").mock(
        return_value=Response(200, json=mock_response(SLOFactory, id="slo-1"))
    )

    # Generate a list response
    respx_mock.get("https://api.honeycomb.io/1/slos/dataset").mock(
        return_value=Response(200, json=mock_list_response(SLOFactory, count=5))
    )
"""

# Base factory
from .base import HoneycombFactory

# Board factories
from .boards import (
    BoardCreateFactory,
    BoardFactory,
    BoardLinksFactory,
    BoardPanelPositionFactory,
    BoardQueryVisualizationSettingsFactory,
    BoardViewCreateFactory,
    BoardViewFactory,
    BoardViewFilterFactory,
    QueryPanelQueryPanelFactory,
)

# Column factories
from .columns import (
    ColumnCreateFactory,
    ColumnFactory,
    DerivedColumnCreateFactory,
    DerivedColumnFactory,
)

# Core factories (Environment, Dataset, ApiKey)
from .core import (
    ApiKeyCreateResponseDataFactory,
    ApiKeyObjectFactory,
    ConfigurationKeyCreateAttributesFactory,
    ConfigurationKeyFactory,
    ConfigurationKeyPermissionsFactory,
    CreateEnvironmentRequestDataAttributesFactory,
    CreateEnvironmentRequestDataFactory,
    DatasetCreateFactory,
    DatasetFactory,
    DatasetSettingsFactory,
    DatasetUpdateFactory,
    EnvironmentAttributesFactory,
    EnvironmentAttributesSettingsFactory,
    EnvironmentCreateFactory,
    EnvironmentFactory,
    EnvironmentLinksFactory,
    IngestKeyCreateAttributesFactory,
    IngestKeyFactory,
    IngestKeyPermissionsFactory,
)

# Helper utilities
from .helpers import mock_list_response, mock_paginated_response, mock_response

# Marker factories
from .markers import (
    MarkerCreateFactory,
    MarkerFactory,
    MarkerSettingCreateFactory,
    MarkerSettingFactory,
)

# Query factories
from .queries import (
    QueryAnnotationCreateFactory,
    QueryAnnotationFactory,
    QueryCalculationFactory,
    QueryFactory,
    QueryResultDetailsDataFactory,
    QueryResultFactory,
    QueryResultsDataFactory,
    QuerySpecFactory,
)

# Recipient factories
from .recipients import (
    EmailRecipientDetailsFactory,
    EmailRecipientFactory,
    RecipientFactory,
    WebhookHeaderFactory,
    WebhookRecipientDetailsFactory,
    WebhookRecipientFactory,
)

# SLO and Burn Alert factories
from .slos import (
    BudgetRateBurnAlertFactory,
    BudgetRateBurnAlertSloFactory,
    BurnAlertSloFactory,
    CreateBudgetRateBurnAlertFactory,
    CreateExhaustionTimeBurnAlertFactory,
    CreateExhaustionTimeBurnAlertRequestSloFactory,
    ExhaustionTimeBurnAlertFactory,
    ExhaustionTimeBurnAlertSloFactory,
    SLOCreateFactory,
    SLOCreateSliFactory,
    SLOFactory,
    SLOSliFactory,
    TagFactory,
)

# Trigger factories
from .triggers import (
    NotificationRecipientFactory,
    TriggerCreateFactory,
    TriggerFactory,
    TriggerThresholdFactory,
    TriggerWithInlineQueryFactory,
    TriggerWithQueryReferenceFactory,
)

__all__ = [
    # Base
    "HoneycombFactory",
    # Helpers
    "mock_response",
    "mock_list_response",
    "mock_paginated_response",
    # Boards
    "BoardFactory",
    "BoardCreateFactory",
    "BoardLinksFactory",
    "BoardPanelPositionFactory",
    "BoardQueryVisualizationSettingsFactory",
    "BoardViewFactory",
    "BoardViewCreateFactory",
    "BoardViewFilterFactory",
    "QueryPanelQueryPanelFactory",
    # Columns
    "ColumnFactory",
    "ColumnCreateFactory",
    "DerivedColumnFactory",
    "DerivedColumnCreateFactory",
    # Core
    "DatasetFactory",
    "DatasetCreateFactory",
    "DatasetUpdateFactory",
    "DatasetSettingsFactory",
    "EnvironmentFactory",
    "EnvironmentCreateFactory",
    "EnvironmentAttributesFactory",
    "EnvironmentAttributesSettingsFactory",
    "EnvironmentLinksFactory",
    "CreateEnvironmentRequestDataFactory",
    "CreateEnvironmentRequestDataAttributesFactory",
    "ApiKeyObjectFactory",
    "ApiKeyCreateResponseDataFactory",
    "IngestKeyFactory",
    "IngestKeyCreateAttributesFactory",
    "ConfigurationKeyFactory",
    "ConfigurationKeyCreateAttributesFactory",
    "IngestKeyPermissionsFactory",
    "ConfigurationKeyPermissionsFactory",
    # Markers
    "MarkerFactory",
    "MarkerCreateFactory",
    "MarkerSettingFactory",
    "MarkerSettingCreateFactory",
    # Queries
    "QueryFactory",
    "QuerySpecFactory",
    "QueryCalculationFactory",
    "QueryResultFactory",
    "QueryResultDetailsDataFactory",
    "QueryResultsDataFactory",
    "QueryAnnotationFactory",
    "QueryAnnotationCreateFactory",
    # Recipients
    "RecipientFactory",
    "EmailRecipientFactory",
    "EmailRecipientDetailsFactory",
    "WebhookRecipientFactory",
    "WebhookRecipientDetailsFactory",
    "WebhookHeaderFactory",
    # SLOs and Burn Alerts
    "SLOFactory",
    "SLOCreateFactory",
    "SLOSliFactory",
    "SLOCreateSliFactory",
    "TagFactory",
    "ExhaustionTimeBurnAlertFactory",
    "ExhaustionTimeBurnAlertSloFactory",
    "BudgetRateBurnAlertFactory",
    "BudgetRateBurnAlertSloFactory",
    "BurnAlertSloFactory",
    "CreateExhaustionTimeBurnAlertFactory",
    "CreateExhaustionTimeBurnAlertRequestSloFactory",
    "CreateBudgetRateBurnAlertFactory",
    # Triggers
    "TriggerFactory",
    "TriggerCreateFactory",
    "TriggerWithInlineQueryFactory",
    "TriggerWithQueryReferenceFactory",
    "TriggerThresholdFactory",
    "NotificationRecipientFactory",
]

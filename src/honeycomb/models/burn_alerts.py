"""Pydantic models for Honeycomb Burn Alerts.

Re-exports generated models with discriminated unions for alert types.
"""

from enum import Enum

from honeycomb._generated_models import AlertType as _AlertType
from honeycomb._generated_models import (
    BudgetRateBurnAlertDetailResponse,
    BurnAlertDetailResponse,
    BurnAlertListResponse,
    CreateBudgetRateBurnAlertRequest,
    CreateBudgetRateBurnAlertRequestSlo,
    CreateBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequestSlo,
    ExhaustionTime1,
    NotificationRecipient,
    UpdateBudgetRateBurnAlert,
    UpdateBurnAlertRequest,
    UpdateExhaustionTimeBurnAlertRequest,
)


# Backward-compatible enum with uppercase names
class BurnAlertType(str, Enum):
    """Burn alert types (backward-compatible with uppercase names)."""

    EXHAUSTION_TIME = "exhaustion_time"
    BUDGET_RATE = "budget_rate"
    # Lowercase aliases (match generated AlertType)
    exhaustion_time = "exhaustion_time"
    budget_rate = "budget_rate"


# Re-export generated types
AlertType = _AlertType
BurnAlertRecipient = NotificationRecipient

__all__ = [
    "AlertType",
    "BudgetRateBurnAlertDetailResponse",
    "BurnAlertDetailResponse",
    "BurnAlertListResponse",
    "BurnAlertRecipient",
    "BurnAlertType",
    "CreateBudgetRateBurnAlertRequest",
    "CreateBudgetRateBurnAlertRequestSlo",
    "CreateBurnAlertRequest",
    "CreateExhaustionTimeBurnAlertRequest",
    "CreateExhaustionTimeBurnAlertRequestSlo",
    "ExhaustionTime1",
    "NotificationRecipient",
    "UpdateBudgetRateBurnAlert",
    "UpdateBurnAlertRequest",
    "UpdateExhaustionTimeBurnAlertRequest",
]

"""Pydantic models for Honeycomb Burn Alerts.

Re-exports generated models with discriminated unions for alert types.
"""

from enum import Enum
from typing import Any

from pydantic.types import AwareDatetime

from honeycomb._generated_models import AlertType as _AlertType
from honeycomb._generated_models import (
    BudgetRateBurnAlertDetailResponse,
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
from honeycomb._generated_models import (
    BurnAlertDetailResponse as _BurnAlertDetailResponseGenerated,
)
from honeycomb._generated_models import (
    BurnAlertListResponse as _BurnAlertListResponseGenerated,
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


class BurnAlertListResponse(_BurnAlertListResponseGenerated):
    """Burn alert list response with property accessors.

    Extends generated BurnAlertListResponse RootModel to hide .root accessor requirement.
    """

    @property
    def id(self) -> str | None:
        """Get burn alert ID."""
        return self.root.id

    @property
    def alert_type(self) -> str:
        """Get alert type (discriminator)."""
        return self.root.alert_type

    @property
    def description(self) -> str | None:
        """Get burn alert description."""
        return self.root.description

    @property
    def triggered(self) -> bool | None:
        """Get triggered status."""
        return self.root.triggered

    @property
    def created_at(self) -> AwareDatetime | None:
        """Get creation timestamp."""
        return self.root.created_at

    @property
    def updated_at(self) -> AwareDatetime | None:
        """Get last update timestamp."""
        return self.root.updated_at

    @property
    def slo(self) -> Any:
        """Get SLO details."""
        return self.root.slo

    @property
    def exhaustion_minutes(self) -> int | None:
        """Get exhaustion minutes (exhaustion_time alerts only)."""
        return getattr(self.root, "exhaustion_minutes", None)

    @property
    def budget_rate_window_minutes(self) -> int | None:
        """Get budget rate window minutes (budget_rate alerts only)."""
        return getattr(self.root, "budget_rate_window_minutes", None)

    @property
    def budget_rate_decrease_threshold_per_million(self) -> int | None:
        """Get budget rate decrease threshold (budget_rate alerts only)."""
        return getattr(self.root, "budget_rate_decrease_threshold_per_million", None)


class BurnAlertDetailResponse(_BurnAlertDetailResponseGenerated):
    """Burn alert detail response with property accessors.

    Extends generated BurnAlertDetailResponse RootModel to hide .root accessor requirement.
    """

    @property
    def id(self) -> str | None:
        """Get burn alert ID."""
        return self.root.id

    @property
    def alert_type(self) -> str:
        """Get alert type (discriminator)."""
        return self.root.alert_type

    @property
    def description(self) -> str | None:
        """Get burn alert description."""
        return self.root.description

    @property
    def triggered(self) -> bool | None:
        """Get triggered status."""
        return self.root.triggered

    @property
    def created_at(self) -> AwareDatetime | None:
        """Get creation timestamp."""
        return self.root.created_at

    @property
    def updated_at(self) -> AwareDatetime | None:
        """Get last update timestamp."""
        return self.root.updated_at

    @property
    def slo(self) -> Any:
        """Get SLO details."""
        return self.root.slo

    @property
    def exhaustion_minutes(self) -> int | None:
        """Get exhaustion minutes (exhaustion_time alerts only)."""
        return getattr(self.root, "exhaustion_minutes", None)

    @property
    def budget_rate_window_minutes(self) -> int | None:
        """Get budget rate window minutes (budget_rate alerts only)."""
        return getattr(self.root, "budget_rate_window_minutes", None)

    @property
    def budget_rate_decrease_threshold_per_million(self) -> int | None:
        """Get budget rate decrease threshold (budget_rate alerts only)."""
        return getattr(self.root, "budget_rate_decrease_threshold_per_million", None)

    @property
    def recipients(self) -> list[NotificationRecipient] | None:
        """Get recipients list."""
        return self.root.recipients


# Type aliases for convenience - both list and detail responses are discriminated unions
BurnAlert = BurnAlertDetailResponse  # For single alert operations
BurnAlertCreate = CreateBurnAlertRequest  # For create operations

__all__ = [
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
]

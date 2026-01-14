"""Factories for SLO, BurnAlert, and related models."""

from honeycomb._generated_models import (
    BurnAlertListSloSlo,
    CreateBudgetRateBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequestSlo,
    SLOCreateSli,
    SLOSli,
    Tag,
)
from honeycomb.models import (
    SLO,
    BudgetRateBurnAlertDetailResponse,
    ExhaustionTimeDetailResponse,
    SLOCreate,
)

from .base import HoneycombFactory


class TagFactory(HoneycombFactory):
    """Factory for Tag model (used in SLOs and Triggers)."""

    __model__ = Tag

    # Override to generate valid tag values (lowercase alphanumeric)
    key = lambda: "team"
    value = lambda: "platform"


class SLOSliFactory(HoneycombFactory):
    """Factory for SLOSli (response model)."""

    __model__ = SLOSli

    alias = lambda: f"sli_{HoneycombFactory._honeycomb_id()}"


class SLOCreateSliFactory(HoneycombFactory):
    """Factory for SLOCreateSli (create request model)."""

    __model__ = SLOCreateSli

    alias = lambda: f"sli_{HoneycombFactory._honeycomb_id()}"


class SLOFactory(HoneycombFactory):
    """Factory for SLO response model.

    Generates complete SLO objects with valid random data.
    Override specific fields as needed for your test.

    Example:
        slo = SLOFactory.build(id="slo-123", name="My SLO")
        slo_list = SLOFactory.batch(5)
    """

    __model__ = SLO

    # Generate deterministic IDs for assertions
    id = lambda: HoneycombFactory._honeycomb_id()

    # Valid name within constraints (1-120 chars)
    name = lambda: f"Test SLO {HoneycombFactory._honeycomb_id()}"

    # Valid target (0-999999)
    target_per_million = lambda: HoneycombFactory.__random__.randint(900000, 999999)

    # Valid time period (>= 1 day)
    time_period_days = lambda: HoneycombFactory.__random__.choice([7, 14, 30, 90])

    # Single dataset by default
    dataset_slugs = lambda: [f"dataset-{HoneycombFactory._honeycomb_id()}"]


class SLOCreateFactory(HoneycombFactory):
    """Factory for SLOCreate request model.

    Generates valid SLO creation payloads.

    Example:
        payload = SLOCreateFactory.build(name="New SLO")
    """

    __model__ = SLOCreate

    name = lambda: f"Test SLO {HoneycombFactory._honeycomb_id()}"
    target_per_million = lambda: HoneycombFactory.__random__.randint(900000, 999999)
    time_period_days = lambda: HoneycombFactory.__random__.choice([7, 14, 30, 90])


# =============================================================================
# Burn Alert Factories
# =============================================================================


class BurnAlertSloFactory(HoneycombFactory):
    """Factory for BurnAlertListSloSlo (shared SLO reference in burn alert list responses).

    This factory is used for both exhaustion_time and budget_rate burn alert responses.
    """

    __model__ = BurnAlertListSloSlo

    id = lambda: HoneycombFactory._honeycomb_id()


# Aliases for backwards compatibility
ExhaustionTimeBurnAlertSloFactory = BurnAlertSloFactory
BudgetRateBurnAlertSloFactory = BurnAlertSloFactory


class ExhaustionTimeBurnAlertFactory(HoneycombFactory):
    """Factory for ExhaustionTimeDetailResponse (exhaustion_time burn alert list/detail response).

    Example:
        alert = ExhaustionTimeBurnAlertFactory.build(id="alert-123")
    """

    __model__ = ExhaustionTimeDetailResponse

    id = lambda: HoneycombFactory._honeycomb_id()
    alert_type = "exhaustion_time"
    exhaustion_minutes = lambda: HoneycombFactory.__random__.choice([60, 120, 240, 480])
    description = lambda: "Test exhaustion time burn alert"
    triggered = False
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


class BudgetRateBurnAlertFactory(HoneycombFactory):
    """Factory for BudgetRateBurnAlertDetailResponse (budget_rate burn alert response).

    Example:
        alert = BudgetRateBurnAlertFactory.build(id="alert-123")
    """

    __model__ = BudgetRateBurnAlertDetailResponse

    id = lambda: HoneycombFactory._honeycomb_id()
    alert_type = "budget_rate"
    budget_rate_window_minutes = lambda: HoneycombFactory.__random__.choice([60, 120, 240, 480])
    budget_rate_decrease_threshold_per_million = lambda: HoneycombFactory.__random__.randint(
        10000, 100000
    )
    description = lambda: "Test budget rate burn alert"
    triggered = False
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


class CreateExhaustionTimeBurnAlertRequestSloFactory(HoneycombFactory):
    """Factory for CreateExhaustionTimeBurnAlertRequestSlo."""

    __model__ = CreateExhaustionTimeBurnAlertRequestSlo

    id = lambda: HoneycombFactory._honeycomb_id()


class CreateExhaustionTimeBurnAlertFactory(HoneycombFactory):
    """Factory for CreateExhaustionTimeBurnAlertRequest.

    Example:
        payload = CreateExhaustionTimeBurnAlertFactory.build(exhaustion_minutes=60)
    """

    __model__ = CreateExhaustionTimeBurnAlertRequest

    alert_type = "exhaustion_time"
    exhaustion_minutes = lambda: HoneycombFactory.__random__.choice([60, 120, 240, 480])


class CreateBudgetRateBurnAlertFactory(HoneycombFactory):
    """Factory for CreateBudgetRateBurnAlertRequest.

    Example:
        payload = CreateBudgetRateBurnAlertFactory.build(budget_rate_window_minutes=60)
    """

    __model__ = CreateBudgetRateBurnAlertRequest

    alert_type = "budget_rate"
    budget_rate_window_minutes = lambda: HoneycombFactory.__random__.choice([60, 120, 240, 480])
    budget_rate_decrease_threshold_per_million = lambda: HoneycombFactory.__random__.randint(
        10000, 100000
    )

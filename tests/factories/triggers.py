"""Factories for Trigger models."""

from honeycomb._generated_models import (
    BaseTriggerAlertType,
    BaseTriggerThreshold,
    BaseTriggerThresholdOp,
    NotificationRecipient,
)
from honeycomb.models import Trigger, TriggerWithInlineQuery, TriggerWithQueryReference

from .base import HoneycombFactory


class TriggerThresholdFactory(HoneycombFactory):
    """Factory for BaseTriggerThreshold."""

    __model__ = BaseTriggerThreshold

    op = lambda: HoneycombFactory.__random__.choice(list(BaseTriggerThresholdOp))
    value = lambda: float(HoneycombFactory.__random__.randint(1, 1000))
    exceeded_limit = lambda: HoneycombFactory.__random__.randint(1, 5)


class NotificationRecipientFactory(HoneycombFactory):
    """Factory for NotificationRecipient (inline recipient in triggers/burn alerts)."""

    __model__ = NotificationRecipient

    id = lambda: HoneycombFactory._honeycomb_id()
    type = "email"
    target = lambda: f"alerts-{HoneycombFactory._honeycomb_id()}@example.com"


class TriggerFactory(HoneycombFactory):
    """Factory for Trigger response model.

    Generates complete Trigger objects with valid random data.

    Example:
        trigger = TriggerFactory.build(id="trigger-123")
        trigger_list = TriggerFactory.batch(5)
    """

    __model__ = Trigger

    id = lambda: HoneycombFactory._honeycomb_id()
    name = lambda: f"Test Trigger {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test trigger"
    dataset_slug = lambda: f"test-dataset-{HoneycombFactory._honeycomb_id()}"
    alert_type = BaseTriggerAlertType.on_change
    disabled = False
    triggered = False
    frequency = lambda: HoneycombFactory.__random__.choice([60, 300, 600, 900])
    # Valid query inline
    query = lambda: {
        "calculations": [{"op": "COUNT"}],
        "time_range": HoneycombFactory.__random__.randint(60, 3600),
    }


class TriggerWithInlineQueryFactory(HoneycombFactory):
    """Factory for TriggerWithInlineQuery (create request with inline query).

    Example:
        trigger_create = TriggerWithInlineQueryFactory.build(name="High Latency Alert")
    """

    __model__ = TriggerWithInlineQuery

    name = lambda: f"Test Trigger {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test trigger"
    frequency = lambda: HoneycombFactory.__random__.choice([60, 300, 600, 900])
    alert_type = BaseTriggerAlertType.on_change
    disabled = False
    # Inline query spec
    query = lambda: {
        "calculations": [{"op": "COUNT"}],
        "time_range": HoneycombFactory.__random__.randint(60, 3600),
    }


class TriggerWithQueryReferenceFactory(HoneycombFactory):
    """Factory for TriggerWithQueryReference (create request with query ID).

    Example:
        trigger_create = TriggerWithQueryReferenceFactory.build(query_id="query-123")
    """

    __model__ = TriggerWithQueryReference

    name = lambda: f"Test Trigger {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test trigger"
    frequency = lambda: HoneycombFactory.__random__.choice([60, 300, 600, 900])
    alert_type = BaseTriggerAlertType.on_change
    disabled = False
    query_id = lambda: HoneycombFactory._honeycomb_id()


# Convenience alias for the most common create pattern
TriggerCreateFactory = TriggerWithInlineQueryFactory

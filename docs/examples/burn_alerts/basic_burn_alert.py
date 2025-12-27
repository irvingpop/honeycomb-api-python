"""Basic burn alert creation examples.

These examples demonstrate creating burn alerts for SLOs.
Burn alerts notify you when error budget is being consumed too quickly.
"""

from __future__ import annotations

from honeycomb import (
    BurnAlert,
    BurnAlertCreate,
    BurnAlertRecipient,
    BurnAlertType,
    HoneycombClient,
)


# start_example:exhaustion_time_alert
async def create_exhaustion_time_alert(
    client: HoneycombClient, dataset: str, slo_id: str, recipient_id: str
) -> str:
    """Create a burn alert that triggers when budget will exhaust within time.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO to monitor
        recipient_id: ID of the recipient to notify

    Returns:
        The created burn alert ID
    """
    alert = await client.burn_alerts.create_async(
        dataset,
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id=slo_id,
            description="Alert when budget depletes within 2 hours",
            exhaustion_minutes=120,
            recipients=[BurnAlertRecipient(id=recipient_id)],
        ),
    )
    return alert.id
# end_example:exhaustion_time_alert


# start_example:budget_rate_alert
async def create_budget_rate_alert(
    client: HoneycombClient, dataset: str, slo_id: str, recipient_id: str
) -> str:
    """Create a burn alert that triggers on rapid budget consumption.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO to monitor
        recipient_id: ID of the recipient to notify

    Returns:
        The created burn alert ID
    """
    alert = await client.burn_alerts.create_async(
        dataset,
        BurnAlertCreate(
            alert_type=BurnAlertType.BUDGET_RATE,
            slo_id=slo_id,
            description="Alert on rapid budget consumption",
            budget_rate_window_minutes=60,
            budget_rate_decrease_threshold_per_million=10000,  # 1% drop
            recipients=[BurnAlertRecipient(id=recipient_id)],
        ),
    )
    return alert.id
# end_example:budget_rate_alert


# start_example:critical_alert
async def create_critical_exhaustion_alert(
    client: HoneycombClient, dataset: str, slo_id: str, recipient_id: str
) -> str:
    """Create a critical burn alert for imminent budget exhaustion.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO to monitor
        recipient_id: ID of the recipient to notify

    Returns:
        The created burn alert ID
    """
    alert = await client.burn_alerts.create_async(
        dataset,
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id=slo_id,
            description="CRITICAL: Budget exhausts in 2 hours - page oncall",
            exhaustion_minutes=120,
            recipients=[BurnAlertRecipient(id=recipient_id)],
        ),
    )
    return alert.id
# end_example:critical_alert


# start_example:warning_alert
async def create_warning_exhaustion_alert(
    client: HoneycombClient, dataset: str, slo_id: str, recipient_id: str
) -> str:
    """Create a warning burn alert for approaching budget exhaustion.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO to monitor
        recipient_id: ID of the recipient to notify

    Returns:
        The created burn alert ID
    """
    alert = await client.burn_alerts.create_async(
        dataset,
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id=slo_id,
            description="WARNING: Budget exhausts in 24 hours - investigate",
            exhaustion_minutes=1440,  # 24 hours
            recipients=[BurnAlertRecipient(id=recipient_id)],
        ),
    )
    return alert.id
# end_example:warning_alert


# start_example:list_burn_alerts
async def list_burn_alerts(
    client: HoneycombClient, dataset: str, slo_id: str
) -> list[BurnAlert]:
    """List all burn alerts for an SLO.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO

    Returns:
        List of burn alerts
    """
    alerts = await client.burn_alerts.list_async(dataset, slo_id=slo_id)
    for alert in alerts:
        print(f"{alert.alert_type}: {alert.description}")
    return alerts
# end_example:list_burn_alerts


# start_example:get_burn_alert
async def get_burn_alert(
    client: HoneycombClient, dataset: str, alert_id: str
) -> BurnAlert:
    """Get a specific burn alert.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the alert
        alert_id: ID of the burn alert

    Returns:
        The burn alert object
    """
    alert = await client.burn_alerts.get_async(dataset, alert_id)
    print(f"Type: {alert.alert_type}")
    print(f"Description: {alert.description}")
    print(f"Triggered: {alert.triggered}")
    return alert
# end_example:get_burn_alert


# start_example:update
async def update_burn_alert(
    client: HoneycombClient, dataset: str, alert_id: str, recipient_id: str
) -> BurnAlert:
    """Update a burn alert's parameters.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the alert
        alert_id: ID of the burn alert to update
        recipient_id: ID of the recipient to notify

    Returns:
        The updated burn alert
    """
    # Get existing alert first to preserve values
    existing = await client.burn_alerts.get_async(dataset, alert_id)

    # Update with new values
    updated = await client.burn_alerts.update_async(
        dataset,
        alert_id,
        BurnAlertCreate(
            alert_type=existing.alert_type,
            slo_id=existing.slo["id"] if existing.slo else "",
            description="Updated: Alert when budget depletes within 1 hour",
            exhaustion_minutes=60,  # Change from 120 to 60 minutes
            recipients=[BurnAlertRecipient(id=recipient_id)],
        ),
    )
    return updated
# end_example:update


# start_example:delete
async def delete_burn_alert(
    client: HoneycombClient, dataset: str, alert_id: str
) -> None:
    """Delete a burn alert.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the alert
        alert_id: ID of the burn alert to delete
    """
    await client.burn_alerts.delete_async(dataset, alert_id)
# end_example:delete


# start_example:list_sync
def list_burn_alerts_sync(
    client: HoneycombClient, dataset: str, slo_id: str
) -> list[BurnAlert]:
    """List burn alerts using sync client.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO

    Returns:
        List of burn alerts
    """
    alerts = client.burn_alerts.list(dataset, slo_id=slo_id)
    for alert in alerts:
        print(f"{alert.alert_type}: {alert.description}")
    return alerts
# end_example:list_sync


# TEST_ASSERTIONS
async def test_exhaustion_alert(
    client: HoneycombClient, dataset: str, alert_id: str
) -> None:
    """Verify exhaustion alert example worked."""
    alert = await client.burn_alerts.get_async(dataset, alert_id)
    assert alert.alert_type == BurnAlertType.EXHAUSTION_TIME
    assert alert.exhaustion_minutes == 120


async def test_budget_rate_alert(
    client: HoneycombClient, dataset: str, alert_id: str
) -> None:
    """Verify budget rate alert example worked."""
    alert = await client.burn_alerts.get_async(dataset, alert_id)
    assert alert.alert_type == BurnAlertType.BUDGET_RATE


async def test_list_burn_alerts(alerts: list[BurnAlert]) -> None:
    """Verify list example worked correctly."""
    assert isinstance(alerts, list)


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, alert_id: str) -> None:
    """Clean up resources created by example."""
    await delete_burn_alert(client, dataset, alert_id)

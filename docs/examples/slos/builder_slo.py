"""SLO Builder CRUD examples - using SLOBuilder for complex SLO creation."""

from __future__ import annotations

from honeycomb import (
    BurnAlertBuilder,
    BurnAlertType,
    HoneycombClient,
    SLO,
    SLOBuilder,
    SLOCreate,
)


# start_example:create_simple
async def create_simple_slo(client: HoneycombClient, dataset: str, sli_alias: str) -> str:
    """Create an SLO using SLOBuilder with existing derived column.

    This example creates a simple SLO using an existing derived column
    without any burn alerts.
    """
    bundle = (
        SLOBuilder("API Availability")
        .description("Track API request success rate")
        .dataset(dataset)
        .target_nines(3)  # 99.9%
        .time_period_days(30)
        .sli(alias=sli_alias)  # Use existing derived column
        .build()
    )

    slos = await client.slos.create_from_bundle_async(bundle)
    return slos[dataset].id
# end_example:create_simple


# start_example:create_with_new_column
async def create_slo_with_new_column(client: HoneycombClient, dataset: str) -> str:
    """Create an SLO with a new derived column using SLOBuilder.

    This example creates both a derived column and an SLO in one operation.
    The builder handles creating the derived column first, then the SLO.
    """
    import time

    # Use timestamp to ensure unique column names across test runs
    bundle = (
        SLOBuilder("Request Success Rate")
        .description("Percentage of successful requests")
        .dataset(dataset)
        .target_percentage(99.5)
        .time_period_weeks(4)
        .sli(
            alias=f"request_success_{int(time.time())}",
            expression="IF(LT($status_code, 400), 1, 0)",
            description="1 if request succeeded, 0 otherwise",
        )
        .build()
    )

    slos = await client.slos.create_from_bundle_async(bundle)
    return slos[dataset].id
# end_example:create_with_new_column


# start_example:create_with_burn_alerts
async def create_slo_with_burn_alerts(
    client: HoneycombClient, dataset: str, sli_alias: str, recipient_id: str
) -> str:
    """Create an SLO with burn alerts using SLOBuilder.

    This example creates an SLO with two burn alerts:
    1. Exhaustion time alert - triggers when budget will be exhausted soon
    2. Budget rate alert - triggers when burn rate exceeds threshold

    The builder handles creating the SLO and all burn alerts in one operation.
    """
    bundle = (
        SLOBuilder("Critical API SLO")
        .description("High-priority API availability tracking")
        .dataset(dataset)
        .target_nines(4)  # 99.99%
        .time_period_days(30)
        .sli(alias=sli_alias)
        # Add exhaustion time alert with existing recipient
        .exhaustion_alert(
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .description("Alert when budget exhausts in 1 hour")
            .recipient_id(recipient_id)
        )
        # Add budget rate alert with existing recipient
        .budget_rate_alert(
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
            .window_minutes(60)
            .threshold_percent(2.0)
            .description("Alert when burn rate exceeds 2% per hour")
            .recipient_id(recipient_id)
        )
        .build()
    )

    slos = await client.slos.create_from_bundle_async(bundle)
    return slos[dataset].id
# end_example:create_with_burn_alerts


# start_example:create_multi_dataset
async def create_multi_dataset_slo(
    client: HoneycombClient, datasets: list[str]
) -> dict[str, str]:
    """Create an SLO across multiple datasets using SLOBuilder.

    When creating an SLO for multiple datasets, any new derived column
    will be created as environment-wide. This allows the same SLI to be
    used across all datasets.
    """
    bundle = (
        SLOBuilder("Cross-Service Availability")
        .description("Overall service availability across all APIs")
        .datasets(datasets)  # Multiple datasets
        .target_percentage(99.9)
        .time_period_days(30)
        .sli(
            alias="service_success",
            expression="IF(EQUALS($status, 200), 1, 0)",
            description="1 for success, 0 for failure",
        )
        .budget_rate_alert(
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
            .window_minutes(60)
            .threshold_percent(1.0)
            .email("platform@example.com")
        )
        .build()
    )

    slos = await client.slos.create_from_bundle_async(bundle)
    # Return SLO IDs for each dataset
    return {dataset: slo.id for dataset, slo in slos.items()}
# end_example:create_multi_dataset


# start_example:get
async def get_slo(client: HoneycombClient, dataset: str, slo_id: str) -> SLO:
    """Get an SLO by ID."""
    return await client.slos.get_async(dataset, slo_id)
# end_example:get


# start_example:list
async def list_slos(client: HoneycombClient, dataset: str) -> list[SLO]:
    """List all SLOs in a dataset."""
    return await client.slos.list_async(dataset)
# end_example:list


# start_example:update
async def update_slo(client: HoneycombClient, dataset: str, slo_id: str) -> SLO:
    """Update an SLO's target.

    Note: Updates use the low-level SLOCreate model, not the builder.
    The builder is primarily for initial creation.
    """
    existing = await client.slos.get_async(dataset, slo_id)

    # Update the target to 99.95%
    updated = SLOCreate(
        name=existing.name,
        description=existing.description,
        sli=existing.sli,
        time_period_days=existing.time_period_days,
        target_per_million=999500,  # 99.95%
    )

    return await client.slos.update_async(dataset, slo_id, updated)
# end_example:update


# start_example:delete
async def delete_slo(client: HoneycombClient, dataset: str, slo_id: str) -> None:
    """Delete an SLO."""
    await client.slos.delete_async(dataset, slo_id)
# end_example:delete


# TEST_ASSERTIONS
async def test_lifecycle(
    client: HoneycombClient, dataset: str, slo_id: str, sli_alias: str
) -> None:
    """Verify the full lifecycle worked."""
    slo = await client.slos.get_async(dataset, slo_id)
    assert slo.id == slo_id
    assert slo.name == "API Availability"
    assert slo.sli["alias"] == sli_alias  # sli is dict, not SLI object
    assert slo.target_per_million == 999000  # 99.9%


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, slo_id: str) -> None:
    """Clean up resources (called even on test failure)."""
    try:
        # Burn alerts are auto-deleted when SLO is deleted
        await client.slos.delete_async(dataset, slo_id)
    except Exception:
        pass  # Already deleted or doesn't exist

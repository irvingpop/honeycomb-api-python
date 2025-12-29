"""Basic trigger creation examples.

These examples demonstrate creating triggers using both
the TriggerBuilder and manual construction patterns.
"""

from __future__ import annotations

from honeycomb import (
    HoneycombClient,
    QueryBuilder,
    TriggerBuilder,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
)


# start_example:simple_with_builder
async def create_simple_trigger(client: HoneycombClient, dataset: str) -> str:
    """Create a simple count-based trigger using TriggerBuilder.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create trigger in

    Returns:
        The created trigger ID
    """
    bundle = (
        TriggerBuilder("High Request Count")
        .dataset(dataset)
        .description("Alert when request count exceeds threshold")
        .last_30_minutes()
        .count()
        .threshold_gt(1000)
        .every_15_minutes()
        .disabled()  # Start disabled for safety
        .build()
    )
    created = await client.triggers.create_from_bundle_async(bundle)
    return created.id


# end_example:simple_with_builder


# start_example:trigger_with_filter
async def create_trigger_with_filter(client: HoneycombClient, dataset: str) -> str:
    """Create a trigger with filter conditions.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create trigger in

    Returns:
        The created trigger ID
    """
    bundle = (
        TriggerBuilder("Error Rate Alert")
        .dataset(dataset)
        .description("Alert on high error rate for API service")
        .last_30_minutes()
        .count()
        .gte("status_code", 500)
        .eq("service", "api")
        .threshold_gt(10)
        .every_15_minutes()
        .disabled()
        .build()
    )
    created = await client.triggers.create_from_bundle_async(bundle)
    return created.id


# end_example:trigger_with_filter


# start_example:manual_construction
async def create_trigger_manual(client: HoneycombClient, dataset: str) -> str:
    """Create a trigger using manual construction.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create trigger in

    Returns:
        The created trigger ID
    """
    trigger = TriggerCreate(
        name="Manual Test Trigger",
        description="Created without builder",
        threshold=TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN,
            value=100.0,
        ),
        frequency=900,
        disabled=True,
        query=QueryBuilder().last_30_minutes().count().build_for_trigger(),
    )
    created = await client.triggers.create_async(dataset, trigger)
    return created.id


# end_example:manual_construction


# start_example:list
async def list_triggers(client: HoneycombClient, dataset: str) -> list:
    """List all triggers in a dataset.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list triggers from

    Returns:
        List of triggers
    """
    triggers = await client.triggers.list_async(dataset)
    for trigger in triggers:
        status = "enabled" if not trigger.disabled else "disabled"
        print(f"{trigger.name} ({status}): threshold {trigger.threshold.value}")
    return triggers


# end_example:list


# start_example:get
async def get_trigger(client: HoneycombClient, dataset: str, trigger_id: str):
    """Get a trigger by ID.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the trigger
        trigger_id: ID of the trigger to retrieve

    Returns:
        The trigger object
    """
    trigger = await client.triggers.get_async(dataset, trigger_id)
    print(f"Name: {trigger.name}")
    print(f"Threshold: {trigger.threshold.op.value} {trigger.threshold.value}")
    print(f"Frequency: every {trigger.frequency}s")
    print(f"Status: {'enabled' if not trigger.disabled else 'disabled'}")
    return trigger


# end_example:get


# start_example:update
async def update_trigger(
    client: HoneycombClient, dataset: str, trigger_id: str
):
    """Update a trigger's threshold and enable it.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the trigger
        trigger_id: ID of the trigger to update

    Returns:
        The updated trigger
    """
    # Get existing trigger first to preserve values
    existing = await client.triggers.get_async(dataset, trigger_id)

    # Update with new values
    updated = TriggerCreate(
        name=existing.name,
        description=existing.description,
        threshold=TriggerThreshold(
            op=existing.threshold.op,
            value=200.0,  # Change threshold value
        ),
        frequency=existing.frequency,
        disabled=False,  # Enable the trigger
        query=existing.query,
    )

    result = await client.triggers.update_async(dataset, trigger_id, updated)
    return result


# end_example:update


# start_example:delete
async def delete_trigger(client: HoneycombClient, dataset: str, trigger_id: str) -> None:
    """Delete a trigger.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the trigger
        trigger_id: ID of the trigger to delete
    """
    await client.triggers.delete_async(dataset, trigger_id)


# end_example:delete


# TEST_ASSERTIONS
async def test_assertions(
    client: HoneycombClient, dataset: str, trigger_id: str, expected_name: str
) -> None:
    """Verify the example worked correctly."""
    trigger = await client.triggers.get_async(dataset, trigger_id)
    assert trigger.name == expected_name
    assert trigger.disabled is True


async def test_list_triggers(triggers: list) -> None:
    """Verify list example worked correctly."""
    assert isinstance(triggers, list)


async def test_get_trigger(trigger, expected_trigger_id: str) -> None:
    """Verify get example worked correctly."""
    assert trigger.id == expected_trigger_id
    assert trigger.name is not None


async def test_update_trigger(updated, original_trigger_id: str) -> None:
    """Verify update example worked correctly."""
    assert updated.id == original_trigger_id
    assert updated.threshold.value == 200.0
    assert updated.disabled is False


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, trigger_id: str) -> None:
    """Clean up resources created by example."""
    await delete_trigger(client, dataset, trigger_id)

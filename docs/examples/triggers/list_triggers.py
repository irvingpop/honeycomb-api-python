"""List and get triggers examples.

These examples demonstrate listing and retrieving triggers in a dataset.
"""

from __future__ import annotations

from honeycomb import HoneycombClient, Trigger


# start_example:list_async
async def list_triggers(client: HoneycombClient, dataset: str) -> list[Trigger]:
    """List all triggers in a dataset.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list triggers from

    Returns:
        List of triggers
    """
    triggers = await client.triggers.list_async(dataset)
    for trigger in triggers:
        print(f"{trigger.name}: {trigger.threshold.op} {trigger.threshold.value}")
        print(f"  Frequency: every {trigger.frequency}s")
        print(f"  State: {'triggered' if trigger.triggered else 'ok'}")
    return triggers


# end_example:list_async


# start_example:list_sync
def list_triggers_sync(client: HoneycombClient, dataset: str) -> list[Trigger]:
    """List triggers using sync client.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list triggers from

    Returns:
        List of triggers
    """
    triggers = client.triggers.list(dataset)
    for trigger in triggers:
        print(f"{trigger.name}: {trigger.threshold.op} {trigger.threshold.value}")
    return triggers


# end_example:list_sync


# start_example:get_trigger
async def get_trigger(client: HoneycombClient, dataset: str, trigger_id: str) -> Trigger:
    """Get a specific trigger by ID.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the trigger
        trigger_id: ID of the trigger to retrieve

    Returns:
        The trigger object
    """
    trigger = await client.triggers.get_async(dataset, trigger_id)
    print(f"Name: {trigger.name}")
    print(f"Description: {trigger.description}")
    print(f"Query: {trigger.query}")
    return trigger


# end_example:get_trigger


# start_example:delete_trigger
async def delete_trigger(client: HoneycombClient, dataset: str, trigger_id: str) -> None:
    """Delete a trigger.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the trigger
        trigger_id: ID of the trigger to delete
    """
    await client.triggers.delete_async(dataset, trigger_id)


# end_example:delete_trigger


# TEST_ASSERTIONS
async def test_assertions(triggers: list[Trigger]) -> None:
    """Verify the example worked correctly."""
    assert isinstance(triggers, list)

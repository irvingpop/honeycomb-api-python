"""List recipients examples.

These examples demonstrate listing all recipients in an environment.
"""

from __future__ import annotations

from honeycomb import HoneycombClient, Recipient


# start_example:list_async
async def list_all_recipients(client: HoneycombClient) -> list[Recipient]:
    """List all recipients in the environment.

    Returns:
        List of all recipients
    """
    recipients = await client.recipients.list_async()
    for recipient in recipients:
        print(f"{recipient.type}: {recipient.id}")
    return recipients


# end_example:list_async


# start_example:list_sync
def list_all_recipients_sync(client: HoneycombClient) -> list[Recipient]:
    """List all recipients using sync client.

    Returns:
        List of all recipients
    """
    recipients = client.recipients.list()
    for recipient in recipients:
        print(f"{recipient.type}: {recipient.id}")
    return recipients


# end_example:list_sync


# TEST_ASSERTIONS
async def test_assertions(recipients: list[Recipient]) -> None:
    """Verify the example worked correctly."""
    assert isinstance(recipients, list)

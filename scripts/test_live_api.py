#!/usr/bin/env python3
"""Test the wrapper client against the live Honeycomb API."""

import asyncio
import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from honeycomb import (
    HoneycombClient,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
    TriggerQuery,
    QueryCalculation,
    HoneycombNotFoundError,
)

# Load from environment variables
API_KEY = os.environ.get("HONEYCOMB_API_KEY")
if not API_KEY:
    print("ERROR: HONEYCOMB_API_KEY environment variable is not set")
    print("Please set it in your .envrc file or export it manually")
    sys.exit(1)

TEST_DATASET = os.environ.get("HONEYCOMB_TEST_DATASET", "test-dataset")


async def test_datasets():
    """Test dataset operations."""
    print("\n=== Testing Datasets ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # List datasets
        datasets = await client.datasets.list_async()
        print(f"Found {len(datasets)} datasets:")
        for ds in datasets[:5]:  # Show first 5
            print(f"  - {ds.name} (slug: {ds.slug})")

        # Get specific dataset
        if datasets:
            ds = await client.datasets.get_async(datasets[0].slug)
            print(f"\nGot dataset: {ds.name}")
            print(f"  Created: {ds.created_at}")
            print(f"  Columns: {ds.regular_columns_count}")


async def test_triggers():
    """Test trigger operations."""
    print("\n=== Testing Triggers ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # List existing triggers
        triggers = await client.triggers.list_async(TEST_DATASET)
        print(f"Found {len(triggers)} existing triggers in {TEST_DATASET}")
        for t in triggers:
            print(f"  - {t.name} (id: {t.id}, triggered: {t.triggered})")

        # Create a new trigger
        print("\nCreating a new trigger...")
        new_trigger = TriggerCreate(
            name="Test Wrapper Trigger",
            description="Created by wrapper client test",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN,
                value=100.0,
            ),
            frequency=900,  # 15 minutes
            query=TriggerQuery(
                time_range=900,  # 15 minutes (must be <= 3600)
                calculations=[QueryCalculation(op="COUNT")],
            ),
        )

        created = await client.triggers.create_async(TEST_DATASET, new_trigger)
        print(f"Created trigger: {created.name} (id: {created.id})")

        # Get the trigger we just created
        fetched = await client.triggers.get_async(TEST_DATASET, created.id)
        print(f"Fetched trigger: {fetched.name}")
        print(f"  Threshold: {fetched.threshold.op.value} {fetched.threshold.value}")
        print(f"  Frequency: {fetched.frequency}s")
        print(f"  Disabled: {fetched.disabled}")

        # Update the trigger
        print("\nUpdating trigger...")
        updated_trigger = TriggerCreate(
            name="Test Wrapper Trigger (Updated)",
            description="Updated by wrapper client test",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN_OR_EQUAL,
                value=150.0,
            ),
            frequency=900,
            query=TriggerQuery(
                time_range=900,
                calculations=[QueryCalculation(op="COUNT")],
            ),
        )
        updated = await client.triggers.update_async(TEST_DATASET, created.id, updated_trigger)
        print(f"Updated trigger: {updated.name}")
        print(f"  New threshold: {updated.threshold.op.value} {updated.threshold.value}")

        # Delete the trigger
        print("\nDeleting trigger...")
        await client.triggers.delete_async(TEST_DATASET, created.id)
        print("Trigger deleted successfully")

        # Verify deletion
        try:
            await client.triggers.get_async(TEST_DATASET, created.id)
            print("ERROR: Trigger still exists!")
        except HoneycombNotFoundError:
            print("Verified: Trigger no longer exists")


async def test_boards():
    """Test board operations."""
    print("\n=== Testing Boards ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # List boards
        boards = await client.boards.list_async()
        print(f"Found {len(boards)} boards:")
        for b in boards[:5]:
            print(f"  - {b.name} (id: {b.id})")


async def test_sync_client():
    """Test sync client operations."""
    print("\n=== Testing Sync Client ===")

    with HoneycombClient(api_key=API_KEY, sync=True) as client:
        datasets = client.datasets.list()
        print(f"Sync client found {len(datasets)} datasets")

        triggers = client.triggers.list(TEST_DATASET)
        print(f"Sync client found {len(triggers)} triggers in {TEST_DATASET}")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Honeycomb Wrapper Client against Live API")
    print("=" * 60)

    try:
        await test_datasets()
        await test_triggers()
        await test_boards()
        await test_sync_client()

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

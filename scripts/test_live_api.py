#!/usr/bin/env python3
"""Test the wrapper client against the live Honeycomb API.

Tests the following resources with API Key authentication:
- Datasets, Triggers, Boards (core resources)
- Columns, Markers, Recipients, Events (secondary resources)
- Sync client operations
- Rate limiting behavior

Not tested (require additional setup):
- Burn Alerts (requires existing SLO)
- API Keys and Environments (require Management Key authentication)
"""

import asyncio
import os
import sys

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from honeycomb import (  # type: ignore[import-untyped]
    BatchEvent,
    ColumnCreate,
    ColumnType,
    HoneycombClient,
    HoneycombNotFoundError,
    HoneycombRateLimitError,
    MarkerCreate,
    QueryCalculation,
    RecipientCreate,
    RecipientType,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)

# Load from environment variables
API_KEY = os.environ.get("HONEYCOMB_API_KEY")
if not API_KEY:
    print("ERROR: HONEYCOMB_API_KEY environment variable is not set")
    print("Please set it in your .envrc file or export it manually")
    sys.exit(1)

TEST_DATASET = os.environ.get("HONEYCOMB_TEST_DATASET", "test-dataset")


async def test_datasets() -> None:
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


async def test_triggers() -> None:
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


async def test_boards() -> None:
    """Test board operations."""
    print("\n=== Testing Boards ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # List boards
        boards = await client.boards.list_async()
        print(f"Found {len(boards)} boards:")
        for b in boards[:5]:
            print(f"  - {b.name} (id: {b.id})")


async def test_columns() -> None:
    """Test column operations."""
    print("\n=== Testing Columns ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # List columns
        columns = await client.columns.list_async(TEST_DATASET)
        print(f"Found {len(columns)} columns in {TEST_DATASET}:")
        for col in columns[:5]:
            print(f"  - {col.key_name} ({col.type.value})")

        # Create a test column
        print("\nCreating a test column...")
        new_column = ColumnCreate(
            key_name="test_wrapper_column",
            type=ColumnType.FLOAT,
            description="Test column created by wrapper client",
        )
        created = await client.columns.create_async(TEST_DATASET, new_column)
        print(f"Created column: {created.key_name} (id: {created.id})")

        # Clean up
        print("Deleting test column...")
        await client.columns.delete_async(TEST_DATASET, created.id)
        print("Column deleted successfully")


async def test_markers() -> None:
    """Test marker operations."""
    print("\n=== Testing Markers ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # List existing markers
        markers = await client.markers.list_async(TEST_DATASET)
        print(f"Found {len(markers)} markers in {TEST_DATASET}")

        # Create a marker
        print("\nCreating a test marker...")
        new_marker = MarkerCreate(
            message="Test deploy from wrapper client",
            type="test_deploy",
        )
        created = await client.markers.create_async(TEST_DATASET, new_marker)
        print(f"Created marker: {created.id} - {created.message}")

        # List marker settings
        settings = await client.markers.list_settings_async(TEST_DATASET)
        print(f"\nFound {len(settings)} marker settings for {TEST_DATASET}")

        # Clean up
        print("Deleting test marker...")
        await client.markers.delete_async(TEST_DATASET, created.id)
        print("Marker deleted successfully")


async def test_recipients() -> None:
    """Test recipient operations."""
    print("\n=== Testing Recipients ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # List recipients
        recipients = await client.recipients.list_async()
        print(f"Found {len(recipients)} recipients:")
        for r in recipients[:5]:
            print(f"  - {r.type.value} (id: {r.id})")

        # Create a test email recipient
        print("\nCreating a test recipient...")
        new_recipient = RecipientCreate(
            type=RecipientType.EMAIL,
            details={"email_address": "test-wrapper@example.com"}
        )
        created = await client.recipients.create_async(new_recipient)
        print(f"Created recipient: {created.id} ({created.type.value})")

        # Get triggers for this recipient
        triggers = await client.recipients.get_triggers_async(created.id)
        print(f"Recipient has {len(triggers)} associated triggers")

        # Clean up
        print("Deleting test recipient...")
        await client.recipients.delete_async(created.id)
        print("Recipient deleted successfully")


async def test_events() -> None:
    """Test event ingestion."""
    print("\n=== Testing Events ===")

    async with HoneycombClient(api_key=API_KEY) as client:
        # Send single event
        print("Sending single test event...")
        await client.events.send_async(
            TEST_DATASET,
            data={
                "test_source": "wrapper_client",
                "test_type": "live_api_test",
                "duration_ms": 42,
            }
        )
        print("Single event sent successfully")

        # Send batch of events
        print("\nSending batch of 3 test events...")
        events = [
            BatchEvent(data={"event": 1, "test": "batch"}),
            BatchEvent(data={"event": 2, "test": "batch"}),
            BatchEvent(data={"event": 3, "test": "batch"}),
        ]
        results = await client.events.send_batch_async(TEST_DATASET, events)
        print(f"Batch sent: {len(results)} results received")

        successful = [r for r in results if r.status == 202]
        failed = [r for r in results if r.status != 202]
        print(f"  ✓ {len(successful)} events accepted")
        if failed:
            print(f"  ✗ {len(failed)} events failed")
            for r in failed:
                print(f"    {r.status}: {r.error}")


async def test_sync_client() -> None:
    """Test sync client operations."""
    print("\n=== Testing Sync Client ===")

    with HoneycombClient(api_key=API_KEY, sync=True) as client:
        datasets = client.datasets.list()
        print(f"Sync client found {len(datasets)} datasets")

        triggers = client.triggers.list(TEST_DATASET)
        print(f"Sync client found {len(triggers)} triggers in {TEST_DATASET}")

        columns = client.columns.list(TEST_DATASET)
        print(f"Sync client found {len(columns)} columns in {TEST_DATASET}")

        markers = client.markers.list(TEST_DATASET)
        print(f"Sync client found {len(markers)} markers in {TEST_DATASET}")

        recipients = client.recipients.list()
        print(f"Sync client found {len(recipients)} recipients")


async def test_rate_limiting() -> None:
    """Test rate limiting and retry behavior.

    WARNING: This test intentionally triggers rate limits by making rapid requests!
    It will demonstrate the retry-after logic working correctly.
    """
    import time

    print("\n=== Testing Rate Limiting & Retry Logic ===")
    print("⚠️  WARNING: This test will make rapid requests to trigger rate limits!")
    print("    Press Ctrl+C within 3 seconds to skip this test...")

    try:
        await asyncio.sleep(3)
    except KeyboardInterrupt:
        print("\n⏭️  Rate limit test skipped by user")
        return

    # First, use a client with NO retries to detect the 429
    print("\n🔄 Phase 1: Making rapid requests (no retries) until rate limited...")

    async with HoneycombClient(api_key=API_KEY, max_retries=0) as client:
        datasets = await client.datasets.list_async()
        if not datasets:
            print("⚠️  No datasets available, skipping rate limit test")
            return

        test_dataset = datasets[0].slug
        rate_limit_hit = False
        retry_after_value = None
        request_count = 0
        max_requests = 200  # Safety limit

        for i in range(max_requests):
            try:
                await client.datasets.get_async(test_dataset)
                request_count += 1

                if i % 10 == 0 and i > 0:
                    print(f"  Request {i}... (no rate limit yet)")

            except HoneycombRateLimitError as e:
                rate_limit_hit = True
                retry_after_value = e.retry_after
                print(f"\n✓ Rate limit hit after {request_count} successful requests")
                print(f"  Status code: {e.status_code}")
                print(f"  Retry-After: {retry_after_value} seconds")
                print(f"  Message: {e.message}")
                if e.request_id:
                    print(f"  Request ID: {e.request_id}")
                break

    if not rate_limit_hit:
        print(f"\n⏭️  Rate limit not triggered after {max_requests} requests")
        print("    (API may have high rate limits - this is OK)")
        return

    # Now test automatic retry with the client's built-in retry logic
    print(f"\n🔄 Phase 2: Testing automatic retry (with {retry_after_value}s wait)...")

    async with HoneycombClient(api_key=API_KEY, max_retries=2) as client:
        start_time = time.time()

        try:
            # This should hit 429, wait for retry_after, then succeed
            result = await client.datasets.get_async(test_dataset)
            elapsed = time.time() - start_time

            print("✓ Request succeeded after automatic retry!")
            print(f"  Total time: {elapsed:.2f}s")
            print(f"  Retrieved dataset: {result.name}")

            # Verify the client waited approximately the right amount of time
            if retry_after_value and retry_after_value > 0:
                expected_wait = retry_after_value
                if elapsed >= expected_wait * 0.8:  # Allow 20% variance
                    print(f"✓ Client correctly waited ~{expected_wait}s before retrying")
                else:
                    print(f"⚠️  Client waited {elapsed:.2f}s (expected ~{expected_wait}s)")

        except HoneycombRateLimitError:
            elapsed = time.time() - start_time
            print(f"⚠️  Still rate limited after {elapsed:.2f}s")
            print("  This can happen if the rate limit window is longer than retry attempts")
            print(f"  The client DID attempt retries (waited {elapsed:.2f}s)")

    # Test that we can successfully make a request after waiting
    if retry_after_value and retry_after_value > 0:
        print(f"\n🔄 Phase 3: Waiting full {retry_after_value}s and trying again...")
        await asyncio.sleep(retry_after_value)

        async with HoneycombClient(api_key=API_KEY, max_retries=0) as client:
            try:
                result = await client.datasets.get_async(test_dataset)
                print(f"✓ Request succeeded after waiting {retry_after_value}s!")
                print(f"  Dataset: {result.name}")
            except HoneycombRateLimitError:
                print(f"⚠️  Still rate limited (rate window may be > {retry_after_value}s)")

    print("\n✓ Rate limiting test completed")


async def main() -> int:
    """Run all tests."""
    print("=" * 60)
    print("Testing Honeycomb Wrapper Client against Live API")
    print("=" * 60)

    try:
        # Core resources
        await test_datasets()
        await test_triggers()
        await test_boards()

        # Secondary resources
        await test_columns()
        await test_markers()
        await test_recipients()
        await test_events()

        # Sync client
        await test_sync_client()

        # Rate limiting (optional, user can skip)
        await test_rate_limiting()

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

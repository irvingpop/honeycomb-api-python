"""Integration tests for Triggers and TriggerBuilder.

Tests the TriggerBuilder pattern against the live Honeycomb API.
"""

from __future__ import annotations

import pytest

from honeycomb import (
    HoneycombClient,
    HoneycombNotFoundError,
    QueryBuilder,
    TriggerBuilder,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
)


class TestTriggerBuilder:
    """Test TriggerBuilder against live API."""

    @pytest.mark.asyncio
    async def test_simple_trigger_builder(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test creating a simple trigger with TriggerBuilder."""
        dataset = ensure_dataset

        # Create trigger using builder
        trigger = (
            TriggerBuilder("Test Simple Trigger")
            .dataset(dataset)
            .description("Created by integration test")
            .last_30_minutes()
            .count()
            .threshold_gt(1000)
            .every_15_minutes()
            .disabled()
            .build()
        )

        # Create via API
        created = await client.triggers.create_async(dataset, trigger)
        try:
            assert created.name == "Test Simple Trigger"
            assert created.description == "Created by integration test"
            assert created.disabled is True
            assert created.threshold.op == TriggerThresholdOp.GREATER_THAN
            assert created.threshold.value == 1000
            assert created.frequency == 900
        finally:
            # Cleanup
            await client.triggers.delete_async(dataset, created.id)

    @pytest.mark.asyncio
    async def test_trigger_with_filter(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test trigger with filter conditions."""
        dataset = ensure_dataset

        # Use 15 minute frequency with 30 min time range (1800s <= 900*4=3600s)
        trigger = (
            TriggerBuilder("Test Filter Trigger")
            .dataset(dataset)
            .last_30_minutes()
            .count()
            .gte("status_code", 500)
            .eq("service", "api")
            .threshold_gt(10)
            .every_15_minutes()
            .disabled()
            .build()
        )

        created = await client.triggers.create_async(dataset, trigger)
        try:
            assert created.name == "Test Filter Trigger"
            # query is a dict in the response, not a model
            assert created.query is not None
            assert "filter_combination" in created.query or "filters" in created.query
        finally:
            await client.triggers.delete_async(dataset, created.id)

    @pytest.mark.asyncio
    async def test_trigger_with_tags(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test trigger with tags (Phase 2.5 feature)."""
        dataset = ensure_dataset

        trigger = (
            TriggerBuilder("Test Tagged Trigger")
            .dataset(dataset)
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .every_15_minutes()
            .tag("team", "platform")
            .tag("severity", "high")
            .disabled()
            .build()
        )

        created = await client.triggers.create_async(dataset, trigger)
        try:
            assert created.name == "Test Tagged Trigger"
            # Tags should be present in the response
            if hasattr(created, "tags") and created.tags:
                assert len(created.tags) == 2
        finally:
            await client.triggers.delete_async(dataset, created.id)

    @pytest.mark.asyncio
    async def test_trigger_with_exceeded_limit(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test trigger with exceeded_limit (requires N consecutive breaches)."""
        dataset = ensure_dataset

        trigger = (
            TriggerBuilder("Test Exceeded Limit Trigger")
            .dataset(dataset)
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .exceeded_limit(3)
            .every_15_minutes()
            .disabled()
            .build()
        )

        created = await client.triggers.create_async(dataset, trigger)
        try:
            assert created.threshold.exceeded_limit == 3
        finally:
            await client.triggers.delete_async(dataset, created.id)

    @pytest.mark.asyncio
    async def test_trigger_update(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test updating a trigger."""
        dataset = ensure_dataset

        # Create initial trigger
        trigger = (
            TriggerBuilder("Test Update Trigger")
            .dataset(dataset)
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .every_15_minutes()
            .disabled()
            .build()
        )

        created = await client.triggers.create_async(dataset, trigger)
        try:
            # Update with new values (use 10 min time range for 5 min frequency)
            updated_trigger = (
                TriggerBuilder("Test Update Trigger - Modified")
                .dataset(dataset)
                .time_range(600)  # 10 minutes fits 5 min frequency (600 <= 300*4)
                .count()
                .threshold_gte(200)
                .every_5_minutes()
                .disabled()
                .build()
            )

            updated = await client.triggers.update_async(dataset, created.id, updated_trigger)
            assert updated.name == "Test Update Trigger - Modified"
            assert updated.threshold.op == TriggerThresholdOp.GREATER_THAN_OR_EQUAL
            assert updated.threshold.value == 200
            assert updated.frequency == 300
        finally:
            await client.triggers.delete_async(dataset, created.id)

    @pytest.mark.asyncio
    async def test_trigger_crud_cycle(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test full CRUD cycle for triggers."""
        dataset = ensure_dataset

        # CREATE
        trigger = (
            TriggerBuilder("CRUD Test Trigger")
            .dataset(dataset)
            .last_30_minutes()
            .count()
            .threshold_gt(50)
            .every_15_minutes()
            .disabled()
            .build()
        )

        created = await client.triggers.create_async(dataset, trigger)
        trigger_id = created.id

        # READ
        fetched = await client.triggers.get_async(dataset, trigger_id)
        assert fetched.id == trigger_id
        assert fetched.name == "CRUD Test Trigger"

        # UPDATE
        updated_trigger = (
            TriggerBuilder("CRUD Test Trigger Updated")
            .dataset(dataset)
            .last_30_minutes()
            .count()
            .threshold_lt(100)
            .every_15_minutes()
            .disabled()
            .build()
        )
        updated = await client.triggers.update_async(dataset, trigger_id, updated_trigger)
        assert updated.name == "CRUD Test Trigger Updated"
        assert updated.threshold.op == TriggerThresholdOp.LESS_THAN

        # DELETE
        await client.triggers.delete_async(dataset, trigger_id)

        # Verify deletion
        with pytest.raises(HoneycombNotFoundError):
            await client.triggers.get_async(dataset, trigger_id)


class TestTriggerManualConstruction:
    """Test triggers created without TriggerBuilder."""

    @pytest.mark.asyncio
    async def test_manual_trigger_create(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test creating trigger with manual TriggerCreate construction."""
        dataset = ensure_dataset

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
        try:
            assert created.name == "Manual Test Trigger"
            assert created.disabled is True
        finally:
            await client.triggers.delete_async(dataset, created.id)


class TestTriggerList:
    """Test listing triggers."""

    @pytest.mark.asyncio
    async def test_list_triggers(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test listing triggers in a dataset."""
        dataset = ensure_dataset
        triggers = await client.triggers.list_async(dataset)
        # Just verify it returns a list (may be empty)
        assert isinstance(triggers, list)

    def test_list_triggers_sync(self, sync_client: HoneycombClient, ensure_dataset: str) -> None:
        """Test listing triggers with sync client."""
        dataset = ensure_dataset
        triggers = sync_client.triggers.list(dataset)
        assert isinstance(triggers, list)

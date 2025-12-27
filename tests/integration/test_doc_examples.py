"""Integration tests for documentation examples.

These tests import and run the executable examples from docs/examples/,
ensuring that all documentation code snippets work against the live API.

This is part of the "Executable Documentation" approach where:
1. Code examples live in docs/examples/*.py with named sections
2. Documentation includes these sections via mkdocs-include-markdown-plugin
3. This test file runs the examples to ensure they actually work
"""

from __future__ import annotations

import contextlib

import pytest

from honeycomb import HoneycombClient


class TestRecipientExamples:
    """Test recipient examples from docs/examples/recipients/."""

    @pytest.mark.asyncio
    async def test_email_with_builder(self, client: HoneycombClient) -> None:
        """Test email recipient creation with RecipientBuilder."""
        from docs.examples.recipients.email_recipient import (
            cleanup,
            create_email_recipient,
            test_assertions,
        )

        recipient_id = await create_email_recipient(client)
        try:
            await test_assertions(client, recipient_id)
        finally:
            await cleanup(client, recipient_id)

    @pytest.mark.asyncio
    async def test_email_manual(self, client: HoneycombClient) -> None:
        """Test email recipient creation with manual construction."""
        from docs.examples.recipients.email_recipient import (
            cleanup,
            create_email_recipient_manual,
            test_assertions,
        )

        recipient_id = await create_email_recipient_manual(client)
        try:
            await test_assertions(client, recipient_id)
        finally:
            await cleanup(client, recipient_id)

    @pytest.mark.asyncio
    async def test_webhook_with_builder(self, client: HoneycombClient) -> None:
        """Test webhook recipient creation with RecipientBuilder."""
        from docs.examples.recipients.webhook_recipient import (
            cleanup,
            create_webhook_recipient,
            test_assertions,
        )

        recipient_id = await create_webhook_recipient(client)
        try:
            await test_assertions(client, recipient_id)
        finally:
            await cleanup(client, recipient_id)

    @pytest.mark.asyncio
    async def test_list_recipients(self, client: HoneycombClient) -> None:
        """Test listing recipients."""
        from docs.examples.recipients.list_recipients import (
            list_all_recipients,
            test_assertions,
        )

        recipients = await list_all_recipients(client)
        await test_assertions(recipients)


class TestDerivedColumnExamples:
    """Test derived column examples from docs/examples/derived_columns/."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("ensure_columns")
    async def test_simple_with_builder(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test simple derived column with DerivedColumnBuilder.

        Note: ensure_columns fixture creates trace.trace_id which is used in the expression.
        """
        from docs.examples.derived_columns.basic_derived_column import (
            cleanup,
            create_simple_derived_column,
            test_assertions,
        )

        dc_id = await create_simple_derived_column(client, ensure_dataset)
        try:
            await test_assertions(client, ensure_dataset, dc_id, "has_trace")
        finally:
            await cleanup(client, ensure_dataset, dc_id)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("ensure_columns")
    async def test_if_expression(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test derived column with IF expression.

        Note: ensure_columns fixture creates status_code which is used in the expression.
        """
        from docs.examples.derived_columns.basic_derived_column import (
            cleanup,
            create_if_expression_column,
        )

        dc_id = await create_if_expression_column(client, ensure_dataset)
        try:
            # Get the actual alias (it's timestamped)
            dc = await client.derived_columns.get_async(ensure_dataset, dc_id)
            assert dc.id == dc_id
            assert "request_success" in dc.alias  # Timestamped alias
            assert dc.expression == "IF(LT($status_code, 400), 1, 0)"
        finally:
            await cleanup(client, ensure_dataset, dc_id)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("ensure_columns")
    async def test_manual_construction(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test derived column with manual construction.

        Note: ensure_columns fixture creates trace.span_id which is used in the expression.
        """
        from docs.examples.derived_columns.basic_derived_column import (
            cleanup,
            create_derived_column_manual,
            test_assertions,
        )

        dc_id = await create_derived_column_manual(client, ensure_dataset)
        try:
            await test_assertions(client, ensure_dataset, dc_id, "has_span")
        finally:
            await cleanup(client, ensure_dataset, dc_id)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("ensure_columns")
    async def test_environment_wide_column(self, client: HoneycombClient) -> None:
        """Test environment-wide derived column.

        Note: ensure_columns fixture creates trace.trace_id in a dataset, which allows
        the environment-wide derived column expression to validate.
        """
        from docs.examples.derived_columns.environment_wide import (
            cleanup,
            create_environment_wide_column,
            test_assertions,
        )

        dc_id = await create_environment_wide_column(client)
        try:
            await test_assertions(client, dc_id)
        finally:
            await cleanup(client, dc_id)

    @pytest.mark.asyncio
    async def test_list_derived_columns(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test listing derived columns."""
        from docs.examples.derived_columns.list_columns import (
            list_derived_columns,
            test_assertions,
        )

        columns = await list_derived_columns(client, ensure_dataset)
        await test_assertions(columns)

    @pytest.mark.asyncio
    async def test_list_environment_wide_columns(self, client: HoneycombClient) -> None:
        """Test listing environment-wide derived columns."""
        from docs.examples.derived_columns.environment_wide import (
            list_environment_wide_columns,
        )

        columns = await list_environment_wide_columns(client)
        assert isinstance(columns, list)


class TestEventExamples:
    """Test event examples from docs/examples/events/.

    Note: Events cannot be deleted. They persist in the dataset as telemetry data.
    """

    @pytest.mark.asyncio
    async def test_send_event(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test sending a single event."""
        from docs.examples.events.basic_event import (
            send_event,
            test_send_event,
        )

        await send_event(client, ensure_dataset)
        await test_send_event(client, ensure_dataset)

    @pytest.mark.asyncio
    async def test_send_batch(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test sending a batch of events."""
        from docs.examples.events.basic_event import (
            send_batch,
            test_send_batch,
        )

        await send_batch(client, ensure_dataset)
        await test_send_batch(client, ensure_dataset)

    @pytest.mark.asyncio
    async def test_verify_events(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test verifying events via query."""
        # Send some events first
        from docs.examples.events.basic_event import (
            send_batch,
            test_verify_events,
            verify_events,
        )

        await send_batch(client, ensure_dataset)

        # Verify they're queryable
        count = await verify_events(client, ensure_dataset)
        await test_verify_events(count)


class TestTriggerExamples:
    """Test trigger examples from docs/examples/triggers/."""

    @pytest.mark.asyncio
    async def test_trigger_lifecycle(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test full trigger CRUD lifecycle: list -> create -> get -> update -> delete."""
        from docs.examples.triggers.basic_trigger import (
            create_simple_trigger,
            delete_trigger,
            get_trigger,
            list_triggers,
            test_get_trigger,
            test_list_triggers,
            test_update_trigger,
            update_trigger,
        )

        # List (before create)
        initial_triggers = await list_triggers(client, ensure_dataset)
        await test_list_triggers(initial_triggers)
        initial_count = len(initial_triggers)

        # Create
        trigger_id = await create_simple_trigger(client, ensure_dataset)
        try:
            # Get
            trigger = await get_trigger(client, ensure_dataset, trigger_id)
            await test_get_trigger(trigger, trigger_id)

            # Update
            updated = await update_trigger(client, ensure_dataset, trigger_id)
            await test_update_trigger(updated, trigger_id)

            # List (after create - verify it appears)
            triggers = await list_triggers(client, ensure_dataset)
            assert len(triggers) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            await delete_trigger(client, ensure_dataset, trigger_id)

    @pytest.mark.asyncio
    async def test_simple_trigger(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test simple trigger creation with TriggerBuilder."""
        from docs.examples.triggers.basic_trigger import (
            cleanup,
            create_simple_trigger,
            test_assertions,
        )

        trigger_id = await create_simple_trigger(client, ensure_dataset)
        try:
            await test_assertions(client, ensure_dataset, trigger_id, "High Request Count")
        finally:
            await cleanup(client, ensure_dataset, trigger_id)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("ensure_columns")
    async def test_trigger_with_filter(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test trigger with filter conditions.

        Note: ensure_columns fixture creates status_code and service columns.
        """
        from docs.examples.triggers.basic_trigger import (
            cleanup,
            create_trigger_with_filter,
            test_assertions,
        )

        trigger_id = await create_trigger_with_filter(client, ensure_dataset)
        try:
            await test_assertions(client, ensure_dataset, trigger_id, "Error Rate Alert")
        finally:
            await cleanup(client, ensure_dataset, trigger_id)

    @pytest.mark.asyncio
    async def test_manual_trigger(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test manual trigger construction."""
        from docs.examples.triggers.basic_trigger import (
            cleanup,
            create_trigger_manual,
            test_assertions,
        )

        trigger_id = await create_trigger_manual(client, ensure_dataset)
        try:
            await test_assertions(client, ensure_dataset, trigger_id, "Manual Test Trigger")
        finally:
            await cleanup(client, ensure_dataset, trigger_id)

    @pytest.mark.asyncio
    async def test_list_triggers(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test listing triggers."""
        from docs.examples.triggers.list_triggers import (
            list_triggers,
            test_assertions,
        )

        triggers = await list_triggers(client, ensure_dataset)
        await test_assertions(triggers)


class TestQueryExamples:
    """Test query examples from docs/examples/queries/.

    Note: The Honeycomb API does not support deleting saved queries, so these tests
    will create queries that persist in the test dataset.
    """

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("ensure_columns")
    async def test_create_and_run(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test create and run query pattern.

        Note: ensure_columns fixture creates duration_ms and service columns.
        """
        from docs.examples.queries.basic_query import (
            create_and_run_query,
            test_create_and_run,
        )

        query, result = await create_and_run_query(client, ensure_dataset)
        await test_create_and_run(query, result)
        # Note: Cannot delete - queries persist

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("ensure_columns")
    async def test_save_then_run(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test save then run query pattern.

        Note: ensure_columns fixture creates duration_ms and endpoint columns.
        """
        from docs.examples.queries.basic_query import (
            get_query,
            save_then_run_query,
            test_get_query,
            test_save_then_run,
        )

        query, result = await save_then_run_query(client, ensure_dataset)
        await test_save_then_run(query, result)

        # Test get_query
        retrieved = await get_query(client, ensure_dataset, query.id)
        await test_get_query(retrieved, query.id)
        # Note: Cannot delete - queries persist


class TestBoardExamples:
    """Test board examples from docs/examples/boards/."""

    @pytest.mark.asyncio
    async def test_board_lifecycle(self, client: HoneycombClient) -> None:
        """Test full board CRUD lifecycle: list -> create -> get -> update -> delete."""
        from docs.examples.boards.basic_board import (
            create_basic_board,
            delete_board,
            get_board,
            list_boards,
            test_get_board,
            test_list_boards,
            test_update_board,
            update_board,
        )

        # List (before create)
        initial_boards = await list_boards(client)
        await test_list_boards(initial_boards)
        initial_count = len(initial_boards)

        # Create
        board_id = await create_basic_board(client)
        try:
            # Get
            board = await get_board(client, board_id)
            await test_get_board(board, board_id)

            # Update
            updated = await update_board(client, board_id)
            await test_update_board(updated, board_id)

            # List (after create - verify it appears)
            boards = await list_boards(client)
            assert len(boards) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            await delete_board(client, board_id)

    @pytest.mark.asyncio
    async def test_create_board(self, client: HoneycombClient) -> None:
        """Test board creation."""
        from docs.examples.boards.basic_board import (
            cleanup,
            create_basic_board,
            test_create_board,
        )

        board_id = await create_basic_board(client)
        try:
            await test_create_board(client, board_id)
        finally:
            await cleanup(client, board_id)

    @pytest.mark.asyncio
    async def test_list_boards(self, client: HoneycombClient) -> None:
        """Test listing boards."""
        from docs.examples.boards.basic_board import (
            list_boards,
            test_list_boards,
        )

        boards = await list_boards(client)
        await test_list_boards(boards)


class TestColumnExamples:
    """Test column examples from docs/examples/columns/."""

    @pytest.mark.asyncio
    async def test_column_lifecycle(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test full column CRUD lifecycle: list -> create -> get -> update -> delete."""
        from docs.examples.columns.basic_column import (
            create_basic_column,
            delete_column,
            get_column,
            list_columns,
            test_get_column,
            test_update_column,
            update_column,
        )

        # List (before create)
        initial_columns = await list_columns(client, ensure_dataset)
        initial_count = len(initial_columns)

        # Create
        column_id = await create_basic_column(client, ensure_dataset)
        try:
            # Get
            column = await get_column(client, ensure_dataset, column_id)
            await test_get_column(column, column_id)

            # Update
            updated = await update_column(client, ensure_dataset, column_id)
            await test_update_column(updated, column_id)

            # List (after create - verify it appears)
            columns = await list_columns(client, ensure_dataset)
            assert len(columns) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            await delete_column(client, ensure_dataset, column_id)

    @pytest.mark.asyncio
    async def test_create_column(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test column creation."""
        from docs.examples.columns.basic_column import (
            cleanup,
            create_basic_column,
            test_create_column,
        )

        column_id = await create_basic_column(client, ensure_dataset)
        try:
            await test_create_column(client, ensure_dataset, column_id)
        finally:
            await cleanup(client, ensure_dataset, column_id)

    @pytest.mark.asyncio
    async def test_list_columns(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test listing columns."""
        from docs.examples.columns.basic_column import (
            list_columns,
            test_list_columns,
        )

        columns = await list_columns(client, ensure_dataset)
        await test_list_columns(columns)


class TestDatasetExamples:
    """Test dataset examples from docs/examples/datasets/."""

    @pytest.mark.asyncio
    async def test_list_datasets(self, client: HoneycombClient) -> None:
        """Test listing datasets."""
        from docs.examples.datasets.basic_dataset import (
            list_datasets,
            test_list_datasets,
        )

        datasets = await list_datasets(client)
        await test_list_datasets(datasets)

    @pytest.mark.asyncio
    async def test_create_dataset(self, client: HoneycombClient) -> None:
        """Test creating a dataset with unique name."""
        from docs.examples.datasets.basic_dataset import (
            cleanup,
            create_dataset,
            test_create_dataset,
        )

        # Create with auto-generated unique name
        dataset_slug = await create_dataset(client)
        try:
            await test_create_dataset(client, dataset_slug)
        finally:
            await cleanup(client, dataset_slug)

    @pytest.mark.asyncio
    async def test_get_dataset(self, client: HoneycombClient) -> None:
        """Test getting a dataset."""
        from docs.examples.datasets.basic_dataset import (
            cleanup,
            create_dataset,
            get_dataset,
            test_get_dataset,
        )

        # Create a dataset first
        dataset_slug = await create_dataset(client)
        try:
            dataset = await get_dataset(client, dataset_slug)
            await test_get_dataset(dataset, dataset_slug)
        finally:
            await cleanup(client, dataset_slug)

    @pytest.mark.asyncio
    async def test_update_dataset(self, client: HoneycombClient) -> None:
        """Test updating a dataset."""
        from docs.examples.datasets.basic_dataset import (
            cleanup,
            create_dataset,
            test_update_dataset,
            update_dataset,
        )

        # Create a dataset first
        dataset_slug = await create_dataset(client)
        try:
            updated = await update_dataset(client, dataset_slug)
            await test_update_dataset(updated)
        finally:
            await cleanup(client, dataset_slug)


class TestMarkerExamples:
    """Test marker examples from docs/examples/markers/."""

    @pytest.mark.asyncio
    async def test_marker_lifecycle(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test full marker CRUD lifecycle: list -> create -> update -> delete."""
        from docs.examples.markers.basic_marker import (
            create_deploy_marker,
            delete_marker,
            list_markers,
            test_list_markers,
            update_marker,
        )

        # List (before create)
        initial_markers = await list_markers(client, ensure_dataset)
        await test_list_markers(initial_markers)
        initial_count = len(initial_markers)

        # Create
        marker_id = await create_deploy_marker(client, ensure_dataset)
        try:
            # Note: Markers don't have a get endpoint, verify via list
            markers = await list_markers(client, ensure_dataset)
            marker_ids = [m.id for m in markers]
            assert marker_id in marker_ids
            assert len(markers) == initial_count + 1

            # Update
            updated = await update_marker(client, ensure_dataset, marker_id)
            assert updated.message == "Updated: Backend deploy v2.5.0 - success"
        finally:
            # Delete (always, even on failure)
            await delete_marker(client, ensure_dataset, marker_id)

    @pytest.mark.asyncio
    async def test_create_marker(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test marker creation."""
        from docs.examples.markers.basic_marker import (
            cleanup,
            create_deploy_marker,
            test_create_marker,
        )

        marker_id = await create_deploy_marker(client, ensure_dataset)
        try:
            await test_create_marker(client, ensure_dataset, marker_id)
        finally:
            await cleanup(client, ensure_dataset, marker_id)

    @pytest.mark.asyncio
    async def test_list_markers(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test listing markers."""
        from docs.examples.markers.basic_marker import (
            list_markers,
            test_list_markers,
        )

        markers = await list_markers(client, ensure_dataset)
        await test_list_markers(markers)


class TestSLOExamples:
    """Test SLO examples from docs/examples/slos/.

    These tests require the create_unique_sli fixture which creates a unique derived
    column that can be used as an SLI, avoiding conflicts with existing SLOs.
    """

    @pytest.mark.asyncio
    async def test_slo_lifecycle(
        self, client: HoneycombClient, ensure_dataset: str, create_unique_sli: str
    ) -> None:
        """Test full SLO CRUD lifecycle: list -> create -> get -> update -> delete."""
        from docs.examples.slos.basic_slo import (
            delete_slo,
            get_slo,
            list_slos,
            test_list_slos,
        )

        from honeycomb import SLI, SLOCreate

        # List (before create)
        initial_slos = await list_slos(client, ensure_dataset)
        await test_list_slos(initial_slos)
        initial_count = len(initial_slos)

        # Create SLO with unique SLI
        slo = await client.slos.create_async(
            ensure_dataset,
            SLOCreate(
                name="API Availability Lifecycle Test",
                description="99.9% availability target for API service",
                sli=SLI(alias=create_unique_sli),
                time_period_days=30,
                target_per_million=999000,
            ),
        )
        slo_id = slo.id
        try:
            # Get
            slo = await get_slo(client, ensure_dataset, slo_id)
            assert slo.id == slo_id
            assert slo.name == "API Availability Lifecycle Test"
            assert slo.target_per_million == 999000

            # Update
            updated = await client.slos.update_async(
                ensure_dataset,
                slo_id,
                SLOCreate(
                    name="Updated API Availability Lifecycle Test",
                    description="Updated: 99.99% availability target",
                    sli=SLI(alias=create_unique_sli),
                    time_period_days=30,
                    target_per_million=999900,
                ),
            )
            assert updated.id == slo_id
            assert updated.name == "Updated API Availability Lifecycle Test"
            assert updated.target_per_million == 999900  # Updated to 99.99%

            # List (after create - verify it appears)
            slos = await list_slos(client, ensure_dataset)
            assert len(slos) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            await delete_slo(client, ensure_dataset, slo_id)

    @pytest.mark.asyncio
    async def test_create_slo(
        self, client: HoneycombClient, ensure_dataset: str, create_unique_sli: str
    ) -> None:
        """Test SLO creation."""
        from docs.examples.slos.basic_slo import (
            cleanup,
            test_create_slo,
        )

        from honeycomb import SLI, SLOCreate

        # Create SLO with unique SLI
        slo = await client.slos.create_async(
            ensure_dataset,
            SLOCreate(
                name="API Availability Test",
                description="99.9% availability target for API service",
                sli=SLI(alias=create_unique_sli),
                time_period_days=30,
                target_per_million=999000,
            ),
        )
        slo_id = slo.id
        try:
            await test_create_slo(client, ensure_dataset, slo_id)
        finally:
            await cleanup(client, ensure_dataset, slo_id)

    @pytest.mark.asyncio
    async def test_list_slos(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test listing SLOs."""
        from docs.examples.slos.basic_slo import (
            list_slos,
            test_list_slos,
        )

        slos = await list_slos(client, ensure_dataset)
        await test_list_slos(slos)

    @pytest.mark.asyncio
    async def test_builder_simple(
        self, client: HoneycombClient, ensure_dataset: str, create_unique_sli: str
    ) -> None:
        """Test simple SLO creation with SLOBuilder."""
        from docs.examples.slos.builder_slo import (
            cleanup,
            create_simple_slo,
            test_lifecycle,
        )

        slo_id = await create_simple_slo(client, ensure_dataset, create_unique_sli)
        try:
            await test_lifecycle(client, ensure_dataset, slo_id, create_unique_sli)
        finally:
            await cleanup(client, ensure_dataset, slo_id)

    @pytest.mark.asyncio
    async def test_builder_with_new_column(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test SLO creation with new derived column using SLOBuilder."""
        from docs.examples.slos.builder_slo import (
            cleanup,
            create_slo_with_new_column,
        )

        slo_id = await create_slo_with_new_column(client, ensure_dataset)
        try:
            # Verify SLO was created
            slo = await client.slos.get_async(ensure_dataset, slo_id)
            assert slo.id == slo_id
            # sli is dict, not SLI object
            assert "request_success" in slo.sli["alias"]  # Timestamped alias
            assert slo.target_per_million == 995000  # 99.5%

            # Store alias for cleanup
            sli_alias = slo.sli["alias"]
        finally:
            await cleanup(client, ensure_dataset, slo_id)
            # Also clean up the derived column (with timestamp)
            with contextlib.suppress(Exception):
                await client.derived_columns.delete_async(ensure_dataset, sli_alias)

    @pytest.mark.asyncio
    async def test_builder_with_burn_alerts(
        self,
        client: HoneycombClient,
        ensure_dataset: str,
        create_unique_sli: str,
        ensure_recipient: str,
    ) -> None:
        """Test SLO creation with burn alerts using SLOBuilder.

        Note: This test creates an SLO with both exhaustion and budget rate alerts.
        The builder handles creating all resources in the correct order.
        """
        from docs.examples.slos.builder_slo import (
            cleanup,
            create_slo_with_burn_alerts,
        )

        slo_id = await create_slo_with_burn_alerts(
            client, ensure_dataset, create_unique_sli, ensure_recipient
        )
        try:
            # Verify SLO was created
            slo = await client.slos.get_async(ensure_dataset, slo_id)
            assert slo.id == slo_id
            assert slo.name == "Critical API SLO"
            assert slo.target_per_million == 999900  # 99.99%

            # Verify burn alerts were created
            burn_alerts = await client.burn_alerts.list_async(ensure_dataset, slo_id)
            assert len(burn_alerts) == 2

            # Check we have both types
            alert_types = {alert.alert_type for alert in burn_alerts}
            from honeycomb import BurnAlertType

            assert BurnAlertType.EXHAUSTION_TIME in alert_types
            assert BurnAlertType.BUDGET_RATE in alert_types
        finally:
            await cleanup(client, ensure_dataset, slo_id)


class TestBurnAlertExamples:
    """Test burn alert examples from docs/examples/burn_alerts/.

    These tests require the ensure_slo fixture which creates an SLO
    that burn alerts can be attached to, and ensure_recipient for notifications.
    """

    @pytest.mark.asyncio
    async def test_burn_alert_lifecycle(
        self,
        client: HoneycombClient,
        ensure_dataset: str,
        ensure_slo: tuple[str, str],
        ensure_recipient: str,
    ) -> None:
        """Test full burn alert CRUD lifecycle: list -> create -> get -> update -> delete."""
        from docs.examples.burn_alerts.basic_burn_alert import (
            BurnAlertType,
            create_exhaustion_time_alert,
            delete_burn_alert,
            get_burn_alert,
            list_burn_alerts,
            test_list_burn_alerts,
            update_burn_alert,
        )

        slo_id, _ = ensure_slo

        # List (before create)
        initial_alerts = await list_burn_alerts(client, ensure_dataset, slo_id)
        await test_list_burn_alerts(initial_alerts)
        initial_count = len(initial_alerts)

        # Create
        alert_id = await create_exhaustion_time_alert(
            client, ensure_dataset, slo_id, ensure_recipient
        )
        try:
            # Get
            alert = await get_burn_alert(client, ensure_dataset, alert_id)
            assert alert.id == alert_id
            assert alert.alert_type == BurnAlertType.EXHAUSTION_TIME
            assert alert.exhaustion_minutes == 120

            # Update
            updated = await update_burn_alert(client, ensure_dataset, alert_id, ensure_recipient)
            assert updated.id == alert_id
            assert updated.exhaustion_minutes == 60  # Updated from 120 to 60
            assert "Updated:" in updated.description

            # List (after create - verify it appears)
            alerts = await list_burn_alerts(client, ensure_dataset, slo_id)
            assert len(alerts) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            await delete_burn_alert(client, ensure_dataset, alert_id)

    @pytest.mark.asyncio
    async def test_exhaustion_time_alert(
        self,
        client: HoneycombClient,
        ensure_dataset: str,
        ensure_slo: tuple[str, str],
        ensure_recipient: str,
    ) -> None:
        """Test exhaustion time burn alert creation."""
        from docs.examples.burn_alerts.basic_burn_alert import (
            cleanup,
            create_exhaustion_time_alert,
            test_exhaustion_alert,
        )

        slo_id, _ = ensure_slo
        alert_id = await create_exhaustion_time_alert(
            client, ensure_dataset, slo_id, ensure_recipient
        )
        try:
            await test_exhaustion_alert(client, ensure_dataset, alert_id)
        finally:
            await cleanup(client, ensure_dataset, alert_id)

    @pytest.mark.asyncio
    async def test_budget_rate_alert(
        self,
        client: HoneycombClient,
        ensure_dataset: str,
        ensure_slo: tuple[str, str],
        ensure_recipient: str,
    ) -> None:
        """Test budget rate burn alert creation."""
        from docs.examples.burn_alerts.basic_burn_alert import (
            cleanup,
            create_budget_rate_alert,
            test_budget_rate_alert,
        )

        slo_id, _ = ensure_slo
        alert_id = await create_budget_rate_alert(client, ensure_dataset, slo_id, ensure_recipient)
        try:
            await test_budget_rate_alert(client, ensure_dataset, alert_id)
        finally:
            await cleanup(client, ensure_dataset, alert_id)

    @pytest.mark.asyncio
    async def test_list_burn_alerts(
        self, client: HoneycombClient, ensure_dataset: str, ensure_slo: tuple[str, str]
    ) -> None:
        """Test listing burn alerts."""
        from docs.examples.burn_alerts.basic_burn_alert import (
            list_burn_alerts,
            test_list_burn_alerts,
        )

        slo_id, _ = ensure_slo
        alerts = await list_burn_alerts(client, ensure_dataset, slo_id)
        await test_list_burn_alerts(alerts)


class TestServiceMapExamples:
    """Test service map examples from docs/examples/service_map/.

    Note: Service map requires trace data in your environment.
    If no trace data exists, the API returns a 404 error.
    These tests handle both cases: with trace data (full test) and without (skip).
    """

    @pytest.mark.asyncio
    async def test_create_request(self, client: HoneycombClient) -> None:
        """Test creating a service map dependency request."""
        from docs.examples.service_map.basic_service_map import (
            create_service_map_request,
            test_create_request,
        )

        from honeycomb import HoneycombNotFoundError

        try:
            request_id = await create_service_map_request(client)
            await test_create_request(request_id)
        except HoneycombNotFoundError as e:
            if "Service map data not found" in str(e):
                pytest.skip("No trace data in environment - service map unavailable")
            raise

    @pytest.mark.asyncio
    async def test_poll_result(self, client: HoneycombClient) -> None:
        """Test polling for service map result."""
        from docs.examples.service_map.basic_service_map import (
            create_service_map_request,
            poll_service_map_result,
            test_poll_result,
        )

        from honeycomb import HoneycombNotFoundError

        try:
            # Create request first
            request_id = await create_service_map_request(client)

            # Poll for result
            result = await poll_service_map_result(client, request_id)
            await test_poll_result(result)
        except HoneycombNotFoundError as e:
            if "Service map data not found" in str(e):
                pytest.skip("No trace data in environment - service map unavailable")
            raise

    @pytest.mark.asyncio
    async def test_get_service_map(self, client: HoneycombClient) -> None:
        """Test the convenience method that creates and polls in one call."""
        from docs.examples.service_map.basic_service_map import (
            get_service_map,
            test_get_service_map,
        )

        from honeycomb import HoneycombNotFoundError

        try:
            result = await get_service_map(client)
            await test_get_service_map(result)
        except HoneycombNotFoundError as e:
            if "Service map data not found" in str(e):
                pytest.skip("No trace data in environment - service map unavailable")
            raise


class TestEnvironmentExamples:
    """Test environment examples from docs/examples/environments/.

    Note: These tests require management key authentication.
    They will be skipped if management credentials are not available.
    """

    @pytest.mark.asyncio
    async def test_environment_lifecycle(
        self, management_client: HoneycombClient, team_slug: str
    ) -> None:
        """Test full environment CRUD lifecycle: list -> create -> get -> update -> delete."""
        from docs.examples.environments.basic_environment import (
            create_environment,
            get_environment,
            list_environments,
            test_create_environment,
            test_get_environment,
            test_list_environments,
            test_update_environment,
            update_environment,
        )

        # List (before create)
        initial_envs = await list_environments(management_client, team_slug)
        await test_list_environments(initial_envs)
        initial_count = len(initial_envs)

        # Create
        env_id = await create_environment(management_client, team_slug)
        try:
            await test_create_environment(env_id)

            # Get
            env = await get_environment(management_client, team_slug, env_id)
            await test_get_environment(env, env_id)

            # Update
            updated = await update_environment(management_client, team_slug, env_id)
            await test_update_environment(updated, env_id)

            # List (after create - verify it appears)
            envs = await list_environments(management_client, team_slug)
            assert len(envs) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            from docs.examples.environments.basic_environment import cleanup

            await cleanup(management_client, team_slug, env_id)


class TestApiKeyExamples:
    """Test API key examples from docs/examples/api_keys/.

    Note: These tests require management key authentication.
    They will be skipped if management credentials are not available.
    """

    @pytest.mark.asyncio
    async def test_api_key_lifecycle(
        self, management_client: HoneycombClient, team_slug: str, session_info: dict
    ) -> None:
        """Test full API key CRUD lifecycle: list -> create -> get -> update -> delete."""
        from docs.examples.api_keys.basic_api_key import (
            create_api_key,
            delete_api_key,
            get_api_key,
            list_api_keys,
            test_create_api_key,
            test_get_api_key,
            test_list_api_keys,
            test_update_api_key,
            update_api_key,
        )

        # List (before create)
        initial_keys = await list_api_keys(management_client, team_slug)
        await test_list_api_keys(initial_keys)
        initial_count = len(initial_keys)

        # Use the test environment from session
        environment_id = session_info["environment_id"]

        # Create
        key_id, secret = await create_api_key(management_client, team_slug, environment_id)
        try:
            await test_create_api_key(key_id, secret)

            # Get
            key = await get_api_key(management_client, team_slug, key_id)
            await test_get_api_key(key, key_id)

            # Update
            updated = await update_api_key(management_client, team_slug, key_id, environment_id)
            await test_update_api_key(updated, key_id)

            # List (after create - verify it appears)
            keys = await list_api_keys(management_client, team_slug)
            assert len(keys) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            await delete_api_key(management_client, team_slug, key_id)

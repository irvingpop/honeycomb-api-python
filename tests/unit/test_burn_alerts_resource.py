"""Tests for BurnAlertsResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import (
    BudgetRateBurnAlertFactory,
    CreateBudgetRateBurnAlertFactory,
    CreateExhaustionTimeBurnAlertFactory,
    ExhaustionTimeBurnAlertFactory,
    mock_response,
)

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_burn_alerts_async():
    """Test listing burn alerts for an SLO (async)."""
    # Note: Can't use mock_list_response here because we need mixed alert types
    mock_data = [
        mock_response(ExhaustionTimeBurnAlertFactory, id="alert-1"),
        mock_response(BudgetRateBurnAlertFactory, id="alert-2"),
    ]
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset?slo_id=slo-123").mock(
        return_value=Response(200, json=mock_data)
    )

    async with HoneycombClient(api_key="test-key") as client:
        alerts = await client.burn_alerts.list_async(dataset="test-dataset", slo_id="slo-123")
        assert len(alerts) == 2
        # Property accessors work for discriminated union
        assert alerts[0].id == "alert-1"
        assert alerts[1].id == "alert-2"


@pytest.mark.asyncio
@respx.mock
async def test_list_burn_alerts_empty_async():
    """Test listing burn alerts returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset?slo_id=slo-123").mock(
        return_value=Response(200, json=[])
    )

    async with HoneycombClient(api_key="test-key") as client:
        alerts = await client.burn_alerts.list_async(dataset="test-dataset", slo_id="slo-123")
        assert len(alerts) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_exhaustion_time_burn_alert_async():
    """Test getting exhaustion_time burn alert (async)."""
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-123").mock(
        return_value=Response(
            200, json=mock_response(ExhaustionTimeBurnAlertFactory, id="alert-123")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        alert = await client.burn_alerts.get_async(
            dataset="test-dataset", burn_alert_id="alert-123"
        )
        assert alert.id == "alert-123"
        assert alert.alert_type == "exhaustion_time"
        assert alert.exhaustion_minutes is not None


@pytest.mark.asyncio
@respx.mock
async def test_get_budget_rate_burn_alert_async():
    """Test getting budget_rate burn alert (async)."""
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-456").mock(
        return_value=Response(200, json=mock_response(BudgetRateBurnAlertFactory, id="alert-456"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        alert = await client.burn_alerts.get_async(
            dataset="test-dataset", burn_alert_id="alert-456"
        )
        assert alert.id == "alert-456"
        assert alert.alert_type == "budget_rate"
        assert alert.budget_rate_window_minutes is not None
        assert alert.budget_rate_decrease_threshold_per_million is not None


@pytest.mark.asyncio
@respx.mock
async def test_create_exhaustion_time_burn_alert_async():
    """Test creating exhaustion_time burn alert (async)."""
    respx.post("https://api.honeycomb.io/1/burn_alerts/test-dataset").mock(
        return_value=Response(
            201, json=mock_response(ExhaustionTimeBurnAlertFactory, id="new-alert")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = CreateExhaustionTimeBurnAlertFactory.build(exhaustion_minutes=120)
        alert = await client.burn_alerts.create_async(dataset="test-dataset", burn_alert=request)
        assert alert.id == "new-alert"
        assert alert.alert_type == "exhaustion_time"


@pytest.mark.asyncio
@respx.mock
async def test_create_budget_rate_burn_alert_async():
    """Test creating budget_rate burn alert (async)."""
    respx.post("https://api.honeycomb.io/1/burn_alerts/test-dataset").mock(
        return_value=Response(201, json=mock_response(BudgetRateBurnAlertFactory, id="new-alert"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = CreateBudgetRateBurnAlertFactory.build(
            budget_rate_window_minutes=60, budget_rate_decrease_threshold_per_million=50000
        )
        alert = await client.burn_alerts.create_async(dataset="test-dataset", burn_alert=request)
        assert alert.id == "new-alert"
        assert alert.alert_type == "budget_rate"


@pytest.mark.asyncio
@respx.mock
async def test_update_burn_alert_async():
    """Test updating a burn alert (async)."""
    respx.put("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-123").mock(
        return_value=Response(
            200,
            json=mock_response(
                ExhaustionTimeBurnAlertFactory, id="alert-123", description="Updated description"
            ),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = CreateExhaustionTimeBurnAlertFactory.build(
            exhaustion_minutes=240, description="Updated description"
        )
        alert = await client.burn_alerts.update_async(
            dataset="test-dataset", burn_alert_id="alert-123", burn_alert=request
        )
        assert alert.id == "alert-123"
        assert alert.description == "Updated description"


@pytest.mark.asyncio
@respx.mock
async def test_delete_burn_alert_async():
    """Test deleting a burn alert (async)."""
    respx.delete("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.burn_alerts.delete_async(dataset="test-dataset", burn_alert_id="alert-123")


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_burn_alerts_sync():
    """Test listing burn alerts for an SLO (sync)."""
    # Note: Can't use mock_list_response here because we need mixed alert types
    mock_data = [
        mock_response(ExhaustionTimeBurnAlertFactory, id="alert-1"),
        mock_response(BudgetRateBurnAlertFactory, id="alert-2"),
    ]
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset?slo_id=slo-123").mock(
        return_value=Response(200, json=mock_data)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        alerts = client.burn_alerts.list(dataset="test-dataset", slo_id="slo-123")
        assert len(alerts) == 2
        assert alerts[0].id == "alert-1"
        assert alerts[1].id == "alert-2"


@respx.mock
def test_list_burn_alerts_empty_sync():
    """Test listing burn alerts returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset?slo_id=slo-123").mock(
        return_value=Response(200, json=[])
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        alerts = client.burn_alerts.list(dataset="test-dataset", slo_id="slo-123")
        assert len(alerts) == 0


@respx.mock
def test_get_exhaustion_time_burn_alert_sync():
    """Test getting exhaustion_time burn alert (sync)."""
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-123").mock(
        return_value=Response(
            200, json=mock_response(ExhaustionTimeBurnAlertFactory, id="alert-123")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        alert = client.burn_alerts.get(dataset="test-dataset", burn_alert_id="alert-123")
        assert alert.id == "alert-123"
        assert alert.alert_type == "exhaustion_time"


@respx.mock
def test_get_budget_rate_burn_alert_sync():
    """Test getting budget_rate burn alert (sync)."""
    respx.get("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-456").mock(
        return_value=Response(200, json=mock_response(BudgetRateBurnAlertFactory, id="alert-456"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        alert = client.burn_alerts.get(dataset="test-dataset", burn_alert_id="alert-456")
        assert alert.id == "alert-456"
        assert alert.alert_type == "budget_rate"


@respx.mock
def test_create_exhaustion_time_burn_alert_sync():
    """Test creating exhaustion_time burn alert (sync)."""
    respx.post("https://api.honeycomb.io/1/burn_alerts/test-dataset").mock(
        return_value=Response(
            201, json=mock_response(ExhaustionTimeBurnAlertFactory, id="new-alert")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = CreateExhaustionTimeBurnAlertFactory.build(exhaustion_minutes=120)
        alert = client.burn_alerts.create(dataset="test-dataset", burn_alert=request)
        assert alert.id == "new-alert"
        assert alert.alert_type == "exhaustion_time"


@respx.mock
def test_create_budget_rate_burn_alert_sync():
    """Test creating budget_rate burn alert (sync)."""
    respx.post("https://api.honeycomb.io/1/burn_alerts/test-dataset").mock(
        return_value=Response(201, json=mock_response(BudgetRateBurnAlertFactory, id="new-alert"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = CreateBudgetRateBurnAlertFactory.build(
            budget_rate_window_minutes=60, budget_rate_decrease_threshold_per_million=50000
        )
        alert = client.burn_alerts.create(dataset="test-dataset", burn_alert=request)
        assert alert.id == "new-alert"
        assert alert.alert_type == "budget_rate"


@respx.mock
def test_update_burn_alert_sync():
    """Test updating a burn alert (sync)."""
    respx.put("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-123").mock(
        return_value=Response(
            200,
            json=mock_response(
                ExhaustionTimeBurnAlertFactory, id="alert-123", description="Updated description"
            ),
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = CreateExhaustionTimeBurnAlertFactory.build(
            exhaustion_minutes=240, description="Updated description"
        )
        alert = client.burn_alerts.update(
            dataset="test-dataset", burn_alert_id="alert-123", burn_alert=request
        )
        assert alert.id == "alert-123"
        assert alert.description == "Updated description"


@respx.mock
def test_delete_burn_alert_sync():
    """Test deleting a burn alert (sync)."""
    respx.delete("https://api.honeycomb.io/1/burn_alerts/test-dataset/alert-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.burn_alerts.delete(dataset="test-dataset", burn_alert_id="alert-123")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.burn_alerts.list(dataset="test-dataset", slo_id="slo-123")

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.burn_alerts.get(dataset="test-dataset", burn_alert_id="alert-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = CreateExhaustionTimeBurnAlertFactory.build()
        client.burn_alerts.create(dataset="test-dataset", burn_alert=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = CreateExhaustionTimeBurnAlertFactory.build()
        client.burn_alerts.update(
            dataset="test-dataset", burn_alert_id="alert-123", burn_alert=request
        )

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.burn_alerts.delete(dataset="test-dataset", burn_alert_id="alert-123")

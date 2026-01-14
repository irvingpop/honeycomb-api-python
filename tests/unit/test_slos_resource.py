"""Tests for SLOs resource (create_from_bundle orchestration)."""

import pytest
import respx
from httpx import Response

from honeycomb import BurnAlertBuilder, BurnAlertType, HoneycombClient, SLOBuilder
from tests.factories import (
    BudgetRateBurnAlertFactory,
    SLOCreateFactory,
    SLOFactory,
    mock_list_response,
    mock_response,
)


@pytest.mark.asyncio
class TestSLOsResourceBundleAsync:
    """Tests for SLO bundle creation orchestration (async)."""

    @respx.mock
    async def test_single_dataset_bundle_creates_one_slo(self, respx_mock):
        """Test that single-dataset bundle creates one SLO in specified dataset."""
        client = HoneycombClient(api_key="test-key")

        # Mock POST to create SLO
        respx_mock.post("https://api.honeycomb.io/1/slos/api-logs").mock(
            return_value=Response(
                200,
                json={
                    "id": "slo-1",
                    "name": "API Availability",
                    "sli": {"alias": "success_rate"},
                    "target_per_million": 999000,
                    "time_period_days": 30,
                },
            )
        )

        async with client:
            bundle = (
                SLOBuilder("API Availability")
                .dataset("api-logs")
                .target_percentage(99.9)
                .sli(alias="success_rate")
                .build()
            )

            slos = await client.slos.create_from_bundle_async(bundle)

            assert len(slos) == 1
            assert "api-logs" in slos
            assert slos["api-logs"].id == "slo-1"

    @respx.mock
    async def test_multi_dataset_bundle_creates_one_slo_via_all(self, respx_mock):
        """Test that multi-dataset bundle creates ONE SLO via __all__ endpoint."""
        client = HoneycombClient(api_key="test-key")

        # Mock environment-wide derived column creation
        respx_mock.post("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(
                200,
                json={
                    "id": "dc-1",
                    "alias": "cross_service_success",
                    "expression": "IF(LT($status_code, 400), 1, 0)",
                    "description": "",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            )
        )

        # Mock POST to __all__ endpoint (should be called ONCE, not per dataset)
        all_endpoint_route = respx_mock.post("https://api.honeycomb.io/1/slos/__all__").mock(
            return_value=Response(
                200,
                json={
                    "id": "slo-multi",
                    "name": "Cross-Service Availability",
                    "sli": {"alias": "cross_service_success"},
                    "target_per_million": 999000,
                    "time_period_days": 30,
                    "dataset_slugs": ["api-logs", "web-logs", "worker-logs"],
                },
            )
        )

        async with client:
            bundle = (
                SLOBuilder("Cross-Service Availability")
                .datasets(["api-logs", "web-logs", "worker-logs"])
                .target_percentage(99.9)
                .sli(
                    alias="cross_service_success",
                    expression="IF(LT($status_code, 400), 1, 0)",
                )
                .build()
            )

            slos = await client.slos.create_from_bundle_async(bundle)

            # Verify: __all__ endpoint called ONCE (not 3 times)
            assert all_endpoint_route.call_count == 1

            # Verify: returns dict with all 3 datasets pointing to SAME SLO object
            assert len(slos) == 3
            assert "api-logs" in slos
            assert "web-logs" in slos
            assert "worker-logs" in slos

            # All point to the same SLO object
            assert slos["api-logs"] is slos["web-logs"]
            assert slos["web-logs"] is slos["worker-logs"]
            assert slos["api-logs"].id == "slo-multi"
            assert slos["api-logs"].dataset_slugs == ["api-logs", "web-logs", "worker-logs"]

    @respx.mock
    async def test_multi_dataset_with_burn_alerts_creates_once(self, respx_mock):
        """Test that multi-dataset SLO with burn alerts creates burn alerts only in first dataset."""
        client = HoneycombClient(api_key="test-key")

        # Mock SLO creation via __all__
        respx_mock.post("https://api.honeycomb.io/1/slos/__all__").mock(
            return_value=Response(
                200,
                json={
                    "id": "slo-multi",
                    "name": "Cross-Service SLO",
                    "sli": {"alias": "success"},
                    "target_per_million": 999000,
                    "time_period_days": 30,
                    "dataset_slugs": ["dataset-1", "dataset-2"],
                },
            )
        )

        # Mock recipients list (needed for inline recipient processing)
        respx_mock.get("https://api.honeycomb.io/1/recipients").mock(
            return_value=Response(200, json=[])
        )

        # Mock burn alert creation (should be in first dataset only)
        burn_alert_route = respx_mock.post("https://api.honeycomb.io/1/burn_alerts/dataset-1").mock(
            return_value=Response(
                200,
                json={
                    "id": "alert-1",
                    "alert_type": "exhaustion_time",
                    "slo_id": "slo-multi",
                    "exhaustion_minutes": 60,
                },
            )
        )

        async with client:
            bundle = (
                SLOBuilder("Cross-Service SLO")
                .datasets(["dataset-1", "dataset-2"])
                .target_percentage(99.9)
                .sli(alias="success")
                .exhaustion_alert(
                    BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME).exhaustion_minutes(60)
                )
                .build()
            )

            slos = await client.slos.create_from_bundle_async(bundle)

            # Verify: burn alert created only once in first dataset
            assert burn_alert_route.call_count == 1

            # Verify: SLO created correctly
            assert len(slos) == 2
            assert slos["dataset-1"] is slos["dataset-2"]
            assert slos["dataset-1"].id == "slo-multi"

    @respx.mock
    async def test_bundle_with_tags(self, respx_mock):
        """Test that tags are included in SLO creation."""
        client = HoneycombClient(api_key="test-key")

        # Capture the request body
        captured_request = None

        def capture_request(request):
            nonlocal captured_request
            captured_request = request
            return Response(
                200,
                json={
                    "id": "slo-1",
                    "name": "API SLO",
                    "sli": {"alias": "success_rate"},
                    "target_per_million": 999000,
                    "time_period_days": 30,
                    "tags": [
                        {"key": "team", "value": "platform"},
                        {"key": "service", "value": "api"},
                    ],
                },
            )

        respx_mock.post("https://api.honeycomb.io/1/slos/api-logs").mock(
            side_effect=capture_request
        )

        async with client:
            bundle = (
                SLOBuilder("API SLO")
                .dataset("api-logs")
                .target_percentage(99.9)
                .sli(alias="success_rate")
                .tag("team", "platform")
                .tag("service", "api")
                .build()
            )

            slos = await client.slos.create_from_bundle_async(bundle)

            # Verify tags were sent in request
            import json

            request_body = json.loads(captured_request.content)
            assert "tags" in request_body
            assert request_body["tags"] == [
                {"key": "team", "value": "platform"},
                {"key": "service", "value": "api"},
            ]

            assert slos["api-logs"].id == "slo-1"


# =============================================================================
# Core SLO CRUD Tests (added for Phase 4)
# =============================================================================


@pytest.mark.asyncio
@respx.mock
async def test_list_slos_async():
    """Test listing SLOs (async)."""
    respx.get("https://api.honeycomb.io/1/slos/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(SLOFactory, count=3))
    )

    async with HoneycombClient(api_key="test-key") as client:
        slos = await client.slos.list_async(dataset="test-dataset")
        assert len(slos) == 3


@pytest.mark.asyncio
@respx.mock
async def test_list_slos_empty_async():
    """Test listing SLOs returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/slos/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    async with HoneycombClient(api_key="test-key") as client:
        slos = await client.slos.list_async(dataset="test-dataset")
        assert len(slos) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_slo_async():
    """Test getting a specific SLO (async)."""
    respx.get("https://api.honeycomb.io/1/slos/test-dataset/slo-123").mock(
        return_value=Response(
            200, json=mock_response(SLOFactory, id="slo-123", name="API Availability")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        slo = await client.slos.get_async(dataset="test-dataset", slo_id="slo-123")
        assert slo.id == "slo-123"
        assert slo.name == "API Availability"


@pytest.mark.asyncio
@respx.mock
async def test_create_slo_async():
    """Test creating an SLO (async)."""
    respx.post("https://api.honeycomb.io/1/slos/test-dataset").mock(
        return_value=Response(201, json=mock_response(SLOFactory, id="new-slo", name="New SLO"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = SLOCreateFactory.build(name="New SLO")
        slo = await client.slos.create_async(dataset="test-dataset", slo=request)
        assert slo.id == "new-slo"
        assert slo.name == "New SLO"


@pytest.mark.asyncio
@respx.mock
async def test_update_slo_async():
    """Test updating an SLO (async)."""
    respx.put("https://api.honeycomb.io/1/slos/test-dataset/slo-123").mock(
        return_value=Response(200, json=mock_response(SLOFactory, id="slo-123", name="Updated SLO"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = SLOCreateFactory.build(name="Updated SLO")
        slo = await client.slos.update_async(dataset="test-dataset", slo_id="slo-123", slo=request)
        assert slo.id == "slo-123"
        assert slo.name == "Updated SLO"


@pytest.mark.asyncio
@respx.mock
async def test_delete_slo_async():
    """Test deleting an SLO (async)."""
    respx.delete("https://api.honeycomb.io/1/slos/test-dataset/slo-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.slos.delete_async(dataset="test-dataset", slo_id="slo-123")


# Sync versions


@respx.mock
def test_list_slos_sync():
    """Test listing SLOs (sync)."""
    respx.get("https://api.honeycomb.io/1/slos/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(SLOFactory, count=2))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        slos = client.slos.list(dataset="test-dataset")
        assert len(slos) == 2


@respx.mock
def test_list_slos_empty_sync():
    """Test listing SLOs returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/slos/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        slos = client.slos.list(dataset="test-dataset")
        assert len(slos) == 0


@respx.mock
def test_get_slo_sync():
    """Test getting a specific SLO (sync)."""
    respx.get("https://api.honeycomb.io/1/slos/test-dataset/slo-123").mock(
        return_value=Response(200, json=mock_response(SLOFactory, id="slo-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        slo = client.slos.get(dataset="test-dataset", slo_id="slo-123")
        assert slo.id == "slo-123"


@respx.mock
def test_create_slo_sync():
    """Test creating an SLO (sync)."""
    respx.post("https://api.honeycomb.io/1/slos/test-dataset").mock(
        return_value=Response(201, json=mock_response(SLOFactory, id="new-slo"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = SLOCreateFactory.build(name="New SLO")
        slo = client.slos.create(dataset="test-dataset", slo=request)
        assert slo.id == "new-slo"


@respx.mock
def test_update_slo_sync():
    """Test updating an SLO (sync)."""
    respx.put("https://api.honeycomb.io/1/slos/test-dataset/slo-123").mock(
        return_value=Response(200, json=mock_response(SLOFactory, id="slo-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = SLOCreateFactory.build(name="Updated")
        slo = client.slos.update(dataset="test-dataset", slo_id="slo-123", slo=request)
        assert slo.id == "slo-123"


@respx.mock
def test_delete_slo_sync():
    """Test deleting an SLO (sync)."""
    respx.delete("https://api.honeycomb.io/1/slos/test-dataset/slo-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.slos.delete(dataset="test-dataset", slo_id="slo-123")


def test_sync_slo_methods_require_sync_mode():
    """Test that sync SLO methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.slos.list(dataset="test-dataset")

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.slos.get(dataset="test-dataset", slo_id="slo-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = SLOCreateFactory.build()
        client.slos.create(dataset="test-dataset", slo=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = SLOCreateFactory.build()
        client.slos.update(dataset="test-dataset", slo_id="slo-123", slo=request)

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.slos.delete(dataset="test-dataset", slo_id="slo-123")


# -------------------------------------------------------------------------
# Bundle tests (sync wrapper)
# -------------------------------------------------------------------------


@respx.mock
def test_create_from_bundle_sync():
    """Test creating SLO from bundle (sync)."""
    # Mock SLO creation
    respx.post("https://api.honeycomb.io/1/slos/__all__").mock(
        return_value=Response(201, json=mock_response(SLOFactory, id="slo-sync"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        bundle = (
            SLOBuilder("API Availability")
            .datasets(["api-logs", "web-logs"])
            .sli(alias="success_rate")
            .target_percentage(99.9)
            .time_period_days(30)
            .build()
        )
        slos = client.slos.create_from_bundle(bundle)
        # Returns dict[dataset, SLO] but for multi-dataset creates one SLO via __all__
        assert len(slos) > 0


@pytest.mark.asyncio
@respx.mock
async def test_bundle_with_budget_rate_burn_alert_async():
    """Test bundle with budget_rate burn alert to cover that branch."""
    # Mock recipients list (needed for inline recipient processing)
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    # Mock SLO creation
    respx.post("https://api.honeycomb.io/1/slos/api-logs").mock(
        return_value=Response(201, json=mock_response(SLOFactory, id="slo-budget"))
    )

    # Mock burn alert creation
    respx.post("https://api.honeycomb.io/1/burn_alerts/api-logs").mock(
        return_value=Response(
            201,
            json=mock_response(
                BudgetRateBurnAlertFactory,
                id="alert-budget",
                budget_rate_window_minutes=60,
                budget_rate_decrease_threshold_per_million=50000,
            ),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        bundle = (
            SLOBuilder("API Availability")
            .dataset("api-logs")
            .sli(alias="success_rate")
            .target_percentage(99.9)
            .time_period_days(30)
            .budget_rate_alert(
                BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
                .window_minutes(60)
                .threshold_percent(5.0)
                .description("Budget burn alert")
            )
            .build()
        )

        slos = await client.slos.create_from_bundle_async(bundle)
        assert "api-logs" in slos

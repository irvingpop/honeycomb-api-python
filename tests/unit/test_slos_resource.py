"""Tests for SLOs resource (create_from_bundle orchestration)."""

import pytest
import respx
from httpx import Response

from honeycomb import BurnAlertBuilder, BurnAlertType, HoneycombClient, SLOBuilder


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

"""Unit tests for Claude tool executor."""

import json

import pytest
from respx import MockRouter

from honeycomb import HoneycombClient
from honeycomb.tools.executor import execute_tool


@pytest.fixture
async def client() -> HoneycombClient:
    """Create test client."""
    async with HoneycombClient(api_key="test-key") as client:
        yield client


class TestExecuteTriggerTools:
    """Test execution of trigger tools."""

    async def test_execute_list_triggers(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute list_triggers tool."""
        respx_mock.get("https://api.honeycomb.io/1/triggers/test-dataset").respond(
            json=[
                {
                    "id": "t1",
                    "name": "Trigger 1",
                    "dataset_slug": "test-dataset",
                    "threshold": {"op": ">", "value": 100},
                    "frequency": 900,
                },
                {
                    "id": "t2",
                    "name": "Trigger 2",
                    "dataset_slug": "test-dataset",
                    "threshold": {"op": ">=", "value": 200},
                    "frequency": 900,
                },
            ]
        )

        result_json = await execute_tool(
            client, "honeycomb_list_triggers", {"dataset": "test-dataset"}
        )

        result = json.loads(result_json)
        assert len(result) == 2
        assert result[0]["id"] == "t1"

    async def test_execute_get_trigger(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute get_trigger tool."""
        respx_mock.get("https://api.honeycomb.io/1/triggers/test-dataset/t1").respond(
            json={
                "id": "t1",
                "name": "Trigger 1",
                "dataset_slug": "test-dataset",
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
            }
        )

        result_json = await execute_tool(
            client, "honeycomb_get_trigger", {"dataset": "test-dataset", "trigger_id": "t1"}
        )

        result = json.loads(result_json)
        assert result["id"] == "t1"
        assert result["name"] == "Trigger 1"

    async def test_execute_create_trigger(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute create_trigger tool with inline query."""
        respx_mock.post("https://api.honeycomb.io/1/triggers/test-dataset").respond(
            json={
                "id": "new-trigger",
                "name": "High Error Rate",
                "dataset_slug": "test-dataset",
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
            }
        )

        tool_input = {
            "dataset": "test-dataset",
            "name": "High Error Rate",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status", "op": ">=", "value": 500}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        result_json = await execute_tool(client, "honeycomb_create_trigger", tool_input)

        result = json.loads(result_json)
        assert result["id"] == "new-trigger"
        assert result["name"] == "High Error Rate"

    async def test_execute_delete_trigger(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute delete_trigger tool."""
        respx_mock.delete("https://api.honeycomb.io/1/triggers/test-dataset/t1").respond(
            status_code=204
        )

        result_json = await execute_tool(
            client, "honeycomb_delete_trigger", {"dataset": "test-dataset", "trigger_id": "t1"}
        )

        result = json.loads(result_json)
        assert result["success"] is True


class TestExecuteSLOTools:
    """Test execution of SLO tools."""

    async def test_execute_list_slos(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute list_slos tool."""
        respx_mock.get("https://api.honeycomb.io/1/slos/test-dataset").respond(
            json=[
                {
                    "id": "slo1",
                    "name": "API Availability",
                    "sli": {"alias": "success_rate"},
                    "target_per_million": 999000,
                    "time_period_days": 30,
                },
            ]
        )

        result_json = await execute_tool(client, "honeycomb_list_slos", {"dataset": "test-dataset"})

        result = json.loads(result_json)
        assert len(result) == 1
        assert result[0]["id"] == "slo1"

    async def test_execute_create_slo_simple(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute create_slo tool without bundle orchestration."""
        respx_mock.post("https://api.honeycomb.io/1/slos/test-dataset").respond(
            json={
                "id": "new-slo",
                "name": "API Availability",
                "target_per_million": 999000,
                "time_period_days": 30,
                "sli": {"alias": "success_rate"},
            }
        )

        tool_input = {
            "dataset": "test-dataset",
            "name": "API Availability",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999000,
            "time_period_days": 30,
        }

        result_json = await execute_tool(client, "honeycomb_create_slo", tool_input)

        result = json.loads(result_json)
        assert result["id"] == "new-slo"


class TestExecuteBurnAlertTools:
    """Test execution of burn alert tools."""

    async def test_execute_list_burn_alerts(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute list_burn_alerts tool."""
        respx_mock.get(
            "https://api.honeycomb.io/1/burn_alerts/test-dataset?slo_id=slo-123"
        ).respond(
            json=[
                {
                    "id": "ba1",
                    "alert_type": "exhaustion_time",
                    "slo": {"id": "slo-123"},
                    "exhaustion_minutes": 60,
                },
            ]
        )

        result_json = await execute_tool(
            client,
            "honeycomb_list_burn_alerts",
            {"dataset": "test-dataset", "slo_id": "slo-123"},
        )

        result = json.loads(result_json)
        assert len(result) == 1
        assert result[0]["id"] == "ba1"

    async def test_execute_create_burn_alert(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute create_burn_alert tool."""
        respx_mock.post("https://api.honeycomb.io/1/burn_alerts/test-dataset").respond(
            json={
                "id": "new-ba",
                "alert_type": "exhaustion_time",
                "slo": {"id": "slo-123"},
                "exhaustion_minutes": 60,
            }
        )

        tool_input = {
            "dataset": "test-dataset",
            "alert_type": "exhaustion_time",
            "slo_id": "slo-123",
            "exhaustion_minutes": 60,
            "recipients": [{"id": "recip-123"}],
        }

        result_json = await execute_tool(client, "honeycomb_create_burn_alert", tool_input)

        result = json.loads(result_json)
        assert result["id"] == "new-ba"


class TestExecutorErrorHandling:
    """Test executor error handling."""

    async def test_unknown_tool_raises(self, client: HoneycombClient):
        """Unknown tool name should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await execute_tool(client, "honeycomb_unknown_tool", {})

    async def test_missing_required_parameter(self, client: HoneycombClient):
        """Missing required parameter should raise appropriate error."""
        with pytest.raises(KeyError):
            await execute_tool(client, "honeycomb_list_triggers", {})  # Missing dataset

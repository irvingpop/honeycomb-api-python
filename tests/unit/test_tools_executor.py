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


@pytest.fixture
async def management_client() -> HoneycombClient:
    """Create test client with management credentials."""
    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        yield client


class TestExecuteAuthTools:
    """Test execution of auth tools."""

    async def test_execute_get_auth_v1(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute get_auth tool with v1 endpoint."""
        respx_mock.get("https://api.honeycomb.io/1/auth").respond(
            json={
                "id": "key123",
                "type": "configuration",
                "team": {"name": "Test Team", "slug": "test-team"},
                "environment": {"name": "Production", "slug": "production"},
                "api_key_access": {"events": True, "markers": True},
            }
        )

        result_json = await execute_tool(client, "honeycomb_get_auth", {})

        result = json.loads(result_json)
        assert result["id"] == "key123"
        assert result["team_name"] == "Test Team"
        assert result["environment_name"] == "Production"

    async def test_execute_get_auth_v2(
        self, management_client: HoneycombClient, respx_mock: MockRouter
    ):
        """Can execute get_auth tool with v2 endpoint."""
        respx_mock.get("https://api.honeycomb.io/2/auth").respond(
            json={
                "data": {
                    "id": "mgmt123",
                    "type": "api-keys",
                    "attributes": {
                        "name": "My Management Key",
                        "key_type": "management",
                        "disabled": False,
                        "scopes": ["environments:read", "api-keys:write"],
                        "timestamps": {},
                    },
                    "relationships": {"team": {"data": {"type": "teams", "id": "team123"}}},
                },
                "included": [
                    {
                        "id": "team123",
                        "type": "teams",
                        "attributes": {"name": "My Team", "slug": "my-team"},
                    }
                ],
            }
        )

        result_json = await execute_tool(management_client, "honeycomb_get_auth", {})

        result = json.loads(result_json)
        assert result["id"] == "mgmt123"
        assert result["name"] == "My Management Key"
        assert result["team_name"] == "My Team"
        assert "api-keys:write" in result["scopes"]

    async def test_execute_get_auth_explicit_v2(
        self, management_client: HoneycombClient, respx_mock: MockRouter
    ):
        """Can execute get_auth tool with explicit v2 flag."""
        respx_mock.get("https://api.honeycomb.io/2/auth").respond(
            json={
                "data": {
                    "id": "mgmt456",
                    "type": "api-keys",
                    "attributes": {
                        "name": "Another Key",
                        "key_type": "management",
                        "disabled": False,
                        "scopes": ["*:*"],
                        "timestamps": {},
                    },
                    "relationships": {"team": {"data": {"type": "teams", "id": "team789"}}},
                },
                "included": [
                    {
                        "id": "team789",
                        "type": "teams",
                        "attributes": {"name": "Team 789", "slug": "team-789"},
                    }
                ],
            }
        )

        result_json = await execute_tool(management_client, "honeycomb_get_auth", {"use_v2": True})

        result = json.loads(result_json)
        assert result["id"] == "mgmt456"


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
        # Mock recipients list (for idempotent recipient handling)
        respx_mock.get("https://api.honeycomb.io/1/recipients").respond(json=[])

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

    async def test_execute_create_trigger_with_inline_recipients(
        self, client: HoneycombClient, respx_mock: MockRouter
    ):
        """Can execute create_trigger with inline recipient creation (idempotent)."""
        # Mock recipients list (returns existing email recipient)
        respx_mock.get("https://api.honeycomb.io/1/recipients").respond(
            json=[
                {
                    "id": "existing-email",
                    "type": "email",
                    "details": {"email_address": "ops@example.com"},
                }
            ]
        )

        # Mock webhook recipient creation (new)
        respx_mock.post("https://api.honeycomb.io/1/recipients").respond(
            json={
                "id": "new-webhook",
                "type": "webhook",
                "details": {
                    "webhook_url": "https://example.com/webhook",
                    "webhook_name": "Webhook",
                },
            }
        )

        # Mock trigger creation
        respx_mock.post("https://api.honeycomb.io/1/triggers/test-dataset").respond(
            json={
                "id": "new-trigger",
                "name": "Test",
                "dataset_slug": "test-dataset",
                "threshold": {"op": ">", "value": 10},
                "frequency": 900,
                "recipients": [
                    {"id": "existing-email", "type": "email"},
                    {"id": "new-webhook", "type": "webhook"},
                ],
            }
        )

        tool_input = {
            "dataset": "test-dataset",
            "name": "Test",
            "query": {"time_range": 900, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 10},
            "frequency": 900,
            "recipients": [
                {"type": "email", "target": "ops@example.com"},  # Existing - should reuse
                {"type": "webhook", "target": "https://example.com/webhook"},  # New - should create
            ],
        }

        result_json = await execute_tool(client, "honeycomb_create_trigger", tool_input)
        result = json.loads(result_json)

        assert result["id"] == "new-trigger"
        # Verify both recipients are in result
        assert len(result["recipients"]) == 2

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
        # Mock recipients list (needed for inline recipient processing)
        respx_mock.get("https://api.honeycomb.io/1/recipients").respond(json=[])

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


class TestExecuteEventTools:
    """Test execution of event ingestion tools."""

    async def test_execute_send_event(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute send_event tool."""
        respx_mock.post("https://api.honeycomb.io/1/events/test-dataset").respond(status_code=200)

        tool_input = {
            "dataset": "test-dataset",
            "data": {"status_code": 200, "duration_ms": 123.4},
        }

        result_json = await execute_tool(client, "honeycomb_send_event", tool_input)
        result = json.loads(result_json)
        assert result["success"] is True

    async def test_execute_send_batch_events(self, client: HoneycombClient, respx_mock: MockRouter):
        """Can execute send_batch_events with time field (ISO8601)."""
        respx_mock.post("https://api.honeycomb.io/1/batch/test-dataset").respond(
            json=[
                {"status": 202, "error": None},
                {"status": 202, "error": None},
            ]
        )

        tool_input = {
            "dataset": "test-dataset",
            "events": [
                {
                    "data": {"status_code": 200, "duration_ms": 123.4},
                    "time": "2024-01-15T10:30:00Z",  # Should accept ISO8601 string
                },
                {
                    "data": {"status_code": 500},
                    # No time - should use server time
                },
            ],
        }

        result_json = await execute_tool(client, "honeycomb_send_batch_events", tool_input)
        results = json.loads(result_json)
        assert len(results) == 2
        assert all(r["status"] == 202 for r in results)


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

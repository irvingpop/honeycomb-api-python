#!/usr/bin/env python3
"""Capture serialization snapshots of all models before DMCG migration.

This script creates comprehensive examples of all Create models and saves
their serialized output to JSON files. After migration, re-run this script
and diff the outputs to ensure no breaking changes.

Usage:
    poetry run python scripts/capture_serialization_snapshots.py

    # After migration, compare:
    diff -r .claude/docs/serialization-snapshots/pre-migration/ \
            .claude/docs/serialization-snapshots/post-migration/
"""

import json
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from honeycomb.models.boards import BoardCreate
from honeycomb.models.columns import ColumnCreate, ColumnType
from honeycomb.models.datasets import DatasetCreate
from honeycomb.models.markers import MarkerCreate, MarkerSettingCreate
from honeycomb.models.query_builder import (
    CalcOp,
    Calculation,
    Filter,
    FilterCombination,
    FilterOp,
    Having,
    Order,
    OrderDirection,
)
from honeycomb.models.queries import QuerySpec
from honeycomb.models.recipients import (
    EmailRecipientDetails,
    PagerDutyRecipientDetails,
    RecipientCreate,
    RecipientType,
    SlackRecipientDetails,
    WebhookHeader,
    WebhookRecipientDetails,
)
from honeycomb.models.slos import SLI, SLOCreate
from honeycomb.models.triggers import (
    TriggerAlertType,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)


def save_snapshot(output_dir: Path, category: str, name: str, data: dict) -> None:
    """Save a serialization snapshot to disk."""
    category_dir = output_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)

    file_path = category_dir / f"{name}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    print(f"  ✓ {category}/{name}.json")


def capture_trigger_snapshots(output_dir: Path) -> None:
    """Capture all trigger model variations."""
    print("Capturing Trigger snapshots...")

    # 1. Minimal trigger
    trigger = TriggerCreate(
        name="Minimal Trigger",
        threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
        query=TriggerQuery(time_range=900),
    )
    save_snapshot(output_dir, "triggers", "minimal", trigger.model_dump_for_api())

    # 2. Full trigger with all fields
    trigger = TriggerCreate(
        name="Full Featured Trigger",
        description="Comprehensive trigger with all optional fields",
        threshold=TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN_OR_EQUAL,
            value=150.0,
            exceeded_limit=3,
        ),
        frequency=1800,
        query=TriggerQuery(
            time_range=1800,
            granularity=60,
            calculations=[Calculation(op=CalcOp.P99, column="duration_ms")],
            filters=[
                Filter(column="status_code", op=FilterOp.EQUALS, value=500),
                Filter(column="error", op=FilterOp.EXISTS),
            ],
            breakdowns=["endpoint", "method"],
            filter_combination=FilterCombination.OR,
        ),
        disabled=True,
        alert_type=TriggerAlertType.ON_TRUE,
        recipients=[{"id": "recip1"}, {"id": "recip2"}],
    )
    save_snapshot(output_dir, "triggers", "full_featured", trigger.model_dump_for_api())

    # 3. Saved query reference
    trigger = TriggerCreate(
        name="Saved Query Trigger",
        threshold=TriggerThreshold(op=TriggerThresholdOp.LESS_THAN, value=50.0),
        frequency=900,
        query_id="saved_query_abc123",
    )
    save_snapshot(output_dir, "triggers", "saved_query", trigger.model_dump_for_api())

    # 4. Complex filters
    trigger = TriggerCreate(
        name="Complex Filters",
        threshold=TriggerThreshold(op=TriggerThresholdOp.LESS_THAN_OR_EQUAL, value=10.0),
        query=TriggerQuery(
            time_range=3600,
            calculations=[Calculation(op=CalcOp.COUNT)],
            filters=[
                Filter(column="endpoint", op=FilterOp.IN, value=["/api/v1", "/api/v2"]),
                Filter(column="duration_ms", op=FilterOp.GREATER_THAN, value=1000),
            ],
            filter_combination=FilterCombination.AND,
        ),
    )
    save_snapshot(output_dir, "triggers", "complex_filters", trigger.model_dump_for_api())


def capture_column_snapshots(output_dir: Path) -> None:
    """Capture all column model variations."""
    print("Capturing Column snapshots...")

    # All column types
    for col_type in ColumnType:
        column = ColumnCreate(key_name=f"test_{col_type.value}", type=col_type)
        save_snapshot(output_dir, "columns", f"type_{col_type.value}", column.model_dump_for_api())

    # With description
    column = ColumnCreate(
        key_name="duration_ms",
        type=ColumnType.FLOAT,
        description="Request duration in milliseconds",
    )
    save_snapshot(output_dir, "columns", "with_description", column.model_dump_for_api())

    # Hidden column
    column = ColumnCreate(
        key_name="internal_id",
        type=ColumnType.STRING,
        hidden=True,
    )
    save_snapshot(output_dir, "columns", "hidden", column.model_dump_for_api())


def capture_marker_snapshots(output_dir: Path) -> None:
    """Capture all marker model variations."""
    print("Capturing Marker snapshots...")

    # Minimal
    marker = MarkerCreate(message="Deploy v1.0", type="deploy")
    save_snapshot(output_dir, "markers", "minimal", marker.model_dump_for_api())

    # With start time
    marker = MarkerCreate(message="Deploy v1.1", type="deploy", start_time=1704067200)
    save_snapshot(output_dir, "markers", "with_start_time", marker.model_dump_for_api())

    # Time range
    marker = MarkerCreate(
        message="Maintenance window",
        type="maintenance",
        start_time=1704067200,
        end_time=1704070800,
    )
    save_snapshot(output_dir, "markers", "time_range", marker.model_dump_for_api())

    # With URL
    marker = MarkerCreate(
        message="Release v1.2.3",
        type="deploy",
        url="https://github.com/org/repo/releases/v1.2.3",
    )
    save_snapshot(output_dir, "markers", "with_url", marker.model_dump_for_api())

    # Marker setting
    setting = MarkerSettingCreate(type="deploy", color="#FF5733")
    save_snapshot(output_dir, "markers", "setting", setting.model_dump_for_api())


def capture_recipient_snapshots(output_dir: Path) -> None:
    """Capture all recipient model variations."""
    print("Capturing Recipient snapshots...")

    # Email
    recipient = RecipientCreate(
        type=RecipientType.EMAIL,
        details=EmailRecipientDetails(email_address="alerts@example.com"),
    )
    save_snapshot(output_dir, "recipients", "email", recipient.model_dump_for_api())

    # Slack
    recipient = RecipientCreate(
        type=RecipientType.SLACK,
        details=SlackRecipientDetails(slack_channel="#alerts"),
    )
    save_snapshot(output_dir, "recipients", "slack", recipient.model_dump_for_api())

    # PagerDuty
    recipient = RecipientCreate(
        type=RecipientType.PAGERDUTY,
        details=PagerDutyRecipientDetails(
            pagerduty_integration_key="a" * 32,
            pagerduty_integration_name="Production Alerts",
        ),
    )
    save_snapshot(output_dir, "recipients", "pagerduty", recipient.model_dump_for_api())

    # Webhook minimal
    recipient = RecipientCreate(
        type=RecipientType.WEBHOOK,
        details=WebhookRecipientDetails(
            webhook_url="https://example.com/webhook",
            webhook_name="My Webhook",
        ),
    )
    save_snapshot(output_dir, "recipients", "webhook_minimal", recipient.model_dump_for_api())

    # Webhook with headers
    recipient = RecipientCreate(
        type=RecipientType.WEBHOOK,
        details=WebhookRecipientDetails(
            webhook_url="https://example.com/webhook",
            webhook_name="Authenticated Webhook",
            webhook_secret="my_secret",
            webhook_headers=[
                WebhookHeader(header="Authorization", value="Bearer token123"),
                WebhookHeader(header="X-Custom-Header", value="custom_value"),
            ],
        ),
    )
    save_snapshot(output_dir, "recipients", "webhook_with_headers", recipient.model_dump_for_api())


def capture_dataset_snapshots(output_dir: Path) -> None:
    """Capture dataset model variations."""
    print("Capturing Dataset snapshots...")

    # Minimal
    dataset = DatasetCreate(name="test-dataset")
    save_snapshot(output_dir, "datasets", "minimal", dataset.model_dump_for_api())

    # With description
    dataset = DatasetCreate(
        name="production-api",
        description="Production API telemetry",
    )
    save_snapshot(output_dir, "datasets", "with_description", dataset.model_dump_for_api())


def capture_query_snapshots(output_dir: Path) -> None:
    """Capture query model variations."""
    print("Capturing Query snapshots...")

    # Simple query
    query = QuerySpec(
        time_range=3600,
        calculations=[Calculation(op=CalcOp.COUNT)],
    )
    save_snapshot(output_dir, "queries", "simple", query.model_dump_for_api())

    # Complex query with all fields
    query = QuerySpec(
        time_range=7200,
        granularity=300,
        calculations=[
            Calculation(op=CalcOp.COUNT),
            Calculation(op=CalcOp.P99, column="duration_ms"),
            Calculation(op=CalcOp.AVG, column="response_size"),
        ],
        filters=[
            Filter(column="status_code", op=FilterOp.EQUALS, value=200),
            Filter(column="endpoint", op=FilterOp.STARTS_WITH, value="/api/"),
        ],
        filter_combination=FilterCombination.AND,
        breakdowns=["endpoint", "method"],
        orders=[
            Order(column="duration_ms", op=CalcOp.P99, order=OrderDirection.DESCENDING),
        ],
        havings=[
            Having(
                calculate_op=CalcOp.COUNT,
                op=FilterOp.GREATER_THAN,
                value=100,
            ),
        ],
        limit=100,
    )
    save_snapshot(output_dir, "queries", "complex", query.model_dump_for_api())


def capture_slo_snapshots(output_dir: Path) -> None:
    """Capture SLO model variations."""
    print("Capturing SLO snapshots...")

    # Simple SLO with existing derived column
    slo = SLOCreate(
        name="API Availability",
        description="99.9% of requests succeed",
        time_period_days=30,
        target_per_million=999000,
        sli=SLI(alias="success_rate"),
    )
    save_snapshot(output_dir, "slos", "simple", slo.model_dump_for_api())

    # SLO with inline derived column expression
    slo = SLOCreate(
        name="API Latency",
        time_period_days=7,
        target_per_million=995000,
        sli=SLI(
            alias="latency_p99",
            expression="HEATMAP(duration_ms, 100)",
            description="P99 latency derived column",
        ),
    )
    save_snapshot(output_dir, "slos", "with_expression", slo.model_dump_for_api())

    # SLO with dataset slugs (multi-dataset)
    slo = SLOCreate(
        name="Multi-Dataset SLO",
        time_period_days=30,
        target_per_million=999000,
        sli=SLI(alias="availability"),
        dataset_slugs=["frontend", "backend", "api"],
    )
    save_snapshot(output_dir, "slos", "multi_dataset", slo.model_dump_for_api())


def capture_board_snapshots(output_dir: Path) -> None:
    """Capture board model variations."""
    print("Capturing Board snapshots...")

    # Minimal board
    board = BoardCreate(
        name="API Dashboard",
    )
    save_snapshot(output_dir, "boards", "minimal", board.model_dump_for_api())

    # Board with description
    board = BoardCreate(
        name="Production Metrics",
        description="Key production API metrics and alerts",
    )
    save_snapshot(output_dir, "boards", "with_description", board.model_dump_for_api())

    # Board with panels (simplified)
    board = BoardCreate(
        name="Full Dashboard",
        description="Dashboard with panels",
        panels=[
            {
                "type": "query",
                "query": {
                    "time_range": 3600,
                    "calculations": [{"op": "COUNT"}],
                },
            },
        ],
        tags=[{"key": "team", "value": "platform"}],
    )
    save_snapshot(output_dir, "boards", "with_panels", board.model_dump_for_api())


def main() -> int:
    """Capture all serialization snapshots."""
    output_dir = Path(__file__).parent.parent / ".claude/serialization-snapshots/pre-migration"

    print(f"Capturing serialization snapshots to: {output_dir}")
    print()

    try:
        capture_trigger_snapshots(output_dir)
        capture_column_snapshots(output_dir)
        capture_marker_snapshots(output_dir)
        capture_recipient_snapshots(output_dir)
        capture_dataset_snapshots(output_dir)
        capture_query_snapshots(output_dir)
        capture_slo_snapshots(output_dir)
        capture_board_snapshots(output_dir)

        print()
        print(f"✓ All snapshots captured successfully in {output_dir}")
        print()
        print("After migration, run this script again with output to post-migration/")
        print("Then compare with: diff -r pre-migration/ post-migration/")

        return 0

    except Exception as e:
        print(f"\n✗ Error capturing snapshots: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Edge case tests using Polyfactory's coverage() method.

The coverage() method generates minimal instances to cover all field variations:
- All enum values
- Optional fields (present vs absent)
- Collection types (empty, single, multiple)
- Boundary conditions

This ensures factories produce valid data for all possible model states.
"""

import pytest

from tests.factories import (
    BoardFactory,
    ColumnFactory,
    DatasetFactory,
    EmailRecipientFactory,
    MarkerFactory,
    QueryAnnotationFactory,
    SLOFactory,
    TriggerFactory,
    WebhookRecipientFactory,
)


class TestFactoryCoverage:
    """Test that factories can generate all valid model variations."""

    def test_column_factory_coverage(self):
        """Test ColumnFactory covers all column types."""
        # coverage() generates instances for all enum values and optional field combinations
        instances = list(ColumnFactory.coverage())

        # Should have multiple instances covering different types
        assert len(instances) > 1

        # All instances should be valid
        for column in instances:
            assert column.id
            assert column.key_name
            assert column.type  # Enum value
            assert isinstance(column.hidden, bool)

    def test_dataset_factory_coverage(self):
        """Test DatasetFactory covers settings variations."""
        instances = list(DatasetFactory.coverage())

        # Should cover delete_protected true/false at minimum
        assert len(instances) >= 2

        for dataset in instances:
            assert dataset.slug
            assert dataset.name

    def test_slo_factory_coverage(self):
        """Test SLOFactory covers time period variations."""
        instances = list(SLOFactory.coverage())

        # Should cover different time_period_days values
        assert len(instances) >= 1

        for slo in instances:
            assert slo.id
            assert slo.name
            assert slo.target_per_million >= 0
            assert slo.target_per_million <= 999999
            assert slo.time_period_days >= 1

    def test_trigger_factory_coverage(self):
        """Test TriggerFactory covers alert types and states."""
        instances = list(TriggerFactory.coverage())

        # Should cover disabled true/false, triggered true/false, alert_type variations
        assert len(instances) >= 2

        for trigger in instances:
            assert trigger.name
            assert trigger.dataset_slug
            assert trigger.frequency >= 60
            assert isinstance(trigger.disabled, bool)

    def test_email_recipient_factory_coverage(self):
        """Test EmailRecipientFactory generates valid recipients."""
        instances = list(EmailRecipientFactory.coverage())

        # Should generate at least one instance
        assert len(instances) >= 1

        for recipient in instances:
            assert recipient.type == "email"
            # details might be None in coverage variations
            if recipient.details:
                assert recipient.details.email_address  # Has some value

    def test_webhook_recipient_factory_coverage(self):
        """Test WebhookRecipientFactory generates valid webhooks."""
        instances = list(WebhookRecipientFactory.coverage())

        assert len(instances) >= 1

        for recipient in instances:
            assert recipient.type == "webhook"
            # details might be None in coverage variations
            if recipient.details:
                assert recipient.details.webhook_url
                assert recipient.details.webhook_name

    def test_marker_factory_coverage(self):
        """Test MarkerFactory covers type variations."""
        instances = list(MarkerFactory.coverage())

        assert len(instances) >= 1

        for marker in instances:
            assert marker.id
            assert marker.message
            # type is optional
            assert marker.created_at
            assert marker.updated_at

    def test_query_annotation_factory_coverage(self):
        """Test QueryAnnotationFactory generates valid annotations."""
        instances = list(QueryAnnotationFactory.coverage())

        assert len(instances) >= 1

        for annotation in instances:
            assert annotation.id
            assert annotation.name
            assert annotation.query_id

    def test_board_factory_coverage(self):
        """Test BoardFactory covers board types."""
        instances = list(BoardFactory.coverage())

        # Should cover different board types and layout_generation values
        assert len(instances) >= 1

        for board in instances:
            assert board.id
            assert board.name
            assert board.type
            # Verify it has valid structure
            assert hasattr(board, 'panels')


class TestCoverageValidation:
    """Verify coverage-generated instances are Pydantic-valid."""

    @pytest.mark.parametrize("factory", [
        ColumnFactory,
        DatasetFactory,
        SLOFactory,
        TriggerFactory,
        EmailRecipientFactory,
        WebhookRecipientFactory,
        MarkerFactory,
        QueryAnnotationFactory,
    ])
    def test_coverage_instances_validate(self, factory):
        """Test that all coverage() instances pass Pydantic validation."""
        # If coverage() produces invalid data, Pydantic will raise ValidationError
        for instance in factory.coverage():
            # Re-validate to ensure it's truly valid
            instance.model_validate(instance.model_dump())
            # If we get here, instance is valid

    def test_coverage_serialization_round_trip(self):
        """Test that coverage instances can be serialized and deserialized."""
        # Pick a complex model
        for slo in SLOFactory.coverage():
            # Serialize to JSON (as would be sent to API)
            json_data = slo.model_dump(mode="json", by_alias=True, exclude_none=True)

            # Should be a dict
            assert isinstance(json_data, dict)
            assert "id" in json_data or json_data  # Either has ID or is non-empty

            # Should be deserializable
            from honeycomb.models import SLO
            reconstructed = SLO.model_validate(json_data)
            assert reconstructed.name == slo.name

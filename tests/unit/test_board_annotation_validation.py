"""Tests for QueryPanel annotation validation."""

import pytest
from pydantic import ValidationError

from honeycomb.models.boards import QueryPanel, QueryPanelQueryPanel


class TestQueryPanelAnnotationValidation:
    """Test validation of query_annotation_id vs query_id."""

    def test_valid_different_ids(self):
        """Valid: annotation_id differs from query_id."""
        panel = QueryPanel(
            type="query",
            query_panel=QueryPanelQueryPanel(
                query_id="query-abc123",
                query_annotation_id="annot-xyz789",
                query_style="table",
            ),
        )
        assert panel.query_panel.query_id == "query-abc123"
        assert panel.query_panel.query_annotation_id == "annot-xyz789"

    def test_invalid_same_ids(self):
        """Invalid: annotation_id same as query_id (common mistake)."""
        with pytest.raises(ValidationError) as exc_info:
            QueryPanel(
                type="query",
                query_panel=QueryPanelQueryPanel(
                    query_id="knS9urAWEPM",
                    query_annotation_id="knS9urAWEPM",  # WRONG - same as query_id
                    query_style="table",
                ),
            )

        error = exc_info.value.errors()[0]
        assert "query_annotation_id cannot be the same as query_id" in error["msg"]
        assert "Query annotations are separate metadata objects" in error["msg"]

    def test_validation_message_includes_helpful_guidance(self):
        """Validation error includes guidance on how to fix."""
        with pytest.raises(ValidationError) as exc_info:
            QueryPanelQueryPanel(
                query_id="test-123",
                query_annotation_id="test-123",
                query_style="graph",
            )

        error_msg = exc_info.value.errors()[0]["msg"]
        assert "create_async" in error_msg.lower()
        assert "BoardBuilder" in error_msg or "QueryBuilder" in error_msg

    def test_nested_panel_validation(self):
        """Validation works when QueryPanelQueryPanel is nested in QueryPanel."""
        with pytest.raises(ValidationError) as exc_info:
            QueryPanel(
                type="query",
                query_panel=QueryPanelQueryPanel(
                    query_id="same-id",
                    query_annotation_id="same-id",  # Invalid
                    query_style="combo",
                ),
            )

        # Should fail validation
        assert exc_info.value.errors()

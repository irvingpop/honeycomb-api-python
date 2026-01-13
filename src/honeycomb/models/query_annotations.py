"""Pydantic models for Honeycomb Query Annotations."""

from __future__ import annotations

from honeycomb._generated_models import (
    QueryAnnotation as _QueryAnnotationGenerated,
)
from honeycomb._generated_models import (
    QueryAnnotationSource,
)

# Re-export for backward compatibility (lowercase → uppercase for enum values)
# Note: Generated enum has lowercase values (query, board) which is correct for API
__all__ = ["QueryAnnotationSource", "QueryAnnotationCreate", "QueryAnnotation"]


class QueryAnnotationCreate(_QueryAnnotationGenerated):
    """Model for creating a new query annotation.

    Query Annotations add name and description metadata to queries
    for collaboration and documentation.

    Generated model works for both create and response (id is optional).
    """

    pass


class QueryAnnotation(_QueryAnnotationGenerated):
    """A Honeycomb query annotation (response model).

    Query Annotations consist of a name and description associated
    with a query to add context when collaborating.

    Generated model includes all fields from the API response.
    """

    model_config = {"extra": "allow"}

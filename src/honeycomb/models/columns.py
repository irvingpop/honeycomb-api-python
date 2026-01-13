"""Pydantic models for Honeycomb Columns."""

from __future__ import annotations

from honeycomb._generated_models import Column as _ColumnGenerated
from honeycomb._generated_models import CreateColumn as _CreateColumnGenerated
from honeycomb._generated_models import CreateColumnColumnType

# Re-export generated enum
ColumnType = CreateColumnColumnType


class ColumnCreate(_CreateColumnGenerated):
    """Model for creating a new column (extends generated CreateColumn)."""

    pass


class Column(_ColumnGenerated):
    """A Honeycomb column (response model, extends generated Column)."""

    pass

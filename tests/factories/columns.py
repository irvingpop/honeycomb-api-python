"""Factories for Column and DerivedColumn models."""

from honeycomb._generated_models import CreateColumnColumnType
from honeycomb.models import Column, ColumnCreate, DerivedColumn, DerivedColumnCreate

from .base import HoneycombFactory


class ColumnFactory(HoneycombFactory):
    """Factory for Column response model.

    Example:
        column = ColumnFactory.build(key_name="request_id")
        columns = ColumnFactory.batch(10)
    """

    __model__ = Column

    id = lambda: HoneycombFactory._honeycomb_id()
    key_name = lambda: f"column_{HoneycombFactory._honeycomb_id()}"
    type = lambda: HoneycombFactory.__random__.choice(list(CreateColumnColumnType))
    description = lambda: "A test column"
    hidden = False


class ColumnCreateFactory(HoneycombFactory):
    """Factory for ColumnCreate request model.

    Example:
        payload = ColumnCreateFactory.build(key_name="new_column")
    """

    __model__ = ColumnCreate

    key_name = lambda: f"column_{HoneycombFactory._honeycomb_id()}"
    type = CreateColumnColumnType.string
    description = lambda: "A test column"
    hidden = False


class DerivedColumnFactory(HoneycombFactory):
    """Factory for DerivedColumn (CalculatedField) response model.

    Example:
        dc = DerivedColumnFactory.build(alias="success_rate")
        dcs = DerivedColumnFactory.batch(5)
    """

    __model__ = DerivedColumn

    id = lambda: HoneycombFactory._honeycomb_id()
    alias = lambda: f"derived_{HoneycombFactory._honeycomb_id()}"
    expression = lambda: "IF(LT($status_code, 400), 1, 0)"
    description = lambda: "A test derived column"
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


class DerivedColumnCreateFactory(HoneycombFactory):
    """Factory for DerivedColumnCreate request model.

    Example:
        payload = DerivedColumnCreateFactory.build(alias="new_derived")
    """

    __model__ = DerivedColumnCreate

    alias = lambda: f"derived_{HoneycombFactory._honeycomb_id()}"
    expression = lambda: "IF(LT($status_code, 400), 1, 0)"
    description = lambda: "A test derived column"

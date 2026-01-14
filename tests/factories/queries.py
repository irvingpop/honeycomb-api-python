"""Factories for Query and QueryAnnotation models."""

from honeycomb._generated_models import (
    QueryAnnotationSource,
    QueryCalculation,
    QueryResultDetailsData,
    QueryResultsData,
)
from honeycomb.models import Query, QueryAnnotation, QueryAnnotationCreate, QueryResult, QuerySpec

from .base import HoneycombFactory


class QueryCalculationFactory(HoneycombFactory):
    """Factory for QueryCalculation."""

    __model__ = QueryCalculation

    op = "COUNT"


class QuerySpecFactory(HoneycombFactory):
    """Factory for QuerySpec (query definition).

    Example:
        spec = QuerySpecFactory.build()
    """

    __model__ = QuerySpec

    calculations = lambda: [QueryCalculationFactory.build()]
    time_range = lambda: HoneycombFactory.__random__.choice([300, 600, 900, 1800, 3600])


class QueryFactory(HoneycombFactory):
    """Factory for Query response model.

    Example:
        query = QueryFactory.build(id="query-123")
        queries = QueryFactory.batch(5)
    """

    __model__ = Query

    id = lambda: HoneycombFactory._honeycomb_id()
    query_annotation_id = lambda: HoneycombFactory._honeycomb_id()
    query_json = lambda: {
        "calculations": [{"op": "COUNT"}],
        "time_range": 3600,
    }
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


class QueryResultsDataFactory(HoneycombFactory):
    """Factory for QueryResultsData (individual result row)."""

    __model__ = QueryResultsData

    data = lambda: {"COUNT": HoneycombFactory.__random__.randint(1, 1000)}


class QueryResultDetailsDataFactory(HoneycombFactory):
    """Factory for QueryResultDetailsData."""

    __model__ = QueryResultDetailsData


class QueryResultFactory(HoneycombFactory):
    """Factory for QueryResult response model.

    Example:
        result = QueryResultFactory.build(id="result-123", complete=True)
    """

    __model__ = QueryResult

    id = lambda: HoneycombFactory._honeycomb_id()
    complete = True


# =============================================================================
# Query Annotation Factories
# =============================================================================


class QueryAnnotationFactory(HoneycombFactory):
    """Factory for QueryAnnotation response model.

    Example:
        annotation = QueryAnnotationFactory.build(name="My Query")
    """

    __model__ = QueryAnnotation

    id = lambda: HoneycombFactory._honeycomb_id()
    name = lambda: f"Test Query {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test query annotation"
    query_id = lambda: HoneycombFactory._honeycomb_id()
    source = QueryAnnotationSource.query
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


class QueryAnnotationCreateFactory(HoneycombFactory):
    """Factory for QueryAnnotationCreate request model.

    Example:
        payload = QueryAnnotationCreateFactory.build(name="New Query", query_id="q123")
    """

    __model__ = QueryAnnotationCreate

    name = lambda: f"Test Query {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test query annotation"
    query_id = lambda: HoneycombFactory._honeycomb_id()

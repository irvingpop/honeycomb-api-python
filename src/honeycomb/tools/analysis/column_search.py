"""Column search functionality with fuzzy matching.

Searches for columns across datasets using fuzzy matching and finds
related derived columns that reference matched columns.
"""

import asyncio
import re
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from honeycomb.tools.analysis.models import (
    ColumnSearchResult,
    SearchColumnsResponse,
    format_relative_time,
)

if TYPE_CHECKING:
    from honeycomb import HoneycombClient
    from honeycomb.models import Column, DerivedColumn


# Minimum similarity threshold for fuzzy matches
MIN_SIMILARITY_THRESHOLD = 0.3


def calculate_similarity(query: str, column_name: str) -> float:
    """Calculate similarity score between query and column name.

    Scoring strategy:
    - Exact match: 1.0
    - Prefix match: 0.9
    - Substring match: 0.8
    - Fuzzy match: ratio * 0.7

    Args:
        query: Search query string
        column_name: Column name to compare against

    Returns:
        Similarity score between 0.0 and 1.0
    """
    query_lower = query.lower()
    name_lower = column_name.lower()

    # Exact match
    if name_lower == query_lower:
        return 1.0

    # Prefix match
    if name_lower.startswith(query_lower):
        return 0.9

    # Substring match
    if query_lower in name_lower:
        return 0.8

    # Fuzzy match using SequenceMatcher
    ratio = SequenceMatcher(None, query_lower, name_lower).ratio()
    return ratio * 0.7


def expression_references_column(expression: str, column_name: str) -> bool:
    """Check if a derived column expression references a column.

    Derived column expressions use $column_name syntax.

    Args:
        expression: The derived column expression
        column_name: The column name to search for

    Returns:
        True if the expression references the column
    """
    # Match $column_name NOT followed by characters that would extend the column name
    # Column names can contain: a-zA-Z0-9_. (letters, numbers, underscore, dot)
    # Using negative lookahead to ensure we match the complete column name
    pattern = rf"\${re.escape(column_name)}(?![a-zA-Z0-9_.])"
    return bool(re.search(pattern, expression))


def _column_to_result(
    col: "Column",
    dataset: str,
    similarity: float,
) -> ColumnSearchResult:
    """Convert a Column model to ColumnSearchResult."""
    return ColumnSearchResult(
        column=col.key_name,
        dataset=dataset,
        type=col.type.value if col.type else "string",
        description=col.description,
        similarity=similarity,
        last_written=format_relative_time(col.last_written),
        is_derived=False,
        derived_expression=None,
    )


def _derived_column_to_result(
    dc: "DerivedColumn",
    dataset: str,
    similarity: float,
) -> ColumnSearchResult:
    """Convert a DerivedColumn model to ColumnSearchResult."""
    return ColumnSearchResult(
        column=dc.alias,
        dataset=dataset,
        type="derived",
        description=dc.description,
        similarity=similarity,
        last_written=None,  # Derived columns don't have last_written
        is_derived=True,
        derived_expression=dc.expression,
    )


async def search_columns_async(
    client: "HoneycombClient",
    query: str,
    dataset: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> SearchColumnsResponse:
    """Search for columns matching a query across datasets.

    Uses v1 endpoints only (Configuration keys):
    - /1/datasets
    - /1/columns/{dataset}
    - /1/derived_columns/{dataset}

    Args:
        client: HoneycombClient instance
        query: Search query for fuzzy matching
        dataset: Optional specific dataset to search (searches all if None)
        limit: Maximum results to return (default: 50, max: 1000)
        offset: Offset for pagination (default: 0)

    Returns:
        SearchColumnsResponse with matched columns and related derived columns
    """
    # Cap limit at 1000
    limit = min(limit, 1000)

    # Get list of datasets to search
    if dataset:
        datasets_to_search = [dataset]
    else:
        all_datasets = await client.datasets.list_async()
        datasets_to_search = [d.slug for d in all_datasets]

    # Fetch columns and derived columns from all datasets in parallel
    async def fetch_dataset_data(
        ds: str,
    ) -> tuple[str, list["Column"], list["DerivedColumn"]]:
        columns_coro = client.columns.list_async(dataset=ds)
        derived_coro = client.derived_columns.list_async(dataset=ds)
        columns, derived = await asyncio.gather(columns_coro, derived_coro)
        return ds, columns, derived

    results = await asyncio.gather(
        *[fetch_dataset_data(ds) for ds in datasets_to_search],
        return_exceptions=True,
    )

    # Collect all matches and derived columns
    all_matches: list[ColumnSearchResult] = []
    all_derived_columns: dict[str, list[DerivedColumn]] = {}
    datasets_searched = 0

    for result in results:
        # Skip failed fetches (dataset might not exist, etc.)
        if isinstance(result, BaseException):
            continue

        # Type narrowing: at this point result is the tuple, not an exception
        ds, columns, derived_cols = result
        datasets_searched += 1
        all_derived_columns[ds] = derived_cols

        # Score regular columns
        for col in columns:
            score = calculate_similarity(query, col.key_name)
            if score >= MIN_SIMILARITY_THRESHOLD:
                all_matches.append(_column_to_result(col, ds, score))

        # Score derived columns
        for dc in derived_cols:
            score = calculate_similarity(query, dc.alias)
            if score >= MIN_SIMILARITY_THRESHOLD:
                all_matches.append(_derived_column_to_result(dc, ds, score))

    # Also search environment-wide derived columns
    try:
        env_derived = await client.derived_columns.list_async(dataset="__all__")
        for dc in env_derived:
            score = calculate_similarity(query, dc.alias)
            if score >= MIN_SIMILARITY_THRESHOLD:
                all_matches.append(_derived_column_to_result(dc, "__environment__", score))
        # Store env-wide DCs for related DC lookup
        all_derived_columns["__environment__"] = env_derived
    except Exception:
        # Environment-wide DCs might not be available
        pass

    # Sort by similarity score (descending)
    all_matches.sort(key=lambda m: m.similarity, reverse=True)
    total_matches = len(all_matches)

    # Apply pagination
    paginated_matches = all_matches[offset : offset + limit]

    # Find related derived columns (DCs that reference matched regular columns)
    related_dcs = _find_related_derived_columns(paginated_matches, all_derived_columns)

    return SearchColumnsResponse(
        results=paginated_matches,
        related_derived_columns=related_dcs,
        total_matches=total_matches,
        datasets_searched=datasets_searched,
        has_more=(offset + limit) < total_matches,
    )


def _find_related_derived_columns(
    matches: list[ColumnSearchResult],
    all_derived_columns: dict[str, list["DerivedColumn"]],
) -> list[ColumnSearchResult]:
    """Find derived columns that reference any of the matched regular columns.

    Args:
        matches: The matched columns from search
        all_derived_columns: Dict mapping dataset slug to list of derived columns

    Returns:
        List of derived columns that reference matched columns
    """
    related: list[ColumnSearchResult] = []

    # Only look at non-derived matches
    regular_matches = {(m.dataset, m.column) for m in matches if not m.is_derived}

    for dataset, dcs in all_derived_columns.items():
        for dc in dcs:
            # Check if expression references any matched column
            for ds, col_name in regular_matches:
                if ds == dataset and expression_references_column(dc.expression, col_name):
                    # This DC references a matched column
                    related.append(
                        ColumnSearchResult(
                            column=dc.alias,
                            dataset=dataset,
                            type="derived",
                            description=dc.description,
                            similarity=0.0,  # Not a direct match
                            last_written=None,
                            is_derived=True,
                            derived_expression=dc.expression,
                        )
                    )
                    break  # Only add once per DC

    return related

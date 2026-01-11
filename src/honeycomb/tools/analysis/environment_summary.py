"""Environment summary functionality.

Provides a high-level overview of all datasets in an environment,
including semantic groups detection and custom column extraction.
"""

import asyncio
from typing import TYPE_CHECKING

from honeycomb.tools.analysis.models import (
    DatasetSummary,
    DerivedColumnSummary,
    EnvironmentSummaryResponse,
    format_relative_time,
)
from honeycomb.tools.analysis.semantic_groups import (
    detect_semantic_groups,
    extract_custom_columns,
)

if TYPE_CHECKING:
    from honeycomb import HoneycombClient
    from honeycomb.models import Dataset


async def get_environment_summary_async(
    client: "HoneycombClient",
    include_sample_columns: bool = True,
    sample_column_count: int = 10,
) -> EnvironmentSummaryResponse:
    """Get a summary of all datasets in the Honeycomb environment.

    Uses v1 endpoints only (Configuration keys):
    - /1/datasets
    - /1/columns/{dataset}
    - /1/derived_columns/{dataset}
    - /1/derived_columns (for environment-wide DCs)

    Args:
        client: HoneycombClient instance
        include_sample_columns: Include custom column names per dataset (default: True)
        sample_column_count: Max custom columns per dataset (default: 10, max: 50)

    Returns:
        EnvironmentSummaryResponse with dataset summaries and semantic groups
    """
    # Cap sample column count
    sample_column_count = min(sample_column_count, 50)

    # Fetch all datasets
    datasets = await client.datasets.list_async()

    # Fetch environment-wide derived columns
    env_derived_cols: list[DerivedColumnSummary] = []
    try:
        env_dcs = await client.derived_columns.list_async(dataset="__all__")
        env_derived_cols = [
            DerivedColumnSummary(
                alias=dc.alias,
                expression=dc.expression,
                description=dc.description,
            )
            for dc in env_dcs
        ]
    except Exception:
        # Environment-wide DCs might not be available
        pass

    # Fetch columns and derived columns for each dataset in parallel
    async def fetch_dataset_summary(dataset: "Dataset") -> DatasetSummary | None:
        try:
            columns_coro = client.columns.list_async(dataset=dataset.slug)
            derived_coro = client.derived_columns.list_async(dataset=dataset.slug)
            columns, derived_cols = await asyncio.gather(columns_coro, derived_coro)

            column_names = [c.key_name for c in columns]
            semantic_groups = detect_semantic_groups(column_names)

            custom_cols: list[str] = []
            if include_sample_columns:
                custom_cols = extract_custom_columns(column_names, sample_column_count)

            return DatasetSummary(
                name=dataset.slug,
                description=dataset.description,
                column_count=len(columns),
                derived_column_count=len(derived_cols),
                last_written=format_relative_time(dataset.last_written_at),
                semantic_groups=semantic_groups,
                custom_columns=custom_cols,
            )
        except Exception:
            # Skip datasets that fail to fetch
            return None

    summaries = await asyncio.gather(
        *[fetch_dataset_summary(ds) for ds in datasets],
        return_exceptions=True,
    )

    # Filter out None results and exceptions
    valid_summaries = [s for s in summaries if isinstance(s, DatasetSummary)]

    # Get environment name from auth info
    environment_name: str = "unknown"
    try:
        auth_info = await client.auth.get_async()
        env_slug = getattr(auth_info, "environment_slug", None)
        env_name = getattr(auth_info, "environment_name", None)
        if env_slug:
            environment_name = str(env_slug)
        elif env_name:
            environment_name = str(env_name)
    except Exception:
        pass  # Keep default "unknown"

    return EnvironmentSummaryResponse(
        environment=environment_name,
        dataset_count=len(valid_summaries),
        datasets=valid_summaries,
        environment_derived_columns=env_derived_cols if env_derived_cols else None,
    )

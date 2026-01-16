"""Environment summary functionality.

Provides a high-level overview of all datasets in an environment,
including semantic groups detection and custom column extraction.
"""

import asyncio
import contextlib
from datetime import datetime
from typing import TYPE_CHECKING

from honeycomb.tools.analysis.cache import (
    get_columns_cached,
    get_datasets_cached,
    get_derived_columns_cached,
)
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

    # Fetch all datasets (using cache - warms cache for subsequent column searches)
    datasets = await get_datasets_cached(client)

    # Fetch environment-wide derived columns (using cache)
    env_derived_cols: list[DerivedColumnSummary] = []
    try:
        env_dcs = await get_derived_columns_cached(client, "__all__")
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
            # Skip if dataset slug is missing
            if not dataset.slug:
                return None

            # Fetch columns and derived columns in parallel (using cache)
            columns_coro = get_columns_cached(client, dataset.slug)
            derived_coro = get_derived_columns_cached(client, dataset.slug)
            columns, derived_cols = await asyncio.gather(columns_coro, derived_coro)

            # Filter out None key_names from columns
            column_names = [c.key_name for c in columns if c.key_name is not None]
            semantic_groups = detect_semantic_groups(column_names)

            custom_cols: list[str] = []
            if include_sample_columns:
                custom_cols = extract_custom_columns(column_names, sample_column_count)

            # Parse ISO8601 timestamp if present
            last_written_dt: datetime | None = None
            if dataset.last_written_at:
                with contextlib.suppress(ValueError):
                    last_written_dt = datetime.fromisoformat(
                        dataset.last_written_at.replace("Z", "+00:00")
                    )

            return DatasetSummary(
                name=dataset.slug,
                description=dataset.description,
                column_count=len(columns),
                derived_column_count=len(derived_cols),
                last_written=format_relative_time(last_written_dt),
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
        # Auth info has nested environment object with slug and name (v1 only)
        # v2 (management key) auth doesn't have environment since it can access multiple
        if hasattr(auth_info, "environment") and auth_info.environment:
            # Prefer slug over name (slug is more canonical)
            if auth_info.environment.slug:
                environment_name = str(auth_info.environment.slug)
            elif auth_info.environment.name:
                environment_name = str(auth_info.environment.name)
    except Exception:
        pass  # Keep default "unknown"

    return EnvironmentSummaryResponse(
        environment=environment_name,
        dataset_count=len(valid_summaries),
        datasets=valid_summaries,
        environment_derived_columns=env_derived_cols if env_derived_cols else None,
    )

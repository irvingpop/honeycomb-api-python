"""Basic dataset operations examples.

These examples demonstrate listing and managing datasets.
"""

from __future__ import annotations

import time

from honeycomb import Dataset, DatasetCreate, DatasetUpdate, HoneycombClient


# start_example:list_datasets
async def list_datasets(client: HoneycombClient) -> list[Dataset]:
    """List all datasets in the environment.

    Args:
        client: Authenticated HoneycombClient

    Returns:
        List of datasets
    """
    datasets = await client.datasets.list_async()
    for dataset in datasets:
        print(f"{dataset.name} ({dataset.slug})")
        print(f"  Columns: {dataset.regular_columns_count}")
    return datasets


# end_example:list_datasets


# start_example:create_dataset
async def create_dataset(client: HoneycombClient, name: str | None = None) -> str:
    """Create a new dataset.

    Args:
        client: Authenticated HoneycombClient
        name: Optional dataset name (defaults to unique name with timestamp)

    Returns:
        The created dataset slug
    """
    # Use timestamp for unique name if not provided
    dataset_name = name or f"test-dataset-{int(time.time())}"
    dataset = await client.datasets.create_async(
        DatasetCreate(
            name=dataset_name,
            description="Created for testing",
            expand_json_depth=2,
        )
    )
    return dataset.slug


# end_example:create_dataset


# start_example:get_dataset
async def get_dataset(client: HoneycombClient, slug: str) -> Dataset:
    """Get a specific dataset by slug.

    Args:
        client: Authenticated HoneycombClient
        slug: Dataset slug to retrieve

    Returns:
        The dataset object
    """
    dataset = await client.datasets.get_async(slug)
    print(f"Name: {dataset.name}")
    print(f"Slug: {dataset.slug}")
    print(f"Description: {dataset.description}")
    print(f"Columns: {dataset.regular_columns_count}")
    return dataset


# end_example:get_dataset


# start_example:update_dataset
async def update_dataset(client: HoneycombClient, slug: str) -> Dataset:
    """Update an existing dataset.

    Args:
        client: Authenticated HoneycombClient
        slug: Dataset slug to update

    Returns:
        The updated dataset
    """
    # Use DatasetUpdate for partial updates - only specified fields are changed
    dataset = await client.datasets.update_async(
        slug,
        DatasetUpdate(
            description="Updated description",
        ),
    )
    return dataset


# end_example:update_dataset


# start_example:delete_protection
async def toggle_delete_protection(client: HoneycombClient, slug: str) -> Dataset:
    """Enable or disable delete protection on a dataset.

    Args:
        client: Authenticated HoneycombClient
        slug: Dataset slug

    Returns:
        The updated dataset
    """
    # Enable delete protection to prevent accidental deletion
    dataset = await client.datasets.set_delete_protected_async(slug, protected=True)
    print(f"Delete protection enabled: {dataset.delete_protected}")

    # Or disable it when you need to delete the dataset
    dataset = await client.datasets.set_delete_protected_async(slug, protected=False)
    print(f"Delete protection disabled: {dataset.delete_protected}")

    return dataset


# end_example:delete_protection


# start_example:list_sync
def list_datasets_sync(client: HoneycombClient) -> list[Dataset]:
    """List datasets using sync client.

    Args:
        client: Authenticated HoneycombClient

    Returns:
        List of datasets
    """
    datasets = client.datasets.list()
    for dataset in datasets:
        print(f"{dataset.name} ({dataset.slug})")
    return datasets


# end_example:list_sync


# TEST_ASSERTIONS
async def test_list_datasets(datasets: list[Dataset]) -> None:
    """Verify list example worked correctly."""
    assert isinstance(datasets, list)


async def test_create_dataset(client: HoneycombClient, dataset_slug: str) -> None:
    """Verify create example worked correctly."""
    dataset = await client.datasets.get_async(dataset_slug)
    assert dataset.slug == dataset_slug


async def test_get_dataset(dataset: Dataset, slug: str) -> None:
    """Verify get example worked correctly."""
    assert dataset.slug == slug


async def test_update_dataset(dataset: Dataset) -> None:
    """Verify update example worked correctly."""
    assert dataset.description == "Updated description"


# CLEANUP
async def cleanup(client: HoneycombClient, dataset_slug: str) -> None:
    """Clean up resources created by example."""
    from honeycomb import HoneycombAPIError

    try:
        # Remove delete protection before deleting
        await client.datasets.set_delete_protected_async(dataset_slug, protected=False)
        await client.datasets.delete_async(dataset_slug)
    except HoneycombAPIError as e:
        # Ignore 404 if dataset doesn't exist
        if e.status_code != 404:
            raise

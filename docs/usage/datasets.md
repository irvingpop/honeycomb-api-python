# Working with Datasets

Datasets are collections of events in Honeycomb. This guide shows how to manage them.

## Listing Datasets

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    datasets = await client.datasets.list_async()
    
    for dataset in datasets:
        print(f"Name: {dataset.name}")
        print(f"Slug: {dataset.slug}")
        print(f"Columns: {dataset.regular_columns_count}")
```

## Getting a Dataset

```python
async with HoneycombClient(api_key="...") as client:
    dataset = await client.datasets.get_async("my-dataset-slug")
    print(f"Created: {dataset.created_at}")
    print(f"Last written: {dataset.last_written_at}")
```

## Creating a Dataset

```python
from honeycomb import HoneycombClient, DatasetCreate

async with HoneycombClient(api_key="...") as client:
    dataset = await client.datasets.create_async(
        DatasetCreate(
            name="My New Dataset",
            description="For production logs",
            expand_json_depth=2,
        )
    )
    print(f"Created dataset: {dataset.slug}")
```

## Updating a Dataset

```python
async with HoneycombClient(api_key="...") as client:
    updated = await client.datasets.update_async(
        "my-dataset",
        DatasetCreate(
            name="Updated Name",
            description="Updated description",
        )
    )
```

## Deleting a Dataset

!!! danger "Permanent Deletion"
    Deleting a dataset is permanent and cannot be undone!

```python
async with HoneycombClient(api_key="...") as client:
    await client.datasets.delete_async("dataset-to-delete")
    print("Dataset deleted")
```

## See Also

- [Datasets API Reference](../api/resources.md#datasets)
- [Dataset Models](../api/models.md#dataset-models)

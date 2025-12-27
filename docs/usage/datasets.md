# Working with Datasets

Datasets are collections of events in Honeycomb. This guide shows how to manage them.

## Listing Datasets

```python
{%
   include "../examples/datasets/basic_dataset.py"
   start="# start_example:list_datasets"
   end="# end_example:list_datasets"
%}
```

## Getting a Dataset

```python
{%
   include "../examples/datasets/basic_dataset.py"
   start="# start_example:get_dataset"
   end="# end_example:get_dataset"
%}
```

## Creating a Dataset

```python
{%
   include "../examples/datasets/basic_dataset.py"
   start="# start_example:create_dataset"
   end="# end_example:create_dataset"
%}
```

## Updating a Dataset

```python
{%
   include "../examples/datasets/basic_dataset.py"
   start="# start_example:update_dataset"
   end="# end_example:update_dataset"
%}
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

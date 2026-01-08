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

## Delete Protection

Datasets can be protected from accidental deletion. Use the `set_delete_protected` method or include `delete_protected` in an update:

```python
{%
   include "../examples/datasets/basic_dataset.py"
   start="# start_example:delete_protection"
   end="# end_example:delete_protection"
%}
```

You can also check if a dataset is protected:

```python
async with HoneycombClient(api_key="...") as client:
    dataset = await client.datasets.get_async("my-dataset")
    print(f"Delete protected: {dataset.delete_protected}")
```

## Deleting a Dataset

!!! danger "Permanent Deletion"
    Deleting a dataset is permanent and cannot be undone!

!!! warning "Delete Protection"
    Datasets with delete protection enabled cannot be deleted. You must first disable delete protection using `set_delete_protected(slug, protected=False)`.

```python
async with HoneycombClient(api_key="...") as client:
    # First, disable delete protection if enabled
    await client.datasets.set_delete_protected_async("dataset-to-delete", protected=False)
    # Then delete
    await client.datasets.delete_async("dataset-to-delete")
    print("Dataset deleted")
```

## See Also

- [Datasets API Reference](../api/resources.md#datasets)
- [Dataset Models](../api/models.md#dataset-models)

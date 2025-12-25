# Working with Columns

Columns define the schema of your datasets and control how fields are displayed and queried in the Honeycomb UI.

## Basic Column Operations

### List Columns

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    columns = await client.columns.list_async("my-dataset")

    for column in columns:
        print(f"{column.key_name}: {column.type.value}")
        if column.hidden:
            print("  (hidden)")
```

### Get a Specific Column

```python
column = await client.columns.get_async("my-dataset", "column-id")

print(f"Name: {column.key_name}")
print(f"Type: {column.type}")
print(f"Description: {column.description}")
print(f"Last written: {column.last_written}")
```

### Delete a Column

```python
await client.columns.delete_async("my-dataset", "column-id")
```

## Creating Columns

### Basic Column

```python
from honeycomb import HoneycombClient, ColumnCreate, ColumnType

async with HoneycombClient(api_key="...") as client:
    column = await client.columns.create_async(
        "my-dataset",
        ColumnCreate(
            key_name="response_time_ms",
            type=ColumnType.FLOAT,
            description="API response time in milliseconds",
        )
    )
    print(f"Created column: {column.id}")
```

### Hidden Column

Hidden columns are excluded from autocomplete and raw data field lists:

```python
column = await client.columns.create_async(
    "my-dataset",
    ColumnCreate(
        key_name="internal_trace_id",
        type=ColumnType.STRING,
        description="Internal tracing identifier",
        hidden=True,  # Don't show in UI autocomplete
    )
)
```

## Updating Columns

```python
updated_column = await client.columns.update_async(
    "my-dataset",
    "column-id",
    ColumnCreate(
        key_name="response_time_ms",
        type=ColumnType.FLOAT,
        description="Updated: API response time in milliseconds",
        hidden=False,
    )
)
```

## Column Types

Available column types:

- `ColumnType.STRING` - Text data (default)
- `ColumnType.INTEGER` - Whole numbers
- `ColumnType.FLOAT` - Decimal numbers
- `ColumnType.BOOLEAN` - True/false values

```python
from honeycomb import ColumnType

# Integer column for counts
count_column = ColumnCreate(
    key_name="retry_count",
    type=ColumnType.INTEGER,
    description="Number of retry attempts"
)

# Boolean column for flags
flag_column = ColumnCreate(
    key_name="is_error",
    type=ColumnType.BOOLEAN,
    description="Whether request resulted in error"
)
```

## Sync Usage

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List columns
    columns = client.columns.list("my-dataset")

    # Create column
    column = client.columns.create(
        "my-dataset",
        ColumnCreate(key_name="new_field", type=ColumnType.STRING)
    )

    # Delete column
    client.columns.delete("my-dataset", "column-id")
```

## Best Practices

1. **Choose Appropriate Types**: Use the correct type for your data to enable proper aggregations
2. **Add Descriptions**: Help your team understand what each column represents
3. **Use Hidden Wisely**: Hide internal fields that shouldn't clutter the UI
4. **Manage Schema Changes**: Coordinate column changes across your team

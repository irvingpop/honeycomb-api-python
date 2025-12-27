# Working with Derived Columns

Derived columns (also called calculated fields) are virtual columns computed from expressions at query time. They allow you to create new fields from existing data without modifying the underlying events.

## Basic Operations

### List Derived Columns

=== "Async"

    ```python
    {%
       include "../examples/derived_columns/list_columns.py"
       start="# start_example:list_async"
       end="# end_example:list_async"
    %}
    ```

=== "Sync"

    ```python
    {%
       include "../examples/derived_columns/list_columns.py"
       start="# start_example:list_sync"
       end="# end_example:list_sync"
    %}
    ```

### Get a Specific Derived Column

```python
dc = await client.derived_columns.get_async("dataset-slug", "column-id")

print(f"Alias: {dc.alias}")
print(f"Expression: {dc.expression}")
```

### Delete a Derived Column

```python
await client.derived_columns.delete_async("dataset-slug", "column-id")
```

## Creating Derived Columns

### Simple Expression with DerivedColumnBuilder

```python
{%
   include "../examples/derived_columns/basic_derived_column.py"
   start="# start_example:simple_with_builder"
   end="# end_example:simple_with_builder"
%}
```

### IF Expression

```python
{%
   include "../examples/derived_columns/basic_derived_column.py"
   start="# start_example:if_expression_builder"
   end="# end_example:if_expression_builder"
%}
```

### Manual Construction

```python
{%
   include "../examples/derived_columns/basic_derived_column.py"
   start="# start_example:manual_construction"
   end="# end_example:manual_construction"
%}
```

## Environment-Wide Derived Columns

Environment-wide derived columns are available across all datasets in your environment. Use `"__all__"` as the dataset slug.

### Create Environment-Wide Column

```python
{%
   include "../examples/derived_columns/environment_wide.py"
   start="# start_example:env_wide_create"
   end="# end_example:env_wide_create"
%}
```

### List Environment-Wide Columns

```python
{%
   include "../examples/derived_columns/environment_wide.py"
   start="# start_example:env_wide_list"
   end="# end_example:env_wide_list"
%}
```

## Expression Functions

Derived column expressions support various functions:

| Function | Description | Example |
|----------|-------------|---------|
| `EXISTS($field)` | Check if field exists | `EXISTS($trace.trace_id)` |
| `IF(cond, then, else)` | Conditional expression | `IF(LT($status, 400), 1, 0)` |
| `LT($a, $b)` | Less than | `LT($status_code, 400)` |
| `GT($a, $b)` | Greater than | `GT($duration_ms, 1000)` |
| `EQUALS($a, $b)` | Equality check | `EQUALS($service, "api")` |
| `CONCAT($a, $b)` | String concatenation | `CONCAT($method, " ", $path)` |
| `COALESCE($a, $b)` | First non-null value | `COALESCE($user_id, "anonymous")` |
| `REG_VALUE($field, regex)` | Regex extraction | `REG_VALUE($path, "^/api/(.+)")` |

## DerivedColumnBuilder Methods

| Method | Description |
|--------|-------------|
| `DerivedColumnBuilder(alias)` | Create builder with column alias |
| `.expression(expr)` | Set the expression |
| `.description(desc)` | Set optional description |
| `.build()` | Build the DerivedColumnCreate object |

## Updating Derived Columns

```python
from honeycomb import DerivedColumnCreate

updated = await client.derived_columns.update_async(
    "dataset-slug",
    "column-id",
    DerivedColumnCreate(
        alias="updated_column_name",
        expression="IF(GT($duration_ms, 500), 1, 0)",
        description="Updated expression"
    )
)
```

## Use Cases

### SLI for SLOs

Derived columns are commonly used to define Service Level Indicators:

```python
# Define success/failure for SLO
sli_column = (
    DerivedColumnBuilder("request_success")
    .expression("IF(LT($status_code, 500), 1, 0)")
    .description("1 for successful requests, 0 for server errors")
    .build()
)

await client.derived_columns.create_async("api-logs", sli_column)
```

### Latency Bucketing

```python
# Categorize latency into buckets
latency_bucket = (
    DerivedColumnBuilder("latency_bucket")
    .expression(
        "IF(LT($duration_ms, 100), 'fast', "
        "IF(LT($duration_ms, 500), 'normal', 'slow'))"
    )
    .description("Categorize requests by latency")
    .build()
)

await client.derived_columns.create_async("api-logs", latency_bucket)
```

## Best Practices

1. **Use descriptive aliases**: Make column names self-explanatory
2. **Document expressions**: Add descriptions explaining what the column calculates
3. **Test expressions**: Verify expressions work before using in production SLOs
4. **Environment-wide for shared logic**: Use environment-wide columns for cross-dataset consistency
5. **Keep expressions simple**: Complex expressions are harder to debug

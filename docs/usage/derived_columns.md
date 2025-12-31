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

## Expression Syntax Fundamentals

Understanding the syntax rules is essential for writing valid expressions.

### Column References

- **Basic**: Prefix column names with `$` - e.g., `$status_code`, `$duration_ms`
- **With spaces/special chars**: Use quotes - e.g., `$"http.status_code"`, `$"user name"`
- **Case sensitive**: `$Status` and `$status` are different columns

### Literals and Quoting

| Type | Syntax | Example |
|------|--------|---------|
| Strings | Double quotes `"..."` | `"error"`, `"GET"` |
| Regex patterns | Backticks `` `...` `` | `` `^/api/v[0-9]+` `` |
| Numbers | Plain | `200`, `1000.5` |
| Booleans | `true`, `false` | Used in comparisons |

### Key Concepts

!!! warning "Single-Row Operation"
    Derived columns operate on **one event at a time**. They are NOT aggregation functions.
    You cannot reference other events or compute across multiple rows.

!!! info "SLI Expressions for SLOs"
    SLI (Service Level Indicator) expressions **must return a boolean** (true/false).
    Values 1/0 are automatically coerced to true/false.
    Example: `LT($status_code, 500)` or `IF(LT($status_code, 500), true, false)`

## Expression Functions Reference

### Conditional Functions

| Function | Description | Example |
|----------|-------------|---------|
| `IF(cond, then, else)` | Conditional expression | `IF(LT($status, 400), "ok", "error")` |
| `SWITCH($field, case1, val1, ..., default)` | Match against string cases | `SWITCH($method, "GET", 1, "POST", 2, 0)` |
| `COALESCE(a, b, ...)` | First non-null value | `COALESCE($user_id, $session_id, "anonymous")` |

### Comparison Functions

All comparison functions return boolean values.

| Function | Description | Example |
|----------|-------------|---------|
| `LT($a, $b)` | Less than | `LT($status_code, 400)` |
| `LTE($a, $b)` | Less than or equal | `LTE($duration_ms, 100)` |
| `GT($a, $b)` | Greater than | `GT($duration_ms, 1000)` |
| `GTE($a, $b)` | Greater than or equal | `GTE($error_count, 1)` |
| `EQUALS($a, $b)` | Equality check | `EQUALS($method, "GET")` |
| `IN($field, val1, val2, ...)` | Value in set | `IN($status, 200, 201, 204)` |

### Boolean Functions

| Function | Description | Example |
|----------|-------------|---------|
| `EXISTS($field)` | True if field is non-null | `EXISTS($trace.parent_id)` |
| `NOT(cond)` | Logical negation | `NOT(EXISTS($error))` |
| `AND(a, b, ...)` | All conditions true | `AND(GT($status, 199), LT($status, 300))` |
| `OR(a, b, ...)` | Any condition true | `OR(EQUALS($level, "error"), EQUALS($level, "fatal"))` |

### Math Functions

| Function | Description | Example |
|----------|-------------|---------|
| `SUM(a, b, ...)` | Add values | `SUM($request_time, $queue_time)` |
| `SUB(a, b)` | Subtract | `SUB($end_time, $start_time)` |
| `MUL(a, b)` | Multiply | `MUL($duration_ms, 0.001)` |
| `DIV(a, b)` | Divide | `DIV($bytes, 1024)` |
| `MOD(a, b)` | Modulo | `MOD($request_id, 100)` |
| `MIN(a, b, ...)` | Minimum value | `MIN($timeout, $max_wait)` |
| `MAX(a, b, ...)` | Maximum value | `MAX($retries, 0)` |
| `LOG10(a)` | Base-10 logarithm | `LOG10($request_count)` |

### String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `CONCAT(a, b, ...)` | Join strings | `CONCAT($method, " ", $path)` |
| `STARTS_WITH($str, prefix)` | Check prefix (returns bool) | `STARTS_WITH($path, "/api/")` |
| `ENDS_WITH($str, suffix)` | Check suffix (returns bool) | `ENDS_WITH($filename, ".json")` |
| `CONTAINS($str, substr)` | Check contains (returns bool) | `CONTAINS($error, "timeout")` |
| `TO_LOWER($str)` | Convert to lowercase | `TO_LOWER($method)` |
| `LENGTH($str)` | String length | `LENGTH($message)` |

### Regular Expression Functions

!!! tip "Use backticks for regex patterns"
    Regex patterns use backticks, not quotes: `` `pattern` `` not `"pattern"`

| Function | Description | Example |
|----------|-------------|---------|
| `REG_MATCH($str, pattern)` | Test if pattern matches (bool) | ``REG_MATCH($path, `/api/v[0-9]+`)`` |
| `REG_VALUE($str, pattern)` | Extract first capture group | ``REG_VALUE($path, `/api/([^/]+)`)`` |
| `REG_COUNT($str, pattern)` | Count pattern matches | ``REG_COUNT($log, `error`)`` |

### Time Functions

| Function | Description | Example |
|----------|-------------|---------|
| `EVENT_TIMESTAMP()` | Event time as Unix timestamp | `EVENT_TIMESTAMP()` |
| `UNIX_TIMESTAMP($field)` | Parse field as timestamp | `UNIX_TIMESTAMP($created_at)` |
| `FORMAT_TIME(format, $ts)` | Format with strftime | `FORMAT_TIME("%Y-%m-%d", EVENT_TIMESTAMP())` |

### Data Transformation

| Function | Description | Example |
|----------|-------------|---------|
| `BUCKET($val, size)` | Numeric bucketing | `BUCKET($duration_ms, 100)` |

### Type Conversion

| Function | Description | Example |
|----------|-------------|---------|
| `INT($val)` | Convert to integer | `INT($string_id)` |
| `FLOAT($val)` | Convert to float | `FLOAT($count)` |
| `BOOL($val)` | Convert to boolean | `BOOL($enabled)` |
| `STRING($val)` | Convert to string | `STRING($status_code)` |

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

Derived columns are commonly used to define Service Level Indicators.

!!! warning "SLI Must Return Boolean"
    SLI expressions for SLOs must evaluate to true (good) or false (bad) for each event.
    Values 1/0 are automatically coerced to true/false.

```python
# Define success/failure for SLO - comparison functions return boolean directly
sli_column = (
    DerivedColumnBuilder("request_success")
    .expression("LT($status_code, 500)")
    .description("true for successful requests, false for server errors")
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
        'IF(LT($duration_ms, 100), "fast", '
        'IF(LT($duration_ms, 500), "normal", "slow"))'
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
6. **Use correct quoting**: Strings use `"..."`, regex patterns use `` `...` ``
7. **Remember case sensitivity**: Column names are case-sensitive (`$Status` != `$status`)

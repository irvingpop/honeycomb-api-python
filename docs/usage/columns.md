# Working with Columns

Columns define the schema of your datasets and control how fields are displayed and queried in the Honeycomb UI.

## Basic Column Operations

### List Columns

```python
{%
   include "../examples/columns/basic_column.py"
   start="# start_example:list_columns"
   end="# end_example:list_columns"
%}
```

### Get a Specific Column

```python
{%
   include "../examples/columns/basic_column.py"
   start="# start_example:get"
   end="# end_example:get"
%}
```

### Delete a Column

```python
{%
   include "../examples/columns/basic_column.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Creating Columns

### Basic Column

```python
{%
   include "../examples/columns/basic_column.py"
   start="# start_example:create_column"
   end="# end_example:create_column"
%}
```

### Hidden Column

Hidden columns are excluded from autocomplete and raw data field lists:

```python
{%
   include "../examples/columns/basic_column.py"
   start="# start_example:create_hidden_column"
   end="# end_example:create_hidden_column"
%}
```

## Updating Columns

```python
{%
   include "../examples/columns/basic_column.py"
   start="# start_example:update"
   end="# end_example:update"
%}
```

## Column Types

Available column types:

- `ColumnType.STRING` - Text data (default)
- `ColumnType.INTEGER` - Whole numbers
- `ColumnType.FLOAT` - Decimal numbers
- `ColumnType.BOOLEAN` - True/false values

## Sync Usage

All column operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    columns = client.columns.list("my-dataset")
    column = client.columns.create("my-dataset", ColumnCreate(...))
    column = client.columns.get("my-dataset", column_id)
    updated = client.columns.update("my-dataset", column_id, ColumnCreate(...))
    client.columns.delete("my-dataset", column_id)
```

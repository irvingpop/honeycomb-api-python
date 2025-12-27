# Working with Boards

Boards are visualization dashboards in Honeycomb. They organize multiple queries and visualizations in one place for monitoring and analysis.

## Basic Board Operations

### List Boards

```python
{%
   include "../examples/boards/basic_board.py"
   start="# start_example:list_boards"
   end="# end_example:list_boards"
%}
```

### Get a Specific Board

```python
{%
   include "../examples/boards/basic_board.py"
   start="# start_example:get"
   end="# end_example:get"
%}
```

### Update a Board

```python
{%
   include "../examples/boards/basic_board.py"
   start="# start_example:update"
   end="# end_example:update"
%}
```

### Delete a Board

```python
{%
   include "../examples/boards/basic_board.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Creating Boards with BoardBuilder

`BoardBuilder` provides a fluent interface for creating boards with inline `QueryBuilder` instances or existing query IDs. Single fluent call creates queries, annotations, and boards automatically.

### Simple Example - Inline QueryBuilder with Auto-Layout

```python
{%
   include "../examples/boards/builder_board.py"
   start="# start_example:create_with_builder"
   end="# end_example:create_with_builder"
%}
```

**Key Points:**
- Use `QueryBuilder` instances directly in `.query()` calls - no need to create queries separately
- Pass name in constructor: `QueryBuilder("Query Name")` (required for board integration)
- `create_from_bundle_async()` handles query creation + annotation + board in one call

### Complex Example - Full Featured Dashboard

This example demonstrates all capabilities: inline QueryBuilder instances, SLO panels, text panels, visualization settings, preset filters, and manual layout with tuple positioning.

```python
{%
   include "../examples/boards/builder_board.py"
   start="# start_example:create_complex"
   end="# end_example:create_complex"
%}
```

## BoardBuilder Reference

### Layout Configuration

| Method | Description |
|--------|-------------|
| `.auto_layout()` | Use automatic panel positioning (positions optional) |
| `.manual_layout()` | Use manual positioning (positions required for all panels) |

### Panel Methods

| Method | Description |
|--------|-------------|
| `.query(QueryBuilder, ...)` | Add query panel with inline QueryBuilder instance |
| `.query(query_id, annotation_id, ...)` | Add query panel from existing query ID |
| `.slo(slo_id, ...)` | Add an SLO panel |
| `.text(content, ...)` | Add a text panel with markdown content |

### Query Panel Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `QueryBuilder \| str` | QueryBuilder instance with name OR existing query ID |
| `annotation_id` | `str \| None` | Required only when using existing query ID |
| `position` | `tuple[int, int, int, int] \| None` | Optional (x, y, width, height) for manual layout |
| `style` | `"graph" \| "table" \| "combo"` | Display style (default: "graph") |
| `dataset` | `str \| None` | Override QueryBuilder's dataset (rare) |
| `visualization` | `dict \| None` | Advanced visualization configuration |

### Positioning for Manual Layout

For manual layout, use tuples `(x, y, width, height)`:

```python
from honeycomb import BoardBuilder, QueryBuilder

# Position format: (x, y, width, height)
bundle = (
    BoardBuilder("Dashboard")
    .manual_layout()
    .query(
        QueryBuilder("Requests").dataset("api-logs").last_1_hour().count(),
        position=(0, 0, 9, 6),  # Top left, large
    )
    .slo("slo-id", position=(9, 0, 3, 6))  # Top right, small
    .text("Notes", position=(0, 6, 12, 2))  # Bottom, full width
    .build()
)
```

### Preset Filter Methods

| Method | Description |
|--------|-------------|
| `.preset_filter(column, alias)` | Add a dynamic filter for a column with display name |

### Tag Methods (from TagsMixin)

See [Triggers documentation](triggers.md) for full details on tag methods:
- `.tag(key, value)` - Add a single tag
- `.tags(dict)` - Add multiple tags from dictionary

## Creating Boards Manually

For simple cases without panels:

```python
{%
   include "../examples/boards/basic_board.py"
   start="# start_example:create_board"
   end="# end_example:create_board"
%}
```

## Sync Usage

All board operations have sync equivalents. Use `sync=True` when creating the client:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List boards
    boards = client.boards.list()

    # Create board
    board = client.boards.create(BoardCreate(name="My Board", type="flexible"))

    # Get board
    board = client.boards.get(board_id)

    # Update board
    updated = client.boards.update(board_id, BoardCreate(name="Updated", type="flexible"))

    # Delete board
    client.boards.delete(board_id)
```

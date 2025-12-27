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

`BoardBuilder` provides a fluent interface for creating boards with query panels, SLO panels, and text panels. It supports both auto-layout and manual positioning, along with tags, preset filters, and advanced visualization settings.

### Simple Example - Multiple Queries with Auto-Layout

```python
{%
   include "../examples/boards/builder_board.py"
   start="# start_example:create_with_builder"
   end="# end_example:create_with_builder"
%}
```

### Complex Example - Full Featured Dashboard

This example demonstrates all BoardBuilder capabilities including queries, SLOs, text panels, visualization settings, preset filters, and manual layout.

**Note:** This example creates queries programmatically and accesses `query_annotation_id` from the API response. In practice, you'll typically create queries via the UI or separately, then reference them by ID when building boards.

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
| `.query(query_id, annotation_id, ...)` | Add a saved query panel |
| `.slo(slo_id, ...)` | Add an SLO panel |
| `.text(content, ...)` | Add a text panel with markdown content |

### Query Panel Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `position` | `BoardPanelPosition \| None` | Optional position and size |
| `style` | `"graph" \| "table" \| "combo"` | Display style (default: "graph") |
| `dataset` | `str \| None` | Optional dataset name |
| `visualization_settings` | `dict \| None` | Advanced visualization configuration |

### BoardPanelPosition

Create position objects for manual layout:

```python
from honeycomb import BoardPanelPosition

position = BoardPanelPosition(
    x_coordinate=0,  # X position (grid-based)
    y_coordinate=0,  # Y position (grid-based)
    width=8,         # Width in grid units (0 = auto)
    height=6,        # Height in grid units (0 = auto)
)
```

### Preset Filter Methods

| Method | Description |
|--------|-------------|
| `.preset_filter(column, alias)` | Add a dynamic filter for a column with display name |

### Tag Methods (from TagsMixin)

See [Triggers documentation](triggers.md#tags-reference) for full details on tag methods:
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

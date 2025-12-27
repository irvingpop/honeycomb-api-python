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

## Creating Boards

```python
{%
   include "../examples/boards/basic_board.py"
   start="# start_example:create_board"
   end="# end_example:create_board"
%}
```

**Note:** The Board API has been updated to use `type="flexible"` instead of the deprecated `column_layout` and `style` fields. Adding queries to boards is typically done through the Honeycomb UI rather than the API.

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

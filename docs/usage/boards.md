# Working with Boards

Boards are visualization dashboards in Honeycomb. They organize multiple queries and visualizations in one place for monitoring and analysis.

## Basic Board Operations

### List Boards

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    boards = await client.boards.list_async()

    for board in boards:
        print(f"{board.name}")
        print(f"  Layout: {board.column_layout}")
        print(f"  Style: {board.style}")
        if board.queries:
            print(f"  Queries: {len(board.queries)}")
```

### Get a Specific Board

```python
board = await client.boards.get_async("board-id")

print(f"Name: {board.name}")
print(f"Description: {board.description}")
print(f"Layout: {board.column_layout}")
print(f"Style: {board.style}")
```

### Delete a Board

```python
await client.boards.delete_async("board-id")
```

## Creating Boards

### Basic Board

```python
from honeycomb import HoneycombClient, BoardCreate

async with HoneycombClient(api_key="...") as client:
    board = await client.boards.create_async(
        BoardCreate(
            name="Service Overview",
            description="Key metrics for the API service",
            column_layout="multi",
            style="visual",
        )
    )
    print(f"Created board: {board.id}")
```

### Board Configuration Options

#### Column Layout

The `column_layout` controls how queries are arranged:

```python
# Multiple columns (default)
column_layout="multi"

# Single column layout
column_layout="single"
```

#### Style

The `style` controls the visualization format:

```python
# Visual charts and graphs (default)
style="visual"

# List/table format
style="list"
```

## Board Examples

### Service Health Dashboard

```python
board = await client.boards.create_async(
    BoardCreate(
        name="API Service Health",
        description="Real-time monitoring for API endpoints",
        column_layout="multi",
        style="visual",
    )
)
```

### Single Column Report

```python
board = await client.boards.create_async(
    BoardCreate(
        name="Daily Metrics Report",
        description="Top-to-bottom metrics summary",
        column_layout="single",
        style="visual",
    )
)
```

### List-Based Dashboard

```python
board = await client.boards.create_async(
    BoardCreate(
        name="Error Log Summary",
        description="List view of recent errors",
        column_layout="multi",
        style="list",
    )
)
```

## Updating Boards

When updating a board, you must provide all fields:

```python
# Get the existing board first
existing = await client.boards.get_async("board-id")

# Update with all fields
updated = await client.boards.update_async(
    "board-id",
    BoardCreate(
        name="Updated Service Overview",  # New name
        description=existing.description,  # Keep existing
        column_layout="single",            # Change layout
        style=existing.style,              # Keep existing style
    )
)
```

## Working with Board Queries

The API returns board configuration including queries, but **adding queries to boards is typically done through the Honeycomb UI** rather than the API. When you fetch a board, you'll see its queries in the response:

```python
board = await client.boards.get_async("board-id")

if board.queries:
    print(f"This board has {len(board.queries)} queries")
    for query in board.queries:
        # Query details vary by board configuration
        print(query)
```

## Common Board Patterns

### Service Overview Boards

Organize key metrics for a service:

```python
board = await client.boards.create_async(
    BoardCreate(
        name="API Service - Production",
        description="Request rate, errors, latency for production API",
        column_layout="multi",
        style="visual",
    )
)
```

### Team Dashboards

Create team-specific monitoring views:

```python
board = await client.boards.create_async(
    BoardCreate(
        name="Platform Team Dashboard",
        description="Infrastructure and platform metrics",
        column_layout="multi",
        style="visual",
    )
)
```

### Incident Investigation Boards

Temporary boards for debugging:

```python
board = await client.boards.create_async(
    BoardCreate(
        name="INC-1234 Investigation",
        description="Queries related to the payment gateway incident",
        column_layout="single",  # Focus on one thing at a time
        style="visual",
    )
)
```

### Executive Summaries

High-level overviews:

```python
board = await client.boards.create_async(
    BoardCreate(
        name="Executive Overview - Q1 2025",
        description="Top-level SLO and reliability metrics",
        column_layout="multi",
        style="visual",
    )
)
```

## Board Organization Tips

### Use Clear Naming Conventions

```python
# Good: Descriptive and hierarchical
name="Production - API Service - Overview"
name="Staging - Payment Service - Errors"
name="[Team: Platform] Infrastructure Metrics"

# Less helpful: Too vague
name="Dashboard 1"
name="Monitoring"
```

### Include Context in Descriptions

```python
# Good
description="Real-time monitoring for the API service. Includes request rates, error rates, P99 latency, and top endpoints. Updated every 60s."

# Less helpful
description="API metrics"
```

### Choose Layout Based on Content

```python
# Multi-column: Good for 4-6+ queries that you want to compare side-by-side
column_layout="multi"

# Single-column: Good for 1-3 queries or when you want to focus on one metric at a time
column_layout="single"
```

### Choose Style Based on Use Case

```python
# Visual style: Good for time-series data, trends, and patterns
style="visual"

# List style: Good for logs, error messages, and tabular data
style="list"
```

## Managing Multiple Boards

You can organize boards by environment, team, or purpose:

```python
# Environment-based
await client.boards.create_async(BoardCreate(
    name="Production - Overview",
    column_layout="multi",
    style="visual"
))
await client.boards.create_async(BoardCreate(
    name="Staging - Overview",
    column_layout="multi",
    style="visual"
))

# Team-based
await client.boards.create_async(BoardCreate(
    name="[Backend Team] Services",
    column_layout="multi",
    style="visual"
))
await client.boards.create_async(BoardCreate(
    name="[Frontend Team] User Flows",
    column_layout="multi",
    style="visual"
))

# Purpose-based
await client.boards.create_async(BoardCreate(
    name="SLO Tracking",
    column_layout="multi",
    style="visual"
))
await client.boards.create_async(BoardCreate(
    name="Cost Analysis",
    column_layout="multi",
    style="visual"
))
await client.boards.create_async(BoardCreate(
    name="Security Events",
    column_layout="multi",
    style="visual"
))
```

## See Also

- [Boards API Reference](../api/resources.md#boards) - Full API documentation
- [Board Models](../api/models.md#board-models) - All board model fields
- [Queries Guide](queries.md) - Create queries to add to your boards

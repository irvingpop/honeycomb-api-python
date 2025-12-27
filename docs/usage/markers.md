# Working with Markers

Markers annotate your data with events like deployments, configuration changes, or other significant occurrences. They appear as vertical lines on your graphs.

## Basic Marker Operations

### List Markers

```python
{%
   include "../examples/markers/basic_marker.py"
   start="# start_example:list_markers"
   end="# end_example:list_markers"
%}
```

### Update a Marker

```python
{%
   include "../examples/markers/basic_marker.py"
   start="# start_example:update"
   end="# end_example:update"
%}
```

### Delete a Marker

```python
{%
   include "../examples/markers/basic_marker.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Creating Markers with MarkerBuilder

`MarkerBuilder` provides a fluent interface for creating markers with convenient helpers for time configuration and common patterns.

```python
{%
   include "../examples/markers/builder_marker.py"
   start="# start_example:create_with_builder"
   end="# end_example:create_with_builder"
%}
```

## MarkerBuilder Reference

### Basic Configuration

| Method | Description |
|--------|-------------|
| `.type(marker_type)` | Set marker type (required) - groups similar markers |
| `.url(url)` | Set target URL (optional) - link to PR, build, incident |

### Time Configuration

| Method | Description |
|--------|-------------|
| `.start_time(timestamp)` | Set start time as Unix timestamp |
| `.end_time(timestamp)` | Set end time as Unix timestamp (for duration markers) |
| `.duration_minutes(minutes)` | Set duration from now in minutes |
| `.duration_hours(hours)` | Set duration from now in hours |

### Static Methods

| Method | Description |
|--------|-------------|
| `MarkerBuilder.setting(type, color)` | Create marker setting (color configuration) |

### Marker Types

Common marker type conventions:

- `deploy` - Deployments and releases
- `maintenance` - Planned maintenance windows
- `incident` - Incidents and outages
- `config-change` - Configuration changes
- `feature-flag` - Feature flag toggles

## Creating Markers Manually

For simple cases or when you need fine-grained control:

```python
{%
   include "../examples/markers/basic_marker.py"
   start="# start_example:create_marker"
   end="# end_example:create_marker"
%}
```

### Additional Options

Markers support several optional fields:

- **url**: Link to PR, build info, or runbook
- **end_time**: For events with duration (e.g., rollouts, maintenance)
- **dataset**: Use `"__all__"` to create environment-wide markers visible across all datasets

### Marker Settings

Customize marker colors by type using the marker settings API. All CRUD operations are available:

- `list_settings_async()` / `list_settings()` - List all marker settings
- `get_setting_async()` / `get_setting()` - Get a specific setting by ID
- `create_setting_async()` / `create_setting()` - Create a new marker type with color
- `update_setting_async()` / `update_setting()` - Update an existing setting
- `delete_setting_async()` / `delete_setting()` - Delete a setting

## Sync Usage

All marker operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List markers
    markers = client.markers.list("my-dataset")

    # Create marker
    marker = client.markers.create(
        "my-dataset",
        MarkerCreate(message="Deploy v1.0", type="deploy", start_time=int(time.time()))
    )

    # Update marker
    updated = client.markers.update("my-dataset", marker_id, MarkerCreate(...))

    # Delete marker
    client.markers.delete("my-dataset", marker_id)

    # Marker settings
    settings = client.markers.list_settings("my-dataset")
```

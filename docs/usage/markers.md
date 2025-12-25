# Working with Markers

Markers annotate your data with events like deployments, configuration changes, or other significant occurrences. They appear as vertical lines on your graphs.

## Basic Marker Operations

### List Markers

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    markers = await client.markers.list_async("my-dataset")

    for marker in markers:
        print(f"{marker.type}: {marker.message}")
        print(f"  Time: {marker.start_time}")
        if marker.url:
            print(f"  URL: {marker.url}")
```

### Delete a Marker

```python
await client.markers.delete_async("my-dataset", "marker-id")
```

## Creating Markers

### Basic Marker

```python
from honeycomb import HoneycombClient, MarkerCreate
import time

async with HoneycombClient(api_key="...") as client:
    marker = await client.markers.create_async(
        "my-dataset",
        MarkerCreate(
            message="Backend deploy v2.5.0",
            type="deploy",
            start_time=int(time.time()),
        )
    )
    print(f"Created marker: {marker.id}")
```

### Marker with Time Range

For events that span a period (like a gradual rollout):

```python
import time

start = int(time.time())
end = start + 300  # 5 minutes later

marker = await client.markers.create_async(
    "my-dataset",
    MarkerCreate(
        message="Gradual rollout: v2.5.0",
        type="deploy",
        start_time=start,
        end_time=end,
    )
)
```

### Marker with URL

Link to build info, PR, or runbook:

```python
marker = await client.markers.create_async(
    "my-dataset",
    MarkerCreate(
        message="Hotfix: Fix memory leak",
        type="deploy",
        url="https://github.com/myorg/myrepo/pull/1234",
    )
)
```

### Environment-Wide Markers

Use `__all__` as the dataset to create markers visible across all datasets:

```python
marker = await client.markers.create_async(
    "__all__",  # All datasets in this environment
    MarkerCreate(
        message="Database maintenance window",
        type="maintenance",
        start_time=int(time.time()),
    )
)
```

## Updating Markers

```python
updated_marker = await client.markers.update_async(
    "my-dataset",
    "marker-id",
    MarkerCreate(
        message="Updated: Backend deploy v2.5.1",
        type="deploy",
    )
)
```

## Marker Settings

Customize marker colors by type:

### List Marker Settings

```python
settings = await client.markers.list_settings_async("my-dataset")

for setting in settings:
    print(f"{setting.type}: {setting.color}")
```

### Get a Specific Marker Setting

```python
setting = await client.markers.get_setting_async("my-dataset", "setting-id")
print(f"Type: {setting.type}, Color: {setting.color}")
```

### Create Marker Setting

```python
from honeycomb import MarkerSettingCreate

setting = await client.markers.create_setting_async(
    "my-dataset",
    MarkerSettingCreate(
        type="deploy",
        color="#00FF00",  # Green for deployments
    )
)
```

### Update Marker Setting

```python
updated_setting = await client.markers.update_setting_async(
    "my-dataset",
    "setting-id",
    MarkerSettingCreate(
        type="deploy",
        color="#0099FF",  # Change to blue
    )
)
```

### Delete Marker Setting

```python
await client.markers.delete_setting_async("my-dataset", "setting-id")
```

## Sync Usage

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List markers
    markers = client.markers.list("my-dataset")

    # Create marker
    marker = client.markers.create(
        "my-dataset",
        MarkerCreate(message="Deploy", type="deploy")
    )

    # Manage settings
    settings = client.markers.list_settings("my-dataset")
    setting = client.markers.create_setting(
        "my-dataset",
        MarkerSettingCreate(type="deploy", color="#FF0000")
    )
```

## Common Marker Types

Recommended marker types and colors:

| Type | Color | Use Case |
|------|-------|----------|
| `deploy` | `#0099FF` | Code deployments |
| `config` | `#FF9900` | Configuration changes |
| `incident` | `#FF0000` | Incidents or outages |
| `maintenance` | `#9966FF` | Planned maintenance |
| `release` | `#00CC66` | Feature releases |

```python
# Example: Create consistent marker types
marker_types = [
    ("deploy", "#0099FF"),
    ("config", "#FF9900"),
    ("incident", "#FF0000"),
    ("maintenance", "#9966FF"),
    ("release", "#00CC66"),
]

for type_name, color in marker_types:
    await client.markers.create_setting_async(
        "my-dataset",
        MarkerSettingCreate(type=type_name, color=color)
    )
```

## Best Practices

1. **Use Consistent Types**: Establish standard marker types across your organization
2. **Configure Colors**: Set up marker settings to visually distinguish event types
3. **Include URLs**: Link to relevant documentation, PRs, or incident reports
4. **Time Ranges**: Use start/end times for events with duration
5. **Environment Markers**: Use `__all__` for org-wide events like maintenance windows

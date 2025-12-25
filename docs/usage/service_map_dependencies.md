# Service Map Dependencies

Service Map Dependencies allow you to query the relationships between services in your distributed system based on trace data. This is useful for understanding service topology, identifying dependencies, and visualizing how services communicate.

## Basic Usage

```python
from honeycomb import HoneycombClient
from honeycomb.models import ServiceMapDependencyRequestCreate

# Get dependencies for the last 2 hours (default)
async with HoneycombClient(api_key="your-api-key") as client:
    result = await client.service_map_dependencies.get_async(
        request=ServiceMapDependencyRequestCreate()
    )

    for dep in result.dependencies or []:
        print(f"{dep.parent_node.name} -> {dep.child_node.name}: {dep.call_count} calls")
```

## Sync Usage

```python
from honeycomb import HoneycombClient
from honeycomb.models import ServiceMapDependencyRequestCreate

with HoneycombClient(api_key="your-api-key", sync=True) as client:
    result = client.service_map_dependencies.get(
        request=ServiceMapDependencyRequestCreate(time_range=3600)  # Last hour
    )

    for dep in result.dependencies or []:
        print(f"{dep.parent_node.name} -> {dep.child_node.name}")
```

## Filtering by Service

You can filter dependencies to only include those involving specific services:

```python
from honeycomb.models import ServiceMapDependencyRequestCreate, ServiceMapNode

# Get dependencies involving the user-service
result = await client.service_map_dependencies.get_async(
    request=ServiceMapDependencyRequestCreate(
        time_range=7200,
        filters=[
            ServiceMapNode(name="user-service"),
            ServiceMapNode(name="auth-service"),
        ]
    )
)
```

## Time Range Options

The `ServiceMapDependencyRequestCreate` model supports several time range configurations:

```python
from honeycomb.models import ServiceMapDependencyRequestCreate

# Option 1: Relative time (seconds before now)
request = ServiceMapDependencyRequestCreate(time_range=7200)  # Last 2 hours

# Option 2: Absolute start time + duration
request = ServiceMapDependencyRequestCreate(
    start_time=1622548800,  # Unix timestamp
    time_range=3600,        # 1 hour after start_time
)

# Option 3: Absolute end time + duration
request = ServiceMapDependencyRequestCreate(
    end_time=1622635200,    # Unix timestamp
    time_range=3600,        # 1 hour before end_time
)

# Option 4: Explicit time range (both start and end)
request = ServiceMapDependencyRequestCreate(
    start_time=1622548800,
    end_time=1622635200,
)
```

## Two-Step API (Advanced)

For more control, you can separate the request creation from result retrieval:

```python
from honeycomb.models import ServiceMapDependencyRequestCreate, ServiceMapDependencyRequestStatus

# Step 1: Create the request
req = await client.service_map_dependencies.create_async(
    request=ServiceMapDependencyRequestCreate(time_range=7200),
    limit=50000,  # Request up to 50,000 dependencies
)
print(f"Request ID: {req.request_id}, Status: {req.status}")

# Step 2: Poll for results (with custom max_pages)
result = await client.service_map_dependencies.get_result_async(
    request_id=req.request_id,
    max_pages=100,  # Limit to 100 pages (10,000 dependencies max)
)

if result.status == ServiceMapDependencyRequestStatus.READY:
    print(f"Found {len(result.dependencies or [])} dependencies")
elif result.status == ServiceMapDependencyRequestStatus.ERROR:
    print("Request failed")
else:
    print("Still processing...")
```

## Rate Limiting and Pagination

Service Map Dependencies queries can return up to **64,000 dependencies**. The API returns results in pages of up to 100 items each. This client automatically paginates through all results.

### Important Considerations

- **Large result sets**: A query returning 64,000 dependencies requires up to 640 API requests
- **Default rate limit**: 100 requests per minute per API operation
- **Automatic retry**: The client handles rate limiting with exponential backoff
- **max_pages parameter**: Limits the number of pages fetched (default: 640)

```python
# Limit pagination to control API usage
result = await client.service_map_dependencies.get_async(
    request=ServiceMapDependencyRequestCreate(time_range=86400),  # Last 24 hours
    limit=10000,      # Request up to 10,000 dependencies
    max_pages=50,     # Fetch at most 50 pages (5,000 dependencies)
    timeout=120.0,    # Wait up to 2 minutes for results
)
```

### Need Higher Rate Limits?

If you need higher rate limits for large queries, contact Honeycomb support:
[https://www.honeycomb.io/support](https://www.honeycomb.io/support)

## Models Reference

### ServiceMapDependencyRequestCreate

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | `int \| None` | Absolute start time (Unix timestamp) |
| `end_time` | `int \| None` | Absolute end time (Unix timestamp) |
| `time_range` | `int` | Duration in seconds (default: 7200) |
| `filters` | `list[ServiceMapNode] \| None` | Services to filter by |

### ServiceMapNode

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Service name |
| `type` | `ServiceMapNodeType` | Node type (currently only "service") |

### ServiceMapDependency

| Field | Type | Description |
|-------|------|-------------|
| `parent_node` | `ServiceMapNode` | Upstream service (caller) |
| `child_node` | `ServiceMapNode` | Downstream service (callee) |
| `call_count` | `int` | Number of calls between services |

### ServiceMapDependencyResult

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | `str` | Unique request identifier |
| `status` | `ServiceMapDependencyRequestStatus` | pending, ready, or error |
| `dependencies` | `list[ServiceMapDependency] \| None` | Results (None if not ready) |

## Example: Building a Dependency Graph

```python
from collections import defaultdict
from honeycomb import HoneycombClient
from honeycomb.models import ServiceMapDependencyRequestCreate

async def build_service_graph(client: HoneycombClient) -> dict:
    """Build a graph of service dependencies."""
    result = await client.service_map_dependencies.get_async(
        request=ServiceMapDependencyRequestCreate(time_range=86400)  # Last 24 hours
    )

    graph = defaultdict(list)
    for dep in result.dependencies or []:
        graph[dep.parent_node.name].append({
            "target": dep.child_node.name,
            "calls": dep.call_count,
        })

    return dict(graph)

# Usage
async with HoneycombClient(api_key="...") as client:
    graph = await build_service_graph(client)

    # Print services and their downstream dependencies
    for service, deps in sorted(graph.items()):
        print(f"\n{service}:")
        for dep in sorted(deps, key=lambda x: -x["calls"]):
            print(f"  -> {dep['target']} ({dep['calls']} calls)")
```

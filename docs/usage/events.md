# Working with Events

Events are the core telemetry data sent to Honeycomb. The Events API allows you to send data programmatically for ingestion.

!!! note
    For production workloads, batch sending is highly preferred over single events for better efficiency and throughput.

## Basic Event Operations

### Send a Single Event

```python
{%
   include "../examples/events/basic_event.py"
   start="# start_example:send_single"
   end="# end_example:send_single"
%}
```

### Send Event with Timestamp

```python
{%
   include "../examples/events/basic_event.py"
   start="# start_example:send_with_timestamp"
   end="# end_example:send_with_timestamp"
%}
```

### Send Batch (Recommended)

```python
{%
   include "../examples/events/basic_event.py"
   start="# start_example:send_batch"
   end="# end_example:send_batch"
%}
```

### Verify Events via Query

Events take ~30 seconds to become queryable after sending:

```python
{%
   include "../examples/events/basic_event.py"
   start="# start_example:verify_via_query"
   end="# end_example:verify_via_query"
%}
```

## Additional Options

Events support optional parameters:
- **timestamp**: Unix timestamp for when the event occurred
- **samplerate**: Sampling rate (e.g., 10 means 1 in 10 events)

`BatchEvent` also supports `time` (ISO 8601 string) and `samplerate` fields.

## Event Size Limits

- **Single event body**: 1MB maximum
- **Maximum columns per event**: 2000 distinct fields
- **Batch size**: Limited by total request size (1MB)

## Sync Usage

All event operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # Send single event
    client.events.send("my-dataset", data={"field": "value"})

    # Send batch
    events = [BatchEvent(data={"event": 1}), BatchEvent(data={"event": 2})]
    results = client.events.send_batch("my-dataset", events)
```

**Note**: Events cannot be deleted once sent. They become part of your dataset's telemetry data.

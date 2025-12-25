# Working with Recipients

Recipients define where to send notifications when triggers fire. Supported types include email, Slack, PagerDuty, webhooks, and MS Teams.

## Basic Recipient Operations

### List Recipients

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    recipients = await client.recipients.list_async()

    for recipient in recipients:
        print(f"{recipient.type}: {recipient.id}")
        print(f"  Details: {recipient.details}")
```

### Get a Specific Recipient

```python
recipient = await client.recipients.get_async("recipient-id")

print(f"Type: {recipient.type}")
print(f"Details: {recipient.details}")
```

### Delete a Recipient

```python
await client.recipients.delete_async("recipient-id")
```

## Creating Recipients

### Email Recipient

```python
from honeycomb import HoneycombClient, RecipientCreate, RecipientType

async with HoneycombClient(api_key="...") as client:
    recipient = await client.recipients.create_async(
        RecipientCreate(
            type=RecipientType.EMAIL,
            details={"email_address": "alerts@example.com"}
        )
    )
    print(f"Created email recipient: {recipient.id}")
```

### Slack Recipient

```python
recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.SLACK,
        details={"slack_channel": "#alerts"}
    )
)
```

### PagerDuty Recipient

```python
recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.PAGERDUTY,
        details={
            "integration_key": "your-pagerduty-integration-key",
            "integration_name": "Production Alerts"
        }
    )
)
```

### Webhook Recipient

```python
recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.WEBHOOK,
        details={
            "url": "https://your-webhook.example.com/alerts",
            "name": "Custom Webhook"
        }
    )
)
```

### MS Teams Workflow Recipient

```python
recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.MSTEAMS_WORKFLOW,
        details={
            "workflow_url": "https://yourco.webhook.office.com/...",
            "workflow_name": "Teams Alerts Channel"
        }
    )
)
```

## Updating Recipients

```python
updated_recipient = await client.recipients.update_async(
    "recipient-id",
    RecipientCreate(
        type=RecipientType.EMAIL,
        details={"email_address": "new-alerts@example.com"}
    )
)
```

## Finding Triggers for a Recipient

See which triggers are using a specific recipient:

```python
triggers = await client.recipients.get_triggers_async("recipient-id")

for trigger in triggers:
    print(f"Trigger: {trigger['name']}")
    print(f"  Dataset: {trigger.get('dataset_slug')}")
```

## Recipient Types

Available recipient types:

| Type | Details Structure |
|------|-------------------|
| `EMAIL` | `{"email_address": "..."}` |
| `SLACK` | `{"slack_channel": "#..."}` |
| `PAGERDUTY` | `{"integration_key": "...", "integration_name": "..."}` |
| `WEBHOOK` | `{"url": "https://...", "name": "..."}` |
| `MSTEAMS_WORKFLOW` | `{"workflow_url": "https://...", "workflow_name": "..."}` |
| `MSTEAMS` | (deprecated, use `MSTEAMS_WORKFLOW`) |

## Sync Usage

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List recipients
    recipients = client.recipients.list()

    # Create recipient
    recipient = client.recipients.create(
        RecipientCreate(
            type=RecipientType.SLACK,
            details={"slack_channel": "#alerts"}
        )
    )

    # Get triggers for recipient
    triggers = client.recipients.get_triggers("recipient-id")

    # Delete recipient
    client.recipients.delete("recipient-id")
```

## Using Recipients with Triggers

Recipients are referenced in trigger configurations:

```python
from honeycomb import TriggerCreate, TriggerThreshold, TriggerThresholdOp

# Create recipient first
email_recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.EMAIL,
        details={"email_address": "oncall@example.com"}
    )
)

# Create trigger with recipient
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="High Error Rate",
        threshold=TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN,
            value=0.05
        ),
        frequency=300,
        query_id="saved-query-id",
        recipients=[
            {"id": email_recipient.id, "type": "email"}
        ]
    )
)
```

## Best Practices

1. **Centralize Recipients**: Create shared recipients for teams rather than duplicating
2. **Descriptive Names**: Use clear names in PagerDuty and webhook details
3. **Test Webhooks**: Verify webhook URLs before creating production triggers
4. **Multiple Recipients**: Add multiple recipients to critical triggers
5. **Audit Usage**: Periodically check which triggers use each recipient before deletion

## Example: Multi-Channel Alert Setup

```python
# Create recipients for different severity levels
critical_recipients = []

# Email for critical issues
email_recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.EMAIL,
        details={"email_address": "critical@example.com"}
    )
)
critical_recipients.append({"id": email_recipient.id, "type": "email"})

# PagerDuty for incidents
pagerduty_recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.PAGERDUTY,
        details={
            "integration_key": "your-key",
            "integration_name": "Critical Alerts"
        }
    )
)
critical_recipients.append({"id": pagerduty_recipient.id, "type": "pagerduty"})

# Slack for team awareness
slack_recipient = await client.recipients.create_async(
    RecipientCreate(
        type=RecipientType.SLACK,
        details={"slack_channel": "#incidents"}
    )
)
critical_recipients.append({"id": slack_recipient.id, "type": "slack"})

# Use in trigger
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="Critical: Service Down",
        threshold=TriggerThreshold(op=TriggerThresholdOp.LESS_THAN, value=1),
        frequency=60,  # Check every minute
        query_id="uptime-query-id",
        recipients=critical_recipients
    )
)
```

# Working with Recipients

Recipients define where to send notifications when triggers fire. Supported types include email, Slack, PagerDuty, webhooks, and MS Teams.

## Basic Recipient Operations

### List Recipients

=== "Async"

    ```python
    {%
       include "../examples/recipients/list_recipients.py"
       start="# start_example:list_async"
       end="# end_example:list_async"
    %}
    ```

=== "Sync"

    ```python
    {%
       include "../examples/recipients/list_recipients.py"
       start="# start_example:list_sync"
       end="# end_example:list_sync"
    %}
    ```

### Get, Update, Delete Recipients

All standard CRUD operations are available:

```python
# Get recipient
recipient = await client.recipients.get_async(recipient_id)

# Update recipient
updated = await client.recipients.update_async(
    recipient_id,
    RecipientCreate(type=RecipientType.EMAIL, details={"email_address": "new@example.com"})
)

# Delete recipient
await client.recipients.delete_async(recipient_id)

# Find which triggers use this recipient
triggers = await client.recipients.get_triggers_async(recipient_id)
```

## Creating Recipients

### Email Recipient

=== "With RecipientBuilder"

    ```python
    {%
       include "../examples/recipients/email_recipient.py"
       start="# start_example:email_with_builder"
       end="# end_example:email_with_builder"
    %}
    ```

=== "Manual Construction"

    ```python
    {%
       include "../examples/recipients/email_recipient.py"
       start="# start_example:email_manual"
       end="# end_example:email_manual"
    %}
    ```

### Webhook Recipient

=== "Basic Webhook"

    ```python
    {%
       include "../examples/recipients/webhook_recipient.py"
       start="# start_example:webhook_with_builder"
       end="# end_example:webhook_with_builder"
    %}
    ```

=== "With Authentication Headers"

    ```python
    {%
       include "../examples/recipients/webhook_recipient.py"
       start="# start_example:webhook_with_auth_headers"
       end="# end_example:webhook_with_auth_headers"
    %}
    ```

=== "With Custom Payload Templates"

    ```python
    {%
       include "../examples/recipients/webhook_recipient.py"
       start="# start_example:webhook_with_custom_payload"
       end="# end_example:webhook_with_custom_payload"
    %}
    ```

## Recipient Types Reference

### Basic Details Structure

| Type | Required Fields | Optional Fields |
|------|----------------|-----------------|
| `EMAIL` | `email_address` | - |
| `SLACK` | `slack_channel` | - |
| `PAGERDUTY` | `pagerduty_integration_key` (32 chars), `pagerduty_integration_name` | - |
| `WEBHOOK` | `webhook_url`, `webhook_name` | `webhook_secret`, `webhook_headers`, `webhook_payloads` |
| `MSTEAMS_WORKFLOW` | `webhook_url`, `webhook_name` | - |
| `MSTEAMS` | (deprecated, use `MSTEAMS_WORKFLOW`) | - |

### Webhook Advanced Features

**HTTP Headers** (max 5):
```python
webhook_headers=[
    {"header": "Authorization", "value": "Bearer token"},
    {"header": "X-Custom-Header", "value": "custom-value"}
]
```

**Payload Templates** (for customizing webhook JSON):
```python
# Define template variables
template_variables=[
    {"name": "environment", "default_value": "production"},
    {"name": "severity", "default_value": "warning"}
]

# Define payload templates for each alert type (trigger, budget_rate, exhaustion_time)
payload_templates={
    "trigger": {"body": '{"env": "{{.environment}}", "level": "{{.severity}}"}'},
    "budget_rate": {"body": '{"env": "{{.environment}}", "level": "critical"}'},
    "exhaustion_time": {"body": '{"env": "{{.environment}}", "level": "critical"}'}
}

# Use in RecipientBuilder
RecipientBuilder.webhook(
    url="https://example.com/webhook",
    template_variables=template_variables,
    payload_templates=payload_templates
)
```

**Template Variable Syntax**: Uses Go template syntax with dot prefix: `{{.variableName}}`

**For complete webhook template reference**, see Honeycomb's documentation:
- [Webhook Template Variables](https://docs.honeycomb.io/notify/webhooks/variables/) - All available variables for triggers and burn alerts
- [Webhook Template Functions](https://docs.honeycomb.io/notify/webhooks/functions/) - Functions like `toJson`, `date`, `upper`, `join`, etc.
- [Example Webhook Templates](https://docs.honeycomb.io/notify/webhooks/example-templates/) - Complete examples for Discord, Slack, incident.io, etc.

**RecipientBuilder** provides static factory methods: `.email()`, `.slack()`, `.pagerduty()`, `.webhook()`, `.msteams()`

## Sync Usage

All recipient operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List recipients
    recipients = client.recipients.list()

    # Create recipient
    recipient = client.recipients.create(
        RecipientCreate(type=RecipientType.EMAIL, details={"email_address": "team@example.com"})
    )

    # Get, update, delete recipient
    recipient = client.recipients.get(recipient_id)
    updated = client.recipients.update(recipient_id, RecipientCreate(...))
    client.recipients.delete(recipient_id)

    # Find triggers using this recipient
    triggers = client.recipients.get_triggers(recipient_id)
```

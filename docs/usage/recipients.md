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

=== "With RecipientBuilder"

    ```python
    {%
       include "../examples/recipients/webhook_recipient.py"
       start="# start_example:webhook_with_builder"
       end="# end_example:webhook_with_builder"
    %}
    ```

=== "Manual Construction"

    ```python
    {%
       include "../examples/recipients/webhook_recipient.py"
       start="# start_example:webhook_manual"
       end="# end_example:webhook_manual"
    %}
    ```

## Recipient Types Reference

| Type | Details Structure |
|------|-------------------|
| `EMAIL` | `{"email_address": "..."}` |
| `SLACK` | `{"slack_channel": "#..."}` |
| `PAGERDUTY` | `{"integration_key": "...", "integration_name": "..."}` |
| `WEBHOOK` | `{"url": "https://...", "name": "...", "secret": "..."}` |
| `MSTEAMS_WORKFLOW` | `{"workflow_url": "https://...", "workflow_name": "..."}` |
| `MSTEAMS` | (deprecated, use `MSTEAMS_WORKFLOW`) |

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

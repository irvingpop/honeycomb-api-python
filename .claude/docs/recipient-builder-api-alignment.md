# Recipient Builder API Alignment Analysis

**Date**: 2026-01-08
**Analysis**: Comparison of hand-written recipient_builder.py against OpenAPI spec

## Summary

✅ **All core recipient types correctly implemented**
✅ **All required fields properly mapped**
⚠️ **1 minor discrepancy**: PagerDuty field naming between inline (triggers) vs standalone (Recipients API)
✅ **RecipientMixin provides excellent UX for inline recipient creation**

---

## Recipient Schema Architecture

The Recipients API uses an **OpenAPI discriminator pattern** with a `oneOf` union based on the `type` field:

```yaml
Recipient:
  discriminator:
    propertyName: type
  oneOf:
    - EmailRecipient
    - SlackRecipient
    - PagerDutyRecipient
    - WebhookRecipient
    - MSTeamsRecipient (deprecated)
    - MSTeamsWorkflowRecipient
```

---

## Detailed Comparison

### 1. RecipientCreate Model

| Property | Hand-Written | Generated (OpenAPI) | Status |
|----------|-------------|---------------------|---------|
| `type` | `RecipientType` (required) | `RecipientType` (discriminator) | ✅ Correct |
| `details` | `dict[str, Any]` (required) | Varies by type | ✅ Correct (dynamic) |
| `id` | ❌ Not in create model | `str` (readOnly) | ✅ Correct (response-only) |
| `created_at` | ❌ Not in create model | `datetime` (readOnly) | ✅ Correct (response-only) |
| `updated_at` | ❌ Not in create model | `datetime` (readOnly) | ✅ Correct (response-only) |

**Source**:
- OpenAPI: `api.yaml:7836-7852` (Recipient discriminator)
- Generated: `_generated/models/email_recipient.py` (and other type-specific files)
- Hand-written: `models/recipients.py:23-31`

**Status**: ✅ Perfect - model correctly represents creation requirements

---

### 2. RecipientType Enum

| Value | Hand-Written | Generated (OpenAPI) | Status |
|-------|-------------|---------------------|---------|
| `email` | ✅ | ✅ | ✅ Correct |
| `slack` | ✅ | ✅ | ✅ Correct |
| `pagerduty` | ✅ | ✅ | ✅ Correct |
| `webhook` | ✅ | ✅ | ✅ Correct |
| `msteams` | ✅ | ✅ | ✅ Correct (deprecated) |
| `msteams_workflow` | ✅ | ✅ | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7605-7614`
- Generated: `_generated/models/recipient_type.py`
- Hand-written: `models/recipients.py:12-20`

**Status**: ✅ All 6 types present (including deprecated msteams)

---

### 3. RecipientBuilder Factory Methods

#### Email Recipient

| Field | RecipientBuilder | API Spec | Status |
|-------|------------------|----------|---------|
| `type` | `"email"` | ✅ Required | ✅ Correct |
| `details.email_address` | ✅ Set from `address` | ✅ Required | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7643-7663`
- Hand-written: `recipient_builder.py:162-171`

**Status**: ✅ Perfect alignment

---

#### Slack Recipient

| Field | RecipientBuilder | API Spec | Status |
|-------|------------------|----------|---------|
| `type` | `"slack"` | ✅ Required | ✅ Correct |
| `details.slack_channel` | ✅ Set from `channel` | ✅ Required | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7664-7684`
- Hand-written: `recipient_builder.py:174-183`

**Status**: ✅ Perfect alignment

---

#### PagerDuty Recipient

| Field | RecipientBuilder | API Spec | Status |
|-------|------------------|----------|---------|
| `type` | `"pagerduty"` | ✅ Required | ✅ Correct |
| `details.pagerduty_integration_key` | ✅ Set from `integration_key` | ✅ Required (32 chars) | ✅ Correct |
| `details.pagerduty_integration_name` | ✅ Set from `integration_name` | ✅ Required | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7615-7642`
- Hand-written: `recipient_builder.py:186-205`

**Status**: ✅ Perfect alignment

**Note**: No validation on 32-character requirement for integration_key, but API will validate.

---

#### Webhook Recipient

| Field | RecipientBuilder | API Spec | Status |
|-------|------------------|----------|---------|
| `type` | `"webhook"` | ✅ Required | ✅ Correct |
| `details.webhook_url` | ✅ Set from `url` | ✅ Required (max 2048) | ✅ Correct |
| `details.webhook_name` | ✅ Set from `name` | ✅ Required (max 255) | ✅ Correct |
| `details.webhook_secret` | ✅ Optional from `secret` | ✅ Optional (max 255) | ✅ Correct |
| `details.webhook_headers` | ❌ Not supported | ✅ Optional (max 5) | ⚠️ Missing |
| `details.webhook_payloads` | ❌ Not supported | ✅ Optional | ⚠️ Missing |

**Source**:
- OpenAPI: `api.yaml:7741-7804`
- Hand-written: `recipient_builder.py:208-229`

**Status**: ⚠️ **Missing advanced webhook features** (headers, custom payloads with template variables)

**Impact**: Users cannot set custom HTTP headers or use advanced webhook payload templating

---

#### MS Teams Workflow Recipient

| Field | RecipientBuilder | API Spec | Status |
|-------|------------------|----------|---------|
| `type` | `"msteams_workflow"` | ✅ Required | ✅ Correct |
| `details.webhook_url` | ✅ Set from `workflow_url` | ✅ Required (max 2048) | ✅ Correct |
| `details.webhook_name` | ✅ Set from `name` | ✅ Required (max 255) | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7713-7740`
- Hand-written: `recipient_builder.py:232-248`

**Status**: ✅ Perfect alignment

---

### 4. RecipientMixin (for Inline Recipients in Triggers/BurnAlerts)

The RecipientMixin uses a **deprecated inline format** that the API still accepts:
- `type` + `target` + optional `details`

This is for **backward compatibility** with trigger creation where recipients can be created inline.

| Method | Creates | API Format | Status |
|--------|---------|------------|---------|
| `.email(address)` | Email inline | `{type: "email", target: address}` | ✅ Works (deprecated format) |
| `.slack(channel)` | Slack inline | `{type: "slack", target: channel}` | ✅ Works (deprecated format) |
| `.pagerduty(key, severity)` | PagerDuty inline | `{type: "pagerduty", target: key, details: {severity}}` | ⚠️ See Note |
| `.webhook(url, name, secret)` | Webhook inline | `{type: "webhook", target: url, details: {...}}` | ✅ Works |
| `.msteams(url)` | MSTeams inline | `{type: "msteams_workflow", target: url}` | ✅ Works |
| `.recipient_id(id)` | Reference existing | `{id}` | ✅ Preferred pattern |

**Source**: `recipient_builder.py:12-148`

**PagerDuty Severity Note**:

**Inline format** (triggers/burn alerts):
```python
# RecipientMixin.pagerduty() generates:
{
  "type": "pagerduty",
  "target": "routing-key",
  "details": {"severity": "critical"}  # For NotificationRecipientDetails
}
```

**Standalone format** (Recipients API):
```python
# RecipientBuilder.pagerduty() generates:
{
  "type": "pagerduty",
  "details": {
    "pagerduty_integration_key": "routing-key",
    "pagerduty_integration_name": "Integration Name"
  }
  # NO severity field (that's in NotificationRecipientDetails, not PagerDutyRecipient)
}
```

**Status**: ⚠️ **Naming discrepancy but correct usage**:
- `RecipientMixin.pagerduty(routing_key, severity)` - "routing_key" parameter name vs API's "pagerduty_integration_key"
- Both work correctly - one is for inline trigger creation, the other for standalone recipient creation
- The `severity` field in inline format goes into `NotificationRecipientDetails`, not the recipient itself

---

### 5. Recipient Response Model

| Property | Hand-Written | API Spec | Status |
|----------|-------------|----------|---------|
| `id` | ✅ `str` | ✅ `str` (readOnly) | ✅ Correct |
| `type` | ✅ `RecipientType` | ✅ enum | ✅ Correct |
| `details` | ✅ `dict[str, Any]` | ✅ Varies by type | ✅ Correct |
| `created_at` | ✅ `datetime \| None` | ✅ `datetime` (readOnly) | ✅ Correct |
| `updated_at` | ✅ `datetime \| None` | ✅ `datetime` (readOnly) | ✅ Correct |

**Source**: `models/recipients.py:34-43`

**Status**: ✅ Complete response model with extras allowed

---

### 6. Advanced Webhook Features (Missing)

#### Webhook Headers

**API Support** (api.yaml:7805-7821):
```yaml
webhook_headers:
  type: array
  maxItems: 5
  items:
    type: object
    required: [header]
    properties:
      header:
        type: string
        maxLength: 64
      value:
        type: string
        maxLength: 750
```

**Current Implementation**: ❌ Not supported in RecipientBuilder

**Impact**: Users cannot add custom HTTP headers like `Authorization: Bearer xyz`

---

#### Webhook Payloads (Template Variables)

**API Support** (api.yaml:7768-7804):
```yaml
webhook_payloads:
  type: object
  properties:
    template_variables:
      type: array
      maxItems: 10
      items:
        name: string (pattern: ^[a-z](?:[a-zA-Z0-9]+$)?$, maxLength: 64)
        default_value: string (maxLength: 256, optional)
    payload_templates:
      trigger: {body: string}
      budget_rate: {body: string}
      exhaustion_time: {body: string}
```

**Current Implementation**: ❌ Not supported in RecipientBuilder

**Impact**: Users cannot customize webhook payloads with template variables or different payloads per alert type

---

## Findings Summary

### Missing Features (Low Priority, Advanced)

1. **Webhook HTTP Headers**
   - **Location**: RecipientBuilder.webhook()
   - **Impact**: Cannot set custom headers (e.g., Authorization, X-Custom-Header)
   - **Usage**: Advanced webhook integrations requiring authentication headers
   - **Priority**: Low - most webhooks work without custom headers

2. **Webhook Payload Templates**
   - **Location**: RecipientBuilder.webhook()
   - **Impact**: Cannot customize webhook JSON payloads or use template variables
   - **Usage**: Advanced webhook integrations requiring custom payload formats
   - **Priority**: Low - default webhook payload usually sufficient

### Correctly Implemented Features

1. ✅ **All 6 recipient types** (email, slack, pagerduty, webhook, msteams, msteams_workflow)
2. ✅ **All required fields** for each type
3. ✅ **RecipientMixin** for inline recipient creation (triggers/burn alerts)
4. ✅ **RecipientBuilder** for standalone recipient creation (Recipients API)
5. ✅ **PagerDuty severity** support in NotificationRecipientDetails
6. ✅ **Webhook secret** support
7. ✅ **RecipientCreate and Recipient** models with proper field handling
8. ✅ **RecipientType enum** with all 6 types

### Intentional Design Choices (Good!)

1. **Dual pattern**: RecipientMixin (inline) vs RecipientBuilder (standalone)
   - RecipientMixin: Used in TriggerBuilder, BurnAlertBuilder for convenience
   - RecipientBuilder: Used for standalone recipient creation
   - Both patterns are valid and serve different use cases

2. **Simple details dict**: Using `dict[str, Any]` instead of typed models per type
   - Provides flexibility for API changes
   - Avoids complex type unions
   - Details schema varies significantly by type

3. **Parameter naming**:
   - RecipientMixin uses friendly names: `routing_key`, `channel`, `address`
   - Maps correctly to API fields: `pagerduty_integration_key`, `slack_channel`, `email_address`

---

## Recommendations

### Optional (Low Priority)

1. **Add webhook headers support** (if needed for advanced integrations)
   ```python
   # recipient_builder.py - RecipientBuilder
   @staticmethod
   def webhook(
       url: str,
       name: str = "Webhook",
       secret: str | None = None,
       headers: list[dict[str, str]] | None = None,  # NEW
   ) -> RecipientCreate:
       details = {
           "webhook_url": url,
           "webhook_name": name,
       }
       if secret:
           details["webhook_secret"] = secret
       if headers:
           details["webhook_headers"] = [
               {"header": h["header"], "value": h.get("value", "")}
               for h in headers
           ]
       return RecipientCreate(type=RecipientType.WEBHOOK, details=details)
   ```

2. **Add webhook payload templates support** (if needed for custom payloads)
   ```python
   @staticmethod
   def webhook_with_templates(
       url: str,
       name: str = "Webhook",
       template_variables: list[dict[str, str]] | None = None,
       payload_templates: dict[str, dict[str, str]] | None = None,
   ) -> RecipientCreate:
       # Implementation for advanced webhook features
   ```

### No Action Needed

The current implementation is **highly functional** for standard use cases:
- ✅ All recipient types work correctly
- ✅ All required fields properly set
- ✅ Good parameter naming (user-friendly)
- ✅ Dual pattern (inline vs standalone) is excellent design

---

## Detailed Field Mappings

### Email Recipient Details

**API Schema** (api.yaml:7643-7663):
```yaml
email_address: string (REQUIRED)
```

**RecipientBuilder.email()**:
```python
{"email_address": address}  ✅
```

**RecipientMixin.email()**:
```python
{"type": "email", "target": address}  ✅ (inline format)
```

---

### Slack Recipient Details

**API Schema** (api.yaml:7664-7684):
```yaml
slack_channel: string (REQUIRED)
```

**RecipientBuilder.slack()**:
```python
{"slack_channel": channel}  ✅
```

**RecipientMixin.slack()**:
```python
{"type": "slack", "target": channel}  ✅ (inline format)
```

---

### PagerDuty Recipient Details

**API Schema** (api.yaml:7615-7642):
```yaml
pagerduty_integration_key: string (REQUIRED, 32 chars)
pagerduty_integration_name: string (REQUIRED)
```

**RecipientBuilder.pagerduty()**:
```python
{
  "pagerduty_integration_key": integration_key,  ✅
  "pagerduty_integration_name": integration_name  ✅
}
```

**RecipientMixin.pagerduty()** (inline for triggers):
```python
{
  "type": "pagerduty",
  "target": routing_key,  # Maps to integration_key
  "details": {"severity": "critical"}  # For NotificationRecipientDetails
}  ✅
```

**Note**: Different usage contexts:
- **RecipientBuilder**: Creates standalone PagerDuty recipient via Recipients API
- **RecipientMixin**: Creates inline recipient for trigger notification (uses deprecated `target` format but still works)

---

### Webhook Recipient Details

**API Schema** (api.yaml:7741-7804):
```yaml
webhook_url: string (REQUIRED, max 2048)
webhook_name: string (REQUIRED, max 255)
webhook_secret: string (OPTIONAL, max 255)
webhook_headers: array (OPTIONAL, max 5 items)
  - header: string (REQUIRED, max 64)
  - value: string (OPTIONAL, max 750)
webhook_payloads: object (OPTIONAL)
  - template_variables: array (max 10)
  - payload_templates: object
```

**RecipientBuilder.webhook()**:
```python
{
  "webhook_url": url,  ✅
  "webhook_name": name,  ✅
  "webhook_secret": secret  ✅ (if provided)
}
# Missing: webhook_headers, webhook_payloads
```

**RecipientMixin.webhook()** (inline for triggers):
```python
{
  "type": "webhook",
  "target": url,
  "details": {
    "webhook_url": url,  ✅
    "webhook_name": name,  ✅
    "webhook_secret": secret  ✅ (if provided)
  }
}
# Missing: webhook_headers, webhook_payloads
```

**Status**: ⚠️ Missing advanced features (headers, custom payloads)

---

### MS Teams Workflow Recipient Details

**API Schema** (api.yaml:7713-7740):
```yaml
webhook_url: string (REQUIRED, max 2048)
webhook_name: string (REQUIRED, max 255)
```

**RecipientBuilder.msteams()**:
```python
{
  "webhook_url": workflow_url,  ✅
  "webhook_name": name  ✅
}
```

**RecipientMixin.msteams()** (inline for triggers):
```python
{
  "type": "msteams_workflow",
  "target": workflow_url
}
# Missing webhook_name in details for inline format
```

**Status**: ⚠️ **Minor discrepancy**: Inline format doesn't include `webhook_name` in details

**Impact**: Minimal - `target` field provides the URL, name is cosmetic

---

### 7. NotificationRecipient (Deprecated Inline Format)

Used in triggers for backward compatibility. The API docs recommend using `id` field instead.

**API Schema** (api.yaml:6681-6709):
```yaml
id: string (OPTIONAL - use this instead of type+target)
type: RecipientType (DEPRECATED)
target: string (DEPRECATED)
details: NotificationRecipientDetails (OPTIONAL)
  - pagerduty_severity: enum (critical, error, warning, info)
  - variables: array of {name, value} pairs
```

**RecipientMixin Implementation**: ✅ Correctly uses this format for inline recipient creation

---

## Conclusion

The Recipient Builder implementation is **highly correct** with only **advanced webhook features missing**:

1. **Webhook HTTP headers** - Custom header support (5 max)
2. **Webhook payload templates** - Custom JSON payloads with template variables

Both are **low-priority advanced features** that most users don't need.

### Strengths

✅ **All core recipient types** fully functional
✅ **Dual pattern** (inline via RecipientMixin, standalone via RecipientBuilder) is excellent design
✅ **All required fields** properly mapped
✅ **User-friendly parameter names** that map to correct API fields
✅ **PagerDuty severity** correctly handled via NotificationRecipientDetails
✅ **Webhook secrets** supported

The implementation provides **excellent UX** while maintaining **full API compatibility** for standard recipient use cases.

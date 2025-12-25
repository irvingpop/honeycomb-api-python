# Authentication

The Honeycomb API Python client supports two authentication methods: API keys for single-environment access and Management keys for multi-environment operations.

## API Key Authentication (Recommended for Most Users)

API keys are the simplest way to authenticate and work great for most use cases where you're working with a single Honeycomb environment.

### Getting Your API Key

1. Log in to your Honeycomb account
2. Navigate to Team Settings → API Keys
3. Create a new API key or copy an existing one

### Using API Keys

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="hcaik_your_key_here") as client:
    datasets = await client.datasets.list_async()
```

API keys are sent via the `X-Honeycomb-Team` header.

### Environment Variables

For better security, use environment variables:

```python
import os
from honeycomb import HoneycombClient

api_key = os.environ["HONEYCOMB_API_KEY"]

async with HoneycombClient(api_key=api_key) as client:
    # Your code here
    pass
```

## Management Key Authentication

Management keys provide access to management APIs across multiple environments. Use this for:

- Managing API keys programmatically
- Multi-environment operations
- Team-level administration

### Getting Your Management Key

1. Log in to your Honeycomb account
2. Navigate to Team Settings → Management API Keys
3. Create a new management key pair (key ID + secret)

### Using Management Keys

```python
from honeycomb import HoneycombClient

async with HoneycombClient(
    management_key="hcmak_your_key_id",
    management_secret="your_key_secret"
) as client:
    # Management operations
    pass
```

Management credentials are sent via the `Authorization: Bearer` header as `Bearer {key_id}:{secret}`.

## Choosing the Right Authentication Method

| Feature | API Key | Management Key |
|---------|---------|----------------|
| Access scope | Single environment | Multi-environment |
| Dataset operations | ✓ | ✓ |
| Trigger/SLO management | ✓ | ✓ |
| API key management | ✗ | ✓ |
| Environment management | ✗ | ✓ |
| Recommended for | Most users | Admin/automation |

!!! tip "Start with API Keys"
    Unless you specifically need multi-environment management, start with API key authentication - it's simpler and covers most use cases.

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** or a secrets manager
3. **Rotate keys regularly** (especially after team member changes)
4. **Use read-only keys** when possible (if you only need to read data)
5. **Set key expiration** in Honeycomb when creating keys

### Example with direnv

Create a `.envrc` file (and add it to `.gitignore`):

```bash
export HONEYCOMB_API_KEY=hcaik_your_key_here
export HONEYCOMB_DATASET=my-dataset
```

Then use in your code:

```python
import os
from honeycomb import HoneycombClient

client = HoneycombClient(api_key=os.environ["HONEYCOMB_API_KEY"])
```

## Troubleshooting

### 401 Unauthorized Error

If you get a `HoneycombAuthError`:

- Verify your API key is correct (no extra spaces)
- Check the key hasn't been revoked or expired
- Ensure you're using the right key for the environment

### 403 Forbidden Error

If you get a `HoneycombForbiddenError`:

- Verify your API key has the required permissions
- Some operations require write access - check your key's capabilities
- Management operations require a management key, not an API key

## Next Steps

- [Quick Start Guide](quickstart.md) - Start using the client
- [Error Handling](../advanced/error-handling.md) - Handle authentication errors gracefully

# Installation

## Requirements

- Python 3.10 or higher

## CLI Only (No Project Install)

To use the CLI without adding to a project:

```bash
# Using uv (fastest)
uv tool install honeycomb-api

# OR Using pipx
pipx install honeycomb-api

# Then use the short alias
hny triggers list
```

## Adding to a Project

### Using uv

```bash
uv add honeycomb-api
```

### Using Poetry

```bash
poetry add honeycomb-api
```

Or add to your `pyproject.toml`:

```toml
[project.dependencies]
honeycomb-api = ">=0.4.0"
```

## Verify Installation

Verify the installation by importing the package:

```python
from honeycomb import HoneycombClient, __version__

print(f"Honeycomb API Client version: {__version__}")
```

## Optional Dependencies

The client has no optional dependencies - everything you need is included in the base installation.

## Development Installation

If you want to contribute to the project or run the latest development version:

```bash
# Clone the repository
git clone https://github.com/irvingpop/honeycomb-api-python.git
cd honeycomb-api-python

# Install with development dependencies
make install-dev
# Or: poetry install

# Run tests to verify
make test
```

See the [Contributing Guide](../contributing.md) for more information on development setup.

## Next Steps

Now that you have the client installed, check out the [Quick Start Guide](quickstart.md) to start using it!

# Installation

## Requirements

- Python 3.10 or higher
- pip or Poetry for package management

## Using pip

Install the latest stable version from PyPI:

```bash
pip install honeycomb-api-python
```

## Using Poetry

Add to your project:

```bash
poetry add honeycomb-api-python
```

Or add to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
honeycomb-api-python = "^0.1.0"
```

Then run:

```bash
poetry install
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

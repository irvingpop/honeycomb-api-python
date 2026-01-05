#!/bin/bash
# Generate the Honeycomb API client from the OpenAPI spec.
#
# This script:
# 1. Optionally fetches the latest spec from Honeycomb
# 2. Applies patches to fix spec issues
# 3. Generates the client using openapi-python-client
#
# Usage:
#   ./scripts/generate-client.sh [--fetch]
#
# Prerequisites:
#   - poetry install --with codegen
#   - pipx install openapi-python-client --include-deps

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Parse arguments
FETCH_SPEC=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --fetch)
            FETCH_SPEC=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Step 1: Optionally fetch latest spec
if [ "$FETCH_SPEC" = true ]; then
    echo "Fetching latest OpenAPI spec from Honeycomb..."
    curl -sSL -o api.yaml https://api.honeycomb.io/api.yaml
    echo "Downloaded api.yaml"
fi

# Step 2: Apply patches (using poetry for pyyaml dependency)
echo ""
echo "Applying patches to OpenAPI spec..."
poetry run python scripts/patch-openapi.py --input api.yaml --output api.yaml --backup

# Step 3: Remove old generated client
echo ""
echo "Removing old generated client..."
rm -rf src/honeycomb/_generated

# Step 4: Generate new client
echo ""
echo "Generating new client..."
openapi-python-client generate \
    --path api.yaml \
    --config generator-config.yaml \
    --output-path ./generated-client

# Step 5: Move generated package to correct location
echo ""
echo "Moving generated package..."
mv ./generated-client/_generated src/honeycomb/
rm -rf ./generated-client

# Step 6: Summary
echo ""
echo "Generation complete!"
echo ""
echo "Generated files:"
find src/honeycomb/_generated -name "*.py" | wc -l | xargs echo "  Python files:"
find src/honeycomb/_generated/api -mindepth 1 -maxdepth 1 -type d | wc -l | xargs echo "  API modules:"
find src/honeycomb/_generated/models -name "*.py" | wc -l | xargs echo "  Model files:"

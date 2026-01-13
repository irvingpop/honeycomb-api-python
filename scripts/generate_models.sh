#!/bin/bash
set -e

# Generate Pydantic v2 models from Honeycomb OpenAPI spec
# Usage: ./scripts/generate_models.sh [--fetch]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SPEC_FILE="$PROJECT_ROOT/api.yaml"
PATCHED_SPEC_FILE="$PROJECT_ROOT/.api-patched.yaml"
OUTPUT_FILE="$PROJECT_ROOT/src/honeycomb/_generated_models.py"

# Optionally fetch fresh spec
if [[ "$1" == "--fetch" ]]; then
    echo "Fetching fresh OpenAPI spec..."
    curl -sS -o "$SPEC_FILE" https://api.honeycomb.io/api.yaml
    echo "Spec downloaded: $(wc -c < "$SPEC_FILE" | tr -d ' ') bytes"
fi

# Patch the spec to add titles to inline schemas
echo "Patching $SPEC_FILE to add titles to inline schemas..."
poetry run python "$SCRIPT_DIR/patch_openapi_spec.py" "$SPEC_FILE" "$PATCHED_SPEC_FILE"

echo ""
echo "Generating models from $PATCHED_SPEC_FILE..."

poetry run datamodel-codegen \
  --input "$PATCHED_SPEC_FILE" \
  --input-file-type openapi \
  --output "$OUTPUT_FILE" \
  --output-model-type pydantic_v2.BaseModel \
  --naming-strategy full-path \
  --use-title-as-name \
  --use-schema-description \
  --field-constraints \
  --use-double-quotes \
  --target-python-version 3.10 \
  --collapse-root-models \
  --reuse-model \
  --use-default-kwarg \
  --disable-timestamp \
  --formatters ruff-format ruff-check

echo "Generated: $OUTPUT_FILE"
echo "  $(grep -c '^class ' "$OUTPUT_FILE") models"
echo "  $(wc -l < "$OUTPUT_FILE" | tr -d ' ') lines"

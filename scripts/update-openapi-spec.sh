#!/bin/bash
# Update OpenAPI spec from Honeycomb and generate change report
#
# This script:
# 1. Downloads the latest spec from Honeycomb
# 2. Compares it with the current patched version
# 3. Applies patches to the new spec
# 4. Generates a comprehensive diff report
#
# Usage:
#   ./scripts/update-openapi-spec.sh
#
# Options:
#   --skip-download    Skip downloading, just regenerate diff from existing files
#   --apply            Apply the changes (move new spec to api.yaml)
#
# Output:
#   - api.yaml.new           New spec with patches applied
#   - api.yaml.downloaded    Original downloaded spec (backup)
#   - .openapi-diff.txt      Summary of changes between old and new

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Parse arguments
SKIP_DOWNLOAD=false
APPLY_CHANGES=false

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Update OpenAPI spec from Honeycomb and generate change report"
    echo ""
    echo "Options:"
    echo "  --skip-download    Skip downloading, use existing api.yaml.downloaded"
    echo "  --apply            Apply changes immediately (move api.yaml.new to api.yaml)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 Download and show diff (safe, doesn't modify api.yaml)"
    echo "  $0 --apply         Download, show diff, and apply changes"
    echo "  $0 --skip-download Re-run diff without re-downloading"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --skip-download)
            SKIP_DOWNLOAD=true
            shift
            ;;
        --apply)
            APPLY_CHANGES=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

echo "============================================"
echo "OpenAPI Spec Update Process"
echo "============================================"
echo ""

# Step 1: Download latest spec (unless skipped)
if [ "$SKIP_DOWNLOAD" = false ]; then
    echo "Step 1: Downloading latest OpenAPI spec from Honeycomb..."
    if ! curl -sSL -o api.yaml.downloaded https://api.honeycomb.io/api.yaml; then
        echo "Error: Failed to download OpenAPI spec"
        exit 1
    fi
    echo "✓ Downloaded to api.yaml.downloaded"

    # Show download info
    LINES=$(wc -l < api.yaml.downloaded | tr -d ' ')
    echo "  Lines: $LINES"
    echo ""
else
    echo "Step 1: Skipping download (using existing api.yaml.downloaded)"
    if [ ! -f api.yaml.downloaded ]; then
        echo "Error: api.yaml.downloaded not found. Run without --skip-download first."
        exit 1
    fi
    echo ""
fi

# Step 2: Apply patches to new spec
echo "Step 2: Applying patches to new spec..."
cp api.yaml.downloaded api.yaml.new
poetry run python scripts/patch-openapi.py --input api.yaml.new --output api.yaml.new --no-backup
echo "✓ Patches applied to api.yaml.new"
echo ""

# Step 3: Generate diff report
echo "Step 3: Generating change report..."

# Create diff report file
DIFF_FILE=".openapi-diff.txt"
{
    echo "============================================"
    echo "OpenAPI Spec Changes"
    echo "Generated: $(date)"
    echo "============================================"
    echo ""
    echo "Comparing:"
    echo "  OLD: api.yaml (current patched version)"
    echo "  NEW: api.yaml.new (newly downloaded + patched)"
    echo ""
    echo "--------------------------------------------"
    echo "File Statistics"
    echo "--------------------------------------------"
    echo ""

    if [ -f api.yaml ]; then
        OLD_LINES=$(wc -l < api.yaml | tr -d ' ')
        echo "OLD: $OLD_LINES lines"
    else
        OLD_LINES=0
        echo "OLD: (not found)"
    fi

    NEW_LINES=$(wc -l < api.yaml.new | tr -d ' ')
    echo "NEW: $NEW_LINES lines"
    DIFF_LINES=$((NEW_LINES - OLD_LINES))
    if [ $DIFF_LINES -gt 0 ]; then
        echo "Δ: +$DIFF_LINES lines"
    elif [ $DIFF_LINES -lt 0 ]; then
        echo "Δ: $DIFF_LINES lines"
    else
        echo "Δ: no change in line count"
    fi
    echo ""

    echo "--------------------------------------------"
    echo "Detailed Diff"
    echo "--------------------------------------------"
    echo ""
} > "$DIFF_FILE"

# Generate unified diff
if [ -f api.yaml ]; then
    # Use git diff for better formatting if available, otherwise fall back to diff
    if command -v git &> /dev/null && [ -d .git ]; then
        git diff --no-index --no-color api.yaml api.yaml.new >> "$DIFF_FILE" 2>&1 || true
    else
        diff -u api.yaml api.yaml.new >> "$DIFF_FILE" 2>&1 || true
    fi
else
    echo "(No existing api.yaml to compare against)" >> "$DIFF_FILE"
fi

echo "✓ Change report saved to $DIFF_FILE"
echo ""

# Step 4: Summary
echo "============================================"
echo "Summary"
echo "============================================"
echo ""
echo "Files created:"
echo "  api.yaml.downloaded     Original downloaded spec (unpatched)"
echo "  api.yaml.new            New spec with patches applied"
echo "  $DIFF_FILE              Change report"
echo ""

# Show quick summary of changes
if [ -f api.yaml ]; then
    echo "Quick summary of changes:"

    # Count added/removed lines
    ADDED=$(grep -c '^+' "$DIFF_FILE" || true)
    REMOVED=$(grep -c '^-' "$DIFF_FILE" || true)

    echo "  +$ADDED lines added"
    echo "  -$REMOVED lines removed"
    echo ""

    # Show first few changes for context
    echo "First few changes (see $DIFF_FILE for full details):"
    head -100 "$DIFF_FILE" | tail -50 || true
    echo ""
    echo "(Use 'less $DIFF_FILE' to view full diff)"
else
    echo "No existing api.yaml found - this appears to be a fresh setup"
fi
echo ""

# Step 5: Apply changes if requested
if [ "$APPLY_CHANGES" = true ]; then
    echo "============================================"
    echo "Applying Changes"
    echo "============================================"
    echo ""

    # Backup current api.yaml if it exists
    if [ -f api.yaml ]; then
        BACKUP_FILE="api.yaml.backup.$(date +%Y%m%d-%H%M%S)"
        cp api.yaml "$BACKUP_FILE"
        echo "✓ Backed up current api.yaml to $BACKUP_FILE"
    fi

    # Apply new spec
    mv api.yaml.new api.yaml
    echo "✓ Applied new spec to api.yaml"
    echo ""

    echo "Changes applied! Next steps:"
    echo "  1. Review the changes in $DIFF_FILE"
    echo "  2. Regenerate the client: make generate-client"
    echo "  3. Run tests: make ci"
    echo ""
else
    echo "============================================"
    echo "Next Steps"
    echo "============================================"
    echo ""
    echo "Review the changes in $DIFF_FILE"
    echo ""
    echo "If you're satisfied with the changes, apply them:"
    echo "  ./scripts/update-openapi-spec.sh --apply"
    echo ""
    echo "Or apply manually:"
    echo "  mv api.yaml.new api.yaml"
    echo "  make generate-client"
    echo ""
fi

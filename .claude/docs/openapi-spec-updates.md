# OpenAPI Spec Update Process

## Quick Commands

```bash
make update-spec        # Download latest spec, show diff (safe)
make update-spec-apply  # Download, show diff, and apply
make generate-client    # Regenerate client from api.yaml
```

## Files

**Tracked:**
- `api.yaml` - Current spec with patches (source of truth)
- `api.yaml.original` - Backup from first patch
- `scripts/patch-openapi.py` - Applies fixes for code generation
- `scripts/update-openapi-spec.sh` - Update orchestration
- `scripts/generate-client.sh` - Client regeneration

**Temporary (gitignored):**
- `api.yaml.downloaded` - Unpatched download
- `api.yaml.new` - Patched, ready to apply
- `.openapi-diff.txt` - Change report
- `api.yaml.backup.*` - Timestamped backups

## Workflow

1. **Check for updates:**
   ```bash
   make update-spec
   ```
   Downloads latest spec, applies patches, generates diff.

2. **Review changes:**
   ```bash
   less .openapi-diff.txt
   # or
   git diff --no-index api.yaml api.yaml.new
   ```
   Look for: new endpoints, schema changes, deprecated fields, new required fields, removed endpoints.

3. **Apply if satisfied:**
   ```bash
   make update-spec-apply
   ```
   Backs up current `api.yaml`, applies new version.

4. **Regenerate client:**
   ```bash
   make generate-client
   ```
   Regenerates `src/honeycomb/_generated/` (never edit directly).

5. **Test:**
   ```bash
   make ci           # Full pipeline
   make test-live    # Against real API
   ```

6. **Update if needed:**
   - Wrapper code in `src/honeycomb/resources/`
   - Models in `src/honeycomb/models/`
   - Tests and docs

## What the Patches Fix

`patch-openapi.py` corrects upstream spec issues:
- Arrays missing `items` definitions
- Invalid `allOf` with default values
- `type` + `allOf` at same level
- `readOnly` + `allOf` patterns
- Inline objects → named schemas
- Duplicate model name titles

## Troubleshooting

**No changes:** Honeycomb hasn't updated the spec yet.

**Generation fails:** Check patches applied, verify YAML validity, review errors.

**Tests fail:** API changed - review diff, update wrappers/models, document breaking changes.

## Manual Process

```bash
# Download
curl -sSL -o api.yaml.downloaded https://api.honeycomb.io/api.yaml

# Patch
cp api.yaml.downloaded api.yaml.new
poetry run python scripts/patch-openapi.py --input api.yaml.new --output api.yaml.new

# Compare
git diff --no-index api.yaml api.yaml.new > .openapi-diff.txt

# Apply if satisfied
mv api.yaml api.yaml.backup.$(date +%Y%m%d-%H%M%S)
mv api.yaml.new api.yaml

# Regenerate
make generate-client
```

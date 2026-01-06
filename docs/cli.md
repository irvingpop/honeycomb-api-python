# CLI Reference

The Honeycomb CLI provides command-line access to the Honeycomb API for managing triggers, SLOs, boards, queries, and datasets. Available as both `honeycomb` and `hny` (short alias). It's particularly useful for:

- Porting objects between teams and environments
- Automating infrastructure-as-code workflows
- Scripting bulk operations
- Quick exploration and testing

## Installation

### Quick Run (No Install)

Use `uvx` or `pipx run` to run the CLI without installing:

```bash
# Configure authentication
export HONEYCOMB_API_KEY=your_api_key_here

# Using uvx (fastest)
uvx honeycomb-api triggers list

# OR Using pipx run
pipx run honeycomb-api triggers list
```

### Permanent Install

After installing, use the shorter `hny` alias:

```bash
# Using uv (fastest)
uv tool install honeycomb-api

# OR Using pipx
pipx install honeycomb-api

# Then use the short alias
export HONEYCOMB_API_KEY=your_api_key_here
hny triggers list
```

## Quick Start

```bash
# Configure authentication
export HONEYCOMB_API_KEY=your_api_key_here

# List all triggers (environment-wide)
hny triggers list

# Run a quick query
hny query run --count --last-30-minutes

# Export a trigger
hny triggers export trigger-123 --dataset my-dataset > trigger.json

# Import to another environment
export HONEYCOMB_API_KEY=another_api_key
hny triggers create --dataset my-dataset --from-file trigger.json
```

## Authentication

The CLI supports multiple authentication methods, checked in this order:

1. **Explicit flags**: `--api-key` or `--management-key` + `--management-secret`
2. **Environment variables**: `HONEYCOMB_API_KEY` or `HONEYCOMB_MANAGEMENT_KEY` + `HONEYCOMB_MANAGEMENT_SECRET`
3. **Profile from config file**: `--profile <name>` or default profile

### Using Profiles

Profiles allow you to manage multiple environments easily:

```bash
# Add a profile
honeycomb config add-profile production --api-key hcaik_prod_xxx

# Add multiple profiles
honeycomb config add-profile staging --api-key hcaik_staging_xxx

# Set default profile
honeycomb config set-default production

# Use specific profile
honeycomb triggers list --dataset my-dataset --profile staging

# Show all profiles
honeycomb config show
```

Config file location: `~/.honeycomb/config.yaml`

## Commands

### Triggers

Manage triggers (alerts). List queries default to environment-wide (`__all__` datasets):

```bash
# List all triggers (environment-wide)
honeycomb triggers list

# List triggers in specific dataset
honeycomb triggers list --dataset my-dataset

# Get a specific trigger
honeycomb triggers get trigger-123 --dataset my-dataset

# Create from JSON file
honeycomb triggers create --dataset my-dataset --from-file trigger.json

# Update existing trigger
honeycomb triggers update trigger-123 --dataset my-dataset --from-file trigger.json

# Delete trigger
honeycomb triggers delete trigger-123 --dataset my-dataset

# Export for porting
honeycomb triggers export trigger-123 --dataset my-dataset > trigger.json

# Export all triggers to directory
honeycomb triggers export-all --dataset my-dataset --output-dir ./triggers/
```

### SLOs

Manage Service Level Objectives. List queries default to environment-wide (`__all__` datasets):

```bash
# List all SLOs (environment-wide)
honeycomb slos list

# List SLOs in specific dataset
honeycomb slos list --dataset my-dataset

# Get a specific SLO
honeycomb slos get slo-123 --dataset my-dataset

# Create from JSON file
honeycomb slos create --dataset my-dataset --from-file slo.json

# Update existing SLO
honeycomb slos update slo-123 --dataset my-dataset --from-file slo.json

# Delete SLO
honeycomb slos delete slo-123 --dataset my-dataset

# Export for porting
honeycomb slos export slo-123 --dataset my-dataset > slo.json

# Export all SLOs to directory
honeycomb slos export-all --dataset my-dataset --output-dir ./slos/
```

### Boards

Manage boards (dashboards):

```bash
# List all boards
honeycomb boards list

# Get a specific board
honeycomb boards get board-123

# Create from JSON file
honeycomb boards create --from-file board.json

# Update existing board
honeycomb boards update board-123 --from-file board.json

# Delete board
honeycomb boards delete board-123

# Export for porting
honeycomb boards export board-123 > board.json

# Export all boards to directory
honeycomb boards export-all --output-dir ./boards/
```

### Queries

Run and manage queries. List queries default to environment-wide. Command aliases: `queries`, `query`, `q`.

```bash
# List all saved queries (environment-wide)
hny query list

# List queries in specific dataset
hny query list --dataset my-dataset

# Run a query using builder flags (recommended)
hny query run --dataset my-dataset --count --last-30-minutes
hny query run --dataset my-dataset --count --avg duration_ms --where-gte status_code,500 --last-24-hours
hny query run --count --p99 duration_ms --where-equals service,api --group-by endpoint --last-1-hour

# Run a query from JSON file
hny query run --dataset my-dataset --from-file query.json

# Run inline query (JSON spec)
hny query run --dataset my-dataset --spec '{"calculations": [{"op": "COUNT"}], "time_range": 3600}'

# Run existing saved query
hny query run --dataset my-dataset --query-id query-123

# Create (save) a query
hny query create --dataset my-dataset --from-file query.json

# Get query details
hny query get query-123

# Get query results
hny query get-result result-123
```

#### Query Builder Flags

The `run` command supports QueryBuilder methods as CLI flags:

**Calculations** (repeatable for multi-column):
- `--count` - Count results
- `--avg <column>` - Average of column
- `--sum <column>` - Sum of column
- `--min <column>` - Minimum value
- `--max <column>` - Maximum value
- `--p50 <column>` - P50 percentile
- `--p90 <column>` - P90 percentile
- `--p95 <column>` - P95 percentile
- `--p99 <column>` - P99 percentile

**Time Ranges** (mutually exclusive):
- `--time-range <seconds>` - Custom time range
- `--last-10-minutes`
- `--last-30-minutes`
- `--last-1-hour`
- `--last-2-hours`
- `--last-8-hours`
- `--last-24-hours`
- `--last-7-days`

**Filters** (repeatable, format: `column,value`):
- `--where-equals service,api` - Equals filter
- `--where-ne status_code,200` - Not equals
- `--where-gt duration_ms,1000` - Greater than
- `--where-gte status_code,400` - Greater than or equal
- `--where-lt duration_ms,100` - Less than
- `--where-lte status_code,299` - Less than or equal
- `--where-contains path,/api/` - Contains substring
- `--where-exists trace.span_id` - Column exists

**Grouping & Ordering**:
- `--group-by <column>` - Group by column (repeatable)
- `--order-by <field>` - Order by field
- `--limit <n>` - Limit results

### Datasets

Manage datasets:

```bash
# List all datasets
honeycomb datasets list

# Get dataset details
honeycomb datasets get my-dataset

# Create a new dataset
honeycomb datasets create --name "My Dataset" --slug my-dataset --description "Dataset description"

# Update dataset
honeycomb datasets update my-dataset --name "Updated Name" --description "New description"

# Delete dataset (WARNING: deletes all data)
honeycomb datasets delete my-dataset
```

### Markers

Manage markers (event annotations):

```bash
# List all markers in a dataset
honeycomb markers list --dataset my-dataset

# Get a specific marker (filters list results)
honeycomb markers get marker-123 --dataset my-dataset

# Create a marker
honeycomb markers create --dataset my-dataset --from-file marker.json

# Update a marker
honeycomb markers update marker-123 --dataset my-dataset --from-file marker.json

# Delete a marker
honeycomb markers delete marker-123 --dataset my-dataset
```

### Recipients

Manage recipients (notification targets for triggers and SLOs):

```bash
# List all recipients
honeycomb recipients list

# Get a specific recipient
honeycomb recipients get recipient-123

# Create a recipient
honeycomb recipients create --from-file recipient.json

# Update a recipient
honeycomb recipients update recipient-123 --from-file recipient.json

# Delete a recipient
honeycomb recipients delete recipient-123

# Export for porting
honeycomb recipients export recipient-123 > recipient.json

# Export all recipients
honeycomb recipients export-all --output-dir ./recipients/
```

### Derived Columns

Manage derived columns (calculated fields). List queries default to environment-wide:

```bash
# List all derived columns (environment-wide)
honeycomb derived-columns list

# List derived columns in specific dataset
honeycomb derived-columns list --dataset my-dataset

# Get a specific derived column
honeycomb derived-columns get column-123 --dataset my-dataset

# Create a derived column
honeycomb derived-columns create --dataset my-dataset --from-file column.json

# Update a derived column
honeycomb derived-columns update column-123 --dataset my-dataset --from-file column.json

# Delete a derived column
honeycomb derived-columns delete column-123 --dataset my-dataset

# Export for porting
honeycomb derived-columns export column-123 --dataset my-dataset > column.json

# Export all derived columns
honeycomb derived-columns export-all --dataset my-dataset --output-dir ./columns/
```

### Auth

Check API key metadata and permissions:

```bash
# Get auth info (v1 endpoint - API key)
hny auth get

# Get management key info (v2 endpoint)
hny auth get --v2

# Output as JSON
hny auth get --output json

# Use specific profile
hny auth get --profile production
```

The `auth get` command shows:
- Team and environment details (v1)
- Key type and permissions/scopes
- Expiration time (if applicable)
- For management keys (v2): key name, scopes, team info

### Config

Manage CLI configuration:

```bash
# Show configuration and profiles
honeycomb config show

# Add a profile
honeycomb config add-profile <name> --api-key <key>

# Add profile with management key
honeycomb config add-profile <name> --management-key <key> --management-secret <secret>

# Set default profile
honeycomb config set-default <name>

# Remove a profile
honeycomb config remove-profile <name>
```

## Output Formats

All commands support multiple output formats (default: table):

```bash
# Table output (default)
honeycomb triggers list --output table

# JSON output
honeycomb triggers list --output json

# YAML output
honeycomb triggers list --output yaml

# Quiet mode (IDs only)
honeycomb triggers list --quiet
```

## Porting Workflow

The primary use case for the CLI is porting objects between teams or environments:

### Example: Port triggers from production to staging

```bash
# 1. Export from production
honeycomb triggers export-all \
    --dataset my-dataset \
    --profile production \
    --output-dir ./triggers-backup/

# 2. Import to staging
for file in ./triggers-backup/*.json; do
    honeycomb triggers create \
        --dataset my-dataset \
        --profile staging \
        --from-file "$file"
done
```

### Example: Port a board between environments

```bash
# Export from source environment
honeycomb boards export board-123 --profile production > board.json

# Import to target environment
honeycomb boards create --profile staging --from-file board.json
```

## Shell Completion

Enable shell completion for better UX:

```bash
# Bash
honeycomb --install-completion bash

# Zsh
honeycomb --install-completion zsh

# Fish
honeycomb --install-completion fish
```

## Common Options

All commands support these options:

- `--profile <name>` or `-p <name>`: Use a specific profile
- `--api-key <key>`: Override API key
- `--output <format>` or `-o <format>`: Set output format (table, json, yaml)
- `--quiet` or `-q`: Minimal output (IDs only)
- `--help`: Show command help

## Examples

### Export and modify a trigger

```bash
# Export trigger
honeycomb triggers export trigger-123 --dataset prod-api > trigger.json

# Edit trigger.json (change threshold, recipients, etc.)
vi trigger.json

# Import as new trigger
honeycomb triggers create --dataset staging-api --from-file trigger.json
```

### Bulk export all resources from a dataset

```bash
# Create backup directory
mkdir -p backups/my-dataset

# Export all resources
honeycomb triggers export-all --dataset my-dataset --output-dir backups/my-dataset/triggers/
honeycomb slos export-all --dataset my-dataset --output-dir backups/my-dataset/slos/
```

### List all datasets in JSON format

```bash
honeycomb datasets list --output json | jq '.[].slug'
```

## Environment Variables

- `HONEYCOMB_API_KEY`: Default API key
- `HONEYCOMB_MANAGEMENT_KEY`: Management key for v2 endpoints
- `HONEYCOMB_MANAGEMENT_SECRET`: Management secret for v2 endpoints

## Exit Codes

- `0`: Success
- `1`: Error (authentication, validation, API error, etc.)

## See Also

- [API Reference](api/client.md) - Full API documentation
- [Usage Guide](usage/triggers.md) - Python SDK usage examples
- [Honeycomb API Docs](https://docs.honeycomb.io/api/) - Official API documentation

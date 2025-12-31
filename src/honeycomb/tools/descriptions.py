"""Hand-crafted tool descriptions for Claude tool definitions.

Each description follows the quality requirements:
1. What it does (1 sentence)
2. When to use it (1 sentence)
3. Key parameters explained (1-2 sentences)
4. Important caveats/limitations (if any)
"""

# ==============================================================================
# Triggers (Alerts)
# ==============================================================================

TRIGGER_DESCRIPTIONS = {
    "honeycomb_list_triggers": (
        "Lists all triggers (alerts) configured in a Honeycomb dataset. "
        "Use this to discover existing alerting rules before creating new ones or when migrating from another observability platform. "
        "Requires the dataset slug parameter to specify which dataset's triggers to retrieve. "
        "Returns a list of trigger objects with their IDs, names, thresholds, and recipient configurations."
    ),
    "honeycomb_get_trigger": (
        "Retrieves detailed configuration for a specific trigger by ID. "
        "Use this to inspect an existing trigger's query specification, threshold settings, frequency, and recipients before modifying or replicating it. "
        "Requires both the dataset slug and trigger ID parameters. "
        "Returns the complete trigger configuration including the query spec, threshold operator and value, evaluation frequency, and notification recipients."
    ),
    "honeycomb_create_trigger": (
        "Creates a new trigger (alert) that fires when query results cross a threshold. "
        "Use this when setting up alerting rules for service health monitoring, error rates, latency thresholds, or when migrating Datadog monitors to Honeycomb. "
        "Requires a dataset, query specification with calculations and filters, threshold operator and value, and evaluation frequency in seconds. "
        "The query can be provided inline with calculations, filters, and time range. "
        "IMPORTANT: Recipients can be provided inline using the 'recipients' array - each recipient needs 'type' (email/webhook/slack/pagerduty/msteams) and 'target' (email address/URL/channel). "
        "Inline recipient creation is PREFERRED - create trigger and recipients in one call for efficiency. Alternatively, you can reference existing recipient IDs. "
        "Note: Trigger queries have a maximum time_range of 3600 seconds (1 hour) and support only a single calculation."
    ),
    "honeycomb_update_trigger": (
        "Updates an existing trigger's configuration including its query, threshold, frequency, or recipients. "
        "Use this to adjust alerting thresholds, change notification targets, or update query filters as service behavior evolves. "
        "Requires the dataset slug, trigger ID, and the complete updated trigger configuration. "
        "Note: This replaces the entire trigger configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_trigger": (
        "Permanently deletes a trigger from Honeycomb. "
        "Use this when decommissioning services, consolidating redundant alerts, or cleaning up test triggers. "
        "Requires both the dataset slug and trigger ID. "
        "Warning: This action cannot be undone. The trigger will stop firing immediately and historical alert data will be lost."
    ),
}

# ==============================================================================
# SLOs (Service Level Objectives)
# ==============================================================================

SLO_DESCRIPTIONS = {
    "honeycomb_list_slos": (
        "Lists all Service Level Objectives (SLOs) defined in a Honeycomb dataset. "
        "Use this to discover existing SLOs, review service reliability targets, or before creating related burn alerts. "
        "Requires the dataset slug parameter. "
        "Returns a list of SLO objects with their IDs, names, target percentages, time periods, and SLI (Service Level Indicator) definitions."
    ),
    "honeycomb_get_slo": (
        "Retrieves detailed configuration for a specific SLO by ID. "
        "Use this to inspect an SLO's target percentage, time period, SLI expression, and associated burn alerts. "
        "Requires both the dataset slug and SLO ID. "
        "Returns the complete SLO configuration including the derived column used for the SLI calculation."
    ),
    "honeycomb_create_slo": (
        "Creates a new Service Level Objective (SLO) to track reliability targets, with automatic derived column creation if needed. "
        "IMPORTANT: Use this tool (not honeycomb_create_derived_column) when you want to create an SLO - it will create both the SLI derived column AND the SLO in one operation. "
        "Use this when defining reliability targets for services, such as 99.9% availability or p99 latency targets. "
        "Requires a dataset, SLO name, target (as percentage, per-million, or nines), time period in days, and an SLI definition. "
        "For the SLI, provide an alias and optionally an expression - if expression is provided, a new derived column is created inline; if only alias is provided, it uses an existing derived column. "
        "You can also add burn alerts inline to notify when error budget depletes too quickly. "
        "Supports both single-dataset and multi-dataset SLOs."
    ),
    "honeycomb_update_slo": (
        "Updates an existing SLO's target percentage, time period, or SLI configuration. "
        "Use this to adjust reliability targets as service requirements change or to associate different derived columns. "
        "Requires the dataset slug, SLO ID, and the complete updated SLO configuration. "
        "Note: This replaces the entire SLO configuration. To update burn alerts separately, use burn alert tools instead."
    ),
    "honeycomb_delete_slo": (
        "Permanently deletes an SLO from Honeycomb. "
        "Use this when decommissioning services, consolidating reliability metrics, or removing test SLOs. "
        "Requires both the dataset slug and SLO ID. "
        "Warning: This action cannot be undone. Associated burn alerts will also be deleted."
    ),
}

# ==============================================================================
# Burn Alerts (SLO Budget Alerts)
# ==============================================================================

BURN_ALERT_DESCRIPTIONS = {
    "honeycomb_list_burn_alerts": (
        "Lists all burn alerts configured for a specific SLO. "
        "Use this to discover existing error budget alerts before creating new ones or when reviewing SLO alerting configuration. "
        "Requires both the dataset slug and SLO ID parameters. "
        "Returns a list of burn alert objects with their IDs, alert types (exhaustion_time or budget_rate), thresholds, and recipients."
    ),
    "honeycomb_get_burn_alert": (
        "Retrieves detailed configuration for a specific burn alert by ID. "
        "Use this to inspect an existing burn alert's threshold, alert type, and recipient configuration. "
        "Requires both the dataset slug and burn alert ID. "
        "Returns the complete burn alert configuration including the SLO it's attached to."
    ),
    "honeycomb_create_burn_alert": (
        "Creates a new burn alert that fires when an SLO's error budget is depleting too quickly. "
        "Use this to get early warning when service reliability is degrading, before completely exhausting your error budget. "
        "Requires a dataset, the SLO ID to attach to, alert type (exhaustion_time or budget_rate), and threshold value. "
        "For exhaustion_time alerts, specify the threshold in minutes (fires when budget will be exhausted in X minutes). "
        "For budget_rate alerts, specify threshold as percentage drop within a time window. "
        "Recipients are OPTIONAL - omit them to create a silent alert, or include inline recipients "
        "(type + target) to create and attach them automatically."
    ),
    "honeycomb_update_burn_alert": (
        "Updates an existing burn alert's threshold, recipients, or alert type. "
        "Use this to adjust alerting sensitivity as you learn about your service's error budget consumption patterns. "
        "Requires the dataset slug, burn alert ID, and the complete updated burn alert configuration. "
        "Note: This replaces the entire burn alert configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_burn_alert": (
        "Permanently deletes a burn alert from an SLO. "
        "Use this when adjusting SLO alerting strategy or removing redundant burn alerts. "
        "Requires both the dataset slug and burn alert ID. "
        "Warning: This action cannot be undone. The alert will stop firing immediately."
    ),
}

# ==============================================================================
# Datasets
# ==============================================================================

DATASET_DESCRIPTIONS = {
    "honeycomb_list_datasets": (
        "Lists all datasets in your Honeycomb environment (no parameters required). "
        "Use this to discover existing datasets before creating new ones, when setting up observability for a new service, or when migrating data from another platform. "
        "This operation requires no parameters - it automatically lists all datasets you have access to. "
        "Returns a list of dataset objects including their slugs, names, descriptions, and metadata like creation timestamps and column counts."
    ),
    "honeycomb_get_dataset": (
        "Retrieves detailed information about a specific dataset by its slug. "
        "Use this to inspect a dataset's configuration including its name, description, JSON expansion settings, and usage statistics. "
        "Requires the dataset slug parameter. "
        "Returns the complete dataset configuration including creation timestamp, last written timestamp, and regular columns count."
    ),
    "honeycomb_create_dataset": (
        "Creates a new dataset to store telemetry data in Honeycomb. "
        "Use this when setting up observability for a new service, creating test environments, or segmenting data by application or team. "
        "Requires a name parameter which will be converted to a URL-safe slug. "
        "Optional parameters include description for documentation and expand_json_depth (0-10) to automatically expand nested JSON fields into separate columns. "
        "The dataset slug will be automatically generated from the name and used for API operations."
    ),
    "honeycomb_update_dataset": (
        "Updates an existing dataset's name, description, or JSON expansion settings. "
        "Use this to correct dataset metadata, add documentation, or adjust JSON parsing behavior as your schema evolves. "
        "Requires the dataset slug and the complete updated configuration. "
        "Note: The slug itself cannot be changed. Changing expand_json_depth only affects new events, not existing data."
    ),
    "honeycomb_delete_dataset": (
        "Permanently deletes a dataset and all its data from Honeycomb. "
        "Use this when decommissioning services, cleaning up test datasets, or consolidating data storage. "
        "Requires the dataset slug parameter. "
        "Warning: This action cannot be undone. All events, columns, queries, triggers, and SLOs in this dataset will be permanently deleted."
    ),
}

# ==============================================================================
# Columns
# ==============================================================================

COLUMN_DESCRIPTIONS = {
    "honeycomb_list_columns": (
        "Lists all columns defined in a dataset's schema. "
        "Use this to discover available fields for querying, understand your data structure, or validate that new columns are being sent correctly. "
        "Requires the dataset slug parameter. "
        "Returns a list of column objects including their IDs, key names, types (string, integer, float, boolean), descriptions, hidden status, and timestamps."
    ),
    "honeycomb_get_column": (
        "Retrieves detailed information about a specific column by its ID. "
        "Use this to inspect a column's configuration including its data type, visibility, description, and usage statistics. "
        "Requires both the dataset slug and column ID parameters. "
        "Returns the complete column configuration including creation timestamp, last update timestamp, and last written timestamp."
    ),
    "honeycomb_create_column": (
        "Creates a new column in a dataset's schema. "
        "Use this to pre-define columns before sending data, add metadata like descriptions, or create hidden columns for internal fields. "
        "Requires the dataset slug and key_name (the column identifier). "
        "Optional parameters include type (string, integer, float, boolean - defaults to string), description for documentation, and hidden flag to exclude from autocomplete. "
        "Columns are automatically created when new fields appear in events, but pre-defining them allows you to set type and visibility."
    ),
    "honeycomb_update_column": (
        "Updates an existing column's description, type, or visibility settings. "
        "Use this to add documentation to columns, change data types, or hide internal debugging fields from query builders. "
        "Requires the dataset slug, column ID, and the complete updated column configuration. "
        "Note: Changing the type doesn't convert existing data, it only affects how the column is displayed and queried in the UI."
    ),
    "honeycomb_delete_column": (
        "Permanently deletes a column from a dataset's schema. "
        "Use this when cleaning up unused columns or removing fields that are no longer being sent. "
        "Requires both the dataset slug and column ID parameters. "
        "Warning: This action cannot be undone. The column definition will be removed, but existing event data containing this field is preserved."
    ),
}

# ==============================================================================
# Recipients
# ==============================================================================

RECIPIENT_DESCRIPTIONS = {
    "honeycomb_list_recipients": (
        "Lists all notification recipients configured in your Honeycomb environment (no parameters required). "
        "Use this to discover existing notification targets before creating triggers, avoid duplicate recipients, or audit alerting destinations. "
        "This operation requires no parameters - it automatically lists all recipients across all types (email, Slack, PagerDuty, webhooks, MS Teams). "
        "Returns a list of recipient objects including their IDs, types, and configuration details."
    ),
    "honeycomb_get_recipient": (
        "Retrieves detailed configuration for a specific recipient by ID. "
        "Use this to inspect a recipient's type and delivery details before updating it or when troubleshooting notification issues. "
        "Requires the recipient ID parameter. "
        "Returns the complete recipient configuration including type-specific details like email addresses, Slack channels, or webhook URLs."
    ),
    "honeycomb_create_recipient": (
        "Creates a new notification recipient for alert delivery. "
        "Use this when setting up alerting for triggers or burn alerts, adding new on-call notification channels, or migrating alert destinations from another platform. "
        "Requires a type (email, slack, pagerduty, webhook, msteams) and type-specific details object. "
        "For email: provide 'email_address'. For Slack: provide 'channel'. For PagerDuty: provide 'routing_key'. For webhooks: provide 'url' and optionally 'secret'. "
        "Recipients can be referenced by ID when creating or updating triggers and burn alerts."
    ),
    "honeycomb_update_recipient": (
        "Updates an existing recipient's configuration including its type or delivery details. "
        "Use this to change notification destinations, update Slack channels, rotate webhook secrets, or fix incorrect email addresses. "
        "Requires the recipient ID and the complete updated recipient configuration. "
        "Note: This replaces the entire recipient configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_recipient": (
        "Permanently deletes a recipient from Honeycomb. "
        "Use this when removing unused notification channels, cleaning up test recipients, or decommissioning alert destinations. "
        "Requires the recipient ID parameter. "
        "Warning: This action cannot be undone. Any triggers or burn alerts using this recipient will have it removed from their notification list."
    ),
    "honeycomb_get_recipient_triggers": (
        "Retrieves all triggers that are configured to send notifications to a specific recipient. "
        "Use this before deleting a recipient to understand impact, when auditing alert routing, or troubleshooting why notifications aren't being sent. "
        "Requires the recipient ID parameter. "
        "Returns a list of trigger objects that reference this recipient, showing which datasets and alerts would be affected by changes."
    ),
}

# ==============================================================================
# Derived Columns
# ==============================================================================

DERIVED_COLUMN_DESCRIPTIONS = {
    "honeycomb_list_derived_columns": (
        "Lists all derived columns (calculated fields) in a dataset. "
        "Use this to discover existing calculated fields before creating new ones, understand available computed metrics, or audit data transformations. "
        "Requires the dataset slug parameter (use '__all__' to list environment-wide derived columns). "
        "Returns a list of derived column objects including their IDs, aliases, expressions, and descriptions."
    ),
    "honeycomb_get_derived_column": (
        "Retrieves detailed configuration for a specific derived column by ID. "
        "Use this to inspect a derived column's expression syntax, alias, and description before modifying it. "
        "Requires both the dataset slug and derived column ID parameters. "
        "Returns the complete derived column configuration including the calculation expression and metadata."
    ),
    "honeycomb_create_derived_column": (
        "Creates a new standalone derived column that calculates values from event fields using expressions. "
        "Use this for general-purpose computed metrics, data normalization, or calculations that will be used in multiple queries. "
        "NOTE: If you are creating a derived column specifically for an SLO, use honeycomb_create_slo instead with an inline SLI expression - it creates both in one operation. "
        "Requires the dataset slug (use '__all__' for environment-wide), an alias (the column name), and an expression using Honeycomb's query language. "
        "Common expression functions include IF() for conditionals, EQUALS/LT/GT for comparisons, and field references with $ prefix (e.g., $status_code). "
        "Optional description parameter documents the column's purpose for team members."
    ),
    "honeycomb_update_derived_column": (
        "Updates an existing derived column's alias, expression, or description. "
        "Use this to fix calculation logic, rename computed fields, or improve documentation as your understanding evolves. "
        "Requires the dataset slug, derived column ID, and the complete updated configuration. "
        "Note: Changing the expression only affects new queries - existing query results are not recalculated."
    ),
    "honeycomb_delete_derived_column": (
        "Permanently deletes a derived column from a dataset. "
        "Use this when removing unused calculated fields or cleaning up temporary analysis columns. "
        "Requires both the dataset slug and derived column ID parameters. "
        "Warning: This action cannot be undone. SLOs, triggers, or queries using this derived column may break if they reference it."
    ),
}

# ==============================================================================
# Queries
# ==============================================================================

QUERY_DESCRIPTIONS = {
    "honeycomb_create_query": (
        "Creates a new saved query in a dataset that can be reused in boards, analysis, or referenced by ID. "
        "Use this to save frequently-used queries, create queries for dashboard panels, or prepare queries for trigger definitions. "
        "Requires the dataset slug and query specification including time_range and calculations. "
        "Optional annotation_name parameter creates the query with a display name for easier identification in the UI. "
        "The query specification supports multiple calculations (unlike triggers which allow only one), filters, breakdowns, orders, havings, and limits for comprehensive data analysis."
    ),
    "honeycomb_get_query": (
        "Retrieves a saved query's configuration by its ID. "
        "Use this to inspect an existing query's calculations, filters, time range, and other settings before modifying it or using it as a template. "
        "Requires both the dataset slug and query ID parameters. "
        "Returns the complete query specification including all calculation definitions, filter conditions, breakdown fields, and ordering rules."
    ),
    "honeycomb_run_query": (
        "Creates a saved query, executes it, and returns results with automatic polling until completion. "
        "Use this for ad-hoc data analysis, investigating issues, or when you want both a saved query and immediate results in one operation. "
        "Requires the dataset slug (or '__all__' for environment-wide queries) and query specification (time_range, calculations, optional filters/breakdowns/orders/havings/limit). "
        "This tool performs two operations: first creates a permanent saved query, then executes it with polling and returns the query results including data rows and metadata. "
        "Supports all query features including multiple calculations (COUNT, AVG, SUM, MIN, MAX, P50-P99, HEATMAP, RATE_*), complex filters, breakdowns, ordering, HAVING clauses, and result limits."
    ),
}

# ==============================================================================
# Boards
# ==============================================================================

BOARD_DESCRIPTIONS = {
    "honeycomb_list_boards": (
        "Lists all boards (dashboards) in your Honeycomb environment (no parameters required). "
        "Use this to discover existing dashboards before creating new ones, audit dashboard organization, or find boards to update. "
        "This operation requires no parameters - it automatically lists all boards you have access to. "
        "Returns a list of board objects including their IDs, names, descriptions, panel configurations, and layout settings."
    ),
    "honeycomb_get_board": (
        "Retrieves detailed configuration for a specific board by its ID. "
        "Use this to inspect a board's panel layout, query configurations, SLO displays, and text content before modifying it. "
        "Requires the board ID parameter. "
        "Returns the complete board configuration including all panel definitions, layout mode (auto or manual), tags, and links to visualizations."
    ),
    "honeycomb_create_board": (
        "Creates a new board (dashboard) with inline query panels, SLO panels, and text panels in a single operation. "
        "Use this to build comprehensive dashboards for service monitoring, create SRE views, or consolidate related visualizations. "
        "Requires a name and supports inline_query_panels (array of query definitions that will be created automatically), text_panels (markdown content), and slo_panels (SLO IDs). "
        "Each inline query panel needs a name, dataset, time_range, and calculations - optionally include filters, breakdowns, orders, and limit. "
        "Layout defaults to auto-layout (Honeycomb arranges panels) but supports manual layout with explicit positioning. "
        "The tool orchestrates: creating all inline queries with annotations, assembling panel configurations, and creating the board with all panels in one API call."
    ),
    "honeycomb_update_board": (
        "Updates an existing board's name, description, or panel configuration. "
        "Use this to add new panels, reorder visualizations, update board metadata, or reorganize dashboards as monitoring needs evolve. "
        "Requires the board ID and the complete updated board configuration. "
        "Note: This replaces the entire board configuration, so include all panels you want to preserve."
    ),
    "honeycomb_delete_board": (
        "Permanently deletes a board from Honeycomb. "
        "Use this when removing outdated dashboards, cleaning up test boards, or consolidating overlapping views. "
        "Requires the board ID parameter. "
        "Warning: This action cannot be undone. The board and its panel configurations will be permanently deleted, but the underlying queries and SLOs are preserved."
    ),
}

# ==============================================================================
# Markers
# ==============================================================================

MARKER_DESCRIPTIONS = {
    "honeycomb_list_markers": (
        "Lists all markers (event annotations) in a dataset. "
        "Use this to view deployment history, configuration changes, incidents, or other significant events marked on your data. "
        "Requires the dataset slug parameter. "
        "Returns a list of marker objects including their IDs, messages, types, timestamps, colors, and URLs."
    ),
    "honeycomb_create_marker": (
        "Creates a new marker to annotate your data with significant events like deployments, configuration changes, or incidents. "
        "Use this to track deployments, mark maintenance windows, document configuration changes, or flag incidents for correlation with metrics. "
        "Requires dataset slug (or '__all__' for environment-wide), message, and type parameters. "
        "Optional color parameter (hex code like '#FF5733') can be provided for visual customization - if the marker setting for that type doesn't exist, it should be created first. "
        "Optional start_time and end_time (Unix timestamps) create time-range markers, otherwise defaults to current time as a point marker."
    ),
    "honeycomb_update_marker": (
        "Updates an existing marker's message, type, timestamps, or URL. "
        "Use this to correct marker details, update deployment notes, or adjust time ranges for maintenance windows. "
        "Requires the dataset slug, marker ID, and updated marker configuration. "
        "Note: Colors are controlled by marker settings, not directly on markers."
    ),
    "honeycomb_delete_marker": (
        "Permanently deletes a marker from a dataset. "
        "Use this when removing incorrect markers, cleaning up test annotations, or removing outdated event tracking. "
        "Requires both the dataset slug and marker ID parameters. "
        "Warning: This action cannot be undone. The marker will be removed from all visualizations."
    ),
}

# ==============================================================================
# Marker Settings
# ==============================================================================

MARKER_SETTING_DESCRIPTIONS = {
    "honeycomb_list_marker_settings": (
        "Lists all marker type-to-color mappings for a dataset. "
        "Use this as the primary way to view all marker settings, see which marker types have custom colors, or audit marker visualization configuration. "
        "Requires the dataset slug parameter (or '__all__' for environment-wide settings). "
        "Returns a list of all marker settings showing type names (e.g., 'deploy', 'incident') and their associated hex color codes."
    ),
    "honeycomb_get_marker_setting": (
        "Retrieves a specific marker setting by its ID. "
        "Use this rarely when you need a specific setting by ID - prefer list_marker_settings to view all settings. "
        "Requires both the dataset slug and setting ID parameters. "
        "Returns the marker setting configuration including type name and color code."
    ),
    "honeycomb_create_marker_setting": (
        "Creates a new marker type-to-color mapping. "
        "Use this to assign colors to marker types for visual consistency (e.g., deployments in green, incidents in red). "
        "Requires the dataset slug (or '__all__' for environment-wide), marker type name, and hex color code (e.g., '#00FF00'). "
        "Once created, all markers of this type will display in the specified color on graphs and timelines."
    ),
    "honeycomb_update_marker_setting": (
        "Updates an existing marker setting's type or color. "
        "Use this to change marker colors for better visual distinction or rename marker types. "
        "Requires the dataset slug, setting ID, and updated configuration (type and color). "
        "The color change applies immediately to all existing and future markers of this type."
    ),
    "honeycomb_delete_marker_setting": (
        "Permanently deletes a marker setting. "
        "Use this when removing unused marker types or resetting color customizations. "
        "Requires both the dataset slug and setting ID parameters. "
        "Warning: Existing markers of this type will lose their custom color and revert to default visualization."
    ),
}

# ==============================================================================
# Events
# ==============================================================================

EVENT_DESCRIPTIONS = {
    "honeycomb_send_event": (
        "Sends a SINGLE telemetry event to a Honeycomb dataset. Use ONLY for one-off events or testing. "
        "STRUCTURE: Flat - parameters are 'dataset' (string) and 'data' (object with key-value pairs) provided directly at top level. "
        "Example: {dataset: 'api-logs', data: {status_code: 200, endpoint: '/api/users'}}. "
        "For 2+ events, you MUST use honeycomb_send_batch_events instead. "
        "Optional parameters: timestamp (Unix seconds), samplerate (integer). "
        "IMPORTANT: This is for SINGLE events only - batch tool is required for multiple events."
    ),
    "honeycomb_send_batch_events": (
        "Sends MULTIPLE telemetry events to a Honeycomb dataset in a single API call (preferred for 2+ events). "
        "STRUCTURE: Nested - requires 'dataset' (string) and 'events' (array) where EACH event object has a 'data' field. "
        "Example: {dataset: 'api-logs', events: [{data: {status_code: 200}}, {data: {status_code: 201}}]}. "
        "CRITICAL: The 'events' parameter is REQUIRED and must be an ARRAY of event objects. Each event MUST have a 'data' field containing key-value pairs. "
        "Per-event optional fields: 'time' (ISO8601 string like '2024-01-15T10:30:00Z'), 'samplerate' (integer). "
        "Use this for efficient bulk data ingestion, application logs, traces, or metrics. "
        "Returns status for each event, allowing identification and retry of failed events."
    ),
}

# ==============================================================================
# Service Map Dependencies
# ==============================================================================

SERVICE_MAP_DESCRIPTIONS = {
    "honeycomb_query_service_map": (
        "Queries service dependencies and relationships from distributed trace data with automatic polling and pagination. "
        "Use this to discover service-to-service call patterns, identify dependencies, visualize system architecture, or debug cross-service issues. "
        "Requires a time range specification (time_range in seconds, or start_time/end_time as Unix timestamps). "
        "Optional filters parameter allows narrowing to specific services by name. "
        "This tool performs create + poll + paginate operations automatically: creates async query, polls until ready, fetches all pages of results (up to 64K dependencies). "
        "Warning: Large time ranges may return thousands of dependencies across hundreds of API pages - use max_pages parameter to limit."
    ),
}

# ==============================================================================
# Auth
# ==============================================================================

AUTH_DESCRIPTIONS = {
    "honeycomb_get_auth": (
        "Returns metadata about the API key used to authenticate with Honeycomb. "
        "Use this to verify authentication is working correctly, check key permissions and scopes, "
        "or discover which team and environment the key belongs to. "
        "Automatically detects whether to use the v1 endpoint (for regular API keys) or "
        "v2 endpoint (for management keys) based on the configured credentials. "
        "Set use_v2=true to explicitly request management key information, which includes "
        "scopes and team details. Returns an error if use_v2=true but management credentials "
        "are not configured."
    ),
}

# ==============================================================================
# API Keys (v2)
# ==============================================================================

API_KEY_DESCRIPTIONS = {
    "honeycomb_list_api_keys": (
        "Lists all API keys for your authenticated team with optional filtering by key type. "
        "Use this to audit team API keys, discover existing keys before creating new ones, or when migrating to management key authentication. "
        "Requires management key authentication. The team is automatically detected from your credentials (no team parameter needed). "
        "Optional key_type parameter filters by 'ingest' or 'configuration' keys. "
        "Returns a list of API key objects with their IDs, names, types, environment associations, and disabled status. "
        "Note: The key secrets are not included in list responses for security."
    ),
    "honeycomb_get_api_key": (
        "Retrieves detailed information about a specific API key by ID. "
        "Use this to inspect an API key's configuration including name, type, environment, and disabled status before updating or deleting it. "
        "Requires only the key ID parameter - the team is automatically detected from your management key credentials. "
        "Returns the complete API key configuration but does NOT include the secret (only shown on creation). "
        "Use this to verify key settings or check which environment a key is associated with."
    ),
    "honeycomb_create_api_key": (
        "Creates a new API key for your authenticated team in a specific environment. "
        "Use this when provisioning new services, creating separate keys for different applications, or rotating credentials. "
        "Requires key name, key_type ('ingest' for data sending or 'configuration' for API access), and environment_id. The team is automatically detected from your management key. "
        "CRITICAL FOR CONFIGURATION KEYS: Must include permissions object with boolean properties. Available permissions: 'create_datasets', 'send_events', 'manage_markers', 'manage_triggers', 'manage_boards', 'run_queries', 'manage_columns', 'manage_slos', 'manage_recipients', 'manage_privateBoards'. "
        "Example for full access: {'create_datasets': true, 'send_events': true, 'manage_markers': true, 'manage_triggers': true, 'manage_boards': true, 'run_queries': true, 'manage_columns': true, 'manage_slos': true, 'manage_recipients': true, 'manage_privateBoards': true}. "
        "Without permissions object, configuration keys will have NO permissions and cannot perform any actions. "
        "Ingest keys have fixed permissions (send events, optionally create datasets implicitly) and don't use permissions object. "
        "CRITICAL: The secret is only returned once during creation - save it immediately. "
        "Returns the created API key object including the secret field (only time it's available)."
    ),
    "honeycomb_update_api_key": (
        "Updates an existing API key's name or disabled status. "
        "Use this to rename keys for clarity, disable compromised keys, or re-enable previously disabled keys. "
        "Requires key ID and at least one of: name (new display name) or disabled (true/false). The team is automatically detected from your credentials. "
        "Note: You cannot change the key type or environment after creation. To rotate the secret, delete and create a new key. "
        "The secret value is never returned in update responses."
    ),
    "honeycomb_delete_api_key": (
        "Permanently deletes an API key from Honeycomb. "
        "Use this when decommissioning services, rotating credentials after a security incident, or cleaning up unused keys. "
        "Requires only the key ID parameter - the team is automatically detected from your management key. "
        "Warning: This action cannot be undone. Any services using this key will immediately lose API access. "
        "The secret cannot be recovered - you must create a new key if deleted accidentally."
    ),
}

# ==============================================================================
# Environments (v2)
# ==============================================================================

ENVIRONMENT_DESCRIPTIONS = {
    "honeycomb_list_environments": (
        "Lists all environments for your authenticated team. "
        "Use this to discover existing environments, understand team organization, or before creating API keys scoped to specific environments. "
        "Requires management key authentication. The team is automatically detected from your credentials (no team parameter needed). "
        "Returns a list of environment objects with their IDs, names, slugs, colors, descriptions, and delete protection status. "
        "Environments help organize your telemetry data by separating production, staging, development, etc."
    ),
    "honeycomb_get_environment": (
        "Retrieves detailed information about a specific environment by ID, optionally including its datasets. "
        "Use this to inspect an environment's configuration or get a complete view of an environment including all its datasets. "
        "Requires only the environment ID parameter - the team is automatically detected from your management key. "
        "Set with_datasets=true to also return the list of datasets in this environment (useful for understanding environment contents). "
        "Returns the environment configuration plus optionally a datasets array with all datasets in this environment."
    ),
    "honeycomb_create_environment": (
        "Creates a new environment for organizing telemetry data within your authenticated team. "
        "Use this when setting up new deployment stages (production, staging, dev), isolating customer data, or creating test environments. "
        "Requires only the environment name - the team is automatically detected from your management key. "
        "Optional parameters include description for documentation and color (blue, green, gold, red, purple, or light variants) for visual distinction. "
        "The environment slug is auto-generated from the name and used for API operations and dataset scoping. "
        "New environments are delete-protected by default to prevent accidental deletion."
    ),
    "honeycomb_update_environment": (
        "Updates an existing environment's description, color, or delete protection status. "
        "Use this to add documentation, change visual appearance, or enable/disable delete protection for production environments. "
        "Requires environment ID and at least one of: description, color, or delete_protected (boolean). The team is automatically detected from your credentials. "
        "Note: The name and slug cannot be changed after creation. Setting delete_protected=true prevents accidental deletion. "
        "To delete a protected environment, you must first update it with delete_protected=false."
    ),
    "honeycomb_delete_environment": (
        "Permanently deletes an environment from Honeycomb. "
        "Use this when decommissioning deployment stages, cleaning up test environments, or reorganizing team structure. "
        "Requires only the environment ID parameter - the team is automatically detected from your management key. "
        "Warning: This action cannot be undone. The environment must not be delete-protected. "
        "All API keys scoped to this environment will become invalid. Datasets are NOT deleted automatically."
    ),
}

# Combined mapping of all descriptions
ALL_DESCRIPTIONS = {
    **TRIGGER_DESCRIPTIONS,
    **SLO_DESCRIPTIONS,
    **BURN_ALERT_DESCRIPTIONS,
    **DATASET_DESCRIPTIONS,
    **COLUMN_DESCRIPTIONS,
    **RECIPIENT_DESCRIPTIONS,
    **DERIVED_COLUMN_DESCRIPTIONS,
    **QUERY_DESCRIPTIONS,
    **BOARD_DESCRIPTIONS,
    **MARKER_DESCRIPTIONS,
    **MARKER_SETTING_DESCRIPTIONS,
    **EVENT_DESCRIPTIONS,
    **SERVICE_MAP_DESCRIPTIONS,
    **AUTH_DESCRIPTIONS,
    **API_KEY_DESCRIPTIONS,
    **ENVIRONMENT_DESCRIPTIONS,
}


def get_description(tool_name: str) -> str:
    """Get the hand-crafted description for a tool.

    Args:
        tool_name: The tool name (e.g., "honeycomb_create_trigger")

    Returns:
        The description string

    Raises:
        KeyError: If tool name not found
    """
    if tool_name not in ALL_DESCRIPTIONS:
        raise KeyError(
            f"No description found for tool '{tool_name}'. "
            f"Available tools: {', '.join(sorted(ALL_DESCRIPTIONS.keys()))}"
        )
    return ALL_DESCRIPTIONS[tool_name]


def validate_description(description: str, min_length: int = 50) -> None:
    """Validate a description meets quality requirements.

    Args:
        description: The description to validate
        min_length: Minimum character count (default 50)

    Raises:
        ValueError: If description is invalid
    """
    if not description:
        raise ValueError("Description cannot be empty")

    if len(description) < min_length:
        raise ValueError(
            f"Description must be at least {min_length} characters (got {len(description)})"
        )

    # Check for placeholder text
    placeholders = ["TODO", "TBD", "FIXME", "XXX"]
    for placeholder in placeholders:
        if placeholder in description.upper():
            raise ValueError(f"Description contains placeholder text: {placeholder}")

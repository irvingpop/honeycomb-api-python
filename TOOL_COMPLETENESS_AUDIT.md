# Tool Definitions Completeness Audit

## Scope

This audit focuses on ensuring our tool definitions and builders support ALL features available through QueryBuilder, SLOBuilder, and related builders.

## Current Status: Priority 1 Resources (Triggers, SLOs, Burn Alerts)

### Triggers (5 tools)

#### ✅ honeycomb_list_triggers
- **Schema:** Simple (dataset only)
- **Completeness:** ✅ Complete

#### ✅ honeycomb_get_trigger
- **Schema:** Simple (dataset + trigger_id)
- **Completeness:** ✅ Complete

#### ⚠️ honeycomb_create_trigger
**Current fields:** dataset, name, description, threshold, frequency, query, query_id, disabled, alert_type, recipients, tags, baseline_details

**Missing/Incomplete:**
1. **threshold.exceeded_limit** - Number of times threshold must be exceeded (1-5)
   - Currently have: op, value
   - Missing: exceeded_limit documentation/examples

2. **query.granularity** - Time granularity in seconds
   - Currently have: time_range, calculations, filters, breakdowns, filter_combination
   - Missing: granularity field

3. **baseline_details** - Historical comparison thresholds
   - Field exists but no examples or documentation
   - Structure: `{offset_minutes: int, comparison_type: "PERCENTAGE" | "ABSOLUTE"}`

4. **tags** - Max 10 tags
   - Field exists but no examples showing structure
   - Structure: `[{"key": "severity", "value": "critical"}]`

5. **query_id** vs **query** - Mutually exclusive
   - Need examples showing both patterns:
     - Inline query (current examples)
     - Reference to saved query (missing examples)

6. **Calculation types** - Limited examples
   - Current: COUNT, P99
   - Missing examples: HEATMAP, CONCURRENCY, COUNT_DISTINCT, RATE_AVG, RATE_SUM, RATE_MAX

7. **Filter operators** - Limited examples
   - Current: =, !=, >, >=, <, <=
   - Missing: contains, does-not-contain, starts-with, in, not-in, exists, does-not-exist

8. **Recipients** - Only show ID format
   - Current: `{"id": "recip-123"}`
   - Missing: Inline recipient format `{"type": "email", "target": "user@example.com"}`

#### ⚠️ honeycomb_update_trigger
Same issues as create_trigger

#### ✅ honeycomb_delete_trigger
- **Schema:** Simple (dataset + trigger_id)
- **Completeness:** ✅ Complete

### SLOs (5 tools)

#### ✅ honeycomb_list_slos
- **Schema:** Simple (dataset only)
- **Completeness:** ✅ Complete

#### ✅ honeycomb_get_slo
- **Schema:** Simple (dataset + slo_id)
- **Completeness:** ✅ Complete

#### ⚠️ honeycomb_create_slo
**Current fields:** dataset, name, description, sli, time_period_days, target_per_million

**Missing/Incomplete:**
1. **Multi-dataset SLOs** - No examples showing multiple datasets
   - Current examples: single dataset
   - Missing: `"datasets": ["api-logs", "web-logs"]` pattern

2. **SLI with new derived column** - Not fully documented
   - Current: Shows `sli.alias` only
   - Missing: Full structure with expression for new derived column:
     ```json
     "sli": {
       "alias": "success_rate",
       "expression": "IF(LT($status_code, 500), 1, 0)",
       "description": "Requests with status < 500"
     }
     ```

3. **Target formats** - Only show target_per_million
   - Missing helper conversions:
     - target_percentage (99.9%)
     - target_nines (3 → 99.9%, 4 → 99.99%)

4. **Burn alerts inline** - Tool definition doesn't show burn_alerts field
   - Current: Separate burn_alerts tools
   - Missing: Creating SLO with burn alerts in single call via SLOBuilder

#### ⚠️ honeycomb_update_slo
Same issues as create_slo

#### ✅ honeycomb_delete_slo
- **Schema:** Simple (dataset + slo_id)
- **Completeness:** ✅ Complete

### Burn Alerts (5 tools)

#### ✅ honeycomb_list_burn_alerts
- **Schema:** Simple (dataset + slo_id)
- **Completeness:** ✅ Complete

#### ✅ honeycomb_get_burn_alert
- **Schema:** Simple (dataset + burn_alert_id)
- **Completeness:** ✅ Complete

#### ⚠️ honeycomb_create_burn_alert
**Current fields:** dataset, alert_type, slo_id, exhaustion_minutes, budget_rate_window_minutes, budget_rate_decrease_threshold_per_million, recipients, description

**Missing/Incomplete:**
1. **Recipients** - Only ID format shown
   - Current: `{"id": "recip-123"}`
   - Missing: Inline formats for email, slack, pagerduty, webhook, msteams

2. **Budget rate alert** - threshold_per_million is confusing
   - Current: budget_rate_decrease_threshold_per_million
   - Need better examples showing percentage → per_million conversion
   - Example: 1% drop = 10,000 per million

3. **Description field** - Optional but not shown in all examples

#### ⚠️ honeycomb_update_burn_alert
Same issues as create_burn_alert

#### ✅ honeycomb_delete_burn_alert
- **Schema:** Simple (dataset + burn_alert_id)
- **Completeness:** ✅ Complete

## Summary

### Completion Status

| Tool | Fields Complete | Examples Complete | Overall |
|------|----------------|-------------------|---------|
| honeycomb_list_triggers | ✅ | ✅ | ✅ 100% |
| honeycomb_get_trigger | ✅ | ✅ | ✅ 100% |
| **honeycomb_create_trigger** | ✅ | ⚠️ | ⚠️ 60% |
| **honeycomb_update_trigger** | ✅ | ⚠️ | ⚠️ 60% |
| honeycomb_delete_trigger | ✅ | ✅ | ✅ 100% |
| honeycomb_list_slos | ✅ | ✅ | ✅ 100% |
| honeycomb_get_slo | ✅ | ✅ | ✅ 100% |
| **honeycomb_create_slo** | ⚠️ | ⚠️ | ⚠️ 50% |
| **honeycomb_update_slo** | ⚠️ | ⚠️ | ⚠️ 50% |
| honeycomb_delete_slo | ✅ | ✅ | ✅ 100% |
| honeycomb_list_burn_alerts | ✅ | ✅ | ✅ 100% |
| honeycomb_get_burn_alert | ✅ | ✅ | ✅ 100% |
| **honeycomb_create_burn_alert** | ✅ | ⚠️ | ⚠️ 70% |
| **honeycomb_update_burn_alert** | ✅ | ⚠️ | ⚠️ 70% |
| honeycomb_delete_burn_alert | ✅ | ✅ | ✅ 100% |

**Overall Completion: 73%** (11/15 tools at 100%)

## Action Items

### High Priority
1. ✅ Add more calculation type examples to trigger definitions (HEATMAP, CONCURRENCY, etc.)
2. ✅ Add more filter operator examples (contains, starts-with, in, exists)
3. ✅ Show inline recipient formats (email, slack, pagerduty)
4. ✅ Document SLI with new derived column creation
5. ✅ Add multi-dataset SLO examples

### Medium Priority
6. ✅ Document threshold.exceeded_limit with examples
7. ✅ Document query.granularity field
8. ✅ Add query_id (saved query reference) examples
9. ✅ Add baseline_details examples
10. ✅ Add tags examples with proper structure

### Low Priority
11. ⚠️ Better budget_rate alert threshold documentation
12. ⚠️ Helper functions for target percentage conversions

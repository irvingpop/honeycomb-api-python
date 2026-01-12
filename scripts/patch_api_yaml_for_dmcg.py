#!/usr/bin/env python3
"""Patch api.yaml to add titles to inline schemas for stable datamodel-codegen output.

This script adds 'title' fields to inline/anonymous schema definitions in the
Honeycomb OpenAPI spec. This allows datamodel-codegen with --use-title-as-name
to generate stable, semantic class names instead of auto-numbered names like
Type1, Details1, etc.

Without this patch:
  - Type1, Type2, Details1, Details2 (88 numbered classes)

With this patch:
  - CreateColumnType, PagerDutyRecipientDetails (5 unused dead code enums remain)

Usage:
    ./scripts/patch_api_yaml_for_dmcg.py api.yaml api-patched.yaml
"""

import argparse
import sys
from pathlib import Path

import yaml


def patch_inline_titles(spec: dict) -> int:
    """Add titles to inline schemas that cause numbered class generation.

    Returns count of titles added.
    """
    patches = 0
    schemas = spec.get("components", {}).get("schemas", {})

    # Patch 1: CreateColumn.type enum -> ColumnType
    if "CreateColumn" in schemas:
        props = schemas["CreateColumn"].get("properties", {})
        if "type" in props and "title" not in props["type"]:
            props["type"]["title"] = "ColumnType"
            patches += 1
            print(f"  ✓ CreateColumn.type -> ColumnType")

    # Patch 2: Recipient details objects -> {Type}RecipientDetails
    recipient_types = [
        "PagerDuty",
        "Email",
        "Slack",
        "Webhook",
        "MSTeams",
        "MSTeamsWorkflow",
    ]

    for recipient_type in recipient_types:
        schema_name = f"{recipient_type}Recipient"
        if schema_name not in schemas:
            continue

        # Recipient schemas use allOf pattern
        all_of = schemas[schema_name].get("allOf", [])
        for item in all_of:
            if not isinstance(item, dict):
                continue
            if "properties" not in item:
                continue
            if "details" not in item["properties"]:
                continue

            details = item["properties"]["details"]
            if "title" not in details:
                details["title"] = f"{recipient_type}RecipientDetails"
                patches += 1
                print(f"  ✓ {schema_name}.details -> {recipient_type}RecipientDetails")

    # Patch 3: Fix DatasetUpdatePayload - make fields optional for partial updates
    if "DatasetUpdatePayload" in schemas:
        if "required" in schemas["DatasetUpdatePayload"]:
            del schemas["DatasetUpdatePayload"]["required"]
            patches += 1
            print(f"  ✓ DatasetUpdatePayload: removed 'required' (UPDATE should be partial)")

    # Patch 4: Make BatchEvent.data required (can't send event without data)
    if "BatchEvent" in schemas:
        schemas["BatchEvent"].setdefault("required", [])
        if "data" not in schemas["BatchEvent"]["required"]:
            schemas["BatchEvent"]["required"].append("data")
            patches += 1
            print(f"  ✓ BatchEvent: added 'data' to required fields")

    # Patch 5: Make burn alert recipients optional (useful for testing/builders)
    burn_alert_schemas = [
        "CreateExhaustionTimeBurnAlertRequest",
        "CreateBudgetRateBurnAlertRequest",
    ]
    for schema_name in burn_alert_schemas:
        if schema_name in schemas:
            all_of = schemas[schema_name].get("allOf", [])
            for item in all_of:
                if isinstance(item, dict) and "required" in item:
                    if "recipients" in item["required"]:
                        item["required"].remove("recipients")
                        patches += 1
                        print(f"  ✓ {schema_name}: removed 'recipients' from required")

    # Patch 6: Fix UpdateBudgetRateBurnAlertRequest title (conflicts with BudgetRateBurnAlert)
    if "UpdateBudgetRateBurnAlertRequest" in schemas:
        if schemas["UpdateBudgetRateBurnAlertRequest"].get("title") == "Budget Rate":
            schemas["UpdateBudgetRateBurnAlertRequest"]["title"] = "UpdateBudgetRateBurnAlert"
            patches += 1
            print(f"  ✓ UpdateBudgetRateBurnAlertRequest: changed title to 'UpdateBudgetRateBurnAlert'")

    # Patch 7: Add additionalProperties: false to recipient details for strict validation
    # This prevents LLMs from hallucinating extra fields
    recipient_detail_schemas = [
        "PagerDutyRecipientDetails",
        "EmailRecipientDetails",
        "SlackRecipientDetails",
        "MSTeamsRecipientDetails",
        "MSTeamsWorkflowRecipientDetails",
        "WebhookRecipientDetails",
    ]

    for recipient_type in recipient_types:
        schema_name = f"{recipient_type}Recipient"
        if schema_name not in schemas:
            continue

        all_of = schemas[schema_name].get("allOf", [])
        for item in all_of:
            if not isinstance(item, dict):
                continue
            if "properties" not in item:
                continue
            if "details" not in item["properties"]:
                continue

            details = item["properties"]["details"]
            if "additionalProperties" not in details:
                details["additionalProperties"] = False
                patches += 1
                print(f"  ✓ {schema_name}.details: added additionalProperties=false")

    # Patch 8: Add x-enum-varnames to FilterOp for usable enum names
    # Without this, = becomes field_, != becomes field__, etc.
    FILTER_OP_VARNAMES = [
        "EQUALS",               # "="
        "NOT_EQUALS",           # "!="
        "GREATER_THAN",         # ">"
        "GREATER_THAN_OR_EQUAL",  # ">="
        "LESS_THAN",            # "<"
        "LESS_THAN_OR_EQUAL",   # "<="
        "STARTS_WITH",          # "starts-with"
        "DOES_NOT_START_WITH",  # "does-not-start-with"
        "ENDS_WITH",            # "ends-with"
        "DOES_NOT_END_WITH",    # "does-not-end-with"
        "EXISTS",               # "exists"
        "DOES_NOT_EXIST",       # "does-not-exist"
        "CONTAINS",             # "contains"
        "DOES_NOT_CONTAIN",     # "does-not-contain"
        "IN",                   # "in"
        "NOT_IN",               # "not-in"
    ]

    if "FilterOp" in schemas:
        schemas["FilterOp"]["x-enum-varnames"] = FILTER_OP_VARNAMES
        patches += 1
        print(f"  ✓ FilterOp: added x-enum-varnames for usable enum names")

    # Patch 9: Add x-enum-varnames to HavingOp (subset of FilterOp)
    HAVING_OP_VARNAMES = [
        "EQUALS",               # "="
        "NOT_EQUALS",           # "!="
        "GREATER_THAN",         # ">"
        "GREATER_THAN_OR_EQUAL",  # ">="
        "LESS_THAN",            # "<"
        "LESS_THAN_OR_EQUAL",   # "<="
    ]

    if "HavingOp" in schemas:
        schemas["HavingOp"]["x-enum-varnames"] = HAVING_OP_VARNAMES
        patches += 1
        print(f"  ✓ HavingOp: added x-enum-varnames for usable enum names")

    # Patch 10: Remove/override problematic defaults from Query schema
    # The spec has example values and API defaults that don't match our usage
    if "Query" in schemas:
        props = schemas["Query"].get("properties", {})

        # Remove bogus timestamp defaults (these are example values, not real defaults)
        if "start_time" in props and "default" in props["start_time"]:
            del props["start_time"]["default"]
            patches += 1
            print(f"  ✓ Query.start_time: removed bogus default timestamp")
        if "end_time" in props and "default" in props["end_time"]:
            del props["end_time"]["default"]
            patches += 1
            print(f"  ✓ Query.end_time: removed bogus default timestamp")

        # Override breakdowns default (spec has ["user_agent"], we want None)
        # We override this in QuerySpec anyway, but removing it from base is cleaner
        if "breakdowns" in props and props["breakdowns"].get("default"):
            props["breakdowns"]["default"] = None
            patches += 1
            print(f"  ✓ Query.breakdowns: changed default from ['user_agent'] to None")

        # Override limit default (spec has 100, we want None for more flexibility)
        # We override this in QuerySpec anyway, but removing it from base is cleaner
        if "limit" in props and props["limit"].get("default"):
            props["limit"]["default"] = None
            patches += 1
            print(f"  ✓ Query.limit: changed default from 100 to None")

    return patches


def main() -> int:
    """Patch api.yaml with inline schema titles."""
    parser = argparse.ArgumentParser(description="Patch api.yaml for datamodel-codegen")
    parser.add_argument("input", type=Path, help="Input api.yaml file")
    parser.add_argument("output", type=Path, help="Output patched api.yaml file")
    args = parser.parse_args()

    print(f"Loading {args.input}...")
    with open(args.input) as f:
        spec = yaml.safe_load(f)

    print("Applying patches...")
    patches = patch_inline_titles(spec)

    print(f"\nWriting {args.output}...")
    with open(args.output, "w") as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n✓ Applied {patches} title patches")
    print(f"  Input:  {args.input}")
    print(f"  Output: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

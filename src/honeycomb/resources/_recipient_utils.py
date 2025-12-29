"""Shared utilities for recipient handling across resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from honeycomb.client import HoneycombClient


async def process_inline_recipients(
    client: HoneycombClient,
    recipients_input: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Process inline recipients with idempotency.

    For each recipient without 'id':
    1. Check if matching recipient exists (by type + target)
    2. Reuse existing ID if found
    3. Create new recipient if not found
    4. Handle 409 conflicts (race conditions)

    Recipients with existing 'id' fields are returned unchanged.

    Args:
        client: HoneycombClient for API calls
        recipients_input: List of recipient specs (may have inline recipients)

    Returns:
        Updated recipients list with all IDs resolved

    Example:
        >>> recipients = [
        ...     {"type": "email", "target": "oncall@example.com"},
        ...     {"id": "existing-recip-id"}
        ... ]
        >>> resolved = await process_inline_recipients(client, recipients)
        >>> # First recipient now has an ID, second unchanged
    """
    from honeycomb.exceptions import HoneycombAPIError
    from honeycomb.models.recipients import RecipientCreate, RecipientType

    # List existing recipients once for idempotent checks
    existing_recipients = await client.recipients.list_async()

    result: list[dict[str, Any]] = []

    for recip in recipients_input:
        if "id" in recip:
            # Already has ID - keep as is
            result.append(recip)
            continue

        # Inline recipient - find existing or create new
        recip_type = RecipientType(recip["type"])
        target = recip["target"]

        # Check if recipient with matching type and target already exists
        existing = None
        for existing_recip in existing_recipients:
            if existing_recip.type == recip_type:
                # Check target match based on type
                existing_target = None
                if recip_type == RecipientType.EMAIL:
                    existing_target = existing_recip.details.get("email_address")
                elif recip_type == RecipientType.SLACK:
                    existing_target = existing_recip.details.get("slack_channel")
                elif recip_type == RecipientType.WEBHOOK or recip_type in (
                    RecipientType.MSTEAMS_WORKFLOW,
                    RecipientType.MSTEAMS,
                ):
                    existing_target = existing_recip.details.get("webhook_url")
                elif recip_type == RecipientType.PAGERDUTY:
                    existing_target = existing_recip.details.get("pagerduty_integration_key")

                if existing_target == target:
                    existing = existing_recip
                    break

        if existing:
            # Reuse existing recipient
            result.append({"id": existing.id})
        else:
            # Create new recipient - build details based on type (matching API spec)
            details = recip.get("details", {})
            if recip_type == RecipientType.EMAIL:
                if "email_address" not in details:
                    details = {"email_address": target}
            elif recip_type == RecipientType.SLACK:
                if "slack_channel" not in details:
                    details = {"slack_channel": target}
            elif recip_type == RecipientType.PAGERDUTY:
                if "pagerduty_integration_key" not in details:
                    details = {
                        "pagerduty_integration_key": target,
                        "pagerduty_integration_name": "PagerDuty Integration",
                    }
            elif recip_type == RecipientType.WEBHOOK:
                if "webhook_url" not in details:
                    details = {
                        "webhook_url": target,
                        "webhook_name": recip.get("name", "Webhook"),
                    }
            elif (
                recip_type
                in (
                    RecipientType.MSTEAMS_WORKFLOW,
                    RecipientType.MSTEAMS,
                )
                and "webhook_url" not in details
            ):
                details = {
                    "webhook_url": target,
                    "webhook_name": "MS Teams",
                }

            # Create recipient via Recipients API
            try:
                recipient_obj = RecipientCreate(type=recip_type, details=details)
                created_recip = await client.recipients.create_async(recipient_obj)
                result.append({"id": created_recip.id})
            except HoneycombAPIError as e:
                if e.status_code == 409:
                    # Conflict - recipient exists but we didn't find it (race condition)
                    # Re-fetch and try to find it
                    existing_recipients = await client.recipients.list_async()
                    found = False
                    for existing_recip in existing_recipients:
                        if existing_recip.type == recip_type:
                            check_target = None
                            if recip_type == RecipientType.EMAIL:
                                check_target = existing_recip.details.get("email_address")
                            elif recip_type == RecipientType.SLACK:
                                check_target = existing_recip.details.get("slack_channel")
                            elif recip_type == RecipientType.WEBHOOK or recip_type in (
                                RecipientType.MSTEAMS_WORKFLOW,
                                RecipientType.MSTEAMS,
                            ):
                                check_target = existing_recip.details.get("webhook_url")
                            elif recip_type == RecipientType.PAGERDUTY:
                                check_target = existing_recip.details.get(
                                    "pagerduty_integration_key"
                                )

                            if check_target == target:
                                result.append({"id": existing_recip.id})
                                found = True
                                break

                    if not found:
                        # Still not found - re-raise original error
                        raise
                else:
                    raise

    return result

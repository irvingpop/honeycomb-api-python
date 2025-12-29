"""Triggers resource for Honeycomb API."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from ..models.triggers import Trigger, TriggerCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient
    from ..models.trigger_builder import TriggerBundle


class TriggersResource(BaseResource):
    """Resource for managing Honeycomb triggers.

    Triggers allow you to define alert conditions on your data
    and receive notifications when those conditions are met.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     triggers = await client.triggers.list(dataset="my-dataset")
        ...     trigger = await client.triggers.get(dataset="my-dataset", trigger_id="abc123")

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     triggers = client.triggers.list(dataset="my-dataset")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, trigger_id: str | None = None) -> str:
        """Build API path for triggers."""
        base = f"/1/triggers/{dataset}"
        if trigger_id:
            return f"{base}/{trigger_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, dataset: str) -> list[Trigger]:
        """List all triggers for a dataset (async).

        Args:
            dataset: Dataset slug.

        Returns:
            List of Trigger objects.
        """
        data = await self._get_async(self._build_path(dataset))
        return self._parse_model_list(Trigger, data)

    async def get_async(self, dataset: str, trigger_id: str) -> Trigger:
        """Get a specific trigger (async).

        Args:
            dataset: Dataset slug.
            trigger_id: Trigger ID.

        Returns:
            Trigger object.
        """
        data = await self._get_async(self._build_path(dataset, trigger_id))
        return self._parse_model(Trigger, data)

    async def create_async(self, dataset: str, trigger: TriggerCreate) -> Trigger:
        """Create a new trigger (async).

        Args:
            dataset: Dataset slug.
            trigger: Trigger configuration.

        Returns:
            Created Trigger object.
        """
        data = await self._post_async(self._build_path(dataset), json=trigger.model_dump_for_api())
        return self._parse_model(Trigger, data)

    async def update_async(self, dataset: str, trigger_id: str, trigger: TriggerCreate) -> Trigger:
        """Update an existing trigger (async).

        Args:
            dataset: Dataset slug.
            trigger_id: Trigger ID.
            trigger: Updated trigger configuration.

        Returns:
            Updated Trigger object.
        """
        data = await self._put_async(
            self._build_path(dataset, trigger_id), json=trigger.model_dump_for_api()
        )
        return self._parse_model(Trigger, data)

    async def delete_async(self, dataset: str, trigger_id: str) -> None:
        """Delete a trigger (async).

        Args:
            dataset: Dataset slug.
            trigger_id: Trigger ID.
        """
        await self._delete_async(self._build_path(dataset, trigger_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, dataset: str) -> list[Trigger]:
        """List all triggers for a dataset.

        Args:
            dataset: Dataset slug.

        Returns:
            List of Trigger objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset))
        return self._parse_model_list(Trigger, data)

    def get(self, dataset: str, trigger_id: str) -> Trigger:
        """Get a specific trigger.

        Args:
            dataset: Dataset slug.
            trigger_id: Trigger ID.

        Returns:
            Trigger object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, trigger_id))
        return self._parse_model(Trigger, data)

    def create(self, dataset: str, trigger: TriggerCreate) -> Trigger:
        """Create a new trigger.

        Args:
            dataset: Dataset slug.
            trigger: Trigger configuration.

        Returns:
            Created Trigger object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=trigger.model_dump_for_api())
        return self._parse_model(Trigger, data)

    def update(self, dataset: str, trigger_id: str, trigger: TriggerCreate) -> Trigger:
        """Update an existing trigger.

        Args:
            dataset: Dataset slug.
            trigger_id: Trigger ID.
            trigger: Updated trigger configuration.

        Returns:
            Updated Trigger object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(
            self._build_path(dataset, trigger_id), json=trigger.model_dump_for_api()
        )
        return self._parse_model(Trigger, data)

    def delete(self, dataset: str, trigger_id: str) -> None:
        """Delete a trigger.

        Args:
            dataset: Dataset slug.
            trigger_id: Trigger ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, trigger_id))

    # -------------------------------------------------------------------------
    # Trigger Bundle creation helpers (async)
    # -------------------------------------------------------------------------

    async def create_from_bundle_async(self, bundle: TriggerBundle) -> Trigger:
        """Create trigger from bundle with recipient orchestration (async).

        Orchestrates:
        1. Create/find inline recipients (idempotent)
        2. Create trigger with recipient IDs

        Args:
            bundle: TriggerBundle from TriggerBuilder.build_bundle()

        Returns:
            Created Trigger object

        Example:
            >>> bundle = (
            ...     TriggerBuilder("High Error Rate")
            ...     .dataset("api-logs")
            ...     .last_30_minutes()
            ...     .count()
            ...     .threshold_gt(100)
            ...     .email("oncall@example.com")
            ...     .build_bundle()
            ... )
            >>> trigger = await client.triggers.create_from_bundle_async(bundle)
        """
        from ._recipient_utils import process_inline_recipients

        # Handle inline recipients with idempotency
        if bundle.inline_recipients:
            processed_recipients = await process_inline_recipients(
                self._client, bundle.inline_recipients
            )

            # Merge with existing recipients in trigger
            existing_recipients = bundle.trigger.recipients or []
            all_recipients = existing_recipients + processed_recipients

            # Create new trigger object with all recipients
            trigger_with_ids = TriggerCreate(
                name=bundle.trigger.name,
                description=bundle.trigger.description,
                threshold=bundle.trigger.threshold,
                frequency=bundle.trigger.frequency,
                query=bundle.trigger.query,
                disabled=bundle.trigger.disabled,
                alert_type=bundle.trigger.alert_type,
                recipients=all_recipients if all_recipients else None,
                tags=bundle.trigger.tags,
                baseline_details=bundle.trigger.baseline_details,
            )
        else:
            trigger_with_ids = bundle.trigger

        # Create trigger
        return await self.create_async(bundle.dataset, trigger_with_ids)

    # -------------------------------------------------------------------------
    # Trigger Bundle creation helpers (sync)
    # -------------------------------------------------------------------------

    def create_from_bundle(self, bundle: TriggerBundle) -> Trigger:
        """Create trigger from bundle with recipient orchestration (sync).

        Orchestrates:
        1. Create/find inline recipients (idempotent)
        2. Create trigger with recipient IDs

        Args:
            bundle: TriggerBundle from TriggerBuilder.build_bundle()

        Returns:
            Created Trigger object

        Raises:
            RuntimeError: If client is in async mode

        Example:
            >>> bundle = (
            ...     TriggerBuilder("High Error Rate")
            ...     .dataset("api-logs")
            ...     .last_30_minutes()
            ...     .count()
            ...     .threshold_gt(100)
            ...     .email("oncall@example.com")
            ...     .build_bundle()
            ... )
            >>> trigger = client.triggers.create_from_bundle(bundle)
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Cannot use sync method with async client. "
                "Use create_from_bundle_async() for async mode, or pass sync=True to client"
            )

        return asyncio.run(self.create_from_bundle_async(bundle))

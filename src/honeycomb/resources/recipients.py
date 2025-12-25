"""Recipients resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List  # noqa: UP035

from ..models.recipients import Recipient, RecipientCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class RecipientsResource(BaseResource):
    """Resource for managing notification recipients.

    Recipients define where to send notifications when triggers fire.
    Supported types include email, Slack, PagerDuty, webhooks, and MS Teams.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     recipients = await client.recipients.list()
        ...     recipient = await client.recipients.create(
        ...         recipient=RecipientCreate(
        ...             type=RecipientType.EMAIL,
        ...             details={"email_address": "alerts@example.com"}
        ...         )
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     recipients = client.recipients.list()
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, recipient_id: str | None = None) -> str:
        """Build API path for recipients."""
        base = "/1/recipients"
        if recipient_id:
            return f"{base}/{recipient_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self) -> list[Recipient]:
        """List all recipients (async).

        Returns:
            List of Recipient objects.
        """
        data = await self._get_async(self._build_path())
        return self._parse_model_list(Recipient, data)

    async def get_async(self, recipient_id: str) -> Recipient:
        """Get a specific recipient (async).

        Args:
            recipient_id: Recipient ID.

        Returns:
            Recipient object.
        """
        data = await self._get_async(self._build_path(recipient_id))
        return self._parse_model(Recipient, data)

    async def create_async(self, recipient: RecipientCreate) -> Recipient:
        """Create a new recipient (async).

        Args:
            recipient: Recipient configuration.

        Returns:
            Created Recipient object.
        """
        data = await self._post_async(self._build_path(), json=recipient.model_dump_for_api())
        return self._parse_model(Recipient, data)

    async def update_async(self, recipient_id: str, recipient: RecipientCreate) -> Recipient:
        """Update an existing recipient (async).

        Args:
            recipient_id: Recipient ID.
            recipient: Updated recipient configuration.

        Returns:
            Updated Recipient object.
        """
        data = await self._put_async(
            self._build_path(recipient_id), json=recipient.model_dump_for_api()
        )
        return self._parse_model(Recipient, data)

    async def delete_async(self, recipient_id: str) -> None:
        """Delete a recipient (async).

        Args:
            recipient_id: Recipient ID.
        """
        await self._delete_async(self._build_path(recipient_id))

    async def get_triggers_async(self, recipient_id: str) -> List[dict[str, Any]]:  # noqa: UP006
        """Get all triggers associated with a recipient (async).

        Args:
            recipient_id: Recipient ID.

        Returns:
            List of trigger objects.
        """
        path = f"{self._build_path(recipient_id)}/triggers"
        data = await self._get_async(path)
        # Return raw dict list as we don't want circular dependency on Trigger model
        return data if isinstance(data, list) else []

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self) -> list[Recipient]:
        """List all recipients.

        Returns:
            List of Recipient objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path())
        return self._parse_model_list(Recipient, data)

    def get(self, recipient_id: str) -> Recipient:
        """Get a specific recipient.

        Args:
            recipient_id: Recipient ID.

        Returns:
            Recipient object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(recipient_id))
        return self._parse_model(Recipient, data)

    def create(self, recipient: RecipientCreate) -> Recipient:
        """Create a new recipient.

        Args:
            recipient: Recipient configuration.

        Returns:
            Created Recipient object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(), json=recipient.model_dump_for_api())
        return self._parse_model(Recipient, data)

    def update(self, recipient_id: str, recipient: RecipientCreate) -> Recipient:
        """Update an existing recipient.

        Args:
            recipient_id: Recipient ID.
            recipient: Updated recipient configuration.

        Returns:
            Updated Recipient object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(self._build_path(recipient_id), json=recipient.model_dump_for_api())
        return self._parse_model(Recipient, data)

    def delete(self, recipient_id: str) -> None:
        """Delete a recipient.

        Args:
            recipient_id: Recipient ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(recipient_id))

    def get_triggers(self, recipient_id: str) -> List[dict[str, Any]]:  # noqa: UP006
        """Get all triggers associated with a recipient.

        Args:
            recipient_id: Recipient ID.

        Returns:
            List of trigger objects.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use get_triggers_async() for async mode, or pass sync=True to client"
            )
        path = f"{self._build_path(recipient_id)}/triggers"
        data = self._get_sync(path)
        return data if isinstance(data, list) else []

"""SLOs resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.burn_alerts import BurnAlertCreate, BurnAlertRecipient
from ..models.slos import SLO, SLOCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient
    from ..models.slo_builder import SLOBundle


class SLOsResource(BaseResource):
    """Resource for managing Honeycomb SLOs (Service Level Objectives).

    SLOs allow you to define and track service level objectives
    based on your data.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     slos = await client.slos.list(dataset="my-dataset")
        ...     slo = await client.slos.get(dataset="my-dataset", slo_id="abc123")

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     slos = client.slos.list(dataset="my-dataset")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, slo_id: str | None = None) -> str:
        """Build API path for SLOs."""
        base = f"/1/slos/{dataset}"
        if slo_id:
            return f"{base}/{slo_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, dataset: str) -> list[SLO]:
        """List all SLOs for a dataset (async).

        Args:
            dataset: Dataset slug.

        Returns:
            List of SLO objects.
        """
        data = await self._get_async(self._build_path(dataset))
        return self._parse_model_list(SLO, data)

    async def get_async(self, dataset: str, slo_id: str) -> SLO:
        """Get a specific SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.

        Returns:
            SLO object.
        """
        data = await self._get_async(self._build_path(dataset, slo_id))
        return self._parse_model(SLO, data)

    async def create_async(self, dataset: str, slo: SLOCreate) -> SLO:
        """Create a new SLO (async).

        Args:
            dataset: Dataset slug.
            slo: SLO configuration.

        Returns:
            Created SLO object.
        """
        data = await self._post_async(self._build_path(dataset), json=slo.model_dump_for_api())
        return self._parse_model(SLO, data)

    async def update_async(self, dataset: str, slo_id: str, slo: SLOCreate) -> SLO:
        """Update an existing SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
            slo: Updated SLO configuration.

        Returns:
            Updated SLO object.
        """
        data = await self._put_async(
            self._build_path(dataset, slo_id), json=slo.model_dump_for_api()
        )
        return self._parse_model(SLO, data)

    async def delete_async(self, dataset: str, slo_id: str) -> None:
        """Delete an SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
        """
        await self._delete_async(self._build_path(dataset, slo_id))

    # -------------------------------------------------------------------------
    # SLO Bundle creation helpers (async)
    # -------------------------------------------------------------------------

    async def create_from_bundle_async(self, bundle: SLOBundle) -> dict[str, SLO]:
        """Create SLO(s) from an SLOBundle with automatic orchestration (async).

        This method handles the full orchestration of creating an SLO bundle:
        1. Creates derived column if needed (environment-wide or dataset-scoped)
        2. Creates SLO (single-dataset or multi-dataset)
        3. Creates burn alerts for the SLO (if configured)

        Args:
            bundle: SLOBundle from SLOBuilder.build()

        Returns:
            Dictionary mapping dataset slugs to created SLO objects.
            For single-dataset SLOs: {"dataset": slo}
            For multi-dataset SLOs: {"dataset1": slo, "dataset2": slo, ...} (same SLO object)

        Example:
            >>> bundle = (
            ...     SLOBuilder("API Availability")
            ...     .dataset("api-logs")
            ...     .target_nines(3)
            ...     .sli(alias="success_rate", expression="IF(LT($status, 400), 1, 0)")
            ...     .exhaustion_alert(
            ...         BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            ...         .exhaustion_minutes(60)
            ...         .email("oncall@example.com")
            ...     )
            ...     .build()
            ... )
            >>> slos = await client.slos.create_from_bundle_async(bundle)
            >>> api_slo = slos["api-logs"]
        """
        created_slos: dict[str, SLO] = {}

        # Step 1: Create derived column if needed
        if bundle.derived_column:
            if bundle.derived_column_environment_wide:
                # Create as environment-wide derived column (use "__all__" dataset)
                await self._client.derived_columns.create_async("__all__", bundle.derived_column)
            else:
                # Create in first dataset (single-dataset SLO)
                await self._client.derived_columns.create_async(
                    bundle.datasets[0], bundle.derived_column
                )

        # Step 2: Create SLO
        is_multi_dataset = bundle.slo.dataset_slugs is not None
        if is_multi_dataset:
            # Multi-dataset SLO: create once via __all__ endpoint
            slo = await self.create_async("__all__", bundle.slo)
            # Add to dict for each dataset
            for dataset in bundle.datasets:
                created_slos[dataset] = slo
        else:
            # Single-dataset SLO: create in the specified dataset
            dataset = bundle.datasets[0]
            slo = await self.create_async(dataset, bundle.slo)
            created_slos[dataset] = slo

        # Step 3: Create burn alerts for the SLO
        # For multi-dataset SLOs, create burn alerts in the first dataset
        burn_alert_dataset = bundle.datasets[0]
        for alert_def in bundle.burn_alerts:
            # Process inline recipients with idempotent handling
            from ._recipient_utils import process_inline_recipients

            processed_recipients = await process_inline_recipients(
                self._client, alert_def.recipients.copy()
            )

            # Convert recipients to BurnAlertRecipient format
            recipients = [BurnAlertRecipient(**recipient) for recipient in processed_recipients]

            # Convert budget rate percent to per-million if needed
            budget_rate_threshold = None
            if alert_def.budget_rate_decrease_percent is not None:
                budget_rate_threshold = int(alert_def.budget_rate_decrease_percent * 10000)

            burn_alert = BurnAlertCreate(
                alert_type=alert_def.alert_type,
                slo_id=slo.id,
                description=alert_def.description,
                exhaustion_minutes=alert_def.exhaustion_minutes,
                budget_rate_window_minutes=alert_def.budget_rate_window_minutes,
                budget_rate_decrease_threshold_per_million=budget_rate_threshold,
                recipients=recipients if recipients else [],
            )

            await self._client.burn_alerts.create_async(burn_alert_dataset, burn_alert)

        return created_slos

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, dataset: str) -> list[SLO]:
        """List all SLOs for a dataset.

        Args:
            dataset: Dataset slug.

        Returns:
            List of SLO objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset))
        return self._parse_model_list(SLO, data)

    def get(self, dataset: str, slo_id: str) -> SLO:
        """Get a specific SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.

        Returns:
            SLO object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, slo_id))
        return self._parse_model(SLO, data)

    def create(self, dataset: str, slo: SLOCreate) -> SLO:
        """Create a new SLO.

        Args:
            dataset: Dataset slug.
            slo: SLO configuration.

        Returns:
            Created SLO object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=slo.model_dump_for_api())
        return self._parse_model(SLO, data)

    def update(self, dataset: str, slo_id: str, slo: SLOCreate) -> SLO:
        """Update an existing SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
            slo: Updated SLO configuration.

        Returns:
            Updated SLO object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(self._build_path(dataset, slo_id), json=slo.model_dump_for_api())
        return self._parse_model(SLO, data)

    def delete(self, dataset: str, slo_id: str) -> None:
        """Delete an SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, slo_id))

    # -------------------------------------------------------------------------
    # SLO Bundle creation helpers (sync)
    # -------------------------------------------------------------------------

    def create_from_bundle(self, bundle: SLOBundle) -> dict[str, SLO]:
        """Create SLO(s) from an SLOBundle with automatic orchestration.

        This method handles the full orchestration of creating an SLO bundle:
        1. Creates derived column if needed (environment-wide or dataset-scoped)
        2. Creates SLO (single-dataset or multi-dataset)
        3. Creates burn alerts for the SLO (if configured)

        Args:
            bundle: SLOBundle from SLOBuilder.build()

        Returns:
            Dictionary mapping dataset slugs to created SLO objects.
            For single-dataset SLOs: {"dataset": slo}
            For multi-dataset SLOs: {"dataset1": slo, "dataset2": slo, ...} (same SLO object)

        Example:
            >>> bundle = (
            ...     SLOBuilder("API Availability")
            ...     .dataset("api-logs")
            ...     .target_nines(3)
            ...     .sli(alias="success_rate", expression="IF(LT($status, 400), 1, 0)")
            ...     .exhaustion_alert(
            ...         BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            ...         .exhaustion_minutes(60)
            ...         .email("oncall@example.com")
            ...     )
            ...     .build()
            ... )
            >>> slos = client.slos.create_from_bundle(bundle)
            >>> api_slo = slos["api-logs"]
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use create_from_bundle_async() for async mode, or pass sync=True to client"
            )

        created_slos: dict[str, SLO] = {}

        # Step 1: Create derived column if needed
        if bundle.derived_column:
            if bundle.derived_column_environment_wide:
                # Create as environment-wide derived column (use "__all__" dataset)
                self._client.derived_columns.create("__all__", bundle.derived_column)
            else:
                # Create in first dataset (single-dataset SLO)
                self._client.derived_columns.create(bundle.datasets[0], bundle.derived_column)

        # Step 2: Create SLO
        is_multi_dataset = bundle.slo.dataset_slugs is not None
        if is_multi_dataset:
            # Multi-dataset SLO: create once via __all__ endpoint
            slo = self.create("__all__", bundle.slo)
            # Add to dict for each dataset
            for dataset in bundle.datasets:
                created_slos[dataset] = slo
        else:
            # Single-dataset SLO: create in the specified dataset
            dataset = bundle.datasets[0]
            slo = self.create(dataset, bundle.slo)
            created_slos[dataset] = slo

        # Step 3: Create burn alerts for the SLO
        # For multi-dataset SLOs, create burn alerts in the first dataset
        burn_alert_dataset = bundle.datasets[0]
        for alert_def in bundle.burn_alerts:
            # Process inline recipients with idempotent handling
            import asyncio

            from ._recipient_utils import process_inline_recipients

            processed_recipients = asyncio.run(
                process_inline_recipients(self._client, alert_def.recipients.copy())
            )

            # Convert recipients to BurnAlertRecipient format
            recipients = [BurnAlertRecipient(**recipient) for recipient in processed_recipients]

            # Convert budget rate percent to per-million if needed
            budget_rate_threshold = None
            if alert_def.budget_rate_decrease_percent is not None:
                budget_rate_threshold = int(alert_def.budget_rate_decrease_percent * 10000)

            burn_alert = BurnAlertCreate(
                alert_type=alert_def.alert_type,
                slo_id=slo.id,
                description=alert_def.description,
                exhaustion_minutes=alert_def.exhaustion_minutes,
                budget_rate_window_minutes=alert_def.budget_rate_window_minutes,
                budget_rate_decrease_threshold_per_million=budget_rate_threshold,
                recipients=recipients if recipients else [],
            )

            self._client.burn_alerts.create(burn_alert_dataset, burn_alert)

        return created_slos

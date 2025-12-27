"""Basic SLO creation examples.

These examples demonstrate creating and managing SLOs.
SLOs require an SLI (a derived column that returns a boolean).
"""

from __future__ import annotations

from honeycomb import HoneycombClient, SLI, SLO, SLOCreate


# start_example:create_slo
async def create_basic_slo(
    client: HoneycombClient, dataset: str, sli_alias: str
) -> str:
    """Create a basic SLO with 99.9% target.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create SLO in
        sli_alias: Alias of the SLI derived column

    Returns:
        The created SLO ID
    """
    slo = await client.slos.create_async(
        dataset,
        SLOCreate(
            name="API Availability",
            description="99.9% availability target for API service",
            sli=SLI(alias=sli_alias),
            time_period_days=30,
            target_per_million=999000,  # 99.9%
        ),
    )
    return slo.id
# end_example:create_slo


# start_example:create_slo_with_targets
async def create_slo_with_targets(
    client: HoneycombClient, dataset: str, sli_alias: str
) -> str:
    """Create an SLO with different target levels.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create SLO in
        sli_alias: Alias of the SLI derived column

    Returns:
        The created SLO ID

    Common target_per_million values:
    - 999000 = 99.9% (3 nines)
    - 999900 = 99.99% (4 nines)
    - 990000 = 99.0% (2 nines)
    - 950000 = 95.0%
    """
    slo = await client.slos.create_async(
        dataset,
        SLOCreate(
            name="API Request Success",
            description="High availability SLO",
            sli=SLI(alias=sli_alias),
            time_period_days=7,  # 7-day rolling window
            target_per_million=995000,  # 99.5%
        ),
    )
    return slo.id
# end_example:create_slo_with_targets


# start_example:list_slos
async def list_slos(client: HoneycombClient, dataset: str) -> list[SLO]:
    """List all SLOs in a dataset.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list SLOs from

    Returns:
        List of SLOs
    """
    slos = await client.slos.list_async(dataset)
    for slo in slos:
        target_pct = slo.target_per_million / 10000
        print(f"{slo.name}: {target_pct}% over {slo.time_period_days} days")
    return slos
# end_example:list_slos


# start_example:get_slo
async def get_slo(client: HoneycombClient, dataset: str, slo_id: str) -> SLO:
    """Get a specific SLO by ID.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO to retrieve

    Returns:
        The SLO object
    """
    slo = await client.slos.get_async(dataset, slo_id)
    print(f"Name: {slo.name}")
    print(f"Target: {slo.target_per_million / 10000}%")
    print(f"Time Period: {slo.time_period_days} days")
    return slo
# end_example:get_slo


# start_example:update_slo
async def update_slo(
    client: HoneycombClient, dataset: str, slo_id: str, sli_alias: str
) -> SLO:
    """Update an existing SLO.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO to update
        sli_alias: SLI alias to use

    Returns:
        The updated SLO
    """
    # Get existing SLO first
    existing = await client.slos.get_async(dataset, slo_id)

    # Update with new values
    updated = await client.slos.update_async(
        dataset,
        slo_id,
        SLOCreate(
            name="Updated API Availability",
            description=existing.description,
            sli=SLI(alias=sli_alias),
            time_period_days=existing.time_period_days,
            target_per_million=999900,  # Increase to 99.99%
        ),
    )
    return updated
# end_example:update_slo


# start_example:delete
async def delete_slo(client: HoneycombClient, dataset: str, slo_id: str) -> None:
    """Delete an SLO.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the SLO
        slo_id: ID of the SLO to delete
    """
    await client.slos.delete_async(dataset, slo_id)
# end_example:delete


# start_example:list_sync
def list_slos_sync(client: HoneycombClient, dataset: str) -> list[SLO]:
    """List SLOs using sync client.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list SLOs from

    Returns:
        List of SLOs
    """
    slos = client.slos.list(dataset)
    for slo in slos:
        print(f"{slo.name}: {slo.target_per_million / 10000}%")
    return slos
# end_example:list_sync


# TEST_ASSERTIONS
async def test_create_slo(client: HoneycombClient, dataset: str, slo_id: str) -> None:
    """Verify the example worked correctly."""
    slo = await client.slos.get_async(dataset, slo_id)
    assert "API Availability" in slo.name
    assert slo.target_per_million == 999000


async def test_list_slos(slos: list[SLO]) -> None:
    """Verify list example worked correctly."""
    assert isinstance(slos, list)


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, slo_id: str) -> None:
    """Clean up resources created by example."""
    await delete_slo(client, dataset, slo_id)

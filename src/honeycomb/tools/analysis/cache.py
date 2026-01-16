"""Cache for analysis tools to reduce API calls during repeated searches.

This module provides caching for datasets, columns, and derived columns
to prevent excessive API calls when tools like honeycomb_search_columns
are called multiple times in an agentic workflow.

Caching is ON by default for all tool calls. The cache is:
- Client-scoped: Each HoneycombClient instance has its own cache
- TTL-based: Entries expire after 5 minutes by default
- Thread-safe: Protected by asyncio.Lock for concurrent coroutine access
"""

import asyncio
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from cachetools import TTLCache

if TYPE_CHECKING:
    from honeycomb import HoneycombClient
    from honeycomb.models import Column, Dataset, DerivedColumn

# Default TTL of 5 minutes
DEFAULT_CACHE_TTL = 300

# Client-scoped caches using WeakKeyDictionary (auto-cleanup when client is GC'd)
_client_caches: WeakKeyDictionary["HoneycombClient", dict[str, TTLCache]] = WeakKeyDictionary()
_cache_lock = asyncio.Lock()


def _get_cache_for_client(
    client: "HoneycombClient", ttl: int = DEFAULT_CACHE_TTL
) -> dict[str, TTLCache]:
    """Get or create cache dict for a client instance."""
    if client not in _client_caches:
        _client_caches[client] = {
            "datasets": TTLCache(maxsize=1000, ttl=ttl),
            "columns": TTLCache(maxsize=50000, ttl=ttl),
            "derived_columns": TTLCache(maxsize=50000, ttl=ttl),
        }
    return _client_caches[client]


async def get_datasets_cached(client: "HoneycombClient") -> list["Dataset"]:
    """Get datasets with caching.

    Args:
        client: HoneycombClient instance

    Returns:
        List of Dataset objects
    """
    async with _cache_lock:
        cache = _get_cache_for_client(client)
        if "all" in cache["datasets"]:
            return cache["datasets"]["all"]

    # Fetch outside lock to avoid blocking other coroutines
    datasets = await client.datasets.list_async()

    async with _cache_lock:
        cache = _get_cache_for_client(client)
        cache["datasets"]["all"] = datasets
    return datasets


async def get_columns_cached(client: "HoneycombClient", dataset: str) -> list["Column"]:
    """Get columns for a dataset with caching.

    Args:
        client: HoneycombClient instance
        dataset: Dataset slug

    Returns:
        List of Column objects
    """
    async with _cache_lock:
        cache = _get_cache_for_client(client)
        if dataset in cache["columns"]:
            return cache["columns"][dataset]

    # Fetch outside lock
    columns = await client.columns.list_async(dataset)

    async with _cache_lock:
        cache = _get_cache_for_client(client)
        cache["columns"][dataset] = columns
    return columns


async def get_derived_columns_cached(
    client: "HoneycombClient", dataset: str
) -> list["DerivedColumn"]:
    """Get derived columns for a dataset with caching.

    Args:
        client: HoneycombClient instance
        dataset: Dataset slug (use "__all__" for environment-wide derived columns)

    Returns:
        List of DerivedColumn objects
    """
    async with _cache_lock:
        cache = _get_cache_for_client(client)
        if dataset in cache["derived_columns"]:
            return cache["derived_columns"][dataset]

    # Fetch outside lock
    derived = await client.derived_columns.list_async(dataset)

    async with _cache_lock:
        cache = _get_cache_for_client(client)
        cache["derived_columns"][dataset] = derived
    return derived


def clear_cache_for_client(client: "HoneycombClient") -> None:
    """Clear all cached data for a specific client.

    Args:
        client: HoneycombClient instance to clear cache for
    """
    if client in _client_caches:
        del _client_caches[client]


def clear_all_caches() -> None:
    """Clear all cached data for all clients.

    Useful for testing or when you need to force a refresh of all data.
    """
    _client_caches.clear()

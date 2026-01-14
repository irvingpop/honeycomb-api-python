"""Base factory class for Honeycomb models.

Provides Honeycomb-specific defaults for ID generation, timestamps, and other common patterns.
"""

import secrets
from datetime import datetime, timezone
from typing import TypeVar

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class HoneycombFactory(ModelFactory[T]):
    """Base factory with Honeycomb-specific defaults.

    All model factories should extend this class to ensure consistent
    data generation patterns across the test suite.

    Features:
    - Generates Honeycomb-style alphanumeric IDs
    - Produces ISO8601 timestamps in UTC
    - Respects Pydantic Field constraints and examples

    Usage:
        class SLOFactory(HoneycombFactory):
            __model__ = SLO

        slo = SLOFactory.build()
        slo_with_override = SLOFactory.build(name="Custom Name")
    """

    __is_base_factory__ = True
    # Note: __use_examples__ disabled because some OpenAPI spec examples have typos
    # (e.g., reset_at has "2022-011-11T09:53:04Z" with invalid month "011")

    @classmethod
    def _honeycomb_id(cls) -> str:
        """Generate a Honeycomb-style ID (alphanumeric, 8-12 chars)."""
        return secrets.token_hex(6)

    @classmethod
    def _honeycomb_timestamp(cls) -> str:
        """Generate an ISO8601 timestamp in UTC."""
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _honeycomb_slug(cls, prefix: str = "test") -> str:
        """Generate a URL-safe slug."""
        suffix = secrets.token_hex(4)
        return f"{prefix}-{suffix}"

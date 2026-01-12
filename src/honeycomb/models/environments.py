"""Pydantic models for Honeycomb Environments (v2 team-scoped).

Re-exports generated models that match JSON:API structure exactly.
"""

from honeycomb._generated_models import (
    CreateEnvironmentRequest,
    Environment,
    EnvironmentColor,
    EnvironmentListResponse,
    EnvironmentResponse,
    UpdateEnvironmentRequest,
)

__all__ = [
    "CreateEnvironmentRequest",
    "Environment",
    "EnvironmentColor",
    "EnvironmentListResponse",
    "EnvironmentResponse",
    "UpdateEnvironmentRequest",
]

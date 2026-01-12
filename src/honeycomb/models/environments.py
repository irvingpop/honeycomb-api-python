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

# Convenience type aliases
EnvironmentCreate = CreateEnvironmentRequest
EnvironmentUpdate = UpdateEnvironmentRequest

__all__ = [
    "CreateEnvironmentRequest",
    "Environment",
    "EnvironmentColor",
    "EnvironmentCreate",  # Convenience alias
    "EnvironmentUpdate",  # Convenience alias
    "EnvironmentListResponse",
    "EnvironmentResponse",
    "UpdateEnvironmentRequest",
]

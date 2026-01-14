"""Pytest configuration and fixtures."""

import pytest
from polyfactory.pytest_plugin import register_fixture

from tests.factories import (
    BoardFactory as _BoardFactory,
)
from tests.factories import (
    ColumnFactory as _ColumnFactory,
)
from tests.factories import (
    DatasetFactory as _DatasetFactory,
)
from tests.factories import (
    EmailRecipientFactory as _EmailRecipientFactory,
)
from tests.factories import (
    MarkerFactory as _MarkerFactory,
)
from tests.factories import (
    QueryAnnotationFactory as _QueryAnnotationFactory,
)
from tests.factories import (
    SLOFactory as _SLOFactory,
)
from tests.factories import (
    TriggerFactory as _TriggerFactory,
)
from tests.factories import (
    WebhookRecipientFactory as _WebhookRecipientFactory,
)

# =============================================================================
# Basic fixtures
# =============================================================================


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "test-api-key"


# =============================================================================
# Polyfactory fixture registration (Phase 5)
# =============================================================================
# Register commonly used factories as pytest fixtures for cleaner test code.
# Usage: def test_something(slo_factory): slo = slo_factory.build()


# Register core resource factories
@register_fixture
class SLOFactory(_SLOFactory):
    """SLO factory fixture."""


@register_fixture
class TriggerFactory(_TriggerFactory):
    """Trigger factory fixture."""


@register_fixture
class BoardFactory(_BoardFactory):
    """Board factory fixture."""


@register_fixture
class DatasetFactory(_DatasetFactory):
    """Dataset factory fixture."""


@register_fixture
class ColumnFactory(_ColumnFactory):
    """Column factory fixture."""


@register_fixture
class MarkerFactory(_MarkerFactory):
    """Marker factory fixture."""


@register_fixture
class QueryAnnotationFactory(_QueryAnnotationFactory):
    """Query annotation factory fixture."""


@register_fixture(name="email_recipient_factory")
class EmailRecipientFactory(_EmailRecipientFactory):
    """Email recipient factory fixture."""


@register_fixture(name="webhook_recipient_factory")
class WebhookRecipientFactory(_WebhookRecipientFactory):
    """Webhook recipient factory fixture."""

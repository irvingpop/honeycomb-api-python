"""Demonstrate factory fixture usage (Phase 5B).

Factories registered in conftest.py can be injected as pytest fixtures,
providing cleaner test code without explicit Factory.build() calls.
"""


def test_slo_factory_fixture(slo_factory):
    """Demo: SLO factory injected as fixture."""
    slo = slo_factory.build()
    assert slo.id
    assert slo.name
    assert slo.target_per_million


def test_trigger_factory_fixture(trigger_factory):
    """Demo: Trigger factory injected as fixture."""
    trigger = trigger_factory.build(name="Custom Trigger")
    assert trigger.name == "Custom Trigger"
    assert trigger.frequency


def test_dataset_factory_fixture(dataset_factory):
    """Demo: Dataset factory injected as fixture."""
    dataset = dataset_factory.build(slug="custom-slug")
    assert dataset.slug == "custom-slug"


def test_column_factory_fixture(column_factory):
    """Demo: Column factory injected as fixture."""
    column = column_factory.build()
    assert column.id
    assert column.key_name


def test_marker_factory_fixture(marker_factory):
    """Demo: Marker factory injected as fixture."""
    marker = marker_factory.build(message="Deployment v1.2.3")
    assert marker.message == "Deployment v1.2.3"


def test_query_annotation_factory_fixture(query_annotation_factory):
    """Demo: Query annotation factory injected as fixture."""
    annotation = query_annotation_factory.build()
    assert annotation.id
    assert annotation.name


def test_email_recipient_factory_fixture(email_recipient_factory):
    """Demo: Email recipient factory injected with custom name."""
    recipient = email_recipient_factory.build()
    assert recipient.type == "email"


def test_webhook_recipient_factory_fixture(webhook_recipient_factory):
    """Demo: Webhook recipient factory injected with custom name."""
    recipient = webhook_recipient_factory.build()
    assert recipient.type == "webhook"


def test_multiple_factories(slo_factory, trigger_factory, dataset_factory):
    """Demo: Multiple factory fixtures in one test."""
    slo = slo_factory.build()
    trigger = trigger_factory.build()
    dataset = dataset_factory.build()

    assert slo.id
    assert trigger.id
    assert dataset.slug


def test_batch_generation(slo_factory):
    """Demo: Generate batch using fixture."""
    slos = slo_factory.batch(5)
    assert len(slos) == 5
    assert all(slo.id for slo in slos)

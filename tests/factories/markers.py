"""Factories for Marker and MarkerSetting models."""

import random
import secrets
import time

from honeycomb.models import Marker, MarkerCreate, MarkerSetting, MarkerSettingCreate

from .base import HoneycombFactory


class MarkerFactory(HoneycombFactory):
    """Factory for Marker response model.

    Example:
        marker = MarkerFactory.build(id="abc123")
        markers = MarkerFactory.batch(5)
    """

    __model__ = Marker

    id = lambda: secrets.token_hex(3)  # 6 char hex
    start_time = lambda: int(time.time()) - random.randint(0, 3600)
    message = lambda: f"Deploy {HoneycombFactory._honeycomb_id()}"
    type = "deploy"
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()
    color = "#7b1fa2"


class MarkerCreateFactory(HoneycombFactory):
    """Factory for MarkerCreate request model.

    Example:
        payload = MarkerCreateFactory.build(message="Production deploy #123")
    """

    __model__ = MarkerCreate

    start_time = lambda: int(time.time())
    message = lambda: f"Deploy {HoneycombFactory._honeycomb_id()}"
    type = "deploy"


class MarkerSettingFactory(HoneycombFactory):
    """Factory for MarkerSetting response model.

    Example:
        setting = MarkerSettingFactory.build(type="deploy")
        settings = MarkerSettingFactory.batch(3)
    """

    __model__ = MarkerSetting

    id = lambda: HoneycombFactory._honeycomb_id()
    type = lambda: random.choice(["deploy", "build", "release", "alert"])
    color = lambda: f"#{secrets.token_hex(3)}"
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


class MarkerSettingCreateFactory(HoneycombFactory):
    """Factory for MarkerSettingCreate request model.

    Example:
        payload = MarkerSettingCreateFactory.build(type="deploy", color="#ff0000")
    """

    __model__ = MarkerSettingCreate

    type = lambda: random.choice(["deploy", "build", "release", "alert"])
    color = lambda: f"#{secrets.token_hex(3)}"

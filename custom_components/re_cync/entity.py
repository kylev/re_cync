"""ReCync entity.

Base functionality
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.device_registry import (
    CONNECTION_BLUETOOTH,
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ReCyncCoordinator

_LOGGER = logging.getLogger(__name__)


class ReCyncEntity(CoordinatorEntity[ReCyncCoordinator]):
    """Base entity full of value."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ReCyncCoordinator, dev_info: Any) -> None:
        """Init."""
        super().__init__(coordinator)

        self._attr_unique_id = str(dev_info["switchID"])
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(dev_info["deviceID"]))},
            connections={
                (CONNECTION_BLUETOOTH, dev_info["mac"]),
                (CONNECTION_NETWORK_MAC, dev_info["wifiMac"]),
            },
            manufacturer="Cync",
            model_id=str(dev_info["deviceType"]),
            name=dev_info["displayName"],
            sw_version=dev_info["firmwareVersion"],
        )

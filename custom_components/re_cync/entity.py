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
from .coordinator import ReCyncUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class ReCyncEntity(CoordinatorEntity[ReCyncUpdateCoordinator]):
    """BasEntity."""

    def __init__(self, coordinator: ReCyncUpdateCoordinator, data: Any) -> None:
        """Init."""
        super().__init__(coordinator)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(data["deviceID"]))},
            connections={
                (CONNECTION_BLUETOOTH, data["mac"]),
                (CONNECTION_NETWORK_MAC, data["wifiMac"]),
            },
            manufacturer="Cync",
            model_id=str(data["deviceType"]),
            name=data["displayName"],
            sw_version=data["firmwareVersion"],
        )

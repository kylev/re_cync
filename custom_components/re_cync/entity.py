"""ReCync entity.

Base functionality
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import callback
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
            identifiers={(DOMAIN, str(dev_info["switchID"]))},
            connections={
                (CONNECTION_BLUETOOTH, dev_info["mac"]),
                (CONNECTION_NETWORK_MAC, dev_info["wifiMac"]),
            },
            manufacturer="Cync",
            model_id=str(dev_info["deviceType"]),
            name=dev_info["displayName"],
            sw_version=dev_info["firmwareVersion"],
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Entity update from coordinator")
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        """If the switch is currently on or off."""
        _LOGGER.debug("is_on %s", self.coordinator.data)

        if self.coordinator.data is None:
            return False
        try:
            return self.coordinator.data[self._attr_unique_id]["is_on"]
        except KeyError:
            return False

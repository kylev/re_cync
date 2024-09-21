"""ReCync entity.

Base functionality
"""

from __future__ import annotations

import contextlib
import logging
from typing import Any

from homeassistant.components.light import ColorMode
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
        super().__init__(coordinator, dev_info)

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
        # _LOGGER.debug("Base entity update from coordinator; noisy.")
        super()._handle_coordinator_update()

    @property
    def is_on(self) -> bool:
        """If the switch is currently on or off."""
        # _LOGGER.debug("is_on %s", self.coordinator.data)
        return self._get_value("is_on") or False

    def _get_value(self, name: str, default: Any = None) -> Any:
        """Fetch a value from the coordinator."""
        val = default
        with contextlib.suppress(KeyError):
            val = self.coordinator.data.get(self.unique_id, {})[name]
        _LOGGER.debug("Value %s for %s: %s", name, self.unique_id, val)
        return val

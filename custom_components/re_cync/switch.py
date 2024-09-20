"""ReCync switch."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ReCyncCoordinator
from .entity import ReCyncEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""
    coordinator = hass.data[config_entry.entry_id]
    async_add_entities([ReCyncSwitch(coordinator, b) for b in coordinator.switches])


class ReCyncSwitch(ReCyncEntity, SwitchEntity):
    """Basic switch."""

    _attr_device_class = SwitchDeviceClass.OUTLET

    def __init__(self, coordinator: ReCyncCoordinator, data) -> None:
        """Init."""
        super().__init__(coordinator, data)
        _LOGGER.debug("Switch init %s", data)

    def _handle_coordinator_update(self) -> None:
        updated = False
        d = self.coordinator.data.get(self._attr_unique_id)
        if d is None:
            return
        if self._attr_is_on != d["is_on"]:
            self._attr_is_on = d["is_on"]
            updated = True

        if updated:
            self.async_write_ha_state()

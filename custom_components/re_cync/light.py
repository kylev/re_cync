"""ReCync light."""
from __future__ import annotations

import logging

from typing import Any

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup light."""
    _LOGGER.debug("Setup light %s", config_entry)

    hub = hass.data[config_entry.entry_id]
    async_add_entities([ReCyncLight(b) for b in hub.bulbs])


class ReCyncLight(LightEntity):
    """Basic light."""

    def __init__(self, data) -> None:
        """Init."""
        self._data = data

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data["deviceID"])},
            connections={(CONNECTION_NETWORK_MAC, data["wifiMac"])},
            manufacturer="Cync",
            name=data["displayName"],
            sw_version=data["firmwareVersion"],
        )

    @property
    def unique_id(self) -> str:
        return self._data["deviceID"]

    @property
    def name(self) -> str:
        return self._data["displayName"]

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""

"""ReCync switch."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import (
    CONNECTION_BLUETOOTH,
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light."""
    _LOGGER.debug("Setup switch %s", config_entry)

    hub = hass.data[config_entry.entry_id]
    async_add_entities([ReCyncSwitch(b) for b in hub.switches])


class ReCyncSwitch(SwitchEntity):
    """Basic switch."""

    def __init__(self, data) -> None:
        """Init."""
        self._data = data

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data["deviceID"])},
            connections={
                (CONNECTION_NETWORK_MAC, data["wifiMac"]),
                (CONNECTION_BLUETOOTH, data["mac"]),
            },
            device_class=SwitchDeviceClass.OUTLET,
            manufacturer="Cync",
            name=data["displayName"],
            sw_version=data["firmwareVersion"],
        )

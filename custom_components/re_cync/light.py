"""ReCync light."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import (
    CONNECTION_BLUETOOTH,
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ReCyncCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light."""
    _LOGGER.debug("Setup light %s", config_entry)

    hub = hass.data[config_entry.entry_id]
    async_add_entities([ReCyncLight(hub, b) for b in hub.bulbs])


class ReCyncLight(LightEntity):
    """Basic light."""

    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, hub, data) -> None:
        """Init."""
        _LOGGER.debug("Light init %s", data)
        self._data = data
        self._hub: ReCyncCoordinator = hub

        self._supported_color_modes: set[str] = {ColorMode.ONOFF}
        self._color_mode: str | None = None

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

        if data["deviceType"] in {55, 146}:
            self._supported_color_modes = {ColorMode.BRIGHTNESS}
        if data["deviceType"] in {146}:
            self._supported_color_modes.add(ColorMode.RGB)
            self._supported_color_modes.add(ColorMode.COLOR_TEMP)

    @property
    def unique_id(self) -> str:
        return str(self._data["switchID"])

    @property
    def name(self) -> str:
        return self._data["displayName"]

    @property
    def supported_color_modes(self) -> set[str] | None:
        return self._supported_color_modes

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self._hub.turn_on(self._data["switchID"])

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self._hub.turn_off(self._data["switchID"])

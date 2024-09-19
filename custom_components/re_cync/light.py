"""ReCync light."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
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
    """Set up light."""
    _LOGGER.debug("Setup light %s", config_entry)

    coordinator = hass.data[config_entry.entry_id]
    async_add_entities([ReCyncLight(coordinator, b) for b in coordinator.bulbs])


class ReCyncLight(ReCyncEntity, LightEntity):
    """Basic light."""

    def __init__(self, coordinator: ReCyncCoordinator, data) -> None:
        """Init."""
        super().__init__(coordinator, data)
        _LOGGER.debug("Light init %s", data)

        self._data = data
        self._supported_color_modes: set[str] = {ColorMode.ONOFF}
        self._color_mode: str | None = None

        if data["deviceType"] in {55}:
            self._supported_color_modes = {ColorMode.BRIGHTNESS}
        if data["deviceType"] in {146}:
            self._supported_color_modes = {ColorMode.RGB, ColorMode.WHITE}

    @property
    def supported_color_modes(self) -> set[str] | None:
        return self._supported_color_modes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""

"""ReCync light."""

from __future__ import annotations

import logging
import math
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import color_temperature_kelvin_to_mired

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

    _attr_min_mireds = color_temperature_kelvin_to_mired(6500)
    _attr_max_mireds = color_temperature_kelvin_to_mired(2700)

    def __init__(self, coordinator: ReCyncCoordinator, data) -> None:
        """Init."""
        super().__init__(coordinator, data)
        _LOGGER.debug("Light init %s", data)

        self._color_mode: str | None = None
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        if data["deviceType"] in {55}:
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        if data["deviceType"] in {146}:
            self._attr_supported_color_modes = {ColorMode.RGB, ColorMode.COLOR_TEMP}

    def _handle_coordinator_update(self) -> None:
        updated = False
        d = self.coordinator.data.get(self.unique_id)
        if d is None:
            return
        if self._attr_is_on != d["is_on"]:
            self._attr_is_on = d["is_on"]
            updated = True
        if self._attr_rgb_color != d["rgb"] and d["white_temp"] == 0xFE:
            self._attr_rgb_color = d["rgb"]
            self._attr_color_mode = ColorMode.RGB
            updated = True
        if self._attr_brightness != d["brightness"]:
            self._attr_brightness = d["brightness"]
            updated = True
        new_ct = (
            self.max_mireds
            - (self.max_mireds - self.min_mireds) * d["white_temp"] / 100
        )
        if self._attr_color_temp != new_ct and d["brightness"] == 0x64:
            self._attr_color_temp = new_ct
            self._attr_color_mode = ColorMode.COLOR_TEMP
            updated = True

        if updated:
            self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""

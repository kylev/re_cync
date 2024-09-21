"""ReCync light."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import color_temperature_kelvin_to_mired
from homeassistant.util.scaling import scale_ranged_value_to_int_range

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

        if data["deviceType"] in {55}:
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        if data["deviceType"] in {146}:
            self._attr_supported_color_modes = {
                ColorMode.BRIGHTNESS,
                ColorMode.RGB,
                ColorMode.COLOR_TEMP,
            }

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        return scale_ranged_value_to_int_range(
            (0, 100), (0, 255), self._get_value("brightness")
        )

    @property
    def color_mode(self) -> str | None:
        """Return the color mode of the light."""
        if self._get_value("white_temp") == 0xFE:
            return ColorMode.RGB
        # if self._get_value("brightness") == 0x64:
        return ColorMode.COLOR_TEMP
        # return ColorMode.BRIGHTNESS

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the RGB color value."""
        return self._get_value("rgb")

    @property
    def color_temp(self) -> int | None:
        """Return the CT color value."""
        wt = self._get_value("white_temp")
        return self.max_mireds - (self.max_mireds - self.min_mireds) * wt / 100

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""

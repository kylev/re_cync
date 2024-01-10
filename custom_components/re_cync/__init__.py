"""Re-worked Cync Lights for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .hub import Hub

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up re_cync from a config entry."""
    _LOGGER.warning("Blergh")

    hass.data.setdefault(DOMAIN, {})
    hass.data["hub"] = Hub()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

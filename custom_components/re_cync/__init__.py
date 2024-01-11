"""Re-worked Cync Lights for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .hub import CyncHub

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up re_cync from a config entry."""
    _LOGGER.warning("Blergh %s", entry.data)

    hass.data.setdefault(DOMAIN, {})
    hub = CyncHub(hass, entry)
    await hub.cloud_start()

    hass.data["hub"] = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

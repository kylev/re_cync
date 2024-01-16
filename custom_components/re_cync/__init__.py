"""Re-worked Cync Lights for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry, ConfigEntryAuthFailed
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .hub import AuthError, CyncHub

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up re_cync from a config entry."""
    _LOGGER.debug("Setup entry %s", entry.data)
    hass.data.setdefault(DOMAIN, {})

    hub = CyncHub(hass, entry)
    hass.data[entry.entry_id] = hub

    try:
        await hub.start_cloud()
    except AuthError as err:
        _LOGGER.error("Error setting up Cync", exc_info=err)
        raise ConfigEntryAuthFailed(err) from err

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unload entry %s", entry.data)
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

"""Re-worked Cync Lights for Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry, ConfigEntryAuthFailed
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# from .coordinator import AuthError, ReCyncCoordinator
from .bt_coordinator import ReCyncBTCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up re_cync from a config entry."""
    _LOGGER.debug("Setup entry %s", entry.data)
    hass.data.setdefault(DOMAIN, {})

    # hub = ReCyncCoordinator(hass, entry)
    # hass.data[entry.entry_id] = hub

    # try:
    #     await hub.start_cloud()
    # except AuthError as err:
    #     raise ConfigEntryAuthFailed("Authentication failed or expired") from err

    # def async_bluetooth_device_discovered(device: bluetooth.Device):
    #     """Handle a discovered Bluetooth device."""
    #     _LOGGER.debug("Discovered Bluetooth device: %s", device)

    # entry.async_on_unload(
    #     bluetooth.async_register_callback(hass, async_bluetooth_device_discovered)
    # )

    coordinator = ReCyncBTCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unload entry %s", entry.data)
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

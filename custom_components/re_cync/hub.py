"""ReCync Hub."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class CyncHub:
    """Cync's cloud "hub" that works over IP."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Create the SIAHub."""
        _LOGGER.debug("Hub init")
        self._hass: HomeAssistant = hass
        self._entry: ConfigEntry = entry

    async def cloud_start(self):
        """Check cloud."""
        _LOGGER.info("Cloud start.")

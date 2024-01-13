"""ReCync Hub."""
from __future__ import annotations

import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .auth import ReCyncSession
from .event import EventStream

_LOGGER = logging.getLogger(__name__)

API_DEVICE_LIST = "https://api.gelighting.com/v2/user/{user_id}/subscribe/devices"
API_DEVICE_PROPS = (
    "https://api.gelighting.com/v2/product/{product_id}/device/{device_id}/property"
)


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
        self._rcs = ReCyncSession(entry.data)
        self._event_stream = EventStream(self._rcs.binary_token)

    async def start_cloud(self):
        """Check cloud."""
        _LOGGER.info("Cloud start %s", self._rcs.user_id)

        url = API_DEVICE_LIST.format(user_id=self._rcs.user_id)
        devs = await self._get_url(url)
        for device in devs:
            await self.start_device(device)

        await self._event_stream.initialize()
        _LOGGER.info("Cloud started")

    async def start_device(self, device):
        url = API_DEVICE_PROPS.format(
            product_id=device["product_id"], device_id=device["id"]
        )
        await self._get_url(url)

    async def _get_url(self, url):
        headers = {"Access-Token": self._rcs.access_token}
        async with aiohttp.ClientSession() as s, s.get(url, headers=headers) as resp:
            data = await resp.json()
            _LOGGER.debug(data)
            if resp.status not in (200, 404):
                raise Exception("Failed to fetch {}".format(url), resp.status, data)
            return data

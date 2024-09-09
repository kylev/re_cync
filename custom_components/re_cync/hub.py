"""ReCync Hub."""

from __future__ import annotations

import logging

import aiohttp

from homeassistant.const import CONF_TOKEN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .auth import ReCyncSession
from .event import EventStream

_LOGGER = logging.getLogger(__name__)

API_DEVICE_LIST = "https://api.gelighting.com/v2/user/{user_id}/subscribe/devices"
API_DEVICE_PROPS = (
    "https://api.gelighting.com/v2/product/{product_id}/device/{device_id}/property"
)


class ApiError(Exception):
    pass


class AuthError(ApiError):
    pass


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
        self._rcs = ReCyncSession(entry.data[CONF_TOKEN])
        self._bulbs = []
        self._event_stream = EventStream(self._rcs.binary_token)

    async def start_cloud(self):
        """Check cloud."""
        _LOGGER.info("Cloud start %s", self._rcs.user_id)

        url = API_DEVICE_LIST.format(user_id=self._rcs.user_id)
        devices = await self._get_url(url)
        for d in devices:
            sku_type = int(d["product_id"], 16) % 1000
            match sku_type:
                case 713, 721:
                    _LOGGER.debug("Ignoring switch/dimmer (?) SKU type %d", sku_type)
                case 897:
                    await self._discover_home(d)
                case _:
                    _LOGGER.debug("Ignoring SKU type %d (%s)", sku_type, d.get("name"))

        await self._event_stream.initialize()
        _LOGGER.info("Cloud started")

    @property
    def bulbs(self):
        return self._bulbs

    async def _discover_home(self, device):
        url = API_DEVICE_PROPS.format(
            product_id=device["product_id"], device_id=device["id"]
        )
        info = await self._get_url(url)
        for bulb in info["bulbsArray"]:
            self._bulbs.append(bulb)

    async def _get_url(self, url):
        headers = {"Access-Token": self._rcs.access_token}
        async with aiohttp.ClientSession() as s, s.get(url, headers=headers) as resp:
            data = await resp.json()
            _LOGGER.debug(data)
            match resp.status:
                case 200:
                    return data
                case 403:
                    raise AuthError("Forbidden", url, resp.status, data)
                case _:
                    raise ApiError("Failed to fetch", url, resp.status, data)

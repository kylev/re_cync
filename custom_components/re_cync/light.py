"""ReCync light."""
from __future__ import annotations

import logging

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Setup switch %s", config_entry)


class ReCyncLight(LightEntity):
    """Basic light."""

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""

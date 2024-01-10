"""Config flow for ReCync integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_TOKEN, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)
STEP_TWO_FACTOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
    }
)


class ReCyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cync Room Lights."""

    VERSION = 1

    def __init__(self) -> None:
        """Init."""
        _LOGGER.debug("Init")

        self.data = {}
        self.options = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """User login."""
        _LOGGER.debug("Login step %s", user_input)

        if user_input is not None:
            # TODO Check username/password
            return await self.async_step_two_factor()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )

    async def async_step_two_factor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            # TODO decide what to store.
            return self.async_create_entry(title="Cync Ready", data=user_input)

        return self.async_show_form(
            step_id="two_factor", data_schema=STEP_TWO_FACTOR_SCHEMA
        )

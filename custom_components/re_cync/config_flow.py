"""Config flow for ReCync integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_TOKEN, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import TextSelectorConfig, TextSelectorType

from .auth import AuthError, ReCyncSession, TwoFactorRequiredError, UsernameError
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
        self._rcs = ReCyncSession()
        self._username = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """User login."""
        _LOGGER.debug("Login step %s", user_input)

        errors = None
        if user_input is not None:
            self._username = user_input[CONF_USERNAME]
            self._password = user_input[CONF_PASSWORD]  # I hate this
            try:
                res = await self._rcs.authenticate(
                    self._username, user_input[CONF_PASSWORD]
                )
                return self._save_token(res)
            except TwoFactorRequiredError:
                await self._rcs.request_code(user_input[CONF_USERNAME])
                return await self.async_step_two_factor()
            except UsernameError:
                errors = {CONF_USERNAME: "User not found"}
            except AuthError as e:
                errors = {"base": e.args[0]}

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_two_factor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = None
        if user_input is not None:
            res = await self._rcs.authenticate(
                self._username, self._password, user_input[CONF_TOKEN]
            )
            self._save_token(res)

        return self.async_show_form(
            step_id="two_factor", data_schema=STEP_TWO_FACTOR_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle re-auth."""
        _LOGGER.debug("Re-auth %s", user_input)

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:  # ConfigFlowResult:
        """Handle reauthorization flow."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user(None)

    async def _save_token(self, res: dict[str, Any]) -> None:
        """Save token."""
        return self.async_create_entry(
            title=self._username, data={CONF_USERNAME: self._username, CONF_TOKEN: res}
        )

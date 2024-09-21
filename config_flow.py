"""Config flow for PureTools 4x1 HDMI Switcher integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.aiohttp_client as hass_aiohttp

from .const import CONF_HOST, CONF_PORT, DOMAIN
from .exceptions import CannotConnect
from .puretools import PuretoolsConnector

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    try:

        host = data[CONF_HOST]
        port = data[CONF_PORT]
        session = hass_aiohttp.async_get_clientsession(hass)

        device = PuretoolsConnector(host, port, session, hass)

        _LOGGER.info("Trying to connect to PureTools 4x1 HDMI Switcher at %s:%s", host, port)
        sysinfo = await device.sysinfo

        device_name = sysinfo['model']

        if sysinfo is None:
            raise CannotConnect  # noqa: TRY301

    except Exception as e:  # noqa: BLE001
        _LOGGER.error(str(e))
        raise CannotConnect from None

    return {
        "title": device_name,
        CONF_HOST: data[CONF_HOST],
        CONF_PORT: data[CONF_PORT]
    }


class PuretoolsConfigFlow(ConfigFlow, domain = DOMAIN):
    """Handle a config flow for PureTools 4x1 HDMI Switcher."""

    VERSION = 1


    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return PuretoolsOptionsFlowHandler(config_entry)


    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle a flow initialized by user."""

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"


        data = {
            vol.Optional(CONF_HOST): str,
            vol.Optional(CONF_PORT): str
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data),
            errors=errors,
        )


    async def async_step_import(self, user_input: dict) -> FlowResult:
        """Handle a flow initialized by import from configuration file."""

        info = await validate_input(self.hass, user_input)

        await self.async_set_unique_id(user_input[CONF_HOST])
        self._abort_if_unique_id_configured(updates={
            CONF_HOST: user_input[CONF_HOST]
        })

        return self.async_create_entry(title=info["title"], data=user_input)


class PuretoolsOptionsFlowHandler(OptionsFlow):
    """Handle a options flow for Dyson Pure Cool."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry


    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = {
            vol.Required('hdmi1', default=self.config_entry.options.get("hdmi1")): str,
            vol.Required('hdmi2', default=self.config_entry.options.get("hdmi2")): str,
            vol.Required('hdmi3', default=self.config_entry.options.get("hdmi3")): str,
            vol.Required('hdmi4', default=self.config_entry.options.get("hdmi4")): str
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(data)
        )

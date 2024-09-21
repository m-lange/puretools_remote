"""PureTools 4x1 HDMI Switcher integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
import homeassistant.helpers.aiohttp_client as hass_aiohttp
from homeassistant.helpers.typing import ConfigType

from .const import CONF_HOST, CONF_PORT, DOMAIN
from .exceptions import CannotConnect
from .puretools import PuretoolsConnector

_LOGGER = logging.getLogger(__name__)


PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.SWITCH]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Optional(CONF_HOST, default=""): cv.string,
            vol.Optional(CONF_PORT, default=""): cv.string
        })
    },
    extra = vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up PureTools 4x1 HDMI Switcher from configuration file."""

    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=config[DOMAIN]
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PureTools 4x1 HDMI Switcher a config entry."""

    try:
        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]
        session = hass_aiohttp.async_get_clientsession(hass)

        device = PuretoolsConnector(host, port, session, hass)

        _LOGGER.info("Trying to connect to PureTools 4x1 HDMI Switcher at %s:%s", host, port)
        sysinfo = await device.sysinfo

        if sysinfo is None:
            _LOGGER.error("Connection refused")
            raise ConfigEntryNotReady from None

        # Store an instance of the "connecting" class that does the work of speaking
        # with your actual devices.
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = device
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    except CannotConnect:
        _LOGGER.error("Connection refused")
        raise ConfigEntryNotReady from None

    return True



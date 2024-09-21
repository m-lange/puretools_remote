"""Provides functionality to interact PureTools 4x1 HDMI Switcher."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .puretools import PuretoolsConnector

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback,) -> None:
    """Set up PureTools 4x1 HDMI Switcher from a config entry."""

    device = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities( [PuretoolsMediaPlayerEntity(hass, device, config_entry)], update_before_add=True )


class PuretoolsMediaPlayerEntity(MediaPlayerEntity):
    """Representation of a PureTools 4x1 HDMI Switcher media player entity."""

    def __init__(self, hass: HomeAssistant, device: PuretoolsConnector, config_entry: ConfigEntry):
        """Initialize media player entity."""
        super().__init__()
        self._device = device
        self._config_entry = config_entry
        self._name = None
        self._attr_unique_id = None
        self._attr_icon = "mdi:video-input-hdmi"
        self._attr_device_class = None

        self._auto_mode = False


    @property
    def should_poll(self):
        """Push an update after each command."""
        return True


    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name


    @property
    def state(self) -> MediaPlayerState | None:
        """State of the player."""
        return MediaPlayerState.ON


    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        return [
            self._config_entry.options.get("hdmi1") or "HDMI 1",
            self._config_entry.options.get("hdmi2") or "HDMI 2",
            self._config_entry.options.get("hdmi3") or "HDMI 3",
            self._config_entry.options.get("hdmi4") or "HDMI 4"
        ]


    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.SELECT_SOURCE
        )


    async def async_update(self):
        """Fetch new state data for this entity."""

        sysinfo = await self._device.sysinfo

        if self._name is None:
            self._name = sysinfo['model']

        if self._attr_unique_id is None:
            self._attr_unique_id = sysinfo['model']

        self._attr_device_info = {
            "identifiers": {(DOMAIN, sysinfo['model'])},
            "name": "PureTools 4x1 HDMI Switcher",
            "manufacturer": "PureTools",
            "model": sysinfo['model'],
            "sw_version": sysinfo['sw_version']
        }

        match sysinfo['source']:
            case "HDMI1":
                self._attr_source = self._config_entry.options.get("hdmi1") or "HDMI 1"
            case "HDMI2":
                self._attr_source = self._config_entry.options.get("hdmi2") or "HDMI 2"
            case "HDMI3":
                self._attr_source = self._config_entry.options.get("hdmi3") or "HDMI 3"
            case "HDMI4":
                self._attr_source = self._config_entry.options.get("hdmi4") or "HDMI 4"

        self._auto_mode = sysinfo["auto"]



    async def async_select_source(self, source: str) -> None:
        """Select input source."""

        if self._auto_mode:
            await self._device.manual()

        if source == self._config_entry.options.get("hdmi1") or source == "HDMI 1":
            await self._device.hdmi1()

        elif source ==  self._config_entry.options.get("hdmi2")  or source == "HDMI 2":
            await self._device.hdmi2()

        elif source ==  self._config_entry.options.get("hdmi3")  or source == "HDMI 3":
            await self._device.hdmi3()

        elif source ==  self._config_entry.options.get("hdmi4")  or source ==  "HDMI 4":
            await self._device.hdmi4()


        await asyncio.sleep(0.25)
        self.async_schedule_update_ha_state(True)

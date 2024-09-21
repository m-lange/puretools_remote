"""Platform for switch integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .puretools import PuretoolsConnector

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback,) -> None:
    """Set up PureTools 4x1 HDMI Switcher switch from a config entry."""


    device = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities( [PuretoolsAutoSwitchingMode(hass, device)], update_before_add=True )



class PuretoolsAutoSwitchingMode(SwitchEntity):
    """Representation of a Puretools switch entity."""

    def __init__(self, hass: HomeAssistant, device: PuretoolsConnector):
        """Initialize a Puretools switch entity."""
        super().__init__()
        self._device = device
        self._attr_unique_id = None
        self._attr_icon = "mdi:auto-mode"
        self._attr_entity_category = EntityCategory.CONFIG


    @property
    def name(self):
        """Return the name of the entity."""
        return "Auto-switching mode"


    @property
    def should_poll(self):
        """Push an update after each command."""
        return True


    async def async_update(self):
        """Fetch new state data for this entity."""
        sysinfo = await self._device.sysinfo

        if self._attr_unique_id is None:
            self._attr_unique_id = sysinfo['model'] + "-auto"

        self._attr_is_on = sysinfo["auto"]

        self._attr_device_info = {
            "identifiers": {(DOMAIN, sysinfo['model'])},
            "name": "PureTools 4x1 HDMI Switcher",
            "manufacturer": "PureTools",
            "model": sysinfo['model'],
            "sw_version": sysinfo['sw_version']
        }


    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable auto-switching mode."""
        await self._device.auto()
        await asyncio.sleep(0.25)
        self.async_schedule_update_ha_state(True)


    async def async_turn_off(self, **kwargs: Any) -> None:
        """Enable manual-switching mode."""
        await self._device.manual()
        await asyncio.sleep(0.25)
        self.async_schedule_update_ha_state(True)

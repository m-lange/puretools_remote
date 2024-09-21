"""Exceptions for PureTools 4x1 HDMI Switcher integration."""

from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

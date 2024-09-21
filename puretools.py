"""Class to control PureTools 4x1 HDMI Switcher."""

import logging

import homeassistant.helpers.aiohttp_client as hass_aiohttp

_LOGGER = logging.getLogger(__name__)


class PuretoolsConnector:
    """Initialize PureTools 4x1 HDMI Switcher connector."""

    def __init__(self, host, port, session=None, hass=None):
        """Initialize connector class."""
        self._host = host
        self._port = port
        self._session = session
        self._hass = hass
        self._baseUrl = "http://" + self._host + ":" + self._port


    async def close_session(self) -> None:
        """Close session."""
        if self._session is not None:
            await self._session.close()
            self._session = None


    async def resurect_session(self) -> None:
        """Resurect session."""
        if self._session is None:
            self._session = hass_aiohttp.async_get_clientsession(self._hass)


    @property
    def host(self) -> str:
        """Get host adress of the device."""
        return self._host


    @property
    def port(self) -> str:
        """Get port adress of the device."""
        return self._port


    @property
    async def sysinfo(self) -> dict | None:
        """Get system information."""
        return await self._get("/sysinfo")


    async def hdmi1(self) -> None:
        """Switch to HDMI input 1."""
        return await self._get("/hdmi1")


    async def hdmi2(self) -> None:
        """Switch to HDMI input 2."""
        return await self._get("/hdmi2")


    async def hdmi3(self) -> None:
        """Switch to HDMI input 3."""
        return await self._get("/hdmi3")


    async def hdmi4(self) -> None:
        """Switch to HDMI input 4."""
        return await self._get("/hdmi4")


    async def auto(self) -> None:
        """Enable auto-switching mode."""
        return await self._get("/auto")


    async def manual(self) -> None:
        """Enable manual-switching mode."""
        return await self._get("/manual")


    async def _get(self, path: str) -> dict | None:
        """Send command."""
        _LOGGER.debug("Send command: %s", path)
        await self.resurect_session()
        async with self._session.get(self._baseUrl + "/" + path) as response:
            _LOGGER.debug("Feedback (%s): %s", path, await response.text())
            return await response.json()



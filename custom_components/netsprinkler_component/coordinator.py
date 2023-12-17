"""DataUpdateCoordinator for netsprinkler_component."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.netsprinkler_component.Sprinkler.netsprinkler import NETSprinkler

from .api import (
    IntegrationBlueprintApiClient,
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientError,
)
from .const import DOMAIN, LOGGER
import async_timeout

TIMEOUT = 10

# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class NETSprinklerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        controller: NETSprinkler,
        scan_interval: int
    ) -> None:
        """Initialize."""
        self.controller = controller
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name='NETSprinkler Resource status',
            update_interval=timedelta(scan_interval),
            update_method=self.async_update_data
        )

    async def async_update_data(self):
        """Fetch data from NETSprinkler"""
        LOGGER.info(f'[coordinator:async_update_data] retrieve data from NETSprinkler')
        async with async_timeout.timeout(TIMEOUT):
            try:
                await self.controller.refresh()
            except Exception as e:
                LOGGER.exception(e)

            if not self.controller._state:
                raise UpdateFailed('Error fetching NETSprinkler State')

            return self.controller._state
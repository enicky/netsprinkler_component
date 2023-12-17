"""Custom integration to integrate netsprinkler_component with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/netsprinkler_component
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform, CONF_URL, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.util.dt import utc_from_timestamp
from homeassistant.util import slugify

from custom_components.netsprinkler_component.Sprinkler.netsprinkler import NETSprinkler

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    LOGGER
)
from .coordinator import NETSprinklerDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.TIME
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    logPrefix = '[__init__:async_setup_entry]'
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    url = entry.data.get(CONF_URL)
    opts = {"session": async_get_clientsession(hass)}
    controller = NETSprinkler(url, opts)
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)


    hass.data[DOMAIN][entry.entry_id] = coordinator = NETSprinklerDataUpdateCoordinator(
        hass=hass,
        controller=controller,
        scan_interval=scan_interval
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    LOGGER.debug(f'{logPrefix} Start refreshing data from coordinator side')
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady
    LOGGER.debug(f'{logPrefix} Finished and last update was a success')
    hass.data[DOMAIN][entry.entry_id] = {
            "coordinator": coordinator,
            "controller": controller,
        }

    for components in PLATFORMS:
        LOGGER.debug(f'{logPrefix} Start processing component {components}')
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, components)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

class NETSprinklerEntity(RestoreEntity):
    """Define a generic OpenSprinkler entity."""

    def __init__(self, entry, name, coordinator):
        """Initialize."""
        self._coordinator = coordinator
        self._entry = entry
        self._name = name

    def _get_state(self):
        """Retrieve the state."""
        raise NotImplementedError

    @property
    def device_info(self):
        """Return device information about Opensprinkler Controller."""

        controller = self.hass.data[DOMAIN][self._entry.entry_id]["controller"]

        model = controller.hardware_version_name or "Unknown"
        if controller.hardware_type_name:
            model += f" - ({controller.hardware_type_name})"

        firmware = controller.firmware_version_name or "Unknown"
        firmware += f" ({ controller.firmware_minor_version })"

        return {
            "identifiers": {(DOMAIN, slugify(self._entry.unique_id))},
            "name": self._name,
            "manufacturer": "OpenSprinkler",
            "configuration_url": self._entry.data.get(CONF_URL),
            "model": model,
            "sw_version": firmware,
        }

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self._coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update latest state."""
        await self._coordinator.async_request_refresh()

class NETSprinklerBinarySensor(NETSprinklerEntity):
    """Define a generic OpenSprinkler binary sensor."""

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._get_state()



class NETSprinklerSensor(NETSprinklerEntity):
    @property
    def state(self):
        return self._get_state()


class NETSprinklerControllerEntity:
    async def run(self, run_seconds = None, continue_running_stations = None):
        await self._controlller.refresh()
        await self._coordinator.async_request_refresh()
        return

    async def stop(self):
        """Stops all stations."""
    #    await self._controller.stop_all_stations()
        await self._coordinator.async_request_refresh()

    async def reboot(self):
        """Reboot controller."""
        #await self._controller.reboot()
        await self._coordinator.async_request_refresh()


class NETSprinklerStationEntity:
    @property
    def extra_state_attributes(self):
        attributes = {"netsprinkler_type": "station"}
        for attr in [
            "name",
            "index",
            "is_master",
            "running_program_id",
        ]:
            try:
                attributes[attr] = getattr(self._valve, attr)
            except:  # noqa: E722
                pass

        for attr in ["start_time", "end_time"]:
            timestamp = getattr(self._valve, attr, 0)
            if not timestamp:
                attributes[attr] = None
            else:
                attributes[attr] = utc_from_timestamp(timestamp).isoformat()

        return attributes

    async def run(self, run_seconds=None):
        """Run station."""
        if run_seconds is not None and not isinstance(run_seconds, int):
            raise Exception("Run seconds should be an integer value for station")

        await self._valve.run(run_seconds)
        await self._coordinator.async_request_refresh()

    async def stop(self):
        """Stop station."""
        await self._valve.stop()
        await self._coordinator.async_request_refresh()

class NETSprinklerProgramEntity:
    @property
    def extra_state_attributes(self):
        attributes = {"netsprinkler_type": "program"}
        for attr in [
            "name",
            "index",
        ]:
            try:
                attributes[attr] = getattr(self._program, attr)
            except:  # noqa: E722
                pass

        return attributes

    async def run(self):
        """Runs the program."""
        await self._program.run()
        await self._coordinator.async_request_refresh()

class NETSprinklerText(NETSprinklerEntity):
    """Define a generic OpenSprinkler text."""
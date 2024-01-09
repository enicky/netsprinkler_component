"""Switch platform for netsprinkler_component."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from typing import Callable
from homeassistant.const import CONF_NAME
from homeassistant.components.switch import SwitchEntity
from homeassistant.util import slugify
from homeassistant.util.dt import utc_from_timestamp

from custom_components.netsprinkler_component import NETSprinklerBinarySensor, NETSprinklerControllerEntity, NETSprinklerStationEntity

from .const import (
    DOMAIN,
    LOGGER
)


async def async_setup_entry(hass: HomeAssistant, entry: dict, async_add_entities: Callable):
    """Set up the sensor platform."""
    logPrefix = '[switch:async_setup_entry]'
    entities = _create_entities(hass, entry)
    async_add_entities(entities)
    LOGGER.debug(f'{logPrefix} Finished async_setup_entry... return ')

def _create_entities(hass: HomeAssistant, entry: dict):
    entities = []

    controller = hass.data[DOMAIN][entry.entry_id]["controller"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]
    entities.append(ControllerOperationSwitch(entry, name, controller, coordinator))


    for _, valve in controller.valves.items():
        entities.append(StationEnabledSwitch(entry, name, valve, coordinator))

    return entities

class ControllerOperationSwitch(NETSprinklerControllerEntity, NETSprinklerBinarySensor, SwitchEntity):
    def __init__(self, entry, name, controller, coordinator):
        self._controller = controller
        self._entity_type = 'switch'
        super().__init__(entry, name, coordinator)

    @property
    def name(self):
        """Return the name of controller switch."""
        return f"{self._name} Enabled"

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return slugify(
            f"{self._entry.unique_id}_{self._entity_type}_controller_enabled"
        )

    @property
    def icon(self) -> str:
        """Return icon."""
        if self._controller.enabled:
            return "mdi:barley"

        return "mdi:barley-off"
    @property
    def extra_state_attributes(self):
        controller = self._controller
        attributes = {"opensprinkler_type": "controller"}
        for attr in [
            "firmware_version",
            "firmware_minor_version",
            "last_reboot_cause",
            "last_reboot_cause_name",

        ]:
            try:
                attributes[attr] = getattr(controller, attr)
            except:  # noqa: E722
                pass

        for attr in [
            "last_reboot_time",
        ]:
            timestamp = getattr(controller, attr)
            if not timestamp:
                attributes[attr] = None
            else:
                attributes[attr] = utc_from_timestamp(timestamp).isoformat()

        return attributes
    def _get_state(self) -> str:
        """Retrieve latest state."""
        return bool(self._controller.enabled)

    async def async_turn_on(self, **kwargs):
        """Enable the controller operation."""
        await self._controller.enable()
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Disable the device operation."""
        LOGGER.debug(f'[switch:_async_turn_off] Turning off switch')
        await self._controller.disable()
        LOGGER.debug(f'[switch:_async_turn_off] start request on async refresh')
        await self._coordinator.async_request_refresh()

class StationEnabledSwitch(NETSprinklerStationEntity, NETSprinklerBinarySensor, SwitchEntity):
    def __init__(self, entry, name, valve, coordinator):
        self._valve = valve
        self._entity_type = 'switch'
        super().__init__(entry, name, coordinator)

    @property
    def name(self):
        """Return the name of the switch."""
        return self._valve.name + " Valve Enabled"

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return slugify(
            f"{self._entry.unique_id}_{self._entity_type}_valve_enabled_{self._valve.index}"
        )

    @property
    def icon(self) -> str:
        """Return icon."""
        if self._valve.is_master:
            if self._valve.enabled:
                return "mdi:water-pump"
            else:
                return "mdi:water-pump-off"

        if self._valve.enabled:
            return "mdi:water"

        return "mdi:water-off"

    def _get_state(self) -> bool:
        """Retrieve latest state."""
        #LOGGER.debug(f'[StationEnabledSwitch:_get_state] returning state of valve {self._valve.enabled}')
        return bool(self._valve.enabled)

    async def async_turn_on(self, **kwargs):
        """Enable the station."""
        await self._valve.enable()
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Disable the station."""
        await self._valve.disable()
        await self._coordinator.async_request_refresh()
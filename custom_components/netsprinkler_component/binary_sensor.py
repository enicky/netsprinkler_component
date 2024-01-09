"""Binary sensor platform for netsprinkler_component."""
from __future__ import annotations
from homeassistant.util import slugify

from homeassistant.components.binary_sensor import (
    BinarySensorEntity
)

from . import (
    NETSprinklerStationEntity,
    NETSprinklerBinarySensor
)

from .const import (DOMAIN, LOGGER)

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from typing import Callable

async def async_setup_entry(hass : HomeAssistant, entry: dict, async_add_devices: Callable):
    logPrefix = '[binary_sensor:async_setup_entry]'
    """Set up the binary_sensor platform."""
    LOGGER.debug(f'{logPrefix} Start setup of binary sensors')
    entities = _create_entities(hass, entry)
    async_add_devices(entities)
    LOGGER.debug(f'{logPrefix} Finished async_setup_entry... return ')


def _create_entities(hass: HomeAssistant, entry: dict):
    entities = []

    controller= hass.data[DOMAIN][entry.entry_id]["controller"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]

    for _, valve in controller.valves.items():
        entities.append(StationIsRunningBinarySensor(entry, name,  valve, coordinator))

    return entities

class StationIsRunningBinarySensor(NETSprinklerStationEntity, NETSprinklerBinarySensor, BinarySensorEntity):
    def __init__(self, entry, name, valve, coordinator):
        self._valve = valve
        self._entity_type = "binary_sensor"
        super().__init__(entry, name, coordinator)

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return self._valve.name + " Valve Running"

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return slugify(
            f"{self._entry.unique_id}_{self._entity_type}_valve_running_{self._valve.index}"
        )

    @property
    def icon(self) -> str:
        """Return icon."""
        if self._valve.is_master:
            if self._valve.is_running:
                return "mdi:water-pump"
            else:
                return "mdi:water-pump-off"
        #return "mdi:water-pump-off"

        if self._valve.is_running:
            return "mdi:valve-open"

        return "mdi:valve-closed"

    def _get_state(self) -> bool:
        """Retrieve latest state."""
        #return False
        return bool(self._valve.is_running)

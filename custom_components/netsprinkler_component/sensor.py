"""Sensor platform for netsprinkler_component."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
from homeassistant.util.dt import utc_from_timestamp
from typing import Callable



from custom_components.netsprinkler_component import NETSprinklerControllerEntity, NETSprinklerSensor, NETSprinklerStationEntity

from .const import (
    DOMAIN,
    LOGGER
    )

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="netsprinkler_component",
        name="Integration Sensor",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(hass : HomeAssistant, entry: dict, async_add_entities: Callable):
    """Set up the sensor platform."""
    """Set up the OpenSprinkler sensors."""
    entities = _create_entities(hass, entry)
    async_add_entities(entities)


def _create_entities(hass: HomeAssistant, entry: dict):
    LOGGER.debug(f'[sensor:_create_entities] start creating entities')
    entities = []

    controller = hass.data[DOMAIN][entry.entry_id]["controller"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]

    #entities.append(LastRunSensor(entry, name, controller, coordinator))
    #entities.append(RainDelayStopTimeSensor(entry, name, controller, coordinator))
    #entities.append(WaterLevelSensor(entry, name, controller, coordinator))
    #entities.append(FlowRateSensor(entry, name, controller, coordinator))
    LOGGER.debug(f'[sensor:_create_entities] Adding CurrentDrawSensor')
    entities.append(CurrentDrawSensor(entry, name, controller, coordinator))
    entities.append(ControllerCurrentTimeSensor(entry, name, controller, coordinator))

    for _, valve in controller.valves.items():
        LOGGER.debug(f'[sensor:_create_entities] Adding ValveStatusSensor {name} - {valve.name}')
        entities.append(ValveStatusSensor(entry, name, valve, coordinator))

    return entities

class ValveStatusSensor(NETSprinklerStationEntity, NETSprinklerSensor, Entity):
    def __init__(self, entry, name, valve, coordinator):
        self._valve = valve
        self._entity_type = 'sensor'
        super().__init__(entry, name, coordinator)

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return self._valve.name + " Valve Status"

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return slugify(
            f"{self._entry.unique_id}_{self._entity_type}_station_status_{self._valve.index}"
        )

    @property
    def icon(self) -> str:
        """Return icon."""
        if self._valve.is_master:
            if self.state == "master_engaged":
                return "mdi:water-pump"
            else:
                return "mdi:water-pump-off"

        if self._valve.is_running:
            return "mdi:valve-open"

        return "mdi:valve-closed"

    def _get_state(self) -> str:
        """Retrieve latest state."""
        LOGGER.debug(f'[sensor:_get_state] valve : {self._valve}')
        return self._valve.status

class CurrentDrawSensor(NETSprinklerControllerEntity, NETSprinklerSensor, Entity):
    def __init__(self, entry, name, controller, coordinator):
        self._name = name
        self._controller = controller
        self._entity_type = 'sensor'
        super().__init__(entry, name, coordinator)

    @property
    def icon(self) -> str:
        return "mdi:meter-electric-outline"
    @property
    def name(self) -> str:
        return f"{self._name} Current Draw"
    @property
    def unique_id(self) -> str | None:
        return slugify(f"{self._entry.unique_id}_{self._entity_type}_current_draw")
    @property
    def unit_of_measurement(self) -> str:
        """Return the units of measurement."""
        return "mA"

    def _get_state(self) -> int:
        """Retrieve latest state."""
        return self._controller.current_draw

class ControllerCurrentTimeSensor(NETSprinklerControllerEntity, NETSprinklerSensor, Entity):
    def __init__(self, entry, name, controller, coordinator):
        self._controller = controller
        self._entity_type = 'sensor'
        super().__init__(entry, name, coordinator)

    @property
    def device_class(self):
        """Return the device class."""
        return SensorDeviceClass.TIMESTAMP

    @property
    def icon(self) -> str:
        """Return icon."""
        return "mdi:clock-check"

    @property
    def name(self) -> str:
        """Return the name of this sensor including the controller name."""
        return f"{self._name} Current Time"

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return slugify(f"{self._entry.unique_id}_{self._entity_type}_devt")

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Set entity disabled by default."""
        return False

    def _get_state(self):
        """Retrieve latest state."""
        devt = self._controller.device_time
        if devt == 0:
            return None

        return utc_from_timestamp(devt).isoformat()
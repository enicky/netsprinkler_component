
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME

from typing import Callable

from .const import (
    DOMAIN,
    LOGGER
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: dict,
    async_add_entities: Callable,
):
    """Set up the OpenSprinkler numbers."""
    logPrefix = '[Number:async_setup_entry]'
    entities = _create_entities(hass, entry)
    async_add_entities(entities)
    LOGGER.debug(f'{logPrefix} Finished async_setup_entry... return ')

def _create_entities(hass: HomeAssistant, entry: dict):
    entities = []

    controller = hass.data[DOMAIN][entry.entry_id]["controller"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]

    # for _, program in controller.programs.items():
    #     for _, station in controller.stations.items():
    #         entities.append(
    #             ProgramDurationNumber(entry, name, program, station, coordinator)
    #         )

    # for _, program in controller.programs.items():
    #     entities.append(ProgramIntervalDaysNumber(entry, name, program, coordinator))
    #     entities.append(ProgramStartingInDaysNumber(entry, name, program, coordinator))
    #     entities.append(ProgramStartTimeOffsetNumber(entry, name, program, coordinator))

    return entities
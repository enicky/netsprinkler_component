import datetime
import logging
from datetime import time
from math import trunc
from typing import Callable

from homeassistant.components.time import TimeEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify


async def async_setup_entry(
    hass: HomeAssistant,
    entry: dict,
    async_add_entities: Callable,
):
    """Set up the OpenSprinkler times."""
    entities = _create_entities(hass, entry)
    async_add_entities(entities)


def _create_entities(hass: HomeAssistant, entry: dict):
    entities = []

    controller = hass.data[DOMAIN][entry.entry_id]["controller"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name = entry.data[CONF_NAME]

    for _, program in controller.programs.items():
        entities.append(ProgramStartTime(entry, name, controller, program, coordinator))

    return entities
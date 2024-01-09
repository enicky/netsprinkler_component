"""Constants for netsprinkler_component."""
from logging import Logger, getLogger
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

LOGGER: Logger = getLogger(__package__)

NAME = "Integration blueprint"
DOMAIN = "netsprinkler_component"
VERSION = "0.0.0"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

DEFAULT_NAME = "NETSprinkler"
DEFAULT_SCAN_INTERVAL = 5

CONF_RUN_SECONDS = "run_seconds"
CONF_INDEX = "index"
CONF_CONTINUE_RUNNING_STATIONS = "continue_running_stations"

SCHEMA_SERVICE_RUN_SECONDS = {
    vol.Required(CONF_INDEX): cv.positive_int,
    vol.Required(CONF_RUN_SECONDS): cv.positive_int,
}
SCHEMA_SERVICE_RUN = {
    vol.Optional(CONF_RUN_SECONDS): vol.Or(
        cv.ensure_list(cv.positive_int),
        cv.ensure_list(SCHEMA_SERVICE_RUN_SECONDS),
        cv.positive_int,
        vol.Schema({}, extra=vol.ALLOW_EXTRA),
    ),
    vol.Optional(CONF_CONTINUE_RUNNING_STATIONS): cv.boolean,
}
SERVICE_RUN = "run"
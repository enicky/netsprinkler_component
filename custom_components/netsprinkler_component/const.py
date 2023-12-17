"""Constants for netsprinkler_component."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Integration blueprint"
DOMAIN = "netsprinkler_component"
VERSION = "0.0.0"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

DEFAULT_NAME = "NETSprinkler"
DEFAULT_SCAN_INTERVAL = 5
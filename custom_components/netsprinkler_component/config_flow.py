"""Adds config flow for Blueprint."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL, CONF_NAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    IntegrationBlueprintApiClient,
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
    IntegrationBlueprintApiClientError,
)
from .const import DOMAIN, LOGGER, DEFAULT_NAME
from .Sprinkler.netsprinkler     import NETSprinkler

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str
    }
)


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:

            try:
                url = user_input[CONF_URL]
                name = user_input[CONF_NAME]

                opts = {"session" : async_get_clientsession(self.hass)}

                controller = NETSprinkler(url, opts)
                await controller.refresh()

            except IntegrationBlueprintApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except IntegrationBlueprintApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except IntegrationBlueprintApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_URL: url
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DEVICE_SCHEMA,
            errors=_errors,
        )

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        client = IntegrationBlueprintApiClient(
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()

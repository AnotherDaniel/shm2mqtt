"""Config flow for shm2mqtt integration"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DATA_SCHEMA, MQTT_ROOT_TOPIC, SERIAL

_LOGGER = logging.getLogger(__name__)


class Shm2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for shm2mqtt"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        title = f"{user_input[MQTT_ROOT_TOPIC]}_{user_input[SERIAL]}"
        # Abort if the same integration was already configured.
        await self.async_set_unique_id(title)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=title, data=user_input)

"""Config flow for Mijn Afvalwijzer."""

from __future__ import annotations

import re

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_HOUSE_NUMBER, CONF_POSTCODE, DOMAIN


class MijnAfvalwijzerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mijn Afvalwijzer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            postcode = user_input[CONF_POSTCODE].upper().replace(" ", "")
            house_number = user_input[CONF_HOUSE_NUMBER].strip()

            if not re.match(r"^\d{4}[A-Z]{2}$", postcode):
                errors[CONF_POSTCODE] = "invalid_postcode"
            elif not house_number.isdigit():
                errors[CONF_HOUSE_NUMBER] = "invalid_house_number"
            else:
                # Check for duplicate entries
                await self.async_set_unique_id(f"{postcode}_{house_number}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"{postcode} {house_number}",
                    data={
                        CONF_POSTCODE: postcode,
                        CONF_HOUSE_NUMBER: house_number,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_POSTCODE): str,
                    vol.Required(CONF_HOUSE_NUMBER): str,
                }
            ),
            errors=errors,
        )

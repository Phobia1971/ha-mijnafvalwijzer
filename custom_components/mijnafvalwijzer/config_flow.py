"""Config flow for Mijn Afvalwijzer."""

from __future__ import annotations

import re

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_HOUSE_NUMBER, CONF_POSTCODE, CONF_PROVIDER, DOMAIN, PROVIDERS


class MijnAfvalwijzerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mijn Afvalwijzer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        # Build provider options: {key: display name}
        provider_options = {
            key: info["name"] for key, info in PROVIDERS.items()
        }

        if user_input is not None:
            postcode = user_input[CONF_POSTCODE].upper().replace(" ", "")
            house_number = user_input[CONF_HOUSE_NUMBER].strip()
            provider = user_input[CONF_PROVIDER]

            if not re.match(r"^\d{4}[A-Z]{2}$", postcode):
                errors[CONF_POSTCODE] = "invalid_postcode"
            elif not house_number.isdigit():
                errors[CONF_HOUSE_NUMBER] = "invalid_house_number"
            elif provider not in PROVIDERS:
                errors[CONF_PROVIDER] = "invalid_provider"
            else:
                await self.async_set_unique_id(
                    f"{provider}_{postcode}_{house_number}"
                )
                self._abort_if_unique_id_configured()

                provider_name = PROVIDERS[provider]["name"]
                return self.async_create_entry(
                    title=f"{provider_name} - {postcode} {house_number}",
                    data={
                        CONF_PROVIDER: provider,
                        CONF_POSTCODE: postcode,
                        CONF_HOUSE_NUMBER: house_number,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PROVIDER, default="mijnafvalwijzer"): vol.In(
                        provider_options
                    ),
                    vol.Required(CONF_POSTCODE): str,
                    vol.Required(CONF_HOUSE_NUMBER): str,
                }
            ),
            errors=errors,
        )

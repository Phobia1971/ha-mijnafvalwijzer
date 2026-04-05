"""The Mijn Afvalwijzer integration."""

from __future__ import annotations

import os

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import CONF_HOUSE_NUMBER, CONF_POSTCODE, DOMAIN
from .coordinator import MijnAfvalwijzerCoordinator

PLATFORMS = [Platform.SENSOR]

CARD_URL = f"/{DOMAIN}/mijnafvalwijzer-card.js"
CARD_FILE = os.path.join(os.path.dirname(__file__), "mijnafvalwijzer-card.js")


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the card frontend resource (once for the whole domain)."""
    hass.http.register_static_path(CARD_URL, CARD_FILE, cache_headers=False)
    add_extra_js_url(hass, CARD_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mijn Afvalwijzer from a config entry."""
    coordinator = MijnAfvalwijzerCoordinator(
        hass,
        postcode=entry.data[CONF_POSTCODE],
        house_number=entry.data[CONF_HOUSE_NUMBER],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

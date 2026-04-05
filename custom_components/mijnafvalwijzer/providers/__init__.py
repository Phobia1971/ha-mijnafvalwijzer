"""Waste collection data providers."""

from __future__ import annotations

from datetime import datetime

from aiohttp import ClientSession

from ..const import PROVIDERS
from .mijnafvalwijzer import fetch_mijnafvalwijzer
from .opzet import fetch_opzet
from .ximmio import fetch_ximmio
from .rova import fetch_rova
from .rd4 import fetch_rd4

FETCHERS = {
    "mijnafvalwijzer": fetch_mijnafvalwijzer,
    "opzet": fetch_opzet,
    "ximmio": fetch_ximmio,
    "rova": fetch_rova,
    "rd4": fetch_rd4,
}


async def fetch_waste_data(
    session: ClientSession,
    provider_key: str,
    postcode: str,
    house_number: str,
) -> dict[str, list[datetime]]:
    """Fetch waste data from the configured provider."""
    provider = PROVIDERS[provider_key]
    provider_type = provider["type"]
    fetcher = FETCHERS[provider_type]
    return await fetcher(session, provider, postcode, house_number)

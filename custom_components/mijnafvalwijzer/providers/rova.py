"""Provider: ROVA."""

from __future__ import annotations

from datetime import datetime

from aiohttp import ClientSession

from .common import empty_result, sort_result, add_date, parse_date


async def fetch_rova(
    session: ClientSession,
    provider: dict,
    postcode: str,
    house_number: str,
) -> dict[str, list[datetime]]:
    """Fetch waste data from ROVA API."""
    url = "https://www.rova.nl/api/waste-calendar/upcoming"
    params = {
        "postalcode": postcode,
        "houseNumber": house_number,
        "addition": "",
        "take": "50",
    }

    async with session.get(url, params=params, timeout=30) as resp:
        resp.raise_for_status()
        data = await resp.json()

    result = empty_result()
    for item in data if isinstance(data, list) else []:
        waste_name = item.get("wasteType", {}).get("title", "")
        date_str = item.get("date", "")
        dt = parse_date(date_str)
        if dt and waste_name:
            add_date(result, waste_name, dt)

    return sort_result(result)

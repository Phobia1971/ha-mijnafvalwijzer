"""Provider: RD4."""

from __future__ import annotations

from datetime import datetime

from aiohttp import ClientSession

from .common import empty_result, sort_result, add_date, parse_date


async def fetch_rd4(
    session: ClientSession,
    provider: dict,
    postcode: str,
    house_number: str,
) -> dict[str, list[datetime]]:
    """Fetch waste data from RD4 API."""
    result = empty_result()

    # RD4 uses postcode format XXXX+YY
    formatted_postcode = postcode[:4] + "+" + postcode[4:]
    year = datetime.now().year

    for y in [year, year + 1]:
        url = "https://data.rd4.nl/api/v1/waste-calendar"
        params = {
            "postal_code": formatted_postcode,
            "house_number": house_number,
            "year": str(y),
        }

        async with session.get(url, params=params, timeout=30) as resp:
            if resp.status != 200:
                continue
            data = await resp.json()

        if not data.get("success"):
            continue

        items = data.get("data", {}).get("items", [])
        if items and isinstance(items[0], dict):
            items = items[0] if isinstance(items[0], list) else items

        for item in items:
            if isinstance(item, dict):
                waste_name = item.get("type", "")
                date_str = item.get("date", "")
                dt = parse_date(date_str)
                if dt and waste_name:
                    add_date(result, waste_name, dt)

    return sort_result(result)

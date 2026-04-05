"""Provider: Opzet-based collectors (Afvalstoffendienstkalender, HVC, GAD, DAR, Cure, etc.)."""

from __future__ import annotations

from datetime import datetime

from aiohttp import ClientSession

from .common import empty_result, sort_result, add_date, parse_date


async def fetch_opzet(
    session: ClientSession,
    provider: dict,
    postcode: str,
    house_number: str,
) -> dict[str, list[datetime]]:
    """Fetch waste data from an Opzet-based API."""
    base_url = provider["base_url"]

    # Step 1: Look up address to get bagId
    address_url = f"{base_url}/rest/adressen/{postcode}-{house_number}"
    async with session.get(address_url, timeout=30) as resp:
        resp.raise_for_status()
        addresses = await resp.json()

    if not addresses:
        return empty_result()

    bag_id = addresses[0].get("bagId")
    if not bag_id:
        return empty_result()

    # Step 2: Fetch waste streams
    waste_url = f"{base_url}/rest/adressen/{bag_id}/afvalstromen"
    async with session.get(waste_url, timeout=30) as resp:
        resp.raise_for_status()
        streams = await resp.json()

    result = empty_result()
    for stream in streams:
        waste_name = stream.get("menu_title", stream.get("title", ""))
        pickup_date = stream.get("ophaaldatum")
        if not waste_name or not pickup_date:
            continue
        dt = parse_date(pickup_date)
        if dt:
            add_date(result, waste_name, dt)

    return sort_result(result)

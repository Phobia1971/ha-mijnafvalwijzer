"""Provider: Ximmio-based collectors (Avalex, Twente Milieu, Circulus, Meerlanden, etc.)."""

from __future__ import annotations

from datetime import datetime, timedelta

from aiohttp import ClientSession

from .common import empty_result, sort_result, add_date, parse_date


async def fetch_ximmio(
    session: ClientSession,
    provider: dict,
    postcode: str,
    house_number: str,
) -> dict[str, list[datetime]]:
    """Fetch waste data from a Ximmio-based API."""
    base_url = provider["base_url"]
    company_code = provider["company_code"]

    # Step 1: Look up address
    address_url = f"{base_url}/api/FetchAdress"
    address_payload = {
        "companyCode": company_code,
        "postCode": postcode.upper(),
        "houseNumber": house_number,
    }
    async with session.post(address_url, json=address_payload, timeout=30) as resp:
        resp.raise_for_status()
        address_data = await resp.json()

    data_list = address_data.get("dataList", [])
    if not data_list:
        return empty_result()

    unique_id = data_list[0].get("UniqueId")
    community = data_list[0].get("Community", "")

    # Step 2: Fetch calendar
    now = datetime.now()
    calendar_url = f"{base_url}/api/GetCalendar"
    calendar_payload = {
        "companyCode": company_code,
        "uniqueAddressID": unique_id,
        "startDate": now.strftime("%Y-%m-%d"),
        "endDate": (now + timedelta(days=365)).strftime("%Y-%m-%d"),
        "community": community,
    }
    async with session.post(calendar_url, json=calendar_payload, timeout=30) as resp:
        resp.raise_for_status()
        calendar_data = await resp.json()

    result = empty_result()
    for item in calendar_data.get("dataList", []):
        waste_name = item.get("_pickupTypeText", "")
        for date_str in item.get("pickupDates", []):
            dt = parse_date(date_str)
            if dt:
                add_date(result, waste_name, dt)

    return sort_result(result)

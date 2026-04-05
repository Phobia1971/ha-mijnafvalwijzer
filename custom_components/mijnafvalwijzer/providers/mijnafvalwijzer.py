"""Provider: Mijn Afvalwijzer (HTML scraping fallback)."""

from __future__ import annotations

import re
from datetime import datetime

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from .common import empty_result, sort_result, classify_waste_type

BASE_URL = "https://www.mijnafvalwijzer.nl/nl/{postcode}/{house_number}/"

DUTCH_MONTHS = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4,
    "mei": 5, "juni": 6, "juli": 7, "augustus": 8,
    "september": 9, "oktober": 10, "november": 11, "december": 12,
}


def _parse_dutch_date(text: str, year: int) -> datetime | None:
    match = re.match(r"\w+\s+(\d{1,2})\s+(\w+)", text.strip())
    if not match:
        return None
    day = int(match.group(1))
    month = DUTCH_MONTHS.get(match.group(2).lower())
    if month is None:
        return None
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def _parse_html(html: str) -> dict[str, list[datetime]]:
    soup = BeautifulSoup(html, "html.parser")
    year = datetime.now().year
    result = empty_result()

    month_sections = soup.find(id="month-sections")
    container = month_sections if month_sections else soup

    for link in container.find_all("a", class_="wasteInfoIcon"):
        date_span = link.find("span", class_="span-line-break")
        desc_span = link.find("span", class_="afvaldescr")
        if not date_span or not desc_span:
            continue

        dt = _parse_dutch_date(date_span.get_text(strip=True), year)
        waste_type = classify_waste_type(desc_span.get_text(strip=True))
        if dt and waste_type and waste_type in result:
            result[waste_type].append(dt)

    return sort_result(result)


async def fetch_mijnafvalwijzer(
    session: ClientSession,
    provider: dict,
    postcode: str,
    house_number: str,
) -> dict[str, list[datetime]]:
    """Fetch waste data from mijnafvalwijzer.nl."""
    url = BASE_URL.format(postcode=postcode, house_number=house_number)
    async with session.get(url, timeout=30) as response:
        response.raise_for_status()
        html = await response.text()
    return _parse_html(html)

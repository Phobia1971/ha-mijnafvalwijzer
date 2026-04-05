"""Data update coordinator for Mijn Afvalwijzer."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
import re

from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, SCAN_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)

DUTCH_MONTHS = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}


def _parse_dutch_date(text: str, year: int) -> datetime | None:
    """Parse a Dutch date string like 'dinsdag 06 januari' into a datetime."""
    match = re.match(r"\w+\s+(\d{1,2})\s+(\w+)", text.strip())
    if not match:
        return None
    day = int(match.group(1))
    month_name = match.group(2).lower()
    month = DUTCH_MONTHS.get(month_name)
    if month is None:
        return None
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def _classify_waste_type(description: str) -> str | None:
    """Classify waste type from the description text."""
    desc_lower = description.lower()
    if "plastic" in desc_lower or "pmd" in desc_lower or "metalen" in desc_lower:
        return "pmd"
    if "groente" in desc_lower or "gft" in desc_lower or "tuinafval" in desc_lower:
        return "gft"
    if "restafval" in desc_lower:
        return "restafval"
    if "papier" in desc_lower:
        return "papier"
    return None


class MijnAfvalwijzerCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch waste collection data."""

    def __init__(
        self, hass: HomeAssistant, postcode: str, house_number: str
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Mijn Afvalwijzer",
            update_interval=timedelta(hours=SCAN_INTERVAL_HOURS),
        )
        self.postcode = postcode
        self.house_number = house_number
        self._previous_data: dict[str, list[datetime]] | None = None
        self._waiting_for_new_data = False

    async def _async_update_data(self) -> dict[str, list[datetime]]:
        """Fetch and parse waste collection data."""
        url = BASE_URL.format(
            postcode=self.postcode, house_number=self.house_number
        )
        session = async_get_clientsession(self.hass)

        try:
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Error fetching data: HTTP {response.status}"
                    )
                html = await response.text()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

        data = await self.hass.async_add_executor_job(self._parse_html, html)

        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        has_future = any(
            any(d >= now for d in dates) for dates in data.values()
        )

        if not has_future and any(data.values()):
            # All dates have passed — poll hourly until the site has new data
            if not self._waiting_for_new_data:
                _LOGGER.info(
                    "All pickup dates have passed, polling hourly for new data"
                )
            self._waiting_for_new_data = True
            self.update_interval = timedelta(hours=1)
        elif self._waiting_for_new_data and has_future:
            # New data appeared — check it actually changed
            if self._previous_data != data:
                _LOGGER.info("New waste collection data detected")
            self._waiting_for_new_data = False
            self.update_interval = timedelta(hours=SCAN_INTERVAL_HOURS)
        else:
            self.update_interval = timedelta(hours=SCAN_INTERVAL_HOURS)

        self._previous_data = data
        return data

    def _parse_html(self, html: str) -> dict[str, list[datetime]]:
        """Parse the HTML and extract collection dates per waste type (all months)."""
        soup = BeautifulSoup(html, "html.parser")
        year = datetime.now().year

        result: dict[str, list[datetime]] = {
            "gft": [],
            "pmd": [],
            "restafval": [],
            "papier": [],
        }

        # Find all waste collection links inside month-sections (all months)
        month_sections = soup.find(id="month-sections")
        container = month_sections if month_sections else soup

        for link in container.find_all("a", class_="wasteInfoIcon"):
            date_span = link.find("span", class_="span-line-break")
            desc_span = link.find("span", class_="afvaldescr")

            if not date_span or not desc_span:
                continue

            date_str = date_span.get_text(strip=True)
            waste_desc = desc_span.get_text(strip=True)

            waste_type = _classify_waste_type(waste_desc)
            if waste_type is None:
                continue

            dt = _parse_dutch_date(date_str, year)
            if dt is None:
                continue

            result[waste_type].append(dt)

        for waste_type in result:
            result[waste_type].sort()

        if not any(result.values()):
            _LOGGER.warning(
                "No waste collection dates found for %s %s",
                self.postcode,
                self.house_number,
            )

        return result

"""Data update coordinator for Mijn Afvalwijzer."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SCAN_INTERVAL_HOURS
from .providers import fetch_waste_data

_LOGGER = logging.getLogger(__name__)


class MijnAfvalwijzerCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch waste collection data."""

    def __init__(
        self,
        hass: HomeAssistant,
        provider_key: str,
        postcode: str,
        house_number: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Mijn Afvalwijzer",
            update_interval=timedelta(hours=SCAN_INTERVAL_HOURS),
        )
        self.provider_key = provider_key
        self.postcode = postcode
        self.house_number = house_number
        self._previous_data: dict[str, list[datetime]] | None = None
        self._waiting_for_new_data = False

    async def _async_update_data(self) -> dict[str, list[datetime]]:
        """Fetch and parse waste collection data."""
        session = async_get_clientsession(self.hass)

        try:
            data = await fetch_waste_data(
                session, self.provider_key, self.postcode, self.house_number
            )
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        has_future = any(
            any(d >= now for d in dates) for dates in data.values()
        )

        if not has_future and any(data.values()):
            if not self._waiting_for_new_data:
                _LOGGER.info(
                    "All pickup dates have passed, polling hourly for new data"
                )
            self._waiting_for_new_data = True
            self.update_interval = timedelta(hours=1)
        elif self._waiting_for_new_data and has_future:
            if self._previous_data != data:
                _LOGGER.info("New waste collection data detected")
            self._waiting_for_new_data = False
            self.update_interval = timedelta(hours=SCAN_INTERVAL_HOURS)
        else:
            self.update_interval = timedelta(hours=SCAN_INTERVAL_HOURS)

        self._previous_data = data
        return data

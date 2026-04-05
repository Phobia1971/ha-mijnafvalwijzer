"""Sensor platform for Mijn Afvalwijzer."""

from __future__ import annotations

from datetime import datetime, time

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, WASTE_TYPES
from .coordinator import MijnAfvalwijzerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mijn Afvalwijzer sensor from a config entry."""
    coordinator: MijnAfvalwijzerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MijnAfvalwijzerSensor(coordinator, entry)], True)


class MijnAfvalwijzerSensor(
    CoordinatorEntity[MijnAfvalwijzerCoordinator], SensorEntity
):
    """Single sensor showing the next waste collection across all types."""

    _attr_has_entity_name = True
    _attr_name = "Volgende ophaling"
    _attr_icon = "mdi:delete-empty"

    WASTE_ICONS = {
        "gft": "mdi:leaf",
        "pmd": "mdi:recycle",
        "restafval": "mdi:trash-can",
        "papier": "mdi:newspaper",
    }

    def __init__(
        self,
        coordinator: MijnAfvalwijzerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next"
        self._unsub_midnight = None

    async def async_added_to_hass(self) -> None:
        """Register midnight update when added to HA."""
        await super().async_added_to_hass()
        self._unsub_midnight = async_track_time_change(
            self.hass, self._midnight_update, hour=0, minute=0, second=0
        )

    async def async_will_remove_from_hass(self) -> None:
        """Clean up midnight listener."""
        if self._unsub_midnight:
            self._unsub_midnight()
            self._unsub_midnight = None
        await super().async_will_remove_from_hass()

    @callback
    def _midnight_update(self, _now=None) -> None:
        """Force a state update at midnight so days_until is recalculated."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        """Return the next collection date as a string."""
        item = self._get_next_item()
        if item is None:
            return None
        return item[0].strftime("%Y-%m-%d")

    @property
    def icon(self) -> str:
        item = self._get_next_item()
        if item is None:
            return "mdi:delete-empty"
        return self.WASTE_ICONS.get(item[1], "mdi:delete-empty")

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        attrs = {}

        item = self._get_next_item()
        if item:
            dt, waste_key = item
            attrs["type"] = WASTE_TYPES[waste_key]["short"]
            attrs["type_full"] = WASTE_TYPES[waste_key]["full"]
            attrs["days_until"] = (dt - now).days
            attrs["day_of_week"] = dt.strftime("%A")

        second = self._get_next_item(skip=1)
        if second:
            dt2, waste_key2 = second
            attrs["next_type"] = WASTE_TYPES[waste_key2]["short"]
            attrs["next_type_full"] = WASTE_TYPES[waste_key2]["full"]
            attrs["next_date"] = dt2.strftime("%Y-%m-%d")
            attrs["next_days_until"] = (dt2 - now).days

        return attrs

    def _get_next_item(self, skip: int = 0) -> tuple[datetime, str] | None:
        """Get the next (or nth) collection across all waste types."""
        if not self.coordinator.data:
            return None
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        all_upcoming: list[tuple[datetime, str]] = []
        for waste_key, dates in self.coordinator.data.items():
            for dt in dates:
                if dt >= now:
                    all_upcoming.append((dt, waste_key))

        all_upcoming.sort(key=lambda x: x[0])

        if len(all_upcoming) > skip:
            return all_upcoming[skip]
        return None

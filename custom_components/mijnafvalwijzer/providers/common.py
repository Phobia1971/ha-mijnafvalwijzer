"""Common utilities for waste data providers."""

from __future__ import annotations

from datetime import datetime

from ..const import WASTE_TYPE_ALIASES


def classify_waste_type(description: str) -> str | None:
    """Classify a waste type string to one of our standard keys."""
    desc = description.strip().lower()

    # Direct match
    if desc in WASTE_TYPE_ALIASES:
        return WASTE_TYPE_ALIASES[desc]

    # Partial match
    if "plastic" in desc or "pmd" in desc or "pbd" in desc or "metalen" in desc:
        return "pmd"
    if "groente" in desc or "gft" in desc or "tuinafval" in desc or "organic" in desc:
        return "gft"
    if "restafval" in desc or "rest" == desc or "residual" in desc:
        return "restafval"
    if "papier" in desc or "paper" in desc or "karton" in desc:
        return "papier"

    return None


def parse_date(date_str: str) -> datetime | None:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
    except (ValueError, IndexError):
        return None


def empty_result() -> dict[str, list[datetime]]:
    """Return an empty result dict."""
    return {"gft": [], "pmd": [], "restafval": [], "papier": []}


def add_date(result: dict, waste_type: str, dt: datetime) -> None:
    """Add a date to the result if the waste type is known."""
    key = classify_waste_type(waste_type)
    if key and key in result:
        result[key].append(dt)


def sort_result(result: dict) -> dict[str, list[datetime]]:
    """Sort all date lists in the result."""
    for key in result:
        result[key].sort()
    return result

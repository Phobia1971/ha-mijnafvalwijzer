"""Constants for the Mijn Afvalwijzer integration."""

DOMAIN = "mijnafvalwijzer"

CONF_POSTCODE = "postcode"
CONF_HOUSE_NUMBER = "house_number"

BASE_URL = "https://www.mijnafvalwijzer.nl/nl/{postcode}/{house_number}/"

WASTE_TYPES = {
    "gft": {
        "short": "GFT",
        "full": "Groente, Fruit en Tuinafval",
    },
    "pmd": {
        "short": "PMD",
        "full": "Plastic, Metalen en Drankkartons",
    },
    "restafval": {
        "short": "Restafval",
        "full": "Restafval",
    },
    "papier": {
        "short": "Papier",
        "full": "Papier en karton",
    },
}

SCAN_INTERVAL_HOURS = 12

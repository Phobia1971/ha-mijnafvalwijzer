"""Constants for the Mijn Afvalwijzer integration."""

DOMAIN = "mijnafvalwijzer"

CONF_POSTCODE = "postcode"
CONF_HOUSE_NUMBER = "house_number"
CONF_PROVIDER = "provider"

SCAN_INTERVAL_HOURS = 12

# Waste type mapping: normalize various names to our standard keys
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

# Aliases used by various providers to map to our standard keys
WASTE_TYPE_ALIASES = {
    # GFT
    "gft": "gft",
    "groente": "gft",
    "gft/tuinafval": "gft",
    "groente, fruit en tuinafval": "gft",
    "groente, fruit- en tuinafval": "gft",
    "gft (groente, fruit en tuinafval)": "gft",
    "organic": "gft",
    "groenafval": "gft",
    "tuinafval": "gft",
    # PMD
    "pmd": "pmd",
    "plastic": "pmd",
    "plastic, metalen en drankkartons": "pmd",
    "pmd (plastic, metaal en drinkpakken)": "pmd",
    "pbd": "pmd",
    "pd": "pmd",
    "kunststof": "pmd",
    # Restafval
    "restafval": "restafval",
    "rest": "restafval",
    "restgft": "restafval",
    "residual": "restafval",
    "grijze bak": "restafval",
    # Papier
    "papier": "papier",
    "papier en karton": "papier",
    "paper": "papier",
    "oud papier": "papier",
    "papier/karton": "papier",
}

# Provider definitions
PROVIDERS = {
    "mijnafvalwijzer": {
        "name": "Mijn Afvalwijzer",
        "type": "mijnafvalwijzer",
    },
    "afvalstoffendienstkalender": {
        "name": "Afvalstoffendienstkalender",
        "type": "opzet",
        "base_url": "https://afvalstoffendienstkalender.nl",
    },
    "hvc": {
        "name": "HVC Groep",
        "type": "opzet",
        "base_url": "https://inzamelkalender.hvcgroep.nl",
    },
    "gad": {
        "name": "GAD",
        "type": "opzet",
        "base_url": "https://inzamelkalender.gad.nl",
    },
    "rova": {
        "name": "ROVA",
        "type": "rova",
    },
    "rd4": {
        "name": "RD4",
        "type": "rd4",
    },
    "avalex": {
        "name": "Avalex",
        "type": "ximmio",
        "base_url": "https://wasteprod2api.ximmio.com",
        "company_code": "f7a74ad1-fdbf-4a43-9f91-44644f4d4222",
    },
    "twentemilieu": {
        "name": "Twente Milieu",
        "type": "ximmio",
        "base_url": "https://wasteapi.ximmio.com",
        "company_code": "8d97bb56-5afd-4cbc-a651-b4f7314264b4",
    },
    "circulus": {
        "name": "Circulus",
        "type": "ximmio",
        "base_url": "https://wasteapi.ximmio.com",
        "company_code": "f8e2844a-095e-48f9-9f98-71f790571571",
    },
    "dar": {
        "name": "DAR",
        "type": "opzet",
        "base_url": "https://afvalkalender.dar.nl",
    },
    "cure": {
        "name": "Cure",
        "type": "opzet",
        "base_url": "https://afvalkalender.cure-afvalbeheer.nl",
    },
    "cyclus": {
        "name": "Cyclus",
        "type": "opzet",
        "base_url": "https://afvalkalender.cyclusnv.nl",
    },
    "rmn": {
        "name": "RMN",
        "type": "opzet",
        "base_url": "https://inzamelschema.rmn.nl",
    },
    "meerlanden": {
        "name": "Meerlanden",
        "type": "ximmio",
        "base_url": "https://wasteapi.ximmio.com",
        "company_code": "800bf8d7-6e1b-4571-b882-adbf42265fad",
    },
    "reinis": {
        "name": "Reinis",
        "type": "opzet",
        "base_url": "https://inzamelkalender.reinis.nl",
    },
    "saver": {
        "name": "Saver",
        "type": "opzet",
        "base_url": "https://inzamelkalender.savermbt.nl",
    },
    "prezero": {
        "name": "PreZero",
        "type": "opzet",
        "base_url": "https://inzamelwijzer.prezero.nl",
    },
    "area": {
        "name": "Area Reiniging",
        "type": "opzet",
        "base_url": "https://afvalkalender.areareiniging.nl",
    },
    "waardlanden": {
        "name": "Waardlanden",
        "type": "ximmio",
        "base_url": "https://wasteapi.ximmio.com",
        "company_code": "942abcf6-3775-400d-ae5d-7571b38bb4f8",
    },
}

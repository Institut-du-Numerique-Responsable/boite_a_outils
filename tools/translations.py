"""Locale registry shared by generators and validation scripts.

Locales are deliberately explicit: a locale is public only when its interface
and editorial catalogue are ready.  This prevents SEO links to half-translated
pages while keeping the future language configuration in one place.
"""

SUPPORTED_LOCALES = ("fr", "en", "nl", "es", "de")

_LOCALES = {
    "fr": {
        "code": "fr",
        "published": True,
        "language_name": "Français",
        "native_name": "Français",
        "main_navigation": "Navigation principale",
    },
    "en": {
        "code": "en",
        "published": True,
        "language_name": "English",
        "native_name": "English",
        "main_navigation": "Main navigation",
    },
    "nl": {
        "code": "nl",
        "published": False,
        "language_name": "Nederlands",
        "native_name": "Nederlands",
        "main_navigation": "Hoofdnavigatie",
    },
    "es": {
        "code": "es",
        "published": False,
        "language_name": "Español",
        "native_name": "Español",
        "main_navigation": "Navegación principal",
    },
    "de": {
        "code": "de",
        "published": False,
        "language_name": "Deutsch",
        "native_name": "Deutsch",
        "main_navigation": "Hauptnavigation",
    },
}


def published_locales():
    """Return locale records in stable menu order."""
    return tuple(_LOCALES[code] for code in SUPPORTED_LOCALES if _LOCALES[code]["published"])


def ui(locale, key):
    """Return a required interface label, failing loudly when absent."""
    try:
        return _LOCALES[locale][key]
    except KeyError as exc:
        raise KeyError(f"Missing UI translation: {locale}.{key}") from exc


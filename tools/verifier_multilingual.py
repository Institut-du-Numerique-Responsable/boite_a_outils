#!/usr/bin/env python3
"""Validate locale attributes and generated SEO links."""

import re
import sys
from pathlib import Path

try:
    from translations import published_locales
except ImportError:  # importé comme module depuis la racine du dépôt
    from tools.translations import published_locales


ROOT = Path(__file__).resolve().parent.parent
WWW = ROOT / "www"
DOMAIN = "https://sustainableit-tools.isit-europe.org"


def pages_for(locale):
    conf = {"fr": ("outils", "themes"), "en": ("en/tools", "en/topics")}[locale]
    for dossier in conf:
        yield from (WWW / dossier).glob("*.html")


def validate():
    published = {item["code"] for item in published_locales()}
    errors = []
    for locale in sorted(published):
        for page in pages_for(locale):
            html = page.read_text(encoding="utf-8")
            if f'<html lang="{locale}"' not in html:
                errors.append(f"{page}: mauvais attribut lang")
            canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            if not canonical or not canonical.group(1).startswith(DOMAIN + "/"):
                errors.append(f"{page}: canonical absente ou invalide")
            for code in re.findall(r'hreflang="([a-z-]+)"', html):
                if code != "x-default" and code not in published:
                    errors.append(f"{page}: locale hreflang non publiée: {code}")
    return errors


if __name__ == "__main__":
    erreurs = validate()
    if erreurs:
        print("\n".join(erreurs), file=sys.stderr)
        sys.exit(1)
    print("Validation multilingue : OK")

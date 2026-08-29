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
    if locale == "fr":
        dossiers = ("outils", "themes")
    else:
        dossiers = (f"{locale}/tools", f"{locale}/topics")
    for dossier in dossiers:
        dossier_path = WWW / dossier
        if dossier_path.exists():
            yield from dossier_path.glob("*.html")


def public_pages():
    published = [item["code"] for item in published_locales()]
    for locale in published:
        yield (WWW / "index.html" if locale == "fr" else WWW / locale / "index.html")
        yield from pages_for(locale)
    yield WWW / "langues" / "index.html"


def public_url(page):
    relative = page.relative_to(WWW).as_posix()
    if relative == "index.html":
        return DOMAIN + "/"
    if relative.endswith("/index.html"):
        return DOMAIN + "/" + relative[:-10]
    return DOMAIN + "/" + relative


def validate():
    published = {item["code"] for item in published_locales()}
    errors = []
    pages = list(public_pages())
    by_url = {public_url(page): page for page in pages}
    sitemap = (WWW / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_urls = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))
    for locale in sorted(published):
        for page in pages_for(locale):
            html = page.read_text(encoding="utf-8")
            if f'<html lang="{locale}"' not in html:
                errors.append(f"{page}: mauvais attribut lang")
            canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            expected = public_url(page)
            if not canonical or canonical.group(1) != expected:
                errors.append(f"{page}: canonical absente ou invalide")
            if expected not in sitemap_urls:
                errors.append(f"{page}: URL absente du sitemap")
            for code, target in re.findall(r'<link rel="alternate" hreflang="([a-z-]+)" href="([^"]+)"', html):
                if code != "x-default" and code not in published:
                    errors.append(f"{page}: locale hreflang non publiée: {code}")
                if code == "x-default":
                    if target != DOMAIN + "/langues/":
                        errors.append(f"{page}: x-default invalide")
                    continue
                target_page = by_url.get(target)
                if target_page is None:
                    errors.append(f"{page}: cible hreflang absente: {target}")
                    continue
                target_html = target_page.read_text(encoding="utf-8")
                if f'hreflang="{locale}"' not in target_html or expected not in target_html:
                    errors.append(f"{page}: hreflang {code} non réciproque")
    for page in pages:
        html = page.read_text(encoding="utf-8")
        if 'name="robots" content="noindex"' not in html and public_url(page) not in sitemap_urls:
            errors.append(f"{page}: page publique absente du sitemap")
    return errors


if __name__ == "__main__":
    erreurs = validate()
    if erreurs:
        print("\n".join(erreurs), file=sys.stderr)
        sys.exit(1)
    print("Validation multilingue : OK")

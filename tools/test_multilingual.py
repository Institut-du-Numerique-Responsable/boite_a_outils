#!/usr/bin/env python3
"""Tests for the locale registry and publication contract."""

import unittest
from pathlib import Path

from tools.translations import SUPPORTED_LOCALES, TERM_GLOSSARY, published_locales, ui
from tools.generer_pages import LANGUES, selecteur_langues
from tools.verifier_multilingual import pages_for
from tools.verifier_donnees import locales_a_verifier


class LocaleRegistryTests(unittest.TestCase):
    def test_supported_locales_are_stable_and_ordered(self):
        self.assertEqual(SUPPORTED_LOCALES, ("fr", "en", "nl", "es", "de"))

    def test_only_locales_with_complete_publication_are_published(self):
        self.assertEqual(tuple(locale["code"] for locale in published_locales()), ("fr", "en"))

    def test_french_and_english_core_labels_are_not_empty(self):
        for locale in ("fr", "en"):
            self.assertTrue(ui(locale, "language_name"))
            self.assertTrue(ui(locale, "main_navigation"))

    def test_dutch_interface_labels_are_translated(self):
        self.assertEqual(LANGUES["nl"]["nav"][0][1], "Hulpmiddelen")
        self.assertEqual(LANGUES["nl"]["champ"]["theme"], "Thema")

    def test_unpublished_locale_has_no_public_navigation(self):
        self.assertNotIn("nl", {locale["code"] for locale in published_locales()})

    def test_planned_locale_catalogues_are_schema_valid_but_unpublished(self):
        root = Path(__file__).parent.parent / "www" / "data"
        for code in ("es", "de"):
            data = __import__("json").loads((root / f"tools-{code}.json").read_text(encoding="utf-8"))
            self.assertEqual(data, {"outils": []})
        nl = __import__("json").loads((root / "tools-nl.json").read_text(encoding="utf-8"))
        self.assertEqual(len(nl["outils"]), 28)

    def test_validator_accepts_any_configured_locale_path(self):
        self.assertEqual(list(pages_for("nl")), [])

    def test_data_validator_discovers_all_configured_catalogues(self):
        self.assertEqual(locales_a_verifier(), ("fr", "en", "nl", "es", "de"))

    def test_language_selector_lists_published_locales_and_marks_current(self):
        markup = selecteur_langues("fr", "../")
        self.assertIn('lang="fr"', markup)
        self.assertIn('lang="en"', markup)
        self.assertIn('aria-current="true"', markup)
        self.assertIn('lang="nl"', markup)
        self.assertIn('aria-disabled="true"', markup)

    def test_generated_pages_have_a_self_canonical_and_language_links(self):
        page = Path(__file__).parent.parent / "www" / "outils" / "42u.html"
        contenu = page.read_text(encoding="utf-8")
        self.assertIn('rel="canonical"', contenu)
        self.assertIn('hreflang="fr"', contenu)
        self.assertIn('hreflang="en"', contenu)
        english = (Path(__file__).parent.parent / "www" / "en" / "tools" / "42u.html").read_text(encoding="utf-8")
        self.assertIn('hreflang="x-default" href="https://sustainableit-tools.isit-europe.org/langues/"', english)
        self.assertIn('href="../../outils/42u.html" lang="fr"', english)
        self.assertIn("(coming soon)", english)
        theme = (Path(__file__).parent.parent / "www" / "themes" / "evaluation-et-mesure.html").read_text(encoding="utf-8")
        self.assertIn('hreflang="en"', theme)

    def test_branding_uses_inr_only_in_french(self):
        root = Path(__file__).parent.parent / "www"
        self.assertIn('src="../../assets/logo-isit.svg" alt=""',
                      (root / "en" / "tools" / "42u.html").read_text(encoding="utf-8"))
        self.assertIn('src="../assets/logo-inr.svg"',
                      (root / "outils" / "42u.html").read_text(encoding="utf-8"))

    def test_non_french_pages_use_isit_name(self):
        english = (Path(__file__).parent.parent / "www" / "en" / "tools" / "42u.html").read_text(encoding="utf-8")
        self.assertIn("Institute for Sustainable IT", english)
        self.assertNotIn("Institut du Numérique Responsable</span>", english)

    def test_international_glossary_uses_isit_and_wEEE(self):
        self.assertEqual(TERM_GLOSSARY["INR"], "ISIT")
        self.assertEqual(TERM_GLOSSARY["DEEE"], "WEEE")
        self.assertEqual(TERM_GLOSSARY["RGAA"], "RGAA")
        self.assertEqual(TERM_GLOSSARY["RGESN"], "RGESN")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for the locale registry and publication contract."""

import unittest

from tools.translations import SUPPORTED_LOCALES, published_locales, ui
from tools.generer_pages import LANGUES, selecteur_langues


class LocaleRegistryTests(unittest.TestCase):
    def test_supported_locales_are_stable_and_ordered(self):
        self.assertEqual(SUPPORTED_LOCALES, ("fr", "en", "nl", "es", "de"))

    def test_only_locales_with_complete_publication_are_published(self):
        self.assertEqual(tuple(locale["code"] for locale in published_locales()), ("fr", "en"))

    def test_french_and_english_core_labels_are_not_empty(self):
        for locale in ("fr", "en"):
            self.assertTrue(ui(locale, "language_name"))
            self.assertTrue(ui(locale, "main_navigation"))

    def test_unpublished_locale_has_no_public_navigation(self):
        self.assertNotIn("nl", {locale["code"] for locale in published_locales()})

    def test_language_selector_lists_published_locales_and_marks_current(self):
        markup = selecteur_langues("fr", "../")
        self.assertIn('lang="fr"', markup)
        self.assertIn('lang="en"', markup)
        self.assertIn('aria-current="true"', markup)
        self.assertNotIn('lang="nl"', markup)


if __name__ == "__main__":
    unittest.main()

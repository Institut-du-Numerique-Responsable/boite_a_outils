#!/usr/bin/env python3
"""Vérifie la cohérence entre les données, les pages générées et le SEO.

À lancer après `generer_pages.py`, avant toute mise en ligne. Contrôle qu'aucune
page n'a été oubliée ni laissée orpheline — une ressource retirée du catalogue
dont la fiche resterait servie continuerait d'être indexée, et pointerait vers
un lien qu'on a justement jugé mauvais.

    cd www && python3 ../tools/verifier_seo.py

Code de sortie 1 si une incohérence est trouvée : utilisable en CI.
"""

import glob
import json
import os
import re
import sys
import urllib.parse

WWW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "www")
anomalies = 0


def verifier(condition, libelle, detail=""):
    global anomalies
    print(("  OK     " if condition else "  ÉCHEC  ") + libelle + (f"  → {detail}" if detail else ""))
    if not condition:
        anomalies += 1


def main():
    os.chdir(WWW)
    fr = json.load(open("data/tools-fr.json", encoding="utf-8"))["outils"]
    en = json.load(open("data/tools-en.json", encoding="utf-8"))["outils"]
    print(f"=== CATALOGUE : {len(fr)} FR / {len(en)} EN ===")

    for lang, outils, dossier in (("fr", fr, "outils"), ("en", en, "en/tools")):
        identifiants = {o["id"] for o in outils}
        pages = {os.path.basename(f)[:-5] for f in glob.glob(f"{dossier}/*.html")} - {"index"}
        verifier(pages == identifiants, f"[{lang}] fiches et données alignées",
                 f"{len(pages)} pages / {len(identifiants)} ressources, "
                 f"manquantes={len(identifiants - pages)}, orphelines={len(pages - identifiants)}")

    for lang, outils, dossier in (("fr", fr, "themes"), ("en", en, "en/topics")):
        themes = {o["theme"] for o in outils}
        pages = {os.path.basename(f)[:-5] for f in glob.glob(f"{dossier}/*.html")} - {"index"}
        verifier(len(pages) == len(themes), f"[{lang}] pages de thème",
                 f"{len(pages)} pages / {len(themes)} thèmes")

    sitemap = open("sitemap.xml", encoding="utf-8").read()
    adresses = re.findall(r"<loc>(.*?)</loc>", sitemap)
    introuvables = []
    for adresse in adresses:
        chemin = urllib.parse.urlparse(adresse).path.lstrip("/")
        cible = chemin if chemin.endswith(".html") else os.path.join(chemin, "index.html")
        if not os.path.exists(cible or "index.html"):
            introuvables.append(adresse)
    verifier(not introuvables, f"sitemap : {len(adresses)} URL, toutes servies",
             f"introuvables : {introuvables[:3]}")

    toutes = set(glob.glob("**/*.html", recursive=True)) - {"404.html"}
    listees = {urllib.parse.urlparse(a).path.lstrip("/") or "index.html" for a in adresses}
    listees = {p if p.endswith(".html") else p + "index.html" for p in listees}
    oubliees = toutes - listees
    verifier(not oubliees, "aucune page absente du sitemap",
             f"{len(oubliees)} oubliée(s) : {sorted(oubliees)[:3]}")
    verifier(all("lastmod" in bloc for bloc in re.findall(r"<url>(.*?)</url>", sitemap, re.S)),
             "chaque URL porte un lastmod")

    llms = open("llms.txt", encoding="utf-8").read()
    verifier(str(len(fr)) in llms, "llms.txt annonce le bon total")
    complet = open("llms-full.txt", encoding="utf-8").read()
    verifier(complet.count("### ") == len(fr), "llms-full.txt contient chaque ressource",
             f"{complet.count('### ')} fiches")

    robots = open("robots.txt", encoding="utf-8").read()
    verifier(all(bot in robots for bot in ("GPTBot", "ClaudeBot", "PerplexityBot")),
             "robots.txt autorise les robots d'IA")
    verifier("Sitemap:" in robots, "robots.txt déclare le sitemap")

    accueil = open("index.html", encoding="utf-8").read()
    verifier("application/ld+json" in accueil and "SearchAction" in accueil,
             "JSON-LD SearchAction sur l'accueil")
    fiche = open(f"outils/{fr[0]['id']}.html", encoding="utf-8").read()
    verifier("BreadcrumbList" in fiche and "canonical" in fiche,
             "fiche : fil d'Ariane et canonique")

    print()
    if anomalies:
        print(f"{anomalies} incohérence(s). Relancer generer_pages.py, puis corriger.")
        sys.exit(1)
    print("SEO et données cohérents.")


if __name__ == "__main__":
    main()

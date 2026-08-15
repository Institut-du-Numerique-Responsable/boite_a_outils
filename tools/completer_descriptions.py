#!/usr/bin/env python3
"""Complète les descriptions manquantes à partir des sites référencés.

On ne rédige rien à la place des auteurs : on récupère la méta-description
(ou og:description, ou le premier paragraphe utile) de la page cible, on la
nettoie, et on la stocke. Les ressources dont la page ne fournit rien
d'exploitable sont listées en fin d'exécution pour rédaction manuelle.

    python3 tools/completer_descriptions.py            # aperçu, n'écrit rien
    python3 tools/completer_descriptions.py --ecrire   # applique les trouvailles
"""

import concurrent.futures
import html
import json
import os
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "www", "data")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
CONTEXTE = ssl.create_default_context()

MINIMUM = 60      # en dessous, une description n'apprend rien
MAXIMUM = 420     # au delà, on coupe à la phrase

BALISES = [
    r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
    r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:description["\']',
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
    r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']',
    r'<meta[^>]+name=["\']twitter:description["\'][^>]+content=["\'](.*?)["\']',
]


def recuperer(url):
    requete = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr,en;q=0.8",
    })
    with urllib.request.urlopen(requete, timeout=25, context=CONTEXTE) as reponse:
        type_contenu = reponse.headers.get("Content-Type", "")
        if "html" not in type_contenu:
            return None
        brut = reponse.read(400_000)
    encodage = "utf-8"
    trouve = re.search(rb'charset=["\']?([\w-]+)', brut[:4000], re.I)
    if trouve:
        encodage = trouve.group(1).decode("ascii", "ignore")
    try:
        return brut.decode(encodage, "replace")
    except LookupError:
        return brut.decode("utf-8", "replace")


def nettoyer(texte):
    texte = html.unescape(texte or "")
    texte = re.sub(r"\s+", " ", texte).strip()
    texte = texte.strip(" \"'|·—-")
    if len(texte) > MAXIMUM:
        coupe = texte[:MAXIMUM]
        point = max(coupe.rfind(". "), coupe.rfind("! "), coupe.rfind("? "))
        texte = coupe[:point + 1] if point > MINIMUM else coupe.rsplit(" ", 1)[0] + "…"
    return texte


def extraire(page):
    for motif in BALISES:
        trouve = re.search(motif, page, re.I | re.S)
        if trouve:
            candidat = nettoyer(trouve.group(1))
            if len(candidat) >= MINIMUM:
                return candidat
    # Repli : premier paragraphe de contenu réel.
    corps = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", page)
    for bloc in re.findall(r"(?is)<p[^>]*>(.*?)</p>", corps)[:12]:
        candidat = nettoyer(re.sub(r"(?s)<[^>]+>", " ", bloc))
        if len(candidat) >= 120:
            return candidat
    return None


def traiter(outil):
    try:
        page = recuperer(outil["url"])
    except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, ssl.SSLError):
        return outil, None, "inaccessible"
    except Exception as erreur:
        return outil, None, type(erreur).__name__
    if not page:
        return outil, None, "pas du HTML"
    description = extraire(page)
    return outil, description, None if description else "rien d'exploitable"


def main():
    ecrire = "--ecrire" in sys.argv
    restants = []

    for lang in ("fr", "en"):
        chemin = os.path.join(DATA, f"tools-{lang}.json")
        with open(chemin, encoding="utf-8") as fichier:
            charge = json.load(fichier)

        cibles = [o for o in charge["outils"]
                  if not o.get("description", "").strip()
                  and o.get("url")
                  and o.get("lien_ok") != "interne"]
        if not cibles:
            print(f"[{lang}] aucune description manquante")
            continue

        print(f"[{lang}] {len(cibles)} description(s) à compléter…", flush=True)
        trouvees = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executeur:
            for outil, description, raison in executeur.map(traiter, cibles):
                if description:
                    trouvees += 1
                    outil["description"] = description
                    outil["description_source"] = "site officiel"
                    print(f"  ✓ {outil['nom'][:38]:38s} {description[:80]}")
                else:
                    restants.append((lang, outil["nom"], outil["url"], raison))
                    print(f"  · {outil['nom'][:38]:38s} — {raison}")

        print(f"[{lang}] {trouvees}/{len(cibles)} complétées")

        if ecrire and trouvees:
            with open(chemin, "w", encoding="utf-8") as fichier:
                json.dump(charge, fichier, ensure_ascii=False, indent=1)
                fichier.write("\n")
            print(f"[{lang}] {chemin} réécrit")

    if restants:
        print(f"\n{len(restants)} ressource(s) à décrire à la main :")
        for lang, nom, url, raison in restants:
            print(f"  [{lang}] {nom}\n        {url}\n        ({raison})")

    if not ecrire:
        print("\nAperçu seulement. Relancer avec --ecrire pour appliquer.")


if __name__ == "__main__":
    main()

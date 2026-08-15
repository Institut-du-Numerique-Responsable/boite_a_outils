#!/usr/bin/env python3
"""Repère les domaines expirés puis rachetés.

Un lien qui répond 200 n'est pas un lien valide : quand un domaine est
abandonné, il est souvent racheté et repeuplé — jeux d'argent, pharmacie,
contenu automatisé. L'audit HTTP ne voit rien, la fiche continue d'exister,
et l'INR recommande un site qu'il n'a jamais approuvé.

Ce script lit le titre et la description de chaque page référencée et signale
celles qui n'ont plus aucun rapport avec la ressource attendue.

    python3 tools/detecter_detournements.py
"""

import concurrent.futures
import html
import json
import os
import re
import ssl
import unicodedata
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "www", "data")
CTX = ssl.create_default_context()
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Vocabulaire des fermes de contenu qui reprennent les domaines abandonnés.
SUSPECT = re.compile(
    r"\b(judi|slot|gacor|casino|poker|togel|bandar|taruhan|situs|maxwin|"
    r"betting|sportsbook|viagra|cialis|pharmacy|escort|porn|crypto\s*signals|"
    r"forex\s*trading|essay\s*writing|write\s*my\s*(essay|paper))\b", re.I)

# Langues sans rapport avec un catalogue francophone ou anglophone : indice fort.
ALPHABETS = re.compile(r"[Ѐ-ӿ一-鿿؀-ۿ฀-๿]")


def sans_accents(texte):
    texte = unicodedata.normalize("NFKD", str(texte).lower())
    return "".join(c for c in texte if not unicodedata.combining(c))


def mots(texte):
    return {m for m in re.findall(r"[a-z0-9]{4,}", sans_accents(texte))}


def lire(url):
    requete = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "fr,en;q=0.8"})
    with urllib.request.urlopen(requete, timeout=25, context=CTX) as reponse:
        if "html" not in reponse.headers.get("Content-Type", ""):
            return None, None, reponse.geturl()
        brut = reponse.read(200_000)
        final = reponse.geturl()
    page = brut.decode("utf-8", "replace")
    titre = re.search(r"(?is)<title[^>]*>(.*?)</title>", page)
    desc = re.search(r'(?is)<meta[^>]+name="description"[^>]+content="(.*?)"', page)
    return (html.unescape(titre.group(1)).strip() if titre else "",
            html.unescape(desc.group(1)).strip() if desc else "", final)


def examiner(outil):
    try:
        titre, desc, final = lire(outil["url"])
    except (urllib.error.HTTPError, urllib.error.URLError, Exception):
        return None
    if titre is None:
        return None

    contenu = f"{titre} {desc}"
    motifs = []

    if SUSPECT.search(contenu):
        motifs.append("vocabulaire de ferme de contenu")
    if ALPHABETS.search(contenu):
        motifs.append("écriture sans rapport avec le catalogue")

    # Le nom de la ressource ou son domaine devraient apparaître quelque part.
    attendu = mots(outil["nom"]) | mots(re.sub(r"^https?://(www\.)?", "", outil["url"]).split("/")[0])
    attendu = {m for m in attendu if m not in {"http", "https", "html", "index", "page"}}
    trouve = mots(contenu)
    if attendu and titre and not (attendu & trouve):
        motifs.append("titre sans rapport avec la ressource")

    # Redirection vers un domaine entièrement différent : signal fort.
    domaine_origine = re.sub(r"^https?://(www\.)?", "", outil["url"]).split("/")[0]
    domaine_final = re.sub(r"^https?://(www\.)?", "", final or "").split("/")[0]
    if domaine_final and domaine_origine.split(".")[-2:] != domaine_final.split(".")[-2:]:
        motifs.append(f"redirigé vers {domaine_final}")

    if motifs:
        return {"nom": outil["nom"], "url": outil["url"], "titre": titre[:110],
                "motifs": motifs}
    return None


def main():
    signales = []
    for lang in ("fr", "en"):
        with open(os.path.join(DATA, f"tools-{lang}.json"), encoding="utf-8") as fichier:
            outils = json.load(fichier)["outils"]
        cibles = [o for o in outils if o.get("url") and o.get("lien_ok") == "ok"]
        print(f"[{lang}] examen de {len(cibles)} pages…", flush=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executeur:
            for resultat in executeur.map(examiner, cibles):
                if resultat:
                    resultat["lang"] = lang
                    signales.append(resultat)

    # Deux motifs ou plus : quasi certain. Un seul : à regarder.
    certains = [s for s in signales if len(s["motifs"]) >= 2]
    doutes = [s for s in signales if len(s["motifs"]) == 1]

    print(f"\n===== {len(certains)} DÉTOURNEMENT(S) PROBABLE(S) =====")
    for s in certains:
        print(f"  [{s['lang']}] {s['nom']}\n      {s['url']}\n"
              f"      titre actuel : {s['titre']}\n      motifs : {', '.join(s['motifs'])}")

    print(f"\n===== {len(doutes)} à regarder =====")
    for s in doutes:
        print(f"  [{s['lang']}] {s['nom'][:44]:44s} {s['motifs'][0]}\n"
              f"      {s['titre'][:100]}")

    print("\nAucune modification faite : ces cas demandent un jugement humain.")


if __name__ == "__main__":
    main()

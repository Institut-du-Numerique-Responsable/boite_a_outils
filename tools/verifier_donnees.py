#!/usr/bin/env python3
"""Vérifie — et au besoin met à jour — les données du site.

Les fichiers www/data/tools-*.json sont la source de vérité : on les modifie
directement. Ce script est le garde-fou avant publication.

    python3 tools/verifier_donnees.py
        Contrôle la structure : champs obligatoires, identifiants uniques,
        URL bien formées, thèmes orphelins. Ne modifie rien.

    python3 tools/verifier_donnees.py --liens
        Rappelle chaque URL, met à jour « lien_ok » et « verifie_le »,
        et signale les liens devenus morts sans les retirer.

    python3 tools/verifier_donnees.py --liens --retirer-morts
        Idem, mais retire les ressources dont le lien ne répond plus.
        Les ressources retirées sont écrites dans tools/retirees-AAAA-MM-JJ.csv.

Code de sortie 1 si une anomalie bloquante subsiste : utilisable en CI.
"""

import concurrent.futures
import csv
import json
import os
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "www", "data")

CHAMPS_OBLIGATOIRES = ["id", "nom", "description", "url", "theme", "type", "tags",
                       "lien_ok", "verifie_le"]
LIEN_OK_VALIDES = {"ok", "a-verifier", "interne"}

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
# TLS vérifié : un certificat invalide n'est pas un détail technique, c'est une
# information à donner sur la ressource. Le lien passe alors en « à revérifier ».
CONTEXTE = ssl.create_default_context()

MORT = re.compile(r"^(404|410)$|gaierror|NameResolution")


def appeler(url):
    for methode in ("HEAD", "GET"):
        try:
            requete = urllib.request.Request(
                url, method=methode, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(requete, timeout=20, context=CONTEXTE) as reponse:
                return str(reponse.status), reponse.geturl()
        except urllib.error.HTTPError as erreur:
            if methode == "HEAD" and erreur.code in (400, 403, 405, 501):
                continue
            return str(erreur.code), url
        except urllib.error.URLError as erreur:
            if isinstance(erreur.reason, ssl.SSLCertVerificationError):
                return "ERR:certificat", url
            return "ERR:" + type(erreur.reason).__name__, url
        except socket.timeout:
            return "ERR:timeout", url
        except Exception as erreur:  # réseau capricieux : on ne veut pas tout arrêter
            return "ERR:" + type(erreur).__name__, url
    return "ERR:inconnu", url


def controler(outils, lang):
    anomalies = []
    identifiants = {}

    for position, outil in enumerate(outils):
        prefixe = f"[{lang}] #{position} « {outil.get('nom', '(sans nom)')} »"

        for champ in CHAMPS_OBLIGATOIRES:
            if champ not in outil:
                anomalies.append(f"{prefixe} : champ « {champ} » absent")

        if not outil.get("nom", "").strip():
            anomalies.append(f"{prefixe} : nom vide")

        identifiant = outil.get("id", "")
        if not identifiant:
            anomalies.append(f"{prefixe} : identifiant vide")
        elif identifiant in identifiants:
            anomalies.append(f"{prefixe} : identifiant « {identifiant} » déjà utilisé "
                             f"par « {identifiants[identifiant]} »")
        else:
            identifiants[identifiant] = outil.get("nom")

        url = outil.get("url", "")
        interne = outil.get("lien_ok") == "interne"
        if interne:
            if not outil.get("loi"):
                anomalies.append(f"{prefixe} : marqué « interne » sans contenu de fiche")
        elif not url:
            anomalies.append(f"{prefixe} : url vide (mettre lien_ok = interne si c'est une fiche)")
        elif not url.startswith(("http://", "https://")):
            anomalies.append(f"{prefixe} : url mal formée → {url}")

        if outil.get("lien_ok") not in LIEN_OK_VALIDES:
            anomalies.append(f"{prefixe} : lien_ok = « {outil.get('lien_ok')} », "
                             f"attendu {sorted(LIEN_OK_VALIDES)}")

        if not isinstance(outil.get("tags", []), list):
            anomalies.append(f"{prefixe} : tags doit être une liste")

        if not outil.get("theme", "").strip():
            anomalies.append(f"{prefixe} : thème vide")

        if "nouveau" in outil:
            anomalies.append(f"{prefixe} : champ « nouveau » obsolète, "
                             "remplacé par « ajoute_le » (année d'entrée au catalogue)")
        annee = outil.get("ajoute_le")
        if annee and not (isinstance(annee, str) and annee.isdigit() and len(annee) == 4):
            anomalies.append(f"{prefixe} : ajoute_le = « {annee} », attendu une année sur "
                             "quatre chiffres")

    # Un thème à une seule ressource encombre la colonne de filtres sans rendre service.
    themes = {}
    for outil in outils:
        themes[outil.get("theme", "")] = themes.get(outil.get("theme", ""), 0) + 1
    maigres = [t for t, n in themes.items() if n < 2]
    for theme in maigres:
        anomalies.append(f"[{lang}] avertissement : le thème « {theme} » n'a qu'une ressource")

    return anomalies, maigres


def rafraichir_liens(outils, lang, retirer_morts):
    a_tester = [o for o in outils if o.get("lien_ok") != "interne" and o.get("url")]
    print(f"[{lang}] test de {len(a_tester)} liens…", flush=True)

    aujourd_hui = date.today().isoformat()
    morts = []

    def travail(outil):
        statut, finale = appeler(outil["url"])
        return outil, statut, finale

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executeur:
        for numero, (outil, statut, finale) in enumerate(executeur.map(travail, a_tester), 1):
            if MORT.search(statut):
                morts.append((outil, statut))
                continue
            if statut == "200":
                if finale and finale != outil["url"]:
                    print(f"   redirection : {outil['nom']}\n      {outil['url']}\n   -> {finale}")
                    outil["url"] = finale
                outil["lien_ok"] = "ok"
            else:
                outil["lien_ok"] = "a-verifier"
            outil["verifie_le"] = aujourd_hui
            if numero % 50 == 0:
                print(f"   {numero}/{len(a_tester)}", flush=True)

    if morts:
        print(f"[{lang}] {len(morts)} lien(s) mort(s) :")
        for outil, statut in morts:
            print(f"   [{statut}] {outil['nom']} — {outil['url']}")
        if retirer_morts:
            a_retirer = {id(o) for o, _ in morts}
            outils[:] = [o for o in outils if id(o) not in a_retirer]
            chemin = os.path.join(HERE, f"retirees-{aujourd_hui}.csv")
            nouveau = not os.path.exists(chemin)
            with open(chemin, "a", encoding="utf-8", newline="") as fichier:
                writer = csv.writer(fichier)
                if nouveau:
                    writer.writerow(["langue", "outil", "theme", "url", "statut"])
                for outil, statut in morts:
                    writer.writerow([lang, outil["nom"], outil["theme"], outil["url"], statut])
            print(f"[{lang}] retirés du catalogue, consignés dans {os.path.basename(chemin)}")
        else:
            print(f"[{lang}] conservés. Relancer avec --retirer-morts pour les supprimer.")

    return len(morts)


def main():
    tester_liens = "--liens" in sys.argv
    retirer_morts = "--retirer-morts" in sys.argv
    if retirer_morts and not tester_liens:
        sys.exit("--retirer-morts n'a de sens qu'avec --liens")

    bloquantes = 0

    for lang in ("fr", "en"):
        chemin = os.path.join(DATA, f"tools-{lang}.json")
        if not os.path.exists(chemin):
            print(f"[{lang}] fichier absent : {chemin}")
            bloquantes += 1
            continue

        with open(chemin, encoding="utf-8") as fichier:
            charge = json.load(fichier)
        outils = charge["outils"]

        anomalies, maigres = controler(outils, lang)
        erreurs = [a for a in anomalies if "avertissement" not in a]
        avertissements = [a for a in anomalies if "avertissement" in a]

        print(f"\n=== {lang.upper()} : {len(outils)} ressources ===")
        for ligne in erreurs:
            print("  ERREUR       " + ligne)
        for ligne in avertissements:
            print("  AVERTISSEMENT " + ligne)
        if not anomalies:
            print("  structure conforme")
        bloquantes += len(erreurs)

        if tester_liens:
            rafraichir_liens(outils, lang, retirer_morts)
            charge["genere_le"] = date.today().isoformat()
            with open(chemin, "w", encoding="utf-8") as fichier:
                json.dump(charge, fichier, ensure_ascii=False, indent=1)
                fichier.write("\n")
            print(f"[{lang}] {chemin} réécrit")

    print()
    if bloquantes:
        print(f"{bloquantes} anomalie(s) bloquante(s). Corrigez avant publication.")
        sys.exit(1)
    print("Données publiables.")


if __name__ == "__main__":
    main()

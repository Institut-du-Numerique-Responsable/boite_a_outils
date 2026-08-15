#!/usr/bin/env python3
"""Génère les données statiques de la boîte à outils NR.

Sources :
  - db_dump.json     : export de l'ancienne base MySQL (281 outils FR, 232 EN)
  - outils_raw.json  : XLSX « 202404_INR_Boite_à_outils_NR_V2.1 » (310 outils)
  - db_link_audit.json / link_audit.json : état HTTP de chaque lien

Sorties :
  - www/data/tools-fr.json, www/data/tools-en.json
  - tools/rapport-liens-morts.csv    : outils retirés, à re-sourcer
  - tools/rapport-redirections.csv   : URL réécrites
  - tools/rapport-a-reclasser.csv    : outils dont le thème est déduit
"""

import csv
import json
import os
import re
import unicodedata
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "www", "data")

# Statuts considérés comme « lien mort » : on retire l'outil du site.
DEAD = re.compile(r"^(404|410)$|gaierror|NameResolution")
# Statuts à vérifier humainement : on garde l'outil, on le signale dans le rapport.
SUSPECT = re.compile(r"^(403|429|5\d\d)$|timeout|SSLEOF|ConnectionReset|RemoteDisconnected|OSError")

# Thème de repli pour les outils présents seulement dans l'ancienne base.
# Revu à la main par l'INR : cf. rapport-a-reclasser.csv
CAT_DB_TO_THEME = {
    "Urgence Climatique": "Urgence climatique",
    "MOOC": "Sensibilisation et formation",
    "Juridique": "Juridique et réglementation",
    "Référence": "Références et guides",
    "Back-End": "Éco-conception (Web)",
    "Front-End": "Éco-conception (Web)",
    "Contenus": "Marketing et Communication",
    "Hébergement": "Gestion de l'énergie et des ressources",
    "IoT": "DEEEE et Equipements",
    "Ux/Ui": "Conception web",
    "Stratégie": "Démarche pour les organisations / entreprises",
    "Transverse": "Évaluation et mesure",
}
# Affine le repli quand un hashtag est plus précis que la catégorie d'origine.
HASHTAG_TO_THEME = {
    "accessibilité": "Accessibilité & inclusivité",
    "rgaa": "Accessibilité & inclusivité",
    "inclusion": "Accessibilité & inclusivité",
    "empreinte carbone": "Évaluation et mesure",
    "bilan carbone": "Évaluation et mesure",
    "acv": "Évaluation et mesure",
    "mesure": "Évaluation et mesure",
    "calculatrice": "Évaluation et mesure",
    "ia": "IA",
    "data privacy": "Respect de la vie privée, transparence et éthique",
    "ethique": "Respect de la vie privée, transparence et éthique",
    "formation": "Sensibilisation et formation",
    "deee": "DEEEE et Equipements",
}

TYPE_NORMALISE = {
    "outils": "Outil",
    "articles": "Article",
    "guide / référentiel": "Guide / Référentiel",
}

# Le XLSX et la base orthographient différemment les mêmes thèmes.
THEME_NORMALISE = {
    "eco-conception (web)": "Éco-conception (Web)",
    "on ne sait pas": "Références et guides",
    "documentation": "Références et guides",
    "urgence climatique": "Sensibilisation et formation",
    "pour aller plus loin - en phase de qualification : innovation/ recherche":
        "Innovation et recherche",
}


def normalise_theme(theme):
    theme = clean(theme)
    if theme.lower().startswith("pour aller plus loin"):
        return "Innovation et recherche"
    return THEME_NORMALISE.get(theme.lower(), theme)


def slug(value):
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value


def norm_url(url):
    if not url:
        return ""
    url = str(url).strip().lower()
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"^www\.", "", url)
    return url.rstrip("/")


def norm_name(name):
    if not name:
        return ""
    name = unicodedata.normalize("NFKD", str(name).lower())
    name = "".join(c for c in name if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", name)


def clean(value):
    if value is None:
        return ""
    value = str(value).strip()
    return "" if value.lower() in ("none", "nan", "?") else value


def titre(nom):
    """L'ancienne base a tout passé en minuscules ; on restaure les sigles."""
    nom = clean(nom)
    if not nom:
        return nom
    if nom.isupper() or not nom[0].islower():
        return nom
    return nom[0].upper() + nom[1:]


def reparer_url(lien):
    """L'ancienne base contient des adresses tronquées à la saisie."""
    lien = clean(lien)
    if not lien:
        return lien
    if lien.startswith("ttps://"):
        return "h" + lien
    if lien.startswith("://"):
        return "https" + lien
    if not lien.startswith(("http://", "https://", "fiche-outils.php")):
        return "https://" + lien.lstrip("/")
    return lien


def parse_loi(texte):
    """precision_3 encode des listes avec « _ » (paragraphe) et « - » (puce)."""
    blocs = []
    for morceau in str(texte).split("_"):
        morceau = morceau.strip()
        if not morceau:
            continue
        if morceau.startswith("-"):
            puces = [p.strip(" -") for p in morceau.split("/") if p.strip(" -")]
            blocs.append({"type": "liste", "items": puces})
        else:
            blocs.append({"type": "paragraphe", "texte": morceau})
    return blocs


def charger(nom):
    with open(os.path.join(HERE, nom), encoding="utf-8") as fichier:
        return json.load(fichier)


def main():
    db = charger("db_dump.json")
    xlsx = charger("outils_raw.json")
    audit = {}
    for entree in charger("db_link_audit.json") + charger("link_audit.json"):
        audit[entree["url"]] = entree

    # ---- index XLSX par URL et par nom -------------------------------------
    xlsx_par_url, xlsx_par_nom = {}, {}
    for ligne in xlsx:
        if clean(ligne.get("Lien")):
            xlsx_par_url.setdefault(norm_url(ligne["Lien"]), ligne)
        if clean(ligne.get("Nom de l'outil")):
            xlsx_par_nom.setdefault(norm_name(ligne["Nom de l'outil"]), ligne)

    morts, redirections, reclasser = [], [], []
    aujourd_hui = date.today().isoformat()

    def etat_lien(url):
        """-> (url_finale, statut, mort?)"""
        info = audit.get(url)
        if not info:
            return url, "non-teste", False
        statut = str(info["status"])
        if DEAD.search(statut):
            return url, statut, True
        finale = info.get("final") or url
        if statut == "200" and finale != url:
            redirections.append((url, finale))
            return finale, "ok", False
        return url, "ok" if statut == "200" else statut, False

    def construire(lang):
        table_outils = "tools_ifs_outils" if lang == "fr" else "tools_ifs_en_outils"
        table_cats = "tools_ifs_categorie" if lang == "fr" else "tools_ifs_en_categorie"
        table_meta = "tools_ifs_outils_meta" if lang == "fr" else "tools_ifs_en_outils_meta"

        cats = {c["id"]: clean(c["nom_cat"]) for c in db[table_cats]}
        tags_par_outil = {}
        for meta in db[table_meta]:
            if meta["meta_key"] == "hashtag" and clean(meta["meta_value"]):
                tags_par_outil.setdefault(meta["id_outil"], []).append(clean(meta["meta_value"]))

        outils, vus_url, vus_nom = [], set(), set()

        for source in db[table_outils]:
            nom = titre(source["nom"])
            lien = clean(source["lien"])
            cat_db = cats.get(source["id_cat"], "")
            tags = sorted(set(tags_par_outil.get(source["id"], [])))

            # Fiche juridique interne : pas un lien externe, on garde le contenu.
            if lien.startswith("fiche-outils.php"):
                outils.append({
                    "id": slug(nom),
                    "nom": nom,
                    "description": clean(source["description"]),
                    "url": "",
                    "theme": "Juridique et réglementation",
                    "domaine": cat_db,
                    "type": "Loi / Règlement",
                    "profil": "",
                    "cout": "",
                    "tags": tags,
                    "lien_ok": "interne",
                    "verifie_le": aujourd_hui,
                    "loi": {
                        "concernes": clean(source["precision_1"]),
                        "depuis": clean(source["precision_2"]),
                        "contenu": parse_loi(source["precision_3"]),
                        "sanctions": clean(source["precision_4"]),
                    },
                })
                continue

            lien = reparer_url(lien)

            url_finale, statut, mort = etat_lien(lien)
            if mort:
                morts.append((lang, nom, cat_db, lien, statut))
                continue

            fiche = xlsx_par_url.get(norm_url(lien)) or xlsx_par_nom.get(norm_name(nom)) or {}
            theme = normalise_theme(fiche.get("Catégorie"))
            if not theme:
                theme = normalise_theme(next(
                    (HASHTAG_TO_THEME[t.lower()] for t in tags if t.lower() in HASHTAG_TO_THEME),
                    CAT_DB_TO_THEME.get(cat_db, "Références et guides"),
                ))
                reclasser.append((lang, nom, cat_db, theme))

            type_outil = clean(fiche.get("Type"))
            type_outil = TYPE_NORMALISE.get(type_outil.lower(), type_outil)

            outils.append({
                "id": slug(nom),
                "nom": nom,
                "description": clean(source["description"]) or clean(fiche.get("Description")),
                "url": url_finale,
                "theme": theme,
                "domaine": clean(fiche.get("Cible Architecture pour les Profils Experts et Intermédiaires")) or cat_db,
                "type": type_outil,
                "profil": clean(fiche.get("A qui s'adresse l'outil - Profil")),
                "cout": clean(fiche.get("Gratuit/payant")),
                "tags": tags,
                "lien_ok": "ok" if statut == "ok" else "a-verifier",
                "verifie_le": aujourd_hui,
            })
            vus_url.add(norm_url(url_finale))
            vus_nom.add(norm_name(nom))

        # ---- outils présents seulement dans le XLSX 2024 (FR uniquement) ----
        if lang == "fr":
            for ligne in xlsx:
                lien = reparer_url(ligne.get("Lien"))
                nom = clean(ligne.get("Nom de l'outil"))
                if not lien or not nom:
                    continue
                if norm_url(lien) in vus_url or norm_name(nom) in vus_nom:
                    continue
                url_finale, statut, mort = etat_lien(lien)
                if mort:
                    morts.append((lang, nom, clean(ligne.get("Catégorie")), lien, statut))
                    continue
                type_outil = clean(ligne.get("Type"))
                outils.append({
                    "id": slug(nom),
                    "nom": nom,
                    "description": clean(ligne.get("Description")),
                    "url": url_finale,
                    "theme": normalise_theme(ligne.get("Catégorie")) or "Références et guides",
                    "domaine": clean(ligne.get("Cible Architecture pour les Profils Experts et Intermédiaires")),
                    "type": TYPE_NORMALISE.get(type_outil.lower(), type_outil),
                    "profil": clean(ligne.get("A qui s'adresse l'outil - Profil")),
                    "cout": clean(ligne.get("Gratuit/payant")),
                    "tags": [],
                    "lien_ok": "ok" if statut == "ok" else "a-verifier",
                    "verifie_le": aujourd_hui,
                    # Année d'entrée au catalogue : ces ressources viennent du
                    # classeur 2024, jamais publié sur l'ancien site.
                    "ajoute_le": "2024",
                })
                vus_url.add(norm_url(url_finale))
                vus_nom.add(norm_name(nom))

        # identifiants uniques
        compteur = {}
        for outil in outils:
            base = outil["id"] or "outil"
            compteur[base] = compteur.get(base, 0) + 1
            if compteur[base] > 1:
                outil["id"] = f"{base}-{compteur[base]}"

        outils.sort(key=lambda o: (o["theme"], o["nom"].lower()))
        return outils

    os.makedirs(OUT, exist_ok=True)
    resume = {}
    for lang in ("fr", "en"):
        outils = construire(lang)
        charge = {
            "genere_le": aujourd_hui,
            "source": "Base MySQL historique + XLSX INR Boîte à outils NR v2.1 (avril 2024)",
            "outils": outils,
        }
        chemin = os.path.join(OUT, f"tools-{lang}.json")
        # Indenté et non échappé : ces fichiers sont la source de vérité, ils se
        # relisent et se modifient à la main. Le surcoût disparaît à la compression.
        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(charge, fichier, ensure_ascii=False, indent=1)
            fichier.write("\n")
        resume[lang] = (len(outils), os.path.getsize(chemin))

    def ecrire_csv(nom, entetes, lignes):
        chemin = os.path.join(HERE, nom)
        with open(chemin, "w", encoding="utf-8", newline="") as fichier:
            writer = csv.writer(fichier)
            writer.writerow(entetes)
            writer.writerows(lignes)
        return len(lignes)

    n_morts = ecrire_csv("rapport-liens-morts.csv",
                         ["langue", "outil", "categorie", "url", "statut"], morts)
    n_red = ecrire_csv("rapport-redirections.csv",
                       ["url_origine", "url_finale"], sorted(set(redirections)))
    n_recl = ecrire_csv("rapport-a-reclasser.csv",
                        ["langue", "outil", "categorie_base", "theme_deduit"], reclasser)

    print("Données générées :")
    for lang, (nombre, taille) in resume.items():
        print(f"  www/data/tools-{lang}.json : {nombre} outils, {taille / 1024:.0f} Ko")
    print("Rapports :")
    print(f"  rapport-liens-morts.csv   : {n_morts} liens retirés")
    print(f"  rapport-redirections.csv  : {n_red} URL réécrites")
    print(f"  rapport-a-reclasser.csv   : {n_recl} thèmes déduits, à valider")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Génère les pages statiques par thème, les données structurées et le sitemap.

Le moteur de recherche du site vit dans le navigateur : sans JavaScript, un robot
ne voit aucun outil. Ces pages donnent au catalogue une existence en HTML pur —
une page par thème, avec titre, description et liens réels — et servent d'entrées
de longue traîne pour la recherche.

    python3 tools/generer_pages.py
"""

import hashlib
import html
import json
import os
import posixpath
import re
import unicodedata
from datetime import date
from urllib.parse import urlparse

try:
    from translations import all_locales, published_locales
except ImportError:  # importé comme module depuis la racine du dépôt
    from tools.translations import all_locales, published_locales

HERE = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(HERE)
WWW = os.path.join(RACINE, "www")
DOMAINE = "https://sustainableit-tools.isit-europe.org"

LANGUES = {
    "fr": {
        "code": "fr",
        "dossier": "",
        "racine": "../",
        "dossier_theme": "themes",
        "titre_site": "Boîte à outils NR",
        "nav": [("../", "Outils"), ("../a-propos.html", "À propos"),
                ("https://institutnr.org", "Site de l'INR")],
        "autre_langue": ("../en/", "English", "en"),
        "intro": "{n} ressources du numérique responsable classées dans le thème « {theme} », "
                 "sélectionnées et vérifiées par l'Institut du Numérique Responsable.",
        "retour": "Filtrer tout le catalogue sur ce thème",
        "tous": "Tous les thèmes",
        "verifie": "Lien vérifié le",
        "doute": "Lien à revérifier",
        "gratuit": "Gratuit",
        "payant": "Payant",
        "sommaire_titre": "Le catalogue par thème",
        "sommaire_intro": "Chaque thème rassemble les ressources d'un même domaine du numérique "
                          "responsable. La recherche complète, avec tous les filtres, reste sur "
                          "la page d'accueil.",
        "ressources": "ressources",
        "dossier_outil": "outils",
        "acceder": "Accéder à la ressource",
        "site_officiel": "Site officiel",
        "a_propos_ressource": "À propos de cette ressource",
        "voisines": "Dans le même thème",
        "accueil": "Accueil",
        "champ": {"theme": "Thème", "type": "Type", "profil": "Public visé",
                  "cout": "Accès", "domaine": "Domaine technique",
                  "tags": "Mots-clés", "verif": "Lien vérifié le"},
    },
    "en": {
        "code": "en",
        "dossier": "en",
        "racine": "../../",
        "dossier_theme": "topics",
        "titre_site": "Sustainable IT Toolbox",
        "nav": [("../", "Tools"), ("../../a-propos.html", "About"),
                ("https://institutnr.org", "ISIT website")],
        "autre_langue": ("../../", "Français", "fr"),
        "intro": "{n} sustainable IT resources filed under « {theme} », selected and checked by "
                 "the Institute for Sustainable IT (ISIT).",
        "retour": "Filter the whole catalogue on this topic",
        "tous": "All topics",
        "verifie": "Link checked on",
        "doute": "Link needs rechecking",
        "gratuit": "Free",
        "payant": "Paid",
        "sommaire_titre": "The catalogue by topic",
        "sommaire_intro": "Each topic gathers the resources of one area of sustainable IT. The "
                          "full search, with every filter, stays on the home page.",
        "ressources": "resources",
        "dossier_outil": "tools",
        "acceder": "Open the resource",
        "site_officiel": "Official website",
        "a_propos_ressource": "About this resource",
        "voisines": "Same topic",
        "accueil": "Home",
        "champ": {"theme": "Topic", "type": "Type", "profil": "Audience",
                  "cout": "Access", "domaine": "Technical area",
                  "tags": "Keywords", "verif": "Link checked on"},
    },
}

for _code, _name, _folder, _topics in (
    ("nl", "Nederlands", "nl", "topics"),
    ("es", "Español", "es", "topics"),
    ("de", "Deutsch", "de", "topics"),
):
    LANGUES[_code] = {**LANGUES["en"], "code": _code, "published": False,
                      "dossier": _folder, "dossier_theme": _topics,
                      "dossier_outil": "tools", "titre_site": f"Sustainable IT Toolbox — {_name}"}

# Interface néerlandaise : le catalogue reste masqué jusqu'à validation éditoriale.
LANGUES["nl"].update({
    "titre_site": "Sustainable IT Toolbox",
    "nav": [("../", "Hulpmiddelen"), ("../../a-propos.html", "Over ons"),
            ("https://institutnr.org", "ISIT-website")],
    "autre_langue": ("../../", "Français", "fr"),
    "intro": "{n} hulpmiddelen voor duurzame IT binnen het thema « {theme} », geselecteerd en "
             "gecontroleerd door het Institute for Sustainable IT (ISIT).",
    "retour": "De volledige catalogus op dit thema filteren",
    "tous": "Alle thema's",
    "verifie": "Link gecontroleerd op",
    "doute": "Link opnieuw controleren",
    "gratuit": "Gratis",
    "payant": "Betaald",
    "sommaire_titre": "De catalogus per thema",
    "sommaire_intro": "Elk thema bundelt hulpmiddelen over één domein van duurzame IT.",
    "ressources": "hulpmiddelen",
    "acceder": "Naar de bron",
    "site_officiel": "Officiële website",
    "a_propos_ressource": "Over deze bron",
    "voisines": "Binnen hetzelfde thema",
    "accueil": "Home",
    "champ": {"theme": "Thema", "type": "Type", "profil": "Doelgroep",
              "cout": "Toegang", "domaine": "Technisch domein",
              "tags": "Trefwoorden", "verif": "Link gecontroleerd op"},
})
LANGUES["fr"]["published"] = True
LANGUES["en"]["published"] = True
LANGUES["nl"]["published"] = True


def selecteur_langues(lang, profondeur, page_url=None):
    """Liens de langue accessibles vers la fiche courante si elle existe."""
    liens = []
    equivalents = (ALTERNATES.get(page_url) or PAGE_ALTERNATES.get(page_url)
                   if page_url else None)
    page_path = posixpath.dirname(urlparse(page_url).path) if page_url else ""
    for locale in all_locales():
        code = locale["code"]
        conf = LANGUES[code]
        prefixe = conf["dossier"] + "/" if conf["dossier"] else ""
        cible = equivalents.get(code) if equivalents else None
        if cible and page_url:
            href = posixpath.relpath(urlparse(cible).path, start=page_path)
        else:
            href = profondeur + prefixe
        courant = ' aria-current="true"' if code == lang else ""
        if locale["published"]:
            liens.append(
                f'        <a href="{e(href)}" lang="{code}" hreflang="{code}"{courant}>'
                f'{e(locale["native_name"])}</a>'
            )
        else:
            suffixe = "bientôt" if lang == "fr" else "coming soon"
            liens.append(
                f'        <span class="entete__langue-indisponible" lang="{code}" '
                f'aria-disabled="true">{e(locale["native_name"])} <small>({suffixe})</small></span>'
            )
    etiquette = "Langues" if lang == "fr" else "Languages"
    return (f'      <div class="entete__langues" aria-label="{etiquette}">\n'
            + "\n".join(liens) + "\n      </div>")


def empreinte(chemin_relatif):
    """Huit caractères de hachage, ajoutés en paramètre d'URL.

    Le cache navigateur est réglé sur un an pour le CSS et le JS : sans cette
    empreinte, un visiteur garderait l'ancienne version pendant douze mois après
    une correction. Elle change à chaque modification du fichier, et seulement là.
    """
    chemin = os.path.join(WWW, chemin_relatif)
    with open(chemin, "rb") as fichier:
        return hashlib.sha256(fichier.read()).hexdigest()[:8]


VERSIONS = {}


def slug(valeur):
    valeur = unicodedata.normalize("NFKD", str(valeur))
    valeur = "".join(c for c in valeur if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "-", valeur).strip("-").lower()


def e(texte):
    return html.escape(str(texte or ""), quote=True)


def date_lisible(iso, lang):
    if lang == "en" or not iso or iso.count("-") != 2:
        return iso
    a, m, j = iso.split("-")
    return f"{j}/{m}/{a}"


def entete(lang, conf, titre, description, canonique, profondeur):
    """profondeur = préfixe relatif vers la racine du site."""
    nav = "\n".join(
        f'      <a href="{e(url)}"{" target=\"_blank\" rel=\"noopener\"" if url.startswith("http") else ""}>{e(libelle)}</a>'
        for url, libelle in conf["nav"]
    )
    logo = "logo-inr.svg" if lang == "fr" else "logo-isit.svg"
    logo_alt = ""
    nom_institut = ("Institut du Numérique Responsable" if lang == "fr"
                    else "Institute for Sustainable IT")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<link rel="canonical" href="{e(canonique)}">{liens_alternes(canonique)}
<link rel="icon" href="{profondeur}favicon.ico">
<link rel="stylesheet" href="{profondeur}assets/style.css?v={VERSIONS['css']}">
<meta property="og:title" content="{e(titre)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(canonique)}">
</head>
<body>

<a class="lien-evitement" href="#contenu">{"Aller au contenu" if lang == "fr" else "Skip to content"}</a>

<header class="entete">
  <div class="entete__inner">
    <a class="entete__marque" href="{profondeur}{conf['dossier'] + '/' if conf['dossier'] else ''}">
      <img class="entete__logo" src="{profondeur}assets/{logo}" alt="{logo_alt}" width="118" height="36" decoding="async">
      <span class="entete__titre">
        <span class="entete__sur-titre">{e(nom_institut)}</span>
        {e(conf['titre_site'])}
      </span>
    </a>
    <nav class="entete__nav" aria-label="{"Navigation principale" if lang == "fr" else "Main navigation"}">
{nav}
{selecteur_langues(lang, profondeur, canonique)}
    </nav>
  </div>
</header>
"""


def pied(lang, profondeur):
    if lang == "fr":
        corps = f"""      <p>
        Boîte à outils du Numérique Responsable, maintenue par l'
        <a href="https://institutnr.org" target="_blank" rel="noopener">Institut du Numérique Responsable</a>.
      </p>
    </div>
    <div>
      <p><a href="{profondeur}mentions-legales.html">Mentions légales</a> · <a href="{profondeur}a-propos.html">À propos</a> · <a href="{profondeur}themes/">Tous les thèmes</a></p>
      <p>Site statique. <a href="{profondeur}mentions-legales.html">Mesure d'audience sans cookie</a>.</p>"""
    else:
        corps = f"""      <p>
        Sustainable IT Toolbox, maintained by the
        <a href="https://institutnr.org" target="_blank" rel="noopener">Institute for Sustainable IT (ISIT)</a>.
      </p>
    </div>
    <div>
      <p><a href="{profondeur}mentions-legales.html" lang="fr" hreflang="fr">Legal notice</a> · <a href="{profondeur}en/topics/">All topics</a></p>
      <p>Static site. Cookieless analytics.</p>"""
    return f"""
<footer class="pied">
  <div class="pied__inner">
    <div>
{corps}
    </div>
  </div>
</footer>

<script src="{profondeur}assets/matomo.js?v={VERSIONS['matomo']}" defer></script>

</body>
</html>
"""


def carte_html(outil, conf, lang):
    """Une fiche, en HTML pur : c'est ce que voit un robot d'indexation."""
    morceaux = [f'      <p class="carte__theme">{e(outil["theme"])}</p>']

    # Le titre mène à la fiche interne : c'est elle qui donne à la ressource une
    # adresse citable, par un moteur comme par un modèle de langage.
    lien = (f'<a href="../{conf["dossier_outil"]}/{e(outil["id"])}.html">'
            f'{e(outil["nom"])}</a>')
    morceaux.append(f'      <h3 class="carte__titre">{lien}</h3>')

    if outil.get("description"):
        texte = outil["description"]
        if len(texte) > 260:
            texte = texte[:260].rsplit(" ", 1)[0] + "…"
        morceaux.append(f'      <p class="carte__desc">{e(texte)}</p>')

    etiquettes = []
    if outil.get("type"):
        etiquettes.append(f'<span class="etiquette">{e(outil["type"])}</span>')
    if outil.get("cout") in ("Gratuit", "Free"):
        etiquettes.append(f'<span class="etiquette etiquette--gratuit">{e(conf["gratuit"])}</span>')
    elif outil.get("cout") in ("Payant", "Paid"):
        etiquettes.append(f'<span class="etiquette etiquette--payant">{e(conf["payant"])}</span>')
    if outil.get("profil"):
        etiquettes.append(f'<span class="etiquette">{e(outil["profil"])}</span>')
    if etiquettes:
        morceaux.append('      <div class="carte__meta">' + "".join(etiquettes) + "</div>")

    if outil.get("lien_ok") != "interne":
        doute = outil.get("lien_ok") == "a-verifier"
        libelle = conf["doute"] if doute else f'{conf["verifie"]} {date_lisible(outil.get("verifie_le"), lang)}'
        classe = "verif verif--doute" if doute else "verif"
        morceaux.append(f'      <p class="{classe}">{e(libelle)}</p>')

    return '    <li class="carte">\n' + "\n".join(morceaux) + "\n    </li>"


def page_outil(outil, voisines, conf, lang, url_page, url_theme):
    """Une fiche par ressource : l'unité que Google indexe et qu'un modèle cite."""
    profondeur = conf["racine"]
    nom = outil["nom"]
    description = outil.get("description") or f"{nom} — ressource du numérique responsable."
    resume = description if len(description) <= 155 else description[:152].rsplit(" ", 1)[0] + "…"
    titre = f"{nom} — {outil['theme']} | {conf['titre_site']}"

    # --- fil d'Ariane, repris en données structurées plus bas ---------------
    accueil = f"{profondeur}{conf['dossier'] + '/' if conf['dossier'] else ''}"
    fil = (f'<p class="chapeau"><a href="{accueil}">{e(conf["accueil"])}</a> · '
           f'<a href="../{conf["dossier_theme"]}/{slug(outil["theme"])}.html">'
           f'{e(outil["theme"])}</a></p>')

    lignes = []
    for cle, libelle in (("theme", conf["champ"]["theme"]), ("type", conf["champ"]["type"]),
                         ("profil", conf["champ"]["profil"]), ("domaine", conf["champ"]["domaine"])):
        if outil.get(cle):
            valeur = outil[cle]
            if cle == "theme":
                valeur = (f'<a href="../{conf["dossier_theme"]}/{slug(valeur)}.html">'
                          f'{e(valeur)}</a>')
            else:
                valeur = e(valeur)
            lignes.append(f"      <tr><th scope=\"row\">{e(libelle)}</th><td>{valeur}</td></tr>")
    if outil.get("cout"):
        cout = conf["gratuit"] if outil["cout"] in ("Gratuit", "Free") else (
            conf["payant"] if outil["cout"] in ("Payant", "Paid") else outil["cout"])
        lignes.append(f'      <tr><th scope="row">{e(conf["champ"]["cout"])}</th>'
                      f"<td>{e(cout)}</td></tr>")
    if outil.get("tags"):
        jetons = ", ".join(e(t) for t in outil["tags"])
        lignes.append(f'      <tr><th scope="row">{e(conf["champ"]["tags"])}</th>'
                      f"<td>{jetons}</td></tr>")
    if outil.get("lien_ok") != "interne":
        etat = (conf["doute"] if outil.get("lien_ok") == "a-verifier"
                else date_lisible(outil.get("verifie_le"), lang))
        lignes.append(f'      <tr><th scope="row">{e(conf["champ"]["verif"])}</th>'
                      f"<td>{e(etat)}</td></tr>")

    if outil.get("url"):
        action = (f'  <p><a class="plus" style="display:inline-block;margin:0" '
                  f'href="{e(outil["url"])}" target="_blank" rel="noopener">'
                  f'{e(conf["acceder"])} →</a></p>\n'
                  f'  <p><small>{e(conf["site_officiel"])} : '
                  f'<a href="{e(outil["url"])}" target="_blank" rel="noopener">'
                  f'{e(outil["url"])}</a></small></p>')
    else:
        action = (f'  <p><a class="plus" style="display:inline-block;margin:0" '
                  f'href="{accueil}?fiche={e(outil["id"])}">'
                  f'{e(conf["acceder"])} →</a></p>')

    # --- contenu de la fiche juridique, s'il y en a un ----------------------
    loi = ""
    if outil.get("loi"):
        blocs = []
        for titre_bloc, valeur in (("Qui est concerné" if lang == "fr" else "Who is concerned",
                                    outil["loi"].get("concernes")),
                                   ("En vigueur depuis" if lang == "fr" else "In force since",
                                    outil["loi"].get("depuis"))):
            if valeur:
                blocs.append(f"  <h2>{e(titre_bloc)}</h2>\n  <p>{e(valeur)}</p>")
        if outil["loi"].get("contenu"):
            blocs.append("  <h2>" + ("Contenu de la loi" if lang == "fr" else "Content") + "</h2>")
            for partie in outil["loi"]["contenu"]:
                if partie.get("type") == "liste":
                    items = "".join(f"<li>{e(i)}</li>" for i in partie.get("items", []))
                    blocs.append(f"  <ul>{items}</ul>")
                else:
                    blocs.append(f'  <p>{e(partie.get("texte"))}</p>')
        if outil["loi"].get("sanctions"):
            blocs.append("  <h2>" + ("Sanctions" if lang == "fr" else "Penalties") + "</h2>\n"
                         f'  <p>{e(outil["loi"]["sanctions"])}</p>')
        loi = "\n" + "\n".join(blocs) + "\n"

    voisines_html = ""
    if voisines:
        elements = "\n".join(
            f'    <li><a href="{e(v["id"])}.html">{e(v["nom"])}</a></li>' for v in voisines)
        voisines_html = (f'\n  <h2>{e(conf["voisines"])}</h2>\n  <ul>\n{elements}\n  </ul>\n'
                         f'  <p><a href="../{conf["dossier_theme"]}/{slug(outil["theme"])}.html">'
                         f'{e(outil["theme"])} →</a></p>\n')

    page = entete(lang, conf, titre, resume, url_page, profondeur)
    page += jsonld_outil(outil, url_page, url_theme, conf, lang)
    page += f"""

<main class="page" id="contenu">
  {fil}
  <h1>{e(nom)}</h1>
  <p class="chapeau">{e(description)}</p>
{action}

  <h2>{e(conf['a_propos_ressource'])}</h2>
  <table>
    <tbody>
{chr(10).join(lignes)}
    </tbody>
  </table>
{loi}{voisines_html}</main>
"""
    return page + pied(lang, profondeur)


def jsonld_outil(outil, url_page, url_theme, conf, lang):
    type_schema = "SoftwareApplication" if outil.get("type") == "Outil" else "CreativeWork"
    fiche = {
        "@type": type_schema,
        "name": outil["nom"],
        "url": url_page,
        "inLanguage": lang,
        "applicationCategory": outil["theme"],
    }
    if outil.get("description"):
        fiche["description"] = outil["description"]
    if outil.get("url"):
        fiche["sameAs"] = outil["url"]
        fiche["installUrl" if type_schema == "SoftwareApplication" else "mainEntityOfPage"] = outil["url"]
    if outil.get("cout") in ("Gratuit", "Free"):
        fiche["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}
    if outil.get("tags"):
        fiche["keywords"] = ", ".join(outil["tags"])
    if outil.get("profil"):
        fiche["audience"] = {"@type": "Audience", "audienceType": outil["profil"]}

    nom_institut = ("Institut du Numérique Responsable" if lang == "fr"
                    else "Institute for Sustainable IT")
    donnees = {
        "@context": "https://schema.org",
        "@graph": [
            fiche,
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": conf["accueil"],
                     "item": DOMAINE + "/" + (conf["dossier"] + "/" if conf["dossier"] else "")},
                    {"@type": "ListItem", "position": 2, "name": outil["theme"],
                     "item": url_theme},
                    {"@type": "ListItem", "position": 3, "name": outil["nom"], "item": url_page},
                ],
            },
        ],
    }
    return ('<script type="application/ld+json">'
            + json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def jsonld_theme(theme, outils, url_page, lang):
    elements = []
    for rang, outil in enumerate(outils, 1):
        element = {
            "@type": "ListItem",
            "position": rang,
            "item": {
                "@type": "SoftwareApplication" if outil.get("type") == "Outil" else "CreativeWork",
                "name": outil["nom"],
                "applicationCategory": theme,
            },
        }
        if outil.get("description"):
            element["item"]["description"] = outil["description"][:300]
        if outil.get("url"):
            element["item"]["url"] = outil["url"]
        if outil.get("cout") in ("Gratuit", "Free"):
            element["item"]["offers"] = {"@type": "Offer", "price": "0",
                                         "priceCurrency": "EUR"}
        elements.append(element)

    nom_institut = ("Institut du Numérique Responsable" if lang == "fr"
                    else "Institute for Sustainable IT")
    donnees = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": theme,
        "url": url_page,
        "inLanguage": lang,
        "isPartOf": {"@type": "WebSite", "name": "Boîte à outils NR", "url": DOMAINE + "/"},
        "publisher": {"@type": "Organization", "name": nom_institut,
                      "url": "https://institutnr.org"},
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(outils),
                       "itemListElement": elements},
    }
    return ('<script type="application/ld+json">'
            + json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def jsonld_accueil(nombre, lang, url):
    nom_institut = ("Institut du Numérique Responsable" if lang == "fr"
                    else "Institute for Sustainable IT")
    donnees = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Boîte à outils du Numérique Responsable" if lang == "fr" else "Sustainable IT Toolbox",
        "url": url,
        "inLanguage": lang,
        "description": (f"{nombre} outils, guides et référentiels du numérique responsable, "
                        "sélectionnés et vérifiés par l'INR." if lang == "fr" else
                        f"{nombre} sustainable IT tools, guides and frameworks, curated and "
                        "checked by the ISIT."),
        "publisher": {"@type": "Organization", "name": nom_institut,
                      "url": "https://institutnr.org",
                        "logo": DOMAINE + "/assets/" + ("logo-inr.svg" if lang == "fr" else "logo-isit.svg")},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": url + "?q={search_term_string}"},
            "query-input": "required name=search_term_string",
        },
    }
    return ('<script type="application/ld+json">'
            + json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def injecter(chemin, marqueur, contenu):
    """Remplace le bloc entre <!-- marqueur --> et <!-- /marqueur -->."""
    with open(chemin, encoding="utf-8") as fichier:
        page = fichier.read()
    debut, fin = f"<!-- {marqueur} -->", f"<!-- /{marqueur} -->"
    bloc = f"{debut}\n{contenu}\n{fin}"
    if debut in page:
        page = re.sub(re.escape(debut) + r".*?" + re.escape(fin), lambda _: bloc, page, flags=re.S)
    else:
        page = page.replace("</head>", bloc + "\n</head>", 1)
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write(page)


ALTERNATES = {}
PAGE_ALTERNATES = {}

THEME_EQUIVALENTS = {
    "Accessibilité & inclusivité": "Accessibility & inclusion",
    "Conception web": "Web design",
    "DEEEE et Equipements": "WEEE & hardware",
    "Démarche pour les organisations / entreprises": "Organisational roadmap",
    "Gestion de l'énergie et des ressources": "Energy & resource management",
    "IA": "AI",
    "Innovation et recherche": "Innovation & research",
    "Juridique et réglementation": None,
    "Marketing et Communication": "Marketing & communication",
    "Respect de la vie privée, transparence et éthique": "Privacy, transparency & ethics",
    "Références et guides": "References & guides",
    "Sensibilisation et formation": "Awareness & training",
    "Sobriété de ses données": "Data sobriety",
    "Éco-conception (Web)": "Web eco-design",
    "Évaluation et mesure": "Measurement & assessment",
}


def construire_alternates():
    """Associe chaque ressource à son équivalent dans l'autre langue.

    Les deux catalogues n'ont ni les mêmes identifiants ni les mêmes intitulés :
    l'URL de la ressource est le seul point commun fiable. Sans cette table, les
    moteurs traitent les versions française et anglaise comme deux pages
    concurrentes au lieu de deux traductions.
    """
    par_url = {}
    for lang, conf in LANGUES.items():
        if not conf.get("published"):
            continue
        chemin = os.path.join(WWW, "data", f"tools-{lang}.json")
        with open(chemin, encoding="utf-8") as fichier:
            for outil in json.load(fichier)["outils"]:
                if not outil.get("url"):
                    continue
                cle = re.sub(r"^https?://(www\.)?", "", outil["url"].lower()).rstrip("/")
                par_url.setdefault(cle, {})[lang] = (
                    DOMAINE + "/" + (conf["dossier"] + "/" if conf["dossier"] else "")
                    + conf["dossier_outil"] + "/" + outil["id"] + ".html")
    for equivalents in par_url.values():
        if len(equivalents) < 2:
            continue
        for lang, adresse in equivalents.items():
            ALTERNATES[adresse] = equivalents
    for fr_theme, en_theme in THEME_EQUIVALENTS.items():
        if not en_theme:
            continue
        fr_url = f"{DOMAINE}/themes/{slug(fr_theme)}.html"
        en_url = f"{DOMAINE}/en/topics/{slug(en_theme)}.html"
        equivalents = {"fr": fr_url, "en": en_url}
        PAGE_ALTERNATES[fr_url] = equivalents
        PAGE_ALTERNATES[en_url] = equivalents
    PAGE_ALTERNATES[f"{DOMAINE}/themes/"] = {
        "fr": f"{DOMAINE}/themes/", "en": f"{DOMAINE}/en/topics/"
    }
    PAGE_ALTERNATES[f"{DOMAINE}/en/topics/"] = PAGE_ALTERNATES[f"{DOMAINE}/themes/"]
    print(f"{len(ALTERNATES) // 2} ressources présentes dans les deux langues")


def liens_alternes(url_page):
    """Balises hreflang, y compris x-default pointant sur le français."""
    equivalents = ALTERNATES.get(url_page) or PAGE_ALTERNATES.get(url_page)
    if not equivalents:
        return f'\n<link rel="alternate" hreflang="x-default" href="{DOMAINE}/langues/">'
    lignes = [f'<link rel="alternate" hreflang="{lang}" href="{e(adresse)}">'
              for lang, adresse in sorted(equivalents.items())]
    lignes.append(f'<link rel="alternate" hreflang="x-default" '
                  f'href="{DOMAINE}/langues/">')
    return "\n" + "\n".join(lignes)


def ecrire_llms():
    """llms.txt et llms-full.txt : le catalogue en texte, pour les modèles.

    Convention llmstxt.org : un résumé court et navigable à la racine, et une
    version complète pour l'ingestion. Un modèle qui cite la boîte à outils doit
    pouvoir en lire le contenu sans exécuter de JavaScript ni parcourir 348 pages.
    """
    with open(os.path.join(WWW, "data", "tools-fr.json"), encoding="utf-8") as fichier:
        outils = json.load(fichier)["outils"]

    themes = {}
    for outil in outils:
        themes.setdefault(outil["theme"], []).append(outil)

    lignes = [
        "# Boîte à outils du Numérique Responsable — Institut du Numérique Responsable (INR)",
        "",
        f"> Catalogue de {len(outils)} outils, guides, référentiels, formations et textes de loi "
        "du numérique responsable, sélectionnés par l'Institut du Numérique Responsable (INR / "
        "Institute for Sustainable IT). Chaque lien est testé périodiquement ; les ressources "
        "dont l'adresse ne répond plus sont retirées, et la date du dernier contrôle est publiée "
        "sur chaque fiche.",
        "",
        "L'INR est une association loi 1901 basée à La Rochelle, réseau européen d'instituts en "
        "France, Belgique et Suisse. Le catalogue couvre l'écoconception de services numériques, "
        "la mesure d'empreinte environnementale, l'accessibilité, la sobriété, l'impact de l'IA "
        "générative, le cadre juridique français et européen, et la sensibilisation.",
        "",
        "## Données",
        "",
        f"- [Catalogue complet, français (JSON)]({DOMAINE}/data/tools-fr.json) : "
        f"{len(outils)} ressources, champs nom, description, url, thème, type, public visé, "
        "coût, mots-clés, état du lien et date de vérification.",
        f"- [Catalogue complet, anglais (JSON)]({DOMAINE}/data/tools-en.json)",
        f"- [Version texte intégrale de ce catalogue]({DOMAINE}/llms-full.txt)",
        f"- [Version anglaise de ce document]({DOMAINE}/en/llms.txt)",
        "",
        "## Thèmes",
        "",
    ]
    for theme, liste in sorted(themes.items()):
        lignes.append(f"- [{theme}]({DOMAINE}/themes/{slug(theme)}.html) : "
                      f"{len(liste)} ressources")
    lignes += [
        "",
        "## Pages",
        "",
        f"- [Recherche et filtres]({DOMAINE}/) : moteur de recherche du catalogue",
        f"- [À propos]({DOMAINE}/a-propos.html) : méthode de sélection, vérification des liens",
        f"- [Mentions légales]({DOMAINE}/mentions-legales.html)",
        "",
        "## Conditions de citation",
        "",
        "Contenu réutilisable avec attribution à l'Institut du Numérique Responsable et lien "
        "vers la fiche concernée. L'INR n'est pas partie prenante des outils référencés et ne "
        "se porte pas garant de leur qualité pour un cas d'usage donné.",
        "",
    ]
    with open(os.path.join(WWW, "llms.txt"), "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(lignes))

    # --- version intégrale -------------------------------------------------
    complet = [
        "# Boîte à outils du Numérique Responsable — catalogue intégral",
        "",
        f"Source : {DOMAINE}/ — Institut du Numérique Responsable (INR).",
        f"Généré le {date.today().isoformat()}. {len(outils)} ressources.",
        "",
    ]
    for theme, liste in sorted(themes.items()):
        complet += [f"## {theme}", ""]
        for outil in sorted(liste, key=lambda o: o["nom"].lower()):
            complet.append(f"### {outil['nom']}")
            if outil.get("description"):
                complet.append(outil["description"])
            details = []
            if outil.get("url"):
                details.append(f"Site : {outil['url']}")
            details.append(f"Fiche : {DOMAINE}/outils/{outil['id']}.html")
            if outil.get("type"):
                details.append(f"Type : {outil['type']}")
            if outil.get("profil"):
                details.append(f"Public : {outil['profil']}")
            if outil.get("cout"):
                details.append(f"Accès : {outil['cout']}")
            if outil.get("tags"):
                details.append("Mots-clés : " + ", ".join(outil["tags"]))
            complet.append(" — ".join(details))
            complet.append("")
    with open(os.path.join(WWW, "llms-full.txt"), "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(complet))

    # --- version anglaise ---------------------------------------------------
    with open(os.path.join(WWW, "data", "tools-en.json"), encoding="utf-8") as fichier:
        outils_en = json.load(fichier)["outils"]
    themes_en = {}
    for outil in outils_en:
        themes_en.setdefault(outil["theme"], []).append(outil)

    anglais = [
        "# Sustainable IT Toolbox — Institute for Sustainable IT (ISIT)",
        "",
        f"> Catalogue of {len(outils_en)} tools, guides, frameworks and training resources for "
        "sustainable IT, curated by the Institute for Sustainable IT (ISIT). Every link is tested "
        "periodically; resources whose address no longer "
        "answers are removed, and the date of the last check is published on each entry.",
        "",
        "ISIT is a French non-profit based in La Rochelle, part of a European network of "
        "institutes across France, Belgium and Switzerland. The catalogue covers eco-design of "
        "digital services, environmental footprint measurement, accessibility, sobriety, the "
        "impact of generative AI, French and European regulation, and awareness raising.",
        "",
        "## Data",
        "",
        f"- [Full catalogue, English (JSON)]({DOMAINE}/data/tools-en.json): {len(outils_en)} "
        "resources with name, description, url, topic, type, audience, access, keywords, link "
        "status and check date.",
        f"- [Full catalogue, French (JSON)]({DOMAINE}/data/tools-fr.json)",
        f"- [Plain-text version of this catalogue]({DOMAINE}/en/llms-full.txt)",
        "",
        "## Topics",
        "",
    ]
    for theme, liste in sorted(themes_en.items()):
        anglais.append(f"- [{theme}]({DOMAINE}/en/topics/{slug(theme)}.html): "
                       f"{len(liste)} resources")
    anglais += [
        "",
        "## Pages",
        "",
        f"- [Search and filters]({DOMAINE}/en/): catalogue search engine",
        f"- [About]({DOMAINE}/a-propos.html) (French): selection method, link checking",
        "",
        "## Citation terms",
        "",
        "Content may be reused with attribution to the Institute for Sustainable IT (ISIT) and a "
        "link to the entry concerned. The INR is not a party to the tools listed and does not "
        "vouch for their fitness for any given use case.",
        "",
    ]
    dossier_en = os.path.join(WWW, "en")
    with open(os.path.join(dossier_en, "llms.txt"), "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(anglais))

    complet_en = [
        "# Sustainable IT Toolbox — full catalogue",
        "",
        f"Source: {DOMAINE}/en/ — Institute for Sustainable IT (ISIT).",
        f"Generated on {date.today().isoformat()}. {len(outils_en)} resources.",
        "",
    ]
    for theme, liste in sorted(themes_en.items()):
        complet_en += [f"## {theme}", ""]
        for outil in sorted(liste, key=lambda o: o["nom"].lower()):
            complet_en.append(f"### {outil['nom']}")
            if outil.get("description"):
                complet_en.append(outil["description"])
            details = []
            if outil.get("url"):
                details.append(f"Website: {outil['url']}")
            details.append(f"Entry: {DOMAINE}/en/tools/{outil['id']}.html")
            for cle, libelle in (("type", "Type"), ("profil", "Audience"), ("cout", "Access")):
                if outil.get(cle):
                    details.append(f"{libelle}: {outil[cle]}")
            if outil.get("tags"):
                details.append("Keywords: " + ", ".join(outil["tags"]))
            complet_en.append(" — ".join(details))
            complet_en.append("")
    with open(os.path.join(dossier_en, "llms-full.txt"), "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(complet_en))

    print(f"llms.txt : {len(outils)} ressources FR, {len(outils_en)} EN")


def ecrire_robots():
    """robots.txt. Les robots d'IA sont explicitement autorisés : l'objet de ce
    site est d'être cité. À inverser si l'INR change de position."""
    robots = f"""User-agent: *
Allow: /

# Robots des assistants conversationnels : autorisés volontairement, pour que la
# boîte à outils soit citée avec sa source plutôt que paraphrasée sans attribution.
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Bingbot
Allow: /

User-agent: MistralAI-User
Allow: /

User-agent: CCBot
Allow: /

Sitemap: {DOMAINE}/sitemap.xml
"""
    with open(os.path.join(WWW, "robots.txt"), "w", encoding="utf-8") as fichier:
        fichier.write(robots)


def elaguer(dossier, attendus):
    """Supprime les pages qui ne correspondent plus à aucune donnée.

    Sans cela, une ressource retirée du catalogue garde sa page en ligne :
    invisible dans le sitemap, mais toujours servie et indexable — et c'est
    précisément le cas des domaines détournés qu'on vient d'écarter.
    """
    if not os.path.isdir(dossier):
        return []
    supprimes = []
    for fichier in os.listdir(dossier):
        if not fichier.endswith(".html") or fichier == "index.html":
            continue
        if fichier[:-5] not in attendus:
            os.remove(os.path.join(dossier, fichier))
            supprimes.append(fichier)
    return supprimes


def versionner_pages_statiques():
    """Applique la même empreinte aux pages écrites à la main."""
    pages = ["index.html", "a-propos.html", "mentions-legales.html", "404.html",
             os.path.join("en", "index.html")]
    for page in pages:
        chemin = os.path.join(WWW, page)
        if not os.path.exists(chemin):
            continue
        with open(chemin, encoding="utf-8") as fichier:
            contenu = fichier.read()
        for fichier_asset, cle in (("style.css", "css"), ("app.js", "app"),
                                   ("matomo.js", "matomo")):
            contenu = re.sub(
                r'(assets/' + re.escape(fichier_asset) + r')(\?v=[0-9a-f]+)?',
                r"\1?v=" + VERSIONS[cle], contenu)
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write(contenu)
    print(f"assets versionnés : css={VERSIONS['css']} app={VERSIONS['app']} "
          f"matomo={VERSIONS['matomo']}")


def ecrire_selecteur_langues():
    """Page x-default explicite pour les visiteurs sans langue publiée."""
    dossier = os.path.join(WWW, "langues")
    os.makedirs(dossier, exist_ok=True)
    url = DOMAINE + "/langues/"
    page = entete("fr", LANGUES["fr"], "Choisir la langue | Boîte à outils NR",
                  "Choisissez la langue de la boîte à outils du Numérique Responsable.",
                  url, "../")
    options = []
    for locale in all_locales():
        code = locale["code"]
        if locale["published"]:
            conf = LANGUES[code]
            href = "../" + (conf["dossier"] + "/" if conf["dossier"] else "")
            options.append(f'    <li><a href="{href}" lang="{code}" hreflang="{code}">{e(locale["native_name"])}</a></li>')
        else:
            options.append(f'    <li><span class="entete__langue-indisponible" lang="{code}" aria-disabled="true">{e(locale["native_name"])} <small>(bientôt)</small></span></li>')
    page += "\n<main class=\"page\" id=\"contenu\">\n  <h1>Choisir la langue</h1>\n  <p class=\"chapeau\">Accédez à la version disponible de la boîte à outils.</p>\n  <ul>\n" + "\n".join(options) + "\n  </ul>\n</main>\n"
    page += pied("fr", "../")
    with open(os.path.join(dossier, "index.html"), "w", encoding="utf-8") as sortie:
        sortie.write(page)


def main():
    aujourd_hui = date.today().isoformat()
    construire_alternates()
    VERSIONS["css"] = empreinte(os.path.join("assets", "style.css"))
    VERSIONS["app"] = empreinte(os.path.join("assets", "app.js"))
    VERSIONS["matomo"] = empreinte(os.path.join("assets", "matomo.js"))
    urls_sitemap = []

    for lang, conf in LANGUES.items():
        if not conf.get("published"):
            continue
        chemin_donnees = os.path.join(WWW, "data", f"tools-{lang}.json")
        with open(chemin_donnees, encoding="utf-8") as fichier:
            outils = json.load(fichier)["outils"]

        base = os.path.join(WWW, conf["dossier"]) if conf["dossier"] else WWW
        dossier = os.path.join(base, conf["dossier_theme"])
        os.makedirs(dossier, exist_ok=True)

        # ---- données structurées et lien « tous les thèmes » sur l'accueil ---
        url_accueil = DOMAINE + "/" + (conf["dossier"] + "/" if conf["dossier"] else "")
        urls_sitemap.append((url_accueil, "1.0"))
        injecter(os.path.join(base, "index.html"), "donnees-structurees",
                 jsonld_accueil(len(outils), lang, url_accueil))

        # ---- une page par thème ---------------------------------------------
        themes = {}
        for outil in outils:
            themes.setdefault(outil["theme"], []).append(outil)

        profondeur = conf["racine"]
        for theme, liste in sorted(themes.items()):
            liste.sort(key=lambda o: o["nom"].lower())
            fichier_theme = slug(theme) + ".html"
            url_page = f"{url_accueil}{conf['dossier_theme']}/{fichier_theme}"

            titre = f"{theme} — {len(liste)} {conf['ressources']} | {conf['titre_site']}"
            description = conf["intro"].format(n=len(liste), theme=theme)

            cartes = "\n".join(carte_html(o, conf, lang) for o in liste)
            filtre = f"../?theme={html.escape(theme, quote=True).replace(' ', '%20')}"

            page = entete(lang, conf, titre, description, url_page, profondeur)
            page += f"""{jsonld_theme(theme, liste, url_page, lang)}

<main class="page" id="contenu" style="max-width:78rem">
  <p class="chapeau"><a href="./">{e(conf['tous'])}</a></p>
  <h1>{e(theme)}</h1>
  <p class="chapeau">{e(description)}</p>
  <p><a href="{filtre}">{e(conf['retour'])}</a></p>

  <ul class="grille">
{cartes}
  </ul>
</main>
"""
            page += pied(lang, profondeur)
            with open(os.path.join(dossier, fichier_theme), "w", encoding="utf-8") as sortie:
                sortie.write(page)
            urls_sitemap.append((url_page, "0.7"))

        # ---- une page par ressource -----------------------------------------
        dossier_outils = os.path.join(base, conf["dossier_outil"])
        os.makedirs(dossier_outils, exist_ok=True)
        for theme, liste in themes.items():
            url_theme = f"{url_accueil}{conf['dossier_theme']}/{slug(theme)}.html"
            for position, outil in enumerate(liste):
                voisines = [v for v in liste if v["id"] != outil["id"]]
                voisines = voisines[position:position + 5] or voisines[:5]
                url_page = f"{url_accueil}{conf['dossier_outil']}/{outil['id']}.html"
                page = page_outil(outil, voisines, conf, lang, url_page, url_theme)
                chemin_page = os.path.join(dossier_outils, f"{outil['id']}.html")
                with open(chemin_page, "w", encoding="utf-8") as sortie:
                    sortie.write(page)
                urls_sitemap.append((url_page, "0.6"))
        elagues = elaguer(dossier_outils, {o["id"] for o in outils})
        if elagues:
            print(f"[{lang}] {len(elagues)} fiche(s) obsolète(s) supprimée(s) : "
                  + ", ".join(sorted(elagues)))
        print(f"[{lang}] {len(outils)} fiches → {dossier_outils}")

        # ---- sommaire des thèmes --------------------------------------------
        url_sommaire = f"{url_accueil}{conf['dossier_theme']}/"
        lignes = "\n".join(
            f'    <li><a href="{slug(t)}.html">{e(t)}</a> — {len(l)} {conf["ressources"]}</li>'
            for t, l in sorted(themes.items())
        )
        sommaire = entete(lang, conf, f"{conf['sommaire_titre']} | {conf['titre_site']}",
                          conf["sommaire_intro"], url_sommaire, profondeur)
        sommaire += f"""
<main class="page" id="contenu">
  <h1>{e(conf['sommaire_titre'])}</h1>
  <p class="chapeau">{e(conf['sommaire_intro'])}</p>
  <ul>
{lignes}
  </ul>
</main>
"""
        sommaire += pied(lang, profondeur)
        with open(os.path.join(dossier, "index.html"), "w", encoding="utf-8") as sortie:
            sortie.write(sommaire)
        urls_sitemap.append((url_sommaire, "0.6"))

        elagues = elaguer(dossier, {slug(t) for t in themes})
        if elagues:
            print(f"[{lang}] {len(elagues)} page(s) de thème obsolète(s) supprimée(s) : "
                  + ", ".join(sorted(elagues)))
        print(f"[{lang}] {len(themes)} pages de thème + sommaire → {dossier}")

    versionner_pages_statiques()
    ecrire_selecteur_langues()

    # ---- llms.txt : point d'entrée pour les modèles de langage --------------
    ecrire_llms()

    # ---- robots.txt ---------------------------------------------------------
    ecrire_robots()

    # ---- sitemap ------------------------------------------------------------
    fixes = [(DOMAINE + "/", "1.0"), (DOMAINE + "/en/", "0.8"),
             (DOMAINE + "/langues/", "0.4"),
             (DOMAINE + "/a-propos.html", "0.5"),
             (DOMAINE + "/mentions-legales.html", "0.3")]
    lignes = []
    for url, priorite in fixes + sorted(urls_sitemap):
        lignes.append(f"  <url>\n    <loc>{url}</loc>\n"
                      f"    <lastmod>{aujourd_hui}</lastmod>\n"
                      f"    <changefreq>monthly</changefreq>\n"
                      f"    <priority>{priorite}</priority>\n  </url>")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(lignes) + "\n</urlset>\n")
    with open(os.path.join(WWW, "sitemap.xml"), "w", encoding="utf-8") as fichier:
        fichier.write(sitemap)
    print(f"sitemap.xml : {len(fixes) + len(urls_sitemap)} URL")


if __name__ == "__main__":
    main()

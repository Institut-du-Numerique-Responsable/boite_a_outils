#!/usr/bin/env python3
"""Ajoute des ressources au catalogue, avec contrôle avant écriture.

Les ressources à ajouter sont décrites dans NOUVELLES ci-dessous. Le script
refuse les doublons (même URL ou même nom), teste chaque lien, génère un
identifiant unique, et réinsère le tout dans l'ordre alphabétique par thème.

    python3 tools/ajouter_ressources.py            # aperçu
    python3 tools/ajouter_ressources.py --ecrire   # applique
"""

import json
import os
import re
import ssl
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "www", "data")
CTX = ssl.create_default_context()
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

LANGUE = "fr"

NOUVELLES = [
    # --- Boîte à outils Numérique responsable de l'ANCT (Les Bases) ---------
    {
        "nom": "Introduction à la démarche Numérique responsable (ANCT)",
        "description": "Point d'entrée de la boîte à outils Numérique responsable de l'ANCT : "
                       "présentation des différentes versions du pas à pas méthodologique et "
                       "aide au choix de celle qui correspond à la taille et à la maturité de "
                       "la collectivité.",
        "url": "https://lesbases.anct.gouv.fr/ressources/introduction-a-la-demarche-numerique-responsable",
        "theme": "Démarche pour les organisations / entreprises",
        "type": "Documentation",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Collectivités", "Démarche", "Secteur public"],
    },
    {
        "nom": "Démarche Numérique responsable (ANCT)",
        "description": "Pas à pas méthodologique de l'ANCT pour construire la stratégie numérique "
                       "responsable d'une collectivité de plus de 3 500 habitants disposant de sa "
                       "propre direction du numérique : étapes, livrables et points de vigilance.",
        "url": "https://lesbases.anct.gouv.fr/ressources/demarche-numerique-responsable",
        "theme": "Démarche pour les organisations / entreprises",
        "type": "Guide / Référentiel",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Collectivités", "Démarche", "Secteur public", "Stratégie"],
    },
    {
        "nom": "Démarche Numérique responsable flash (ANCT)",
        "description": "Version allégée du pas à pas de l'ANCT, destinée aux collectivités de moins "
                       "de 3 500 habitants qui n'ont pas de direction du numérique dédiée : mêmes "
                       "étapes, effort réduit.",
        "url": "https://lesbases.anct.gouv.fr/ressources/demarche-numerique-responsable-flash",
        "theme": "Démarche pour les organisations / entreprises",
        "type": "Guide / Référentiel",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Collectivités", "Démarche", "Secteur public"],
    },
    {
        "nom": "Proposer un accompagnement Numérique responsable (ANCT)",
        "description": "Guide de l'ANCT à destination des structures mutualisatrices — syndicats "
                       "mixtes et opérateurs de territoire — qui souhaitent accompagner plusieurs "
                       "collectivités dans leur démarche numérique responsable.",
        "url": "https://lesbases.anct.gouv.fr/ressources/proposer-un-accompagnement-numerique-responsable",
        "theme": "Démarche pour les organisations / entreprises",
        "type": "Guide / Référentiel",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Collectivités", "Démarche", "Secteur public"],
    },
    {
        "nom": "Kit NR — Passer de l'échelle de l'administration à celle du territoire (ANCT)",
        "description": "Kit de l'ANCT pour élargir une démarche numérique responsable menée en "
                       "interne à l'ensemble d'un territoire : acteurs à mobiliser, leviers et "
                       "supports prêts à l'emploi.",
        "url": "https://lesbases.anct.gouv.fr/ressources/kit-nr-passer-de-l-echelle-de-l-administration-a-celle-du-territoire",
        "theme": "Démarche pour les organisations / entreprises",
        "type": "Guide / Référentiel",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Collectivités", "Démarche", "Secteur public"],
    },
    {
        "nom": "Kit NR — Communiquer autour de sa démarche Numérique responsable (ANCT)",
        "description": "Kit de communication de l'ANCT pour les collectivités qui veulent faire "
                       "connaître leur démarche numérique responsable, en interne comme auprès "
                       "des habitants, sans tomber dans le greenwashing.",
        "url": "https://lesbases.anct.gouv.fr/ressources/kit-nr-communiquer-autour-de-sa-demarche-numerique-responsable",
        "theme": "Marketing et Communication",
        "type": "Guide / Référentiel",
        "profil": "Créateur contenu/Intermédiaire",
        "cout": "Gratuit",
        "tags": ["Collectivités", "Communication", "Secteur public"],
    },
    # --- Mesure d'impact de l'IA générative ---------------------------------
    {
        "nom": "EcoLogits",
        "description": "Bibliothèque Python open source qui estime la consommation d'énergie et "
                       "l'empreinte environnementale des appels aux modèles d'IA générative "
                       "(OpenAI, Anthropic, Mistral, Google, Hugging Face…). S'ajoute au code "
                       "existant et rend les impacts visibles à chaque requête, texte, image ou "
                       "vidéo. Projet porté par GenAI Impact.",
        "url": "https://ecologits.ai/latest/",
        "theme": "IA",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["IA", "Mesure", "Empreinte Carbone", "Open Source"],
    },
    # --- Analyse de code orientée performance et carbone --------------------
    {
        "nom": "perf-sentinel",
        "description": "Analyseur open source qui détecte les anti-patterns de performance dans "
                       "plusieurs langages et leur associe un score tenant compte du carbone. "
                       "Écrit en Rust, sous licence AGPL-3.0, il s'intègre à la chaîne de "
                       "développement pour traiter la sobriété logicielle comme un défaut de "
                       "qualité ordinaire.",
        "url": "https://github.com/robintra/perf-sentinel",
        "theme": "Évaluation et mesure",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Mesure", "Open Source", "Qualité logicielle", "Empreinte Carbone"],
    },
    {
        "nom": "PerfSentinelHub",
        "description": "Service compagnon de perf-sentinel : il centralise les résultats de "
                       "plusieurs instances et les expose aux extensions d'IDE via un point "
                       "d'accès unique, avec conservation par défaut de 180 jours. Projet en "
                       "version antérieure à la 1.0, sans publication stable à ce jour.",
        "url": "https://github.com/robintra/PerfSentinelHub",
        "theme": "Évaluation et mesure",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Mesure", "Open Source", "Qualité logicielle"],
    },
    {
        "nom": "claude-carbon",
        "description": "Extension open source qui affiche l'empreinte carbone d'une session "
                       "Claude Code directement dans la barre d'état du terminal : coût, "
                       "consommation du quota et grammes de CO₂ émis, mis à jour en continu. "
                       "Rend visible l'impact d'un usage quotidien de l'IA générative au moment "
                       "même où il est produit. Licence MIT.",
        "url": "https://github.com/gwittebolle/claude-carbon",
        "theme": "IA",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["IA", "Mesure", "Empreinte Carbone", "Open Source"],
    },
    {
        "nom": "Impact'IA (SNCF)",
        "description": "Calculateur d'empreinte environnementale des grands modèles de langage, "
                       "accompagné d'un document de méthodologie détaillé. Couvre 30 modèles "
                       "d'IA générative de Google, Anthropic, OpenAI et Mistral, et restitue "
                       "émissions de gaz à effet de serre, consommation d'eau et d'électricité "
                       "par token, avec une vue cycle de vie et des bonnes pratiques de "
                       "réduction. Fruit d'un an de travail conjoint SNCF, Resilio et Wavestone.",
        "url": "https://github.com/SNCFdevelopers/ImpactIA",
        "theme": "IA",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["IA", "Mesure", "Empreinte Carbone", "ACV", "Open Source"],
    },
    # --- Sobriété des documents bureautiques --------------------------------
    {
        "nom": "oPPTimiz",
        "description": "Extension PowerPoint développée par le groupe EDF qui réduit le poids "
                       "des présentations en compressant les images et en supprimant les masques "
                       "de diapositives inutilisés. Ajoute un groupe « Numérique responsable » au "
                       "ruban, avec un raccourci vers le vérificateur d'accessibilité de "
                       "Microsoft. Fonctionne aussi en ligne de commande et depuis l'explorateur "
                       "Windows. Licence GPL-3.0.",
        "url": "https://github.com/groupe-edf/oPPTimiz",
        "theme": "Sobriété de ses données",
        "type": "Outil",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Outils Bureautique", "Open Source", "Sobriété"],
    },
    # --- Dispositifs portés par l'INR / ISIT --------------------------------
    {
        "nom": "Charte Numérique Responsable",
        "description": "Charte d'engagement de l'Institut du Numérique Responsable : quinze "
                       "principes qu'une organisation signe pour structurer sa démarche "
                       "numérique responsable, de la sobriété des équipements à l'inclusion "
                       "numérique. Point de départ avant le label NR.",
        "url": "https://charter.isit-europe.org/?lang=fr_FR",
        "theme": "Démarche pour les organisations / entreprises",
        "type": "Guide / Référentiel",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Démarche", "Engagement", "INR"],
    },
    {
        "nom": "Digital Cleanup Day",
        "description": "Journée mondiale du nettoyage numérique : ressources, kits d'animation "
                       "et supports pour organiser un événement de tri des données dans une "
                       "organisation ou un établissement scolaire. Porte d'entrée concrète vers "
                       "la sobriété des données.",
        "url": "https://digital-cleanup-day.fr/",
        "theme": "Sobriété de ses données",
        "type": "Animation et Atelier",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Sensibilisation", "Sobriété", "Data"],
    },
    # --- MOOC de l'Académie NR (mis à jour en 2026) -------------------------
    {
        "nom": "MOOC Sensibilisation au Numérique Responsable (Académie NR)",
        "description": "Première approche en 30 minutes des enjeux environnementaux, sociaux et "
                       "éthiques du numérique. Format court conçu pour être diffusé largement "
                       "dans une organisation. Gratuit, proposé par l'Académie NR de l'INR.",
        "url": "https://www.academie-nr.org/mooc-sensibilisation/fr/index.html",
        "theme": "Sensibilisation et formation",
        "type": "MOOC",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Formation", "Sensibilisation", "INR"],
    },
    {
        "nom": "MOOC Numérique Responsable — formation complète (Académie NR)",
        "description": "Onze modules pour maîtriser les fondamentaux du numérique responsable : "
                       "impacts environnementaux, sociaux, économiques et géopolitiques, puis "
                       "solutions concrètes. Le parcours de référence de l'Académie NR.",
        "url": "https://www.academie-nr.org/mooc-nr/fr/index.html",
        "theme": "Sensibilisation et formation",
        "type": "MOOC",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Formation", "Sensibilisation", "INR"],
    },
    {
        "nom": "MOOC Conception responsable d'un service numérique (Académie NR)",
        "description": "Dix modules vidéo pour acquérir les premières clés de la conception "
                       "responsable : démarche, outils, référentiels et mise en pratique "
                       "professionnelle. Destiné aux équipes qui conçoivent des services "
                       "numériques.",
        "url": "https://www.academie-nr.org/mooc-conception/fr/index.html",
        "theme": "Éco-conception (Web)",
        "type": "MOOC",
        "profil": "Créateur contenu/Intermédiaire",
        "cout": "Gratuit",
        "tags": ["Formation", "Éco-conception", "INR"],
    },
    {
        "nom": "MOOC IA Responsable (Académie NR)",
        "description": "Formation d'une heure sur les enjeux éthiques, environnementaux et de "
                       "gouvernance de l'intelligence artificielle. Proposée par l'Académie NR "
                       "de l'INR.",
        "url": "https://www.academie-nr.org/mooc-ia/fr/index.html",
        "theme": "IA",
        "type": "MOOC",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Formation", "IA", "INR"],
    },
    # --- Référentiels d'écoconception --------------------------------------
    {
        "nom": "RGESN — Référentiel général de l'écoconception des services numériques",
        "description": "Référentiel de référence en France pour l'écoconception des services "
                       "numériques, version 2024 portée par l'Arcep avec l'ADEME, l'Arcom, la "
                       "DINUM, la CNIL et l'Inria. Structuré en critères vérifiables couvrant "
                       "stratégie, spécifications, architecture, contenus, front-end, back-end "
                       "et hébergement. Sert de base aux déclarations d'écoconception.",
        "url": "https://www.arcep.fr/mes-demarches-et-services/entreprises/fiches-pratiques/referentiel-general-ecoconception-services-numeriques.html",
        "theme": "Éco-conception (Web)",
        "type": "Guide / Référentiel",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Référentiel", "Éco-conception", "Réglementation"],
    },
    {
        "nom": "Web Sustainability Guidelines (W3C)",
        "description": "Lignes directrices du W3C pour la conception durable du web, sur le "
                       "modèle des WCAG pour l'accessibilité. Couvre l'interface, le contenu, "
                       "le développement, l'hébergement et la gestion de projet, avec des "
                       "critères de succès et des tests associés.",
        "url": "https://w3c-cg.github.io/sustyweb/",
        "theme": "Éco-conception (Web)",
        "type": "Guide / Référentiel",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Référentiel", "Éco-conception", "Web", "W3C"],
    },
    {
        "nom": "Sustainable Web Design",
        "description": "Modèle de calcul de l'empreinte carbone d'une page web devenu une "
                       "référence du secteur, accompagné de principes de conception durable. "
                       "C'est la méthodologie qui sous-tend la plupart des calculateurs "
                       "d'empreinte web du marché.",
        "url": "https://sustainablewebdesign.org/",
        "theme": "Éco-conception (Web)",
        "type": "Guide / Référentiel",
        "profil": "Créateur contenu/Intermédiaire",
        "cout": "Gratuit",
        "tags": ["Référentiel", "Éco-conception", "Web", "Empreinte Carbone"],
    },
    # --- Données et facteurs d'impact ---------------------------------------
    {
        "nom": "Base Empreinte (ADEME)",
        "description": "Base de données publique de l'ADEME rassemblant les facteurs d'émission "
                       "et les données d'analyse de cycle de vie utilisables pour un bilan "
                       "carbone. Source officielle française pour convertir une consommation en "
                       "équivalent CO₂.",
        "url": "https://base-empreinte.ademe.fr/",
        "theme": "Évaluation et mesure",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["ACV", "Empreinte Carbone", "Data", "Référentiel"],
    },
    {
        "nom": "BoaviztAPI",
        "description": "API open source de Boavizta qui restitue les impacts environnementaux "
                       "multicritères des équipements et services cloud — fabrication comprise, "
                       "pas seulement l'usage. S'intègre dans un outil de mesure maison ou une "
                       "chaîne d'intégration continue.",
        "url": "https://doc.api.boavizta.org/",
        "theme": "Évaluation et mesure",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["ACV", "Mesure", "Cloud", "Open Source"],
    },
    {
        "nom": "Datavizta (Boavizta)",
        "description": "Interface de visualisation des données d'impact de Boavizta : comparer "
                       "l'empreinte de serveurs, terminaux et instances cloud sans écrire une "
                       "ligne de code. Utile pour arbitrer un choix d'équipement ou "
                       "d'hébergement.",
        "url": "https://dataviz.boavizta.org/",
        "theme": "Évaluation et mesure",
        "type": "Outil",
        "profil": "Créateur contenu/Intermédiaire",
        "cout": "Gratuit",
        "tags": ["ACV", "Mesure", "Cloud", "Open Source"],
    },
    {
        "nom": "CO2.js (Green Web Foundation)",
        "description": "Bibliothèque JavaScript qui convertit un volume de données transférées "
                       "en émissions de CO₂, avec le choix du modèle de calcul et la prise en "
                       "compte de l'intensité carbone du réseau électrique. Permet d'afficher "
                       "l'empreinte d'une page directement dans l'application.",
        "url": "https://developers.thegreenwebfoundation.org/co2js/overview/",
        "theme": "Évaluation et mesure",
        "domaine": "Front-end",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Mesure", "Web", "Empreinte Carbone", "Open Source"],
    },
    # --- Mesure d'énergie côté infrastructure -------------------------------
    {
        "nom": "Kepler (CNCF)",
        "description": "Exportateur Prometheus qui estime la consommation énergétique des pods "
                       "Kubernetes à partir des compteurs matériels et de l'eBPF. Projet de la "
                       "Cloud Native Computing Foundation, pour attribuer une consommation à "
                       "chaque charge de travail conteneurisée.",
        "url": "https://github.com/sustainable-computing-io/kepler",
        "theme": "Gestion de l'énergie et des ressources",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Mesure", "Energie", "Cloud", "Open Source"],
    },
    {
        "nom": "Scaphandre (Hubblo)",
        "description": "Agent de métrologie énergétique open source, écrit en Rust, qui mesure "
                       "la consommation électrique d'une machine et l'attribue processus par "
                       "processus. Fonctionne sur serveur physique comme en machine virtuelle, "
                       "et s'expose à Prometheus.",
        "url": "https://github.com/hubblo-org/scaphandre",
        "theme": "Gestion de l'énergie et des ressources",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Mesure", "Energie", "Open Source"],
    },
    {
        "nom": "Carbon Aware SDK (Green Software Foundation)",
        "description": "Kit de développement qui permet à une application de décaler ses "
                       "traitements vers les moments ou les régions où l'électricité est la "
                       "moins carbonée. Passe de la mesure à l'action, sans changer "
                       "l'architecture applicative.",
        "url": "https://github.com/Green-Software-Foundation/carbon-aware-sdk",
        "theme": "Gestion de l'énergie et des ressources",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Energie", "Cloud", "Open Source"],
    },
    # --- Qualité et performance des services numériques ---------------------
    {
        "nom": "Beacon (Digital Beacon)",
        "description": "Calculateur en ligne de l'empreinte carbone d'une page web, avec un "
                       "rapport détaillant les ressources les plus lourdes et des pistes de "
                       "correction. Analyse gratuite depuis une simple URL.",
        "url": "https://digitalbeacon.co/",
        "theme": "Évaluation et mesure",
        "domaine": "Front-end",
        "type": "Outil",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Mesure", "Web", "Empreinte Carbone"],
    },
    {
        "nom": "EcoSonar",
        "description": "Extension SonarQube qui ajoute l'écoconception et l'accessibilité aux "
                       "analyses de qualité de code déjà en place : EcoIndex, Lighthouse et "
                       "règles vertes remontent dans le même tableau de bord que la dette "
                       "technique. Portée par la Green Code Initiative.",
        "url": "https://github.com/green-code-initiative/EcoSonar",
        "theme": "Évaluation et mesure",
        "domaine": "Back-End",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Mesure", "Qualité logicielle", "Éco-conception", "Open Source"],
    },
    {
        "nom": "Firefox Profiler",
        "description": "Profileur intégré à Firefox qui expose le temps processeur, la mémoire "
                       "et l'énergie consommée par une page. Outil de diagnostic gratuit pour "
                       "identifier ce qui, dans un service, coûte réellement des ressources.",
        "url": "https://profiler.firefox.com/",
        "theme": "Évaluation et mesure",
        "domaine": "Front-end",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Gratuit",
        "tags": ["Mesure", "Energie", "Web", "Open Source"],
    },
    # --- Services --------------------------------------------------------
    {
        "nom": "Verdikt",
        "description": "Plateforme commerciale de mesure et de pilotage de l'empreinte "
                       "environnementale d'un système d'information, du parc d'équipements aux "
                       "usages cloud, avec suivi des plans de réduction.",
        "url": "https://verdikt.io/",
        "theme": "Évaluation et mesure",
        "type": "Outil",
        "profil": "Informaticien/Expert",
        "cout": "Payant",
        "tags": ["Mesure", "Empreinte Carbone", "Stratégie"],
    },
    {
        "nom": "Cleanfox",
        "description": "Service de désinscription en masse des courriels publicitaires et de "
                       "nettoyage des boîtes de réception. Levier d'entrée grand public vers la "
                       "sobriété des données, souvent utilisé en accompagnement d'un Digital "
                       "Cleanup Day.",
        "url": "https://www.cleanfox.io/",
        "theme": "Sobriété de ses données",
        "type": "Outil",
        "profil": "Tout public/débutant",
        "cout": "Gratuit",
        "tags": ["Sobriété", "Data", "Sensibilisation"],
    },
]


def slug(valeur):
    valeur = unicodedata.normalize("NFKD", str(valeur))
    valeur = "".join(c for c in valeur if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "-", valeur).strip("-").lower()


def norm_url(url):
    url = (url or "").strip().lower()
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"^www\.", "", url)
    return url.rstrip("/")


def norm_nom(nom):
    nom = unicodedata.normalize("NFKD", (nom or "").lower())
    nom = "".join(c for c in nom if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", nom)


def tester(url):
    for methode in ("HEAD", "GET"):
        try:
            requete = urllib.request.Request(url, method=methode,
                                             headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(requete, timeout=25, context=CTX) as reponse:
                return str(reponse.status), reponse.geturl()
        except urllib.error.HTTPError as erreur:
            if methode == "HEAD" and erreur.code in (400, 403, 405, 501):
                continue
            return str(erreur.code), url
        except Exception as erreur:
            return "ERR:" + type(erreur).__name__, url
    return "ERR:inconnu", url


def main():
    ecrire = "--ecrire" in sys.argv
    chemin = os.path.join(DATA, f"tools-{LANGUE}.json")
    with open(chemin, encoding="utf-8") as fichier:
        charge = json.load(fichier)
    outils = charge["outils"]

    urls = {norm_url(o["url"]) for o in outils if o.get("url")}
    noms = {norm_nom(o["nom"]) for o in outils}
    identifiants = {o["id"] for o in outils}
    aujourd_hui = date.today().isoformat()

    ajoutees, ignorees = [], []

    for entree in NOUVELLES:
        if norm_url(entree["url"]) in urls:
            ignorees.append((entree["nom"], "URL déjà référencée"))
            continue
        if norm_nom(entree["nom"]) in noms:
            ignorees.append((entree["nom"], "nom déjà référencé"))
            continue

        statut, finale = tester(entree["url"])
        if statut in ("404", "410") or statut.startswith("ERR:gaierror"):
            ignorees.append((entree["nom"], f"lien injoignable ({statut})"))
            continue
        if statut == "200" and finale != entree["url"]:
            print(f"  redirection suivie : {entree['url']} -> {finale}")
            entree["url"] = finale

        identifiant = slug(entree["nom"])
        suffixe = 2
        while identifiant in identifiants:
            identifiant = f"{slug(entree['nom'])}-{suffixe}"
            suffixe += 1
        identifiants.add(identifiant)

        outil = {
            "id": identifiant,
            "nom": entree["nom"],
            "description": entree["description"],
            "url": entree["url"],
            "theme": entree["theme"],
            "domaine": entree.get("domaine", ""),
            "type": entree["type"],
            "profil": entree.get("profil", ""),
            "cout": entree.get("cout", ""),
            "tags": entree.get("tags", []),
            "lien_ok": "ok" if statut == "200" else "a-verifier",
            "verifie_le": aujourd_hui,
            "ajoute_le": str(date.today().year),
        }
        outils.append(outil)
        urls.add(norm_url(outil["url"]))
        noms.add(norm_nom(outil["nom"]))
        ajoutees.append((outil["nom"], statut, outil["theme"]))

    outils.sort(key=lambda o: (o["theme"], o["nom"].lower()))

    for nom, statut, theme in ajoutees:
        print(f"  + [{statut}] {nom}\n      → {theme}")
    for nom, raison in ignorees:
        print(f"  · ignorée : {nom} ({raison})")
    print(f"\n{len(ajoutees)} ajoutée(s), {len(ignorees)} ignorée(s). "
          f"Catalogue {LANGUE} : {len(outils)} ressources.")

    if ecrire and ajoutees:
        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(charge, fichier, ensure_ascii=False, indent=1)
            fichier.write("\n")
        print(f"{chemin} réécrit")
    elif not ecrire:
        print("Aperçu seulement. Relancer avec --ecrire pour appliquer.")


if __name__ == "__main__":
    main()

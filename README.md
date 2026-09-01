# Boîte à outils du Numérique Responsable

[![Licence: MIT + CC BY 4.0](https://img.shields.io/badge/Licence-MIT%20%2B%20CC%20BY%204.0-yellow.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/github/v/release/Institut-du-Numerique-Responsable/boite_a_outils?label=Version)](https://github.com/Institut-du-Numerique-Responsable/boite_a_outils/releases)
[![CI](https://github.com/Institut-du-Numerique-Responsable/boite_a_outils/actions/workflows/validate-data.yml/badge.svg)](https://github.com/Institut-du-Numerique-Responsable/boite_a_outils/actions/workflows/validate-data.yml)
[![HTML/CSS/JS](https://img.shields.io/badge/Tech-HTML%2FCSS%2FJS-blue.svg)]()
[![Outils](https://img.shields.io/badge/Outils-355_FR_%7C_341_EN_%7C_341_NL-orange.svg)]()

Site statique de la boîte à outils NR de l'[Institut du Numérique Responsable](https://institutnr.org).
Publié sur <https://sustainableit-tools.isit-europe.org/>.

**355 ressources en français, 341 en anglais et 341 en néerlandais** : outils, guides,
référentiels, formations et textes de loi du numérique responsable, classés par thème, public
visé, type et mode d'accès.

## Ce que c'est

HTML, CSS et JavaScript. Pas de base de données, pas de PHP, pas de framework, pas de
bibliothèque tierce, aucune police téléchargée. La recherche et les filtres s'exécutent dans
le navigateur à partir d'un fichier JSON. Aucun cookie n'est déposé.

Le site remplace une application PHP + MySQL de 2022, dont l'archive est conservée hors dépôt
(`../inr-sustainableit-tools-ARCHIVE-php-2026-08-15.tar.gz`).

## Organisation

```
www/                 le site à publier : copier son contenu à la racine web
  data/*.json        source de vérité du catalogue, éditée directement
  assets/            style.css, app.js, matomo.js, logo
  outils/ themes/    pages générées, une par ressource et par thème
  en/                version anglaise (logo ISIT)
  nl/                version néerlandaise (341 fiches traduites, en relecture)
  data/tools-{es,de}.json  catalogues réservés aux futures traductions
tools/               scripts de maintenance et rapports : non publiés
```

## Modifier le catalogue

Éditez `www/data/tools-fr.json`, puis :

```bash
python3 tools/verifier_donnees.py    # structure, identifiants, URL
python3 tools/generer_pages.py       # fiches, thèmes, sitemap, llms.txt, versions d'assets
python3 tools/verifier_seo.py        # cohérence données ↔ pages ↔ sitemap
python3 tools/precompresser.py       # archives .br et .gz
```

Détail des champs et des autres scripts : [`tools/README.md`](tools/README.md).

## Tester

```bash
cd www && python3 -m http.server 8765     # terminal 1
npm install jsdom && node tools/test-site.mjs   # terminal 2
```

45 assertions : recherche, facettes, tri, pagination, fiches juridiques, accessibilité.

## Langues et traductions

Le français, l'anglais et le néerlandais sont publiés. Le catalogue néerlandais compte
341 fiches traduites et reste ouvert à la relecture éditoriale. L'espagnol et l'allemand sont
préparés dans le menu et signalés « bientôt ». Une langue devient publique après validation
de ses fiches, de ses thèmes et de ses métadonnées SEO.

## Contribuer

Les contributions passent par une Pull Request vers `main`. Les contributeurs peuvent
proposer des corrections, de nouvelles ressources ou des améliorations de traduction.
Le détail du format des données, des contrôles et de la procédure est disponible dans
[`CONTRIBUTING.md`](CONTRIBUTING.md). Les changements de données doivent être accompagnés
des pages générées et passer les validateurs avant la revue.

Les propriétaires de code sont définis dans [`.github/CODEOWNERS`](.github/CODEOWNERS) :
`@gridboy`, `@Guillaume-INR`, `@vcourbou` et `@vincentcourboulay`.

## Documentation

- [Guide de contribution](CONTRIBUTING.md)
- [Documentation des outils de maintenance](tools/README.md)
- [Spécification multilingue et SEO](docs/superpowers/specs/2026-08-28-multilingual-seo-design.md)
- [Points de relecture des traductions NL](TRANSLATION_REVIEW.md)

La CI vérifie automatiquement la structure des catalogues, les liens, le SEO, les pages
multilingues et les tests Python à chaque Pull Request et à chaque mise à jour de `main`.

Les pages françaises utilisent le logo INR. Les pages dans les autres langues utilisent
le logo neutre ISIT (Institute for Sustainable IT).

## Licence et crédits

Contenu éditorial © Institut du Numérique Responsable. Les ressources référencées appartiennent
à leurs auteurs respectifs ; le site en donne le nom, une description et un lien.

Le dépôt est distribué sous licence double :

- [MIT](LICENSE) pour le code HTML, CSS, JavaScript et les scripts ;
- [CC BY 4.0](LICENSE-CC-BY-4.0) pour les textes éditoriaux, traductions, sélections et données.

La licence CC BY 4.0 autorise la copie, la modification et la redistribution, y compris
commerciale, avec attribution et indication des changements. Les droits des auteurs des
ressources externes restent inchangés.

# Boîte à outils du Numérique Responsable

Site statique de la boîte à outils NR de l'[Institut du Numérique Responsable](https://institutnr.org).
Publié sur <https://sustainableit-tools.isit-europe.org/>.

**355 ressources en français, 193 en anglais** — outils, guides, référentiels, formations et
textes de loi du numérique responsable, classés par thème, public visé, type et mode d'accès.

## Ce que c'est

HTML, CSS et JavaScript. Pas de base de données, pas de PHP, pas de framework, pas de
bibliothèque tierce, aucune police téléchargée. La recherche et les filtres s'exécutent dans
le navigateur à partir d'un fichier JSON. Aucun cookie n'est déposé.

Le site remplace une application PHP + MySQL de 2022, dont l'archive est conservée hors dépôt
(`../inr-sustainableit-tools-ARCHIVE-php-2026-08-15.tar.gz`).

## Organisation

```
www/                 le site à publier — copier son contenu à la racine web
  data/*.json        source de vérité du catalogue, éditée directement
  assets/            style.css, app.js, matomo.js, logo
  outils/ themes/    pages générées, une par ressource et par thème
  en/                version anglaise
tools/               scripts de maintenance et rapports — non publiés
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

## Publier

```bash
rsync -av --delete --exclude '.DS_Store' www/ utilisateur@serveur:/chemin/racine-web/
```

C'est le **contenu** de `www/` qui va à la racine web. Vérifiez que le `.htaccess` a bien été
transféré : il commence par un point et la plupart des clients FTP le masquent.

## Licence et crédits

Contenu éditorial © Institut du Numérique Responsable. Les ressources référencées appartiennent
à leurs auteurs respectifs ; le site en donne le nom, une description et un lien.

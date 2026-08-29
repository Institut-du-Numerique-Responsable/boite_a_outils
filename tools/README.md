# Maintenance de la boîte à outils NR

Le site publié (`www/`) est statique : HTML, CSS, JavaScript et un catalogue JSON par langue.
Il n'y a plus de base MySQL, plus de PHP, plus de back-office.

**La source de vérité, ce sont les fichiers `www/data/tools-*.json`.**
On les modifie directement dans le code : ils sont indentés, non échappés, et donnent
des diffs Git lisibles.

## Ajouter ou modifier une ressource

Éditez `www/data/tools-fr.json`, dans le tableau `outils` :

```json
{
 "id": "ecoindex",
 "nom": "EcoIndex",
 "description": "Mesure l'empreinte environnementale d'une page web…",
 "url": "https://www.ecoindex.fr/",
 "theme": "Évaluation et mesure",
 "domaine": "Front-end",
 "type": "Outil",
 "profil": "Informaticien/Expert",
 "cout": "Gratuit",
 "tags": ["Mesure", "Web"],
 "lien_ok": "ok",
 "verifie_le": "2026-08-15"
}
```

| Champ | Obligatoire | Remarque |
|---|---|---|
| `id` | oui | unique, en minuscules sans accent ; sert d'ancre d'URL |
| `nom` | oui | tel qu'il s'affiche sur la fiche |
| `description` | oui | tronquée à ~190 signes à l'affichage, texte intégral dans la recherche |
| `url` | oui | absolue, `https://` — vide seulement si `lien_ok` vaut `interne` |
| `theme` | oui | alimente la facette principale ; réutilisez un thème existant |
| `type`, `profil`, `cout`, `domaine` | non | alimentent les autres facettes ; laisser `""` si inconnu |
| `tags` | oui | liste, éventuellement vide |
| `lien_ok` | oui | `ok`, `a-verifier` ou `interne` |
| `verifie_le` | oui | date ISO affichée sur la fiche |
| `ajoute_le` | non | année d'entrée **au catalogue**, ex. `"2024"` ; affiche le badge « Référencé en 2024 ». Ce n'est pas la date de création de la ressource |
| `loi` | non | contenu des fiches juridiques (`lien_ok` = `interne`) |

Un thème ou un type inédit crée automatiquement une entrée de filtre : pas de liste à
tenir ailleurs. Inversement, une faute de frappe crée un doublon dans la colonne de
filtres — d'où le validateur ci-dessous.

## Ajouter des ressources

Décrivez-les dans la liste `NOUVELLES` de `tools/ajouter_ressources.py`, puis :

```bash
python3 tools/ajouter_ressources.py            # aperçu : doublons, liens testés
python3 tools/ajouter_ressources.py --ecrire   # applique
```

Le script refuse les doublons d'URL et de nom, suit les redirections, génère
l'identifiant et réinsère au bon endroit. Une entrée déjà présente est simplement ignorée :
la liste peut donc rester en place d'une fois sur l'autre.

## Compléter les descriptions manquantes

```bash
python3 tools/completer_descriptions.py            # aperçu
python3 tools/completer_descriptions.py --ecrire   # applique
```

Récupère la méta-description du site cible plutôt que d'inventer un texte. Relisez toujours
le résultat : un domaine expiré et racheté renvoie une description sans rapport — c'est
ainsi qu'un lien vers un site de jeu en ligne a été détecté et retiré.

## Regénérer les pages de thème après une modification des données

**Obligatoire dès que le catalogue change**, sinon les pages de thème et le sitemap
restent sur l'ancien contenu :

```bash
python3 tools/generer_pages.py
```

Produit `www/themes/*.html` (15 pages FR), `www/en/topics/*.html` (13 pages EN), les
sommaires, les données structurées JSON-LD et `www/sitemap.xml`.

Les catalogues `tools-nl.json`, `tools-es.json` et `tools-de.json` sont préparés mais
restent désactivés tant que leurs entrées ne sont pas traduites et relues. Ne marquez
une locale comme publiée qu'après avoir exécuté :

```bash
python3 tools/verifier_donnees.py
python3 tools/verifier_multilingual.py
```

## Détecter les domaines détournés

```bash
python3 tools/detecter_detournements.py
```

Un lien qui répond 200 n'est pas un lien valide. Quand un domaine est abandonné, il est
souvent racheté et repeuplé — jeux d'argent, pharmacie, contenu automatisé. L'audit HTTP
ne voit rien et l'INR se retrouve à recommander un site qu'il n'a jamais approuvé.

Le script lit le titre et la description de chaque page référencée et croise avec le nom
de la ressource attendue. Il ne modifie rien : les cas demandent un jugement humain.
Quatre domaines ont été retirés grâce à lui — `enviroscore.fr` (devenu un comparateur de
casinos), `thulatula.com` pour Ecometer (couvertures africaines), la Fresque de la
Publicité (site de jeu indonésien) et `negaoctet.org`, écarté avant ajout.

Les signalements à un seul motif sont surtout des produits renommés (Contrast Ratio,
Electricity Maps, Solidarité Numérique) : à lire, pas à retirer machinalement.

## Vérifier la cohérence SEO

```bash
python3 tools/verifier_seo.py
```

Le contrôle complémentaire des locales vérifie les attributs `lang`, les canoniques et
les annotations `hreflang` :

```bash
python3 tools/verifier_multilingual.py
```

Contrôle, après `generer_pages.py` : une fiche par ressource et aucune orpheline, autant de
pages de thème que de thèmes, toutes les URL du sitemap réellement servies, aucune page
absente du sitemap, `lastmod` partout, totaux exacts dans `llms.txt` et `llms-full.txt`,
robots d'IA autorisés, JSON-LD présent sur l'accueil et sur les fiches. Sortie en code 1
si une incohérence subsiste.

C'est ce contrôle qui a révélé que le générateur laissait derrière lui les fiches des
ressources retirées : quatre pages continuaient d'être servies et indexées, dont celles
des domaines détournés. `generer_pages.py` élague désormais ces fichiers.

## Vérifier avant de publier

```bash
# Structure : champs obligatoires, ids uniques, URL bien formées, thèmes orphelins
python3 tools/verifier_donnees.py

# En plus : rappelle chaque lien, met à jour lien_ok et verifie_le, signale les morts
python3 tools/verifier_donnees.py --liens

# Idem, et retire les ressources mortes (consignées dans tools/retirees-AAAA-MM-JJ.csv)
python3 tools/verifier_donnees.py --liens --retirer-morts
```

Le script sort en code 1 si une anomalie bloquante subsiste : utilisable tel quel en CI.
Le TLS est vérifié — un certificat invalide fait passer la ressource en « à revérifier »,
ce qui est une information utile sur l'outil référencé.

## Tester le site

```bash
cd www && python3 -m http.server 8765     # terminal 1
npm install jsdom && node tools/test-site.mjs   # terminal 2
```

45 assertions : chargement FR et EN, recherche sans accent, recherche multi-mots,
facettes, jetons de filtre, mots-clés, pagination, tri, fiches juridiques, liens
sortants, pages de thème, accessibilité de base.

## Décisions de structure

- **Thème** = colonne `Catégorie` du classeur 2024, renseignée à 100 %, donc facette
  principale. L'axe `Cible Architecture` n'est rempli qu'à 38 % : facette secondaire.
- **Fiches juridiques** : les 15 textes de loi n'ont jamais eu de lien externe, leur
  contenu vivait dans `precision_1` à `precision_4`. Ils s'ouvrent en fiche, sans page
  dédiée, et restent partageables par l'URL `?fiche=<id>`.
- **Aucune police téléchargée** : Inter si installée, pile système sinon.
- **Mesure d'audience sans cookie** : Matomo auto-hébergé (`analytic.institutnr.org:8443`,
  site 16), configuré avec `disableCookies` et `setDoNotTrack`. Cette configuration relève
  de l'exemption de consentement CNIL, d'où l'absence de bandeau. Réactiver les cookies
  imposerait de rétablir un bandeau **et** de corriger les mentions légales.
  Le code est dans `www/assets/matomo.js`, jamais en ligne dans le HTML : un script inline
  exigerait `'unsafe-inline'` dans la CSP.
- **CSP** : définie dans `www/.htaccess`. L'origine Matomo est autorisée dans `script-src`,
  `connect-src` et `img-src`, **port 8443 inclus** — une origine sans port ne la couvre pas.
- Le tri par défaut est thématique : mettre les ajouts récents en tête remontait les
  fiches les moins documentées.

## SEO et référencement auprès des IA

### Terminologie multilingue

Dans les versions non françaises, **INR** est rendu par **ISIT** (*Institute for
Sustainable IT*) et **DEEE** par **WEEE** (*Waste Electrical and Electronic Equipment*).
Les acronymes français **RGAA** et **RGESN** restent inchangés : ce sont les noms
officiels des référentiels.

Le catalogue vit dans un JSON : sans JavaScript, un robot ne verrait rien, et aucune
ressource n'aurait d'adresse citable. Cinq dispositifs compensent, tous produits par
`generer_pages.py` :

1. **Une page par ressource** — `www/outils/<id>.html` (348 en français),
   `www/en/tools/<id>.html` (205 en anglais). C'est l'unité qu'un moteur indexe et qu'un
   modèle de langage cite. Titre, description, tableau de métadonnées, fil d'Ariane,
   ressources voisines du même thème, et lien sortant vers le site officiel.
2. **Pages de thème** — 15 en français, 13 en anglais, plus leurs sommaires. Entrées de
   longue traîne, et maillage vers les fiches.
3. **Données structurées JSON-LD** — `WebSite` + `SearchAction` sur les accueils,
   `CollectionPage` + `ItemList` sur les thèmes, `SoftwareApplication` ou `CreativeWork`
   + `BreadcrumbList` sur chaque fiche.
4. **`llms.txt` et `llms-full.txt`** — convention llmstxt.org. Le premier présente le site,
   ses thèmes et ses jeux de données ; le second contient le catalogue entier en texte
   (~170 Ko), pour qu'un modèle puisse le lire sans parcourir 348 pages ni exécuter de
   JavaScript. Les conditions de citation y figurent explicitement.
5. **`robots.txt` ouvert aux robots conversationnels** — GPTBot, ClaudeBot, PerplexityBot,
   Google-Extended, Applebot-Extended, CCBot et consorts sont **autorisés volontairement** :
   l'objectif est que la boîte à outils soit citée avec sa source plutôt que paraphrasée
   sans attribution. Si l'INR change de position, inverser les règles dans
   `ecrire_robots()` — le fichier est régénéré à chaque exécution, une modification
   manuelle serait écrasée.

Maillage interne : l'accueil et les pieds de page pointent vers le sommaire des thèmes,
chaque carte de résultat porte un lien « Fiche détaillée », chaque fiche renvoie vers son
thème et vers cinq ressources voisines.

**Sitemap** : 731 URL avec `lastmod`, régénéré à chaque exécution.

#### Ce que le générateur produit aussi

- **`hreflang`** entre les 335 ressources présentes dans les deux langues, plus `x-default`
  vers le français. Sans ces balises, les moteurs traitent les deux versions comme des pages
  concurrentes au lieu de traductions.
- **`llms.txt` et `llms-full.txt` en anglais** dans `www/en/`, en plus des versions françaises.
- **Directives d'extrait** (`max-snippet:-1`, `max-image-preview:large`) sur toutes les pages :
  elles autorisent les moteurs et les assistants à citer un extrait complet plutôt qu'une
  ligne tronquée.

## Ce qui reste à faire côté INR

- Déclarer le site dans la Search Console Google et Bing Webmaster Tools, puis y soumettre
  le sitemap.
- Obtenir des liens depuis `institutnr.org` vers cette boîte à outils : c'est le signal
  qui manque le plus, et le seul que le code ne peut pas produire.
- Renseigner le domaine réel dans `DOMAINE` (`tools/generer_pages.py`) s'il diffère de
  `https://tools.institutnr.org` — toutes les URL canoniques, le sitemap et les `llms.txt`
  en dépendent.

## Migration : ce qui a été archivé

La chaîne qui a servi une seule fois — import du dump MySQL, lecture du classeur XLSX, audits
initiaux et fusion — n'est plus dans le dépôt. Elle est conservée hors dépôt dans
`../inr-sustainableit-tools-ARCHIVE-migration.tar.gz`, avec les rapports produits à l'époque
(liens morts retirés, adresses corrigées, thèmes déduits). Les sources d'origine existent
toujours de leur côté : l'export SQL et les classeurs INR.

Il n'y a plus de commande qui écrase `www/data/*.json` : ces fichiers ne se modifient qu'à la
main ou par `ajouter_ressources.py`.

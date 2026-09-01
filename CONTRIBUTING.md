# Contribuer à la boîte à outils du Numérique Responsable

Merci de vouloir contribuer ! Ce projet est un catalogue collaboratif d'outils, guides et ressources pour le numérique responsable.

## Comment contribuer

### 1. Ajouter un nouvel outil

**Ne modifiez PAS directement `www/data/tools-fr.json`.**

Pour proposer un nouvel outil :

1. **Fork** ce dépôt
2. Créez une nouvelle branche : `git checkout -b ajout/[nom-de-l-outil]`
3. Éditez `tools/ajouter_ressources.py` :
   - Ajoutez votre outil dans la liste `NOUVELLES` en suivant le format existant
   - Exécutez : `python3 tools/ajouter_ressources.py --ecrire`
4. Vérifiez les données : `python3 tools/verifier_donnees.py`
5. Régénérez les pages : `python3 tools/generer_pages.py`
6. Vérifiez le SEO : `python3 tools/verifier_seo.py`
7. **Commitez** vos changements avec un message clair : `feat: ajouter [nom-de-l-outil]`
8. **Ouvrez une Pull Request** vers la branche `main`

### 2. Signaler un problème ou une correction

- Ouvrez une **Issue** pour signaler un lien mort, une description incorrecte ou un bug
- Si vous voulez corriger directement, suivez le même processus que pour un ajout

### 3. Mettre à jour un outil existant

Modifiez directement l'entrée dans `www/data/tools-fr.json` et ouvrez une PR avec :
- Le pourquoi de la modification
- La source de l'information (nouvelle URL, description mise à jour, etc.)

## Règles de contribution

- **Vérifiez toujours** avec `tools/verifier_donnees.py` avant de commiter
- **Testez** localement : `cd www && python3 -m http.server 8765`
- **Un outil par PR** pour faciliter la relecture
- **Pas de doublons** : vérifiez que l'outil n'existe pas déjà
- **Liens valides** : utilisez `https://` et vérifiez qu'ils répondent 200

## Structure des données

Chaque outil doit avoir :
- `id`: unique, minuscules, sans accents (ex: `ecoindex`)
- `nom`: nom officiel de l'outil
- `description`: claire et concise
- `url`: URL absolue en HTTPS
- `theme`: catégorie principale
- `type`, `profil`, `cout`, `domaine`: facettes de filtrage
- `tags`: mots-clés pertinents
- `lien_ok`: `"ok"` (testé) ou `"a-verifier"` (à vérifier)
- `verifie_le`: date au format `YYYY-MM-DD`

Voir [`tools/README.md`](tools/README.md) pour le détail des champs.

## Processus de validation

Les maintainers vérifieront :
1. La conformité du format JSON
2. L'unicité de l'ID et de l'URL
3. La validité du lien
4. La cohérence des métadonnées
5. L'absence de doublons

Votre PR sera mergée une fois validée, ou vous recevrez des commentaires pour correction.

## Code de conduite

Soyez bienveillant et respectueux. Les contributions doivent être constructives et alignées avec les valeurs du numérique responsable.

## Licences

Le code est distribué sous [licence MIT](LICENSE). Les textes, traductions, sélections et
données du catalogue sont distribués sous [licence CC BY 4.0](LICENSE-CC-BY-4.0). En
contribuant, vous confirmez disposer des droits nécessaires et acceptez cette réutilisation
libre avec attribution. Les contenus et marques des ressources référencées restent soumis
aux droits de leurs auteurs respectifs.

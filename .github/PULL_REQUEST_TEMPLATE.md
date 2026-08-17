# Pull Request - Boîte à outils NR

## Type de modification

- [ ] Ajout d'un nouvel outil
- [ ] Correction d'un outil existant
- [ ] Correction de bug
- [ ] Amélioration de la documentation
- [ ] Autre (précisez) : _________

## Description

Décrivez brièvement les changements apportés.

## Vérifications effectuées

- [ ] J'ai exécuté `python3 tools/verifier_donnees.py`
- [ ] J'ai exécuté `python3 tools/verifier_seo.py`
- [ ] J'ai régénéré les pages avec `python3 tools/generer_pages.py`
- [ ] J'ai testé localement avec `cd www && python3 -m http.server 8765`

## Pour les ajouts d'outils

- [ ] J'ai utilisé `tools/ajouter_ressources.py` (et non pas modifié directement le JSON)
- [ ] L'outil n'existe pas déjà dans le catalogue
- [ ] Le lien est valide et répond en 200
- [ ] J'ai rempli tous les champs obligatoires (id, nom, description, url, theme, tags, lien_ok, verifie_le)

## Notes supplémentaires

Ajoutez ici toute information utile pour les relecteurs.

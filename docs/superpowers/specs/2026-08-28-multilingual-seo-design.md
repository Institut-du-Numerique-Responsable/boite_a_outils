# Architecture multilingue et stratégie SEO — conception

## Objectif

Étendre la Boîte à outils NR du français et de l’anglais au néerlandais,
à l’espagnol et à l’allemand, avec une architecture qui permette d’ajouter
d’autres langues sans réécrire le générateur.

## Périmètre

- Interface et navigation dans `fr`, `en`, `nl`, `es` et `de`.
- Catalogues et pages statiques par langue, lorsque le contenu est traduit.
- Sélecteur de langue accessible sur les accueils, thèmes et fiches.
- SEO international : URLs, canoniques, `hreflang`, JSON-LD, sitemaps et liens internes.
- Contrôles CI empêchant les pages ou annotations de langue cassées.

Les traductions éditoriales seront publiées progressivement. Une langue non
traduite ne doit pas être annoncée comme disponible ni apparaître dans ses
annotations `hreflang`.

## Architecture retenue

Les langues sont déclarées dans une table unique `LANGUES` avec, pour chaque
locale, le préfixe URL, le dossier de données, le dossier des thèmes, le dossier
des fiches, les libellés d’interface, les métadonnées SEO et l’état de publication.
Le générateur boucle sur les langues publiées au lieu de tester uniquement
`fr` ou `en`. Les identifiants de ressources restent stables et servent à
associer les variantes traduites.

Structure URL :

- français : `/`, `/themes/`, `/outils/` ;
- anglais : `/en/`, `/en/topics/`, `/en/tools/` ;
- néerlandais : `/nl/`, `/nl/topics/`, `/nl/tools/` ;
- espagnol : `/es/`, `/es/topics/`, `/es/tools/` ;
- allemand : `/de/`, `/de/topics/`, `/de/tools/`.

Le français reste la version par défaut de l’organisation INR. Les URLs sont
explicites et ne dépendent ni des cookies, ni de l’adresse IP, ni de
`Accept-Language`.

## Modèle de traduction

Chaque catalogue de langue est un fichier dédié (`tools-nl.json`, etc.)
contenant uniquement des ressources réellement traduites. Chaque entrée
conserve l’identifiant, l’URL externe, la licence et les informations factuelles
de la source ; les champs éditoriaux localisables sont traduits séparément.

Le générateur refuse silencieusement les fallbacks de langue pour les pages
SEO : une fiche non traduite n’est pas générée dans la langue concernée. Les
libellés de l’interface, les thèmes et les textes de pied de page doivent être
complets pour qu’une langue soit marquée `published`.

## Stratégie SEO

- `rel="canonical"` pointe vers l’URL de la page dans sa propre langue.
- Chaque page publiée contient un jeu identique de liens `hreflang` : elle-même
  et toutes ses variantes traduites, en codes `fr`, `en`, `nl`, `es`, `de`.
- `x-default` pointe vers une page de choix de langue dédiée, légère et
  indexable, qui renvoie vers les cinq accueils sans redirection automatique.
- Les balises `lang`, titres, descriptions, titres de sections, JSON-LD et
  fils d’Ariane sont localisés. `inLanguage` reflète la langue réelle.
- Un sitemap index référence un sitemap par langue. Les URLs absentes d’une
  langue ne sont pas ajoutées à son sitemap.
- Les pages d’une même ressource se lient entre elles via le sélecteur de
  langue ; les pages sans équivalent n’affichent pas de lien trompeur.
- Les fichiers `llms.txt` et `llms-full.txt` sont produits pour chaque langue.

Cette stratégie suit les recommandations Google : URLs distinctes, annotations
`hreflang` réciproques et contenu visible réellement traduit. Google précise que
`hreflang` n’est pas un mécanisme de détection de langue et qu’il ne faut pas
compter sur une adaptation automatique par navigateur ou IP.

## Déploiement éditorial

1. Refactoriser le moteur et les contrôles pour accepter toute langue déclarée.
2. Publier le néerlandais sur l’interface, les thèmes et les ressources prioritaires.
3. Étendre le même pipeline à l’espagnol.
4. Étendre le même pipeline à l’allemand.
5. Compléter progressivement les catalogues et soumettre les pages à une relecture humaine.

Une page traduite automatiquement mais non relue doit rester identifiée comme
brouillon interne et ne pas être publiée dans le sitemap.

## Contrôles et critères d’acceptation

- aucune URL générée ne retourne vers une langue inexistante ;
- chaque page publiée possède un canonical auto-référent et des `hreflang` réciproques ;
- tous les liens du sélecteur sont relatifs et valides depuis la profondeur courante ;
- les sitemaps ne contiennent que des pages existantes et publiées ;
- les contrôles existants de données, SEO et navigation passent pour toutes les langues ;
- le site reste utilisable au clavier, sur mobile et avec les préférences `prefers-reduced-motion`.

## Décisions hors périmètre

- pas de domaines ou sous-domaines nationaux ;
- pas de géociblage par pays (`nl-BE`, `de-DE`, etc.) tant qu’aucun contenu
  régional spécifique n’est fourni ;
- pas de traduction automatique en temps réel côté navigateur ;
- pas de réécriture des URLs historiques françaises ou anglaises.

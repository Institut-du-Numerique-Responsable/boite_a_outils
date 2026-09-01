# Traductions à relire

Points de doute rencontrés pendant la traduction du catalogue vers le
néerlandais. Chaque entrée conserve le terme d'origine dans les données tant
qu'un relecteur néerlandophone n'a pas tranché.

## Traduction complète du catalogue, 2026-09-01 (313 fiches)


## Récapitulatif

Le catalogue néerlandais couvre maintenant les 341 fiches du catalogue anglais.
28 fiches existaient avant cette session, 313 ont été ajoutées. Aucune fiche
préexistante n'a été modifiée.

Sur ces 341 fiches, **86 portent un nom différent de la source anglaise**. Dans
tous les cas il s'agit du nom réel du produit, restauré à partir d'une preuve
présente dans la fiche elle-même : la description, l'URL ou le dépôt de code.
La règle appliquée est qu'un nom de produit ne se traduit ni ne se reformate.
Ces corrections sont à répercuter dans `tools-en.json`, sans quoi le même
produit portera deux noms selon la langue.

### Libellés de thèmes appliqués

Les sept libellés qui restaient à fixer ont été appliqués pour pouvoir terminer
la traduction. Ils servent de filtres sur le site : les changer après
publication cassera les URL de filtre. À valider avant mise en ligne.

| Anglais | Néerlandais appliqué | Fiches |
| ------- | -------------------- | ------ |
| Energy & resource management | Energie- & grondstoffenbeheer | 25 |
| Organisational roadmap | Organisatorische routekaart | 25 |
| References & guides | Referenties & gidsen | 13 |
| Privacy, transparency & ethics | Privacy, transparantie & ethiek | 12 |
| WEEE & hardware | WEEE & hardware | 11 |
| Marketing & communication | Marketing & communicatie | 8 |
| Data sobriety | Datasoberheid | 7 |

### Points relevés sur les dernières passes

- **`Workshop`** est conservé tel quel comme valeur de `type` : le mot est
  d'usage courant en néerlandais. Cinq fiches sont concernées.
- **`ml-co2-impact` et `mlco2`** pointent vers le même outil sur
  mlco2.github.io. Quatrième doublon repéré, après `aequitas`,
  `axis`/`axe-devtools` et `greenframe`/`greenframe-2`.
- **`scaphandre` et `scaphandre-hubblo`** décrivent le même agent, avec deux URL
  différentes et deux thèmes différents. Cinquième doublon.
- **`data-centre-measures-catalogue-green-it-switzerland` et
  `data-centre-recommendations-green-it-switzerland`** partagent exactement la
  même URL. Sixième doublon.
- **Tag `HAVE`** sur la fiche `ml-co2-impact` : étiquette sans signification
  identifiable, probablement un artefact de traduction. Retirée, remplacée par
  les tags `AI` et `Machine learning` cohérents avec la fiche jumelle.
- **Tags avec virgule parasite** dans la source anglaise : `Data,` sur
  `denton-declaration`, `Climate,` sur `open-sustainable-technology`,
  `Accessibility,` sur `tanaguru`. Nettoyés côté néerlandais, à corriger côté
  anglais.
- **`INR` devient `ISIT`** dans les textes et les tags, conformément au
  glossaire. En revanche les noms propres « Académie NR » et « Institut du
  Numérique Responsable » sont conservés tels quels dans les intitulés de
  fiches : ce sont des noms d'entités, pas des mentions à traduire. À arbitrer
  si vous voulez l'inverse.
- **Valeurs restées en français dans le catalogue anglais**, traduites au passage
  côté néerlandais : domaines `Urgence Climatique` et `Référence`, tags
  `Conformité`, `Outils`, `Serveur`, `Empreinte carbone`, `Dérèglement
  climatique`, `Médias`, `Vulgarisation`, `Ecologie`, `Infographie`,
  `Ressources`, `Economie`, `Industrie`, `Efficacité Energétique`.
- **Fautes de frappe dans la source anglaise**, corrigées en néerlandais :
  `Caclulate your environmental footprint` (tag), `he Turing Way` (description),
  `SmartCitie` (tag), `Grabriel Salerno` (description), `GrenFrame`
  (description).

## Second passage du 2026-09-01 : thème Meting & beoordeling (50 fiches)

### Onze noms de produits encore restaurés

| Identifiant | Catalogue anglais | Forme retenue | Justification |
| ----------- | ----------------- | ------------- | ------------- |
| `aro` | Aro | ARO | acronyme d'Application Resource Optimizer, développé dans la description |
| `air-e-lca` | Air.e lca | Air.e LCA | acronyme |
| `cloud-carbon-footprint` | Cloud carbon footprint | Cloud Carbon Footprint | casse dans la description |
| `cloud-foundry-footprint` | Cloud foundry footprint | Cloud Foundry footprint | Cloud Foundry est un nom propre |
| `cloud-jewels` | Cloud jewels | Cloud Jewels | casse employée dans la fiche `cloud-carbon-footprint` |
| `ecodiag` | Ecodiag | EcoDiag | casse dans la description |
| `energy-profiler` | Energy profiler | Energy Profiler | nom du profileur Android |
| `globaldcanalysis-…` | Globaldcanalysis: … | GlobalDCAnalysis: … | dépôt `emasanet/GlobalDCAnalysis` |
| `green-algorithms` | Green algorithms | Green Algorithms | nom du site |
| `greenframe` et `greenframe-2` | Greenframe | GreenFrame | casse confirmée par la fiche `greenframe-cli` |

### greenframe et greenframe-2 : deux fiches pour le même produit

- **Texte concerné** : les fiches `greenframe` et `greenframe-2`, toutes deux
  vers greenframe.io.
- **Difficulté** : même produit, deux fiches, deux descriptions, deux domaines
  (`Front-end` et `Hosting`), deux jeux de tags. Depuis la restauration du nom,
  les deux s'appellent « GreenFrame » et le doublon saute aux yeux.
- **Proposition** : fusionner côté anglais. La fiche `greenframe-cli` est un
  produit distinct et doit rester.

### Nouveaux noms laissés en l'état malgré un doute

| Identifiant | Nom actuel | Doute | Proposition |
| ----------- | ---------- | ----- | ----------- |
| `agaro` | Agaro | l'URL est `aguaro.io`, la description écrit « Agaro ». L'un des deux est fautif | Aguaro, à confirmer |
| `ecograding` | Ecograding | l'URL pointe vers ecograder.com, dont le produit s'appelle Ecograder | Ecograder |
| `42u` | 42u | 42U est une société de datacenters, la casse habituelle est en capitale | 42U |
| `cookieviz` | Cookieviz | la CNIL écrit « CookieViz » sur ses propres pages | CookieViz |
| `greenprint` | Greenprint | le site printgreener.com présente le produit sous « GreenPrint » | GreenPrint |

### Choix de vocabulaire de ce second passage

| Anglais | Néerlandais retenu | Remarque |
| ------- | ------------------ | -------- |
| `Article` (type) | Artikel | |
| `Hosting` (domaine) | Hosting | emprunt courant |
| `Urgence Climatique` (domaine, resté en français dans la source) | Klimaaturgentie | valeur à normaliser côté anglais |
| `Référence` (domaine, resté accentué dans la source) | Referentie | même valeur que `Reference`, doublon à fusionner côté anglais |
| `Life-cycle assessment` (tag) | Levenscyclusanalyse | |
| `LCA software` (tag) | LCA-software | |
| `Serveur` (tag, resté en français) | Server | |
| `Empreinte carbone` (tag, resté en français) | CO2-voetafdruk | aligné sur le premier lot |
| `Ecologie` (tag, resté en français) | Ecologie | |
| `Understand` (tag) | Begrijpen | |
| `Calculator` (tag) | Rekenmodule | |
| `Software quality` (tag) | Softwarekwaliteit | |
| `Infrastructure` (tag) | Infrastructuur | |
| `language` (tag) | Programmeertaal | « language » seul est ambigu dans un filtre |
| `Imprint` (tag) | Voetafdruk | « imprint » semble une mauvaise traduction d'« empreinte » |
| `Ink`, `Paper`, `Print`, `Printer` (tags) | Inkt, Papier, Afdrukken, Printer | |
| `tuner` (tag, fiche `greenprint`) | retiré | tag opaque, sans signification identifiable. Les fiches concernées perdent donc un ou deux tags par rapport à la source anglaise |
| `carbon` et `footprint` (tags en minuscule) | retirés | doublons de `CO2` et `Footprint` déjà présents sur les mêmes fiches, la source les porte deux fois avec des casses différentes |

## Lots du 2026-09-01, premier passage

### Noms de produits restaurés dans leur forme réelle

Règle appliquée : le nom d'un produit ou d'un outil ne se traduit pas et ne se
reformate pas, il reste identique dans toutes les langues. Le catalogue anglais
a perdu la casse d'origine de nombreuses marques, et a traduit deux noms propres
comme s'ils étaient des mots communs. Les 50 fiches néerlandaises portent le nom
réel du produit. Dix-sept noms diffèrent donc de la source anglaise :

| Identifiant | Catalogue anglais | Forme retenue en néerlandais | Justification |
| ----------- | ----------------- | ---------------------------- | ------------- |
| `cottage` | Cottage | Cabanon | nom du projet dans l'URL, la description anglaise et le catalogue français |
| `axis` | Axis | axe DevTools | l'URL pointe vers l'extension axe DevTools de Deque |
| `opidor` | Opidor | OPIDoR | casse utilisée dans la description anglaise |
| `coldcms` | Coldcms | ColdCMS | casse utilisée dans la description anglaise |
| `video-optimizer` | Video optimizer | Video Optimizer | dépôt `attdevsupport/VideoOptimizer` |
| `data-co2-calculator-v4` | Data co2 calculator v4 | Data CO2 Calculator V4 | nom du fichier dans l'URL |
| `device-co2-calculator-v4` | Device co2 calculator v4 | Device CO2 Calculator V4 | nom du fichier dans l'URL |
| `ecoindex-simulator` | Ecoindex simulator | EcoIndex simulator | casse de la marque EcoIndex, déjà retenue au premier lot |
| `google-amp` | Google amp | Google AMP | acronyme |
| `gt-metrix` | Gt metrix | GTmetrix | casse utilisée dans la description anglaise |
| `intel-power-gadget` | Intel power gadget | Intel Power Gadget | nom du produit Intel |
| `ionos` | Ionos | IONOS | marque écrite en capitales |
| `linux-extended-bpf` | Linux extended bpf | Linux extended BPF | acronyme |
| `petra` | Petra | PETrA | casse utilisée dans la description anglaise |
| `accessible-office-documents-rgaa` | Accessible office documents (rgaa) | Accessible office documents (RGAA) | acronyme |
| `color-contrast-analyzer-cca` | Color contrast analyzer (cca) | Color contrast analyzer (CCA) | acronyme |
| `color-safe` | Color safe | Color Safe | nom du site colorsafe.co |

Ces corrections sont à répercuter dans `tools-en.json`, et pour partie dans
`tools-fr.json`, sans quoi le même produit portera deux noms selon la langue.
La correction des données sources n'a pas été faite ici, faute de mandat.

### axis et axe-devtools : deux fiches pour le même produit

- **Texte concerné** : les fiches `axis` (thème Web-ecodesign) et `axe-devtools`
  (thème Toegankelijkheid & inclusie).
- **Difficulté** : même extension de Deque, deux entrées, deux URL, deux thèmes.
  Depuis la restauration du nom réel, les deux fiches néerlandaises s'appellent
  « axe DevTools », ce qui rend le doublon visible sur le site.
- **Proposition** : fusionner côté anglais, en gardant la fiche du thème
  accessibilité et l'URL deque.com.

### cottage : le nom de la fiche ne correspond pas au projet

- **Texte concerné** : champ `nom` = « Cottage ».
- **Difficulté** : le projet s'appelle Cabanon, comme le confirment l'URL
  (`github.com/LINCnil/Cabanon`) et la description anglaise, qui parle bien de
  « Cabanon ». Le champ `nom` du catalogue anglais semble être une traduction
  automatique du mot français « cabanon ». Le défaut vient de la source
  anglaise, pas de la traduction néerlandaise.
- **Proposition** : corriger `nom` en « Cabanon » dans `tools-en.json`. La fiche
  néerlandaise porte déjà « Cabanon ».

### axis : le nom de la fiche ne correspond pas au produit

- **Texte concerné** : champ `nom` = « Axis ».
- **Difficulté** : l'URL pointe vers l'extension « axe DevTools » de Deque. Même
  hypothèse que ci-dessus, un « axe » lu comme un mot commun et traduit.
- **Proposition** : corriger `nom` en « axe DevTools » dans le catalogue
  anglais. La fiche néerlandaise porte déjà « axe DevTools ».

### aequitas et aequitas-framework : deux fiches pour un même projet

- **Texte concerné** : les fiches `aequitas` (thème Web-ecodesign) et
  `aequitas-framework` (thème AI), toutes deux traduites.
- **Difficulté** : même outil, deux entrées, deux thèmes, deux URL différentes
  mais liées. Le doublon existe dans le catalogue anglais.
- **Proposition** : fusionner côté anglais avant d'aller plus loin. Les deux
  fiches sont traduites pour l'instant, aucune n'est supprimée.

### avolin : thème et description incohérents

- **Texte concerné** : thème « Web eco-design », description « Energy management
  of IT parks ».
- **Difficulté** : la gestion énergétique d'un parc informatique relève du thème
  « Energy & resource management », pas de l'écoconception web. Incohérence
  présente dans la source anglaise.
- **Proposition** : reclasser côté anglais. Le thème néerlandais reprend pour
  l'instant la valeur de la source, « Web-ecodesign ».

### Tag « Tool » sur la fiche avolin

- **Texte concerné** : `tags: ["Tool"]`.
- **Difficulté** : « Tool » est déjà la valeur du champ `type`, l'utiliser comme
  tag n'apporte rien et le tag traduit (« Hulpmiddel ») encombrera le filtre.
- **Proposition** : retirer ce tag des deux catalogues. Traduit en attendant.

### Noms laissés en l'état malgré un doute

Ces fiches portent un nom qui semble fautif dans la source anglaise, mais je
n'ai pas de confirmation suffisante pour trancher. Le nom d'origine est
conservé.

| Identifiant | Nom actuel | Doute | Proposition |
| ----------- | ---------- | ----- | ----------- |
| `contrastradio` | Contrastradio | l'URL pointe vers l'outil « Contrast Ratio » de Siege Media. « Contrastradio » ressemble à une faute de frappe sur « contrast ratio » | Contrast Ratio |
| `checkmycolor` | Checkmycolor | le site s'appelle « Check My Colours » (checkmycolours.com) | Check My Colours |
| `google-richtxt` | Google richtxt | l'URL pointe vers le « Rich Results Test » de Google. « richtxt » n'est le nom d'aucun produit | Google Rich Results Test |
| `avolin` | Avolin | l'URL pointe vers le produit Verdiem d'IgniteTech. Avolin est une société, pas l'outil décrit | à vérifier auprès du contributeur d'origine |
| `color-contrast-analyzer-cca` | Color contrast analyzer (CCA) | l'outil de TPGi s'écrit « Colour Contrast Analyser », en orthographe britannique | Colour Contrast Analyser (CCA) |

### Choix de vocabulaire à confirmer

Ces termes n'apparaissaient pas dans le premier lot néerlandais. Ils sont
appliqués de façon cohérente dans ce lot et méritent une validation avant que
les lots suivants ne les reprennent.

| Anglais | Néerlandais retenu | Remarque |
| ------- | ------------------ | -------- |
| `Infographic` (type) | Infografiek | |
| `Paid` (coût) | Betaald | |
| `Contents` (domaine) | Content | « Inhoud » serait plus néerlandais, mais le domaine désigne le métier du contenu |
| `Referential` (tag) | Referentiekader | aligné sur le type « Gids / Referentiekader » du premier lot |
| `Sobriety` (tag) | Soberheid | |
| `Eval. Web` (tag) | Webevaluatie | abréviation opaque dans la source |
| `ToolBox` (tag) | Toolbox | emprunt courant en néerlandais |
| `Inclusion` (tag) | Inclusie | |
| `Footprint` (tag) | Voetafdruk | conforme au premier lot |
| `Data privacy` (tag) | Gegevensbescherming | |
| `Study` (type) | Studie | |
| `Reference` (domaine) | Referentie | |
| `Measure` (tag) | Meting | aligné sur le premier lot |
| `Energy` (tag) | Energie | |
| `Device` / `Terminals` (tags) | Apparaat / Eindapparatuur | |
| `Code Quality` (tag) | Codekwaliteit | |
| `Digital Mediation` (tag) | Digitale bemiddeling | |
| `Conformité` (tag, resté en français dans la source) | Conformiteit | |
| `Outils` (tag, resté en français dans la source) | Hulpmiddelen | |
| `Repository` (tag) | Referentiekader | « repository » désigne ici un référentiel de bonnes pratiques, pas un dépôt de code |

### Métadonnée `source` du fichier néerlandais

- **Texte concerné** : `"source": "Vertaling van het Engelstalige INR/ISIT-catalogus — eerste proefbatch"`.
- **Difficulté** : le fichier n'est plus un premier lot d'essai, il compte
  maintenant 48 fiches. La mention est restée telle quelle, faute de savoir quel
  libellé vous voulez y mettre.
- **Proposition** : « Vertaling van de Engelstalige INR/ISIT-catalogus ». À noter
  que le néerlandais correct est « van de » et non « van het » devant
  « catalogus », qui est un mot commun.

### Libellés de thèmes non encore fixés

Ce lot est resté dans les thèmes déjà traduits. Sept thèmes du catalogue anglais
n'ont pas encore d'équivalent néerlandais et bloqueront les prochains lots :

| Anglais | Proposition |
| ------- | ----------- |
| Energy & resource management | Energie- & resourcebeheer |
| Organisational roadmap | Organisatorische routekaart |
| References & guides | Referenties & gidsen |
| Privacy, transparency & ethics | Privacy, transparantie & ethiek |
| WEEE & hardware | WEEE & hardware |
| Marketing & communication | Marketing & communicatie |
| Data sobriety | Datasoberheid |

Ces libellés servent de filtres sur le site : une fois publiés, les changer
casse les URL de filtre. À valider avant le prochain lot.

## Incohérences du premier lot néerlandais (28 fiches), non modifiées

Relevées en dérivant les correspondances entre les 28 fiches déjà traduites et
leur source anglaise. Aucune n'a été corrigée, conformément à la consigne de ne
pas toucher aux fiches déjà traduites.

- `domaine` : trois fiches passent de « Front-end » à « Back-end » ou
  l'inverse, et « Reference » devient tantôt « Back-end », tantôt une chaîne
  vide.
- `profil` : « Content creator / Intermediate » est rendu tantôt par
  « Contentmaker / Gemiddeld », tantôt par « Algemeen publiek / Beginner »,
  tantôt par « IT-professional / Expert ».
- `type` : « Documentation » est rendu par « Documentatie », « Gids /
  Referentiekader » et « Opleiding » selon les fiches.
- `tags` : plusieurs fiches ont des tags sans rapport avec la source anglaise,
  par exemple « Repository » rendu par « Cloud, Impact ».

Ces écarts viennent peut-être d'un enrichissement volontaire à partir du
catalogue français. Si c'est le cas, la règle mérite d'être écrite, pour que les
lots suivants s'y conforment.

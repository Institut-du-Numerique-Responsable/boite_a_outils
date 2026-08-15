/* Boîte à outils NR — recherche et filtres côté client.
   Aucune dépendance : le JSON est chargé une fois, tout se fait en mémoire. */

(function () {
  "use strict";

  var LANG = document.documentElement.lang === "en" ? "en" : "fr";
  var PAGE = 48; // fiches rendues par lot

  var T = {
    fr: {
      resultats: "outils",
      resultat: "outil",
      sur: "sur",
      vide_titre: "Aucun outil ne correspond",
      vide_texte: "Élargissez la recherche : retirez un filtre, ou essayez un mot-clé plus court.",
      tout_effacer: "Tout effacer",
      voir_plus: "Voir plus d'outils",
      verifie: "Lien vérifié le",
      doute: "Lien à revérifier",
      fiche: "Fiche détaillée",
      dossier_fiches: "outils/",
      filtres_ouvrir: "Filtres",
      annonce: function (n) {
        return n + (n > 1 ? " outils trouvés" : " outil trouvé");
      }
    },
    en: {
      resultats: "tools",
      resultat: "tool",
      sur: "of",
      vide_titre: "No tool matches",
      vide_texte: "Broaden the search: remove a filter, or try a shorter keyword.",
      tout_effacer: "Clear all",
      voir_plus: "Show more tools",
      verifie: "Link checked on",
      doute: "Link needs rechecking",
      fiche: "Details",
      dossier_fiches: "tools/",
      filtres_ouvrir: "Filters",
      annonce: function (n) {
        return n + (n > 1 ? " tools found" : " tool found");
      }
    }
  }[LANG];

  /* ------------------------------------------------------------ outils */

  function deburr(texte) {
    return (texte || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  function el(tag, classe, texte) {
    var noeud = document.createElement(tag);
    if (classe) noeud.className = classe;
    if (texte != null) noeud.textContent = texte;
    return noeud;
  }

  function dateLisible(iso) {
    if (!iso) return "";
    var parts = iso.split("-");
    if (parts.length !== 3) return iso;
    if (LANG === "en") return iso;
    return parts[2] + "/" + parts[1] + "/" + parts[0];
  }

  /* ------------------------------------------------------------- état */

  var etat = {
    q: "",
    theme: [],
    type: [],
    profil: [],
    cout: [],
    tag: [],
    verifies: false,
    tri: "pertinence",
    limite: PAGE
  };

  var OUTILS = [];
  var vue = [];

  var dom = {
    champ: document.getElementById("champ-recherche"),
    effacer: document.getElementById("effacer-recherche"),
    raccourci: document.getElementById("raccourci"),
    suggestions: document.getElementById("suggestions"),
    filtres: document.getElementById("filtres-panneau"),
    bascule: document.getElementById("filtres-bascule"),
    reinit: document.getElementById("reinitialiser"),
    jetons: document.getElementById("jetons"),
    compte: document.getElementById("compte"),
    annonce: document.getElementById("annonce"),
    tri: document.getElementById("tri"),
    grille: document.getElementById("grille"),
    plus: document.getElementById("voir-plus"),
    vide: document.getElementById("vide"),
    fiche: document.getElementById("fiche"),
    total: document.getElementById("total-outils")
  };

  var FACETTES = [
    { cle: "theme", champ: "theme", titre: { fr: "Thème", en: "Topic" } },
    { cle: "type", champ: "type", titre: { fr: "Type de ressource", en: "Resource type" } },
    { cle: "profil", champ: "profil", titre: { fr: "Public visé", en: "Audience" } },
    { cle: "cout", champ: "cout", titre: { fr: "Accès", en: "Access" } }
  ];

  /* --------------------------------------------------------- recherche */

  function indexer(outil) {
    outil._nom = deburr(outil.nom);
    outil._desc = deburr(outil.description);
    outil._tags = deburr((outil.tags || []).join(" "));
    outil._reste = deburr([outil.theme, outil.type, outil.profil, outil.domaine].join(" "));
  }

  /* Score par terme : un mot tapé doit apparaître quelque part, et le nom
     pèse plus que la description. Zéro = le terme est absent, l'outil sort. */
  function scoreTerme(outil, terme) {
    if (outil._nom.indexOf(terme) === 0) return 100;
    if (outil._nom.indexOf(terme) > -1) return 60;
    if (outil._tags.indexOf(terme) > -1) return 30;
    if (outil._reste.indexOf(terme) > -1) return 15;
    if (outil._desc.indexOf(terme) > -1) return 8;
    return 0;
  }

  function correspond(outil, termes) {
    var total = 0;
    for (var i = 0; i < termes.length; i++) {
      var score = scoreTerme(outil, termes[i]);
      if (score === 0) return -1;
      total += score;
    }
    return total;
  }

  function filtrer() {
    var termes = deburr(etat.q).split(/\s+/).filter(Boolean);

    var retenus = OUTILS.filter(function (outil) {
      if (etat.verifies && outil.lien_ok === "a-verifier") return false;
      for (var i = 0; i < FACETTES.length; i++) {
        var facette = FACETTES[i];
        var choix = etat[facette.cle];
        if (choix.length && choix.indexOf(outil[facette.champ]) === -1) return false;
      }
      if (etat.tag.length) {
        for (var j = 0; j < etat.tag.length; j++) {
          if ((outil.tags || []).indexOf(etat.tag[j]) === -1) return false;
        }
      }
      if (!termes.length) {
        outil._score = 0;
        return true;
      }
      outil._score = correspond(outil, termes);
      return outil._score > -1;
    });

    if (etat.tri === "nom") {
      retenus.sort(function (a, b) {
        return a.nom.localeCompare(b.nom, LANG);
      });
    } else if (etat.tri === "theme") {
      retenus.sort(function (a, b) {
        return a.theme.localeCompare(b.theme, LANG) || a.nom.localeCompare(b.nom, LANG);
      });
    } else if (termes.length) {
      retenus.sort(function (a, b) {
        return b._score - a._score || a.nom.localeCompare(b.nom, LANG);
      });
    } else {
      // Sans recherche, l'ordre par thème est le plus lisible : mettre les
      // ajouts récents en tête remonterait les fiches les moins documentées.
      retenus.sort(function (a, b) {
        return a.theme.localeCompare(b.theme, LANG) || a.nom.localeCompare(b.nom, LANG);
      });
    }
    return retenus;
  }

  /* ------------------------------------------------------------ rendu */

  function surligner(texte, termes) {
    var fragment = document.createDocumentFragment();
    if (!termes.length) {
      fragment.appendChild(document.createTextNode(texte));
      return fragment;
    }
    var plat = deburr(texte);
    var bornes = [];
    termes.forEach(function (terme) {
      var depuis = 0;
      var trouve;
      while ((trouve = plat.indexOf(terme, depuis)) > -1) {
        bornes.push([trouve, trouve + terme.length]);
        depuis = trouve + terme.length;
      }
    });
    if (!bornes.length) {
      fragment.appendChild(document.createTextNode(texte));
      return fragment;
    }
    bornes.sort(function (a, b) {
      return a[0] - b[0];
    });
    var curseur = 0;
    bornes.forEach(function (borne) {
      if (borne[0] < curseur) return;
      fragment.appendChild(document.createTextNode(texte.slice(curseur, borne[0])));
      fragment.appendChild(el("mark", "marque", texte.slice(borne[0], borne[1])));
      curseur = borne[1];
    });
    fragment.appendChild(document.createTextNode(texte.slice(curseur)));
    return fragment;
  }

  function carte(outil, termes) {
    var item = el("li", "carte");

    item.appendChild(el("p", "carte__theme", outil.theme));

    var titre = el("h3", "carte__titre");
    var lien = document.createElement("a");
    if (outil.loi) {
      lien.href = "?fiche=" + encodeURIComponent(outil.id);
      lien.setAttribute("data-fiche", outil.id);
    } else {
      lien.href = outil.url;
      lien.target = "_blank";
      lien.rel = "noopener";
    }
    lien.appendChild(surligner(outil.nom, termes));
    titre.appendChild(lien);
    item.appendChild(titre);

    if (outil.description) {
      var desc = el("p", "carte__desc");
      var texte = outil.description.length > 190
        ? outil.description.slice(0, 190).replace(/\s+\S*$/, "") + "…"
        : outil.description;
      desc.appendChild(surligner(texte, termes));
      item.appendChild(desc);
    }

    var meta = el("div", "carte__meta");
    // « ajoute_le » est l'année d'entrée au catalogue, pas l'âge de la ressource :
    // « Référencé en » le dit, « Ajouté en » laissait croire à une date de création.
    if (outil.ajoute_le) {
      meta.appendChild(el("span", "etiquette etiquette--nouveau",
        (LANG === "fr" ? "Référencé en " : "Listed in ") + outil.ajoute_le));
    }
    if (outil.type) meta.appendChild(el("span", "etiquette", outil.type));
    // Les données portent le libellé dans leur propre langue : on reconnaît les
    // deux, sinon l'étiquette perdrait sa couleur sur la version anglaise.
    if (outil.cout === "Gratuit" || outil.cout === "Free") {
      meta.appendChild(el("span", "etiquette etiquette--gratuit", LANG === "fr" ? "Gratuit" : "Free"));
    }
    if (outil.cout === "Payant" || outil.cout === "Paid") {
      meta.appendChild(el("span", "etiquette etiquette--payant", LANG === "fr" ? "Payant" : "Paid"));
    }
    if (outil.profil) meta.appendChild(el("span", "etiquette", outil.profil));
    if (meta.childNodes.length) item.appendChild(meta);

    if (outil.tags && outil.tags.length) {
      var liste = el("ul", "carte__tags");
      // Les tags sont délégués à la grille : un écouteur au total, pas un par
      // bouton — sinon chaque rendu en recrée près de deux cents.
      outil.tags.slice(0, 4).forEach(function (tag) {
        var li = document.createElement("li");
        var bouton = el("button", null, "#" + tag);
        bouton.type = "button";
        bouton.setAttribute("data-tag", tag);
        li.appendChild(bouton);
        liste.appendChild(li);
      });
      item.appendChild(liste);
    }

    // Permalien vers la fiche : adresse citable, et seule voie d'accès quand la
    // ressource n'a pas de lien externe.
    var permalien = el("p", "carte__fiche");
    var versFiche = document.createElement("a");
    versFiche.href = T.dossier_fiches + encodeURIComponent(outil.id) + ".html";
    versFiche.textContent = T.fiche;
    permalien.appendChild(versFiche);
    item.appendChild(permalien);

    if (outil.lien_ok !== "interne") {
      var doute = outil.lien_ok === "a-verifier";
      item.appendChild(el(
        "p",
        "verif" + (doute ? " verif--doute" : ""),
        doute ? T.doute : T.verifie + " " + dateLisible(outil.verifie_le)
      ));
    }

    return item;
  }

  function rendre() {
    vue = filtrer();
    var termes = deburr(etat.q).split(/\s+/).filter(Boolean);
    var visibles = vue.slice(0, etat.limite);

    dom.grille.textContent = "";
    var fragment = document.createDocumentFragment();
    visibles.forEach(function (outil) {
      fragment.appendChild(carte(outil, termes));
    });
    dom.grille.appendChild(fragment);

    dom.vide.hidden = vue.length > 0;
    dom.grille.hidden = vue.length === 0;
    dom.plus.hidden = vue.length <= etat.limite;
    dom.plus.textContent = T.voir_plus + " (" + (vue.length - etat.limite) + ")";

    dom.compte.textContent = "";
    var fort = el("b", null, String(vue.length));
    dom.compte.appendChild(fort);
    dom.compte.appendChild(document.createTextNode(
      " " + (vue.length > 1 ? T.resultats : T.resultat) + " " + T.sur + " " + OUTILS.length
    ));
    dom.annonce.textContent = T.annonce(vue.length);

    rendreJetons();
    dom.effacer.hidden = !etat.q;
    dom.raccourci.hidden = !!etat.q;
    dom.reinit.disabled = !actif();
    majUrl();
  }

  function actif() {
    return !!etat.q || etat.verifies || etat.tag.length > 0 ||
      FACETTES.some(function (f) {
        return etat[f.cle].length > 0;
      });
  }

  function rendreJetons() {
    dom.jetons.textContent = "";
    FACETTES.forEach(function (facette) {
      etat[facette.cle].forEach(function (valeur) {
        ajouterJeton(valeur, function () {
          basculer(facette.cle, valeur, false);
        });
      });
    });
    etat.tag.forEach(function (tag) {
      ajouterJeton("#" + tag, function () {
        basculer("tag", tag, false);
      });
    });
    if (etat.verifies) {
      ajouterJeton(LANG === "fr" ? "Liens vérifiés" : "Checked links", function () {
        etat.verifies = false;
        document.getElementById("verifies").checked = false;
        etat.limite = PAGE;
        rendre();
      });
    }
  }

  function ajouterJeton(libelle, retrait) {
    var bouton = el("button", "jeton", libelle);
    bouton.type = "button";
    bouton.setAttribute("aria-label", (LANG === "fr" ? "Retirer le filtre " : "Remove filter ") + libelle);
    bouton.addEventListener("click", retrait);
    dom.jetons.appendChild(bouton);
  }

  function basculer(cle, valeur, force) {
    var liste = etat[cle];
    var position = liste.indexOf(valeur);
    var doitAjouter = force === undefined ? position === -1 : force;
    if (doitAjouter && position === -1) liste.push(valeur);
    if (!doitAjouter && position > -1) liste.splice(position, 1);

    var case_ = document.querySelector('input[data-cle="' + cle + '"][value="' + CSS.escape(valeur) + '"]');
    if (case_) case_.checked = doitAjouter;

    etat.limite = PAGE;
    rendre();
  }

  /* ---------------------------------------------------------- facettes */

  function construireFiltres() {
    FACETTES.forEach(function (facette) {
      var compte = {};
      OUTILS.forEach(function (outil) {
        var valeur = outil[facette.champ];
        if (valeur) compte[valeur] = (compte[valeur] || 0) + 1;
      });
      var valeurs = Object.keys(compte).sort(function (a, b) {
        return compte[b] - compte[a] || a.localeCompare(b, LANG);
      });
      if (!valeurs.length) return;

      var groupe = el("fieldset", "groupe");
      groupe.appendChild(el("legend", null, facette.titre[LANG]));
      valeurs.forEach(function (valeur) {
        var label = el("label", "option");
        var input = document.createElement("input");
        input.type = "checkbox";
        input.value = valeur;
        input.setAttribute("data-cle", facette.cle);
        input.addEventListener("change", function () {
          basculer(facette.cle, valeur, input.checked);
        });
        label.appendChild(input);
        label.appendChild(el("span", null, valeur));
        label.appendChild(el("em", null, String(compte[valeur])));
        groupe.appendChild(label);
      });
      dom.filtres.appendChild(groupe);
    });

    // Filtre signature : ne montrer que les liens dont l'audit est franc.
    var groupeLiens = el("fieldset", "groupe");
    groupeLiens.appendChild(el("legend", null, LANG === "fr" ? "Qualité des liens" : "Link quality"));
    var label = el("label", "option");
    var input = document.createElement("input");
    input.type = "checkbox";
    input.id = "verifies";
    input.addEventListener("change", function () {
      etat.verifies = input.checked;
      etat.limite = PAGE;
      rendre();
    });
    label.appendChild(input);
    label.appendChild(el("span", null, LANG === "fr" ? "Liens vérifiés uniquement" : "Verified links only"));
    groupeLiens.appendChild(label);
    dom.filtres.appendChild(groupeLiens);
  }

  function construireSuggestions() {
    var compte = {};
    OUTILS.forEach(function (outil) {
      (outil.tags || []).forEach(function (tag) {
        compte[tag] = (compte[tag] || 0) + 1;
      });
    });
    Object.keys(compte)
      .sort(function (a, b) {
        return compte[b] - compte[a];
      })
      .slice(0, 6)
      .forEach(function (tag) {
        var bouton = el("button", null, "#" + tag);
        bouton.type = "button";
        bouton.addEventListener("click", function () {
          basculer("tag", tag, true);
          dom.grille.scrollIntoView({ block: "start" });
        });
        dom.suggestions.appendChild(bouton);
      });
  }

  /* ---------------------------------------------------------------- URL */

  function majUrl() {
    var params = new URLSearchParams();
    if (etat.q) params.set("q", etat.q);
    FACETTES.forEach(function (facette) {
      etat[facette.cle].forEach(function (valeur) {
        params.append(facette.cle, valeur);
      });
    });
    etat.tag.forEach(function (tag) {
      params.append("tag", tag);
    });
    if (etat.verifies) params.set("verifies", "1");
    if (etat.tri !== "pertinence") params.set("tri", etat.tri);
    var chaine = params.toString();
    history.replaceState(null, "", chaine ? "?" + chaine : location.pathname);
  }

  function lireUrl() {
    var params = new URLSearchParams(location.search);
    etat.q = params.get("q") || "";
    FACETTES.forEach(function (facette) {
      etat[facette.cle] = params.getAll(facette.cle);
    });
    etat.tag = params.getAll("tag");
    etat.verifies = params.get("verifies") === "1";
    etat.tri = params.get("tri") || "pertinence";
    return params.get("fiche");
  }

  function appliquerUrlAuxControles() {
    dom.champ.value = etat.q;
    dom.tri.value = etat.tri;
    var verifies = document.getElementById("verifies");
    if (verifies) verifies.checked = etat.verifies;
    FACETTES.forEach(function (facette) {
      etat[facette.cle].forEach(function (valeur) {
        var case_ = document.querySelector('input[data-cle="' + facette.cle + '"][value="' + CSS.escape(valeur) + '"]');
        if (case_) case_.checked = true;
      });
    });
  }

  /* -------------------------------------------------- fiche juridique */

  function ouvrirFiche(id) {
    var outil = OUTILS.filter(function (o) {
      return o.id === id && o.loi;
    })[0];
    if (!outil) return;

    var entete = dom.fiche.querySelector(".fiche__entete h2");
    var corps = dom.fiche.querySelector(".fiche__corps");
    entete.textContent = outil.nom;
    corps.textContent = "";

    function bloc(titre, contenu) {
      if (!contenu) return;
      corps.appendChild(el("h3", null, titre));
      corps.appendChild(el("p", null, contenu));
    }

    if (outil.description) corps.appendChild(el("p", null, outil.description));
    bloc(LANG === "fr" ? "Qui est concerné" : "Who is concerned", outil.loi.concernes);
    bloc(LANG === "fr" ? "En vigueur depuis" : "In force since", outil.loi.depuis);

    if (outil.loi.contenu && outil.loi.contenu.length) {
      corps.appendChild(el("h3", null, LANG === "fr" ? "Contenu de la loi" : "Content"));
      outil.loi.contenu.forEach(function (partie) {
        if (partie.type === "liste") {
          var liste = document.createElement("ul");
          partie.items.forEach(function (item) {
            liste.appendChild(el("li", null, item));
          });
          corps.appendChild(liste);
        } else {
          corps.appendChild(el("p", null, partie.texte));
        }
      });
    }
    bloc(LANG === "fr" ? "Sanctions" : "Penalties", outil.loi.sanctions);

    if (typeof dom.fiche.showModal === "function") dom.fiche.showModal();
    else dom.fiche.setAttribute("open", "");
  }

  /* ------------------------------------------------------------ écoute */

  function brancher() {
    var minuteur;
    dom.champ.addEventListener("input", function () {
      clearTimeout(minuteur);
      minuteur = setTimeout(function () {
        etat.q = dom.champ.value.trim();
        etat.limite = PAGE;
        rendre();
      }, 120);
    });

    dom.effacer.addEventListener("click", function () {
      dom.champ.value = "";
      etat.q = "";
      etat.limite = PAGE;
      dom.champ.focus();
      rendre();
    });

    dom.tri.addEventListener("change", function () {
      etat.tri = dom.tri.value;
      rendre();
    });

    dom.plus.addEventListener("click", function () {
      var premierNouveau = etat.limite;
      etat.limite += PAGE;
      rendre();
      var cartes = dom.grille.children;
      if (cartes[premierNouveau]) {
        var lien = cartes[premierNouveau].querySelector("a");
        if (lien) lien.focus();
      }
    });

    dom.reinit.addEventListener("click", function () {
      etat.q = "";
      etat.tag = [];
      etat.verifies = false;
      etat.limite = PAGE;
      FACETTES.forEach(function (facette) {
        etat[facette.cle] = [];
      });
      dom.champ.value = "";
      Array.prototype.forEach.call(dom.filtres.querySelectorAll("input"), function (input) {
        input.checked = false;
      });
      rendre();
    });

    dom.bascule.addEventListener("click", function () {
      var ouvert = dom.filtres.hidden;
      dom.filtres.hidden = !ouvert;
      dom.bascule.setAttribute("aria-expanded", String(ouvert));
    });

    dom.grille.addEventListener("click", function (evenement) {
      var tag = evenement.target.closest("button[data-tag]");
      if (tag) {
        basculer("tag", tag.getAttribute("data-tag"), true);
        return;
      }
      var lien = evenement.target.closest("a[data-fiche]");
      if (!lien) return;
      evenement.preventDefault();
      ouvrirFiche(lien.getAttribute("data-fiche"));
    });

    dom.fiche.querySelector(".fiche__fermer").addEventListener("click", function () {
      dom.fiche.close();
    });

    document.addEventListener("keydown", function (evenement) {
      if (evenement.key === "/" && document.activeElement !== dom.champ) {
        evenement.preventDefault();
        dom.champ.focus();
        dom.champ.select();
      }
      if (evenement.key === "Escape" && document.activeElement === dom.champ && dom.champ.value) {
        dom.champ.value = "";
        etat.q = "";
        rendre();
      }
    });
  }

  /* ------------------------------------------------------------ départ */

  var BASE = document.documentElement.getAttribute("data-donnees") || "data/";

  fetch(BASE + "tools-" + LANG + ".json")
    .then(function (reponse) {
      if (!reponse.ok) throw new Error(reponse.status);
      return reponse.json();
    })
    .then(function (charge) {
      OUTILS = charge.outils;
      OUTILS.forEach(indexer);
      if (dom.total) dom.total.textContent = String(OUTILS.length);

      var fiche = lireUrl();
      construireFiltres();
      construireSuggestions();
      appliquerUrlAuxControles();
      brancher();
      rendre();
      if (fiche) ouvrirFiche(fiche);
    })
    .catch(function () {
      dom.vide.hidden = false;
      dom.vide.querySelector("h2").textContent = LANG === "fr"
        ? "Les données n'ont pas pu être chargées"
        : "Data could not be loaded";
      dom.vide.querySelector("p").textContent = LANG === "fr"
        ? "Rechargez la page. Si le problème persiste, écrivez à contact@institutnr.org."
        : "Reload the page. If the problem persists, write to contact@institutnr.org.";
    });
})();

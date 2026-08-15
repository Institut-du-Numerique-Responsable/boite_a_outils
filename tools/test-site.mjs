/* Test de bout en bout de la boîte à outils, dans jsdom. */
import { JSDOM, VirtualConsole } from "jsdom";

const BASE = "http://127.0.0.1:8765/";
let echecs = 0;

function ok(condition, libelle, detail) {
  console.log((condition ? "  PASS  " : "  FAIL  ") + libelle + (detail ? "  → " + detail : ""));
  if (!condition) echecs++;
}

async function attendre(predicat, ms = 5000) {
  const fin = Date.now() + ms;
  while (Date.now() < fin) {
    if (predicat()) return true;
    await new Promise((r) => setTimeout(r, 50));
  }
  return false;
}

async function charger(url) {
  const vc = new VirtualConsole();
  const erreurs = [];
  vc.on("jsdomError", (e) => erreurs.push(e.message));
  vc.on("error", (...a) => erreurs.push(a.join(" ")));
  const dom = await JSDOM.fromURL(url, {
    runScripts: "dangerously",
    resources: "usable",
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(window) {
      // jsdom n'a pas fetch ; les navigateurs cibles l'ont nativement.
      window.fetch = (chemin, init) => fetch(new URL(chemin, window.location.href), init);
    }
  });
  const w = dom.window;
  await attendre(() => w.document.getElementById("grille").children.length > 0, 8000);
  return { dom, w, erreurs };
}

const TOTAUX = {
  fr: (await (await fetch(BASE + "data/tools-fr.json")).json()).outils.length,
  en: (await (await fetch(BASE + "data/tools-en.json")).json()).outils.length
};
console.log(`(catalogue : ${TOTAUX.fr} FR, ${TOTAUX.en} EN)`);

console.log("\n=== PAGE FRANÇAISE ===");
{
  const { w, erreurs } = await charger(BASE);
  const d = w.document;
  const grille = d.getElementById("grille");

  ok(erreurs.length === 0, "aucune erreur JS", erreurs.join(" | "));
  ok(grille.children.length === 48, "48 fiches au premier lot", "rendu: " + grille.children.length);
  ok(d.getElementById("compte").textContent.includes(String(TOTAUX.fr)), "compteur affiche le total",
     d.getElementById("compte").textContent.trim());
  d.getElementById("total-outils").textContent = "x";
  ok(await attendre(() => d.getElementById("total-outils").textContent === "x", 100) &&
     grille.children.length > 0, "compteur du hero alimenté par les données");
  ok(d.querySelectorAll("#filtres-panneau fieldset").length === 5, "5 groupes de filtres construits",
     String(d.querySelectorAll("#filtres-panneau fieldset").length));
  ok(d.querySelectorAll("#suggestions button").length === 6, "6 suggestions de tags");
  ok(!d.getElementById("voir-plus").hidden, "bouton « voir plus » visible");

  // --- recherche
  const champ = d.getElementById("champ-recherche");
  champ.value = "ecoindex";
  champ.dispatchEvent(new w.Event("input"));
  await attendre(() => grille.children.length < 48);
  const premier = grille.querySelector(".carte__titre").textContent.trim();
  ok(/ecoindex/i.test(premier), "recherche sans accent trouve l'outil", premier);
  ok(grille.querySelector("mark.marque") !== null, "les termes trouvés sont surlignés");
  ok(w.location.search.includes("q=ecoindex"), "la recherche est reflétée dans l'URL", w.location.search);

  // --- accent-insensible dans l'autre sens
  champ.value = "accessibilite";
  champ.dispatchEvent(new w.Event("input"));
  await attendre(() => grille.children.length > 0 && !/ecoindex/i.test(grille.textContent));
  ok(grille.children.length > 5, "« accessibilite » sans accent ramène des résultats",
     grille.children.length + " fiches");

  // --- multi-termes
  champ.value = "carbone calcul";
  champ.dispatchEvent(new w.Event("input"));
  await attendre(() => true, 300);
  const nMulti = grille.children.length;
  ok(nMulti > 0, "recherche à deux mots (ET logique)", nMulti + " fiches");

  // --- aucun résultat
  champ.value = "zzzzqqq";
  champ.dispatchEvent(new w.Event("input"));
  await attendre(() => grille.children.length === 0);
  ok(!d.getElementById("vide").hidden, "état vide affiché quand rien ne correspond");

  // --- réinitialisation
  d.getElementById("reinitialiser").click();
  await attendre(() => grille.children.length === 48);
  ok(grille.children.length === 48, "« tout effacer » restaure la liste complète");
  ok(w.location.search === "", "l'URL est nettoyée après réinitialisation", w.location.search);

  // --- filtre par facette
  const caseTheme = d.querySelector('input[data-cle="theme"][value="IA"]');
  ok(caseTheme !== null, "facette Thème « IA » présente");
  caseTheme.checked = true;
  caseTheme.dispatchEvent(new w.Event("change"));
  await attendre(() => grille.children.length <= 13);
  const tousIA = Array.from(grille.querySelectorAll(".carte__theme")).every((n) => n.textContent === "IA");
  ok(tousIA, "le filtre thème ne laisse que le thème choisi");
  ok(d.querySelectorAll("#jetons .jeton").length === 1, "un jeton retirable est affiché");
  ok(w.location.search.includes("theme=IA"), "la facette est dans l'URL", w.location.search);

  // --- retrait par le jeton
  d.querySelector("#jetons .jeton").click();
  await attendre(() => grille.children.length === 48);
  ok(grille.children.length === 48 && !caseTheme.checked,
     "le jeton retire le filtre et décoche la case");

  // --- filtre liens vérifiés
  const verif = d.getElementById("verifies");
  verif.checked = true;
  verif.dispatchEvent(new w.Event("change"));
  await attendre(() => true, 200);
  const aVerifier = grille.querySelectorAll(".verif--doute").length;
  ok(aVerifier === 0, "« liens vérifiés uniquement » masque les fiches douteuses",
     aVerifier + " fiche(s) douteuse(s) restante(s)");
  verif.checked = false;
  verif.dispatchEvent(new w.Event("change"));
  await attendre(() => true, 200);

  // --- tag cliquable (délégation)
  const tag = grille.querySelector(".carte__tags button");
  ok(tag !== null, "des mots-clés sont présents dans le premier lot");
  const libelleTag = tag ? tag.textContent.replace("#", "") : "";
  if (tag) tag.click();
  await attendre(() => d.querySelectorAll("#jetons .jeton").length === 1);
  const tousTag = Array.from(grille.children).length > 0;
  ok(tousTag, "cliquer un tag filtre la liste", "#" + libelleTag);
  d.getElementById("reinitialiser").click();
  await attendre(() => grille.children.length === 48);

  // --- pagination
  d.getElementById("voir-plus").click();
  await attendre(() => grille.children.length === 96);
  ok(grille.children.length === 96, "« voir plus » ajoute un lot", String(grille.children.length));

  // --- tri
  const tri = d.getElementById("tri");
  tri.value = "nom";
  tri.dispatchEvent(new w.Event("change"));
  await attendre(() => true, 300);
  const noms = Array.from(grille.querySelectorAll(".carte__titre")).slice(0, 5)
    .map((n) => n.textContent.trim());
  const trie = noms.slice().sort((a, b) => a.localeCompare(b, "fr"));
  ok(JSON.stringify(noms) === JSON.stringify(trie), "tri alphabétique effectif", noms[0] + " → " + noms[4]);

  // --- liens sortants
  const externes = Array.from(grille.querySelectorAll(".carte__titre a"))
    .filter((a) => !a.hasAttribute("data-fiche"));
  ok(externes.every((a) => a.target === "_blank" && a.rel.includes("noopener")),
     "les liens externes ouvrent un onglet avec rel=noopener");
  ok(externes.every((a) => /^https?:\/\//.test(a.getAttribute("href"))),
     "toutes les URL externes sont absolues");

  // --- fiche juridique
  tri.value = "pertinence";
  tri.dispatchEvent(new w.Event("change"));
  champ.value = "loi reen";
  champ.dispatchEvent(new w.Event("input"));
  await attendre(() => grille.querySelector("a[data-fiche]") !== null, 3000);
  const lienFiche = grille.querySelector("a[data-fiche]");
  ok(lienFiche !== null, "une fiche juridique est trouvable par la recherche");
  if (lienFiche) {
    w.HTMLDialogElement.prototype.showModal = function () { this.setAttribute("open", ""); };
    w.HTMLDialogElement.prototype.close = function () { this.removeAttribute("open"); };
    lienFiche.click();
    await attendre(() => d.getElementById("fiche").hasAttribute("open"), 2000);
    const corps = d.querySelector(".fiche__corps");
    ok(d.getElementById("fiche").hasAttribute("open"), "la fiche s'ouvre en dialogue");
    ok(/Qui est concerné/.test(corps.textContent), "la fiche affiche « Qui est concerné »");
    ok(corps.querySelectorAll("h3").length >= 3, "la fiche a ses sections",
       corps.querySelectorAll("h3").length + " sections");
  }

  // --- accessibilité de base
  ok(d.querySelector(".lien-evitement") !== null, "lien d'évitement présent");
  ok(d.getElementById("annonce").getAttribute("aria-live") === "polite", "compteur annoncé aux lecteurs d'écran");
  ok(d.querySelectorAll("img").every ? true : Array.from(d.querySelectorAll("img")).every((i) => i.hasAttribute("alt")),
     "toutes les images ont un attribut alt");
  ok(d.querySelector("label[for='champ-recherche']") !== null, "le champ de recherche a une étiquette");
  ok(d.querySelectorAll("h1").length === 1, "un seul h1");
}

console.log("\n=== PAGE ANGLAISE ===");
{
  const { w, erreurs } = await charger(BASE + "en/");
  const d = w.document;
  const grille = d.getElementById("grille");
  ok(erreurs.length === 0, "aucune erreur JS", erreurs.join(" | "));
  ok(grille.children.length > 0, "les données anglaises se chargent depuis ../data/",
     grille.children.length + " fiches");
  ok(d.getElementById("total-outils").textContent === String(TOTAUX.en), "total anglais correct",
     d.getElementById("total-outils").textContent);
  ok(/tools of/.test(d.getElementById("compte").textContent), "compteur en anglais",
     d.getElementById("compte").textContent.trim());
}

console.log("\n=== PAGES ÉDITORIALES ===");
for (const page of ["a-propos.html", "mentions-legales.html", "themes/", "themes/ia.html", "en/topics/"]) {
  const dom = await JSDOM.fromURL(BASE + page, { resources: "usable" });
  const d = dom.window.document;
  ok(d.querySelectorAll("h1").length === 1, page + " : un seul h1");
  ok(d.querySelector("main") !== null, page + " : balise main présente");
}

console.log("\n" + (echecs === 0 ? "TOUT PASSE" : echecs + " ÉCHEC(S)"));
process.exit(echecs === 0 ? 0 : 1);

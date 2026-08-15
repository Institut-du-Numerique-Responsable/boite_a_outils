/* Mesure d'audience Matomo, auto-hébergée par l'INR.
   Configuré sans cookie : sous cette forme, la mesure relève de l'exemption
   de consentement CNIL et le site n'a pas besoin de bandeau. Voir
   mentions-legales.html. Toute réactivation des cookies impose de rétablir
   un bandeau de consentement avant le chargement de ce fichier. */

(function () {
  "use strict";

  var _paq = (window._paq = window._paq || []);

  // Aucun cookie déposé : ni identifiant de visiteur, ni cookie de session.
  _paq.push(["disableCookies"]);
  // Respecte le signal « Do Not Track » du navigateur.
  _paq.push(["setDoNotTrack", true]);

  // Paramètres d'URL retirés avant enregistrement : ils identifient la
  // provenance ou la personne, pas la page. Les paramètres du moteur de
  // recherche interne (q, theme, tag…) sont conservés : ce sont eux qui
  // renseignent sur les besoins réels des visiteurs.
  _paq.push(["setExcludedQueryParams", [
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "utm_id",
    "gclid", "gbraid", "wbraid", "fbclid", "msclkid",
    "mc_cid", "mc_eid", "_ga", "igshid", "ref", "referrer"
  ]]);

  _paq.push(["trackPageView"]);
  // Compte les clics sortants : sur un annuaire, c'est la mesure qui compte.
  _paq.push(["enableLinkTracking"]);

  var hote = "https://analytic.institutnr.org:8443/";
  _paq.push(["setTrackerUrl", hote + "matomo.php"]);
  _paq.push(["setSiteId", "16"]);

  var script = document.createElement("script");
  var premier = document.getElementsByTagName("script")[0];
  script.async = true;
  script.src = hote + "matomo.js";
  premier.parentNode.insertBefore(script, premier);
})();

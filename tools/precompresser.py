#!/usr/bin/env python3
"""Pré-compresse les fichiers du site en gzip et brotli.

Compresser à la volée coûte du CPU au serveur à chaque requête. Compresser une
fois à la génération, au niveau maximal, donne des fichiers plus petits pour
moins d'énergie côté serveur — et Apache les sert tels quels.

    python3 tools/precompresser.py

Les fichiers .gz et .br sont régénérés à chaque exécution ; ceux devenus
orphelins sont supprimés.
"""

import gzip
import os
import shutil
import subprocess

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW = os.path.join(RACINE, "www")
EXTENSIONS = (".html", ".css", ".js", ".json", ".svg", ".xml", ".txt")
SEUIL = 1024  # en dessous, la compression ne fait pas gagner de paquet réseau


def main():
    brotli = shutil.which("brotli")
    if not brotli:
        print("brotli absent : seul gzip sera produit "
              "(brew install brotli pour l'activer)")

    compresses = ignores = elagues = 0
    gains = [0, 0]

    for dossier, _, fichiers in os.walk(WWW):
        for nom in fichiers:
            chemin = os.path.join(dossier, nom)

            if nom.endswith((".gz", ".br")):
                origine = chemin[:-3]
                if not os.path.exists(origine):
                    os.remove(chemin)
                    elagues += 1
                continue

            if not nom.endswith(EXTENSIONS):
                continue
            taille = os.path.getsize(chemin)
            if taille < SEUIL:
                ignores += 1
                continue

            with open(chemin, "rb") as source:
                brut = source.read()
            with open(chemin + ".gz", "wb") as sortie:
                sortie.write(gzip.compress(brut, 9, mtime=0))
            if brotli:
                subprocess.run([brotli, "-fq", "11", chemin, "-o", chemin + ".br"],
                               check=True)

            gains[0] += taille
            gains[1] += os.path.getsize(chemin + (".br" if brotli else ".gz"))
            compresses += 1

    print(f"{compresses} fichiers compressés, {ignores} ignorés (< {SEUIL} o), "
          f"{elagues} archives orphelines supprimées")
    if gains[0]:
        print(f"{gains[0] / 1024:.0f} Ko → {gains[1] / 1024:.0f} Ko "
              f"({100 - gains[1] * 100 / gains[0]:.0f} % de moins sur le réseau)")


if __name__ == "__main__":
    main()

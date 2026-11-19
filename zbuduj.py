"""Buduje stronę do publikacji: kopiuje pliki z `strona/` do folderu.

    python3 zbuduj.py [folder]   (domyślnie _site)
"""

import os
import shutil
import sys

TU = os.path.dirname(os.path.abspath(__file__))


def zbuduj(cel, zrodlo=TU):
    """Kopiuje <zrodlo>/strona/ do `cel`; zwraca tekst <cel>/index.html."""
    shutil.copytree(os.path.join(zrodlo, "strona"), cel, dirs_exist_ok=True)
    with open(os.path.join(cel, "index.html"), encoding="utf-8") as fh:
        return fh.read()


if __name__ == "__main__":
    zbuduj(sys.argv[1] if len(sys.argv) > 1 else "_site")

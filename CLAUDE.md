# Pracownia Przykład — strona z listą nowości

Strona statyczna pracowni z zapisem na listę nowości. `zbuduj.py` kopiuje `strona/` do `_site/`, a workflow `.github/workflows/publikacja.yml` publikuje ją na GitHub Pages. Zapis na listę robi `serwer.py`: podaje stronę i przyjmuje `POST /zapisz`, który dodaje kontakt w Resend (`resend.py`, klucz z pliku dostępu `resend`). Na Pages działa sama strona; część serwerowa uruchamia się lokalnie w sprawdzeniu na żywo.

Wygląd strony zmienia się w `strona/styl.css`, treść w `strona/index.html`, zachowanie formularza w `strona/zapis.js`. Bez zmian w `.github/workflows/`, w `cofnij.sh`, w `resend.py` i w `sprawdzenie.py`.

## Verify

`python3 -m unittest discover -s testy -t .`

## Sprawdzenie na żywo

- zapis: `python3 sprawdzenie.py`
- przycisk: `python3 sprawdzenie.py`

## Wdrożenie

- workflow: publikacja.yml
- krok wdrożenia: Publikacja na Pages
- cofnięcie: bash cofnij.sh
- adres: https://lukeblonski.github.io/fabryka-przyklad-naprawa/

## Dostępy

- resend: /home/fabryka/.secrets/fabryka-przyklad-naprawa/resend · host: api.resend.com

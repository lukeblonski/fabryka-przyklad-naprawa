"""Sprawdzenia na żywo strony z listą (## Sprawdzenie na żywo w CLAUDE.md): `zapis` i `przycisk`.

Uruchamia je autopilot ze zmiennymi NA_ZYWO_SCIEZKA (nazwa sprawdzenia), NA_ZYWO_MIEJSCE, NA_ZYWO_ADRES i
NA_ZYWO_WYNIK (oraz PORT przed publikacją):

- przed publikacją (NA_ZYWO_MIEJSCE=przed-publikacja): serwer.py z plików bieżącego folderu (worktree commitu) na
  porcie PORT pod NA_ZYWO_ADRES;
- po publikacji (NA_ZYWO_MIEJSCE=po-publikacji): czeka, aż <NA_ZYWO_ADRES>wersja.txt poda commit HEAD bieżącego
  folderu (najwyżej CZEKANIE sekund), i czyta stronę pod NA_ZYWO_ADRES; część serwerowa (POST /zapisz) działa tylko
  lokalnie, więc `zapis` uruchamia serwer.py na wolnym porcie obok opublikowanej strony.

`zapis`: zapisuje adres testowy zapis-<losowe>@example.com przez POST /zapisz (kontakt w Resend), potem usuwa ten
kontakt w Resend. Gdy Resend odmówi, wynik ma pole `odpowiedz` ({"status", "tresc"}) z odpowiedzią usługi, z której
autopilot ustala rodzaj przyczyny. `przycisk`: czyta styl.css strony i liczy szerokość formularza zapisu (.zapis) na
ekranie szerokości SZEROKOSC px; stała szerokość ponad SZEROKOSC px wypycha przycisk poza ekran.

Wynik zapisuje w pliku NA_ZYWO_WYNIK; kod 0 tylko wtedy, gdy sprawdzenie przeszło.
"""

import json
import os
import re
import secrets
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

SZEROKOSC = 360
CZEKANIE = 600
TRESC_ZNAKI = 500
STAN = {
    "zapis": "kontakt z adresu testowego trafia na listę w Resend i zostaje usunięty",
    "przycisk": "przycisk zapisu mieści się na ekranie szerokości 360 px",
}
REGULA = re.compile(r"([^{}]+)\{([^{}]*)\}")
MEDIA = re.compile(r"@media([^{]*)\{((?:[^{}]*\{[^{}]*\})*[^{}]*)\}")


def pobierz(adres):
    """Tekst spod adresu, z parametrem, który omija pamięć podręczną serwera stron."""
    znak = "&" if "?" in adres else "?"
    zapytanie = urllib.request.Request(f"{adres}{znak}t={time.time_ns()}", headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(zapytanie, timeout=30) as odpowiedz:
        return odpowiedz.read().decode("utf-8", errors="replace")


def wyslij(adres, obiekt):
    """(status, obiekt JSON odpowiedzi) POST `obiekt` pod `adres`."""
    zapytanie = urllib.request.Request(adres, data=json.dumps(obiekt).encode("utf-8"), method="POST",
                                       headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(zapytanie, timeout=60) as odpowiedz:
            return odpowiedz.status, json.loads(odpowiedz.read() or b"{}")
    except urllib.error.HTTPError as blad:
        with blad:
            try:
                return blad.code, json.loads(blad.read() or b"{}")
            except ValueError:
                return blad.code, {}


def czekaj_na_wersje(adres):
    """Czeka, aż pod `adres` działa wersja commitu HEAD bieżącego folderu."""
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    koniec, wersja = time.monotonic() + CZEKANIE, ""
    while True:
        try:
            wersja = pobierz(adres + "wersja.txt").strip()
        except OSError as blad:
            wersja = f"błąd odczytu: {blad}"
        if wersja == commit:
            return
        if time.monotonic() >= koniec:
            raise RuntimeError(f"pod {adres}wersja.txt po {CZEKANIE} s jest {wersja!r}, a nie commit {commit}")
        time.sleep(15)


def uruchom_serwer(port):
    """Serwer zapisu z plików bieżącego folderu na porcie `port` (0: wolny port); (serwer, adres)."""
    sys.path.insert(0, os.getcwd())
    import serwer

    obiekt = serwer.serwer(port, os.getcwd())
    threading.Thread(target=obiekt.serve_forever, daemon=True).start()
    return obiekt, f"http://127.0.0.1:{obiekt.server_address[1]}/"


def piksele(wartosc):
    znalezione = re.fullmatch(r"\s*(\d+(?:\.\d+)?)px\s*(?:!important)?\s*", wartosc or "")
    return float(znalezione.group(1)) if znalezione else None


def deklaracje(css):
    """[(selektor, własność, wartość)] reguł, które działają na ekranie szerokości SZEROKOSC px, w kolejności pliku."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    wynik = []

    def dodaj(tekst):
        for selektory, cialo in REGULA.findall(tekst):
            for selektor in selektory.split(","):
                for deklaracja in cialo.split(";"):
                    nazwa, _, wartosc = deklaracja.partition(":")
                    if wartosc:
                        wynik.append((" ".join(selektor.split()), nazwa.strip().lower(), wartosc.strip()))

    pozycja = 0
    for media in MEDIA.finditer(css):
        dodaj(css[pozycja:media.start()])
        warunek = media.group(1)
        maks = re.search(r"max-width\s*:\s*(\d+)px", warunek)
        mini = re.search(r"min-width\s*:\s*(\d+)px", warunek)
        if (not maks or int(maks.group(1)) >= SZEROKOSC) and (not mini or int(mini.group(1)) <= SZEROKOSC):
            dodaj(media.group(2))
        pozycja = media.end()
    dodaj(css[pozycja:])
    return wynik


def szerokosci_formularza(css):
    """{selektor: szerokość w px na ekranie SZEROKOSC px albo None} reguł formularza zapisu (.zapis)."""
    wlasnosci = {}
    for selektor, nazwa, wartosc in deklaracje(css):
        if ".zapis" in selektor and nazwa in ("width", "min-width", "max-width"):
            wlasnosci.setdefault(selektor, {})[nazwa] = wartosc
    wynik = {}
    for selektor, pola in wlasnosci.items():
        szerokosc = piksele(pola.get("width"))
        maks = pola.get("max-width")
        maks_px = piksele(maks) if maks is not None else None
        if maks is not None and maks_px is None and maks.strip().endswith(("%", "vw")):
            maks_px = SZEROKOSC
        if szerokosc is not None and maks_px is not None:
            szerokosc = min(szerokosc, maks_px)
        mini = piksele(pola.get("min-width"))
        if mini is not None:
            szerokosc = max(szerokosc or 0, mini)
        wynik[selektor] = szerokosc
    return wynik


def przycisk(baza, wynik):
    css = pobierz(baza + "styl.css")
    za_szerokie = {s: w for s, w in szerokosci_formularza(css).items() if w is not None and w > SZEROKOSC}
    if za_szerokie:
        opis = ", ".join(f"{s} ma {w:g} px" for s, w in sorted(za_szerokie.items()))
        wynik.update(wynik="nie przeszło", dowod=f"styl.css pod {baza}: {opis}",
                     powod=f"na ekranie szerokości {SZEROKOSC} px formularz zapisu jest szerszy niż ekran ({opis}), "
                           "więc przycisk zapisu wychodzi poza ekran")
        return 1
    wynik.update(wynik="przeszło", dowod=f"styl.css pod {baza}: formularz zapisu bez stałej szerokości ponad "
                                         f"{SZEROKOSC} px, przycisk mieści się na ekranie")
    return 0


def zapis(serwer_adres, wynik):
    sys.path.insert(0, os.getcwd())
    import resend

    wynik["uslugi"] = [urllib.parse.urlsplit(resend.adres_api(os.getcwd())).hostname or ""]
    email = f"zapis-{secrets.token_hex(4)}@example.com"
    status, obiekt = wyslij(serwer_adres + "zapisz", {"email": email})
    if status != 200 or not obiekt.get("id"):
        wynik.update(wynik="nie przeszło", dowod=f"POST /zapisz z {email}: {status}",
                     powod=f"zapis na listę dał {status}: {obiekt.get('blad') or obiekt}")
        if "status" in obiekt:
            wynik["odpowiedz"] = {"status": obiekt.get("status"), "tresc": str(obiekt.get("tresc"))[:TRESC_ZNAKI]}
        # Kontaktu na pewno nie ma tylko po odrzuceniu adresu albo po odpowiedzi Resend z błędem; inaczej (brak
        # odpowiedzi, Resend 2xx bez identyfikatora) zapis przebiegu nie może mówić, że nic nie powstało.
        resend_status = obiekt.get("status")
        if not (status == 400 or (isinstance(resend_status, int) and not 200 <= resend_status < 300)):
            wynik["sprzatanie"] = {"usuniete": [], "wynik": f"nie da się: kontakt {email} mógł zostać w Resend, "
                                                            f"bo zapis dał {status}"}
        return 1
    status, tekst = resend.usun_kontakt(obiekt["id"], os.getcwd())
    if status is None or not 200 <= status < 300:
        wynik.update(wynik="nie przeszło", dowod=f"kontakt {email} dodany (id {obiekt['id']})",
                     powod=f"usunięcie kontaktu testowego dało {status}", sprzatanie={
                         "usuniete": [], "wynik": f"nie da się: usunięcie kontaktu {email} dało {status}"},
                     odpowiedz={"status": status, "tresc": tekst[:TRESC_ZNAKI]})
        return 1
    wynik.update(wynik="przeszło", dowod=f"kontakt {email} dodany w Resend (id {obiekt['id']}) i usunięty ({status})",
                 sprzatanie={"usuniete": [f"kontakt {email} w Resend"], "wynik": "posprzątane"})
    return 0


def main():
    nazwa = os.environ.get("NA_ZYWO_SCIEZKA", "")
    miejsce = os.environ.get("NA_ZYWO_MIEJSCE", "")
    adres = os.environ.get("NA_ZYWO_ADRES", "")
    plik = os.environ.get("NA_ZYWO_WYNIK", "")
    baza = adres if adres.endswith("/") else adres + "/"
    wynik = {"sciezka": nazwa, "miejsce": miejsce, "adres": adres, "ustawienia": "docelowe", "atrapy": [],
             "uslugi": [], "stan_koncowy": STAN.get(nazwa, ""),
             "sprzatanie": {"usuniete": [], "wynik": "nic nie tworzy"}}
    serwery = []
    try:
        if nazwa not in STAN:
            raise RuntimeError(f"nieznane sprawdzenie {nazwa!r}")
        if miejsce == "przed-publikacja":
            serwery.append(uruchom_serwer(int(os.environ["PORT"]))[0])
            serwer_adres = baza
        elif miejsce == "po-publikacji":
            czekaj_na_wersje(baza)
            if 'id="zapis"' not in pobierz(baza):
                raise RuntimeError(f"strona pod {baza} nie ma formularza zapisu")
            serwer_adres = None
            if nazwa == "zapis":
                obiekt, serwer_adres = uruchom_serwer(0)
                serwery.append(obiekt)
        else:
            raise RuntimeError(f"miejsce {miejsce!r} nie jest obsługiwane")
        kod = zapis(serwer_adres, wynik) if nazwa == "zapis" else przycisk(baza, wynik)
    except (OSError, RuntimeError, KeyError, ValueError, subprocess.CalledProcessError) as blad:
        wynik.update(wynik="nie przeszło", powod=str(blad), dowod="")
        kod = 1
    finally:
        for obiekt in serwery:
            obiekt.shutdown()
            obiekt.server_close()
    if plik:
        with open(plik, "w", encoding="utf-8") as fh:
            json.dump(wynik, fh, ensure_ascii=False)
    print(json.dumps(wynik, ensure_ascii=False))
    return kod


if __name__ == "__main__":
    sys.exit(main())

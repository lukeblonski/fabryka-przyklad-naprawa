"""Klient Resend aplikacji: dodanie i usunięcie kontaktu (https://resend.com/docs/api-reference/contacts).

Klucz czyta z pliku dostępu `resend` z sekcji ## Dostępy w CLAUDE.md (linia `- resend: <ścieżka> · host: <host>`).
Adres API to https://<host>; zmienna RESEND_ADRES podmienia go tylko w przebiegu na sucho laboratorium (lokalna
atrapa usługi), nigdy w aplikacji. Każda funkcja zwraca (status albo None bez połączenia, tekst odpowiedzi).
"""

import json
import os
import urllib.error
import urllib.request

TU = os.path.dirname(os.path.abspath(__file__))
DOSTEP = "resend"
CZAS = 20


def linia_dostepu(katalog=TU):
    """(ścieżka pliku klucza, host) z linii dostępu `resend` w ## Dostępy w CLAUDE.md."""
    with open(os.path.join(katalog, "CLAUDE.md"), encoding="utf-8") as fh:
        tekst = fh.read()
    w_sekcji = False
    for linia in tekst.splitlines():
        if linia.startswith("## "):
            w_sekcji = linia.strip() == "## Dostępy"
            continue
        if w_sekcji and linia.startswith(f"- {DOSTEP}:"):
            sciezka, *pola = linia.split(":", 1)[1].split(" · ")
            host = ""
            for pole in pola:
                nazwa, _, wartosc = pole.partition(":")
                if nazwa.strip() == "host":
                    host = wartosc.strip()
            return sciezka.strip().strip("`"), host
    raise RuntimeError(f"CLAUDE.md nie ma linii dostępu {DOSTEP} w ## Dostępy")


def adres_api(katalog=TU):
    return os.environ.get("RESEND_ADRES") or f"https://{linia_dostepu(katalog)[1]}"


def klucz(katalog=TU):
    with open(linia_dostepu(katalog)[0], encoding="utf-8") as fh:
        return fh.read().strip()


def wywolaj(metoda, sciezka, tresc=None, katalog=TU):
    dane = json.dumps(tresc).encode("utf-8") if tresc is not None else None
    zapytanie = urllib.request.Request(adres_api(katalog) + sciezka, data=dane, method=metoda,
                                       headers={"Authorization": f"Bearer {klucz(katalog)}",
                                                "Content-Type": "application/json",
                                                "User-Agent": "pracownia-przyklad/1.0"})
    try:
        with urllib.request.urlopen(zapytanie, timeout=CZAS) as odpowiedz:
            return odpowiedz.status, odpowiedz.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as blad:
        with blad:
            return blad.code, blad.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError) as blad:
        return None, f"brak połączenia: {getattr(blad, 'reason', blad)}"


def dodaj_kontakt(email, katalog=TU):
    return wywolaj("POST", "/contacts", {"email": email}, katalog)


def usun_kontakt(identyfikator, katalog=TU):
    return wywolaj("DELETE", f"/contacts/{identyfikator}", katalog=katalog)

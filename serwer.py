"""Część serwerowa „zapisz na listę”: podaje pliki strony z `strona/` i przyjmuje POST /zapisz z {"email": …}.

    python3 serwer.py <port>

POST /zapisz dodaje kontakt w Resend (resend.py). Odpowiedź: 200 {"id": <identyfikator kontaktu>} albo 400 przy
złym adresie e-mail, albo 502 {"blad": …, "status": <status Resend albo null>, "tresc": <odpowiedź Resend>}, gdy Resend
odmówił albo nie odpowiedział.
"""

import functools
import http.server
import json
import os
import re
import sys

import resend

TU = os.path.dirname(os.path.abspath(__file__))
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def zapisz(email, katalog=TU):
    """(status HTTP, obiekt odpowiedzi) zapisu adresu `email` na listę."""
    if not isinstance(email, str) or not EMAIL.match(email):
        return 400, {"blad": "zły adres e-mail"}
    status, tekst = resend.dodaj_kontakt(email, katalog)
    if status is not None and 200 <= status < 300:
        try:
            return 200, {"id": json.loads(tekst)["id"]}
        except (ValueError, KeyError, TypeError):
            return 502, {"blad": "Resend nie podał identyfikatora kontaktu", "status": status, "tresc": tekst}
    return 502, {"blad": "Resend nie dodał kontaktu", "status": status, "tresc": tekst}


class Obsluga(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, katalog=TU, **kwargs):
        self.katalog = katalog
        super().__init__(*args, directory=os.path.join(katalog, "strona"), **kwargs)

    def do_POST(self):
        if self.path.rstrip("/") != "/zapisz":
            self.send_error(404)
            return
        try:
            dlugosc = int(self.headers.get("Content-Length") or 0)
            email = json.loads(self.rfile.read(dlugosc) or b"{}").get("email")
        except (ValueError, AttributeError):
            email = None
        status, obiekt = zapisz(email, self.katalog)
        dane = json.dumps(obiekt, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dane)))
        self.end_headers()
        self.wfile.write(dane)

    def log_message(self, format, *args):
        pass


def serwer(port, katalog=TU):
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Obsluga, katalog=katalog))


if __name__ == "__main__":
    serwer(int(sys.argv[1])).serve_forever()

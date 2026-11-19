import os
import tempfile
import unittest

import serwer
import sprawdzenie
import zbuduj


class StronaTest(unittest.TestCase):
    def test_strona_ma_formularz_zapisu_z_przyciskiem(self):
        with tempfile.TemporaryDirectory() as cel:
            tekst = zbuduj.zbuduj(cel)
            self.assertIn('id="zapis"', tekst)
            self.assertIn("<button", tekst)
            for plik in ("index.html", "styl.css", "zapis.js"):
                self.assertTrue(os.path.isfile(os.path.join(cel, plik)), plik)

    def test_zly_adres_nie_idzie_do_resend(self):
        for email in (None, "", "bez-malpy", "a@b", "dwa@@example.com"):
            status, obiekt = serwer.zapisz(email)
            self.assertEqual(status, 400, email)
            self.assertIn("blad", obiekt)

    def test_potwierdzenie_pokazuje_adres(self):
        katalog = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(katalog, "strona", "zapis.js"), encoding="utf-8") as plik:
            tekst = plik.read()
        self.assertIn("`Zapisane: ${email}. Napiszemy, gdy otworzymy drugi warsztat.`", tekst)
        self.assertNotIn('"Zapisane."', tekst)
        self.assertNotIn("innerHTML", tekst)

    def test_formularz_miesci_sie_na_telefonie(self):
        katalog = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(katalog, "strona", "styl.css"), encoding="utf-8") as plik:
            css = plik.read()
        for selektor, szerokosc in sprawdzenie.szerokosci_formularza(css).items():
            if szerokosc is not None:
                self.assertLessEqual(
                    szerokosc,
                    sprawdzenie.SZEROKOSC,
                    f"{selektor} ma {szerokosc} px na ekranie {sprawdzenie.SZEROKOSC} px",
                )


if __name__ == "__main__":
    unittest.main()

---
change_id: naprawa-zapis
title: Potwierdzenie zapisu na listę
status: planned
created: 2026-11-19
updated: 2026-11-19
archived_at: null
---

## Notes

**Problem.** Po zapisie na listę nowości strona pokazuje tylko „Zapisane.”, więc klient nie wie, na jaki adres przyjdzie wiadomość o drugim warsztacie.

**Oczekiwany efekt.** Po udanym zapisie strona pokazuje „Zapisane: <adres e-mail>. Napiszemy, gdy otworzymy drugi warsztat.”; zapis dalej dodaje kontakt w Resend przez `POST /zapisz`.

**Scenariusz człowieka.**
1. Klient wpisuje e-mail, klika „Zapisz mnie” i widzi „Zapisane: <jego adres>. Napiszemy, gdy otworzymy drugi warsztat.”; jego adres trafia na listę w Resend.
   - Sprawdzenie: zapis · stan końcowy: kontakt z adresu testowego trafia na listę w Resend i zostaje usunięty · sprzątanie: posprzątane

**Kogo dotyczy.** Klienci pracowni, którzy zapisują się na listę nowości.

**Ograniczenia.**
- Tekst potwierdzenia zmienia się tylko w `strona/zapis.js`.
- Bez zmian w `serwer.py`, `resend.py`, `sprawdzenie.py`, `.github/workflows/` i `cofnij.sh`.

**Czego nie robimy.** Wysyłki wiadomości do klienta ani zmian w wyglądzie strony.

**Decyzje z góry.**
- Plan nie ma wierszy Manual Verification (bez sekcji „#### Manual Verification:” i bez „#### Manual” w Progress): każde kryterium sukcesu to polecenie. Źródło: człowiek — przykładowy projekt prawdziwego przebiegu.
- Sprawdzenie zapisu dodaje prawdziwy kontakt testowy w Resend kluczem z `## Dostępy` i zaraz go usuwa. Źródło: człowiek — zgoda na testowy kontakt w Resend dla prawdziwego przebiegu.
- Gdy sprawdzenie zapisu nie przechodzi, bo Resend odmawia kluczowi, kod zostaje bez zmian: to przyczyna w ustawieniu, którą naprawia nowy klucz. Źródło: człowiek — przykładowy projekt prawdziwego przebiegu, punkt klucza przy sprawdzeniu.

**Kryteria akceptacji.**

- **C1.** Po udanym zapisie `strona/zapis.js` pokazuje „Zapisane: <adres>. Napiszemy, gdy otworzymy drugi warsztat.”, a testy projektu przechodzą.
  - Sprawdzenie: polecenie `python3 -m unittest discover -s testy -t .`

**Ryzyko.** Niskie. Jeden tekst w skrypcie formularza strony statycznej.

**Zgodność z piramidą.**
- Po co: klient wie, że zapis się udał i na jaki adres.
- Zakłady: wzmacnia kontakt z klientem; nic nie łamie.
- Granice:
  - Instalacja: nic
  - Pieniądze: nic
  - Dane: adres testowy w Resend, usuwany po sprawdzeniu
  - Terminal człowieka: nic
  - Nieodwracalne przed akceptacją: nic
  - Tymczasowe na stałe: nic
  - Odrzucone prostsze warianty: (a) potwierdzenie bez adresu — klient dalej nie wie, gdzie przyjdzie wiadomość; (b) osobna podstrona — za dużo jak na jedno zdanie
- Najbliżej konfliktu: nic.

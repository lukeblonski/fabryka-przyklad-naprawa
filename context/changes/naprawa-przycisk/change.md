---
change_id: naprawa-przycisk
title: Przycisk zapisu na telefonie
status: implementing
created: 2026-11-19
updated: 2026-11-19
archived_at: null
---

## Notes

**Problem.** Właściciel zgłosił: „na telefonie przycisk zapisu wychodzi poza ekran”. Diagnoza (`context/changes/naprawa-przycisk/diagnoza.md`) odtworzyła to na opublikowanej stronie: formularz zapisu ma w `strona/styl.css` stałą szerokość 520 px, a ekran telefonu ma 360 px.

**Oczekiwany efekt.** Na ekranie szerokości 360 px formularz zapisu i przycisk „Zapisz mnie” mieszczą się w całości; na szerszym ekranie strona wygląda jak dotąd.

**Scenariusz człowieka.**
1. Klient otwiera stronę na telefonie (360 px) i widzi cały przycisk „Zapisz mnie” obok pola e-mail albo pod nim.
   - Sprawdzenie: przycisk · stan końcowy: przycisk zapisu mieści się na ekranie szerokości 360 px · sprzątanie: nic nie tworzy

**Kogo dotyczy.** Klienci pracowni, którzy zapisują się na listę z telefonu.

**Ograniczenia.**
- Poprawka tylko w `strona/styl.css`.
- Bez zmian w `serwer.py`, `resend.py`, `sprawdzenie.py`, `.github/workflows/` i `cofnij.sh`.

**Czego nie robimy.** Nowego wyglądu strony, innych kolorów ani zmian w treści.

**Decyzje z góry.**
- Plan nie ma wierszy Manual Verification (bez sekcji „#### Manual Verification:” i bez „#### Manual” w Progress): każde kryterium sukcesu to polecenie. Źródło: człowiek — przykładowy projekt prawdziwego przebiegu.
- Naprawa zgłoszonego błędu w kodzie z diagnozą i dowodem: pierwsza faza planu to test, który odtwarza błąd i nie przechodzi przed poprawką. Źródło: człowiek — akceptacja naprawy w `diagnoza.md` tej zmiany.

**Kryteria akceptacji.**

- **C1.** Formularz zapisu w `strona/styl.css` nie ma szerokości ponad 360 px na ekranie szerokości 360 px, test projektu, który to sprawdza, przechodzi, a pozostałe testy projektu też.
  - Sprawdzenie: polecenie `python3 -m unittest discover -s testy -t .`

**Ryzyko.** Niskie. Jedna reguła w arkuszu stylów strony statycznej.

**Zgodność z piramidą.**
- Po co: klient z telefonem może się zapisać na listę.
- Zakłady: wzmacnia kontakt z klientem; nic nie łamie.
- Granice:
  - Instalacja: nic
  - Pieniądze: nic
  - Dane: nic
  - Terminal człowieka: nic
  - Nieodwracalne przed akceptacją: nic
  - Tymczasowe na stałe: nic
  - Odrzucone prostsze warianty: (a) ukrycie formularza na telefonie — klient z telefonu nie może się zapisać; (b) mniejsza czcionka przycisku — przycisk dalej poza ekranem
- Najbliżej konfliktu: nic.

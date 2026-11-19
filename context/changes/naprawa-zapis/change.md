---
change_id: naprawa-zapis
title: Potwierdzenie zapisu na listę
status: impl_reviewed
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

## Decyzje triage

### context/changes/naprawa-zapis/reviews/plan-review.md

- F1 — Kryterium 1.2 nie sprawdza, że test jest czerwony, i nie działa po commicie (WARNING, Phase 1 — Success Criteria 1.2): AUTO-FIX (normalne używanie): Kryterium 1.2 kończy się kodem `git stash pop`, więc nie dowodzi, że test był czerwony, a po commicie fazy pada albo rusza cudzy stash. Dzieje się to przy zwykłym przeglądzie kodu i sprawdzeniu zamknięcia. · commit 79eee85
- F2 — Test tekstu przechodzi także wtedy, gdy strona pokaże literalne `${email}` (WARNING, Phase 1 — zmiana 1 i kryterium 1.3): AUTO-FIX (normalne używanie): Test i `grep -F` w 1.3 przepuszczają zwykły napis z literalnym `${email}`, więc klient zobaczyłby `${email}` zamiast swojego adresu. Łamie to scenariusz człowieka i C1, a to właśnie ta zmiana ma być chroniona testem. · commit 79eee85
- F3 — Sprawdzenie na żywo `zapis` nie dotyka `zapis.js` (OBSERVATION, Testing Strategy — Integration Tests): AUTO-SKIP (styl): To tylko dopisek w opisie Integration Tests. Plan trafnie opisuje już zakres sprawdzenia na żywo, a uwaga nie dotyczy działania.

### context/changes/naprawa-zapis/reviews/impl-review.md

- brak uwag — nic do triage; zamknięcie: `reviews/impl-review-zamkniecie.md`

## Zatrzymania autopilota

- czas: 2026-11-19 23:00 · krok: przygotowanie-wdrozenia · powód: przyczyna w ustawieniu (sprawdzenie przed publikacją, commit c810293): odpowiedź usługi (krok 1: status 401, treść „{"statusCode":401,"message":"This API key is restricted to only send emails","name":"restricted_api_key"}”); krok 1 (sprawdzenie zapis): polecenie zakończyło się kodem 1; log .autopil… · zrobiono: — · skutek: —

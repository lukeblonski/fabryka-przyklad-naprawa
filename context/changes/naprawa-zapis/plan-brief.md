# Potwierdzenie zapisu na listę — Plan Brief

> Full plan: `context/changes/naprawa-zapis/plan.md`

## What & Why

Po zapisie na listę nowości strona pokazuje tylko „Zapisane.”, więc klient nie wie, na jaki adres przyjdzie wiadomość. Po zmianie strona pokaże „Zapisane: <adres>. Napiszemy, gdy otworzymy drugi warsztat.”.

## Starting Point

`strona/zapis.js` ustawia „Zapisane.” po udanym `POST /zapisz`; zmienna `email` jest już w zasięgu. Żaden test nie sprawdza treści potwierdzenia.

## Desired End State

Klient po zapisie widzi swój adres w zdaniu potwierdzenia; kontakt dalej trafia do Resend. Testy projektu pilnują tekstu.

## Key Decisions Made

| Decision | Choice | Why | Source |
| --- | --- | --- | --- |
| Źródło adresu | zmienna `email` z formularza | serwer nie zwraca adresu i jest zamrożony | Plan |
| Wstawienie adresu | `textContent` z szablonem | brak wstrzyknięcia HTML | Plan |
| Test | asercja tekstowa na `zapis.js` w `testy/test_strona.py` | bez testu C1 przechodzi także przed zmianą; `node` to tylko shim | Plan |
| Sprawdzenie na żywo `zapis` | poza planem, robi je autopilot | brak wierszy Manual; zgoda na kontakt testowy już jest | Plan |

## Scope

**In scope:** tekst sukcesu w `strona/zapis.js`; test w `testy/test_strona.py`.

**Out of scope:** `serwer.py`, `resend.py`, `sprawdzenie.py`, workflow, `cofnij.sh`, wygląd strony, wysyłka wiadomości, komunikat błędu.

## Architecture / Approach

Test najpierw (czerwony), potem zmiana jednej linii w `zapis.js` (zielony).

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Tekst potwierdzenia z adresem | nowe zdanie + test | literówka w brzmieniu (pilnuje test) |

**Prerequisites:** brak. **Estimated effort:** jedna krótka sesja.

## Open Risks & Assumptions

- Adres pokazany jest tym z pola formularza, nie potwierdzonym przez serwer.
- Sprawdzenie `zapis` na żywo może paść z powodu klucza Resend — wtedy kod zostaje bez zmian (decyzja z góry).

## Success Criteria (Summary)

- C1: potwierdzenie z adresem w `zapis.js`, testy przechodzą.

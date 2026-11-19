# Przycisk zapisu na telefonie — Plan Brief

> Full plan: `context/changes/naprawa-przycisk/plan.md`
> Diagnoza: `context/changes/naprawa-przycisk/diagnoza.md`

## What & Why

Właściciel zgłosił: „na telefonie przycisk zapisu wychodzi poza ekran”. Diagnoza na opublikowanej stronie: `.zapis` w `strona/styl.css` ma stałą szerokość 520 px, a ekran telefonu 360 px. Poprawiamy tę jedną regułę, żeby klient z telefonu mógł się zapisać.

## Starting Point

`.zapis` ma `width: 520px`; żaden test nie sprawdza arkusza stylów, więc polecenie z C1 przechodzi dziś mimo błędu. `sprawdzenie.py` ma gotowy czytnik szerokości formularza z CSS.

## Desired End State

Na ekranie 360 px formularz i przycisk „Zapisz mnie” mieszczą się w całości; na szerokim ekranie formularz ma nadal do 520 px. Nowy test pilnuje tego i jest czerwony bez poprawki.

## Key Decisions Made

| Decision | Choice | Why (1 sentence) | Source |
| --- | --- | --- | --- |
| Poprawka | `width: 100%; max-width: 520px` + `min-width: 0` na polu | Mieści się na telefonie, a szeroki ekran wygląda jak dotąd. | Plan |
| Test | czyta `styl.css` przez `sprawdzenie.szerokosci_formularza` | Ta sama logika co sprawdzenie na żywo, bez przeglądarki. | Plan |
| Układ faz | faza 1 sam test (czerwony), faza 2 poprawka | Wymóg naprawy błędu: test odtwarza błąd przed poprawką. | Diagnoza |
| Bramki | żadna nie dotyczy | Pliki to aplikacja, bez płatnych testów i wysyłki danych. | Plan |

## Scope

**In scope:** nowy test w `testy/test_strona.py`; reguły `.zapis` i `.zapis input` w `strona/styl.css`.

**Out of scope:** `serwer.py`, `resend.py`, `sprawdzenie.py`, `.github/workflows/`, `cofnij.sh`, treść i zachowanie strony, nowy wygląd.

## Architecture / Approach

Statyczny arkusz stylów; zmiana jednej reguły. Test w Pythonie analizuje CSS tak jak sprawdzenie `przycisk`.

## Phases at a Glance

| Phase | What it delivers | Key risk |
| --- | --- | --- |
| 1. Test odtwarzający błąd | test czerwony: `python3 -m unittest testy.test_strona.StronaTest.test_formularz_miesci_sie_na_telefonie` | Test musi padać z powodu szerokości, nie importu. |
| 2. Poprawka szerokości | `styl.css` z elastyczną szerokością; test i cały zestaw zielone | Parser CSS w `sprawdzenie.py` nie widzi np. `calc()`; dlatego zostaje `100%`. |

**Prerequisites:** brak.
**Estimated effort:** 2 krótkie fazy w jednej sesji.

## Open Risks & Assumptions

- Test nie uruchamia przeglądarki; opiera się na tym samym parserze CSS co sprawdzenie na żywo, które potwierdza wynik po publikacji.

## Success Criteria (Summary)

- Test z fazy 1 pada przed poprawką i przechodzi po niej.
- `python3 -m unittest discover -s testy -t .` przechodzi.
- Sprawdzenie na żywo `przycisk` po publikacji przechodzi.

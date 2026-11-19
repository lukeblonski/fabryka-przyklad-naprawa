# Przycisk zapisu na telefonie — Implementation Plan

## Overview

Na ekranie szerokości 360 px formularz zapisu ma się mieścić w całości razem z przyciskiem „Zapisz mnie”; na szerszym ekranie strona wygląda jak dotąd. Najpierw test, który odtwarza zgłoszony błąd i jest czerwony (faza 1), potem poprawka jednej reguły w `strona/styl.css` (faza 2).

## Current State Analysis

Naprawa zgłoszonego błędu; przyczyna i zakres z `context/changes/naprawa-przycisk/diagnoza.md` (rodzaj przyczyny: kod, akceptacja właściciela: „Tak, napraw (Recommended)”). Brak `frame.md` i `research.md`; plan oparty na `diagnoza.md`, `change.md` i kodzie.

- `strona/styl.css`: reguła `.zapis` ma `display: flex; gap: 0.5rem; width: 520px;`. Stała szerokość 520 px przekracza ekran 360 px (z `body` `padding: 1rem` zostaje 328 px), więc przycisk wychodzi poza ekran.
- `strona/index.html` ma `<meta name="viewport" content="width=device-width, initial-scale=1">`, więc telefon naprawdę renderuje na 360 px.
- `testy/test_strona.py` nie sprawdza arkusza stylów, więc C1 przechodzi dziś także przy błędzie.
- `sprawdzenie.py` (zamrożony) ma `szerokosci_formularza(css)`: czyta CSS, uwzględnia `@media` i `max-width`/`min-width` i zwraca `{selektor: szerokość w px albo None}` na ekranie 360 px. To ta sama logika, którą autopilot sprawdza opublikowaną stronę (krok `przycisk`). Dziś zwraca `{'.zapis': 520.0}`. Importowanie modułu nie ma skutków ubocznych (`main()` tylko pod `__main__`).

## Desired End State

`strona/styl.css`: formularz `.zapis` nie ma szerokości ponad 360 px na ekranie 360 px (rośnie do 100% dostępnej szerokości, do 520 px na szerokim ekranie). `python3 -m unittest discover -s testy -t .` przechodzi i zawiera test, który odtwarza błąd. Sprawdzenie na żywo `przycisk` (`python3 sprawdzenie.py`, uruchamia autopilot po publikacji) przechodzi.

### Key Discoveries:

- `strona/styl.css`, reguła `.zapis`: jedyne źródło błędu (`width: 520px`).
- `sprawdzenie.py:szerokosci_formularza` — gotowy czytnik CSS, którego test może użyć zamiast pisać własny parser; test i sprawdzenie na żywo mówią wtedy to samo.
- Pola flex: `input` z `flex: 1` ma domyślnie `min-width: auto` (szerokość własna pola), więc w wąskim formularzu może nie chcieć się zwęzić; `min-width: 0` na polu to usuwa.

## Decyzje planu

| Decyzja | Wybór | Uzasadnienie |
|---|---|---|
| Jak poprawić szerokość | `width: 100%; max-width: 520px` zamiast `width: 520px` w `.zapis` | Na telefonie formularz zajmuje dostępne 328 px, na szerokim ekranie zostaje 520 px jak dotąd, więc „na szerszym ekranie strona wygląda jak dotąd” z intencji jest zachowane. |
| Czy dodać `@media` | nie | Jedna reguła z `max-width` załatwia oba rozmiary bez progu, który trzeba by dobierać. |
| Pole e-mail w formularzu | dodać `min-width: 0` do `.zapis input` | Żeby pole mogło się zwęzić we flexie i przycisk został w ekranie; zmiana mieści się w `strona/styl.css` (jedyny dozwolony plik poprawki). |
| Jak testować | test w `testy/test_strona.py` używa `sprawdzenie.szerokosci_formularza` na `strona/styl.css` i wymaga, by żadna szerokość nie była ponad 360 px | Test jest ten sam co sprawdzenie na żywo (bez drugiego parsera) i nie wymaga przeglądarki, której środowisko nie ma. Import z zamrożonego `sprawdzenie.py` tylko czyta; pliku nie zmieniamy. |
| Stała 360 w teście | `sprawdzenie.SZEROKOSC` | Jedno źródło liczby, ta sama co w intencji i w sprawdzeniu na żywo. |
| Wiersze Manual | brak | Decyzja z góry w `change.md`: każde kryterium sukcesu to polecenie. |
| Sprawdzenie na żywo `przycisk` | poza planem, uruchamia je autopilot po publikacji | Wymaga opublikowanej strony; plan nie ma wierszy Manual, a `sprawdzenie.py` jest zamrożony. |
| Bramki z „Kiedy pytać człowieka” | żadna nie dotyczy | Zmieniane pliki to `testy/test_strona.py` i `strona/styl.css` (aplikacja, nie ścieżki z `docs/zgoda-czlowieka.md`); brak płatnych testów fabryki, wysyłki danych i płatnych usług; plan niczego nie wysyła ani nie upublicznia (publikuje autopilot po akceptacji). |

## What We're NOT Doing

- Zmian w `serwer.py`, `resend.py`, `sprawdzenie.py`, `.github/workflows/`, `cofnij.sh`.
- Zmian w `strona/index.html` i `strona/zapis.js` (treść i zachowanie bez zmian).
- Nowego wyglądu strony, innych kolorów, zmian w treści.
- Ukrywania formularza na telefonie ani zmniejszania czcionki przycisku (odrzucone w `change.md`).
- Wierszy Manual Verification.

## Implementation Approach

Dwie fazy wymagane dla naprawy błędu: faza 1 dodaje tylko test i commituje go bez poprawki (test czerwony), faza 2 zmienia `strona/styl.css` i ten sam test przechodzi.

## Phase 1: Test odtwarzający błąd

**Criteria**: C1

**Czerwony test**: `python3 -m unittest testy.test_strona.StronaTest.test_formularz_miesci_sie_na_telefonie`

### Overview

Dodać test, który na obecnym `strona/styl.css` nie przechodzi (formularz ma 520 px na ekranie 360 px). Faza nie zmienia `strona/styl.css`; commit zawiera sam test.

### Changes Required:

#### 1. Test szerokości formularza na telefonie

**File**: `testy/test_strona.py`

**Intent**: Dodać test, który czyta `strona/styl.css` i sprawdza, że żadna reguła formularza zapisu (`.zapis`) nie daje szerokości ponad 360 px na ekranie 360 px. Test odtwarza zgłoszony błąd i nie przechodzi, dopóki `.zapis` ma `width: 520px`.

**Contract**: Nowa metoda `StronaTest.test_formularz_miesci_sie_na_telefonie`. Import `sprawdzenie` (moduł z korzenia repozytorium, jak `serwer` i `zbuduj`). Plik `strona/styl.css` czytany względem katalogu repozytorium (`os.path` od `__file__` testu), UTF-8. Asercja: dla każdej pary `(selektor, szerokość)` z `sprawdzenie.szerokosci_formularza(css)` szerokość jest `None` albo `<= sprawdzenie.SZEROKOSC`; komunikat błędu wymienia selektor i szerokość. Test jest też niezależny od kolejności innych testów. Dodatkowo asercja, że wynik zawiera selektor `.zapis` nie jest potrzebna po poprawce (po poprawce szerokość może być `None`), więc jej nie dodajemy.

### Success Criteria:

#### Automated Verification:

- Pozostałe testy projektu przechodzą bez poprawki: `python3 -m unittest testy.test_strona.StronaTest.test_strona_ma_formularz_zapisu_z_przyciskiem testy.test_strona.StronaTest.test_zly_adres_nie_idzie_do_resend testy.test_strona.StronaTest.test_potwierdzenie_pokazuje_adres`
- Faza 1 nie zmienia arkusza stylów ani zamrożonych plików: `git diff --exit-code 40c5c37 -- strona serwer.py resend.py sprawdzenie.py .github cofnij.sh`

---

## Phase 2: Poprawka szerokości formularza

**Criteria**: C1

### Overview

Zmienić regułę `.zapis` w `strona/styl.css`, tak by formularz mieścił się na ekranie 360 px. Test z fazy 1 przechodzi.

### Changes Required:

#### 1. Szerokość formularza zapisu

**File**: `strona/styl.css`

**Intent**: Zamienić stałą szerokość formularza `.zapis` na szerokość elastyczną: pełna dostępna szerokość do górnej granicy 520 px, żeby na telefonie przycisk został w ekranie, a na szerokim ekranie formularz wyglądał jak dotąd. Pole e-mail ma się móc zwęzić we flexie.

**Contract**: W regule `.zapis` `width: 520px` zastąpić przez `width: 100%` i `max-width: 520px`; w regule `.zapis input` dodać `min-width: 0`. Pozostałe reguły i kolory bez zmian. Po zmianie `sprawdzenie.szerokosci_formularza` zwraca dla `.zapis` `None` (brak stałej szerokości w px).

### Success Criteria:

#### Automated Verification:

- Test odtwarzający błąd przechodzi po poprawce: `python3 -m unittest testy.test_strona.StronaTest.test_formularz_miesci_sie_na_telefonie`
- Wszystkie testy projektu przechodzą (C1): `python3 -m unittest discover -s testy -t .`
- Zamrożone pliki, treść i skrypt strony bez zmian: `git diff --exit-code 40c5c37 -- serwer.py resend.py sprawdzenie.py .github cofnij.sh strona/index.html strona/zapis.js`

---

## Testing Strategy

### Unit Tests:

- Nowy test `test_formularz_miesci_sie_na_telefonie`: szerokość formularza `.zapis` na ekranie 360 px nie jest ponad 360 px; czerwony przed poprawką (520 px), zielony po.
- Istniejące testy (budowa strony, zły adres, potwierdzenie) zostają i przechodzą w obu fazach.

### Integration Tests:

- Sprawdzenie na żywo `przycisk` (`python3 sprawdzenie.py`, uruchamia autopilot po publikacji): `styl.css` opublikowanej strony bez stałej szerokości ponad 360 px. Poza wierszami planu — patrz `## Decyzje planu`.

## Performance Considerations

Brak.

## Migration Notes

Brak danych do migracji. Cofnięcie: `bash cofnij.sh` albo cofnięcie commita fazy 2.

## References

- Intencja: `context/changes/naprawa-przycisk/change.md`
- Diagnoza: `context/changes/naprawa-przycisk/diagnoza.md`
- Kod: `strona/styl.css`, `testy/test_strona.py`, `sprawdzenie.py` (`szerokosci_formularza`)

## Plan Changes

> Append-only. One entry per departure from the plan, written in the same commit as the phase. See `references/progress-format.md`.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Test odtwarzający błąd

#### Automated

- [x] 1.1 Pozostałe testy projektu przechodzą bez poprawki — 20ccd70
- [x] 1.2 Faza 1 nie zmienia arkusza stylów ani zamrożonych plików — 20ccd70

### Phase 2: Poprawka szerokości formularza

#### Automated

- [x] 2.1 Test odtwarzający błąd przechodzi po poprawce — 2298fb7
- [x] 2.2 Wszystkie testy projektu przechodzą (C1) — 2298fb7
- [x] 2.3 Zamrożone pliki, treść i skrypt strony bez zmian — 2298fb7

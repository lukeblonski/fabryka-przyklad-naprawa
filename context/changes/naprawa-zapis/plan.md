# Potwierdzenie zapisu na listę — Implementation Plan

## Overview

Po udanym zapisie strona pokazuje „Zapisane: <adres e-mail>. Napiszemy, gdy otworzymy drugi warsztat.” zamiast samego „Zapisane.”. Zmienia się jeden tekst w `strona/zapis.js` i dochodzi test, który pilnuje tego tekstu. Zapis przez `POST /zapisz` zostaje bez zmian.

## Current State Analysis

`strona/zapis.js` wysyła e-mail do `zapisz` i przy `odpowiedz.ok` ustawia `wynik.textContent = "Zapisane."` (linia z operatorem `?:`). Zmienna `email` (wartość pola formularza) jest już w zasięgu. `testy/test_strona.py` sprawdza tylko budowę strony i odrzucanie złych adresów — treści potwierdzenia nie sprawdza żaden test, więc C1 nie ma teraz czego zweryfikować. Brak `research.md` i `frame.md`; plan oparty na `change.md` i kodzie.

## Desired End State

Po udanym zapisie `#wynik` zawiera „Zapisane: <wpisany adres>. Napiszemy, gdy otworzymy drugi warsztat.”; komunikat błędu bez zmian. `python3 -m unittest discover -s testy -t .` przechodzi i zawiera test tekstu potwierdzenia.

### Key Discoveries:

- `strona/zapis.js`: tekst sukcesu to jedyne miejsce do zmiany; `wynik.textContent` (nie `innerHTML`) sprawia, że wpisany adres nie jest interpretowany jako HTML — to ma zostać.
- `serwer.py` waliduje adres (`EMAIL`) po stronie serwera; strona pokazuje adres z pola formularza, który przeglądarka też waliduje (`type="email"`).
- `node` w środowisku to shim `mise`, więc test nie może zależeć od uruchamiania JS; test czyta plik jako tekst.

## Decyzje planu

| Decyzja | Wybór | Uzasadnienie |
|---|---|---|
| Skąd bierze się adres w komunikacie | zmienna `email` z pola formularza, już istniejąca w `zapis.js` | Intencja każe pokazać adres, który klient wpisał; odpowiedź serwera (`{"id": …}`) adresu nie zwraca, a `serwer.py` jest zamrożony. |
| Jak wstawić adres w tekst | `textContent` z szablonem tekstowym | Zachowuje obecny sposób ustawiania tekstu; adres nie trafia do HTML, więc nie ma wstrzyknięcia. |
| Czy dodać test | tak, w `testy/test_strona.py` | C1 wymaga, by „testy projektu przechodziły” z sensem; bez testu tekstu polecenie z C1 przechodzi także przed zmianą. Test jest poza listą zamrożonych plików z `change.md`. |
| Jak testować tekst | asercja na treści `strona/zapis.js` (bez uruchamiania JS) | Aplikacja nie ma narzędzi do testów JS, a `node` jest tylko shimem. |
| Sprawdzenie na żywo `zapis` | poza planem, uruchamia je autopilot po wdrożeniu | Plan nie ma wierszy Manual, a `sprawdzenie.py` jest zamrożony; wysyłkę kontaktu testowego do Resend człowiek już zatwierdził w `change.md` (Decyzje z góry). |
| Bramki z „Kiedy pytać człowieka” | żadna nie dotyczy | Zmieniane pliki to `strona/zapis.js` i `testy/test_strona.py` (aplikacja, nie ścieżki z `zgoda-czlowieka.md`); brak płatnych testów fabryki; plan sam niczego nie wysyła. |

## What We're NOT Doing

- Zmian w `serwer.py`, `resend.py`, `sprawdzenie.py`, `.github/workflows/`, `cofnij.sh`.
- Zmian w `strona/styl.css` i `strona/index.html` (wygląd i treść strony bez zmian).
- Wysyłki wiadomości do klienta.
- Zmiany komunikatu błędu „Nie udało się zapisać. Spróbuj później.”.
- Wierszy Manual Verification (decyzja z góry z `change.md`).

## Implementation Approach

Najpierw test (czerwony na obecnym kodzie), potem zmiana tekstu w `zapis.js` (zielony). Jedna faza, bo zmiana to jedna linia i jeden test.

## Phase 1: Tekst potwierdzenia z adresem

**Criteria**: C1

### Overview

Test pilnujący nowego tekstu i zmiana tekstu sukcesu w skrypcie formularza.

### Changes Required:

#### 1. Test tekstu potwierdzenia

**File**: `testy/test_strona.py`

**Intent**: Dodać test, który czyta `strona/zapis.js` i sprawdza, że potwierdzenie zawiera adres i pełne zdanie, że stary tekst „Zapisane.” zniknął z gałęzi sukcesu oraz że wynik nadal jest ustawiany przez `textContent`.

**Contract**: Nowa metoda w `StronaTest` (np. `test_potwierdzenie_pokazuje_adres`); asercje na tekście pliku: obecność `Zapisane: ${email}. Napiszemy, gdy otworzymy drugi warsztat.`, brak `"Zapisane."` jako osobnego napisu, brak `innerHTML`. Plik czytany względem katalogu repozytorium (`os.path` od `__file__` testu), w UTF-8.

#### 2. Tekst potwierdzenia w formularzu

**File**: `strona/zapis.js`

**Intent**: W gałęzi sukcesu ustawić `wynik.textContent` na „Zapisane: <adres>. Napiszemy, gdy otworzymy drugi warsztat.” z adresem z `email`; gałąź błędu i `catch` bez zmian.

**Contract**: Wartość `textContent` po `odpowiedz.ok` to szablon tekstowy z `${email}` w miejscu adresu, dokładnie w brzmieniu z `change.md` (C1), z kropką po adresie. Komentarz na górze pliku pozostaje prawdziwy.

### Success Criteria:

#### Automated Verification:

- Testy projektu przechodzą, w tym nowy test potwierdzenia: `python3 -m unittest discover -s testy -t .`
- Nowy test jest czerwony na kodzie sprzed zmiany `zapis.js` i zielony po niej: `git stash push strona/zapis.js && python3 -m unittest discover -s testy -t . ; git stash pop`
- Plik z tekstem zawiera nowe zdanie: `grep -F 'Zapisane: ${email}. Napiszemy, gdy otworzymy drugi warsztat.' strona/zapis.js`
- Zamrożone pliki bez zmian: `git diff --exit-code f395f1f -- serwer.py resend.py sprawdzenie.py .github cofnij.sh strona/styl.css strona/index.html`

---

## Testing Strategy

### Unit Tests:

- Test tekstowy na `strona/zapis.js`: pełne zdanie z `${email}`, brak starego „Zapisane.”, brak `innerHTML`.
- Istniejące testy (budowa strony, zły adres) zostają i przechodzą.

### Integration Tests:

- Sprawdzenie na żywo `zapis` (`python3 sprawdzenie.py`, uruchamia autopilot): kontakt testowy trafia do Resend i jest usuwany. Poza wierszami planu — patrz `## Decyzje planu`.

## Performance Considerations

Brak.

## Migration Notes

Brak danych do migracji. Cofnięcie: `bash cofnij.sh` albo cofnięcie jednego commita ze zmianą `zapis.js`.

## References

- Intencja: `context/changes/naprawa-zapis/change.md`
- Kod: `strona/zapis.js`, `testy/test_strona.py`

## Plan Changes

> Append-only. One entry per departure from the plan, written in the same commit as the phase. See `references/progress-format.md`.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles. See `references/progress-format.md`.

### Phase 1: Tekst potwierdzenia z adresem

#### Automated

- [ ] 1.1 Testy projektu przechodzą, w tym nowy test potwierdzenia
- [ ] 1.2 Nowy test jest czerwony na kodzie sprzed zmiany `zapis.js` i zielony po niej
- [ ] 1.3 Plik z tekstem zawiera nowe zdanie
- [ ] 1.4 Zamrożone pliki bez zmian

<!-- PLAN-REVIEW-REPORT -->
# Plan Review: Potwierdzenie zapisu na listę

- **Plan**: context/changes/naprawa-zapis/plan.md
- **Mode**: Deep (weryfikacja ryzykownych twierdzeń zrobiona w sesji, bez pod-agenta — plan ma jedną fazę i dwa pliki)
- **Date**: 2026-11-19
- **Verdict**: REVISE
- **Findings**: 0 critical, 2 warnings, 1 observation

## Verdicts

| Dimension | Verdict |
|-----------|---------|
| End-State Alignment | PASS |
| Lean Execution | PASS |
| Architectural Fitness | PASS |
| Blind Spots | WARNING |
| Plan Completeness | WARNING |

## Grounding

Grounding: 9/9 paths ✓ (zapis.js, test_strona.py, serwer.py, resend.py, sprawdzenie.py, cofnij.sh, styl.css, index.html, .github/workflows), 3/3 symbols ✓ (`EMAIL` w serwer.py, `wynik.textContent`, `type="email"`), brief↔plan ✓, `validate_change.py --rules 4` exit 0, Progress↔Phase ✓ (4 kryteria = 4 wiersze), blast radius: „Zapisane.” występuje tylko w `strona/zapis.js` (grep po repo; `sprawdzenie.py` nie czyta tekstu strony).

## Findings

### F1 — Kryterium 1.2 nie sprawdza, że test jest czerwony, i nie działa po commicie

- **Severity**: ⚠️ WARNING
- **Dimension**: Plan Completeness
- **Location**: Phase 1 — Success Criteria, Automated Verification (1.2)
- **Detail**: Polecenie `git stash push strona/zapis.js && python3 -m unittest … ; git stash pop` kończy się kodem ostatniego polecenia (`git stash pop`), więc exit 0 nie mówi nic o tym, czy test był czerwony. Po commicie fazy `zapis.js` nie ma zmian, `git stash push` nic nie chowa (exit 0, „No local changes to save”), testy przechodzą na nowym kodzie, a `git stash pop` kończy się kodem 1 („No stash entries found”) albo — gdy w repozytorium leży cudzy stash — zdejmuje go na drzewo. Przegląd kodu i sprawdzenie zamknięcia uruchamiają polecenia po commicie, więc kryterium albo zawsze pada, albo nic nie dowodzi.
- **Fix**: Zastąpić polecenie takim, które nie dotyka drzewa roboczego i kończy się 0 tylko wtedy, gdy test jest czerwony na starym `zapis.js`, zarówno przed, jak i po commicie: `t=$(mktemp -d) && cp -r . "$t/k" && git show f395f1f:strona/zapis.js > "$t/k/strona/zapis.js" && ! (cd "$t/k" && python3 -m unittest discover -s testy -t .)`.
  - Strength: Nie zmienia drzewa ani stashu; wynik wynika z kodu wyjścia; działa w obu momentach (przed i po commicie).
  - Tradeoff: Dłuższe polecenie; kopiuje repozytorium do katalogu tymczasowego (małe).
  - Confidence: HIGH — repozytorium ma kilkanaście plików, a `f395f1f` to commit ze starym `zapis.js`.
  - Blind spot: `cp -r .` kopiuje też `.git` i `.autopilot-local`; przy dużym katalogu autopilota kopia rośnie.
  - Intent: within
- **Decision**: AUTO-FIX (normalne używanie): Kryterium 1.2 kończy się kodem `git stash pop`, więc nie dowodzi, że test był czerwony, a po commicie fazy pada albo rusza cudzy stash. Dzieje się to przy zwykłym przeglądzie kodu i sprawdzeniu zamknięcia.

### F2 — Test tekstu przechodzi także wtedy, gdy strona pokaże literalne `${email}`

- **Severity**: ⚠️ WARNING
- **Dimension**: Blind Spots
- **Location**: Phase 1 — zmiana 1 (test) i kryterium 1.3
- **Detail**: Test (i `grep -F` w 1.3) sprawdza tylko obecność podciągu `Zapisane: ${email}. Napiszemy, gdy otworzymy drugi warsztat.`. Jeśli zdanie trafi do zwykłego napisu w cudzysłowie (`"Zapisane: ${email}. …"`), asercja przechodzi, a klient zobaczy dosłownie `${email}` zamiast swojego adresu. Plan wymaga „szablonu tekstowego”, ale nic tego nie pilnuje, a `node` jest tylko shimem, więc JS nie uruchomi się w teście. To właśnie ta zmiana ma być chroniona testem przy C1.
- **Fix**: W teście i w 1.3 sprawdzać zdanie razem z apostrofami wstecznymi: `` `Zapisane: ${email}. Napiszemy, gdy otworzymy drugi warsztat.` `` (otwierający i zamykający znak są częścią szukanego tekstu).
  - Strength: Test odróżnia szablon od zwykłego napisu bez uruchamiania JS.
  - Tradeoff: Test wiąże się ze składnią szablonu; zmiana na konkatenację wymagałaby zmiany testu.
  - Confidence: HIGH — składnia szablonu to jedyna forma wymagana przez plan („szablon tekstowy z `${email}`”).
  - Blind spot: Błąd składni w innym miejscu pliku test nadal nie wykryje.
  - Intent: within
- **Decision**: AUTO-FIX (normalne używanie): Test i `grep -F` w 1.3 przepuszczają zwykły napis z literalnym `${email}`, więc klient zobaczyłby `${email}` zamiast swojego adresu. Łamie to scenariusz człowieka i C1, a to właśnie ta zmiana ma być chroniona testem.

### F3 — Sprawdzenie na żywo `zapis` nie dotyka `zapis.js`

- **Severity**: ℹ️ OBSERVATION
- **Dimension**: Blind Spots
- **Location**: Testing Strategy — Integration Tests
- **Detail**: `sprawdzenie.py` `zapis` wysyła `POST /zapisz` bezpośrednio i nie ładuje strony ani skryptu, więc krok scenariusza „klient widzi zdanie” jest pokryty tylko testem tekstowym, a sprawdzenie na żywo pokrywa stronę Resend. Plan opisuje je trafnie, ale nie mówi wprost, że nie sprawdza tekstu.
- **Fix**: Dopisać w Integration Tests jedno zdanie, że sprawdzenie `zapis` obejmuje tylko zapis kontaktu, a tekst pilnuje test z fazy 1.
- **Decision**: AUTO-SKIP (styl): To tylko dopisek w opisie Integration Tests. Plan trafnie opisuje już zakres sprawdzenia na żywo, a uwaga nie dotyczy działania.

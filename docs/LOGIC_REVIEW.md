# Kontrola logiky proti původní myšlence projektu

## Co už odpovídá zadání

- UI směřuje k Excel-like pracovní ploše, ne k pouhému dashboardu.
- Každá PEKAT instance může mít vlastní záložku (`Camera_1`, `Camera_2`).
- Existuje `Coordinator` záložka pro slučování více instancí.
- Context JSON je samostatný pravý panel a slouží jako zdroj proměnných.
- Drag-and-drop z Contextu vkládá vazbu `=PV(...)`, ne statickou hodnotu.
- Backend má workbook model: `Workbook`, `Sheet`, `Cell`, `CellBinding`,
  `OutputMapping`, `Recipe`.
- Základní vzorce jsou deterministické a nespouští libovolný Python/JS.
- PEKAT Code bridge má timeout a fallback, takže nemá blokovat FLOW neomezeně.

## Co bylo nutné opravit

- `/api/evaluate` původně používal jen jednoduchý MVP evaluator a ignoroval
  workbook output mapping. Nyní ukládá snapshot, sestaví dostupné contexty,
  vyhodnotí workbook a vrací `context_updates`, `global_updates` i `control`.
- PEKAT bridge původně aplikoval jen `context_updates`. Nyní zapisuje i
  `global_updates` do `context["global_data"]` nebo `context["globalData"]`.
- Logické funkce nyní berou `#MISSING` jako nepravdivou hodnotu, aby chybějící
  kamerová data nemohla omylem projít jako `TRUE`.

## Co zatím zůstává MVP omezení

- Grid není plnohodnotný Excel; nepodporuje kopírování bloků, relativní odkazy,
  formátování buněk ani XLSX import/export.
- Output mapping zatím není plně uživatelsky editovatelný v UI, jen se zobrazuje
  a lze jej spravovat přes API.
- Workbook je zatím in-memory. Pro práci mezi více PC je konfigurace v kódu a
  dokumentaci, ne v persistentní SQLite databázi.
- Chybové stavy jsou dostupné v modelu, ale UI je zatím zobrazuje pouze
  základním obarvením buňky.

## Doporučený další krok

1. Přidat editor output mappingu přímo do UI.
2. Přidat perzistenci workbooku do JSON/SQLite souboru.
3. Přidat validátor workbooku před nasazením do PEKAT FLOW.
4. Rozšířit Code bridge o režimy `sync`, `cached`, `global_data_only`.
5. Přidat test s reálným exportem Context JSON z PEKATu, jakmile bude instance
   dostupná.


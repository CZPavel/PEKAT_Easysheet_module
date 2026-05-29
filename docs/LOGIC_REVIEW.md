# Kontrola logiky proti p?vodn? my?lence projektu

## Co u? odpov?d? zad?n?

- UI sm??uje k Excel-like pracovn? plo?e, ne k pouh?mu dashboardu.
- Ka?d? PEKAT instance m??e m?t vlastn? z?lo?ku (`Camera_1`, `Camera_2`).
- Existuje `Coordinator` z?lo?ka pro slu?ov?n? v?ce instanc?.
- Context JSON je samostatn? prav? panel a slou?? jako zdroj prom?nn?ch.
- Drag-and-drop z Contextu vkl?d? vazbu `=PV(...)`, ne statickou hodnotu.
- Backend m? workbook model: `Workbook`, `Sheet`, `Cell`, `CellBinding`,
  `OutputMapping`, `Recipe`.
- Z?kladn? vzorce jsou deterministick? a nespou?t? libovoln? Python/JS.
- PEKAT Code bridge m? timeout a fallback, tak?e nem? blokovat FLOW neomezen?.

## Co bylo nutn? opravit

- `/api/evaluate` p?vodn? pou??val jen jednoduch? MVP evaluator a ignoroval
  workbook output mapping. Nyn? ukl?d? snapshot, sestav? dostupn? contexty,
  vyhodnot? workbook a vrac? `context_updates`, `global_updates` i `control`.
- PEKAT bridge p?vodn? aplikoval jen `context_updates`. Nyn? zapisuje i
  `global_updates` do `context["global_data"]` nebo `context["globalData"]`.
- Logick? funkce nyn? berou `#MISSING` jako nepravdivou hodnotu, aby chyb?j?c?
  kamerov? data nemohla omylem proj?t jako `TRUE`.

## Co zat?m z?st?v? MVP omezen?

- Grid nen? plnohodnotn? Excel; nepodporuje kop?rov?n? blok?, relativn? odkazy,
  form?tov?n? bun?k ani XLSX import/export.
- Output mapping zat?m nen? pln? u?ivatelsky editovateln? v UI, jen se zobrazuje
  a lze jej spravovat p?es API.
- Workbook je zat?m in-memory. Pro pr?ci mezi v?ce PC je konfigurace v k?du a
  dokumentaci, ne v persistentn? SQLite datab?zi.
- Chybov? stavy jsou dostupn? v modelu, ale UI je zat?m zobrazuje pouze
  z?kladn?m obarven?m bu?ky.

## Doporu?en? dal?? krok

1. P?idat editor output mappingu p??mo do UI.
2. P?idat perzistenci workbooku do JSON/SQLite souboru.
3. P?idat valid?tor workbooku p?ed nasazen?m do PEKAT FLOW.
4. Roz???it Code bridge o re?imy `sync`, `cached`, `global_data_only`.
5. P?idat test s re?ln?m exportem Context JSON z PEKATu, jakmile bude instance
   dostupn?.

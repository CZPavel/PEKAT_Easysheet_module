# Uživatelský návod: PEKAT Easysheet Module

## 1. Co aplikace dělá

PEKAT Easysheet je externí spreadsheetové prostředí nad PEKAT VISION. Uživatel
pracuje s tabulkou podobnou Excelu, ale zdrojová data přicházejí z PEKAT
`Context` a `GlobalData`.

Základní tok:

```text
PEKAT Context JSON -> Context Explorer -> buňka tabulky -> vzorec
    -> output mapping -> context_updates / global_updates -> PEKAT FLOW
```

Aplikace běží i bez PEKATu přes offline simulator.

## 2. Spuštění

Backend:

```powershell
cd C:\PYTHON_test\PEKAT_Easysheet_modul
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

UI:

```powershell
cd C:\PYTHON_test\PEKAT_Easysheet_modul\ui
npm run dev
```

Otevři:

```text
http://127.0.0.1:5173/
```

## 3. První práce bez PEKAT instance

1. Klikni **Tick frame + evaluate**.
2. Backend vygeneruje demo Context pro kamery.
3. Vpravo vyber `Camera_1` nebo `Camera_2`.
4. Přetáhni hodnotu z Context stromu do buňky.
5. Do buňky se vloží například:

```text
=PV("Camera_1.context.measurements.diameter_mm")
```

6. Další klik na **Tick frame + evaluate** tabulku přepočítá.
7. Dole uvidíš `context_updates` a `global_updates`.

## 4. Význam záložek

- `Camera_1`, `Camera_2`: vstupní listy pro jednotlivé PEKAT instance.
- `Coordinator`: slučuje hodnoty z více kamer a dělá master rozhodnutí.
- `Recipes`: tabulkový pohled na receptury a tolerance.
- `Outputs`: přehled, které buňky se zapisují zpět do PEKATu.

## 5. Drag-and-drop z Context JSON

Přetažením položky se nevloží statická hodnota. Vloží se vzorec `PV`, který se
při další evaluaci znovu načte z aktuálního Contextu.

```text
Camera_1.context.result               -> =PV("Camera_1.context.result")
Camera_1.context.measurements.gap_mm  -> =PV("Camera_1.context.measurements.gap_mm")
Camera_1.global_data.recipe.active_id -> =PV("Camera_1.global_data.recipe.active_id")
```

## 6. Podporované vzorce v MVP

```text
=PV("Camera_1.context.result")
=PV_COUNT("Camera_1", "Screw")
=PV_EXISTS("Camera_2", "Defect")
=IF(B2, "OK", "NG")
=AND(Camera_1!B2, Camera_2!B2)
=OR(B2, B3)
=NOT(B2)
=ABS(B4)
=ROUND(B4, 2)
=MIN(B2, B3)
=MAX(B2, B3)
=SUM(B2, B3)
=AVERAGE(B2, B3)
```

Buňky nespouští libovolný Python ani JavaScript.

## 7. Output mapping zpět do PEKATu

Output mapping říká, kam se má hodnota buňky propsat po vyhodnocení:

```text
Coordinator!B2 -> context.spreadsheet.master_result
Coordinator!B3 -> context.spreadsheet.allow_branch_default
Coordinator!B4 -> global_data.spreadsheet.reject_reason
```

PEKAT Code bridge zapisuje:

- `context_updates` přímo do `context`,
- `global_updates` do `context["global_data"]` nebo `context["globalData"]`,
- `control.exit` do `context["exit"]`,
- `control.override_result` do `context["result"]`.

## 8. PEKAT Code tool zapojení

1. Spusť backend.
2. Do PEKAT FLOW vlož Code tool na místo, kde má spreadsheet rozhodovat.
3. Vlož skript `pekat_code_modules/spreadsheet_bridge_sync.py`.
4. Nastav `module_item`:

```json
{
  "backend_url": "http://127.0.0.1:8000",
  "project_id": "Camera_1",
  "mode": "sync",
  "timeout_s": 0.3
}
```

Navazující Conditional Gate může číst:

```text
context.spreadsheet.master_result
context.spreadsheet.allow_branch_default
```


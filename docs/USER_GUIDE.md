# U?ivatelsk? n?vod: PEKAT Easysheet Module

## 1. Co aplikace d?l?

PEKAT Easysheet je extern? spreadsheetov? prost?ed? nad PEKAT VISION.
U?ivatel pracuje s tabulkou podobnou Excelu, ale zdrojov? data nejsou ru?n?
opisovan? ??sla. Data p?ich?zej? z PEKAT `Context` a `GlobalData`.

Z?kladn? tok:

```text
PEKAT Context JSON -> Context Explorer -> bu?ka tabulky -> vzorec
    -> output mapping -> context_updates / global_updates -> PEKAT FLOW
```

Aplikace zat?m b??? i bez PEKATu p?es offline simulator. Simulator vytv???
uk?zkov? Context JSON objekty pro `Camera_1`, `Camera_2` a `Coordinator`.

## 2. Spu?t?n? na tomto PC

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

Otev?i:

```text
http://127.0.0.1:5173/
```

## 3. Prvn? pr?ce bez PEKAT instance

1. Klikni **Tick frame + evaluate**.
2. Backend vygeneruje demo Context pro kamery.
3. Vpravo v panelu **PEKAT Context JSON** vyber `Camera_1` nebo `Camera_2`.
4. P?et?hni vybranou hodnotu z Context stromu do libovoln? bu?ky.
5. Do bu?ky se vlo?? vazba, nap??klad:

```text
=PV("Camera_1.context.measurements.diameter_mm")
```

6. Znovu klikni **Tick frame + evaluate**.
7. Tabulka se p?epo??t? a dole uvid?? `context_updates` a `global_updates`.

## 4. V?znam z?lo?ek

- `Camera_1`, `Camera_2`: vstupn? listy pro jednotliv? PEKAT instance.
- `Coordinator`: slu?uje hodnoty z v?ce kamer a d?l? master rozhodnut?.
- `Recipes`: tabulkov? pohled na receptury a tolerance.
- `Outputs`: p?ehled, kter? bu?ky se maj? zapisovat zp?t do PEKATu.

## 5. Drag-and-drop z Context JSON

P?eta?en?m polo?ky se nevlo?? statick? hodnota. Vlo?? se vzorec `PV`, kter? se
p?i dal?? evaluaci znovu na?te z aktu?ln?ho Contextu.

P??klad:

```text
Camera_1.context.result               -> =PV("Camera_1.context.result")
Camera_1.context.measurements.gap_mm  -> =PV("Camera_1.context.measurements.gap_mm")
Camera_1.global_data.recipe.active_id -> =PV("Camera_1.global_data.recipe.active_id")
```

## 6. Podporovan? vzorce v MVP

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

Z bezpe?nostn?ch d?vod? bu?ky nespou?t? libovoln? Python ani JavaScript.
Nepodporovan? nebo chyb?j?c? hodnota se m? v dal??ch iterac?ch zobrazovat jako
`#MISSING` nebo `#ERROR`.

## 7. Output mapping zp?t do PEKATu

Output mapping ??k?, kam se m? hodnota bu?ky propsat po vyhodnocen?:

```text
Coordinator!B2 -> context.spreadsheet.master_result
Coordinator!B3 -> context.spreadsheet.allow_branch_default
Coordinator!B4 -> global_data.spreadsheet.reject_reason
```

V PEKAT Code toolu bridge p?e?te odpov?? backendu a zap??e:

- `context_updates` p??mo do `context`,
- `global_updates` do `context["global_data"]` nebo `context["globalData"]`,
- `control.exit` do `context["exit"]`,
- `control.override_result` do `context["result"]`.

## 8. PEKAT Code tool zapojen?

1. Spus? backend.
2. Do PEKAT FLOW vlo? Code tool na m?sto, kde m? spreadsheet rozhodovat.
3. Vlo? skript `pekat_code_modules/spreadsheet_bridge_sync.py`.
4. Nastav `module_item`:

```json
{
  "backend_url": "http://127.0.0.1:8000",
  "project_id": "Camera_1",
  "mode": "sync",
  "timeout_s": 0.3
}
```

5. Navazuj?c? Conditional Gate m??e ??st nap??klad:

```text
context.spreadsheet.master_result
context.spreadsheet.allow_branch_default
```

## 9. P?enos na jin? PC

```powershell
git clone https://github.com/CZPavel/PEKAT_Easysheet_module.git
cd PEKAT_Easysheet_module
python -m pip install -e ".[dev]"
cd ui
npm install
```

Pak spus? backend a UI podle kapitoly 2.

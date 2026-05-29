# PEKAT Easysheet Module

Externí spreadsheetové pracovní prostředí pro PEKAT VISION. Projekt má sloužit
jako uživatelsky přívětivá výpočetní a rozhodovací vrstva nad PEKAT
`Context` a `GlobalData`.

Hlavní myšlenka:

```text
PEKAT Context JSON → Context Explorer → buňka tabulky → vzorec
    → output mapping → context_updates / global_updates → PEKAT FLOW
```

PEKAT zůstává hlavní vision runtime. Easysheet nad ním poskytuje tabulkové
prostředí podobné Excelu, Cognex Spreadsheet nebo Keyence Vision Dashboardu.

## Aktuální stav

- FastAPI backend s REST API.
- React/Vite UI se světlým Excel-like rozvržením.
- Offline PEKAT simulator pro běh bez aktivní PEKAT instance.
- Workbook se záložkami `Camera_1`, `Camera_2`, `Coordinator`, `Recipes`,
  `Outputs`.
- Pravý panel s PEKAT Context JSON stromem.
- Drag-and-drop z Contextu do buňky.
- Bezpečný subset vzorců bez spouštění libovolného Pythonu/JavaScriptu.
- Output mapping z vybraných buněk zpět do `context_updates` a
  `global_updates`.
- PEKAT Code bridge s timeoutem a fallbackem.

## Rychlé spuštění

Backend:

```powershell
cd C:\PYTHON_test\PEKAT_Easysheet_modul
python -m pip install -e ".[dev]"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd C:\PYTHON_test\PEKAT_Easysheet_modul\ui
npm install
npm run dev
```

Otevři:

```text
http://127.0.0.1:5173/
```

## První použití bez PEKATu

1. Klikni **Tick frame + evaluate**.
2. Backend vygeneruje demo Context pro `Camera_1`, `Camera_2` a
   `Coordinator`.
3. Vpravo vyber kameru v panelu **PEKAT Context JSON**.
4. Přetáhni položku z Context stromu do buňky.
5. Do buňky se vloží vazba:

```text
=PV("Camera_1.context.measurements.diameter_mm")
```

6. Další klik na **Tick frame + evaluate** tabulku přepočítá.
7. Dole uvidíš `context_updates` a `global_updates`.

## Podporované vzorce v MVP

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

Chybějící hodnota se vyhodnocuje jako `#MISSING`. Nepodporovaný nebo chybný
vzorec se má zobrazovat jako `#ERROR`.

## Napojení do PEKAT Code toolu

1. Spusť backend.
2. Do PEKAT FLOW vlož Code tool na místo, kde má spreadsheet rozhodovat.
3. Vlož skript:

```text
pekat_code_modules/spreadsheet_bridge_sync.py
```

4. V `module_item` nastav například:

```json
{
  "backend_url": "http://127.0.0.1:8000",
  "project_id": "Camera_1",
  "mode": "sync",
  "timeout_s": 0.3
}
```

Bridge odešle snapshot do `/api/evaluate`, převezme odpověď a zapíše:

- `context_updates` přímo do PEKAT `context`,
- `global_updates` do `context["global_data"]` nebo `context["globalData"]`,
- `control.exit` do `context["exit"]`,
- `control.override_result` do `context["result"]`.

Navazující Conditional Gate může číst například:

```text
context.spreadsheet.master_result
context.spreadsheet.allow_branch_default
```

## API přehled

Základní:

- `GET /health`
- `POST /api/projects/register`
- `POST /api/snapshots`
- `GET /api/projects`
- `GET /api/projects/{project_id}/last-snapshot`
- `POST /api/evaluate`

Workbook:

- `GET /api/workbooks/default`
- `PUT /api/workbooks/default`
- `POST /api/workbooks/default/evaluate`
- `POST /api/workbooks/default/bindings`
- `POST /api/workbooks/default/output-mappings`
- `GET /api/context/{project_id}/tree`

## Dokumentace

- `docs/USER_GUIDE.md` – praktický uživatelský návod.
- `docs/FUNCTIONS.md` – vysvětlení funkcí, vzorců a write-back mapování.
- `docs/WORKBOOK_MODEL.md` – datový model workbooku.
- `docs/LOGIC_REVIEW.md` – kontrola souladu aplikace s původní myšlenkou.
- `docs/DEVELOPMENT_ROADMAP.md` – plán dalšího vývoje.
- `docs/api.md` – REST API.
- `docs/pekat_integration.md` – napojení do PEKAT Code toolu.

## Přenos na jiné PC

```powershell
git clone https://github.com/CZPavel/PEKAT_Easysheet_module.git
cd PEKAT_Easysheet_module
python -m pip install -e ".[dev]"
cd ui
npm install
```

Spuštění je stejné jako v části **Rychlé spuštění**.

## Ověření

Backend testy:

```powershell
python -m pytest
```

Frontend build:

```powershell
cd ui
npm run build
```

## Bezpečnostní poznámky

- Buňky nespouští libovolný Python ani JavaScript.
- PEKAT Code bridge má explicitní timeout.
- Při výpadku backendu bridge zapíše diagnostiku do `context["spreadsheet"]`
  a neshodí PEKAT FLOW výjimkou.
- `GlobalData`/`global_data` se aktualizuje přes řízený `global_updates`
  výstup.


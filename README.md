# PEKAT Easysheet Module

MVP skeleton pro extern? spreadsheetovou nadstavbu nad PEKAT VISION 4.0.
C?lem je vytvo?it v?po?etn? a rozhodovac? vrstvu podobnou spreadsheetu,
kter? p?ij?m? snapshoty z PEKAT `Context` / `GlobalData`, vyhodnot? pravidla
a vr?t? bezpe?n? v?stupy zp?t do PEKAT FLOW.

## Co je hotov? v bootstrapu

- FastAPI backend s health endpointem a MVP REST API.
- In-memory storage p?ipraven? na pozd?j?? SQLite persistenci.
- Jednoduch? bezpe?n? formula runtime pro literal/boolean/number hodnoty.
- PEKAT Code bridge `main(context, module_item=None)` s timeoutem a fallbackem.
- Smoke testy backendu a bridge skriptu.
- Dokumentace architektury, API a PEKAT integrace.

## Rychl? spu?t?n?

```powershell
cd C:\PYTHON_test\PEKAT_Easysheet_modul
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
uvicorn backend.app.main:app --reload
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Minim?ln? PEKAT bridge pou?it?

1. Spus? backend: `uvicorn backend.app.main:app --reload`.
2. V PEKAT Code tool vlo? obsah `pekat_code_modules/spreadsheet_bridge_sync.py`.
3. V `module_item` nastav voliteln?:
   - `backend_url`: `http://127.0.0.1:8000`
   - `project_id`: nap?. `Camera_1`
   - `timeout_s`: nap?. `0.3`
4. Bridge zap??e v?sledek do `context["spreadsheet"]`.

## API MVP

- `GET /health`
- `POST /api/projects/register`
- `POST /api/snapshots`
- `GET /api/projects/{project_id}/last-snapshot`
- `POST /api/evaluate`

Podrobnosti jsou v `docs/api.md`.

## Pozn?mka k bezpe?nosti

Prvn? verze nepou?t? libovoln? Python k?d ze vzorc?. Formula runtime je
z?m?rn? omezen? a deterministick?, aby ?el auditovat pro pr?myslov? pou?it?.

## React/Vite offline UI

Aplikace um? b??et bez aktivn? PEKAT instance p?es vestav?n? simulator:

```powershell
uvicorn backend.app.main:app --reload
cd ui
npm install
npm run dev
```

Pot? otev?i `http://127.0.0.1:5173` a pou?ij tla??tka `Start demo`,
`Tick frame` a `Reset`.


## Spreadsheet mapping workspace

Aktu?ln? UI je navr?en? jako extern? Cognex-like spreadsheet nad PEKAT Contextem:

- vlevo hlavn? tabulka se z?lo?kami `Camera_1`, `Camera_2`, `Coordinator`, `Recipes`, `Outputs`,
- vpravo PEKAT Context JSON strom,
- drag-and-drop z Contextu do bu?ky vlo?? `=PV(...)`,
- output mappings mapuj? vybran? bu?ky zp?t do `context_updates` a `global_updates`.

### P?enos na jin? PC

```powershell
git clone https://github.com/CZPavel/PEKAT_Easysheet_module.git
cd PEKAT_Easysheet_module
python -m pip install -e ".[dev]"
cd ui
npm install
```


## Dokumentace

- `docs/USER_GUIDE.md` - praktick? u?ivatelsk? n?vod.
- `docs/FUNCTIONS.md` - vysv?tlen? funkc?, vzorc? a write-back mapov?n?.
- `docs/WORKBOOK_MODEL.md` - datov? model workbooku.
- `docs/LOGIC_REVIEW.md` - kontrola souladu aplikace s p?vodn? my?lenkou.
- `docs/DEVELOPMENT_ROADMAP.md` - dal?? pl?n v?voje.

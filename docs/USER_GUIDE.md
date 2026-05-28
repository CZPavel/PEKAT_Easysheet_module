# User guide

## Lok?ln? ov??en?

```powershell
python -m pip install -e ".[dev]"
python -m pytest
uvicorn backend.app.main:app --reload
```

## PEKAT Code tool

1. Otev?i PEKAT projekt.
2. P?idej Code tool na m?sto, kde chce? vyhodnotit Easysheet logiku.
3. Vlo? obsah `pekat_code_modules/spreadsheet_bridge_sync.py`.
4. Nastav `backend_url`, `project_id` a `timeout_s`.
5. Navazuj?c? Conditional Gate ?te `context.spreadsheet.outputs.master_result`.


## Spreadsheet workflow

1. Spus? backend a UI.
2. Klikni `Tick frame + evaluate`, aby vznikl demo Context.
3. Vpravo vyber `Camera_1` nebo `Camera_2`.
4. P?et?hni polo?ku Context JSON do bu?ky.
5. Bu?ka dostane `=PV(...)` vzorec a m??e b?t namapov?na zp?t p?es output mapping.

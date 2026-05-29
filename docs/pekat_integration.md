# PEKAT integrace

## Code tool bridge

Soubor `pekat_code_modules/spreadsheet_bridge_sync.py` je navr?en pro vlo?en?
do PEKAT Code toolu. Hlavn? entrypoint je:

```python
def main(context, module_item=None):
    ...
```

Bridge:

- ?te `context` p?es bezpe?n? guardy,
- nem?n? typy kl??? `image`, `detectedRectangles`, `heatmaps`, pokud existuj?,
- pos?l? metadata obrazu m?sto cel?ho NumPy pole,
- nastavuje `context["spreadsheet"]`,
- pou?ije `context["exit"] = True` pouze pokud to explicitn? vr?t? backend.

## Doporu?en? nastaven? module_item

```json
{
  "backend_url": "http://127.0.0.1:8000",
  "project_id": "Camera_1",
  "mode": "sync",
  "timeout_s": 0.3
}
```

## V?stup do Conditional Gate

Typick? hodnota pro ?ten? v navazuj?c? logice:

```text
context.spreadsheet.outputs.allow_branch_default
context.spreadsheet.outputs.master_result
```

## SDK pozn?mka

PEKAT Vision SDK dr??me jako volitelnou z?vislost `.[pekat]`. Backend MVP
nevy?aduje SDK, proto?e prim?rn? integra?n? bod je Code tool volaj?c? REST API.


## Write-back mapping

Vybran? bu?ky workbooku se mapuj? na `context.spreadsheet.*`, `global_data.*` nebo `control.*`. PEKAT Code bridge pak vr?cen? `context_updates` zap??e do `context`, `global_updates` do perzistentn?ho stavu a `control.exit`/`control.override_result` pou?ije pro FLOW.

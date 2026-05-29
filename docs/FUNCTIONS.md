# Vysvětlení funkcí aplikace

## PEKAT Context Explorer

Pravý panel zobrazuje poslední známý Context JSON pro vybranou PEKAT instanci.
V offline režimu ho generuje simulator. V produkčním režimu ho bude plnit Code
bridge nebo budoucí ingest endpoint.

## Spreadsheet grid

Hlavní plocha je workbook se záložkami. Buňka může obsahovat:

- text nebo číslo,
- boolean hodnotu `TRUE`/`FALSE`,
- vzorec začínající `=`,
- binding na PEKAT Context přes `PV(...)`.

## Binding funkce

### `PV(path)`

Načte hodnotu z context stromu.

```text
=PV("Camera_1.context.result")
=PV("Camera_1.context.measurements.diameter_mm")
```

### `PV_COUNT(project_id, label)`

Spočítá objekty v `detectedRectangles` podle labelu.

```text
=PV_COUNT("Camera_1", "Screw")
```

### `PV_EXISTS(project_id, label)`

Vrátí `TRUE`, pokud existuje alespoň jeden objekt daného labelu.

```text
=PV_EXISTS("Camera_2", "Defect")
```

## Logické funkce

```text
=IF(condition, value_if_true, value_if_false)
=AND(A1, B1)
=OR(A1, B1)
=NOT(A1)
```

## Matematické funkce

```text
=ABS(A1)
=ROUND(A1, 2)
=MIN(A1, B1)
=MAX(A1, B1)
=SUM(A1, B1)
=AVERAGE(A1, B1)
```

## Odkazy na buňky

Aktuální MVP umí jednoduché odkazy v rámci listu a základní odkazy mezi listy:

```text
=B2
=AND(Camera_1!B2, Camera_2!B2)
```

## Write-back funkce

Výsledná buňka se přes `OutputMapping` zapíše do odpovědi backendu:

```json
{
  "context_updates": {
    "spreadsheet": {
      "master_result": true
    }
  },
  "global_updates": {
    "spreadsheet": {
      "reject_reason": "OK"
    }
  }
}
```

PEKAT Code bridge tyto hodnoty promítne zpět do `context` a `global_data`.


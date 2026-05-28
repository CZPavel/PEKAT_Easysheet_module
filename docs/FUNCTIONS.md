# Vysv?tlen? funkc? aplikace

## PEKAT Context Explorer

Prav? panel zobrazuje posledn? zn?m? Context JSON pro vybranou PEKAT instanci.
V offline re?imu ho generuje simulator. V produk?n?m re?imu ho bude plnit Code
bridge nebo HTTP ingest endpoint.

## Spreadsheet grid

Hlavn? plocha je workbook se z?lo?kami. Bu?ka m??e obsahovat:

- text nebo ??slo,
- boolean hodnotu `TRUE`/`FALSE`,
- vzorec za??naj?c? `=`,
- binding na PEKAT Context p?es `PV(...)`.

## Binding funkce

### `PV(path)`

Na?te hodnotu z context stromu.

```text
=PV("Camera_1.context.result")
=PV("Camera_1.context.measurements.diameter_mm")
```

### `PV_COUNT(project_id, label)`

Spo??t? objekty v `detectedRectangles` podle labelu.

```text
=PV_COUNT("Camera_1", "Screw")
```

### `PV_EXISTS(project_id, label)`

Vr?t? `TRUE`, pokud existuje alespo? jeden objekt dan?ho labelu.

```text
=PV_EXISTS("Camera_2", "Defect")
```

## Logick? funkce

```text
=IF(condition, value_if_true, value_if_false)
=AND(A1, B1)
=OR(A1, B1)
=NOT(A1)
```

## Matematick? funkce

```text
=ABS(A1)
=ROUND(A1, 2)
=MIN(A1, B1)
=MAX(A1, B1)
=SUM(A1, B1)
=AVERAGE(A1, B1)
```

## Odkazy na bu?ky

Aktu?ln? MVP um? jednoduch? odkazy v r?mci listu a z?kladn? odkazy mezi listy:

```text
=B2
=AND(Camera_1!B2, Camera_2!B2)
```

## Write-back funkce

V?sledn? bu?ka se p?es `OutputMapping` zap??e do odpov?di backendu:

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

PEKAT Code bridge tyto hodnoty prom?tne zp?t do `context` a `global_data`.

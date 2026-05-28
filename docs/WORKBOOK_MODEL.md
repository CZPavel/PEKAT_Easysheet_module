# Workbook model

PEKAT Easysheet pou??v? JSON workbook p?ipraven? na pozd?j?? SQLite ulo?en?.

## Entity

- `Workbook`: cel? projekt tabulek, binding?, v?stup? a receptur.
- `Sheet`: z?lo?ka pro jednu PEKAT instanci nebo koordina?n? logiku.
- `Cell`: adresa, raw hodnota/vzorec, posledn? hodnota a status.
- `CellBinding`: mapov?n? `Context/GlobalData -> bu?ka`.
- `OutputMapping`: mapov?n? `bu?ka -> Context/GlobalData/control`.
- `Recipe`: verzovan? parametry receptury.

## Binding syntax

```text
=PV("Camera_1.context.result")
=PV("Camera_1.context.measurements.diameter_mm")
=PV_COUNT("Camera_1", "Screw")
=PV_EXISTS("Camera_2", "Defect")
```

## Error states

- `#MISSING`: hodnota v Context JSON neexistuje.
- `#ERROR`: chyba vzorce nebo nepodporovan? funkce.

Runtime nesm? spou?t?t libovoln? Python/JavaScript z bu?ky.

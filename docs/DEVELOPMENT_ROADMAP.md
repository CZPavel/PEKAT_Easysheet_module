# Development roadmap

## F?ze 1: Spreadsheet mapping MVP

- Sv?tl? Excel-like UI.
- Z?lo?ky `Camera_1`, `Camera_2`, `Coordinator`, `Recipes`, `Outputs`.
- Drag-and-drop z Context JSON do bu?ky.
- Z?kladn? vzorce a output mapping zp?t do Context/GlobalData.

## F?ze 2: Stabiln? runtime

- Persistovat workbook do SQLite.
- P?idat audit zm?n bun?k, binding? a receptur.
- P?idat validaci p?ed nasazen?m do PEKAT FLOW.

## F?ze 3: PEKAT integration hardening

- Roz???it Code bridge o re?imy `sync`, `cached`, `global_data_only`.
- Doplnit watchdog, stale frame detekci a jasn? timeout strategie.
- P?ipravit Conditional Gate demo projekt.

## F?ze 4: Multikamera

- Registr PEKAT instanc?.
- Coordinator sheet pro slu?ov?n? v?sledk?.
- Cross-Pekat/GlobalData write-back strategie.

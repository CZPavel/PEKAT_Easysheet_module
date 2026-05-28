# Architektura PEKAT Easysheet Module

## C?l

Aplikace tvo?? extern? spreadsheetovou rozhodovac? vrstvu pro PEKAT VISION 4.0.
PEKAT Code tool po?le snapshot aktu?ln?ho `Context`/`GlobalData`, backend jej
vyhodnot? a vr?t? stav do `context["spreadsheet"]` pro Conditional Gate nebo
navazuj?c? logiku.

## Komponenty MVP

1. **PEKAT Code bridge**
   - b??? uvnit? PEKAT Code toolu,
   - pou??v? `main(context, module_item=None)`,
   - komunikuje p?es HTTP s kr?tk?m timeoutem,
   - p?i chyb? zapisuje bezpe?n? fallback.

2. **FastAPI backend**
   - p?ij?m? registrace projekt? a snapshoty,
   - dr?? posledn? snapshot v in-memory store,
   - vrac? deterministick? master v?sledek.

3. **Formula runtime**
   - v MVP pouze bezpe?n? literal/boolean/number vyhodnocen?,
   - bez `eval()` a bez spou?t?n? u?ivatelsk?ho Pythonu,
   - p?ipraveno na budouc? AST/DSL.

4. **Budouc? UI**
   - React/Vite dashboard s tabulkou, Context Explorerem, recepturami,
     watch panelem a auditn?m zobrazen?m,
   - zat?m pouze n?vrh, bez implementace.

## Datov? tok

```text
PEKAT FLOW -> Code bridge -> POST /api/evaluate -> Evaluator
    ^                                                |
    |                                                v
context["spreadsheet"] <- context_updates/global_updates
```

## Provozn? princip

- Synchronn? re?im pou??v? odpov?? backendu pro aktu?ln? frame.
- Cached re?im se dopln? v dal?? f?zi p?es posledn? validn? v?sledek.
- Timeout mus? b?t kr?tk?, typicky 0.2 a? 0.5 s podle taktu linky.


## Spreadsheet mapping workspace

Aktu?ln? sm?r UI je Excel-like tabulka jako hlavn? pracovn? plocha a PEKAT Context JSON jako prav? zdrojov? panel. Drag-and-drop vytv??? `=PV(...)` bindingy a output mapping zapisuje vybran? bu?ky zp?t do `context_updates` nebo `global_updates`.

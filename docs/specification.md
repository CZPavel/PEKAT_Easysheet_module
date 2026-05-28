# Návrh projektu: externí spreadsheetová nadstavba pro PEKAT VISION 4.0

**Pracovní název:** PEKAT Spreadsheet Bridge  
**Typ dokumentu:** návrhová a technická specifikace pro založení projektu  
**Datum:** 2026-05-28  
**Cílové prostředí:** PEKAT VISION 4.0, Windows PC / MX-G2000 / případně PEKAT runtime na podporovaných zařízeních  
**Předpokládaný další krok:** založení GitHub repozitáře a vývoj ve VS Code s agentem Codex

---

## 1. Shrnutí myšlenky

Cílem projektu je vytvořit externí aplikaci, která bude fungovat jako tabulkové, uživatelsky přívětivé programovací a rozhodovací prostředí pro PEKAT VISION. Aplikace bude připomínat spreadsheet / Excel: buňky, vzorce, záložky, receptury, odkazy mezi hodnotami a podmínkové výpočty.

Rozdíl proti běžnému Excelu je v tom, že zdrojová data do buněk budou pocházet z aktuálního stavu PEKAT projektu:

- z `Context` aktuálního snímku,
- z `GlobalData` daného projektu,
- z výsledků detekcí, měření, OCR, klasifikace a dalších toolů,
- z jiných běžících PEKAT instancí v multikamerové aplikaci,
- z receptur a uživatelských konfiguračních tabulek.

Tabulka nebude sloužit jen pro zobrazení nebo logování. Bude tvořit výpočetní a rozhodovací vrstvu, jejíž výstupy budou moci ovlivňovat další chod PEKAT FLOW:

- pokračování / ukončení větve,
- přepsání nebo doplnění výsledku OK/NG,
- nastavení hodnot do `Context`,
- nastavení hodnot do `GlobalData`,
- koordinaci více projektů PEKAT,
- přípravu výstupů pro PLC, MES, operátorský panel nebo vyšší nadřazený systém.

Projekt je koncepčně inspirovaný:

- tabulkovým programovacím prostředím Cognex In-Sight Spreadsheet,
- uživatelským dashboardovým přístupem Keyence VS / Vision Dashboard,
- novými prvky PEKAT VISION 4.0: `GlobalData`, `Conditional Gate`, `Cross-Pekat Communication`, samostatné Output tooly a rozšířený `Code` tool.

---

## 2. Základní předpoklady

### 2.1 Typické taktování

Pro multikamerové aplikace se nepředpokládají extrémně vysoké frameraty. Typický rozsah je přibližně:

```text
4 až 6 FPS na kameru
```

To umožňuje realisticky uvažovat i o externí synchronní nebo polo-synchronní komunikaci, pokud bude mít jasné timeouty a fallback režimy.

### 2.2 Režimy práce s aktuálností dat

Aplikace musí od začátku počítat se dvěma režimy:

1. **Synchronní režim – čekat na aktuální výpočet**
   - PEKAT pošle data do spreadsheet runtime.
   - Čeká na odpověď.
   - Odpověď se použije pro aktuální snímek a aktuální místo ve FLOW.
   - Vhodné pro rozhodnutí, která musí přesně odpovídat aktuálnímu snímku.

2. **Asynchronní / cached režim – použít poslední platnou hodnotu**
   - PEKAT odešle nový snapshot.
   - Nečeká na kompletní nový přepočet.
   - Přečte poslední validní hodnotu z cache / GlobalData.
   - Vhodné pro multikamerovou koordinaci, pomalejší receptury a stavové řízení.

Volba režimu bude později dostupná v nastavení aplikace, ideálně samostatně pro každou vazbu nebo výstupní skupinu.

---

## 3. Principy PEKAT VISION, o které se projekt opírá

### 3.1 Context

`Context` je aplikační proměnná, která prochází jednotlivými tooly během zpracování jednoho snímku. V PEKAT 4.0 je scope Contextu omezen na jednu evaluaci: každý nový snímek začíná s čerstvým Contextem.

Typické položky:

```python
context["image"]
context["detectedRectangles"]
context["result"]
context["exit"]
context["heatmaps"]
context["operatorInput"]
context["completeTime"]
```

Důležité vlastnosti:

- `context["image"]` je obraz jako NumPy pole.
- `context["detectedRectangles"]` obsahuje nalezené objekty.
- `context["result"]` reprezentuje OK/NG výsledek.
- `context["exit"] = True` ukončí další zpracování aktuální větve.
- Uživatel může do Contextu přidávat vlastní atributy.
- Při úpravách se nesmí měnit typová struktura existujících objektů.

V projektu bude Context sloužit jako hlavní per-snímek zdroj dat pro spreadsheet:

```text
context.result
context.detectedRectangles
context.heatmaps
context.operatorInput
context.completeTime
context.custom_measurements
context.spreadsheet
```

### 3.2 GlobalData

PEKAT 4.0 zavádí `GlobalData` jako projektový key/value store, který přetrvává mezi evaluacemi po dobu běhu projektu. To je zásadní pro tento projekt.

Vhodné použití:

- receptura aktivní v projektu,
- počítadla,
- poslední platné hodnoty ze spreadsheetu,
- stav synchronizace více kamer,
- kalibrační příznaky,
- historie posledních N výsledků,
- handshake stavy mezi projekty,
- řízení Conditional Gate podle dlouhodobého stavu.

Navržené namespace v GlobalData:

```python
context["global_data"]["spreadsheet"] = {
    "last_update_ts": "...",
    "last_frame_id": "...",
    "mode": "sync" | "cached",
    "result": True,
    "reason": "OK",
    "recipe_id": "A",
    "sheet_version": "1.0.0",
    "outputs": {
        "allow_branch_a": True,
        "allow_branch_b": False,
        "master_result": True
    }
}
```

### 3.3 Code tool

`Code` tool je hlavní integrační bod. Umožňuje Pythonem upravovat Context, pracovat s obrazem a hodnotami, volat externí služby a v PEKAT 4.0 také využívat komunikaci mezi projekty.

V tomto projektu bude existovat několik typů Code bridge skriptů:

1. **Snapshot exporter**
   - vezme vybrané položky z Contextu a GlobalData,
   - normalizuje je,
   - odešle do externího backendu.

2. **Spreadsheet evaluator bridge**
   - odešle snapshot,
   - podle nastavení čeká / nečeká na odpověď,
   - zapíše odpověď do Contextu a/nebo GlobalData.

3. **GlobalData synchronizer**
   - čte stav z externí aplikace nebo jiných PEKAT instancí,
   - zapisuje ho do lokálního GlobalData.

4. **Cross-Pekat coordinator**
   - používá `pekat_communication.PEKAT`,
   - čte/zapisuje GlobalData mezi více PEKAT instancemi.

5. **Fallback / watchdog script**
   - hlídá dostupnost backendu,
   - při timeoutu nastaví bezpečný stav,
   - případně ukončí větev pomocí `context["exit"] = True`.

### 3.4 Conditional Gate

`Conditional Gate` v PEKAT 4.0 je přirozený nástroj pro čtení výsledků ze spreadsheetu. Na rozdíl od původního jednoduchého filtru umí číst Context i GlobalData a ukončit zpracování v konkrétním místě FLOW.

Navržený princip:

```text
Spreadsheet spočítá výstupní buňku:
  allow_branch_measure_detail = TRUE

Code bridge zapíše:
  context["spreadsheet"]["allow_branch_measure_detail"] = True

Conditional Gate přečte:
  context.spreadsheet.allow_branch_measure_detail

Pokud je False:
  větev se ukončí
```

Pro stavové nebo multikamerové řízení:

```text
Spreadsheet Coordinator spočítá:
  master_allow_camera_2 = TRUE

Zápis do GlobalData:
  global_data.spreadsheet.outputs.master_allow_camera_2 = TRUE

Conditional Gate v projektu Camera_2:
  čte GlobalData a podle toho pustí nebo zastaví větev
```

### 3.5 Cross-Pekat Communication

PEKAT 4.0 poskytuje knihovnu `pekat_communication`, která umožňuje sdílet data mezi běžícími PEKAT instancemi.

Základní princip:

```python
from pekat_communication import PEKAT

PEKAT.add_client_to_pekat("192.168.0.10", 8000, "Camera1")
value = PEKAT.get_global_data("Camera1", "some_key")
PEKAT.update_global_data("Camera1", {"some_key": "new_value"})
```

Pro tento projekt je Cross-Pekat komunikace ideální pro:

- multikamerovou koordinaci,
- přenos stavu mezi projekty,
- zápis výsledků ze společné záložky `Coordinator`,
- synchronizaci receptur,
- sdílení master OK/NG,
- nastavování příznaků pro Conditional Gate v jednotlivých instancích.

Důležité rozhodnutí:

- synchronní `update_global_data()` použít tam, kde je nutné potvrzení,
- asynchronní `update_global_data_async()` použít tam, kde stačí fronta a prioritou je výkon.

### 3.6 HTTP Output a TCP Output

PEKAT 4.0 rozdělil dříve společný Output tool na samostatné protokolové tooly.

`HTTP Output` je vhodný pro finální odeslání výsledků do externího backendu, MES, ERP nebo dashboardu. Umí poslat celý Context nebo jen subContext. Nevýhoda: běží až na konci flow a jen v production režimu, takže není vhodný jako hlavní inline rozhodovací mechanismus uvnitř FLOW.

`TCP Output` je vhodný pro jednoduché legacy systémy a raw TCP servery. Je potřeba hlídat timeout, protože TCP Output čeká na odpověď serveru a bez timeoutu může flow zablokovat.

Doporučení:

- pro inline ovlivnění FLOW používat hlavně `Code` bridge + `Conditional Gate`,
- pro finální výstupy, logování a dashboard používat `HTTP Output`,
- pro starší linkové systémy použít `TCP Output`, ale vždy s timeoutem,
- pro multikamerové stavové sdílení preferovat `GlobalData` a Cross-Pekat.

### 3.7 Excel Writer

PEKAT 4.0 obsahuje `Excel Writer`, ale ten je vhodné chápat jako výstupní logger, ne jako výpočetní spreadsheetový runtime.

Umí zapisovat detekce, OCR a vybrané atributy z Contextu do Excel souboru. Pro tento projekt může být užitečný pro audit a export, ale nemůže nahradit hlavní tabulkový výpočetní engine.

---

## 4. Cílová architektura

### 4.1 Přehled

```text
+------------------+          +-----------------------------+
| PEKAT Camera 1   |          |                             |
| Flow + Code      | <------> |                             |
| GlobalData       |          |                             |
+------------------+          |                             |
                              |                             |
+------------------+          |  PEKAT Spreadsheet Bridge   |
| PEKAT Camera 2   |          |  Backend + Formula Runtime  |
| Flow + Code      | <------> |                             |
| GlobalData       |          |                             |
+------------------+          |                             |
                              |                             |
+------------------+          |                             |
| PEKAT Camera N   |          |                             |
| Flow + Code      | <------> |                             |
| GlobalData       |          +--------------+--------------+
+------------------+                         |
                                             |
                                  +----------v----------+
                                  | Spreadsheet UI      |
                                  | Context Explorer    |
                                  | Recipe Editor       |
                                  | Coordinator Sheet   |
                                  +---------------------+
```

### 4.2 Hlavní komponenty

#### 4.2.1 Spreadsheet UI

Uživatelské rozhraní podobné Excelu:

- buňky,
- vzorce,
- odkazy mezi buňkami,
- více záložek,
- zamykání oblastí,
- zvýraznění chyb,
- recepturové tabulky,
- přehled aktuálních hodnot,
- watch panel,
- audit změn.

Základní záložky:

```text
Camera_1
Camera_2
Camera_3
Coordinator
Recipes
Outputs
Diagnostics
```

#### 4.2.2 Context Explorer

Panel se stromem hodnot dostupných z PEKATu:

```text
Camera_1
  context
    result
    detectedRectangles
      by_label
        Screw
        Defect
        Label
    measurements
    operatorInput
  global_data
    spreadsheet
    recipe
    counters
```

Uživatel bude moci přetáhnout položku do buňky. Do buňky se nevloží statická hodnota, ale vazba:

```text
=PV("Camera_1.context.result")
=PV_COUNT("Camera_1", "Screw")
=PV_BEST("Camera_1", "Defect", "confidence")
=PV_GLOBAL("Camera_1", "recipe.active_id")
```

#### 4.2.3 Formula Runtime

Výpočetní jádro bude interpretovat omezený bezpečný jazyk vzorců inspirovaný Excel/Cognex stylem.

První sada funkcí:

```text
IF()
AND()
OR()
NOT()
ABS()
ROUND()
MIN()
MAX()
SUM()
AVERAGE()
COUNT()
COUNTIF()
INRANGE()
INTOLERANCE()
LOOKUP()
VLOOKUP() / RECIPE_LOOKUP()
PV()
PV_GLOBAL()
PV_COUNT()
PV_EXISTS()
PV_BEST()
PV_NEAREST()
PV_DISTANCE()
PV_CENTER_X()
PV_CENTER_Y()
PV_AGE_MS()
```

Nedoporučuje se v první verzi dovolit libovolný Python v buňkách. Je vhodnější mít bezpečný DSL / omezený parser vzorců. Pokročilý skriptovací režim může být až pozdější rozšíření pro administrátory.

#### 4.2.4 Backend

Backend bude centrální runtime služba.

Odpovědnosti:

- příjem snapshotů z PEKAT instancí,
- normalizace Contextu,
- uložení posledních hodnot,
- přepočet tabulek,
- správa receptur,
- správa mapování vstupů a výstupů,
- API pro PEKAT bridge,
- API pro UI,
- audit a logování,
- watchdog stavy,
- multikamerová koordinace.

#### 4.2.5 PEKAT Code Bridge

Malý Python skript vložený do PEKAT Code toolu.

Bude mít tyto režimy:

```text
mode = "sync"
mode = "cached"
mode = "export_only"
mode = "globaldata_only"
mode = "crosspekat_coordinator"
```

Minimální výměnný formát směrem do backendu:

```json
{
  "project_id": "Camera_1",
  "project_name": "Cam1_Left",
  "frame_id": "Cam1_Left_2026-05-28T12:00:00.123",
  "timestamp": "2026-05-28T12:00:00.123",
  "context": {
    "result": true,
    "detectedRectangles": [],
    "operatorInput": {},
    "completeTime": 0.045
  },
  "global_data": {
    "recipe": {
      "active_id": "A"
    }
  }
}
```

Minimální odpověď z backendu:

```json
{
  "ok": true,
  "frame_id": "Cam1_Left_2026-05-28T12:00:00.123",
  "mode": "sync",
  "context_updates": {
    "spreadsheet": {
      "result": true,
      "reason": "OK",
      "gap_mm": 0.32,
      "allow_detail_branch": true
    }
  },
  "global_updates": {
    "spreadsheet": {
      "last_frame_id": "Cam1_Left_2026-05-28T12:00:00.123",
      "last_result": true,
      "last_reason": "OK"
    }
  },
  "control": {
    "override_result": null,
    "exit": false
  }
}
```

---

## 5. Doporučený datový model

### 5.1 Problém se syrovými indexy detekcí

Není vhodné uživateli dávat jako hlavní způsob odkazy typu:

```text
context.detectedRectangles[3].x
```

Pořadí detekcí se může měnit podle inference, confidence nebo interního zpracování.

Lepší je vytvořit stabilní normalizovanou vrstvu:

```text
PV_COUNT("Screw")
PV_BEST("Screw")
PV_BEST("Screw").center_x
PV_BY_ID(1604385708721000)
PV_NEAREST("Hole", ref="Screw")
PV_CLASS_EXISTS("Defect")
```

### 5.2 Normalizovaná reprezentace detekcí

Interní datový model backendu:

```json
{
  "objects": {
    "by_label": {
      "Screw": [
        {
          "id": 123,
          "x": 100,
          "y": 200,
          "width": 50,
          "height": 40,
          "center_x": 125,
          "center_y": 220,
          "area": 2000,
          "confidence": 0.98,
          "label": "Screw"
        }
      ]
    }
  }
}
```

### 5.3 Stav hodnot

Každá buňka a každá PEKAT vazba by měla mít nejen hodnotu, ale i stav:

```text
VALID
MISSING
STALE
TYPE_ERROR
FORMULA_ERROR
TIMEOUT
CYCLE_ERROR
PERMISSION_DENIED
```

Doporučená reprezentace:

```json
{
  "value": 0.32,
  "state": "VALID",
  "updated_at": "2026-05-28T12:00:00.123",
  "frame_id": "Cam1_000123",
  "source": "Camera_1.context.measurements.gap_mm"
}
```

### 5.4 Aktuálnost dat

Kvůli multikameře je nutné u každé hodnoty sledovat:

- `project_id`,
- `frame_id`,
- `timestamp`,
- `age_ms`,
- `source_path`,
- `source_type`,
- `calculation_version`.

Vzorec pak může například kontrolovat:

```text
=AND(PV_AGE_MS("Camera_1.result") < 500, PV_AGE_MS("Camera_2.result") < 500)
```

---

## 6. Spreadsheet funkcionality

### 6.1 Základní buňky

Každá buňka bude mít:

- adresu (`A1`, `B2`),
- volitelný název (`gap_ok`, `master_result`),
- typ (`number`, `bool`, `text`, `object`, `array`, `error`),
- vzorec nebo konstantu,
- poslední hodnotu,
- stav výpočtu,
- metadata zdroje,
- informaci, zda je editovatelná.

### 6.2 Pojmenované buňky

Pro čitelnost musí být možné buňkám dávat jména:

```text
Recipe_MinGap
Recipe_MaxGap
Cam1_GapMm
Cam1_GapOk
Master_Result
Reject_Reason
```

Vzorec pak může být:

```text
=AND(Cam1_GapMm >= Recipe_MinGap, Cam1_GapMm <= Recipe_MaxGap)
```

### 6.3 Receptury

Receptury budou samostatná datová entita, nikoliv jen formátovaná část spreadsheetu.

Příklad:

```json
{
  "recipe_id": "A",
  "name": "Variant A",
  "version": 12,
  "parameters": {
    "min_gap_mm": 0.20,
    "max_gap_mm": 0.45,
    "required_screw_count": 4,
    "allowed_label": "TYPE_A"
  }
}
```

Spreadsheet je bude umět zobrazit a editovat, ale backend bude držet validovaný JSON model.

### 6.4 Výstupní mapování

Samostatná záložka `Outputs` bude definovat, které buňky se zapisují zpět do PEKATu:

| Sheet | Cell / Name | Target project | Target type | Target path | Mode |
|---|---|---|---|---|---|
| Camera_1 | GapOk | Camera_1 | context | spreadsheet.gap_ok | sync |
| Camera_1 | RejectReason | Camera_1 | context | spreadsheet.reject_reason | sync |
| Coordinator | MasterResult | Camera_1 | global_data | spreadsheet.master_result | cached |
| Coordinator | MasterResult | Camera_2 | global_data | spreadsheet.master_result | cached |
| Recipes | ActiveRecipe | all | global_data | recipe.active_id | async |

### 6.5 Chráněné oblasti

Pro průmyslové použití je potřeba rozdělit buňky na:

- vývojářské,
- recepturové,
- operátorské,
- jen pro čtení,
- systémové.

Změna receptury a výstupních mapování musí být auditovaná.

---

## 7. Doporučené režimy komunikace

### 7.1 Inline synchronní režim

```text
PEKAT Code Bridge
  → HTTP POST /api/evaluate
  → backend přepočítá relevantní buňky
  → vrátí context_updates/global_updates/control
  → Code zapíše výsledky
  → Conditional Gate rozhodne další větev
```

Výhody:

- rozhodnutí odpovídá aktuálnímu snímku,
- snadné ladění,
- vhodné pro kritická měření.

Nevýhody:

- citlivé na timeout,
- backend musí být dostupný,
- zvyšuje latenci FLOW.

Doporučení:

- timeout typicky 50 až 200 ms podle reálného taktu,
- při timeoutu konfigurovatelný fallback:
  - poslední validní hodnota,
  - bezpečné NG,
  - `exit=True`,
  - ignorovat spreadsheet a pokračovat.

### 7.2 Cached režim

```text
PEKAT Code Bridge
  → odešle snapshot
  → ihned přečte poslední platnou hodnotu z GlobalData/cache
  → pokračuje
```

Výhody:

- nízké zdržení,
- vhodné pro 4–6 FPS multikamerové sestavy,
- robustnější proti krátkým výpadkům backendu.

Nevýhody:

- výsledek může být ze staršího snímku,
- nutné hlídat `frame_id` a `age_ms`.

### 7.3 Cross-Pekat režim

```text
Camera_1 GlobalData → Coordinator sheet
Camera_2 GlobalData → Coordinator sheet
Coordinator output → GlobalData Camera_1/2/...
Conditional Gate čte GlobalData v lokálním projektu
```

Tento režim je doporučený pro multikamerové aplikace.

### 7.4 Finální export přes HTTP Output

Použití:

- finální report,
- MES,
- dashboard,
- auditní backend,
- ukládání context/subContext.

Nepoužívat jako hlavní vnitřní rozhodovací mechanismus pro větvení uprostřed FLOW.

---

## 8. Multikamerová architektura

### 8.1 Doporučené členění záložek

```text
Camera_1      hodnoty, měření a výpočty pro PEKAT projekt 1
Camera_2      hodnoty, měření a výpočty pro PEKAT projekt 2
Camera_3      hodnoty, měření a výpočty pro PEKAT projekt 3
Coordinator   sdružená rozhodnutí nad více projekty
Recipes       receptury a toleranční tabulky
Outputs       mapování buněk zpět do Context/GlobalData
Diagnostics   komunikace, timeouty, age_ms, chybové stavy
```

### 8.2 Příklad koordinace

```text
Camera_1:
  Cam1_Result = PV("Camera_1.context.result")
  Cam1_GapOk  = INRANGE(PV("Camera_1.measure.gap_mm"), Recipe_MinGap, Recipe_MaxGap)

Camera_2:
  Cam2_Result = PV("Camera_2.context.result")
  Cam2_LabelOk = PV("Camera_2.ocr.label") == Recipe_Label

Coordinator:
  Master_Result = AND(Cam1_Result, Cam1_GapOk, Cam2_Result, Cam2_LabelOk)
  Reject_Reason = IF(NOT(Cam1_GapOk), "CAM1_GAP", IF(NOT(Cam2_LabelOk), "CAM2_LABEL", "OK"))
```

Výstupy:

```text
Master_Result → Camera_1.global_data.spreadsheet.master_result
Master_Result → Camera_2.global_data.spreadsheet.master_result
Reject_Reason → Camera_1.global_data.spreadsheet.reject_reason
Reject_Reason → Camera_2.global_data.spreadsheet.reject_reason
```

### 8.3 Vztah k PEKAT Multi-Camera přes SDK

PEKAT dokumentace popisuje multi-camera setup přes SDK jako HTTP požadavky z více kamer zpracované ve FIFO frontě. Tento projekt na to může navázat, ale pro koordinaci více běžících projektů je praktičtější stavová vrstva přes GlobalData a Cross-Pekat komunikaci.

---

## 9. Bezpečnost, robustnost a průmyslová spolehlivost

### 9.1 Timeouty

Každá komunikace z Code bridge do externí služby musí mít timeout.

Doporučené strategie:

```text
sync critical:
  timeout → NG nebo exit

sync non-critical:
  timeout → poslední validní hodnota

cached:
  timeout → pokračovat s cache, zvýšit diag counter

export_only:
  timeout → pouze zapsat chybu do diagnostiky
```

### 9.2 Watchdog

Backend musí držet diagnostiku:

```json
{
  "Camera_1": {
    "online": true,
    "last_seen_ms": 120,
    "last_frame_id": "Cam1_000123",
    "last_eval_ms": 8,
    "timeouts": 0
  }
}
```

### 9.3 Audit

Každá změna, která může ovlivnit výsledek, musí být auditovaná:

- změna vzorce,
- změna receptury,
- změna výstupního mapování,
- ruční override,
- změna komunikačního režimu,
- změna timeoutu.

Auditní záznam:

```json
{
  "timestamp": "2026-05-28T12:00:00",
  "user": "admin",
  "action": "recipe_update",
  "object": "Recipe A",
  "old_value": 0.45,
  "new_value": 0.50,
  "reason": "new tolerance from customer"
}
```

### 9.4 Bezpečnost vzorců

První verze nesmí vykonávat libovolný Python z buněk. Doporučený postup:

- vlastní parser nebo bezpečný formula engine,
- whitelist funkcí,
- žádné přístupy k filesystemu,
- žádné síťové volání z buněk,
- žádné importy,
- výstupy jen přes definované mapování.

### 9.5 Práva uživatelů

Role:

```text
Viewer      pouze čtení
Operator    výběr receptury, reset čítačů, potvrzení hlášek
Engineer    editace vzorců a mapování
Admin       správa uživatelů, systémová nastavení
```

---

## 10. Doporučený technologický stack

### 10.1 Backend

Doporučení pro první verzi:

```text
Python 3.11+
FastAPI
Pydantic
Uvicorn
SQLite pro lokální konfiguraci
JSON/YAML pro export/import projektu
pytest
```

Alternativa pro pozdější robustní nasazení:

```text
PostgreSQL
Redis cache
WebSocket server
Docker / Windows service
```

### 10.2 UI

Možnosti:

1. **Web UI**
   - React / TypeScript,
   - AG Grid nebo podobná tabulková komponenta,
   - WebSocket pro živé hodnoty,
   - nejvhodnější pro dlouhodobý vývoj.

2. **Desktop UI**
   - PySide6 / Qt,
   - jednodušší lokální instalace,
   - horší webová dostupnost.

3. **Hybrid**
   - backend FastAPI,
   - web UI,
   - lokální launcher jako Windows aplikace.

Doporučení: začít web UI, protože se nejlépe hodí pro dashboard, více kamer a budoucí síťové použití.

### 10.3 Formula Engine

Možnosti:

- vlastní jednoduchý evaluator,
- Python knihovna pro Excel-like formule,
- vlastní DSL s AST,
- později import/export XLSX bez spoléhání na Microsoft Excel runtime.

Doporučení: vlastní omezený DSL nad AST, protože průmyslový runtime vyžaduje bezpečnost, auditovatelnost a determinismus.

---

## 11. Návrh API

### 11.1 Registrace projektu

```http
POST /api/projects/register
```

```json
{
  "project_id": "Camera_1",
  "name": "Left camera",
  "ip": "127.0.0.1",
  "port": 8000,
  "role": "inspection_camera"
}
```

### 11.2 Odeslání snapshotu

```http
POST /api/snapshots
```

```json
{
  "project_id": "Camera_1",
  "frame_id": "Camera_1_000123",
  "timestamp": "2026-05-28T12:00:00.123",
  "context": {},
  "global_data": {}
}
```

### 11.3 Synchronní evaluace

```http
POST /api/evaluate
```

```json
{
  "project_id": "Camera_1",
  "frame_id": "Camera_1_000123",
  "mode": "sync",
  "context": {},
  "global_data": {}
}
```

Odpověď:

```json
{
  "ok": true,
  "context_updates": {},
  "global_updates": {},
  "control": {
    "exit": false,
    "override_result": null
  }
}
```

### 11.4 Poslední platný výsledek

```http
GET /api/projects/{project_id}/last-valid
```

### 11.5 Receptury

```http
GET /api/recipes
POST /api/recipes
PUT /api/recipes/{recipe_id}
POST /api/recipes/{recipe_id}/activate
```

### 11.6 Spreadsheet projekt

```http
GET /api/workbooks/{workbook_id}
PUT /api/workbooks/{workbook_id}
POST /api/workbooks/{workbook_id}/evaluate
```

---

## 12. Návrh struktury GitHub repozitáře

```text
pekat-spreadsheet-bridge/
├─ README.md
├─ LICENSE
├─ pyproject.toml
├─ docs/
│  ├─ specification.md
│  ├─ architecture.md
│  ├─ pekat_integration.md
│  ├─ formula_language.md
│  ├─ recipes.md
│  ├─ api.md
│  └─ deployment.md
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ models/
│  │  ├─ services/
│  │  ├─ formula/
│  │  ├─ storage/
│  │  └─ pekat/
│  └─ tests/
├─ ui/
│  ├─ package.json
│  ├─ src/
│  └─ public/
├─ pekat_code_modules/
│  ├─ spreadsheet_bridge_sync.py
│  ├─ spreadsheet_bridge_cached.py
│  ├─ crosspekat_globaldata_sync.py
│  └─ examples/
├─ examples/
│  ├─ single_camera_demo/
│  ├─ multicamera_demo/
│  └─ recipe_demo/
└─ tools/
   ├─ export_workbook.py
   └─ validate_recipe.py
```

---

## 13. Podrobný plán vývoje

### Fáze 0 – Upřesnění rozsahu

Výstup:

- potvrzený název projektu,
- základní licence,
- rozhodnutí web UI vs desktop UI,
- minimální sada PEKAT verzí,
- rozhodnutí, zda první verze cílí pouze na PEKAT 4.0.

Úkoly:

- založit GitHub repozitář,
- připravit `README.md`,
- přidat tento dokument do `docs/specification.md`,
- vytvořit issue šablony,
- založit milestone `MVP`.

### Fáze 1 – Backend skeleton

Cíl:

- běžící FastAPI backend,
- základní REST API,
- uložení projektů a snapshotů,
- health endpoint.

Výstupy:

```text
GET /health
POST /api/projects/register
POST /api/snapshots
GET /api/projects/{id}/last-snapshot
```

Akceptační kritéria:

- backend běží lokálně,
- lze zapsat snapshot,
- lze přečíst poslední snapshot,
- testy pokrývají základní API.

### Fáze 2 – PEKAT Code Bridge MVP

Cíl:

- Code modul pošle vybraný Context do backendu,
- backend vrátí jednoduchý výsledek,
- Code modul zapíše výsledek do `context["spreadsheet"]`.

První bridge script:

```python
def main(context, module_item=None):
    # 1. sestavit snapshot
    # 2. odeslat na backend s timeoutem
    # 3. zapsat odpověď do context["spreadsheet"]
    # 4. případně nastavit context["exit"] nebo context["result"]
    pass
```

Akceptační kritéria:

- funguje v PEKAT Code toolu,
- timeout nezablokuje FLOW,
- při chybě se zapíše diagnostika,
- lze použít Conditional Gate na hodnotě ze `context["spreadsheet"]`.

### Fáze 3 – Formula Engine MVP

Cíl:

- umět přepočítat jednoduchý workbook v backendu.

Podporované funkce:

```text
IF
AND
OR
NOT
ABS
ROUND
MIN
MAX
INRANGE
PV
PV_COUNT
PV_EXISTS
```

Akceptační kritéria:

- buňka umí konstantu,
- buňka umí odkaz na jinou buňku,
- buňka umí `PV()` odkaz na snapshot,
- engine detekuje cyklické odkazy,
- engine vrací stav `VALID/MISSING/FORMULA_ERROR`.

### Fáze 4 – Jednokamerový prototyp

Cíl:

- jeden PEKAT projekt,
- jedna tabulka,
- několik vzorců nad detekcemi,
- výstup do Contextu,
- Conditional Gate podle výstupní buňky.

Demo scénář:

```text
Detector najde objekty Screw.
Spreadsheet spočítá:
  ScrewCount = PV_COUNT("Screw")
  CountOk = ScrewCount == 4
Code bridge zapíše:
  context["spreadsheet"]["count_ok"]
Conditional Gate pustí / zastaví další větev.
```

### Fáze 5 – UI MVP

Cíl:

- zobrazit workbook,
- editovat buňky,
- zobrazit živé hodnoty,
- zobrazit chyby buněk.

Funkce:

- grid,
- formula bar,
- named cells,
- read-only live values,
- basic context explorer,
- ruční refresh.

### Fáze 6 – Drag and drop Context Explorer

Cíl:

- strom PEKAT hodnot,
- přetažení položky do buňky,
- generování `PV()` výrazu.

Důležité:

- generovat stabilní semantické odkazy,
- nepreferovat syrové indexy `detectedRectangles[3]`,
- umožnit advanced režim pro přímou JSON path.

### Fáze 7 – GlobalData integrace

Cíl:

- číst lokální GlobalData,
- zapisovat výsledky do GlobalData,
- podporovat persistentní stavy.

Výstupy:

```text
global_data.spreadsheet.last_result
global_data.spreadsheet.last_reason
global_data.recipe.active_id
global_data.counters.ok
global_data.counters.ng
```

### Fáze 8 – Multikamerová koordinace

Cíl:

- více PEKAT instancí,
- každá má vlastní sheet,
- `Coordinator` sheet slučuje výsledky,
- výstupy se zapisují zpět do jednotlivých projektů.

Technické prvky:

- registry projektů,
- heartbeat,
- `age_ms`,
- Cross-Pekat update,
- cached režim,
- diagnostika stárnutí hodnot.

### Fáze 9 – Receptury

Cíl:

- samostatný model receptur,
- editace v UI,
- aktivace receptury,
- mapování receptury do GlobalData.

Funkce:

- import/export JSON,
- verze receptury,
- audit změn,
- validace rozsahů,
- volitelný export do XLSX.

### Fáze 10 – Audit, práva, zamykání

Cíl:

- role uživatelů,
- auditní log,
- zamykání buněk,
- historie změn.

### Fáze 11 – Balíčkování a nasazení

Cíl:

- Windows service / lokální launcher,
- konfigurační soubor,
- jednoduché spuštění na průmyslovém PC,
- dokumentace nasazení.

Možnosti:

```text
python -m backend
uvicorn backend.app.main:app
Windows service
Docker později
```

---

## 14. MVP definice

### 14.1 MVP musí umět

- přijmout Context snapshot z jednoho PEKAT projektu,
- zobrazit poslední hodnoty v jednoduchém UI nebo API,
- přepočítat jednoduché vzorce,
- vrátit výsledek do PEKAT Code modulu,
- zapsat `context["spreadsheet"]`,
- řídit Conditional Gate,
- mít timeout a fallback,
- ukládat konfiguraci workbooku.

### 14.2 MVP nemusí umět

- plnou kompatibilitu s Excelem,
- import složitých XLSX souborů,
- realtime editaci více uživatelů,
- rozsáhlé uživatelské role,
- pokročilé grafy,
- vlastní Python skripty v buňkách,
- kompletní MES integraci.

---

## 15. Příklad minimálního PEKAT bridge skriptu

Tento kód je jen ilustrační kostra. Finální verze musí být otestovaná přímo v PEKAT 4.0 Code toolu.

```python
import json
import time
import requests


BACKEND_URL = "http://127.0.0.1:8787/api/evaluate"
PROJECT_ID = "Camera_1"
TIMEOUT_S = 0.10
MODE = "sync"  # sync | cached


def safe_get_context_snapshot(context):
    """Vytvoří lehký JSON snapshot bez obrazu."""
    return {
        "result": context.get("result"),
        "detectedRectangles": context.get("detectedRectangles", []),
        "operatorInput": context.get("operatorInput", {}),
        "completeTime": context.get("completeTime"),
        "spreadsheet": context.get("spreadsheet", {}),
    }


def apply_response_to_context(context, response_data):
    """Zapíše odpověď backendu do Contextu a GlobalData."""
    context_updates = response_data.get("context_updates", {})
    for key, value in context_updates.items():
        context[key] = value

    global_updates = response_data.get("global_updates", {})
    if global_updates:
        if "global_data" not in context or context["global_data"] is None:
            context["global_data"] = {}
        context["global_data"].update(global_updates)

    control = response_data.get("control", {})

    if "override_result" in control and control["override_result"] is not None:
        context["result"] = bool(control["override_result"])

    if control.get("exit") is True:
        context["exit"] = True


def main(context, module_item=None):
    started = time.time()

    if "spreadsheet" not in context:
        context["spreadsheet"] = {}

    frame_id = "{}_{:.6f}".format(PROJECT_ID, started)

    payload = {
        "project_id": PROJECT_ID,
        "frame_id": frame_id,
        "timestamp": started,
        "mode": MODE,
        "context": safe_get_context_snapshot(context),
        "global_data": context.get("global_data", {}),
    }

    try:
        response = requests.post(
            BACKEND_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT_S,
        )
        response.raise_for_status()
        data = response.json()
        apply_response_to_context(context, data)

        context["spreadsheet"]["bridge_ok"] = True
        context["spreadsheet"]["bridge_error"] = ""
        context["spreadsheet"]["bridge_ms"] = int((time.time() - started) * 1000)

    except Exception as exc:
        context["spreadsheet"]["bridge_ok"] = False
        context["spreadsheet"]["bridge_error"] = str(exc)
        context["spreadsheet"]["bridge_ms"] = int((time.time() - started) * 1000)

        # Fallback strategie pro MVP:
        # - neblokovat flow
        # - nepřepisovat result
        # - pouze zapsat diagnostiku
        # Později bude konfigurovatelné: NG / exit / last-valid / ignore.
        return
```

---

## 16. Otevřené otázky pro další rozhodnutí

1. Má první prototyp cílit výhradně na PEKAT 4.0, nebo má mít omezený fallback pro 3.18/3.19 bez GlobalData?
2. Má být první UI webové, nebo desktopové?
3. Jaký bude přesný název projektu a repozitáře?
4. Jaká bude licence?
5. Má být formula syntax blíže Excelu, nebo vlastní PEKAT DSL?
6. Jak moc bude nutná kompatibilita s XLSX importem/exportem?
7. Jaký fallback je výchozí při timeoutu: poslední validní hodnota, NG, exit, nebo ignorovat?
8. Jaké hodnoty z PEKAT Contextu budou v první verzi podporované?
9. Jak bude řešen uživatelský login a audit v MVP?
10. Má být Cross-Pekat komunikace prováděná přímo z PEKAT Code modulů, nebo centrálně backendem přes vlastní endpointy?

---

## 17. Doporučení pro první GitHub issue

### Issue 1: Project bootstrap

```text
Vytvořit základní strukturu repozitáře:
- backend FastAPI skeleton
- docs/specification.md
- pekat_code_modules/spreadsheet_bridge_sync.py
- testy pro /health
- README s popisem cíle
```

### Issue 2: Snapshot API

```text
Implementovat:
POST /api/projects/register
POST /api/snapshots
GET /api/projects/{project_id}/last-snapshot
```

### Issue 3: Minimal formula engine

```text
Implementovat:
- konstanty
- odkazy na buňky
- IF, AND, OR, NOT
- PV(path)
- chybové stavy
```

### Issue 4: PEKAT Code Bridge MVP

```text
Vytvořit Code tool skript:
- sestaví snapshot bez obrazu
- odešle na backend
- zapíše context["spreadsheet"]
- má timeout
- zapisuje diagnostiku
```

### Issue 5: Conditional Gate demo

```text
Připravit ukázkový PEKAT flow:
Detector → Code Bridge → Conditional Gate → další větev
```

---

## 18. Zdrojové opory

### PEKAT VISION 4.0

- PEKAT VISION 4.0 Knowledge Base – přehled:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/overview?homepageId=1512243624
- Context a GlobalData:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513132787/Context
- Code tool:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513132287
- Conditional Gate:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513132739
- Cross-Pekat Communication:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513132513/Cross-Pekat%2BCommunication
- HTTP Output:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1609105419/HTTP%2BOutput
- TCP Output:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1607958579/TCP%2BOutput
- Excel Writer:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513132699
- Multi-Camera Setup:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513129698
- REST API:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513133459
- PEKAT SDK & API:  
  https://pekatvision.atlassian.net/wiki/spaces/KB4/pages/1513133390

### Lokální PEKAT znalostní báze

- `pekat_docs_manifest.txt`
- `KB32-Code-170625-224032.pdf`
- `KB32-Context-170625-224230.pdf`
- `KB32-REST API - Send Images to PEKAT-170625-224514.pdf`
- `KB32-Simple TCP communications-170625-223813.pdf`
- `KB32-Usage Examples-170625-224128.pdf`
- `PEKAT Vision Code module script examples.zip`

### Cognex

- In-Sight Spreadsheet Editor:  
  https://docs.cognex.com/is2d_2310/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/spreadsheet.htm
- Getting Started with In-Sight Spreadsheet:  
  https://docs.cognex.com/is-usp_2421/web/EN/InSight_Sheet/Content/Topics/GettingStarted/getstarted_sheet.htm
- In-Sight Spreadsheet Logic functions:  
  https://docs.cognex.com/is-usp_2430/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/Logic.htm

### Keyence

- Keyence VS Series:  
  https://www.keyence.eu/products/vision/vision-sys/vs/

---

## 19. Závěrečné doporučení

Projekt by měl být veden jako externí nadstavba, ne jako pokus nahradit PEKAT FLOW. PEKAT má zůstat hlavní vision runtime, zatímco spreadsheetová aplikace bude:

- recepturová vrstva,
- výpočetní rozhodovací vrstva,
- přehledná uživatelská logika,
- multikamerový koordinátor,
- auditovatelný konfigurátor vztahů mezi hodnotami.

Nejsilnější kombinace pro PEKAT 4.0 je:

```text
Code tool
  → export / import hodnot

GlobalData
  → persistentní stav a multikamerové sdílení

Cross-Pekat Communication
  → koordinace více instancí

Conditional Gate
  → nativní větvení FLOW podle výsledků tabulky

HTTP Output
  → finální reporting do externích systémů
```

První prototyp by měl být malý, ale uzavřený:

```text
jeden PEKAT projekt
+
jeden Code Bridge
+
backend s jednoduchou tabulkou
+
vzorec nad počtem detekcí
+
zápis výsledku do Contextu
+
Conditional Gate
```

Teprve po ověření latence, timeoutů a spolehlivosti má smysl přidat drag-and-drop, receptury, více záložek a multikamerový Coordinator.

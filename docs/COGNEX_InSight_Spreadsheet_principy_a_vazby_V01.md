# COGNEX In-Sight Spreadsheet – principy, vazby, logika a praktický model pro agentní práci

**Verze dokumentu:** V01  
**Datum zpracování:** 2026-05-28  
**Zaměření:** Cognex In-Sight / In-Sight Vision Suite / In-Sight Explorer – prostředí **Spreadsheet** pro smartkamery a vision systémy Cognex  
**Účel:** přehled pro technické pochopení, návrh inspekčních úloh a jako vzorový popis funkcionalit pro použití agentem CODEX ve VS Code.

---

## 1. Krátké shrnutí

Cognex **In-Sight Spreadsheet** je programovací a konfigurační prostředí pro kamerové systémy Cognex, které kombinuje tabulkový styl podobný Excelu s funkcemi pro strojové vidění. Kamera nebo vision systém zde neběží jako klasický textový program, ale jako **datově-procesní graf buněk**:

- buňka obsahuje hodnotu, vzorec nebo funkční nástroj,
- nástroj má parametry nastavované přes **Property Sheet**,
- parametry mohou být pevné hodnoty, odkazy na jiné buňky nebo další výpočty,
- výsledkem nástroje může být jednoduchá hodnota, text, logická hodnota, obrazová struktura, datová struktura typu Blob/Edge/Pattern/Historgram/Result, případně objekt nebo výstup do HMI/PLC,
- navazující buňky odkazují na výstupy předchozích buněk,
- pořadí výpočtu je řízené závislostmi mezi buňkami a spouští se typicky po akvizici snímku, události, komunikaci nebo ovládacím prvku.

Z praktického pohledu je Spreadsheet potřeba chápat jako **low-code vision runtime**, ve kterém se propojují:

1. **akvizice obrazu** – `AcquireImage` v buňce A0,
2. **lokalizace dílu** – pattern / edge / blob / fixture,
3. **měřicí nebo detekční nástroje** – hrany, blob analýza, OCR, ID, barva, deep learning, vady,
4. **datové extrakce** – Vision Data Access funkce typu `GetX`, `GetY`, `GetScore`, `GetString`, `GetResult`,
5. **logické vyhodnocení** – `If`, `And`, `Or`, `InRange`, `InTolerance`, `OneShot`, limity, tolerance,
6. **publikace výsledků** – WebHMI, EasyView, Custom Views, PLC komunikace, MQTT, TCP/serial, uložení snímků,
7. **řízení běhu** – triggery, eventy, cell state, podmíněné spouštění, synchronizace a bufferování výsledků.

Pro CODEX agenta je nejdůležitější nevnímat Spreadsheet jako „tabulku hodnot“, ale jako **konfigurovatelný výpočetní graf vision nástrojů**, ve kterém jsou klíčové vazby mezi buňkami, datovými strukturami, ROI, fixturami, událostmi a komunikačními výstupy.

---

## 2. Ověřené hlavní zdroje

Dokument vychází primárně z veřejně dostupné oficiální dokumentace Cognex. Níže jsou hlavní zdroje, které jsou vhodné uložit i jako referenční odkazy pro další agentní dohledání:

| Oblast | Odkaz |
|---|---|
| Getting Started with In-Sight Spreadsheet | https://docs.cognex.com/isvs_500/web/EN/InSight_Sheet/Content/Topics/GettingStarted/getstarted_sheet.htm |
| Spreadsheet Editor – obecný popis | https://docs.cognex.com/is2d_2310/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/spreadsheet.htm |
| Using Spreadsheet | https://docs.cognex.com/isvs_500/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/using-spreadsheet.htm |
| Function Reference – kategorie funkcí | https://docs.cognex.com/is_611/web/EN/ise/Content/Reference/FunctionReference.htm |
| Cell Execution | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/HowTo/CellExecution.htm |
| Cell References | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/CellReferences.htm |
| Property Sheet | https://docs.cognex.com/is2d_2310/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/PropertySheet.htm |
| AcquireImage | https://docs.cognex.com/is2d_2320/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/AcquireImage.htm |
| AcquireImage trigger modes | https://docs.cognex.com/isvidi_170/web/EN/Help_ISViDi/Content/Topics/HowTo/is-vidi-job-d900-acquireimage-trigger-modes.htm |
| Vision Tools Functions | https://docs.cognex.com/is_592/web/EN/ise/Content/Reference/VisionTools.htm |
| DetectBlobs | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/DetectBlobs.htm |
| FindLine | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/FindLine.htm |
| OCR/OCV | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/OCV_OCR.htm |
| ID / ReadIDMax | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/ID.htm |
| CalibrateImage / souřadnicové transformace | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/CalibrateImage.htm |
| Logic functions | https://docs.cognex.com/is-usp_2430/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/Logic.htm |
| Cell State Dialog | https://docs.cognex.com/is_611/web/EN/ise/Content/Dialogs/CellStateDialog.htm |
| SetEvent | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/SetEvent.htm |
| EasyView / WebHMI | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/DeployProject/webhmi-easyview.htm |
| Custom Views / WebHMI | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/custom-view-settings.htm |
| MQTT Forwarding | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/HowTo/mqtt-forwarding.htm |
| WriteResultsBuffer | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/WriteResultsBuffer.htm |
| Modbus TCP Communications example | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/IndustrialCommunications/Modbus_Communications_5x.htm |
| Industrial communication control block example | https://docs.cognex.com/isvs_2530/web/EN/InSight_Sheet/Content/Topics/IndustrialCommunications/slmp-defined-data-blocks-vision-control-IS2800-3800.htm |
| Script function | https://docs.cognex.com/isvs_2520/web/EN/InSight_Sheet/Content/Topics/Spreadsheet/VisionTools/Script.htm |
| Audit Logging | https://support.cognex.com/docs/is-usp_2441/web/EN/Help_ISVS/Content/Topics/utilities/audit-log-utility.htm |
| Hidden Spreadsheet Functions – Cognex Support | https://support.cognex.com/en/help-articles/hidden-in-sight-explorer-spreadsheet-functions |

Poznámka: Cognex má paralelně více dokumentačních větví – například **In-Sight Vision Suite**, **In-Sight Explorer**, **In-Sight 2D**, **In-Sight 3D**, **In-Sight ViDi**. Princip spreadsheetu je velmi podobný, ale dostupnost konkrétních funkcí a nástrojů se může lišit podle modelu kamery, firmware a licence.

---

## 3. Mentální model prostředí Spreadsheet

### 3.1 Co Spreadsheet ve skutečnosti je

Spreadsheet je konfigurační/programovací prostředí, ve kterém se vision aplikace sestavuje z buněk. Cognex sám popisuje Spreadsheet jako hlavní GUI komponentu pro tvorbu jednoduchých i komplexních vision aplikací, kde se do buněk vkládají funkční nástroje, upravují jejich vlastnosti a propojují se jejich výsledky a ovládací prvky.

Z hlediska architektury je to kombinace:

- tabulkového editoru,
- výpočetního enginu,
- vision toolchainu,
- runtime pro události,
- HMI publishing vrstvy,
- komunikační vrstvy pro průmyslové systémy.

### 3.2 Buňka jako výpočetní uzel

Každá buňka může obsahovat:

| Typ obsahu buňky | Příklad významu |
|---|---|
| pevná hodnota | limit, tolerance, konstanta, ID receptury |
| textový popisek | organizační nebo HMI text |
| vzorec | výpočet, logika, složení stringu |
| vision funkce | `FindLine`, `DetectBlobs`, `ReadIDMax`, `OCRMax`, `MatchColor` |
| ovládací prvek | tlačítko, checkbox, editovatelná hodnota, region editor |
| komunikační funkce | zápis výsledků do PLC, TCP, MQTT, uložení souboru |
| datová struktura | `Image`, `Blobs`, `Edge`, `Pattern`, `Histogram`, `Buffer`, `Result`, objekt/array |

V běžném programovacím jazyce by se to podobalo sadě proměnných a funkcí. Ve Spreadsheetu je ale vše umístěné v buňkách, takže vazby jsou viditelné a editovatelné přes odkazy typu `A0`, `$A$0`, `B5`, `$D$12`.

### 3.3 Buňka jako vazba v grafu

Typická vazba:

```text
A0  AcquireImage()  -> Image data structure
B3  FindPatMax(A0, ROI...) -> Pattern/fixture result
C3  GetX(B3) -> X pozice
D3  GetY(B3) -> Y pozice
E3  FindLine(A0, fixture z B3, region...) -> Edge result
F3  GetScore(E3) -> skóre hrany
G3  InRange(F3, 80, 100) -> logický výsledek
H3  WriteResultsBuffer(A0, buffer, G3, protocol...) -> výstup do PLC
```

Pro CODEX agenta je vhodné reprezentovat úlohu jako **orientovaný graf**:

```text
AcquireImage[A0]
   ├── LocatePart[B3]
   │     ├── FixtureX[C3]
   │     ├── FixtureY[D3]
   │     └── FixtureTheta[E3]
   ├── InspectionTool1[F3]
   │     └── Tool1Score[G3]
   ├── InspectionTool2[H3]
   │     └── Tool2Value[I3]
   └── FinalLogic[J3]
         └── OutputToPLC[K3]
```

---

## 4. Základní fyzická struktura Spreadsheetu

Podle dokumentace je Spreadsheet organizovaný jako tabulka buněk se 400 řádky a 26 sloupci, tedy řádky 0–399 a sloupce A–Z. Buňka je určena sloupcem a řádkem, například `A2`.

Praktický dopad:

- kapacita není nekonečná,
- přehlednost je důležitá,
- buňky by měly být rozloženy do bloků,
- pro rozsáhlé aplikace je vhodné používat strukturované oblasti: akvizice, lokalizace, měření, limity, logika, komunikace, diagnostika.

Doporučené layoutové členění:

| Oblast | Řádky | Obsah |
|---|---:|---|
| Akvizice | 0–9 | `AcquireImage`, nastavení akvizice, live/test informace |
| Receptura a vstupy | 10–29 | editovatelné parametry, typ dílu, limity, volby programu |
| Lokalizace dílu | 30–69 | Pattern, fixture, referenční hrany |
| Inspekční nástroje | 70–199 | jednotlivé detekce, měření, OCR/ID, blob/edge/AI |
| Logika výsledků | 200–249 | PASS/FAIL, mezivýsledky, alarmy, kódy vad |
| HMI | 250–289 | buňky publikované do EasyView/WebHMI |
| PLC/komunikace | 290–339 | FormatOutputBuffer, WriteResultsBuffer, ReadUserDataBuffer |
| Diagnostika a audit | 340–399 | časy, počítadla, uložení snímků, textové debug výstupy |

Toto členění není požadavek Cognex, ale praktické doporučení pro větší udržovatelnost.

---

## 5. AcquireImage jako kořen vision úlohy

### 5.1 Význam buňky A0

V každé běžné spreadsheet vision úloze je klíčová buňka `A0`, kde je automaticky vložená funkce `AcquireImage`. Ta definuje pořízení obrazu a vrací **Image data structure**. Většina vision nástrojů má výchozí odkaz na `$A$0` jako zdroj obrazu.

Prakticky:

```text
A0 = AcquireImage()
```

Výstup z `A0` je vstup pro další nástroje:

```text
B5 = DetectBlobs($A$0, ...)
C5 = FindLine($A$0, ...)
D5 = ReadIDMax($A$0, ...)
```

Význam:

- nová akvizice spouští přepočet závislých buněk,
- obraz je datová struktura, nikoli jen „náhled“,
- parametry akvizice mohou ovlivnit celý zbytek grafu,
- odstranění `AcquireImage` z `A0` prakticky znemožní běžnou akvizici obrazu.

### 5.2 Co se děje při akvizici

Cognex popisuje, že `AcquireImage` zachytí digitální obraz a přesune ho do procesní paměti vision systému. Šedotónové systémy typicky produkují 8bitový obraz, barevné 24bitový obraz. Výsledkem je obrazová datová struktura, na kterou se odkazují další buňky.

Z hlediska logiky úlohy:

```text
trigger -> acquisition -> A0 Image -> dependent tools -> result logic -> HMI/PLC outputs
```

### 5.3 Trigger režimy

Akvizice může být aktivována více způsoby podle modelu a konfigurace:

| Režim | Princip | Vhodné použití |
|---|---|---|
| Camera / externí trigger | fyzický trigger nebo vstup | výrobní linka, přesná synchronizace |
| Industrial Ethernet | trigger z PLC přes průmyslový protokol | Profinet/EtherNet/IP/Modbus/SLMP workflow |
| Timer / interval | periodické spouštění | pomalejší monitorovací úlohy |
| Continuous | opakované snímání po dokončení cyklu | seřizování, kontinuální inspekce |
| Manual | ruční spuštění | testování, servis, HMI trigger |

Důležitý princip: u externě spouštěných režimů je akvizice typicky „ozbrojena“ po skončení předchozího cyklu. Pokud trigger přijde v nevhodnou chvíli, může dojít k missed acquisition. U self-triggered režimů systém čeká na dokončení předchozího cyklu a další cyklus spustí až potom.

### 5.4 ApplyAcquisitionSettings

Novější dokumentace uvádí funkci `ApplyAcquisitionSettings`, která umožňuje některé parametry akvizice přenést do Spreadsheetu a měnit je za běhu bez otevření Acquisition panelu.

Typické použití:

- dynamická expozice podle receptury,
- změna gainu podle typu dílu,
- zapnutí/vypnutí světla,
- volba ROI/částečné akvizice, pokud to model podporuje.

Pozor na časování: u externě spouštěných režimů se změna nemusí projevit na již „ozbrojené“ akvizici, ale až na další následující akvizici. V praxi je proto potřeba při změně receptury počítat s jedním přechodovým cyklem nebo řízeně kameru pozastavit a znovu ozbrojit.

---

## 6. Cell references – absolutní a relativní odkazy

### 6.1 Proč jsou odkazy zásadní

Odkazy mezi buňkami jsou hlavní mechanismus, kterým se nástroje propojují. Například:

```text
$A$0  absolutní odkaz na obraz z AcquireImage
B10   relativní nebo běžný odkaz podle kontextu
$C$5  absolutní odkaz na konkrétní limit
D$7   smíšený odkaz – fixovaný řádek
$D7   smíšený odkaz – fixovaný sloupec
```

### 6.2 Praktická pravidla

| Situace | Doporučení |
|---|---|
| Odkaz na `AcquireImage` | používat absolutně `$A$0` |
| Odkaz na globální limit | absolutně, například `$C$12` |
| Opakované řádky podobných kontrol | relativní odkazy pomáhají kopírovat bloky |
| Fixture používaná více nástroji | pojmenovat a odkazovat konzistentně |
| HMI hodnoty | pojmenovat buňky a držet stabilní adresy |
| PLC výstupy | nechat ve stabilním komunikačním bloku, nemíchat s výpočty |

### 6.3 Riziko při kopírování bloků

Relativní odkazy se při kopírování posouvají. To je výhoda pro opakované nástroje, ale velké riziko u odkazů na:

- obraz `A0`,
- globální recepturu,
- referenční pattern,
- výstupní buffer,
- HMI buňky.

Pro agentní generování je vhodné mít pravidlo:

```text
Všechny odkazy na globální zdroje a komunikační buňky generuj jako absolutní.
Všechny odkazy uvnitř opakovatelného bloku inspekce mohou být relativní, pokud se blok kopíruje.
```

---

## 7. Property Sheet – vazby parametrů nástrojů

### 7.1 Co je Property Sheet

Property Sheet je konfigurační dialog funkce/nástroje. Umožňuje nastavit parametry vision nástroje, například:

- vstupní obraz,
- fixture,
- region of interest,
- threshold,
- polarity,
- minimální kontrast,
- počet nalezených objektů,
- režim zobrazení grafiky,
- limity,
- event pro spuštění,
- výstupní formát.

Zásadní vlastnost: parametry v Property Sheet nemusí být jen pevné hodnoty. Mohou být navázány na buňky nebo dokonce vyplněny výpočtem/funkcí.

### 7.2 Parametr jako pevná hodnota

Příklad principu:

```text
Threshold = 128
MinArea   = 50
MaxArea   = 99999
Show      = 1
```

Vhodné pro jednoduché a stabilní úlohy.

### 7.3 Parametr jako odkaz na buňku

Příklad principu:

```text
Threshold = $C$20
MinArea   = $C$21
MaxArea   = $C$22
```

Výhody:

- parametry lze publikovat do HMI,
- lze je měnit podle receptury,
- lze je číst z PLC,
- lze je auditovat a dokumentovat.

### 7.4 Parametr jako výpočet

Příklad principu:

```text
Threshold = MeanIntensity + Offset
Tolerance = If(ProductType == 1, 0.2, 0.5)
```

To umožňuje dynamické aplikace, například:

- práh podle histogramu,
- tolerance podle typu dílu,
- ROI podle polohy patternu,
- záchyt snímků jen při neshodě,
- zápis dat jen na událost.

### 7.5 Externí regiony

Mnoho nástrojů umožňuje jako region použít buď interní region definovaný v property sheetu, nebo odkaz na externí region vytvořený funkcí typu `Region`, `EditRegion`, `EditPolygon`, `EditCompositeRegion`, `Mask` apod.

Praktický význam:

- ROI může být editovatelná operátorem,
- jeden region může sdílet více nástrojů,
- složený region může obsahovat oblasti přidané i odečtené,
- masky lze použít pro vynechání rušivých částí obrazu.

Příklad logiky:

```text
B10 = EditCompositeRegion($A$0, ...)
C10 = DetectBlobs($A$0, Fixture, ExternalRegion=$B$10, ...)
D10 = FindLine($A$0, Fixture, ExternalRegion=$B$10, ...)
```

---

## 8. Pořadí výpočtu a časový běh úlohy

### 8.1 Závislostní strom

Spreadsheet neurčuje pořadí výpočtu jen podle polohy buněk. Primárně vyhodnocuje závislosti mezi funkcemi. Pokud buňka `D10` odkazuje na `C10`, musí se nejprve spočítat `C10`. Pokud se změní zdrojová buňka, přepočítají se její závislé buňky.

Princip:

```text
A0 = image
B5 = FindPattern(A0)
C5 = GetX(B5)
D5 = GetY(B5)
E5 = FindLine(A0, fixture = B5)
F5 = GetScore(E5)
```

Výpočetní strom:

```text
A0
├── B5
│   ├── C5
│   └── D5
└── E5
    └── F5
```

### 8.2 Sekundární pořadí podle polohy buňky

Pokud už jsou závislosti vyřešené, Cognex uvádí, že se buňky vyhodnocují podle polohy ve spreadsheetu – v řádku zleva doprava a potom další řádky. Prakticky to znamená:

- buňky ve stejném bloku je vhodné mít logicky zleva doprava,
- výsledky a výpočty držet vpravo od zdrojového nástroje,
- nepřeskakovat chaoticky mezi vzdálenými oblastmi.

### 8.3 Spouštěče výpočtu

Buňky se mohou přepočítat, když:

- dojde k akvizici obrazu,
- změní se buňka, na které závisí další buňky,
- přijde externí událost,
- dorazí data přes komunikaci,
- ovládací prvek jako Button/Checkbox/EditInt vyvolá spreadsheet event,
- přijde paket do TCPDevice,
- proběhne ruční trigger nebo HMI akce.

### 8.4 Výjimky a zvláštní případy

Některé funkce mají speciální chování:

- clocked data storage funkce potřebují přístup ke starším hodnotám,
- některé funkce používají odkazy jako parametr, ale nezakládají běžnou dependency vazbu,
- komunikační funkce typu ReadResult/WriteResult nebo bufferované výstupy mohou být vykonávány později kvůli synchronizaci,
- `SetEvent` frontuje událost až po dokončení aktuálního job execution cyklu,
- Script funkce má vlastní pravidla a limity.

---

## 9. Cell State – podmíněné spouštění buněk

### 9.1 Účel

Cell State umožňuje buňku nebo rozsah buněk:

- explicitně povolit,
- explicitně zakázat,
- povolit podmíněně podle hodnoty jiné buňky.

Pokud je buňka zakázaná, při update spreadsheetu se nevykoná a typicky si drží poslední hodnotu. To je důležité pro:

- podmíněné ukládání snímků,
- jednorázové trénování patternu,
- řízení drahých výpočtů,
- spouštění události při změně stavu,
- výběr větve logiky podle receptury.

### 9.2 Typický příklad – ukládání jen vadných snímků

```text
A0  AcquireImage()
B20 FinalPass = And(Tool1Pass, Tool2Pass, Tool3Pass)
C20 Fail = Not(B20)
D20 WriteImageLocal($A$0, $A$0, "FailImage", ...)
```

Buňka `D20` má Cell State = Conditionally Enabled podle `C20`. Tím se funkce uložení snímku spustí pouze při neshodě.

### 9.3 Typický příklad – SetEvent na hranu signálu

```text
A30 SignalFromPLC
B30 OneShot(A30)
C30 SetEvent(External0)  // podmíněně enabled podle B30
```

Tento princip je vhodný pro převod změny hodnoty na událost. Je potřeba hlídat, aby se `SetEvent` nedostal do rychlé smyčky nebo opakované iterace.

### 9.4 Pozor u Script funkce

Oficiální dokumentace upozorňuje, že `Script` se při zakázaném cell state chová odlišně od běžných funkcí. Protože pro vrácení konkrétní hodnoty potřebuje provést svůj `run` method, mohou navazující `Get` funkce skončit chybou, pokud script nebyl vykonán.

Praktické pravidlo:

```text
Nepodmiňovat Script funkce tak, aby navazující buňky očekávaly validní objekt v cyklu, kde Script neběžel.
Pokud je Script podmíněný, doplnit fallback hodnoty nebo ochrannou logiku.
```

---

## 10. Datové struktury ve Spreadsheetu

### 10.1 Proč nejde jen o čísla

Výstup nástroje není často jen jedno číslo. Mnoho vision funkcí vrací datovou strukturu, ze které se teprve pomocí dalších funkcí čtou konkrétní hodnoty.

| Struktura | Typický zdroj | Typické čtené hodnoty |
|---|---|---|
| `Image` | `AcquireImage`, image processing, `CalibrateImage` | obraz, rozměr, kalibrace |
| `Blobs` | `DetectBlobs`, `FindBlobs`, `SortBlobs` | počet, plocha, X/Y, elongace, perimeter |
| `Edge` / `Edges` | `FindLine`, `FindCircle`, `FindEdges` | poloha, úhel, kontrast, skóre, radius |
| `Pattern` / `Patterns` | `TrainPatMax`, `FindPatMax` | X/Y, theta, score, počet shod |
| `Histogram` | histogram funkce | intenzity, min/max, prahy |
| `Result` | `ReadResult`, komunikační výsledky | indexed hodnoty přes `GetResult` |
| `Buffer` | `FormatOutputBuffer`, `FormatInputBuffer` | průmyslová data pro PLC |
| `Script object` | `Script` | vlastnosti přes `Get` |

### 10.2 Vision Data Access funkce

Vision Data Access funkce slouží k extrakci hodnot ze struktur.

Příklad principu:

```text
B5 = FindLine($A$0, ...)
C5 = GetX(B5)
D5 = GetY(B5)
E5 = GetTheta(B5)
F5 = GetScore(B5)
```

Důležité: při vložení mnoha nástrojů Cognex automaticky vytvoří vedlejší tabulku výsledků, která používá příslušné Data Access funkce. To je velmi důležité pro agentní interpretaci – vedle nástroje často najdeme jeho automaticky vytvořenou result table.

### 10.3 Praktická vazba nástroj → result table

Příklad pro hranu:

```text
B10 = FindLine($A$0, ...)
C10 = GetX(B10)
D10 = GetY(B10)
E10 = GetTheta(B10)
F10 = GetScore(B10)
G10 = InRange(F10, 70, 100)
```

Příklad pro blob:

```text
B20 = DetectBlobs($A$0, ...)
C20 = GetNFound(B20)
D20 = GetArea(B20, 0)
E20 = GetX(B20, 0)
F20 = GetY(B20, 0)
G20 = InRange(D20, MinArea, MaxArea)
```

Názvy `Get...` funkcí se liší podle datové struktury a verze dokumentace. Princip je ale stabilní: nástroj vrátí strukturu a samostatné funkce z ní vyčtou hodnoty.

---

## 11. Vision nástroje – hlavní kategorie a vazby

### 11.1 Přehled kategorií funkcí

Oficiální Function Reference uvádí kategorie funkcí, které lze vkládat do buněk. Pro praktické použití je vhodné dělit je takto:

| Kategorie | Účel |
|---|---|
| Vision Tools | zpracování obrazu a detekce příznaků |
| Geometry | vzdálenosti, konstrukce, fitování, výpočty nad body/hranami/kružnicemi |
| Graphics | grafika, HMI prvky, interaktivní editace regionů |
| Mathematics | výpočty, logika, statistika, trigonometrie |
| Text | formátování stringů, komunikace, serializace |
| Coordinate Transforms | převody mezi pixel, fixture a world souřadnicemi |
| Input/Output | PLC, síť, serial, eventy, soubory |
| Clocked Data Storage | čítače, běžící hodnoty, historické veličiny |
| Vision Data Access | extrakce hodnot z datových struktur |
| Structures | tvorba regionů, tvarů, fixture |
| Scripting | JavaScript pro vlastní logiku |
| Arrays and Objects | práce s poli a objekty v novějších verzích |

---

## 12. Fixture a souřadnicové vazby

### 12.1 Proč je fixture zásadní

Fixture je souřadnicový rámec navázaný na nalezený díl nebo referenci v obrazu. Bez fixture by ROI nástrojů byla pevná v obraze. Pokud se díl posune nebo pootočí, nástroj by kontroloval špatné místo.

Princip:

```text
1. Najdi díl nebo referenční znak.
2. Z výsledku vytvoř X/Y/Theta fixture.
3. Další nástroje nastav relativně k této fixture.
4. ROI se posune a natočí společně s dílem.
```

### 12.2 Typický řetězec

```text
A0  AcquireImage()
B10 Train/Find pattern nebo edge lokalizace
C10 Fixture X
D10 Fixture Y
E10 Fixture Theta
F20 FindLine($A$0, Fixture=(C10,D10,E10), Region=...)
F30 DetectBlobs($A$0, Fixture=(C10,D10,E10), Region=...)
F40 OCRMax($A$0, Fixture=(C10,D10,E10), Region=...)
```

### 12.3 Pixel, fixture a world souřadnice

Cognex podporuje převody mezi:

- obrazovými/pixelovými souřadnicemi,
- fixture souřadnicemi,
- reálnými/world souřadnicemi po kalibraci.

Funkce typu `CalibrateImage` asociuje kalibraci s obrazem a vytvoří novou Image strukturu, kterou mohou další nástroje používat pro výsledky ve world souřadnicích. Praktické použití je měření vzdáleností v mm místo pixelů.

Pozor: oficiální dokumentace upozorňuje, že výstup vision toolu reportovaný ve world coordinates nelze jednoduše použít jako fixture/region vstup pro další 2D vision tool. Při kombinaci 2D a kalibrovaných dat je potřeba velmi pečlivě rozlišovat souřadnicový systém.

---

## 13. Blob analýza

### 13.1 Princip

Blob analýza hledá souvislé oblasti pixelů, které splňují určitou podmínku. V Cognex dokumentaci je to popsané jako connectivity analysis: pixely v ROI se rozdělí na Blob a Background, potom se analyzuje jejich propojenost a vlastnosti.

Typické výstupy:

- počet blobů,
- plocha,
- pozice X/Y,
- obvod,
- elongace,
- spread,
- bounding rectangle,
- pořadí podle plochy nebo skóre.

### 13.2 Typické použití

| Úloha | Blob princip |
|---|---|
| přítomnost dílu | existuje blob v ROI |
| kontrola otvoru | plocha tmavé/světlé oblasti v toleranci |
| množství materiálu | součet ploch blobů |
| detekce nečistoty | malé blob objekty mimo toleranci |
| kontrola štítku | bílý/černý region v očekávaném místě |

### 13.3 Typický řetězec

```text
A0  AcquireImage()
B20 DetectBlobs($A$0, Fixture, Region, Threshold, AreaMin, AreaMax)
C20 NFound = GetNFound(B20)
D20 Area0  = GetArea(B20, 0)
E20 X0     = GetX(B20, 0)
F20 Y0     = GetY(B20, 0)
G20 Pass   = And(C20 >= 1, InRange(D20, MinArea, MaxArea))
```

### 13.4 Vazba na histogram

Pokud je threshold obtížný, je vhodné použít histogramové funkce k odhadu intenzity v oblasti. Dokumentace u DetectBlobs zmiňuje, že histogram může pomoci při jemných gradacích, kdy automatické prahování nestačí.

Příklad principu:

```text
HistROI -> Mean/Head/Tail -> DynamicThreshold -> DetectBlobs
```

---

## 14. Edge nástroje

### 14.1 Princip

Edge nástroje hledají přechody intenzity. Například `FindLine` lokalizuje jednu přímou hranu v obrazovém regionu. Podle dokumentace vytváří jednorozměrnou projekci regionu a extrahuje přechody.

Typické parametry:

- obraz,
- fixture,
- ROI,
- polarita přechodu,
- minimální kontrast,
- šířka hrany,
- očekávaný úhel,
- normalizace skóre,
- režim zobrazení.

### 14.2 Typické výstupy

- X/Y hrany,
- theta/úhel,
- contrast/score,
- radius u kruhových hran,
- min/max deviation,
- standard deviation,
- počet nalezených hran.

### 14.3 Typický řetězec pro měření

```text
A0   AcquireImage()
B10  FindPattern -> fixture dílu
B30  FindLine($A$0, fixture z B10, levá hrana)
B40  FindLine($A$0, fixture z B10, pravá hrana)
C30  X_left  = GetX(B30)
C40  X_right = GetX(B40)
D50  WidthPx = Abs(C40 - C30)
E50  WidthMm = WidthPx * PixelToMm
F50  Pass    = InTolerance(E50, NominalWidth, TolPct, Margin)
```

### 14.4 Doporučení

- Hranové nástroje jsou vhodné pro přesnější geometrii než blob, pokud existuje stabilní kontrastní přechod.
- Vždy je potřeba hlídat polaritu: black-to-white vs. white-to-black.
- ROI má být co nejužší a navázaná na fixture.
- Příliš široký ROI zvyšuje riziko nalezení špatné hrany.
- Edge Width a kontrast ovlivňují stabilitu i rychlost.

---

## 15. Pattern Match / PatMax / lokalizace dílu

### 15.1 Účel

Pattern matching slouží k nalezení známého tvaru v obraze a typicky poskytuje:

- polohu X/Y,
- natočení theta,
- skóre shody,
- počet nalezených shod,
- fixture pro další nástroje.

Cognex PatMax/PatMax RedLine je historicky jedna ze silných oblastí Cognexu. Ve Spreadsheetu se obvykle používá kombinace trénovací funkce a hledací funkce.

### 15.2 Typický workflow

```text
1. Vybrat stabilní referenční oblast dílu.
2. Natrénovat pattern.
3. Hledat pattern v runtime obrazu.
4. Vyčíst X/Y/Theta/Score.
5. Použít X/Y/Theta jako fixture pro další kontroly.
```

### 15.3 Rizika

- Pattern nesmí obsahovat příliš proměnlivou oblast.
- Pattern by měl obsahovat dost geometrických příznaků.
- Příliš velká oblast zpomalí hledání.
- Příliš malá oblast může být nespolehlivá.
- Trénovací buňka má být běžně disabled, aby se pattern omylem nepřetrénoval při další akvizici.

### 15.4 Doporučený agentní zápis

```yaml
locate_part:
  tool: PatternMatch
  image: $A$0
  train_cell: B10
  find_cell: B20
  outputs:
    x: C20
    y: D20
    theta: E20
    score: F20
  pass_condition: F20 >= MinPatternScore
  used_as_fixture_by:
    - edge_left
    - edge_right
    - label_ocr
    - presence_blob
```

---

## 16. OCR/OCV

### 16.1 Princip OCRMax

OCRMax provádí OCR procesem segmentace a klasifikace. Nejprve v ROI najde textovou linii, řeší úhel, skew a polaritu, normalizuje region, binarizuje text a segmentuje znaky. Potom znaky porovnává s trénovanou font databází.

Důležitá poznámka: OCRMax není obecný nástroj pro hledání textu v libovolně složité scéně. ROI musí být nastavené přímo na očekávanou linii textu.

### 16.2 Typické použití

- čtení vyraženého kódu,
- čtení štítku,
- kontrola datumu/šarže,
- OCV ověření, že text odpovídá očekávání,
- kontrola prefix/suffix a formátu.

### 16.3 Fielding

Fielding umožňuje zúžit očekávaný formát textu. Například:

```text
NN/NN/NN  -> číslo číslo / číslo číslo / číslo číslo
AAAA-NNN  -> čtyři písmena, pomlčka, tři čísla
```

Význam:

- zvýšení spolehlivosti,
- odmítnutí nesmyslných výsledků,
- oprava nebo validace proti očekávanému formátu,
- rychlejší klasifikace, protože se nezkouší nemožné znaky.

### 16.4 Typický řetězec

```text
A0   AcquireImage()
B10  LocatePart -> fixture
C40  OCRMax($A$0, fixture z B10, ROI nad textem, font, fielding)
D40  ReadString = GetString(C40)
E40  Score      = GetScore(C40)
F40  FormatOK   = Validate / porovnání s očekávaným patternem
G40  Pass       = And(E40 >= MinOCRScore, F40)
```

---

## 17. ID / ReadIDMax

### 17.1 Účel

ID nástroje čtou 1D a 2D kódy. `ReadIDMax` lokalizuje a dekóduje symboly v ROI. Podle dokumentace umí číst více 1D symbolik ve stejném obraze a více 2D symbolů stejného typu.

### 17.2 Ověření kvality kódu

In-Sight Spreadsheet může volitelně ověřovat kvalitu symbolu podle standardizovaných testů. Prakticky je důležité rozlišit:

- **čitelnost** – kód se podařilo přečíst,
- **kvalita tisku/markingu** – kód může být čitelný, ale proces značení se zhoršuje.

V průmyslové aplikaci je vhodné reportovat obojí:

```text
ReadOK = kód přečten
QualityOK = grade >= požadovaná mez
DataOK = data odpovídají očekávanému formátu / výrobnímu ID
FinalPass = And(ReadOK, QualityOK, DataOK)
```

### 17.3 Typický řetězec

```text
A0   AcquireImage()
B10  Locate label area
C50  ReadIDMax($A$0, ROI)
D50  CodeString = GetString(C50)
E50  ReadOK     = Not(IsError(C50)) / status podle dostupné funkce
F50  DataOK     = porovnání s očekávaným KNR/VIN/serial
G50  FinalPass  = And(E50, F50)
```

---

## 18. Color nástroje

### 18.1 Princip

Color tool workflow typicky obsahuje:

1. `TrainMatchColor` – vytvoření knihovny trénovaných barev,
2. `MatchColor` – porovnání aktuální ROI proti knihovně,
3. vyhodnocení skóre a nejlepší shody.

Nástroj pracuje s průměrnými hodnotami v RGB/HSI prostoru v ROI a je nejvhodnější pro objekty s relativně uniformní barvou.

### 18.2 Typické použití

- kontrola barevné varianty dílu,
- přítomnost barevné značky,
- rozlišení typů komponent,
- ověření správné barvy štítku nebo krytky.

### 18.3 Omezení

- citlivost na osvětlení,
- citlivost na odlesky,
- vhodné jen pro relativně homogenní barvy,
- u náročných aplikací vyžaduje stabilní světelné podmínky nebo normalizaci.

---

## 19. Deep learning / ViDi EL nástroje

### 19.1 Charakter použití

Novější In-Sight prostředí obsahuje i nástroje typu ViDi EL, například segmentaci. `ViDiELSegment` lze použít pro hledání vad nebo lokalizaci příznaků. Uživatel značkuje oblasti perem nebo polygonem, může vytvořit více tříd a po tréninku nástroj predikuje výskyty na nových snímcích.

### 19.2 Typický workflow

```text
1. Vložit ViDi EL tool do Spreadsheetu.
2. Nastavit ROI.
3. Označit vzorové snímky.
4. Vytvořit třídy vad/příznaků.
5. Akceptovat labely a trénovat.
6. Doladit false predictions.
7. Vyhodnotit výsledek a navázat na logiku PASS/FAIL.
```

### 19.3 Praktické poznámky

- U vysokých rozlišení mohou predikce vytvářet velmi malé labely a zatížit přehlednost.
- Je vhodné ukládat job průběžně při delším labelingu.
- Deep learning výstup je potřeba převést na jasné provozní rozhodnutí: počet vad, plocha vad, třída vady, skóre, lokalizace, případně severity.
- V dokumentaci a akceptaci aplikace je potřeba řešit dataset, reprezentativnost vzorků, změny osvětlení, re-training a verzi modelu.

---

## 20. Image processing nástroje

### 20.1 Účel

Image processing funkce vytvářejí novou Image strukturu, kterou lze použít jako vstup pro další nástroje. Typicky jde o:

- filtraci šumu,
- zvýraznění hran,
- škálování,
- kalibraci,
- maskování,
- transformace obrazu,
- separaci barevných složek.

Příklad principu:

```text
A0  AcquireImage()
B5  FilterImage($A$0, ...)
C5  DetectBlobs(B5, ...)
```

### 20.2 Důležitá vazba

Funkce vyžadující Image parametr nemusí odkazovat jen na `A0`, ale také na jinou buňku vracející Image data structure.

To umožňuje řetězení:

```text
A0 -> preprocess image -> calibrate image -> detect blobs -> geometry -> logic
```

---

## 21. Logické vyhodnocení

### 21.1 Základní logické funkce

Cognex Spreadsheet podporuje logické a bitové funkce. Důležitý princip: FALSE je 0, TRUE je jakákoliv nenulová hodnota. Prázdná buňka nebo prázdný string se chová jako FALSE, neprázdný string včetně textu `"0"` se může chovat jako TRUE.

Typické funkce:

| Funkce | Význam |
|---|---|
| `And(...)` | všechny podmínky musí být true |
| `Or(...)` | stačí jedna true |
| `Not(x)` | negace |
| `If(cond, a, b)` | podmíněný výběr hodnoty |
| `InRange(value, start, end)` | hodnota v intervalu |
| `InTolerance(actual, expected, tolerance, margin)` | tolerance vůči nominálu |
| `OneShot(value)` | pulz při přechodu false → true |
| `BitAnd`, `BitOr`, `BitXor` | bitová logika pro stavy a masky |

### 21.2 Doporučený model PASS/FAIL

Pro složitější aplikace nepoužívat jeden dlouhý vzorec, ale vrstvenou logiku:

```text
Tool1Pass = InRange(Tool1Value, Tool1Min, Tool1Max)
Tool2Pass = Tool2Score >= Tool2MinScore
Tool3Pass = And(ReadOK, DataOK)

InspectionPass = And(Tool1Pass, Tool2Pass, Tool3Pass)
InspectionCode = If(InspectionPass, 0, FailureCode)
```

Výhody:

- snadná diagnostika,
- HMI může ukázat dílčí stavy,
- PLC může dostat detailní kód vady,
- agent dokáže vysvětlit, proč výsledek neprošel.

### 21.3 MultiStatus a bitové kódy

Pro přehledné předání více stavů lze vytvořit bitovou masku:

```text
bit0 = Not(Tool1Pass)
bit1 = Not(Tool2Pass)
bit2 = Not(OCRPass)
bit3 = Not(IDPass)

FailureMask = BitOr(bit0*1, bit1*2, bit2*4, bit3*8)
FinalPass = FailureMask == 0
```

To je výhodné pro PLC i pro diagnostické reporty.

---

## 22. #ERR a robustnost úlohy

### 22.1 Co znamená #ERR

`#ERR` může vzniknout z mnoha důvodů:

- neplatný vstupní parametr,
- ROI mimo obraz,
- chybějící datová struktura,
- špatný typ odkazu,
- nenalezený objekt,
- neplatná komunikace,
- nedostupné úložiště,
- chyba scriptu,
- model/funkce není podporovaná daným hardwarem/firmwarem.

### 22.2 Doporučený přístup

U každé důležité větve je vhodné rozlišit:

| Stav | Význam |
|---|---|
| nástroj se spočítal a výsledek je OK | PASS |
| nástroj se spočítal, ale hodnota je mimo limit | FAIL |
| nástroj nenašel objekt | FAIL nebo NO_READ podle aplikace |
| nástroj skončil `#ERR` | chyba aplikace / invalidní měření / fail-safe |

Pro průmyslové použití je bezpečný default:

```text
Pokud není výsledek validní, výsledek inspekce nesmí být PASS.
```

### 22.3 Praktický návrh výstupů

```text
InspectionPass      bool
InspectionValid     bool
FailureMask         uint
ErrorMask           uint
PrimaryFailReason   int/string
InspectionID        int
AcquisitionID       int
Timestamp           string/time
```

---

## 23. Události, SetEvent, Button, Timer

### 23.1 Event jako spouštěč

Funkce `Event` reprezentuje trigger zdroj pro update spreadsheetu. Může reagovat na vstupní/výstupní události, soft/external eventy, tlačítka nebo timer.

Typické použití:

- servisní ruční akce,
- periodické počítadlo,
- přepočet jen při změně hodnoty,
- vyvolání výpočtu z PLC,
- oddělení akvizičního cyklu od pomocných akcí.

### 23.2 SetEvent

`SetEvent` frontuje událost, která se provede po dokončení aktuálního job execution. Dokumentace uvádí limit fronty 30 událostí. Důležité je nevkládat `SetEvent` do opakovaných iterací, aby nevzniklo zahlcení fronty a zmeškané eventy.

### 23.3 Riziko soft/external eventů v přesných aplikacích

Dokumentace upozorňuje, že v prostředí s monitorováním přes In-Sight Spreadsheet nebo VisionView Web může external/soft event spuštěný těsně před koncem akvizice zpozdit inspekci, zejména u velkých jobů. Pro aplikace s přesným časováním v milisekundách je lepší na takové eventy nespoléhat jako na hlavní trigger logiku.

Praktické pravidlo:

```text
Pro hlavní výrobní takt používat jednoznačný trigger a synchronizovaný výstup.
Soft/external eventy používat spíše pro servis, pomocné akce, diagnostiku nebo HMI.
```

---

## 24. Grafika, ovládací prvky, region editory

### 24.1 Graphics funkce

Graphics funkce slouží nejen k vykreslení, ale i k ovládání:

- Button,
- Checkbox,
- EditInt / EditFloat / EditString,
- EditRegion,
- EditPolygon,
- EditCompositeRegion,
- grafické overlaye výsledků,
- status labely.

### 24.2 EditCompositeRegion

`EditCompositeRegion` umožňuje vytvořit složený region z více podregionů. Subregiony mohou být přidávací nebo odečítací, tedy lze vytvořit masku. Pořadí subregionů ovlivňuje výslednou oblast.

Typický význam:

- kontrola jen části dílu,
- vynechání děr/šroubů/odrazu,
- editovatelná maska pro servis,
- jeden region sdílený více nástroji.

### 24.3 Show parametr

Mnoho nástrojů má `Show` parametr. Ten určuje, zda se grafika skrývá, zobrazuje jen výsledek, vstupní region, graf nebo vše.

Prakticky:

| Show režim | Vhodné použití |
|---|---|
| hide except active | běžný runtime, méně rušení |
| result graphics | operátor vidí výsledek |
| input + result | seřizování |
| input + result + chart | ladění hran a citlivosti |

---

## 25. WebHMI, EasyView a Custom Views

### 25.1 EasyView

EasyView umožňuje vybrat a uspořádat spreadsheet buňky, které se mají zobrazit v WebHMI. Důležitý limit: EasyView neumí přidat nepojmenované buňky, proto je potřeba buňky pojmenovat.

Typické buňky vhodné pro EasyView:

- celkový PASS/FAIL,
- dílčí stavy nástrojů,
- skóre patternu,
- naměřené rozměry,
- přečtený kód,
- nastavení limitů,
- počítadla kusů,
- tlačítka pro servisní akce.

### 25.2 Custom Views

Custom View umožňuje ve WebHMI zobrazit obraz a vybranou oblast spreadsheetu na jedné obrazovce. Lze uložit více custom views a přepínat je.

Typické pohledy:

| Pohled | Obsah |
|---|---|
| Operator | PASS/FAIL, aktuální snímek, jednoduché stavy |
| Setup | ROI, pattern score, limity, exposure |
| Maintenance | error mask, komunikace, trigger counts |
| Quality | měřené hodnoty, statistika, uložené fail snímky |

### 25.3 Doporučení pro HMI

- Operátor nemá vidět interní chaotické buňky.
- Všechny HMI buňky pojmenovat srozumitelně.
- Oddělit zobrazované hodnoty od interních výpočtů.
- Nepublikovat přímo nízkoúrovňové mezivýsledky, pokud matou obsluhu.
- Servisní view oddělit od operátorského view.

---

## 26. Komunikace s PLC a nadřazenými systémy

### 26.1 Základní vrstvy komunikace

Spreadsheet může komunikovat více způsoby:

| Vrstva | Typické použití |
|---|---|
| Discrete I/O | jednoduché trigger/result signály |
| Industrial Ethernet | EtherNet/IP, PROFINET, SLMP, Modbus TCP podle modelu/podpory |
| Native Mode / string commands | příkazy a čtení hodnot |
| TCP/UDP device | vlastní síťový protokol |
| Serial | starší zařízení, jednoduchá komunikace |
| MQTT / Enterprise Connectivity | publikace metrik a výsledků do IT/IIoT |
| File/image write | ukládání snímků, SVG overlay, lokální/remote úložiště |

### 26.2 Výstup do PLC přes buffer

Oficiální postup pro Modbus TCP, ale princip platí obecně i pro průmyslové protokoly:

```text
Spreadsheet values -> FormatOutputBuffer -> WriteResultsBuffer -> protocol stack -> PLC reads data
```

`WriteResultsBuffer` používá:

- Buffer vytvořený `FormatOutputBuffer`,
- Result Code,
- Protocol – EtherNet/IP, PROFINET, SLMP, Modbus TCP nebo Default,
- Byte/Word order.

Doporučené členění výstupu:

```text
ResultCode          uint16
InspectionPass      bool/uint16
FailureMask         uint16/uint32
ErrorMask           uint16/uint32
Measurement1        float/int scaled
Measurement2        float/int scaled
CodeString          string/ascii buffer
InspectionID        uint16/uint32
```

### 26.3 Vstup z PLC

Princip:

```text
PLC writes user data -> protocol stack -> ReadUserDataBuffer -> Spreadsheet cells
```

Typické vstupy:

- receptura / typ dílu,
- očekávaný kód,
- příkaz změny jobu,
- povel k validaci,
- parametry limitů,
- servisní reset,
- trigger nebo external event.

### 26.4 Trigger a handshake

Industrial communication control block typicky obsahuje bity jako:

- Trigger Enable,
- Trigger,
- Inspection Results Ack,
- Buffer Results Enable,
- Set Offline,
- Execute Command,
- Set User Data,
- ExternalEvent 0–7.

Důležitý princip synchronizace:

```text
PLC nastaví Trigger Enable
PLC vyšle Trigger
kamera provede akvizici a inspekci
kamera nastaví ResultsValid / Inspection Results
PLC přečte data
PLC potvrdí Inspection Results Ack
kamera uvolní další výsledky
```

Při bufferování výsledků může kamera držet výsledky, dokud PLC nepotvrdí převzetí. Dokumentace u některých protokolových bloků uvádí buffer až pro několik inspekcí, například osm výsledků v konkrétním control block popisu. Přesná kapacita je závislá na protokolu/modelu.

### 26.5 Změna jobu přes PLC

Cognex umožňuje měnit job přes PLC podle názvu nebo ID, ale dokumentace uvádí nevýhody:

- pomalejší přepnutí, minimálně jednotky sekund podle velikosti jobu,
- vision systém musí být Offline,
- WebHMI se musí znovu načíst,
- I/O je delší dobu deaktivované,
- nastavení HMI/I/O musí být duplikované mezi joby.

Doporučení:

```text
Pokud jde jen o variantu dílu, preferovat jeden job s recepturou a parametry.
Job swap přes PLC používat až tam, kde se opravdu mění kompletní aplikace.
```

### 26.6 MQTT / Enterprise Connectivity

Novější In-Sight Vision Suite umožňuje MQTT forwarding pro metriky ve Spreadsheet jobu. Po nastavení brokeru a spojení lze přidat **named cells** jako metriky pro forwarding.

Důležité prvky MQTT konfigurace:

- broker address,
- client ID,
- MQTT v3.1.1 nebo v5,
- TLS/mTLS certifikáty,
- credentials,
- result/command/response topics,
- custom formatter script,
- Last Will and Testament,
- QoS,
- keep alive,
- reconnect,
- limity script enginu.

Doporučený payload pro IT/IIoT:

```json
{
  "camera": "IS3800_Station01",
  "job": "door_label_check_v03",
  "inspection_id": 12345,
  "timestamp": "2026-05-28T22:15:00+02:00",
  "pass": true,
  "failure_mask": 0,
  "measurements": {
    "pattern_score": 94.2,
    "width_mm": 25.13,
    "barcode": "ABC123456"
  }
}
```

---

## 27. Script funkce

### 27.1 Princip

`Script` umožňuje vložit uživatelský JavaScript. Skript je vázaný na konkrétní buňku Script funkce. Pokud je v jobu více Script funkcí, proměnná definovaná v jednom Scriptu není automaticky globální pro ostatní.

### 27.2 Vstupy a výstupy

Script může přijímat různé vstupy:

- číslo,
- string,
- image,
- event,
- shape objekt,
- Binary,
- Blob/Edge/Histogram/Pattern data structure,
- Object/Array ze Script funkce.

Může vracet:

- number,
- boolean,
- string,
- Binary,
- Blob/Edge/Histogram/Pattern,
- shape object,
- object,
- Image,
- null/undefined/empty object.

### 27.3 Omezení

Oficiální dokumentace uvádí limity script memory a stacku. Dále doporučuje mazat nepoužité části defaultního scriptu, protože i nevyužitý draw kód může spotřebovávat paměť a CPU.

Praktická pravidla:

- nepoužívat Script jako náhradu za běžnou logiku, pokud stačí buňky,
- Script používat pro formátování, nestandardní rozhodovací logiku, parsování objektů nebo speciální transformace,
- u každého Scriptu validovat vstupy,
- vracet jednoduchý objekt se stabilními vlastnostmi,
- na výstupní vlastnosti navazovat přes `Get`,
- nezneužívat Script pro časově kritický handshake.

### 27.4 Vzorový princip scriptu

```javascript
function Tool() {}
module.exports = Tool;

function isNumber(n) {
  return !(n === undefined || n === null || isNaN(parseFloat(n)) || !isFinite(n));
}

Tool.prototype.run = function(actual, minValue, maxValue) {
  if (!isNumber(actual) || !isNumber(minValue) || !isNumber(maxValue)) {
    throw new Error("Usage: actual, minValue and maxValue must be numeric");
  }
  const pass = actual >= minValue && actual <= maxValue;
  return {
    pass: pass ? 1 : 0,
    margin_low: actual - minValue,
    margin_high: maxValue - actual
  };
};
```

---

## 28. Audit, správa změn a provoz

### 28.1 Audit logging

In-Sight Vision Suite obsahuje audit logging pro sledování změn jobu a systémových změn. Audit se týká mimo jiné:

- změn výrazů v buňkách,
- enable/disable cell state,
- symbolic tag,
- změn hodnot,
- komentářů,
- změn v complex tools,
- OCRMax, ReadIDMax, Script, ViDi nástrojů,
- HMI settings,
- industrial Ethernet,
- user settings,
- firmware update,
- backup/restore.

### 28.2 Proč je to důležité

Pro výrobní aplikace je audit zásadní, protože Spreadsheet je velmi snadno editovatelný. Bez auditu je obtížné dokázat:

- kdo změnil limit,
- kdo přetrénoval pattern,
- kdo změnil ROI,
- kdy se změnila receptura,
- proč se po zásahu změnilo chování kontroly.

### 28.3 Doporučený provozní režim

- rozdělit role: operátor, údržba, technolog, vision specialista,
- chránit kritické buňky,
- HMI vystavit jen potřebné parametry,
- pravidelně zálohovat joby,
- versionovat job soubory v repozitáři,
- audit log exportovat do centrálního syslogu, pokud je to dostupné,
- dokumentovat validované verze jobu.

---

## 29. Hidden Spreadsheet Functions

Cognex Support uvádí některé skryté Spreadsheet funkce pro In-Sight Explorer kamery, například:

| Funkce | Význam |
|---|---|
| `getSystemConfig("Jobname")` | získá název aktuálně nahraného jobu |
| `Stringf("%V")` | firmware verze kamery |
| `Stringf("%H")` | název kamery |
| `Stringf("%T")` | model kamery |
| `Stringf("%M")` | MAC adresa |
| `Stringf("%I")` | IP adresa |
| `Stringf("%N")` | sériové číslo |
| `SetSystemTime(...)` | nastavení času kamery |
| `_sStartup("test.job",1)` | nastavení startup jobu |
| `SelectLightControl(x)` | výběr interního/externího světla, pokud hardware podporuje |
| `SetPolygonPoint(...)` | změna bodu polygonu |

Pozor: jde o podporou publikované „hidden“ funkce, ne nutně běžný stabilní návrhový interface pro všechny modely a verze. V agentním návrhu je vhodné je označit jako **diagnostické/podpůrné**, ne jako hlavní základ aplikace.

---

## 30. Doporučený návrhový pattern pro jednu inspekční úlohu

### 30.1 Pattern – Presence + measurement + ID

```text
A0   AcquireImage()

// Receptura
C10  ProductType
C11  ExpectedCode
C12  WidthNominal
C13  WidthTolerance
C14  MinPatternScore
C15  MinIDQuality

// Lokalizace
B30  FindPattern($A$0, ROI_full_part)
C30  PartX = GetX(B30)
D30  PartY = GetY(B30)
E30  PartTheta = GetTheta(B30)
F30  LocatePass = GetScore(B30) >= $C$14

// Měření
B60  FindLine($A$0, fixture=(C30,D30,E30), region_left)
B61  FindLine($A$0, fixture=(C30,D30,E30), region_right)
C60  XLeft = GetX(B60)
C61  XRight = GetX(B61)
D60  Width = Abs(C61 - C60) * PixelToMm
E60  WidthPass = InTolerance(D60, $C$12, $C$13, 0)

// ID
B90  ReadIDMax($A$0, fixture=(C30,D30,E30), region_code)
C90  Code = GetString(B90)
D90  CodePass = C90 == $C$11

// Celkový výsledek
B200 FinalPass = And(F30, E60, D90)
B201 FailureMask = BitOr(Not(F30)*1, Not(E60)*2, Not(D90)*4)
B202 ResultCode = If(B200, 0, B201)

// Výstup
B290 FormatOutputBuffer(B200, B201, D60, C90)
B291 WriteResultsBuffer($A$0, B290, B202, Protocol=Default)

// Uložení fail snímku
B330 WriteImageLocal($A$0, $A$0, "Fail", ...)
// Cell State B330 = enabled only if Not(B200)
```

### 30.2 Poznámky k patternu

- `A0` je vždy kořen.
- Lokalizační nástroj je oddělen od inspekčních nástrojů.
- Limity jsou ve vlastní oblasti.
- Výsledky jsou nejdříve dílčí, až potom celkové.
- PLC výstup je oddělený a má stabilní datovou mapu.
- Fail image logging je řízen cell state.

---

## 31. Doporučený dokumentační model pro agent CODEX

Pro CODEX agenta je vhodné vytvořit textovou reprezentaci Spreadsheet jobu nezávislou na proprietárním Cognex editoru. Například ve formátu YAML/JSON/Markdown.

### 31.1 Doporučené entity

```yaml
job:
  name: door_label_check
  platform: Cognex In-Sight Spreadsheet
  version: V03
  acquisition:
    root_cell: A0
    trigger: Industrial Ethernet
    image_source: AcquireImage
  cells:
    - address: B30
      name: LocatePart
      type: vision_tool
      function: PatternMatch
      inputs:
        image: $A$0
        region: full_part_roi
      outputs:
        x: C30
        y: D30
        theta: E30
        score: F30
      dependencies:
        - A0
    - address: B200
      name: FinalPass
      type: logic
      expression: And(F30, E60, D90)
  communication:
    plc_output:
      format_cell: B290
      write_cell: B291
      protocol: Default/PROFINET/EtherNetIP/Modbus
      fields:
        - name: pass
          source: B200
        - name: failure_mask
          source: B201
        - name: width_mm
          source: D60
        - name: code
          source: C90
```

### 31.2 Doporučené atributy buňky

| Atribut | Význam |
|---|---|
| `address` | adresa buňky |
| `name` | logický název |
| `category` | acquisition / locate / inspect / logic / hmi / comm / diagnostic |
| `function` | název Cognex funkce |
| `expression` | vzorec nebo pseudo-vzorec |
| `inputs` | vstupní odkazy a parametry |
| `outputs` | výsledkové buňky |
| `data_structure` | Image / Blobs / Edge / Buffer / Object |
| `dependencies` | buňky, na kterých závisí |
| `cell_state` | enabled / disabled / conditional |
| `hmi_publish` | zda a jak se buňka publikuje |
| `plc_publish` | zda se posílá do PLC |
| `risk` | poznámka k riziku nastavení |
| `test` | ověřovací scénář |

### 31.3 Doporučený výstup agenta

Agent by měl umět generovat:

1. slovní popis jobu,
2. dependency graf,
3. seznam buněk a jejich význam,
4. seznam parametrů vhodných pro HMI,
5. PLC datovou mapu,
6. seznam rizik a validací,
7. checklist pro FAT/SAT,
8. návrh komentářů do Spreadsheetu.

---

## 32. Praktický prompt pro CODEX agenta

Níže je návrh zadání, které lze vložit do projektu jako instrukci pro agenta:

```text
Jsi technický agent pro analýzu a návrh Cognex In-Sight Spreadsheet jobů.
Nevnímej Spreadsheet jako obyčejnou tabulku, ale jako orientovaný výpočetní graf buněk.
Každá buňka může obsahovat hodnotu, funkci, vision nástroj, datovou strukturu, logiku, HMI prvek nebo komunikační funkci.

Při popisu nebo návrhu jobu vždy rozliš:
1. A0 AcquireImage jako kořen akvizice.
2. Parametry akvizice a trigger režim.
3. Lokalizační část – pattern/edge/fixture.
4. Inspekční nástroje – blob, edge, OCR, ID, color, DL.
5. Vision Data Access buňky, které extrahují hodnoty ze struktur.
6. Logiku PASS/FAIL a failure mask.
7. Cell State a podmíněné spouštění.
8. WebHMI/EasyView publikované buňky.
9. PLC/MQTT/TCP komunikační výstupy.
10. Diagnostiku, audit, uložené fail snímky a validaci.

U každé buňky uváděj:
- adresu,
- název,
- funkci/vzorec,
- vstupy,
- výstupy,
- závislosti,
- datový typ nebo strukturu,
- zda je publikovaná do HMI nebo PLC,
- riziko nebo validační poznámku.

Pro návrhy používej bezpečné průmyslové defaulty:
- nevalidní nebo chybějící výsledek nesmí projít jako PASS,
- globální odkazy používej absolutně,
- trénovací buňky drž disabled, pokud nemají být úmyslně spuštěny,
- ROI navazuj na fixture, pokud se díl může posouvat,
- odděl výpočty, HMI a komunikaci do samostatných bloků,
- pro PLC publikuj stabilní datovou mapu: InspectionID, ResultCode, Pass, FailureMask, ErrorMask, hlavní měření a identifikaci.
```

---

## 33. Checklist pro návrh Cognex Spreadsheet úlohy

### 33.1 Akvizice

- [ ] Je `AcquireImage` v `A0` zachovaný a validní?
- [ ] Je jasně definovaný trigger režim?
- [ ] Je známá odezva při missed acquisition?
- [ ] Jsou nastavené expozice, gain, světlo a případně partial acquisition?
- [ ] Je při změně receptury řešen jeden přechodový cyklus nastavení?

### 33.2 Lokalizace

- [ ] Existuje stabilní lokalizační pattern/hrana/reference?
- [ ] Je score lokalizace vyhodnocené jako dílčí PASS/FAIL?
- [ ] Používají navazující ROI fixture?
- [ ] Je řešen případ nenalezeného dílu?

### 33.3 Vision nástroje

- [ ] Má každý nástroj jasnou ROI?
- [ ] Má každý nástroj definované parametry a limity?
- [ ] Jsou výsledky extrahované přes Data Access buňky?
- [ ] Je zachyceno `#ERR` nebo nevalidní chování?
- [ ] Jsou grafické overlaye nastavené podle režimu seřizování/runtime?

### 33.4 Logika

- [ ] Existují dílčí PASS/FAIL pro každý nástroj?
- [ ] Je celkový PASS složen z dílčích stavů?
- [ ] Existuje failure mask nebo error code?
- [ ] Není logika skrytá v jednom nepřehledném vzorci?

### 33.5 HMI

- [ ] Jsou buňky pro EasyView pojmenované?
- [ ] Operátor vidí jen potřebné hodnoty?
- [ ] Existuje servisní view pro diagnostiku?
- [ ] Jsou editovatelné parametry oddělené od interních hodnot?

### 33.6 Komunikace

- [ ] Je jasná PLC datová mapa?
- [ ] Je definovaný trigger/result handshake?
- [ ] Je řešen ACK výsledků a bufferování?
- [ ] Je definovaný result code?
- [ ] Jsou stringy a číselné hodnoty správně formátované?
- [ ] Je jasný endian/word order?

### 33.7 Provoz a audit

- [ ] Jsou kritické změny auditované?
- [ ] Je job verzovaný?
- [ ] Jsou trénovací buňky chráněné nebo disabled?
- [ ] Existuje záloha validované verze?
- [ ] Je popsán postup po výměně kamery / čočky / světla?

---

## 34. Nejčastější chyby návrhu

| Chyba | Důsledek | Prevence |
|---|---|---|
| Pevné ROI bez fixture | nástroj kontroluje špatné místo při posunu dílu | lokalizační pattern + fixture |
| Jeden obří vzorec PASS/FAIL | špatná diagnostika | dílčí stavy + failure mask |
| Trénovací funkce zůstane enabled | pattern/model se může nechtěně přetrénovat | po trénování disabled / chránit |
| Relativní odkaz na globální limit | po kopírování bloků chybné limity | absolutní odkazy `$C$10` |
| `#ERR` není řešen | chyba může být špatně interpretována | validita + fail-safe |
| Job swap místo receptury | pomalé přepnutí, offline stav, HMI reload | parametry/receptura v jednom jobu |
| Příliš široký OCR ROI | OCR hledá špatné znaky | ROI přímo nad textem |
| Příliš široký edge ROI | nalezení jiné hrany | úzký region, fixture, polarita |
| Soft event jako hlavní takt | zpoždění a race condition | hlavní trigger přes akvizici/PLC handshake |
| HMI ukazuje interní buňky | obsluha je zahlcená | oddělené operator/setup/maintenance view |

---

## 35. Doporučený způsob dokumentace konkrétní aplikace

Pro každý Cognex job je vhodné vytvořit doprovodný markdown soubor:

```text
/docs
  cognex_job_overview.md
  cell_map.md
  plc_interface.md
  hmi_map.md
  validation_plan.md
  change_log.md
```

### 35.1 `cell_map.md`

Obsah:

```markdown
| Cell | Name | Function | Inputs | Outputs | Meaning | HMI | PLC | Notes |
|---|---|---|---|---|---|---|---|---|
| A0 | AcquireImage | AcquireImage | trigger | Image | Root image acquisition | no | no | Do not delete |
| B30 | LocatePart | PatternMatch | A0 | Pattern | Part localization | setup | no | Disabled train cell separate |
| F30 | LocatePass | Logic | score | bool | Localization valid | yes | yes | score >= min |
```

### 35.2 `plc_interface.md`

Obsah:

```markdown
| Offset | Name | Type | Source Cell | Description |
|---:|---|---|---|---|
| 0 | InspectionID | UINT | A0/B291 | Acquisition/result sync |
| 1 | ResultCode | UINT | B202 | 0 OK, nonzero failure |
| 2 | Pass | BOOL/UINT | B200 | Final pass |
| 3 | FailureMask | UINT | B201 | Bit-coded failures |
| 4 | Width_mm_x100 | INT | D60 | scaled measurement |
```

### 35.3 `validation_plan.md`

Obsah:

- seznam typů dílů,
- počet OK/NG vzorků,
- minimální score,
- tolerance,
- test posunu/natočení,
- test osvětlení,
- test komunikace s PLC,
- test restartu,
- test změny receptury,
- test auditovatelnosti.

---

## 36. Shrnutí pro management

Cognex Spreadsheet je silné prostředí pro realizaci smartkamerových inspekcí, protože umožňuje přímo v kameře nebo vision systému propojit akvizici obrazu, vision nástroje, logiku, HMI a průmyslovou komunikaci. Jeho výhoda je rychlá konfigurace a vysoká názornost. Nevýhoda je, že u větších aplikací se bez disciplíny může stát nepřehledným „tabulkovým programem“, kde jsou kritické vazby skryté v buňkách.

Pro profesionální použití je proto potřeba:

- strukturovaný layout buněk,
- pojmenované hodnoty,
- dokumentovaná dependency mapa,
- jasné PASS/FAIL stavy,
- stabilní PLC datová mapa,
- audit změn,
- validace na reprezentativních datech,
- verzování jobů a záloh.

Pro CODEX a agentní podporu je Spreadsheet vhodný tehdy, pokud se přepíše do textového modelu buněk, vazeb, nástrojů a datových struktur. Agent pak může pomáhat s dokumentací, návrhem logiky, kontrolou vazeb, generováním PLC mapy, vysvětlením funkce jobu a přípravou validačních scénářů.

---

## 37. Limity tohoto dokumentu

- Nejde o náhradu licencované nebo verzi-specifické dokumentace Cognex.
- Dostupnost konkrétních funkcí závisí na modelu kamery, firmware, licenci a produktové řadě.
- Některé principy jsou společné pro In-Sight Vision Suite a starší In-Sight Explorer, ale názvy funkcí nebo parametry se mohou mezi verzemi lišit.
- Vzorce uvedené v dokumentu jsou často **principiální pseudo-zápis**, ne vždy přesná syntaxe pro okamžité vložení do konkrétní verze Cognex editoru.
- Před nasazením je nutné ověřit přesnou syntaxi v aktuální Function Reference pro daný model a firmware.

---

## 38. Jak ověřit v praxi

1. Vytvořit nový In-Sight Spreadsheet job.
2. Ověřit, že `A0 = AcquireImage()` existuje a že se při triggeru přepočítají závislé buňky.
3. Vložit jednoduchý nástroj, například `FindLine` nebo `DetectBlobs`, a sledovat automaticky vytvořenou result table.
4. Přidat logickou buňku `InRange` nebo `And` a navázat ji na výstup nástroje.
5. Přidat buňku do EasyView a ověřit zobrazení ve WebHMI.
6. Přidat `FormatOutputBuffer` + `WriteResultsBuffer` a ověřit mapu s PLC nebo simulátorem protokolu.
7. Nastavit Cell State na funkci uložení snímku a ověřit, že se spouští jen při FAIL.

---

Konec dokumentu.

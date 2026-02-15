---
name: pekat-vision
description: Integrace a skriptovani pro PEKAT Vision (Code module, REST API, SDK, Projects Manager, externi Python knihovny). Pouzij pri implementaci nebo debugovani PEKAT workflow; nepouzivej pro cisty frontend nebo neodsouhlasene produkcni zasahy.
---

# Quick workflow
1. Potvrd cil integrace: Code modul, REST API, SDK, Projects Manager, nebo kombinace.
2. Odkazuj se na aktualni verejne zdroje:
   - SDK docs: `https://pekat-vision.github.io/pekat-vision-sdk-python/`
   - SDK repo: `https://github.com/pekat-vision/pekat-vision-sdk-python`
   - PyPI release: `https://pypi.org/project/pekat-vision-sdk/`
   - Public examples: `https://github.com/pekat-vision/pekat-vision-examples`
3. Nejdriv priprav minimalni robustni reseni, pak dodej rozsireni.
4. U kodu pro Code modul drz stabilni typy v `context`.
5. U API/TCP volani vzdy nastav timeout a osetri chyby.
6. Pridej nebo uprav demo/test, ktery jde spustit i mimo PEKAT runtime.
7. Synchronizuj `docs/TECHNICAL.md` a `docs/USER_GUIDE.md`, pokud se zmeni workflow.

# Rules for Code module
## Entrypoint and compatibility
- Definuj `main(context, module_item=None)`.
- Ber `module_item` jako form values (`dict`) z Form Editoru.
- Nevyhazuj vyjimku pri chybejicich vstupech; vrat bezpecne `return`.

## Context safety
- Pouzivej `context.get(...)` a guardy pro listy/slovniky.
- Nemen typ existujicich klicu (`image`, `detectedRectangles`, `heatmaps`, `result`, `exit`).
- Pokud menis `context["image"]`, vrat validni `np.ndarray` s konzistentnim shape/dtype.

## Runtime behavior
- Nespoustej dlouhe blokujici operace bez timeoutu.
- Uprednostni NumPy/OpenCV vektorove operace pred pixel loops.
- Pro branch skipping pouzij `context["exit"] = True` jen kdyz to je zamyslene.

# REST API defaults (aligned with current SDK behavior)
Pouzij tyto endpointy:
- `POST /analyze_image`
- `POST /analyze_raw_image?height=<h>&width=<w>`
- `POST /analyze_image_shared_memory` (lokalni analyza, PEKAT server >= 3.18, typicky reseno SDK)
- `GET /ping`
- `GET /stop` (SDK pouziva stop key pri vlastnim lifecycle)

Pouzij query parametry:
- `response_type`: `context | image | annotated_image | heatmap`
- `data`: volitelna string hodnota, v projektu pristupna jako `context["data"]`
- `context_in_body`: pouzij pro velke context payloady (SDK doporucuje pri velikosti > 4 KB)

Parsuj odpoved robustne:
- Kdyz `response_type=context`, cekej JSON body.
- Kdyz `context_in_body=true`, ocekavej `ImageLen` header a payload `image_bytes + context_json`.
- Jinak ocekavej `ContextBase64utf` v headerech a image bytes v body.

Viz `scripts/rest_api_client_demo.py`.

# Projects Manager guidance
- Prioritne pouzij public/official API nebo SDK wrapper, kdyz je dostupny.
- Pro legacy Simple TCP workflow pouzij `scripts/projects_manager_tcp_demo.py`.
- Osetri socket timeout, decode chyby a neplatne odpovedi.
- Pokud instance vraci jine command formaty nez demo, probehni capability check na cilove instalaci a commandy adaptuj.

# External Python libraries in PEKAT server
- Instaluj knihovny pro stejnou platformu a stejnou Python ABI jako cilovy PEKAT server.
- Vytvor portable balicek:
  - `pip install --target <folder> <package>`
- Zkopiruj obsah do PEKAT server adresare.
- Kdyz import nefunguje, pridej cestu do `sys.path` (viz `scripts/add_libs_to_sys_path.py`).
- U `.pyd`/`.so` knihoven over OS/arch kompatibilitu a zavislosti.

# Delivery checklist
- [ ] Kod obsahuje `main(context, module_item=None)` pokud je urcen pro Code modul.
- [ ] Kod nepada na `KeyError`/`IndexError`.
- [ ] API/TCP volani maji timeouty a osetreni chyb.
- [ ] Dokumentace odpovida skutecnemu kodu v `scripts/`.
- [ ] Existuje aspon jeden smoke test nebo spustitelne demo.

# Bundle map
- `docs/TECHNICAL.md`: technicke poznamky a API pravidla.
- `docs/USER_GUIDE.md`: prakticky postup pro vlozeni a ladeni Code skriptu.
- `scripts/`: sablony a demo klienti.
- `tests/`: smoke testy pro rychlou verifikaci.


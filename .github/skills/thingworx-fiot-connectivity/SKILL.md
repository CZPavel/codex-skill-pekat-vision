---
name: thingworx-fiot-connectivity
description: Bezpecna a rychla integrace lokalniho SW, PLC, monitoringu a Kepware do FIOT (Foxon) postaveneho na PTC ThingWorx. Pouzij pri pozadavcich s FIOT, ThingWorx, appKey autentizaci, Mashup, Thing, Property, Service, ExtensionPackageUploader, EMS/AlwaysOn, PROFINET topologii a client certifikaty (mTLS), hlavne pro vytvoreni REST konektoru/bridge, healthchecku a write-property nebo invoke-service skeletonu s dokumentaci. Nepouzivej pro ciste frontend design bez integrace ani pro neodsouhlasene produkcni zasahy do serveru, uzivatelu nebo klicu.
---

# Cil skillu

Vytvorit opakovatelny playbook pro konektor mezi lokalnim zdrojem dat a FIOT/ThingWorx tak, aby byl:
- rychle nasaditelny (MVP healthcheck + prvni zapis dat),
- bezpecny (appKey, bez session, TLS/mTLS, bez ulozeni secretu do repa),
- dobre zdokumentovany (`docs/TECHNICAL.md`, `docs/USER_GUIDE.md`, `CHANGELOG.md`, `project_context.md`),
- pripraveny na rozsirovani (Kepware, EMS/AlwaysOn, Extensions).

# Triggery
- `FIOT`
- `ThingWorx`
- `PTC`
- `appKey`
- `Mashup`
- `Thing`
- `Property`
- `Service`
- `ExtensionPackageUploader`
- `EMS`
- `AlwaysOn`
- `PROFINET topology`
- `client certificate`
- `Kepware`

# Kdy nepouzit
- Kdyz uzivatel chce jen obecny frontend bez komunikace s ThingWorx.
- Kdyz uzivatel chce menit uzivatele, role, aplikacni klice nebo webhooky bez explicitniho souhlasu.
- Kdyz neni potreba integrace na FIOT/ThingWorx/Kepware.

# Bezpecnostni guardraily
- Bez explicitniho souhlasu nedelej zmeny na serveru.
- Bez explicitniho souhlasu nenasazuj webhooky ani Extensions.
- Bez explicitniho souhlasu nemanipuluj s uzivateli, rolemi a `Application Key`.
- Bez explicitniho souhlasu neprovadej `git push`.
- Nikdy neukladej `appKey` ani privatni klice do repozitare.
- Vzdy preferuj `.env`/secret manager.

# Architektura integrace (kratce)
- `ThingWorx Foundation` je aplikacni vrstva pro modelovani assetu, data ingest, alarmy a vizualizaci.
- `Thing` reprezentuje konkretni asset nebo logicky zdroj dat.
- `ThingTemplate` definuje sdilenou strukturu a chovani pro vice `Thing`.
- `Property` nese stav/telemetrii (napr. vibration RMS, energie, stav linky).
- `Service` je volatelna operace (zapis, agregace, business logika).
- `Event` signalizuje zmenu/stav, typicky navazany na notifikace a alarming.

Typicke FIOT datove toky:
- Diagnostika stroju (`vibro`, energie, PROFINET monitoring).
- Agregace a vypocty KPI.
- Alarmy/notifikace.
- Vizualizace v mashupech a reporting.

# Komunikacni varianty
- `REST` z aplikace: vychozi varianta pro externi SW. Pouzij `appKey` v HTTP hlavicce a `x-thingworx-session=false`.
- `EMS/AlwaysOn`: pouzij pro edge zarizeni a dlouhodoby device channel.
- `Extensions`: pokrocila varianta. Nasazeni muze zahrnovat upload balicku pres REST (`ExtensionPackageUploader`) a casto vyzaduje restart/sluzby admin.

# Playbook

## 1) Discovery
Pri dotazu obsahujicim `FIOT`/`ThingWorx` nejdriv ziskej nebo odvod:
- `base URL` (napr. `https://fiot.customer.tld`),
- autentizaci (`appKey`),
- cilove entity (`Thing`, `Property`, `Service`),
- format payloadu (`JSON` schema, jednotky, timestamp),
- sitove a cert pozadavky (TLS/mTLS, proxy, DNS, porty).

## 2) Vytvor MVP konektor
1. Vytvor skeleton projektu prikazem:
   - `python .github/skills/thingworx-fiot-connectivity/scripts/scaffold_project.py --output <target-folder>`
2. Automaticky priprav:
   - REST `healthcheck`,
   - prvni skeleton `write property`,
   - prvni skeleton `invoke service`,
   - dokumentaci (`docs/TECHNICAL.md`, `docs/USER_GUIDE.md`) + `CHANGELOG.md` + `project_context.md`.

## 3) Robustnost a provoz
- Nastav timeouty, retry a exponential backoff.
- Loguj request id, endpoint, latency a status code.
- Drz `dry-run` mod pro bezpecne overeni bez zapisu.
- Vynucuj TLS validaci; pro Foxon use-cases priprav i klientsky certifikat (`mTLS`).

## 4) Kepware varianty
- Pouzij Kepware jako zdroj dat:
  - bud nativni ThingWorx konektivita z KEPServerEX,
  - nebo mezivrstva (bridge), ktera cte tagy (napr. OPC UA) a zapisuje do ThingWorx REST.
- Vzdy mapuj tagy na ThingWorx `Property` s jednotkami a timestampem.

## 5) EMS/AlwaysOn a Extensions
- Pokud je use-case zarizeni-centric, zvaz `EMS/AlwaysOn` s `appKey`.
- U Extensions povazuj upload/deploy za citlivou operaci:
  - vyzadej souhlas,
  - over prava a maintenance okno,
  - zdokumentuj rollback.

## 6) Dokumentace a kontext
- Synchronizuj:
  - `docs/TECHNICAL.md` (endpointy, auth, session policy, troubleshooting),
  - `docs/USER_GUIDE.md` (instalace, konfigurace, spusteni, test),
  - `CHANGELOG.md`,
  - `project_context.md`.
- Dopln checklist: sit, DNS, certifikaty, porty, appKey prava, odpovedi serveru.

# Safe defaults
- Vzdy posilej `x-thingworx-session=false` pro aplikacni REST volani.
- Vzdy pouzij `appKey` (bez user session).
- Nikdy nedavej tajemstvi do git.
- Drz zapnute TLS overovani (`verify=true`), vypnuti povol jen docasne pro diagnostiku.
- Nabidni `dry-run` jako vychozi startovaci rezim.

# Co ma agent delat automaticky
Kdyz uzivatel rekne `FIOT/ThingWorx`, agent automaticky:
1. Vyzada chybejici Discovery vstupy (`base URL`, `appKey`, `Thing/Service/Property`, JSON schema).
2. Vytvori nebo aktualizuje konektor s `healthcheck` + prvnim `write property` nebo `invoke service`.
3. Vytvori nebo aktualizuje `docs/TECHNICAL.md`, `docs/USER_GUIDE.md`, `CHANGELOG.md`, `project_context.md`.
4. Provede rychly sanity test (`dry-run`, nebo mock endpoint).

# Checklist overeni
- [ ] Funguje DNS a routovani na FIOT/ThingWorx host.
- [ ] Otevrener spravny port (`443` nebo customer-specific).
- [ ] Certifikaty serveru (a pripadne klienta) jsou validni.
- [ ] `appKey` ma pravo na cilovy `Thing/Property/Service`.
- [ ] REST odpoved vraci ocekavany HTTP status a telo.
- [ ] `x-thingworx-session=false` je pritomny v requestech.
- [ ] Nikde v repu neni ulozeny `appKey`.

# Bundle map
- `scripts/scaffold_project.py`: vygeneruje minimalni projektovy skeleton konektoru.
- `assets/project-template/`: sablony `src/`, `docs/`, `.env.example`, `CHANGELOG.md`, `project_context.md`.
- `references/primary_sources.md`: verejne zdroje Foxon/PTC/Kepware.
- `references/integration_notes.md`: endpoint patterns, mTLS postup a troubleshooting.

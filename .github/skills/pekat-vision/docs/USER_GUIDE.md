# USER GUIDE

## 1. Co skill umi
- Navrh a uprava PEKAT Code module skriptu.
- REST klient pro analyzu obrazu.
- Zakladni napojeni na Projects Manager.

## 2. Instalace do Codex
```powershell
python C:\Users\P.J\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo CZPavel/codex-skill-pekat-vision --path .github/skills/pekat-vision --name pekat-vision
```

## 3. Lokalni overeni
```powershell
python C:\Users\P.J\.codex\skills\.system\skill-creator\scripts\quick_validate.py .github/skills/pekat-vision
python -m pytest -q tests/test_code_module_smoke.py tests/test_rest_api_client_demo.py
```

## 4. Typicky postup
1. Vyber use-case: Code module / REST / Projects Manager.
2. Vytvor minimalni variantu se safe defaults.
3. Pridej smoke test.
4. Aktualizuj dokumentaci a changelog.

## 5. Bezpecnost
- Nepouzivej produkcni endpoint bez schvaleni.
- Necommituj tajemstvi.
- Drz timeouty a explicitni error handling.

# Codex Skill: PEKAT Vision

Samostatny repozitar pro skill `pekat-vision`.
Repo je zamereny na integraci PEKAT Vision (Code module, REST API, SDK, Projects Manager) a je pripraveny pro samostatnou instalaci pres Skill Installer.

## Kdy pouzit
- Potrebujete navrhnout nebo upravit PEKAT Code module script.
- Potrebujete REST klienta pro analyze image/raw image endpointy.
- Potrebujete napojit Projects Manager nebo pridat externi Python knihovnu do PEKAT serveru.

## Kdy nepouzit
- Ciste frontend/UI bez integrace na PEKAT.
- Neodsouhlasene produkcni zasahy do serveru, uzivatelu, klicu nebo site.

## Struktura
- `.github/skills/pekat-vision/SKILL.md`
- `.github/skills/pekat-vision/agents/openai.yaml`
- `scripts/`
- `tests/`
- `docs/`
- `project_context.md`
- `CHANGELOG.md`

## Instalace skillu
```powershell
python C:\Users\P.J\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo CZPavel/codex-skill-pekat-vision --path .github/skills/pekat-vision --name pekat-vision
```

## Validace
```powershell
python C:\Users\P.J\.codex\skills\.system\skill-creator\scripts\quick_validate.py .github/skills/pekat-vision
python -m pytest -q tests/test_code_module_smoke.py tests/test_rest_api_client_demo.py
```

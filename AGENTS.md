# AGENTS Instructions

## Lokalne kontroly
```powershell
python C:\Users\P.J\.codex\skills\.system\skill-creator\scripts\quick_validate.py .github/skills/pekat-vision
python -m pytest -q tests/test_code_module_smoke.py tests/test_rest_api_client_demo.py
```

## Instalacni test (izolovane)
```powershell
python C:\Users\P.J\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo CZPavel/codex-skill-pekat-vision --path .github/skills/pekat-vision --dest C:\PYTHON_test\_skill_split_work\install_test\skills
```

## Publikace
- Nepouzivat force push.
- Pred pushem aktualizovat `CHANGELOG.md` a `VALIDATION.md`.
- Overit, ze `SKILL.md` obsahuje `name` a `description`.

# AGENTS Instructions

## Canonical source

- Edit only `.github/skills/pekat-vision` for installed skill behavior/resources.
- Do not recreate root-level script/reference mirrors.
- Never include credentials, private endpoints, raw proprietary documents, venv/cache files, or Codex state.

## Local validation

```powershell
$Validator = Join-Path $env:USERPROFILE ".codex\skills\.system\skill-creator\scripts\quick_validate.py"
python $Validator .github/skills/pekat-vision
python -m pytest -q
```

## Isolated installer test

```powershell
$Installer = Join-Path $env:USERPROFILE ".codex\skills\.system\skill-installer\scripts\install-skill-from-github.py"
python $Installer --repo CZPavel/codex-skill-pekat-vision --ref <branch-or-tag> --path .github/skills/pekat-vision --dest <empty-test-directory>
```

## Publication

- Do not force-push.
- Update root `CHANGELOG.md` and `VALIDATION.md` before push.
- Require local validation and green GitHub Actions before merge/tag/release.
- Keep PEKAT UI round-trip explicitly manual and isolated.

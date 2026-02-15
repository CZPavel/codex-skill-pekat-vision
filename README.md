# PEKAT Vision Codex Skill

Custom skill for Codex focused on PEKAT Vision integration (Code module, REST API, SDK, and Projects Manager workflows).

## Repository Layout
- `SKILL.md`
- `agents/openai.yaml`
- `docs/`
- `scripts/`
- `tests/`

## Local Validation
```powershell
cd C:\Users\P.J\.codex\skills\pekat-vision
python -m pytest -q
```

## Install into Codex from GitHub
Use the built-in `skill-installer` script:

```powershell
python C:\Users\P.J\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo CZPavel/codex-skill-pekat-vision --path .
```

If `pekat-vision` already exists in `~/.codex/skills`, remove or rename it before reinstalling.

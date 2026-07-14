# Codex Skill: PEKAT VISION

Public, version-aware Codex skill for PEKAT VISION 3.19.3 and 4.0.1. It covers Code modules and Form Editor exports, Context/GlobalData migration, REST/SDK/Projects Manager, external runtime ABI and barcode libraries, and guarded IFM/IO-Link, PLC/Snap7, MX-G2000, and Baumer workflows.

## Canonical skill

The only publishable skill is `.github/skills/pekat-vision`. Domain scripts and references are not mirrored elsewhere in the repository.

Key capabilities:

- Generate validated `.pmodule` (3.19.3) and `.ptool` (4.0.1) files.
- Use `main(context, form=None)` for Form Editor modules and keep `operatorInput` separate.
- Build robust binary PNG REST clients with timeouts and guarded parsing.
- Match native libraries to PEKAT's Python ABI and architecture.
- Default industrial I/O and project lifecycle operations to read-only/dry-run.

## Installation

```powershell
$Installer = Join-Path $env:USERPROFILE ".codex\skills\.system\skill-installer\scripts\install-skill-from-github.py"
python $Installer --repo CZPavel/codex-skill-pekat-vision --ref v2.0.0 --path .github/skills/pekat-vision --name pekat-vision
```

The installer requires that the destination does not already exist. Back up and replace an existing installation outside synchronized/committed paths.

## Validation

```powershell
$Validator = Join-Path $env:USERPROFILE ".codex\skills\.system\skill-creator\scripts\quick_validate.py"
python $Validator .github/skills/pekat-vision
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The automated suite is offline and does not write to PEKAT, PLC, IO-Link, cameras, or Projects Manager. PEKAT UI import/display/edit/export round-trip remains a manual test in new isolated projects.

## Security

The skill contains sanitized derived notes and safe fixtures only. It excludes raw proprietary manuals, Confluence bodies, credentials, private addresses, real project identifiers, virtual environments, and Codex authentication/state.

Licensed under MIT; source documentation and device manuals retain their own terms.

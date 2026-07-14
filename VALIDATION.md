# Validation record

Date: 2026-07-14
Target: PEKAT Vision Codex Skill v2.0.0
Pre-publication status: **PASS**

## Automated validation

- [x] Official `quick_validate.py`: `Skill is valid!`
- [x] Python 3.11: `21 passed`
- [x] Python 3.13: `21 passed`
- [x] All canonical Python scripts compile with `compileall`.
- [x] The ModuleSpec suite covers both versions/extensions, four form types, value normalization, unknown `formValues`, unique IDs, and AST entrypoint validation.
- [x] Both export fixtures validate against `references/module_spec.schema.json`.
- [x] Context tests confirm the diagnostic template does not mutate `result`.
- [x] REST mocks cover success, timeout, HTTP error, invalid JSON, and an unavailable endpoint.
- [x] Industrial helpers remain dry-run/read-only unless mutation is explicitly approved.
- [x] The security test rejects private IPv4 addresses, unsafe TLS, unexpected resource types, and legacy `module_item` in Python.
- [x] The fixture set contains exactly 48 golden cases, including version mixing, invented IODD maps, and production-write requests.

## Read-only runtime fingerprint

The filesystem-only probe found both supported local installations without starting or modifying PEKAT:

| PEKAT | Architecture | Python ABI |
|---|---|---|
| 3.19.3 | AMD64 | `cp310` |
| 4.0.1 | AMD64 | `cp312` |

The exact local package inventory is intentionally not committed; the probe can reproduce it with:

```powershell
python .github/skills/pekat-vision/scripts/runtime_fingerprint.py
```

## Packaging gates

- [x] `.github/skills/pekat-vision` is the only canonical skill tree.
- [x] No root-level copies of domain scripts or references remain.
- [x] The skill tree contains no raw PDF, Confluence body, cache, venv, credential, private endpoint, or real project data.
- [x] Network and device tests are mocked and perform no writes.
- [x] GitHub Actions passes on the release PR for Python 3.11 and 3.13.
- [x] The release branch installs and validates through Skill Installer; all 17 canonical files match the published commit's Git blob IDs.
- [x] Tag `v2.0.0` installs, validates, and matches all 17 files in the release ZIP.

Published release evidence:

- Tag target: `adefc300218e4652f1ed82930bff648ceff3e91f`
- Release ZIP SHA256: `32bf7982e9559200a6da9a6a35351f2b64844503269fa4c9ef4b8bbc481fe39f`
- Release: <https://github.com/CZPavel/codex-skill-pekat-vision/releases/tag/v2.0.0>

All publication gates passed. The locally installed skill was validated after replacement; its 17 file hashes match the release archive.

## Manual acceptance boundary

Import/display/edit/export round-trip of both fixtures remains a manual acceptance test in new isolated PEKAT 3.19.3 and 4.0.1 projects. Existing projects and running flows must not be used.

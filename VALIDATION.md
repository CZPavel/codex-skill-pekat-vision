# Validation record

Date: 2026-08-13
Target: PEKAT VISION runtime diagnostics and Code tooling update
Status: **PASS for static/offline scope**

## New scope

- References: PEKAT 4.0.1 Code runtime/library matrix, library installation and ABI rules, project log troubleshooting, project diagnostics, and expanded documented communication routing.
- Helpers: read-only `analyze_pekat_log.py`, `pekat_project_diagnostics.py`, and `check_pekat_library_compat.py`.
- Tests: synthetic multiline/repeated log families, camera/model/filesystem routing, project metadata/anatomy/log handling, runtime-matrix regression, and wheel ABI/architecture classification.

## Runtime evidence represented by the skill

The machine-readable matrix records a direct PEKAT VISION 4.0.1 Code test on Windows AMD64 with CPython 3.12.12 / `cp312`: 46 of 58 targeted imports passed, 2 packages were present but failed import, 10 were unavailable, and 24 of 24 bounded functional smoke operations passed. Functional boundaries are recorded per package. This evidence belongs to the tested installation and is not projected onto PEKAT 3.x or every clean 4.0.1 installation.

## Current automated validation

- [x] Official `quick_validate.py`: `Skill is valid!`
- [x] Default Python suite: `47 passed`.
- [x] Python 3.11 isolated environment: `47 passed`.
- [x] Python 3.13 isolated environment: `47 passed`.
- [x] Canonical Python scripts compile.
- [x] Existing module/export, REST failure-path, Projects Manager and industrial safety regressions remain enabled.
- [x] FLOW analyzer still uses a restricted non-executing Pickle reader and reuses one parser for project diagnostics.
- [x] Machine data parses as JSON; skill metadata/references parse under the existing YAML/JSON regression tests.
- [x] Public bundle security scan and 48 golden routing fixtures remain enabled.
- [x] `git diff --check` passes.

## Evidence boundary

The log/project/library helper results above are unit-tested with synthetic local fixtures. They do not install packages, modify PEKAT, write a project database, start training, contact a PLC, or alter a camera. The 4.0.1 runtime matrix is prior direct PEKAT Code evidence; this repository validation does not repeat those PEKAT operations.

## Manual acceptance boundary

The following remain OPEN unless performed separately on an isolated exact-version target:

- PEKAT UI import/display/edit/run/export/reimport;
- live REST and SDK exchange;
- Projects Manager and Cross-PEKAT lifecycle/failure/reconnect behavior;
- installing a new package into the embedded server and validating its direct Code import/function;
- physical camera acquisition, IO-Link/PLC communication, and vision-system acceptance;
- direct project database modification (not implemented as a general feature).

Automated tests never start/stop PEKAT, mutate a project, or write to industrial hardware.

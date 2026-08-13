# Validation record

Date: 2026-08-13
Target: current PEKAT Vision Codex Skill update
Status: **PASS for static/offline scope**

## Regression baseline

- Existing baseline before this update: `21 passed` on Python 3.11.
- Existing functional tests were retained.
- New coverage targets version-aware entrypoints, Form normalization, safe Pickle rejection, recursive `modules.sort` including an empty branch, module states, Filter/Gate extraction, Code dependencies/side effects, ZIP input and separate `database_old` diff.

## Current automated validation

- [x] Official `quick_validate.py`: `Skill is valid!`
- [x] Python 3.11: `37 passed`
- [x] Python 3.13: `37 passed`
- [x] Canonical Python scripts compile.
- [x] ModuleSpec covers 3.19.3/4.0.1 extensions, entrypoint routing, four Form types, default/current-value handling, unique IDs and AST validation.
- [x] Existing REST mocks cover success, timeout, HTTP error, invalid JSON and unavailable endpoint.
- [x] FLOW analyzer uses no `pickle.load(s)`, rejects dangerous construction/execution opcodes, and runs on synthetic sanitized directory/ZIP fixtures.
- [x] Industrial helpers remain dry-run/read-only unless mutation is explicitly approved.
- [x] The 48-case golden routing fixture and bundle security scan remain passing.

## Behavior smoke coverage

The updated skill/router and references explicitly cover the requested behaviors: 3.19.3 branch stop; 4.0.1 Form threshold/PTool; database ZIP FLOW; inactive versus soft-deleted; same-project GlobalData; external image SDK/REST; Cross-PEKAT; O1D110/AL1306 routing; Basler routing; and vision-first FOV/lighting design.

Two clean `codex exec --ephemeral --sandbox read-only` sessions loaded the installed skill and passed representative prompts:

1. 3.19.3 `Still_OK` branch stop returned minimal Code and the correct signature evidence boundary.
2. A synthetic sanitized project ZIP was analyzed through the installed safe utility; recursive Parallelism/empty branch, active/disabled/soft-deleted state, Context Gate, Code dependencies and `database_old` diff were reported correctly without writes.

Codex emitted unrelated local warnings about another installed skill's YAML and a missing MCP program during shutdown; neither affected PEKAT skill discovery or the requested outputs.

This is a static content/routing review plus executable utility tests and two clean read-only Codex smoke sessions. It is not PEKAT runtime/UI proof.

## Manual acceptance boundary

The following remain OPEN unless performed separately on an isolated exact-version target:

- PEKAT UI import/display/edit/run/export/reimport;
- live REST and SDK exchange;
- Projects Manager and Cross-PEKAT failure/reconnect behavior;
- camera, IO-Link/PLC and physical vision-system acceptance;
- direct project DB modification (not implemented as a general feature).

Automated tests never start/stop PEKAT, mutate a project, or write to industrial hardware.

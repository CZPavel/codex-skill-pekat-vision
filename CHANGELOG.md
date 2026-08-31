# Changelog

## Unreleased - 2026-08-31

- Targeted PEKAT Assistant 3.x verified-evidence backport: added the standalone exact-4.0.3 CODE/Form `.ptool` generator subset and offline read-only source-state helper.
- Added project-wide Production/Simulation negative contract, source-state mappings, narrow 4.0.3 Conditional Gate recipe, provider-switch restore guard, stale `camera.status.notAvailable` gap, and capability/evidence discipline.
- Kept the skill standalone: no Assistant Host/UI, App Server/auth, Socket.IO/browser writer, generic DB/project writer, or PEKAT import operation was added.

## Unreleased - 2026-08-27

- Synchronized the current skill with RC1.4 exact PEKAT 4.0.3 evidence while preserving 3.18.x, 3.19.3/3.19.x, common 4.0.x, and exact 4.0.1 routing.
- Added the clean 4.0.3 Code/ML/GPU matrix, missing-package boundaries, and corrected `zxingcpp`/`pyzbar` local-add-on provenance.
- Added process-lifetime GlobalData, branch-order collision, inspection side-effect, Classifier-first-winner, zero-survivor, generated FLOW/Gate encoding, Folder, Saver, PTool, REST/readiness, and PEKAT-specific Basler guidance.
- Kept `module_spec.schema.json`, generator, template, REST/Projects Manager helpers, and `agents/openai.yaml` unchanged; exact 4.0.3 UI evidence does not silently extend generator support.
- Added focused RC1.4 semantic regressions and retained the no-browser/no-Socket.IO/no-Skill-2.0 boundary.

## Previous unreleased scope - 2026-08-14

- Added a three-layer PEKAT 4.0.1 Parallelism contract that separates custom Context, native result/overlay data, and the raster image.
- Added mutually exclusive Conditional Gate routing, empty original-image pass-through, bounded geometry guidance, GlobalData concurrency gates, and machine-readable semantic regressions.
- Added PEKAT 4.0.1 sequential image-replacement/changed-shape evidence and bounded OpenCV performance guidance.
- Closed the tested generated PTool import/open/run gate, retained reexport/reimport as open, and enforced native string `visibility: ""` with regression coverage.
- Added PEKAT 4.0.1 Code runtime libraries, package compatibility, project/log diagnostics, and expanded communication routing.
- Added standard-library log and project diagnostic helpers plus a read-only package/wheel compatibility checker.
- Added 3.18.x routing while keeping its export/database contracts explicitly open.
- Aligned Code signatures, PEKAT 4 Form default/current-state types and GlobalData guidance with current exact-version evidence.
- Added a restricted non-executing Pickle protocol-4 reader and offline FLOW/database ZIP analyzer with recursive Parallelism, module states, Filter/Gate, Code dependency/side-effect and `database_old` handling.
- Replaced the historical script catalog with small native-first recipes and a simplicity/complexity gate.
- Clarified REST/SDK/Projects Manager/Cross-PEKAT responsibilities and conditional reliability behavior.
- Added PEKAT-specific hardware routing plus vision-design feasibility guidance.
- Expanded regression coverage to 55 tests.

## 2.0.0 - 2026-07-14

- Breaking: replaced legacy `module_item` entrypoints with `main(context, form=None)` and `form or {}`.
- Added strict PEKAT 3.19.3/4.0.1 routing and Context/GlobalData migration guidance.
- Added validated ModuleSpec generation for `.pmodule` and `.ptool`, JSON Schema, and four-control fixtures.
- Reworked REST handling for binary PNG bodies, timeouts, HTTP failures, and response validation.
- Added read-only runtime ABI fingerprinting and fail-closed Projects Manager/industrial I/O helpers.
- Added curated references for 21 Code patterns, barcode, IFM/IO-Link, Snap7, MX-G2000, and Baumer.
- Consolidated all runtime skill content under `.github/skills/pekat-vision`.
- Added Python 3.11/3.13 CI, 48 golden cases, mock tests, and public bundle security checks.

## 1.0.0 - 2026-02-15

- Initial standalone PEKAT VISION skill.

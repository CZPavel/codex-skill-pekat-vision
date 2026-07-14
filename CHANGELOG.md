# Changelog

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

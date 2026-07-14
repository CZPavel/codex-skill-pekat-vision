---
name: pekat-vision
description: Version-aware integration and scripting for PEKAT VISION 3.19.3 and 4.0.1, including Code modules, Context, Form Editor, GlobalData migration, importable .pmodule/.ptool generation, REST API, SDK, Projects Manager, external Python ABI and barcode libraries, IFM/IO-Link, PLC/Snap7, MX-G2000, and Baumer VAX/PV50C. Use when Codex must implement, review, generate, migrate, or debug these PEKAT workflows. Do not use for unrelated frontend work or unapproved production/device writes.
---

# PEKAT VISION workflow

1. Determine the exact target: `3.19.3` or `4.0.1`. Ask before generating an import file if unknown.
2. Identify the flow position, Context keys read/written, image dtype/shape, intended `result` behavior, allowed libraries, and I/O safety boundary.
3. Read only the relevant bundled reference:
   - Version, Context, GlobalData, and migration: `references/version-context.md`
   - Form Editor, ModuleSpec, and import files: `references/module-format.md`
   - REST, SDK, Projects Manager, ABI, and barcode: `references/rest-sdk-runtime.md`
   - Curated Code patterns: `references/script-cookbook.md`
   - IFM, PLC, MX-G2000, and Baumer: `references/industrial-hardware.md`
4. Separate sourced facts from inference. Cite bundled document IDs. Never invent Context keys, APIs, IODD maps, PLC layouts, commands, or pinouts.
5. Generate a minimal safe implementation, then run the applicable bundled tests or an isolated mock.

## Code modules and forms

- Without Form Editor items, `main(context)` is valid.
- With Form Editor items, use `main(context, form=None)` and start with `values = form or {}`.
- Never treat `operatorInput` as Form Editor values. Never generate the legacy `module_item` signature.
- Preserve types of standard Context keys. Diagnostics must not change `context["result"]` unless explicitly requested.
- Set `context["exit"] = True` only for deliberate branch termination.
- Do not recommend process-global state as a cross-frame contract. Route persistent-state questions by version; GlobalData is a 4.0.1 concept.

Use `scripts/generate_code_module.py` for importable files. It validates ModuleSpec, Python AST, form types, values, IDs, version, and extension. Return the standalone Python, a form table, the generated file, and isolated import/test instructions.

## Network, runtime, and industrial safety

- Use `localhost` or TEST-NET addresses in examples. Never emit credentials or private project identifiers.
- Send PNG REST bodies as bytes in `data=` with `Content-Type: application/octet-stream`, bounded timeouts, HTTP checks, and guarded response parsing.
- Match native wheels to target Python ABI and architecture. The audited PC fingerprint was `cp310` for 3.19.3 and `cp312` for 4.0.1; re-probe other installations.
- Default Projects Manager, PLC, IO-Link, and camera operations to read-only or `dry_run=True`. Require explicit approval, an exact source map/manual, backup, isolated target, and rollback before writes.
- Do not start/stop PEKAT or modify an existing project unless the user explicitly authorizes that exact action.

## Delivery checklist

- Target version and evidence are explicit.
- Code parses and mock Context tests pass.
- Form values and import extension match the target.
- Timeouts and failure paths are tested.
- No credential, private IP, unsafe default, or accidental `result` mutation is present.
- PEKAT UI import/display/edit/export remains a manual isolated-project acceptance gate.

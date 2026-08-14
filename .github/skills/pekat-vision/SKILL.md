---
name: pekat-vision
description: Version-aware PEKAT VISION 3.18.x, 3.19.3, and 4.0.1 work for Code, Context/GlobalData, Form Editor, .pmodule/.ptool, FLOW/database analysis, project/log diagnostics, PEKAT 4 Code libraries and package compatibility, REST/SDK, Projects Manager/Simple TCP, Cross-PEKAT, Outputs, cameras, PLC/IO-Link, and troubleshooting. Use when Codex must design, generate, analyze, integrate, diagnose, migrate, or safely operate on a PEKAT application or project. Do not use for unrelated frontend work or unapproved live/device/project writes.
---

# PEKAT VISION workflow

1. Establish the target version or infer it only from explicit project/export metadata. Support `3.18.x`, `3.19.3`, and `4.0.1`; never infer a version from one legacy DB field.
2. For a failure, identify project/version, symptom and relevant log session before changing FLOW. Separate server, camera, model, filesystem and evaluation states.
3. Choose the simplest working route: native PEKAT feature, simple FLOW, NumPy/OpenCV Code, specialized library, then heavy ML/new dependency only when justified.
4. State the evidence class for consequential claims: documented, runtime/UI tested, observed/static, practical evidence, or unknown/open gate.
5. Read only the relevant reference:
   - Version, Context, `result`/`exit`, GlobalData, migration: `references/version-context.md`
   - `.pmodule`, `.ptool`, Form runtime and generation: `references/module-format.md`
   - FLOW, `modules.db`, `modules.sort`, `database_old`: `references/flow-database-projects.md`
   - Project metadata/runtime/anatomy and `running.db` boundary: `references/project-diagnostics.md`
   - Project `output.log` grouping and troubleshooting: `references/log-troubleshooting.md`
   - PEKAT 4.0.1 Code runtime and verified/importable/missing libraries: `references/code-runtime-pekat401.md`
   - Adding a library, `cp312`/wheel compatibility and export dependency rules: `references/code-library-installation.md`
   - REST, SDK, Projects Manager and Cross-PEKAT: `references/rest-sdk-runtime.md`
   - Minimal Code recipes: `references/script-cookbook.md`
   - MX-G2000, smart cameras, Basler and IFM routing: `references/industrial-hardware.md`
   - FOV, optics, lighting, motion, dataset and acceptance: `references/vision-design-routing.md`
6. Declare Context/Form inputs, outputs, dependency/version assumptions, state lifetime, side effects, timeouts, and safety boundary before implementation.
7. Validate locally with the bundled utility/test appropriate to the artifact; never describe static/unit validation as PEKAT runtime proof.

## Code and export contract

- Do not invent one universal `main(...)` signature. For 4.0.1 use runtime-tested `main(context)` without Form and `main(context, form)` with Form. For 3.19.3, `main(context)` is a safe current no-Form pattern, while a fresh UI record also stored `main(context, form)` with an empty Form; runtime round-trip remains open. Treat 3.18 signatures/export schema as version-specific/open.
- Keep generated Code short: no `__main__` persistence, infinite loops, customer paths/IPs, unnecessary classes, or hidden side effects.
- Preserve standard Context types. Change `result` only when requested; set `exit=True` only for deliberate termination of the current branch. Form is not `operatorInput`.
- In PEKAT 4.0.1 sequential FLOW, `context["image"] = output` may replace the image with a new NumPy ndarray and a different shape; validate dtype/channels and every downstream consumer. Parallel branch merge/copy behavior remains open.
- Use GlobalData only as the version-scoped PEKAT 4 project state contract. Use Context for one evaluation and Cross-PEKAT/REST/SDK for project boundaries.
- Normalize Form number/select values when type affects logic. Keep `defaultValue` distinct from saved current `formValues`.
- Use `scripts/generate_code_module.py` for 3.19.3 `.pmodule` or 4.0.1 `.ptool`. Do not generate a 3.18 export without exact evidence.
- For a new 4.0.1 unconditional Form field, preserve native serialization `"visibility": ""`; never emit a boolean. Generated PTool import/open/run is runtime/UI verified for one Code/Form use case, while its subsequent reexport/reimport remains open.
- For 4.0.1 dependencies, consult the directly tested library matrix. An export does not package an arbitrary Python dependency; state the required import/version/ABI and retest it in Code on the destination PC.

## FLOW/database contract

- For a project or database ZIP, run `scripts/analyze_flow_database.py <path> [--output report.json]`. It reads only primitive/container Pickle protocol-4 opcodes and rejects object construction/execution opcodes; never replace it with `pickle.load()` on user data.
- Treat `modules.items` as the registry and `modules.sort` as observed live topology. Parse integers as module IDs, nested list nodes as Parallelism, their items as branches, and `[]` as an empty branch. This is observed project evidence, not a public vendor API.
- Active candidate: ID in `sort`, `softDeletedDate is None`, and `isActive` not explicitly `False`. Missing `isActive` is not disabled. Report disabled and soft-deleted records separately.
- Analyze `database_old` separately as historical/pre-upgrade evidence, not live FLOW. Prefer analysis/dry-run/patch design before any experimental DB writer.

## Runtime and industrial safety

- For local troubleshooting, run `scripts/analyze_pekat_log.py` and/or `scripts/pekat_project_diagnostics.py`. Never infer a live server from `running.db` alone; correlate metadata, process, port and logs when needed.
- Distinguish REST/SDK (running-project inference), Projects Manager/Simple TCP (lifecycle), Cross-PEKAT (between projects), GlobalData (within one PEKAT 4 project), and PEKAT Output HTTP/CMD/TCP/S7 (simple external output).
- Use bounded timeouts and explicit error handling. Do not automatically add retries or health frameworks.
- For a new library, identify exact version/ABI, inspect pure/native wheel and dependencies, stage only through an evidence-backed approved method, then require direct Code import and preferably a minimal functional call. Never auto-install during diagnosis.
- Default Projects Manager, PLC, IO-Link, camera, and project changes to read-only/dry-run. Require explicit approval, exact mapping/manual, backup, isolated target, readback, and rollback before writes.
- Use `pekat-vision` for PEKAT-side integration; route deep pylon/camera work to `basler-cameras` and exact IODD/device work to `ifm-io-link` when available.
- If the problem is actually FOV, px/mm, optics, DoF, blur, lighting, trigger, line rate, dataset, false accept/reject, or repeatability, solve that physical/measurement constraint before prescribing a complex FLOW.

## Delivery check

- Version and evidence limits are explicit.
- Code/JSON/Pickle parsing is bounded and tested; no user Code or Pickle callable executes.
- Context/Form/state and side effects are documented.
- No credentials, private endpoint, customer identifier, or unsafe write default is present.
- PEKAT 4.0.1 generated PTool reexport/reimport, other exact-version UI gates, live REST/SDK, and physical hardware acceptance remain explicit manual gates unless actually performed.

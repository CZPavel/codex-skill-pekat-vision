---
name: pekat-vision
description: Version-aware PEKAT VISION 3.18.x, 3.19.3, and 4.0.1 integration for Code, Context/GlobalData, Form Editor, .pmodule/.ptool, FLOW and safe database ZIP analysis, migration history, REST/SDK/Projects Manager/Cross-PEKAT, MX-G2000 and smart cameras, and PEKAT-specific Basler or IFM/IO-Link routing. Use when Codex must design, generate, analyze, migrate, or troubleshoot a PEKAT vision application or project. Do not use for unrelated frontend work, PEKAT web-UI reverse engineering, or unapproved live/device writes.
---

# PEKAT VISION workflow

1. Establish the target version or infer it only from explicit project/export metadata. Support `3.18.x`, `3.19.3`, and `4.0.1`; never infer a version from one legacy DB field.
2. Choose the simplest working route: native PEKAT feature before Code/FLOW workaround, and a small readable Code module before a framework. Add retry, heartbeat, watchdog, cache, state machine, or fallback only for a concrete requirement or observed failure.
3. State the evidence class for consequential claims: documented, runtime/UI tested, static/reverse-engineered, practical evidence, or unknown/open gate.
4. Read only the relevant reference:
   - Version, Context, `result`/`exit`, GlobalData, migration: `references/version-context.md`
   - `.pmodule`, `.ptool`, Form runtime and generation: `references/module-format.md`
   - FLOW, `modules.db`, `modules.sort`, `database_old`: `references/flow-database-projects.md`
   - REST, SDK, Projects Manager and Cross-PEKAT: `references/rest-sdk-runtime.md`
   - Minimal Code recipes: `references/script-cookbook.md`
   - MX-G2000, smart cameras, Basler and IFM routing: `references/industrial-hardware.md`
   - FOV, optics, lighting, motion, dataset and acceptance: `references/vision-design-routing.md`
5. Declare Context/Form inputs, outputs, state lifetime, side effects, timeouts, and safety boundary before implementation.
6. Validate locally with the bundled utility/test appropriate to the artifact; never describe static validation as PEKAT runtime proof.

## Code and export contract

- Do not invent one universal `main(...)` signature. For 4.0.1 use runtime-tested `main(context)` without Form and `main(context, form)` with Form. For 3.19.3, `main(context)` is a safe current no-Form pattern, while a fresh UI record also stored `main(context, form)` with an empty Form; runtime round-trip remains open. Treat 3.18 signatures/export schema as version-specific/open.
- Keep generated Code short: no `__main__` persistence, infinite loops, customer paths/IPs, unnecessary classes, or hidden side effects.
- Preserve standard Context types. Change `result` only when requested; set `exit=True` only for deliberate termination of the current branch. Form is not `operatorInput`.
- Use GlobalData only as the version-scoped PEKAT 4 project state contract. Use Context for one evaluation and Cross-PEKAT/REST/SDK for project boundaries.
- Normalize Form number/select values when type affects logic. Keep `defaultValue` distinct from saved current `formValues`.
- Use `scripts/generate_code_module.py` for 3.19.3 `.pmodule` or 4.0.1 `.ptool`. Do not generate a 3.18 export without exact evidence.

## FLOW/database contract

- For a project or database ZIP, run `scripts/analyze_flow_database.py <path> [--output report.json]`. It reads only primitive/container Pickle protocol-4 opcodes and rejects object construction/execution opcodes; never replace it with `pickle.load()` on user data.
- Treat `modules.items` as the registry and `modules.sort` as observed live topology. Parse integers as module IDs, nested list nodes as Parallelism, their items as branches, and `[]` as an empty branch. This is reverse-engineered evidence, not a public vendor API.
- Active candidate: ID in `sort`, `softDeletedDate is None`, and `isActive` not explicitly `False`. Missing `isActive` is not disabled. Report disabled and soft-deleted records separately.
- Analyze `database_old` separately as historical/pre-upgrade evidence, not live FLOW. Prefer analysis/dry-run/patch design before any experimental DB writer.

## Runtime and industrial safety

- Distinguish REST/SDK (running project), Projects Manager (lifecycle), Cross-PEKAT (between projects), GlobalData (within one PEKAT 4 project), and PEKAT Output (simple external output).
- Use bounded timeouts and explicit error handling. Do not automatically add retries or health frameworks.
- Default Projects Manager, PLC, IO-Link, camera, and project changes to read-only/dry-run. Require explicit approval, exact mapping/manual, backup, isolated target, readback, and rollback before writes.
- Use `pekat-vision` for PEKAT-side integration; route deep pylon/camera work to `basler-cameras` and exact IODD/device work to `ifm-io-link` when available.
- If the problem is actually FOV, px/mm, optics, DoF, blur, lighting, trigger, line rate, dataset, false accept/reject, or repeatability, solve that physical/measurement constraint before prescribing a complex FLOW.

## Delivery check

- Version and evidence limits are explicit.
- Code/JSON/Pickle parsing is bounded and tested; no user Code or Pickle callable executes.
- Context/Form/state and side effects are documented.
- No credentials, private endpoint, customer identifier, or unsafe write default is present.
- PEKAT UI import/reimport, live REST/SDK, and physical hardware acceptance remain explicit manual gates unless actually performed.

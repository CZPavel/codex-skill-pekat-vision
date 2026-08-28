---
name: pekat-vision
description: Version-aware PEKAT VISION 3.18.x, 3.19.x, and 4.0.x work, including exact 3.19.3, 4.0.1, and 4.0.3 evidence, for Code, Context/GlobalData, Form Editor, .pmodule/.ptool, FLOW/database analysis, project/log diagnostics, Code libraries, REST/SDK, Projects Manager/Simple TCP, Cross-PEKAT, Outputs, cameras, PLC/IO-Link, and troubleshooting. Use when Codex must design, generate, analyze, integrate, diagnose, migrate, or safely operate on a PEKAT application or project. Do not use for unrelated frontend work, internal Socket.IO/browser authoring, Skill 2.0 orchestration, or unapproved live/device/project writes.
---

# PEKAT VISION workflow

1. Establish the target version or infer it only from explicit project/export metadata. Route `3.18.x`, `3.19.x` (exact `3.19.3`), and the common `4.0.x` contract with exact `4.0.1`/`4.0.3` evidence; never flatten exact-version differences or infer a version from one legacy DB field.
2. For a failure, identify project/version, symptom and relevant log session before changing FLOW. Separate server, camera, model, filesystem and evaluation states.
3. Before redesigning an existing project, reconstruct the complete relevant FLOW and its behavioral contract, including continuation after joins and empty-branch roles. State **MUST PRESERVE** and **INTENTIONAL CHANGE**; preserve observable I/O, filenames/folders, compression, annotations, Form controls and side effects. Classify custom complexity as required behavior, relevant compatibility, proven redundancy or actual overengineering before removing it.
4. Choose the simplest working route: native PEKAT feature, simple FLOW, NumPy/OpenCV Code, specialized library, then heavy ML/new dependency only when justified. Replace custom behavior with a native feature only after all required observable behavior is feature-equivalent or the user accepts the change.
5. State the evidence class for consequential claims: documented, runtime/UI tested, observed/static, practical evidence, or unknown/open gate. Do not request a test that merely reconfirms already established exact-version behavior; test only a material unresolved dimension.
6. Read only the relevant reference:
   - Version, Context, Parallelism data layers, `result`/`exit`, GlobalData, migration: `references/version-context.md`
   - `.pmodule`, `.ptool`, Form runtime and generation: `references/module-format.md`
   - FLOW, `modules.db`, `modules.sort`, `database_old`: `references/flow-database-projects.md`
   - Project metadata/runtime/anatomy and `running.db` boundary: `references/project-diagnostics.md`
   - Project `output.log` grouping and troubleshooting: `references/log-troubleshooting.md`
   - PEKAT 4.0.1 Code runtime and verified/importable/missing libraries: `references/code-runtime-pekat401.md`
   - Clean tested PEKAT 4.0.3 Code/ML/GPU package matrix and boundaries: `references/code-runtime-pekat403.md`
   - Adding a library, `cp312`/wheel compatibility and export dependency rules: `references/code-library-installation.md`
   - REST, SDK, Projects Manager and Cross-PEKAT: `references/rest-sdk-runtime.md`
   - Minimal Code recipes: `references/script-cookbook.md`
   - MX-G2000, smart cameras, Basler and IFM routing: `references/industrial-hardware.md`
   - FOV, optics, lighting, motion, dataset and acceptance: `references/vision-design-routing.md`
7. Declare Context/Form inputs, outputs, dependency/version assumptions, state lifetime, side effects, timeouts, and safety boundary before implementation.
8. Validate locally with the bundled utility/test appropriate to the artifact; never describe static/unit validation as PEKAT runtime proof.

## Code and export contract

- Do not invent one universal `main(...)` signature. For 4.0.1 use runtime-tested `main(context)` without Form and `main(context, form)` with Form. For 3.19.3, `main(context)` is a safe current no-Form pattern, while a fresh UI record also stored `main(context, form)` with an empty Form; runtime round-trip remains open. Treat 3.18 signatures/export schema as version-specific/open.
- Keep generated Code short: no `__main__` persistence, infinite loops, customer paths/IPs, unnecessary classes, or hidden side effects.
- Preserve standard Context types. Change `result` only when requested; set `exit=True` only for deliberate termination of the current branch. Form is not `operatorInput`.
- In PEKAT 4.0.1 sequential FLOW, `context["image"] = output` may replace the image with a new NumPy ndarray and a different shape; validate dtype/channels and every downstream consumer. Do not infer a universal parallel image-winner or geometry-remap contract.
- In experimentally tested PEKAT 4.0.1, custom Context propagates sequentially but branch changes do not survive a true multi-branch join, including equal-value writes. Do not invent first/last-writer, union, or consensus merge. A mutually exclusive Conditional Gate router with exactly one continuing branch may propagate that branch's custom Context. In exact 4.0.3 zero-survivor tests, downstream FLOW could continue from the pre-parallel Context; all branch exits do not automatically terminate the whole FLOW.
- Capturing `context["cap_raw_result"] = context.get("result")` is valid for sequential downstream or branch-local use before a join; it is not a mechanism for propagating custom Context through a true multi-branch join.
- Keep three layers separate: custom `context["X"]`, PEKAT-native `result`/detections/classes/heatmaps, and raster `context["image"]`. Prefer native `result` for parallel OK/NOK. Native overlays are not automatically drawn into image pixels.
- Do not remove an empty branch by default: it may pass the original/pre-transform image to UI or Image Saver while detector branches crop/preprocess. It also contributes to true multi-branch custom-Context semantics. Gate FALSE and a disabled/no-op branch are not equivalent to empty.
- Use GlobalData only as the version-scoped PEKAT 4 project state contract. It persists across evaluations in one project-server process, resets on project-server restart, and is not durable storage. Use Context for one evaluation and Cross-PEKAT/REST/SDK for project boundaries.
- Do not use GlobalData as an automatic parallel merge workaround. Exact 4.0.3 tests found that independent branch keys may survive and same-key collision was branch-order dependent, not wall-clock dependent; prefer branch-specific keys plus an explicit merge.
- For Classifier output, treat the first `classNames` element as the reproduced PEKAT 4 winner after checking for an empty list. Never select the winner by testing whether any candidate has a wanted label; keep Detector semantics separate.
- Normalize Form number/select values when type affects logic. Keep `defaultValue` distinct from saved current `formValues`.
- Use `scripts/generate_code_module.py` only for its currently validated targets: 3.19.3 `.pmodule` or 4.0.1 `.ptool`. Exact 4.0.3 UI PTool round-trip evidence does not by itself extend that generator/schema. Do not generate a 3.18 export without exact evidence.
- For a new 4.0.1 unconditional Form field, preserve native serialization `"visibility": ""`; never emit a boolean. Generated PTool import/open/run is runtime/UI verified for one Code/Form use case, while its subsequent reexport/reimport remains open.
- For 4.0.x dependencies, consult the exact-version matrix. `zxingcpp` and `pyzbar` were local post-install additions in the tested 4.0.1 installation and absent in clean tested 4.0.3; they are not bundled, their absence is not a vendor regression, and a PTool does not carry them. State the required import/version/ABI, distinguish a clean baseline from local modification, and retest in destination Code.

## FLOW/database contract

- For a project or database ZIP, run `scripts/analyze_flow_database.py <path> [--output report.json]`. It reads only primitive/container Pickle protocol-4 opcodes and rejects object construction/execution opcodes; never replace it with `pickle.load()` on user data.
- Treat `modules.items` as the registry and `modules.sort` as observed live topology. Parse integers as module IDs, nested list nodes as Parallelism, their items as branches, and `[]` as an empty branch. This is observed project evidence, not a public vendor API.
- Generated 4.0.1 `modules.db` evidence covers recursive/nested topology plus Code, Detector, OCR, internal `FILTER`, Mask, structural Image Saver, and explicit `modelId`. Keep direct DB generation exact-version, internal, fixture-backed, and outside the normal public authoring route. For that exact Gate fixture, `classname = local_class_id * 2^42 + source_module_id`; do not reverse the IDs or generalize the encoding.
- Active candidate: ID in `sort`, `softDeletedDate is None`, and `isActive` not explicitly `False`. Missing `isActive` is not disabled. Report disabled and soft-deleted records separately.
- Analyze `database_old` separately as historical/pre-upgrade evidence, not live FLOW. Prefer analysis/dry-run/patch design before any experimental DB writer.

## Runtime and industrial safety

- For local troubleshooting, run `scripts/analyze_pekat_log.py` and/or `scripts/pekat_project_diagnostics.py`. Never infer readiness from `running.db`, `cameraIsRunning`, or saved provider state alone; correlate process/PID, listening port, `/ping`, inference/model readiness, and camera/provider live state.
- Distinguish REST/SDK (running-project inference), Projects Manager/Simple TCP (lifecycle), Cross-PEKAT (between projects), GlobalData (within one PEKAT 4 project), and PEKAT Output HTTP/CMD/TCP/S7 (simple external output).
- Use bounded timeouts and explicit error handling. Do not automatically add retries or health frameworks.
- Keep simple current-state Cross-PEKAT master/contributor exchange as the default when sufficient. Add timestamp/heartbeat/freshness/cycle or product identifiers only for actual stale-state detection, communication-loss detection, exact pairing, or another explicit application contract.
- For a new library, identify exact version/ABI, inspect pure/native wheel and dependencies, stage only through an evidence-backed approved method, then require direct Code import and preferably a minimal functional call. Never auto-install during diagnosis.
- Prefer native Image Saver when feature-equivalent. In exact 4.0.3, `ALL` + local + `by_days` + `image_only` persisted PNGs only when the root already existed; HTTP/context success did not prove filesystem persistence and a missing root could be log-only.
- Treat internal `inspection:getContext`/`inspection:getFlow` as potentially evaluation-triggering, not behaviorally passive, when FLOW has Code, GlobalData, or I/O side effects. Do not promote internal Socket.IO or browser-driven project authoring into the normal workflow.
- Default Projects Manager, PLC, IO-Link, camera, and project changes to read-only/dry-run. Require explicit approval, exact mapping/manual, backup, isolated target, readback, and rollback before writes.
- Use `pekat-vision` for PEKAT-side integration; route deep pylon/camera work to `basler-cameras` and exact IODD/device work to `ifm-io-link` when available.
- If the problem is actually FOV, px/mm, optics, DoF, blur, lighting, trigger, line rate, dataset, false accept/reject, or repeatability, solve that physical/measurement constraint before prescribing a complex FLOW.

## Delivery check

- Version and evidence limits are explicit.
- Code/JSON/Pickle parsing is bounded and tested; no user Code or Pickle callable executes.
- Context/Form/state and side effects are documented.
- No credentials, private endpoint, customer identifier, or unsafe write default is present.
- Exact-version evidence and open gates are not mixed: 4.0.3 PTool full UI round-trip and bounded public REST runtime are closed only for their tested fixtures, while untested Saver variants, 3.19.3 PModule round-trip, other runtime/HW cases, and physical acceptance stay explicit gates.

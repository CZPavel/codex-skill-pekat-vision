# PEKAT VISION public Codex skill — usage and capability guide

Updated 2026-11-09. This document describes what the **standalone public skill** can do for a Codex user. It is distinct from the separately developed PEKAT Assistant application.

## What is shipped

This repository includes version-scoped knowledge, Code/Form/PTool guidance, reference material and executable **offline analysis scripts**. Its scripts operate on explicitly supplied local input, do not require an active PEKAT project and do not perform unapproved project or device actions.

The separate [public PEKAT Assistant](https://github.com/CZPavel/PEKAT-Assistant) presents a more approachable knowledge/GPT interface and end-user scenarios. Both editions should share engineering conclusions; they should not independently invent conflicting capability claims.

The separately developed Assistant Core includes more advanced bounded operations, but these **are not shipped by installing this public skill**.

## User requests and recommended routes

| Request to Codex | Public skill route | Expected result |
|---|---|---|
| "Help me design an inspection for this defect" | vision-design-routing.md, version-context.md | Acquisition, method, FLOW and evidence plan |
| "Explain this supplied FLOW/project" | flow-database-projects.md; analyze_flow_database.py | Offline explanation and diagnostic report, within supported input scope |
| "Draft a PEKAT Code or PTool" | module-format.md; script-cookbook.md | Readable version-correct draft, inputs/outputs and verification steps |
| "Why does the result change across branches?" | version-context.md and FLOW guidance | Explicit separation of image data, native results and shared application state |
| "Find the likely cause in these logs" | analyze_pekat_log.py; log-troubleshooting.md | Time/component/incident correlation and diagnostic hypotheses |
| "Check a project startup/source problem" | pekat_project_diagnostics.py; analyze_source_state_403.py | Offline or read-only observations and targeted troubleshooting steps |
| "Review my dataset or model metadata" | inspect_dataset_model.py; dataset-model-inspection.md | Inventory, provenance and possible QA gaps |
| "Interpret a model training run" | analyze_training_history.py; training-history-diagnostics.md | Family-specific summary with uncertainty, without a new training run |
| "Can this Python library work in PEKAT Code?" | check_pekat_library_compat.py; code-library-installation.md | Target-version compatibility assessment and a minimal import test |
| "Plan camera/sensor integration" | rest-sdk-runtime.md, industrial-hardware.md, vision-design-routing.md | Ownership, timing, quality, REST/SDK and safety requirements |

Use the existing scripts instead of writing another parser or diagnostic utility for the same task. Scripts should be run on user-authorized input only.

## Public workflows

### Design from images and a control objective
1. Define the feature, defect and measurable OK/NOK acceptance criteria.
2. Check whether optics, lighting, exposure, trigger and pose give usable information.
3. Compare classic computer vision/geometry with Detector, Classifier, OCR, anomaly or surface tools.
4. Propose the smallest useful sequential or branched FLOW; note Context, results, overlays and frame identity separately.
5. Provide a test plan with expected failure cases and data requirements.

### Review an existing PEKAT application
1. Establish exact PEKAT version and intended observable behavior.
2. Inspect only supplied, authorized project exports, screenshots, Code and reports.
3. Explain active behavior, dependencies, state lifetime and external side effects.
4. Identify the smallest safe change and what must remain unchanged.
5. Use offline scripts for additional evidence; do not infer that a report authorizes changing a live project.

### Diagnose an unstable result
1. State symptom, source type, frame identity, timestamp and expected result.
2. Separate acquisition failures, image changes, evaluation logic, model uncertainty and output delivery.
3. Prefer an existing filtered log or training-history analyzer when applicable.
4. Name the lowest-risk discriminating check and its expected observation.
5. Treat unobserved runtime or hardware behavior as unknown.

### Draft Code, PTool or Form
1. Start from the target PEKAT version and accepted entry point.
2. Declare Form keys, defaults, units, Context inputs, outputs and dependency requirements.
3. Handle missing/invalid values and shared-state freshness; preserve existing working behavior.
4. Generate readable source with a small offline test.
5. Require actual target-version validation before claiming a successful import or runtime execution.

## Evidence boundaries

- PEKAT 3.18.x and 3.19.x include general guidance; exact evidence may be limited to 3.19.3.
- 4.0.1 and 4.0.3 include separate observed and tested examples. A newer 4.x release requires a new compatibility check.
- A documented PEKAT feature, an offline script, a private Assistant Core action and a physically accepted inspection are different things.
- The public skill does not include a generic FLOW writer, live training controller, automatic model activation, device control or private application installer.
- The current scope of a tool is determined by its actual shipped code and tests, not by a roadmap entry.

## Next development directions

1. **Public knowledge parity:** carry forward approved, version-scoped lessons from the canonical PEKAT Assistant project, with no customer data or proprietary implementation descriptions.
2. **Better offline tools:** improve error handling, sample fixtures and readable diagnostics without replacing already working scripts.
3. **Shared examples:** provide reproducible Code/PTool and inspection-design cases, including comparisons of native PEKAT operations and auxiliary code.
4. **Optional public Assistant integration:** let the public Assistant reuse this skill's knowledge/offline tools rather than duplicating and diverging.
5. **Future supported interfaces:** evaluate any officially available PEKAT integration interfaces for narrowly permissioned workflows; MCP may serve as a future adapter when available.

These are directions, not published features or delivery commitments.

## Privacy and safe use

Use synthetic or permission-cleared examples. Strip customer names, addresses, host/device IDs, credentials, production configurations and personal data before sharing inputs or results. Present observable behavior and supported user operations; do not republish proprietary implementation material.

See the [public PEKAT Assistant capability guide](https://github.com/CZPavel/PEKAT-Assistant/blob/main/docs/PUBLIC_CAPABILITY_GUIDE.md) once its corresponding documentation update is merged. Until then consult the guide in the companion review branch.

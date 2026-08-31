# Validation record

## Unreleased - 2026-08-31

Targeted PEKAT Assistant 3.x verified-evidence backport and 4.0.x family normalization. The public bundle has one offline Form payload serializer for the 4.0.1/4.0.3 evidence anchors; the exact-4.0.3 CODE/Form acceptance remains a narrow target guard. The restricted-parser source-state reader remains exact 4.0.3 because retained evidence does not establish every stored mapping across the family. It does not include Assistant runtime architecture, private evidence, PEKAT transport or any writer.

Final local validation is recorded with this change: complete pytest, compileall, official skill validation, public bundle/security checks and diff check. The source-state helper accepts only exact 4.0.3 primitive/container Pickle data and reports runtime state as unknown/not checked.

---

Date: 2026-08-27

Target: current `pekat-vision` skill synchronized with PEKAT Agent RC1.4

Status: **PASS for static/offline skill scope**

## Source and baseline

- Primary knowledge source:
  `C:\VS_CODE_PROJECTS\PEKAT_AGENT_DATA_MAKE\07_build\PEKAT_AGENT_KNOWLEDGE_RC1_4_2026-08-27`
- Skill repository HEAD before changes:
  `135afe03dcd2c64f58269a3dd2f64549bdb0a68b`
- Baseline official `quick_validate.py`: `Skill is valid!`
- Baseline default suite: `55 passed`.
- Baseline canonical scripts compile and `git diff --check` passes.

## Historical RC1.4 knowledge synchronized (superseded where noted above)

- Version routing preserves 3.18.x, 3.19.3/3.19.x, common 4.0.x, and exact
  4.0.1/4.0.3 evidence without flattening package/runtime differences.
- A clean tested 4.0.3 matrix records CPython 3.12.12, exact core libraries,
  Torch CUDA PASS, bounded torchvision/timm/FAISS/ONNX/TensorRT evidence, and
  targeted packages not present.
- `zxingcpp`/`pyzbar` are corrected to local post-install 4.0.1 additions, not
  bundled libraries or a 4.0.3 vendor regression; PTool dependency transport
  remains explicitly false.
- Additional-library guidance starts from exact embedded Python/current package
  state, uses a minimal approved install only when needed, requires Code import
  plus functional smoke, and records the resulting local modification.
- GlobalData process lifetime/restart reset, independent branch keys, same-key
  branch-order collision, inspection-triggered evaluation, Classifier first
  winner, and zero-survivor continuation are exact-scope routed.
- Generated 4.0.1 `modules.db`, recursive/nested `modules.sort`, `[]`, covered
  module families, explicit `modelId`, correct Gate encoding, and the
  exact-version/internal/fixture-backed boundary are represented.
- Exact 4.0.3 PTool full UI round-trip, Folder filename-only `data`, native
  Image Saver persistence/error boundary, public REST quirks, readiness chain,
  and PEKAT-specific Basler facts are represented with remaining gates intact.

## Preserved capabilities and reviewed unchanged files

MUST PRESERVE behavior remains: native PEKAT and clear FLOW first, small Code
before a larger mechanism, version-aware Code/PModule/PTool, static export
validation, cookbook, public REST/SDK/TCP, FLOW/database and log/project
diagnostics, library installation troubleshooting, and specialized Basler/IFM
routing.

Reviewed and unchanged:

- `.github/skills/pekat-vision/references/module_spec.schema.json`;
- `.github/skills/pekat-vision/scripts/code_module_template.py`;
- `.github/skills/pekat-vision/scripts/generate_code_module.py`;
- `.github/skills/pekat-vision/scripts/rest_api_client_demo.py`;
- `.github/skills/pekat-vision/scripts/projects_manager_tcp_demo.py`;
- `.github/skills/pekat-vision/agents/openai.yaml`;
- existing `.pmodule`/`.ptool` fixtures.

Historical 2026-08-27 position: the generator advertised only 3.19.3 and
4.0.1. This was superseded on 2026-08-31 by later exact 4.0.3 CODE/Form
serializer acceptance; see the current Unreleased section above.

## Targeted regression coverage

`tests/test_rc14_guidance.py` adds 12 focused tests for exact 4.0.3 routing and
runtime levels; Classifier winner selection; barcode provenance; additional
library workflow; GlobalData/Inspection/zero-survivor behavior; generated DB and
Gate encoding; PTool without schema invention; Folder/Saver; REST/readiness;
Basler routing; and the Skill 2.0/Socket.IO exclusion.

The existing machine-readable Parallelism regression was intentionally updated
from the formerly open GlobalData/zero-survivor gates to the exact 4.0.3 result.

## Final automated validation

- [x] Focused RC1.4 skill tests: `12 passed`.
- [x] Full default skill suite: `67 passed`.
- [x] Existing module/export, REST failure-path, Projects Manager, analyzer,
  industrial safety, bundle-security, and 48 golden routing regressions remain
  enabled.
- [x] Final official `quick_validate.py`: `Skill is valid!`.
- [x] Canonical skill scripts compile.
- [x] `git diff --check` passes (line-ending conversion notices only).
- [x] PEKAT Agent RC1.4 focused suite: `7 tests`, `OK`.

## Scope boundary

Static/offline tests do not repeat PEKAT runtime, UI, camera, GPU, REST, or
filesystem side-effect experiments. No package was installed; no PEKAT project,
database, process, camera, Detector, PLC, output, or endpoint was mutated.

Skill 2.0, browser/CDP/Playwright authoring, internal Socket.IO authoring,
`update_flow`/`set_store` automation, autonomous Projects Manager control,
autonomous camera/Detector mutation, and MCP/live orchestration were **NOT
STARTED**.

## Remaining manual gates

- clean PEKAT 3.18 database/export/Form fixture;
- 3.19.3 PModule full round-trip;
- reexport/reimport of the specific generated 4.0.1 PTool;
- branch-local A1→A2 and generalized native-result merge;
- arbitrary geometry remap and GlobalData patterns beyond the exact 4.0.3 case;
- native Saver OK/NOK, overlay/rectangle, heatmap, and exact source/processed
  matrix;
- REST variants beyond the tested 4.0.3 surface, current SDK matrix, Projects
  Manager repeated readiness/stuck lifecycle, and Cross-PEKAT regression;
- physical hardware and production vision acceptance.

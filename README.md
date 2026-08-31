# Codex Skill: PEKAT VISION

Public, version-aware Codex skill for PEKAT VISION 3.18.x, 3.19.x and 4.0.x, with exact 3.19.3, 4.0.1 and 4.0.3 evidence. The canonical skill is `.github/skills/pekat-vision`; no domain scripts/references are mirrored elsewhere in this repository.

## Capabilities

- Generate and validate Code plus 3.19.3 `.pmodule`, 4.0.1 `.ptool`, and narrow exact-4.0.3 CODE/Form `.ptool` exports while keeping 3.18 export gates explicit.
- Route exact `main(...)` signatures, Context, `result`/`exit`, Form runtime values and PEKAT 4 GlobalData.
- Generate native-compatible PEKAT 4.0.1 Form metadata and route verified sequential `context["image"]` replacement with changed resolution.
- Route PEKAT 4.0.1 sequential versus true multi-branch custom Context, mutually exclusive Conditional Gates, native result/overlay behavior, empty original-image pass-through, and scoped GlobalData/geometry gates.
- Safely analyze a PEKAT project/database directory or ZIP: restricted non-executing protocol-4 Pickle reader, recursive `modules.sort`/Parallelism, active/disabled/soft-deleted state, Filter/Gate rules, Code dependencies/side effects, and separate `database_old` migration diff.
- Analyze `output.log` families and project metadata/runtime state without treating `running.db` as process liveness; read exact-4.0.3 stored source state without a PEKAT connection.
- Route the directly tested PEKAT 4.0.1 Code library matrix, `cp312`/`win_amd64` wheel compatibility, and evidence-backed third-party library staging/acceptance.
- Route the clean tested PEKAT 4.0.3 CPython/ML/GPU matrix without conflating Torch CUDA, FAISS CPU, ONNX tooling, TensorRT Runtime-only evidence, missing packages, or locally added barcode dependencies.
- Apply exact 4.0.3 GlobalData restart/collision, zero-survivor, Folder filename, native Image Saver persistence, PTool full UI round-trip, public REST quirks, readiness, and PEKAT-specific Basler boundaries.
- Distinguish REST/SDK, Projects Manager, Cross-PEKAT, GlobalData and PEKAT Output, with bounded failure handling rather than automatic reliability frameworks.
- Route PEKAT-side MX-G2000/smart-camera/Basler/IFM integration and solve FOV/optics/lighting/motion/dataset constraints before overbuilding FLOW.

The skill defaults project/device/lifecycle operations to read-only or dry-run and contains only sanitized general knowledge and synthetic fixtures.

## Installation or update

Install from the canonical checkout without creating a divergent second source:

```powershell
$Source = ".github\skills\pekat-vision"
$Target = Join-Path $env:USERPROFILE ".codex\skills\pekat-vision"
if (Test-Path $Target) { Copy-Item "$Target\SKILL.md" "$Target\SKILL.md.bak" -Force }
New-Item -ItemType Directory -Path $Target -Force | Out-Null
Copy-Item "$Source\*" $Target -Recurse -Force
```

The backup is intentionally preserved. For a clean first install, Skill Installer may be used against this repository/path; it requires an absent destination.

## Validation

```powershell
$Validator = Join-Path $env:USERPROFILE ".codex\skills\.system\skill-creator\scripts\quick_validate.py"
python $Validator .github/skills/pekat-vision
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q .github/skills/pekat-vision/scripts
git diff --check
```

Offline analyzer smoke:

```powershell
python .github/skills/pekat-vision/scripts/analyze_flow_database.py <project-or-database.zip> --output flow-report.json
python .github/skills/pekat-vision/scripts/analyze_pekat_log.py <project-or-logs>
python .github/skills/pekat-vision/scripts/pekat_project_diagnostics.py <project> --json
python .github/skills/pekat-vision/scripts/analyze_source_state_403.py <project>
python .github/skills/pekat-vision/scripts/check_pekat_library_compat.py --pekat-version 4.0.1 --package scipy
```

Automated validation never starts PEKAT or writes to a project, PLC, IO-Link device, camera, or Projects Manager.

## Known open gates

- clean PEKAT 3.18 DB/export fixture and exact current Form/export contract;
- 3.19.3 Form runtime plus full `.pmodule` round-trip;
- 4.0.1 generated `.ptool` import/open/run is complete for the tested Code/Form use case; its reexport/reimport into a second clean project remains open. Exact 4.0.3 generation is limited to the separately tested CODE/Form subset, never a generic module/project writer;
- universal PEKAT DB writer (intentionally not implemented);
- REST cases beyond the exact tested 4.0.3 public surface, SDK release matrix, Projects Manager repeated readiness/stuck lifecycle, and Cross-PEKAT regression;
- branch-local A1→A2 propagation, generalized native-result merge, GlobalData patterns beyond the exact 4.0.3 collision result, and arbitrary geometry remapping;
- native Image Saver OK/NOK, overlay/rectangle, heatmap, and exact source-versus-processed variants;
- exact physical camera/IO-Link/vision acceptance.

Static/schema/AST tests are not described as PEKAT runtime or UI proof.

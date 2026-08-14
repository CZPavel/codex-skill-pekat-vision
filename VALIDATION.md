# Validation record

Date: 2026-08-14
Target: PEKAT VISION 4.0.1 Parallelism, Context, native-result and image-runtime sync
Status: **PASS for static/offline scope**

## New scope

- Guidance now separates three runtime layers: custom Context, native result/detection/class/heatmap data, and raster image propagation.
- Sequential custom Context propagation and exactly one surviving Conditional Gate branch are supported; true multi-branch custom changes are not described as first-writer, last-writer, union, or consensus merges.
- Empty, Gate-false, and disabled/no-op branches remain distinct. The original-image plus processing-branch pattern is documented without claiming overlays are rasterized.
- Standard crop coordinate behavior is bounded as a practical observation; rotation, Unifier, resize, warp, and other geometry changes require verification or explicit coordinate transformation.
- Concurrent GlobalData write/collision/order semantics remain open and GlobalData is not presented as an automatic Parallelism merge workaround.
- References now record PEKAT 4.0.1 sequential `context["image"]` replacement with changed shape, the bounded OpenCV enhancer timing, and the exact evidence boundary.
- Generated PTool import/open/run is recorded as runtime/UI verified for the tested Code/Form use case; its subsequent reexport/reimport remains open.
- The generator, JSON schema, distributed fixture and regressions enforce PEKAT 4.0.1 unconditional Form `visibility` as string `""`, never boolean.
- References: PEKAT 4.0.1 Code runtime/library matrix, library installation and ABI rules, project log troubleshooting, project diagnostics, and expanded documented communication routing.
- Helpers: read-only `analyze_pekat_log.py`, `pekat_project_diagnostics.py`, and `check_pekat_library_compat.py`.
- Tests: synthetic multiline/repeated log families, camera/model/filesystem routing, project metadata/anatomy/log handling, runtime-matrix regression, and wheel ABI/architecture classification.

## Runtime evidence represented by the skill

The machine-readable matrix records a direct PEKAT VISION 4.0.1 Code test on Windows AMD64 with CPython 3.12.12 / `cp312`: 46 of 58 targeted imports passed, 2 packages were present but failed import, 10 were unavailable, and 24 of 24 bounded functional smoke operations passed. Functional boundaries are recorded per package. This evidence belongs to the tested installation and is not projected onto PEKAT 3.x or every clean 4.0.1 installation.

## Current automated validation

- [x] Official `quick_validate.py`: `Skill is valid!`
- [x] Default Python suite: `55 passed`.
- [x] Python 3.11 isolated environment: `55 passed`.
- [x] Python 3.13 isolated environment: `55 passed`.
- [x] Canonical Python scripts compile.
- [x] Existing module/export, REST failure-path, Projects Manager and industrial safety regressions remain enabled.
- [x] FLOW analyzer still uses a restricted non-executing Pickle reader and reuses one parser for project diagnostics.
- [x] Machine data parses as JSON; skill metadata/references parse under the existing YAML/JSON regression tests.
- [x] Public bundle security scan and 48 golden routing fixtures remain enabled.
- [x] `git diff --check` passes.

## Evidence boundary

The log/project/library helpers and updated generator are unit-tested with synthetic local fixtures. They do not install packages, modify PEKAT, write a project database, start training, contact a PLC, or alter a camera. The 4.0.1 runtime matrix, Parallelism/Context/image behavior, sequential image replacement, OpenCV timing and generated PTool import/open/run are prior direct runtime/UI evidence represented by the skill; this repository validation does not repeat those PEKAT operations.

## Manual acceptance boundary

The following remain OPEN unless performed separately on an isolated exact-version target:

- reexport of the externally generated/imported PEKAT 4.0.1 PTool and reimport into a second clean project;
- zero-surviving Conditional Gate behavior, branch-local A1→A2 propagation, and generalized native-result merge behavior;
- concurrent GlobalData write/collision/winner/order semantics;
- coordinate remapping for rotation, Unifier, resize, warp, and other arbitrary geometry transforms;
- exact 3.19.3 `.pmodule` and 3.18 export/Form runtime round-trips;
- live REST and SDK exchange;
- Projects Manager and Cross-PEKAT lifecycle/failure/reconnect behavior;
- installing a new package into the embedded server and validating its direct Code import/function;
- physical camera acquisition, IO-Link/PLC communication, and vision-system acceptance;
- direct project database modification (not implemented as a general feature).

Automated tests never start/stop PEKAT, mutate a project, or write to industrial hardware.

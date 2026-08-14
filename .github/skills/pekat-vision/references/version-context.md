# Version, Context, and state routing

## Evidence labels

- **Documented (D):** exact-version vendor/SDK contract.
- **Runtime/UI tested (E):** reproduced on the stated version and path.
- **Observed/static (S/R):** observed in exports or project files; not a public API.
- **Practical (P):** useful field evidence that still needs reproduction.
- **Open:** do not promote to fact.

Prefer current exact-version runtime/export evidence, then exact-version documentation/SDK, then sanitized practical evidence. Never claim cross-version compatibility merely because names match.

## Version matrix

| Topic | 3.18.x | 3.19.3 | 4.0.1 |
|---|---|---|---|
| FLOW unit | module (D) | module (D) | tool (D) |
| No-Form Code | `main(context)` exists; documentation also contains inconsistent legacy signatures (D) | `main(context)` is a safe current pattern; fresh UI DB also stored `main(context, form)` with `form=[]` (D/S, runtime variant open) | `main(context)` runtime tested (E) |
| Form Code | exact current Form/export contract open | `main(context, form)` in documentation and real exports; exact runtime matrix open (D/R) | `main(context, form)` runtime tested (E) |
| Export | exact schema/extension open | `.pmodule`, root `type/module/version` observed (R) | `.ptool`, root `type/module/version`, create/edit/run/export and one externally generated import/open/run tested (R/E); reexport/reimport of that generated PTool open |
| GlobalData | not established | Inspection may show `globalData: null`; do not claim API/persistence | `context["globalData"]` is a dict shared by Code tools and persisted between evaluations while the project ran (E); restart/concurrent-write semantics open |
| DB topology | exact disk schema open | protocol-4 `modules.db`/`sort` contract observed (S/E) | same topology grammar observed; record fields are migration/lineage-aware (S/E) |
| Audited Windows ABI | unknown | `cp310` on one PC | direct Code test: CPython 3.12.12, `cp312`, AMD64 on one installation |

ABI values are local fingerprints, not universal guarantees. Re-probe another installation with `scripts/runtime_fingerprint.py`.
For the complete 4.0.1 import/function matrix and flattened-metadata caveat, read
`code-runtime-pekat401.md`; never project that matrix onto 3.19.3.

## Context cards

Context moves through active FLOW steps for the current evaluation. Validate presence, type, shape, and producer before use.

| Key | Safe contract and boundary |
|---|---|
| `image` | NumPy-like raster; dtype, channels and shape are provider/tool-specific. In a PEKAT 4.0.1 sequential FLOW test, assigning a new ndarray changed `(864, 1184, 3)` to `(432, 592, 3)` and the next Code tool received the new shape (E). Validate downstream tools and do not infer a universal parallel image winner. |
| `detectedRectangles` | Native detection metadata; fields vary by producer. Check type/length/keys before access. PEKAT may display it as an overlay without drawing it into `image` pixels. |
| `heatmaps` | Native tool-produced visualization data; exact shape/content is tool-specific and separate from the image raster. |
| `result` | `True` OK, `False` NOK; `None` was observed before a result-producing step in 4.0.1. Do not mutate for diagnostics. |
| `exit` | Boolean deliberate termination of the current branch; other Parallelism branches continue. |
| `data` | Provider/request-specific internal data. A Folder filename/path is only practical evidence; diagnostics may read it, but do not write or generalize it. |
| `operatorInput` | Operator View state, not Form values. |
| `production_mode` | Documented for images received through HTTP API; not a general server-production flag. |
| `completeTime` | Processing time in seconds; do not assume when it becomes final without an exact test. |
| `stdout` / `stderr` | Inspection-captured Code output observed in 4.0.1. Prefer a small diagnostic key over excessive prints. |

Custom Context keys are appropriate between sequential tools in one evaluation. Define owner, type, optionality, and reset behavior. In controlled PEKAT 4.0.1 tests, new keys, scalar changes, delete/replacement and nested/in-place dict/list mutations propagated sequentially. A changed Python `id()` did not mean the value failed to propagate.

## PEKAT 4.0.1 Parallelism contract

Experimentally verified for the tested 4.0.1 scenarios:

- At a true join of multiple continuing branches, custom branch changes did not survive. Unique keys, differing writes and equal values in both branches all returned to the pre-parallel custom state; timing and physical branch order did not create first/last-writer behavior.
- With mutually exclusive Conditional Gates and exactly one continuing branch, that branch's custom Context could continue after Parallelism. Gate FALSE is not the same as an empty branch.
- An empty branch can be useful as original/pre-transform image pass-through, but it also contributes to true multi-branch custom-Context behavior. A disabled/no-op Code branch is not equivalent to Gate FALSE and may act as pass-through; treat its exact mechanism as observation/inference, not a vendor implementation contract.
- Native `result`, detections/classes and heatmaps have separate PEKAT result/visualization semantics. Prefer native `result` for parallel OK/NOK; do not generalize custom-Context loss to native results.
- Native bounding boxes/heatmaps are overlays/metadata, not automatically rasterized pixels. Standard crop coordinate handling was practically observed; rotation, Unifier, manual/custom resize and warp require overlay verification or explicit coordinate transformation.
- GlobalData concurrent writes, collisions and winner/order are open. Persistence makes it unsuitable as an automatic branch-merge workaround.

Machine-readable decision contract:

```yaml
pekat_4_0_1_parallelism_contract:
  custom_context:
    sequential_propagation: runtime_verified
    true_multi_branch_join: branch_changes_not_propagated
    equal_values_consensus_merge: false
    first_or_last_writer: false
    single_surviving_conditional_gate_branch: propagation_runtime_verified
  branches:
    conditional_gate_false_equals_empty: false
    empty_can_pass_original_image: true
    empty_contributes_to_custom_multi_branch_join: true
    disabled_noop_equals_gate_false: false
  native_results:
    use_result_for_parallel_ok_nok: true
    detections_classes_heatmaps_are_custom_context: false
  image:
    native_overlay_automatically_rasterized: false
    standard_crop_mapping: practical_observation
    arbitrary_transform_mapping: verify_or_transform_coordinates
  globaldata:
    concurrent_write_semantics: open
    automatic_parallel_merge_workaround: false
  open:
    - zero_surviving_gate_branches
    - branch_local_a1_to_a2
    - generalized_native_result_merge
    - arbitrary_geometry_remap
```

## State selection

| Required lifetime | Mechanism |
|---|---|
| Same evaluation, sequential steps | custom Context key |
| Between evaluations in one PEKAT 4 project | GlobalData, with explicit initialization/reset contract |
| Between projects | Cross-PEKAT or explicit REST/SDK transport |
| External consumer | REST response or a suitable PEKAT Output |

Do not use `__main__`, module globals, or an implicit process cache as a default persistence contract.

Runtime-tested PEKAT 4.0.1 minimum:

```python
def main(context):
    global_data = context.get("globalData")
    if not isinstance(global_data, dict):
        context["code_error"] = "globalData unavailable"
        return
    global_data["counter"] = int(global_data.get("counter", 0)) + 1
```

## Controlled migration observations

In one controlled 3.19.3-to-4 upgrade, `database_old` was byte-identical to the pre-upgrade database and current `database` contained migrated records; `modules.sort` remained structurally equal. Observed field changes included Filter `evalType`, model/mask metadata, preview metadata, and output items. Treat this as strong route-specific evidence, not a universal guarantee.

Migration procedure:

1. Preserve and hash the source project/export.
2. Inventory Code signatures, Context reads/writes, Form, native imports, external I/O, and `database_old`.
3. Regenerate the target envelope; never rename an extension or only edit `version`.
4. Rebuild native wheels for the target ABI/architecture.
5. Compare FLOW topology and record-level changes separately.
6. Validate only in a new isolated project; record UI/runtime gates honestly.

Known gates: clean 3.18 DB/export fixture, 3.19.3 Form runtime/round-trip, 4.0.1 generated PTool reexport/reimport, Folder `data`, GlobalData restart/concurrency, zero-surviving Gate branches, branch-local A1→A2, generalized native-result merge, and arbitrary geometry remap.

Legacy public evidence IDs retained for regression routing: `pekat-kb-4-0-1-page-1513132787`, `local-runtime-fingerprint-2026`.

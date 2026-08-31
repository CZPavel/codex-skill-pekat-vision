# FLOW, project databases, and migration history

## Scope and safety

This contract comes from controlled PEKAT 3.19.3 and 4.x project observations. It is not a public vendor API. PEKAT 3.18 disk schema remains open.

Observed project `.db` files are Python Pickle protocol 4, not SQLite. Never call `pickle.load()`/`pickle.loads()` on user-supplied project data. Use:

```powershell
python scripts/analyze_flow_database.py project-or-database.zip --output flow-report.json
```

The bundled analyzer:

- accepts a project/database directory or ZIP without extracting it;
- bounds file/ZIP sizes and rejects unsafe paths;
- interprets only primitive/container protocol-4 opcodes;
- rejects `GLOBAL`, `STACK_GLOBAL`, `REDUCE`, `BUILD`, `OBJ`, `INST`, `NEWOBJ*`, `EXT*`, persistent IDs, and external buffers;
- never executes Code found in records; Python Code is parsed only with `ast`;
- analyzes `database` and `database_old` separately.

## Disk model

`database/modules.db` is the primary FLOW object. Other observed DBs include camera, image/model registries, output items, statistics, tags and Operator View state. Legacy sidecars can be historical/supplementary; do not substitute them for `modules.db`.

Observed `modules.db` top level:

```python
{
    "items": [...],       # record registry
    "sort": [...],        # live topology and order
    "filter": [...],      # not the Conditional Gate record list
    "lastUpdate": ...,
    # lineage-specific fields may exist
}
```

Never use one field such as `showPreview` as a version detector.

## `modules.sort` grammar

```text
integer          = module ID
nested list node = Parallelism
items in node    = branches
branch           = sequence
[]               = explicit empty branch
```

Equivalent grammar:

```ebnf
flow      = sequence ;
sequence  = { module_id | parallel } ;
parallel  = "[" branch { "," branch } "]" ;
branch    = sequence ;
module_id = integer ;
```

Example `[1, [[2, 3], []], 4]`:

```text
[1] Code
Parallelism
  Branch 1: [2] Filter -> [3] Preprocess
  Branch 2: empty
[4] next module
```

Parallelism is a virtual structural node, not necessarily an item record. Parse recursively; real evidence contains nested Parallelism.

## Module state

For each record, report raw fields and interpretation:

```text
active candidate:
    ID in modules.sort
    AND softDeletedDate is None
    AND isActive is not explicitly False

disabled:
    ID in modules.sort
    AND isActive == False

soft-deleted/historical:
    softDeletedDate is not None
    (also report whether ID unusually remains in modules.sort)
```

Missing `isActive` is not `False`; some observed live model records omit it. A soft-deleted record may still contain `isActive=True`.

## Filter / Conditional Gate

- PEKAT 3.x Filter and PEKAT 4 Conditional Gate can both be stored as module type `FILTER`.
- PEKAT 4 Context/GlobalData Gate evidence includes `evalType="CONTEXT"` and a `contextNode.path`.
- Top-level `modules.filter` is not the list of Conditional Gate nodes.
- Report rule structure, `evalType`, and Context/GlobalData path without inventing missing semantics.

The common observed PEKAT 4.0.x Gate/FILTER family has 4.0.1 and 4.0.3 evidence anchors. Exact 4.0.3 runtime evidence verifies this narrow recipe:
type `FILTER`, one rule with `evalType="CONTEXT"`,
`contextNode.path="/globalData/<key>"`, `valueType="boolean"`,
`operator="EQUAL"` and a boolean value. It routed TRUE and FALSE exclusively
in the tested fixture. This is a KNOWN RECIPE for analysis/design, not a public
writer: strings, numbers, NOT_EQUAL, CONTAINS, NOT_CONTAINS, rectangle logic,
multi-rule combinations and other paths/operators/types remain
acceptance-pending or unsupported.

## Parallelism runtime design in PEKAT 4.0.1

Do not treat all branch data as one generic Context merge. In controlled tests, custom branch `context["X"]` changes did not propagate through a true multi-branch join, including equal-value writes. Do not propose first/last-writer, union, consensus, timing or branch-position logic.

Capturing a tool result into a custom key such as `context["cap_raw_result"]` is useful for a following sequential step or branch-local consumer before the join. It is not a generic post-join propagation mechanism for a real multi-branch Parallelism.

For mutually exclusive routing, prefer Conditional Gates whose conditions ensure exactly one branch continues for a frame. That surviving branch may propagate custom Context. Gate FALSE is not equivalent to an empty branch. In exact 4.0.3 zero-survivor tests, all branches exiting did not automatically terminate the whole FLOW: downstream continued from the pre-parallel Context.

An empty branch is not automatically redundant:

```text
Parallelism
  EMPTY                              -> original/full image
  crop/preprocess -> detector A      -> native detections
  crop/preprocess -> detector B      -> native detections/result
JOIN
  original/full image + native overlays/result -> UI or Image Saver
```

This is a practical original-image pass-through pattern. It also creates a true multi-branch join for custom Context, so branch custom values should not be expected after the join. A disabled/no-op Code branch may similarly contribute an unchanged pass-through state and is not equivalent to Gate FALSE; do not claim its internal mechanism.

Prefer PEKAT-native `result` for parallel OK/NOK and native detections/classes/heatmaps for result visualization. They do not follow the tested custom-Context rule. Bounding boxes/heatmaps are overlay metadata, not automatically drawn into the raster. Standard crop mapping was practically observed; verify or explicitly transform coordinates after rotation, Unifier, custom resize or warp.

Do not replace this simple topology with a GlobalData state machine merely to merge branches. In exact 4.0.3, independent branch keys could survive and a same-key collision was deterministic by branch order, not wall-clock completion. Use branch-specific keys plus explicit merge; remember that GlobalData resets with the project-server process and can otherwise become stale.

## Exact generated FLOW boundary

A generated PEKAT 4.0.1 `database/modules.db` fixture loaded and ran with:

- `modules.items` plus recursive `modules.sort`;
- nested Parallelism and an explicit `[]` empty branch;
- Code, Detector, OCR, Conditional Gate stored internally as `FILTER`, Mask,
  structural Image Saver, and explicit `modelId` for model-backed tools.

This closes only the exact fixture proof. Direct DB generation remains an
exact-version, internal/offline, fixture-backed technique, not a stable public
API or the normal authoring recommendation. Prefer the PEKAT UI/supported
workflow and do not infer unobserved module fields.

For the reproduced exact-version Gate fixture, the encoded class name was:

```text
classname = local_class_id * 2^42 + source_module_id
2^42 = 4398046511104
```

Do not reverse the IDs. This encoding is internal and version-gated.

## Classifier boundary

Classifier `classNames` may contain all candidate classes. In reproduced PEKAT
4 runtime the first element is the winner; candidate presence elsewhere is not
final classification. Never implement winner routing with `any(candidate
label)`, and keep Detector result/detection semantics separate.

## Folder and native Image Saver 4.0.3 evidence

- Folder F1 new-file watcher, F2 `analyzeExisting`, and F3 simulation plus
  `analyzeExisting` passed. `context["data"]` was filename-only `str`; do not
  generalize that to another provider/version. For programmatic settings,
  write the leaf, wait for persistence/readback, then perform the dependent
  operation.
- Native Image Saver `ALL` + local + `by_days` + `image_only` persisted PNGs.
  The configured root had to exist and was not auto-created. A missing root
  could be log-only while REST still returned HTTP 200 with `error=false`.
  Transport/analysis success is not persistence success. OK/NOK triggers,
  overlays/rectangles, heatmaps, and exact source-versus-processed behavior
  remain untested.

## Static Code inventory

For each CODE record, parse but never run `sourceCode`. Inventory:

- Context reads/writes, especially `result`, `exit`, custom flags, image/detections;
- GlobalData reads/writes;
- imports and syntax status;
- filesystem, network, Cross-PEKAT, PLC/fieldbus, image/report saves;
- hard-coded endpoint/path risks and ordering relative to Gates.

Cross-PEKAT calls create dependencies outside local `modules.sort`; render them separately.

## Recommended analysis output

1. Source identity/hash and explicit version metadata when present; otherwise probable lineage with uncertainty.
2. `database`/`database_old` inventories and hashes.
3. Recursive readable FLOW tree (optionally Mermaid).
4. Module table: ID, label/type, in-flow, active-field presence, state.
5. Disabled, soft-deleted, historical and missing-reference lists.
6. Code inventory, Context/GlobalData dependencies and side effects.
7. Filter/Gate rules and paths.
8. Integrity warnings: duplicate/missing/deleted refs, invalid Code, inconsistent record links.
9. Migration diff and known uncertainty.

## `database_old`

Analyze as historical/pre-upgrade evidence, never as live FLOW. In one controlled 3.19.3-to-4 migration it was byte-identical to the complete pre-upgrade database and current `database` was migrated; `modules.sort` remained structurally equal. Other upgrade routes may differ.

Compare filenames/hashes, `modules.sort`, record keys, Code, Gates, models and output items. State whether findings are byte equality, semantic equality, or inference.

## Modification boundary

Priority order:

1. analyze and explain;
2. propose a readable FLOW skeleton;
3. prepare a dry-run/patch plan over a project copy;
4. generate/modify `.db` only for a controlled exact-schema, fixture-backed laboratory case.

Do not create a universal Pickle writer. Before any DB mutation require a copy, version/schema evidence, deterministic diff, isolated import/open test, rollback, and explicit approval.

Known gates: clean 3.18 fixture, full type-specific schema across releases, branch-local A1→A2 custom propagation, generalized native-result merge, untested GlobalData collision patterns beyond the exact 4.0.3 result, arbitrary geometry remap, every upgrade route, remaining Saver variants, and universal DB generation.

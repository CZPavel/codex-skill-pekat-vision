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
4. generate/modify `.db` only for a controlled exact-schema laboratory case.

Do not create a universal Pickle writer. Before any DB mutation require a copy, version/schema evidence, deterministic diff, isolated import/open test, rollback, and explicit approval.

Known gates: clean 3.18 fixture, full type-specific schema across releases, custom Context merge, concurrent GlobalData writes, every upgrade route, and universal DB generation.

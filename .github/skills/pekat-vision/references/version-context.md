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
| Export | exact schema/extension open | `.pmodule`, root `type/module/version` observed (R) | `.ptool`, root `type/module/version`, create/edit/run/export tested (R/E); import/reimport open |
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
| `image` | NumPy-like image; dtype, channels and shape are provider/tool-specific. Preserve valid type/shape semantics. |
| `detectedRectangles` | Sequence of detections; fields vary by producer. Check type/length/keys before access. |
| `heatmaps` | Tool-produced heatmap sequence; exact shape/content is tool-specific. |
| `result` | `True` OK, `False` NOK; `None` was observed before a result-producing step in 4.0.1. Do not mutate for diagnostics. |
| `exit` | Boolean deliberate termination of the current branch; other Parallelism branches continue. |
| `data` | Provider/request-specific internal data. A Folder filename/path is only practical evidence; diagnostics may read it, but do not write or generalize it. |
| `operatorInput` | Operator View state, not Form values. |
| `production_mode` | Documented for images received through HTTP API; not a general server-production flag. |
| `completeTime` | Processing time in seconds; do not assume when it becomes final without an exact test. |
| `stdout` / `stderr` | Inspection-captured Code output observed in 4.0.1. Prefer a small diagnostic key over excessive prints. |

Custom Context keys are appropriate between sequential tools in one evaluation. Define owner, type, optionality, and reset behavior. Custom mutable Context merge semantics across Parallelism branches remain open.

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

Known gates: clean 3.18 DB/export fixture, 3.19.3 Form runtime/round-trip, 4.0.1 import/reimport, Folder `data`, GlobalData restart/concurrency, and custom Context branch merge.

Legacy public evidence IDs retained for regression routing: `pekat-kb-4-0-1-page-1513132787`, `local-runtime-fingerprint-2026`.

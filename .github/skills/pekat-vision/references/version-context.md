# Version routing, Context, and GlobalData

## Contents

- [Mandatory routing](#mandatory-routing)
- [Context contract](#context-contract)
- [Version matrix](#version-matrix)
- [Migration](#migration)

## Mandatory routing

Ask for PEKAT VISION `3.19.3` or `4.0.1` before creating an import file. Do not infer cross-version compatibility. Label facts with a document ID; label extrapolations as inference.

Evidence priority: exact-version local export/runtime fingerprint, exact-version official documentation, official SDK, exact device manual/IODD, then curated examples.

## Context contract

Context passes through active processing modules/tools. Custom keys may be added, but the type/shape of established values must stay stable.

Documented standard keys include:

| Key | Contract |
|---|---|
| `image` | NumPy array; preserve valid dtype and shape semantics. |
| `detectedRectangles` | Array of detections; inspect the actual project structure before indexing. |
| `result` | Boolean inspection result. Diagnostics must not mutate it accidentally. |
| `exit` | Boolean early branch termination. In parallelism, only the current branch terminates. |
| `heatmaps` | Array/list of NumPy heatmap data. |
| `production_mode` | True when processing an image received through the HTTP API. |
| `operatorInput` | Operator View values; not Form Editor input. |
| `completeTime` | Image processing time in seconds. |
| `data` | Internal/additional request data; do not assume it appears in every response. |

Sources: `[pekat-kb-3-19-3-page-1207111718]`, `[pekat-kb-4-0-1-page-1513132787]`.

## Version matrix

| Topic | 3.19.3 | 4.0.1 |
|---|---|---|
| Form entrypoint | `main(context, form=None)` | `main(context, form=None)` |
| Export | `.pmodule`, version `3.19.3` | `.ptool`, version `4.0.1` |
| Verified form types | text, number, checkbox, select | text, number, checkbox, select |
| Context lifetime | Per evaluation | Per evaluation |
| Cross-evaluation state | Do not claim GlobalData | GlobalData is project-level state across evaluations |
| Audited Windows ABI | `cp310` | `cp312` |

The ABI values are a read-only fingerprint of one PC, not a universal guarantee. Sources: `[pekat-module-export-schema-v1]`, `[local-runtime-fingerprint-2026]`.

The 4.0.1 Context documentation describes GlobalData as a project-level key/value store that survives evaluations for the lifetime of the running project and is available to Code/Conditional Gate. Do not invent access methods when the exact API is not in the supplied evidence. Source: `[pekat-kb-4-0-1-page-1513132787]`.

## Migration

1. Inventory Context reads/writes and external imports.
2. Replace legacy `main(context, module_item=None)` with `main(context, form=None)` and `values = form or {}`.
3. Regenerate the target envelope; never rename an extension or only edit its version string.
4. Rebuild native wheels for the target ABI/architecture.
5. Verify form rendering/defaults/values and export round-trip in a new isolated project.
6. Verify state lifetime and all network/device failure paths.

Do not modify a running PEKAT project during migration.

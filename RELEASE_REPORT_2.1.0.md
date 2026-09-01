# PEKAT VISION public maintenance feature release 2.1.0

Date: 2026-09-01

## Scope and source

- Public repository: `CZPavel/codex-skill-pekat-vision`.
- Baseline: `a36521b78d3e1fbfe703fe639fab9cf4b48c3530`.
- Canonical skill source and distributable package:
  `.github/skills/pekat-vision`.
- Build mechanism: the repository is the distributable skill; validation is
  `quick_validate.py`, `pytest`, and `compileall`. No second build tree exists.
- Assistant upstream used read-only at `56ae9fcc16b4cad2f13eb774dd0fddc9eaa2e367`.
- PEKAT runtime mutations: `0`.

## Knowledge and routing

The release adds exact-4.0.3 boundaries for Image Library read knowledge,
training-derived `trainingImages`/`testImages`, Detector editor quiescence,
training/model lifecycle gaps, Smart Mask/SAM2, serialized Detector rectangle
states, and FLOW Mask taxonomy. It retains the strict distinction between
read/schema evidence, runtime observation, and writer authority. It corrects
no older exact 4.0.1 scope by pretending it is 4.0.3 writer authority.

## Tool promotion matrix

| Assistant source | Public use case | Existing public equivalent | Dependencies | Version scope | Side effects | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| `analysis/flow_database.py` | FLOW topology/project inventory | `analyze_flow_database.py` | stdlib | 3.19.3/4.x observed | read-only | REUSE_EXISTING |
| `analysis/project_diagnostics.py` | log/runtime metadata diagnosis | `pekat_project_diagnostics.py` | stdlib | version-aware | read-only | REUSE_EXISTING |
| `form_compat.py` | Form value normalization | `form_normalization.py` | stdlib | 4.0.x evidence | none | REUSE_EXISTING |
| `analysis/dataset_model.py` read projection | dataset/model, annotation-state, artifacts | none | bundled restricted reader, stdlib | exact 4.0.3 | read-only | ADAPT_PURE_LOGIC |
| detector training/annotation/model transports | live mutation | none | Assistant bridge/acceptance contracts | exact 4.0.3 | production-affecting | DO_NOT_PORT |
| Host, transaction layer, A4 planner, capability registry | orchestration | none | Assistant-only | Assistant 3.x | broad | DO_NOT_PORT |
| PTool generator | exact Form artifact generation | `generate_code_module.py` | stdlib/jsonschema | 3.19.3/4.0.1/4.0.3 bounds | output file only | REUSE_EXISTING |

## Added helper

`scripts/inspect_dataset_model.py <project> --output report.json` is a
standalone exact-4.0.3 offline inspector. It reads allowlisted primitive
Pickle registries only, reports inventory and QA, and never loads weights.
Its only optional output is an explicitly requested JSON report outside the
project. It does not modify its input.

## Explicitly excluded executors

No public helper uploads/deletes images, changes tags, writes annotations,
calls Smart Mask, starts/stops training, selects/deletes models, executes
Socket.IO, edits a project DB, or starts PEKAT.

## Recommended PEKAT_AGENT_DATA_MAKE / GPT knowledge follow-up

No mutation was made to `PEKAT_AGENT_DATA_MAKE` because its public publication
workflow remains separately gated. For a later targeted knowledge refresh:

| Priority | Target | Delta | Evidence source | Reason |
| --- | --- | --- | --- | --- |
| High | operating rules and FLOW/project direct files | train/test provenance; Smart Mask/FLOW Mask distinction; training quiescence | Assistant A3.7b3r1, A3.7c2, A3.7d1 | high public explanation value |
| Medium | FLOW/project direct file | Image Library boundary, annotation serialized state, model artifact read boundary | Assistant A3.7a, A3.7c3r1, A3.7d1 | prevents accidental writer inference |

## Release and validation status

The tag/release decision follows the repository's existing `v2.0.0` tag
convention only after the pushed commit has green GitHub Actions. See
`VALIDATION.md` for the final local static/offline results.

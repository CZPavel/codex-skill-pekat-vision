# PModule, PTool, and Form Editor

## Route by version

| Version | Generate | Entrypoint rule | Evidence boundary |
|---|---|---|---|
| 3.18.x | Do not generate without an exact export/schema | No universal signature: documentation contains `main(context)` and legacy alternatives | Code documented; current Form/export schema open |
| 3.19.3 | `.pmodule` | Form exports use `main(context, form)`; no-Form `main(context)` is safe, while a fresh UI record also stored two args with empty Form | JSON/export static evidence; exact runtime/round-trip open |
| 4.0.1 | `.ptool` | `main(context)` without Form; `main(context, form)` with Form | Both signatures and Form runtime tested; create/edit/run/export plus one externally generated import/open/run tested; generated reexport/reimport open |
| 4.0.3 | `.ptool`, narrow CODE/Form generator subset | exactly `main(context, form)` | exact runtime-accepted CODE/Form serializer only: text, number, checkbox, select; no generic module writer |

A module/tool export is one Code step, not a project and not a sandbox. Never rename `.pmodule` to `.ptool` or only edit the root version.

An export also does not bundle an arbitrary external Python dependency. If
`sourceCode` imports a non-standard package, record the required package,
target PEKAT version/ABI, tested version/evidence level and destination Code
import test. A package verified in the 4.0.1 matrix is not thereby available in
3.19.3 or on another PC. See `code-library-installation.md`.

## Observed envelope

```json
{
  "type": "CODE",
  "module": {
    "label": "Purpose",
    "id": 1700000000000,
    "type": "CODE",
    "note": "Inputs, outputs, side effects and failure mode",
    "gpuSettings": [],
    "softDeletedDate": null,
    "sourceCode": "def main(context):\n    pass\n",
    "form": [],
    "formValues": {},
    "showImagePreview": true,
    "editDate": 1700000000000,
    "isActive": true
  },
  "version": "4.0.1"
}
```

This is an observed 3.19.3/4.0.1 family, not a public promise for all releases. Generate unique positive integer IDs and check collisions before import.

## Form definition versus current state

- `module.form` defines UI controls. Runtime keys are `formKey`, not `label`.
- `form[*].defaultValue` is the defined default.
- `module.formValues` contains saved current/changed values by `formKey`; in a 4.0.1 UI test it was empty before edits and populated after edits without changing defaults.
- `form` is a runtime dict and is separate from `context["operatorInput"]`.

Runtime-tested PEKAT 4.0.1 representations:

| Type | Untouched default | After UI edit | Normalize when used |
|---|---|---|---|
| text | `str` | `str` | `str`, then domain validation |
| number | e.g. `"12"` (`str`) | e.g. `27` (`int`) | reject bool; `float`/`int`; range check |
| checkbox | `bool` | `bool` | require bool; explicitly parse known legacy strings only if needed |
| select | e.g. `"0"` index string | e.g. `"manual"` text | allow valid index or allowlisted text |

For an unconditional PEKAT 4.0.1 Form item, preserve `"visibility": ""` as a
string. A generated item with boolean `true` imported but failed while opening
with `TypeError: n.visibility.includes is not a function`; changing it to the
native empty-string representation allowed the tested PTool to open and run.
Do not infer conditional-visibility syntax from this one unconditional value,
and do not backport the rule to an older version without its own export evidence.

Use `scripts/form_normalization.py` or copy only the small helper needed into a PEKAT Code module. Do not use `bool("false")`.

```python
def main(context, form):
    values = form if isinstance(form, dict) else {}
    try:
        threshold = float(values.get("threshold", 12))
    except (TypeError, ValueError):
        context["code_error"] = "threshold must be numeric"
        return
```

Changing the local runtime dict is not a UI persistence API.

## Generator contract

`scripts/generate_code_module.py` accepts a small JSON ModuleSpec validated by `references/module_spec.schema.json`:

```json
{
  "target_version": "4.0.1",
  "label": "Threshold",
  "note": "Reads image and threshold; changes image only",
  "source_code": "def main(context, form):\n    pass\n",
  "form": [
    {"type":"number","formKey":"threshold","label":"Threshold","defaultValue":"12","min":"0","max":"255"},
    {"type":"select","formKey":"mode","label":"Mode","defaultValue":"0","options":"auto;manual"}
  ],
  "form_values": {}
}
```

```powershell
python scripts/generate_code_module.py spec.json --output threshold
```

The generator derives the extension, validates JSON types, unique Form keys/IDs, Form values, and Python AST/entrypoint. Its validated targets are 3.19.3, 4.0.1 and a narrow exact 4.0.3 CODE/Form subset. For 4.0.1 it emits and enforces string `visibility: ""`; boolean or unknown non-empty visibility is rejected. For 4.0.3 Form is required, `main(context, form)` is exact, visibility is `""`, number `min`/`max` are required numeric JSON values, and `formValues` is normalized for every declared item. The helper writes UTF-8 JSON and never opens PEKAT.

## Acceptance sequence

1. Preserve/hash the original; generate beside it.
2. Run JSON schema, Python AST, and security/static checks.
3. Import into a new isolated exact-version project.
4. Verify label/note/activity/code/Form order/defaults/current values.
5. Run representative images and inspect Context/stdout/stderr.
6. Export under a new name and compare semantic fields.
7. Reimport into another clean project.

The 2026-08-14 test completed import/open/run for one externally generated
4.0.1 Code/Form PTool. Steps 6-7 for that generated artifact remain open.

For a separate exact 4.0.3 fixture, the full supported UI sequence passed:

```text
import → run → export → remove → reimport → run
```

Semantic comparison preserved `sourceCode`, `form`, `defaultValue`,
`formValues`, `showImagePreview`, `gpuSettings`, and module version. Correct UI
insertion put the imported module into FLOW. An earlier orphan direct-import
probe did not establish a universal import contract; it was not proof that
ordinary supported UI import necessarily creates an orphan. Internal event
details remain evidence, not a public authoring API.

The PTool still does not carry third-party packages or model assets. In
particular, `zxingcpp`/`pyzbar` require a local add-on installation and were not
present in clean tested 4.0.3. Preserve reproduced unconditional
`"visibility": ""`; do not invent conditional syntax or boolean visibility.

Legacy public evidence ID retained for regression routing: `pekat-module-export-schema-v1`.

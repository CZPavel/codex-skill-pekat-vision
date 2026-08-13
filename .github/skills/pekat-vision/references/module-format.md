# PModule, PTool, and Form Editor

## Route by version

| Version | Generate | Entrypoint rule | Evidence boundary |
|---|---|---|---|
| 3.18.x | Do not generate without an exact export/schema | No universal signature: documentation contains `main(context)` and legacy alternatives | Code documented; current Form/export schema open |
| 3.19.3 | `.pmodule` | Form exports use `main(context, form)`; no-Form `main(context)` is safe, while a fresh UI record also stored two args with empty Form | JSON/export static evidence; exact runtime/round-trip open |
| 4.0.1 | `.ptool` | `main(context)` without Form; `main(context, form)` with Form | Both signatures and Form runtime tested; create/edit/run/export tested; import/reimport open |

A module/tool export is one Code step, not a project and not a sandbox. Never rename `.pmodule` to `.ptool` or only edit the root version.

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

The generator derives the extension, validates JSON types, unique Form keys/IDs, Form values, and Python AST/entrypoint. It writes UTF-8 JSON and never opens PEKAT.

## Acceptance sequence

1. Preserve/hash the original; generate beside it.
2. Run JSON schema, Python AST, and security/static checks.
3. Import into a new isolated exact-version project.
4. Verify label/note/activity/code/Form order/defaults/current values.
5. Run representative images and inspect Context/stdout/stderr.
6. Export under a new name and compare semantic fields.
7. Reimport into another clean project.

Until steps 3-7 are actually performed, report `statically_validated / UI round-trip open`, not runtime PASS.

Legacy public evidence ID retained for regression routing: `pekat-module-export-schema-v1`.
